# main.py2 - uses CopyTradingBot 

# Standard library imports
import os
import asyncio
import json
import base64
import statistics
import time
import traceback
from typing import List, Dict, Union, Optional
from dataclasses import dataclass
from datetime import datetime, UTC, timezone

# Third-party imports
import pytz
import websockets
from websockets.client import connect
from websockets.legacy.client import connect
import aiohttp

# Solana imports
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0, VersionedMessage
from solders.address_lookup_table_account import AddressLookupTableAccount
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from spl.token.instructions import get_associated_token_address, create_associated_token_account

# Local imports
import keyZ as kz
from models import Bundle
from jito_service import JitoClient
from fast_executor import FastExecutor
from utils import fetch_json_rpc
from simulate_clone import clone_transaction_from_wallet_a
from logger import log_mirrored_trade
from replicator import Replicator
from tx_builder import (
    create_and_sign_transaction,
    RPC_ENDPOINTS,
    create_jito_tip_instruction,
    START_TIME,
    CURRENT_USER
)
from config import (
    DECODED_PRIVATE_KEY,
    BOT_PUBKEY,
    HELIUS_RPC_URL as RPC_URL,
    HELIUS_WS_URL as WS_URL
)
from wallet_tx_parser import (
    WalletATxParser,
    KNOWN_PROGRAMS,
    BUY_KEYWORDS,
    SELL_KEYWORDS
)

# Constants
WALLET_A_ADDRESS = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"

# Utility Functions
def get_formatted_datetime():
    """Get current UTC datetime formatted as YYYY-MM-DD HH:MM:SS"""
    return datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')

def get_current_user():
    """Get the current user's login name"""
    return "tinotc-72"

def display_system_info():
    """Display current system information"""
    print(f"\nCurrent Date and Time (UTC): {get_formatted_datetime()}")
    print(f"Current User's Login: {get_current_user()}\n")

def _load_keypair() -> Optional[Keypair]:
    """Load keypair from private key"""
    try:
        keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        print(f"✅ Wallet loaded successfully: {keypair.pubkey()}")
        return keypair
    except Exception as e:
        print(f"❌ Failed to load wallet: {e}")
        return None

# Data Classes
@dataclass
class PerformanceStats:
    def __init__(self):
        self.trades_seen = 0
        self.trades_mirrored = 0
        self.successful_mirrors = 0
        self._latencies = []
    
    def update_latency(self, latency_ms: float):
        """Update latency statistics."""
        self._latencies.append(latency_ms)
    
    @property
    def avg_latency(self) -> float:
        """Get average latency in milliseconds."""
        if not self._latencies:
            return 0.0
        return sum(self._latencies) / len(self._latencies)
    
    def print_stats(self):
        print("\n📊 Performance Tracker")
        print(f"  Wallet A trades seen   : {self.trades_seen}")
        print(f"  Trades mirrored        : {self.trades_mirrored}")
        print(f"  Successful mirrors     : {self.successful_mirrors}")
        print(f"  Avg Mirror Latency (ms): {self.avg_latency:.2f}")

class JitoClient:
    def __init__(self):
        self.url = "https://phoenix.rpc.jito.wtf"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {kz.JITO_UUID}"
        }
        self.session = aiohttp.ClientSession(headers=self.headers)
        
    async def send_bundle(self, bundle: Bundle) -> Optional[str]:
        """Send bundle following docs.jito.wtf"""
        try:
            if not isinstance(bundle, Bundle):
                print(f"❌ Invalid bundle type: {type(bundle)}")
                return None
                
            bundle_json = bundle.to_json()
            if bundle_json is None:
                return None
                
            data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendBundle",
                "params": [bundle_json]
            }
            
            print(f"\n📦 Submitting bundle to Jito...")
            print(f"📝 Bundle transactions: {len(bundle.transactions)}")
            
            async with self.session.post(self.url, json=data) as response:
                response_text = await response.text()
                print(f"🔍 Jito Response Status: {response.status}")
                print(f"🔍 Jito Response: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    if "error" in result:
                        print(f"❌ Jito bundle error: {result['error']}")
                        return None
                    print("✅ Bundle submitted successfully")
                    return result.get('result')
                else:
                    print(f"⚠️ Jito API returned status {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ Jito API request failed: {str(e)}")
            traceback.print_exc()
            return None
        
class CopyTradingBot:
    def __init__(self, keypair: Keypair, target_wallet: str):
        self.keypair = keypair
        self.target_wallet = target_wallet
        self.CURRENT_TIME = get_formatted_datetime()
        self.CURRENT_USER = get_current_user()
        self.rpc_url = RPC_URL
        self.ws_url = WS_URL
        self.client = AsyncClient(self.rpc_url)
        self.stats = PerformanceStats()
        self.executor = FastExecutor(keypair)
        self.tx_parser = WalletATxParser(keypair)  # Initialize the parser
        self.client = AsyncClient(self.rpc_url)
        print("✅ Initialized Solana RPC client")

    def _load_keypair() -> Optional[Keypair]:
        """Load keypair from private key"""
        try:
            keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
            print(f"✅ Wallet loaded successfully: {keypair.pubkey()}")
            return keypair
            
        except Exception as e:
            print(f"❌ Failed to load wallet: {e}")
            return None

    async def trade_menu(bot):  # Added bot parameter
        while True:
            print("\n📈 Trading Menu")
            print("="*50)
            print(f"Current Date and Time (UTC): {get_formatted_datetime()}")
            print(f"Current User's Login: {get_current_user()}\n")
            print("1. Buy")
            print("2. Sell")
            print("3. Return to main menu")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "3":
                break
                
            try:
                amount = float(input("Enter amount to trade: "))
                price = input("Enter price (or press Enter for market price): ")
                price = float(price) if price else None
                
                if choice == "1":
                    execute_trade("buy", amount, price)
                elif choice == "2":
                    execute_trade("sell", amount, price)
            except ValueError:
                print("Invalid input. Please enter valid numbers.")

    def execute_trade(trade_type, amount, price=None):
        """
        Execute a trade
        trade_type: 'buy' or 'sell'
        amount: amount to trade
        price: optional limit price
        """
        current_time = get_formatted_datetime()  # Use our helper function
        
        # Log the trade attempt
        print(f"\nAttempting {trade_type} trade at {current_time}")
        print(f"Amount: {amount}")
        if price:
            print(f"Price: {price}")
        
        try:
            # Simulate trade execution (replace with actual trading logic)
            time.sleep(2)  # Simulate processing time
            print(f"Trade executed successfully!")
            return True
        except Exception as e:
            print(f"Trade failed: {str(e)}")
            return False

    def _analyze_transaction_logs(self, logs: List[str]) -> bool:
        try:
            # Use the class instance's parser
            parsed_result = self.tx_parser.parse_transaction_logs(logs)
            if not parsed_result:
                return False

            # Check if Wallet A is involved
            if not any(self.target_wallet in log for log in logs):
                return False

            # Print useful info
            print("\n🔍 Wallet A Trade Detected:")
            print(f"DEX: {parsed_result['dex']}")
            print(f"Instruction: {parsed_result['instruction']}")
            print(f"Type: {parsed_result['type']}")
            print(f"Program ID: {parsed_result['program_id']}")

            return True

        except Exception as e:
            print(f"❌ Error analyzing transaction logs: {str(e)}")
            traceback.print_exc()
            return False

    def _determine_transaction_type(self, logs: List[str]) -> str:
        """Determine if trade is BUY or SELL"""
        try:
            # Use the class instance's parser
            parsed_result = self.tx_parser.parse_transaction_logs(logs)
            if parsed_result:
                if parsed_result["instruction"] == "Buy":
                    print("✅ Detected Wallet A BUY")
                    return "BUY"
                elif parsed_result["instruction"] == "Sell":
                    print("✅ Detected Wallet A SELL")
                    return "SELL"

        except Exception as e:
            print(f"❌ Error determining transaction type: {str(e)}")
            traceback.print_exc()

        return "UNKNOWN"

    async def initialize(self):
        """Initialize bot components"""
        try:
            print("\n🔧 Initializing bot components...")
            
            # Initialize FastExecutor
            await self.executor.initialize()
            print("✅ FastExecutor initialized")
            
            # Initialize JitoClient with proper error handling
            self.jito_client = JitoClient()
            try:
                # Test Jito connection
                print("\n🔍 Testing connection to London Block Engine...")
                async with aiohttp.ClientSession(headers=self.jito_client.headers) as session:
                    async with session.get(self.jito_client.url) as response:
                        if response.status == 404:
                            print("⚠️ Warning: London Block Engine returned status 404")
                            print("ℹ️ Will use RPC fallback for transactions")
                        elif response.status != 200:
                            print(f"⚠️ Warning: London Block Engine returned status {response.status}")
                        else:
                            print("✅ Jito connection test successful")
            except Exception as e:
                print(f"⚠️ Warning: Could not connect to Jito: {str(e)}")
                print("ℹ️ Will use RPC fallback for transactions")
            
            print("✅ FastExecutor session initialized")
            print("✅ FastExecutor initialized")
            print("✅ JitoClient initialized")
            
            # Print configuration
            print("\n📝 Bot Configuration:")
            print(f"🎯 Target Wallet: {self.target_wallet}")
            print(f"💰 Your Wallet: {self.keypair.pubkey()}")
            print(f"🌐 RPC URL: {self.rpc_url}")
            print(f"📡 WebSocket URL: {self.ws_url}")
            
            print("\n✅ Bot initialization complete")
            return True
            
        except Exception as e:
            print(f"❌ Bot initialization failed: {str(e)}")
            traceback.print_exc()
            return False
    
    async def get_recent_blockhash(self) -> str:
        """Get a recent blockhash from the network"""
        try:
            async with aiohttp.ClientSession() as session:
                json_data = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "confirmed"}]
                }
                async with session.post(self.rpc_url, json=json_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "result" in result and "value" in result["result"]:
                            return result["result"]["value"]["blockhash"]
                        else:
                            raise Exception("Invalid response format")
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ Failed to get blockhash: {str(e)}")
            raise

    def log_stats(self):
        """Log current performance statistics"""
        print("\n📊 Transaction Processing Summary")
        print(f"Total trades seen    : {self.stats.trades_seen}")
        print(f"Trades mirrored      : {self.stats.trades_mirrored}")
        print(f"Successful mirrors   : {self.stats.successful_mirrors}")
        if self.stats.mirror_latencies:
            avg_latency = statistics.mean(self.stats.mirror_latencies)
            print(f"Average latency (ms) : {avg_latency:.2f}")

    async def simulate_transaction(self, tx) -> bool:
        """Simulate a transaction before sending."""
        try:
            encoded_tx = base64.b64encode(bytes(tx)).decode('utf-8')
            
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "simulateTransaction",
                "params": [
                    encoded_tx,
                    {
                        "encoding": "base64",
                        "commitment": "processed",
                        "replaceRecentBlockhash": True
                    }
                ]
            }
            
            print("\n🧪 Simulating transaction...")
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=request) as response:
                    result = await response.json()
                    
                    latency = (time.time() - start_time) * 1000
                    print(f"⏱️ Simulation latency: {latency:.2f}ms")
                    
                    if "result" in result:
                        sim_result = result["result"]["value"]
                        
                        if "err" in sim_result and sim_result["err"]:
                            print(f"❌ Simulation failed: {sim_result['err']}")
                            return False
                            
                        print("✅ Simulation successful")
                        if "logs" in sim_result:
                            print("\n📝 Simulation logs:")
                            for log in sim_result["logs"]:
                                print(f"  {log}")
                        return True
                        
                    print(f"❌ Invalid simulation response: {result}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error simulating transaction: {str(e)}")
            traceback.print_exc()
            return False
    
    async def get_sol_balance(self) -> float:
        """Get current SOL balance."""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [str(self.keypair.pubkey())]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=request) as response:
                    result = await response.json()
                    if "result" in result and "value" in result["result"]:
                        return result["result"]["value"] / 1e9  # Convert lamports to SOL
                        
                    print("❌ Invalid balance response")
                    return 0.0
                    
        except Exception as e:
            print(f"❌ Error getting balance: {str(e)}")
            traceback.print_exc()
            return 0.0

    def _validate_transaction_type(self, tx_type: str) -> bool:
        """Validate transaction type."""
        VALID_TYPES = {"BUY", "SELL"}
        return tx_type in VALID_TYPES

    async def _fetch_transaction(self, signature: str) -> Optional[dict]:
        """
        Fetch transaction details using RPC.
        
        Args:
            signature (str): Transaction signature to fetch
            
        Returns:
            Optional[dict]: Transaction details if successful, None otherwise
        """
        try:
            print(f"\n🔄 Fetching transaction: {signature}")
            
            # Validate signature
            if not signature or len(signature) < 32:
                print("❌ Invalid transaction signature")
                return None
                
            # Prepare request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "base64",
                        "maxSupportedTransactionVersion": 0,
                        "commitment": "confirmed"
                    }
                ]
            }
            
            # Log request time
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=request) as response:
                    # Check response status
                    if response.status != 200:
                        print(f"❌ RPC request failed with status {response.status}")
                        return None
                        
                    result = await response.json()
                    
                    # Calculate and log latency
                    latency = (time.time() - start_time) * 1000
                    print(f"📊 RPC Latency: {latency:.2f}ms")
                    
                    # Validate response
                    if "error" in result:
                        print(f"❌ RPC error: {result['error']}")
                        return None
                        
                    if "result" not in result:
                        print("❌ Invalid RPC response format")
                        return None
                        
                    if not result["result"]:
                        print("⚠️ Transaction not found")
                        return None
                        
                    print("✅ Transaction fetched successfully")
                    return result["result"]
                    
        except aiohttp.ClientError as e:
            print(f"❌ Network error fetching transaction: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding RPC response: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching transaction: {str(e)}")
            traceback.print_exc()
            return None
        
    async def process_transaction_data(self, versioned_tx: VersionedTransaction, tx_type: str, blockhash: str) -> None:
        try:
            start_time = time.time()
            print(f"\n📥 Processing {tx_type} transaction at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get message for better readability
            msg = versioned_tx.message
            
            # First, initialize any needed token accounts
            print("\n🔍 Checking for token accounts...")
            for ix in msg.instructions:
                if ix.program_id_index < len(msg.account_keys):
                    program_id = msg.account_keys[ix.program_id_index]
                    if str(program_id) == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                        for acc_idx in ix.accounts:
                            if acc_idx < len(msg.account_keys):
                                account = msg.account_keys[acc_idx]
                                # If this is a token mint, create ATA if needed
                                try:
                                    ata = await get_associated_token_address(
                                        self.keypair.pubkey(),
                                        account
                                    )
                                    # Check if ATA exists
                                    account_info = await self.client.get_account_info(ata)
                                    if not account_info.value:
                                        print(f"Creating ATA for mint: {account}")
                                        create_ata_ix = create_associated_token_account(
                                            payer=self.keypair.pubkey(),
                                            owner=self.keypair.pubkey(),
                                            mint=account
                                        )
                                        # Send ATA creation transaction
                                        tx = Transaction().add(create_ata_ix)
                                        await self.client.send_transaction(tx, [self.keypair])
                                        print(f"✅ Created ATA for mint: {account}")
                                except Exception as e:
                                    print(f"⚠️ Error checking/creating ATA: {str(e)}")
                                    continue

            # Now proceed with the original transaction processing
            try:
                # Create and sign transaction
                print("\n📝 Creating transaction...")
                tx = create_and_sign_transaction(
                    keypair=self.keypair,
                    instructions=msg.instructions,
                    recent_blockhash=blockhash,
                    account_keys=msg.account_keys,
                    num_required_signatures=msg.header.num_required_signatures,
                    num_readonly_signed_accounts=msg.header.num_readonly_signed_accounts,
                    num_readonly_unsigned_accounts=msg.header.num_readonly_unsigned_accounts
                )

                if not tx:
                    print("❌ Failed to create transaction")
                    return

                # First try Jito bundle
                print("\n🚀 Attempting Jito bundle submission...")
                bundle = Bundle(tx)
                bundle_result = await self.jito_client.send_bundle(bundle)
                
                if bundle_result:
                    print("✅ Jito bundle submitted successfully")
                    self.stats.successful_mirrors += 1
                else:
                    print("⚠️ Jito bundle failed, falling back to RPC...")
                    # RPC fallback
                    sim_result = await self.simulate_transaction(tx)
                    if not sim_result:
                        print("❌ Transaction simulation failed")
                        return

                    print("🚀 Sending via RPC fallback...")
                    sig = await self.client.send_transaction(tx)
                    print(f"✅ RPC transaction submitted: {sig}")
                    self.stats.successful_mirrors += 1

                end_time = time.time()
                latency = (end_time - start_time) * 1000
                print(f"\n⏱️ Processing time: {latency:.2f}ms")
                self.stats.update_latency(latency)

            except Exception as e:
                print(f"❌ Error processing transaction data: {str(e)}")
                traceback.print_exc()
                self.stats.failed_mirrors += 1

        except Exception as e:
            print(f"❌ Error in process_transaction_data: {str(e)}")
            traceback.print_exc()
            self.stats.failed_mirrors += 1
            
    async def clone_transaction_from_wallet_a(raw_tx, your_wallet):
        try:
            print(f"\n📅 Starting clone at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")
            print("🧪 clone_transaction_from_wallet_a STARTED")

            # Decode base64 transaction
            encoded = raw_tx["transaction"][0] if isinstance(raw_tx["transaction"], list) else raw_tx["transaction"]
            tx_bytes = b64decode(encoded)

            from solders.transaction import VersionedTransaction
            from solders.message import VersionedMessage, MessageV0, AddressLookupTableAccount
            from solders.instruction import AccountMeta, Instruction
            from solders.pubkey import Pubkey
            from spl.token.instructions import get_associated_token_address, create_associated_token_account

            tx = VersionedTransaction.from_bytes(tx_bytes)
            msg: VersionedMessage = tx.message

            print(f"✅ Decoded base64 transaction")
            print(f"💰 Using payer: {your_wallet.pubkey()}")

            # Reuse blockhash from Wallet A transaction
            blockhash = raw_tx["transaction"][1]["recentBlockhash"]
            print(f"📦 Using blockhash: {blockhash}")

            # === STEP 1: Collect all token mints and ATAs ===
            print("\n🔍 Step 1: Analyzing token accounts...")
            token_mints = set()
            wallet_a_atas = set()

            # First pass: find all SPL Token program calls
            for ix in msg.instructions:
                if ix.program_id_index < len(msg.account_keys):
                    program_id = msg.account_keys[ix.program_id_index]
                    if str(program_id) == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                        for acc_idx in ix.accounts:
                            if acc_idx < len(msg.account_keys):
                                acc = msg.account_keys[acc_idx]
                                if str(acc) == "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK":
                                    wallet_a_atas.add(str(acc))
                                token_mints.add(str(acc))

            print(f"Found {len(token_mints)} potential token mints")
            print(f"Found {len(wallet_a_atas)} Wallet A ATAs")

            # === STEP 2: Get corresponding ATAs for your wallet ===
            print("\n🔍 Step 2: Processing ATAs...")
            ata_instructions = []
            ata_mappings = {}

            for ata in wallet_a_atas:
                try:
                    ata_info = await fetch_json_rpc(
                        "getAccountInfo", 
                        [ata, {"encoding": "jsonParsed", "commitment": "processed"}]
                    )
                    if ata_info.get("result", {}).get("value"):
                        mint = ata_info["result"]["value"]["data"]["parsed"]["info"]["mint"]

                        your_ata = get_associated_token_address(your_wallet.pubkey(), Pubkey.from_string(mint))
                        ata_mappings[ata] = str(your_ata)

                        your_ata_info = await fetch_json_rpc(
                            "getAccountInfo", 
                            [str(your_ata), {"encoding": "base64"}]
                        )
                        if not your_ata_info.get("result", {}).get("value"):
                            print(f"🔧 Creating your ATA for mint {mint[:8]}...")
                            create_ix = create_associated_token_account(
                                payer=your_wallet.pubkey(),
                                wallet_address=your_wallet.pubkey(),
                                token_mint=Pubkey.from_string(mint)
                            )
                            ata_instructions.append(create_ix)
                        else:
                            print(f"✅ Your ATA exists for mint {mint[:8]}")
                except Exception as e:
                    print(f"⚠️ Error processing ATA {ata}: {str(e)}")

            # === STEP 3: Reconstruct instructions with proper account replacements ===
            print("\n🔍 Step 3: Building instructions...")
            from tx_builder import get_jito_fee_instructions
            jito_ixs = get_jito_fee_instructions(your_wallet.pubkey())

            new_ixs = []
            for ix in msg.instructions:
                program_id = msg.account_keys[ix.program_id_index]
                new_accounts = []
                for idx in ix.accounts:
                    if idx < len(msg.account_keys):
                        key = msg.account_keys[idx]
                        key_str = str(key)
                        if key_str == "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK":
                            key = your_wallet.pubkey()
                        elif key_str in ata_mappings:
                            key = Pubkey.from_string(ata_mappings[key_str])

                        is_signer = idx < msg.header.num_required_signatures
                        is_writable = idx < msg.header.num_required_write_locks
                        new_accounts.append(AccountMeta(key, is_signer, is_writable))

                new_ixs.append(Instruction(program_id, bytes(ix.data), new_accounts))

            # === STEP 3.5: Validate instructions before compilation ===
            print("\n🔍 Validating instructions...")
            
            if not ata_instructions:
                print("✅ No ATA creation needed")
            else:
                print(f"✅ ATA instructions prepared: {len(ata_instructions)}")
            
            print(f"✅ Jito fee instructions prepared: {len(jito_ixs)}")
            print(f"✅ Main instructions prepared: {len(new_ixs)}")
            
            # Validate account replacements
            replaced_count = 0
            for ix in new_ixs:
                for acc in ix.accounts:
                    if str(acc.pubkey) == str(your_wallet.pubkey()):
                        replaced_count += 1
            print(f"✅ Replaced {replaced_count} account references")

            # Check for token program instructions
            token_ix_count = 0
            for ix in new_ixs:
                if str(ix.program_id) == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    token_ix_count += 1
            print(f"✅ Found {token_ix_count} token instructions")

            all_instructions = ata_instructions + jito_ixs + new_ixs

            # === STEP 4: Compile with lookup tables ===
            print("\n🔍 Step 4: Compiling transaction...")
            lookup_tables = []
            if msg.address_table_lookups:
                for lookup in msg.address_table_lookups:
                    try:
                        writable = [msg.loaded_addresses.writable[i] for i in lookup.writable_indexes]
                        readonly = [msg.loaded_addresses.readonly[i] for i in lookup.readonly_indexes]
                        lookup_tables.append(
                            AddressLookupTableAccount(
                                key=lookup.account_key,
                                writable_addresses=writable,
                                readonly_addresses=readonly,
                            )
                        )
                        print(f"✅ Added lookup table: {lookup.account_key}")
                    except Exception as e:
                        print(f"⚠️ Error adding lookup table: {str(e)}")

            try:
                message = MessageV0.try_compile(
                    payer=your_wallet.pubkey(),
                    instructions=all_instructions,
                    address_lookup_table_accounts=lookup_tables,
                    recent_blockhash=blockhash
                )
                print("✅ Message compiled successfully")
            except Exception as e:
                print(f"❌ Message compilation failed: {str(e)}")
                raise e

            # Sign transaction
            tx = VersionedTransaction(message, [your_wallet])
            
            # Verify final transaction
            print("\n🔍 Final Transaction Verification:")
            print(f"• Fee payer: {tx.message.account_keys[0]}")
            print(f"• Total accounts: {len(tx.message.account_keys)}")
            print(f"• Required signatures: {tx.message.header.num_required_signatures}")
            print(f"• Readonly signers: {tx.message.header.num_readonly_signed_accounts}")
            print(f"• Readonly non-signers: {tx.message.header.num_readonly_unsigned_accounts}")
            print(f"• Transaction size: {len(tx.to_bytes_versioned())} bytes")
            print(f"• Instructions: {len(all_instructions)}")
            print(f"• Lookup tables: {len(lookup_tables)}")

            print(f"\n✅ Transaction cloned successfully!")
            print(f"📏 Size: {len(tx.to_bytes_versioned())} bytes")
            print(f"🔑 Signature: {tx.signatures[0]}")
            print(f"⏱️ Clone completed at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")

            return tx

        except Exception as e:
            print(f"\n❌ Error in clone_transaction_from_wallet_a:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            traceback.print_exc()
            return None
    
    async def _get_recent_blockhash(self) -> Optional[str]:
        """Get a recent blockhash from the network using RPC."""
        try:
            # Prepare the RPC request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getLatestBlockhash",
                "params": [{"commitment": "processed"}]
            }
            
            # Make the request
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=request) as response:
                    result = await response.json()
                    
                    if "result" in result and "value" in result["result"]:
                        blockhash = result["result"]["value"]["blockhash"]
                        print(f"📦 Got recent blockhash: {blockhash}")
                        return blockhash
                    else:
                        print("❌ Invalid response format from RPC")
                        return None
                        
        except Exception as e:
            print(f"❌ Error getting recent blockhash: {str(e)}")
            traceback.print_exc()
            return None

    async def start(self):
        print("\n🚀 Copy Trading Bot Initialization")
        print(f"👤 User: {self.CURRENT_USER}")
        print(f"🎯 Target: Wallet A ({self.target_wallet})")
        print(f"💰 Your Wallet: {self.keypair.pubkey()}")
        print(f"⏰ Start time (UTC): {self.CURRENT_TIME}")

    async def _start_websocket(self):
        """Internal method to handle WebSocket connection and message processing"""
        try:
            async with connect(self.ws_url) as ws:
                print("📡 Connected to WebSocket")
                
                # Subscribe to account notifications with logs
                subscribe_message = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {
                            "mentions": [self.target_wallet]
                        },
                        {
                            "commitment": "confirmed",
                            "encoding": "base64"
                        }
                    ]
                }
                
                await ws.send(json.dumps(subscribe_message))
                response = await ws.recv()
                subscription_id = json.loads(response)["result"]
                print(f"✅ Subscribed to logs (ID: {subscription_id})")
                
                print(f"\n📅 Bot started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                print("\n🚀 Bot running - Press Ctrl+C to stop")
                print(f"📊 Waiting for ANY Wallet A trades...\n")
                
                while True:
                    try:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        print(f"🔍 Full message: {json.dumps(data, indent=2)}")
                        
                        if "params" in data and "result" in data["params"]:
                            result = data["params"]["result"]
                            if "value" in result:
                                value = result["value"]
                                
                                if "signature" in value:
                                    signature = value["signature"]
                                    print(f"📝 Found transaction signature: {signature}")
                                    
                                    # Check for transaction error
                                    if "err" in value and value["err"] is not None:
                                        print(f"⚠️ Transaction failed: {value['err']}")
                                        continue
                                    
                                    if "logs" in value:
                                        logs = value["logs"]
                                        if self._analyze_transaction_logs(logs):
                                            print("✅ Found relevant transaction")
                                            tx_data = await self._fetch_transaction(signature)
                                            
                                            if tx_data and "transaction" in tx_data and tx_data["transaction"][0]:
                                                print("✅ Retrieved transaction data")
                                                transaction_data = tx_data["transaction"][0]
                                                
                                                # Determine transaction type
                                                tx_type = self._determine_transaction_type(logs)
                                                if not self._validate_transaction_type(tx_type):
                                                    print("⚠️ Skipping transaction with invalid type")
                                                    continue
                                                
                                                # Get recent blockhash
                                                blockhash = await self._get_recent_blockhash()
                                                if not blockhash:
                                                    print("❌ Failed to get recent blockhash")
                                                    continue
                                                    
                                                try:
                                                    # Decode the transaction
                                                    versioned_tx = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
                                                    
                                                    # Update stats and process transaction
                                                    self.stats.trades_seen += 1
                                                    start_time = time.time()
                                                    
                                                    await self.process_transaction_data(
                                                        versioned_tx=versioned_tx,
                                                        tx_type=tx_type,
                                                        blockhash=blockhash
                                                    )
                                                    
                                                    # Update latency stats
                                                    end_time = time.time()
                                                    latency = (end_time - start_time) * 1000  # Convert to milliseconds
                                                    self.stats.update_latency(latency)
                                                    
                                                except Exception as e:
                                                    print(f"❌ Error processing transaction: {str(e)}")
                                                    traceback.print_exc()
                                            else:
                                                print("❌ Failed to fetch transaction details")
                                        else:
                                            print("ℹ️ Transaction not relevant to our trading strategy")
                                    else:
                                        print("⚠️ No logs found in transaction")
                                else:
                                    print("ℹ️ Non-transaction log message received")
                                    
                    except Exception as e:
                        print(f"❌ Error in websocket message handler: {str(e)}")
                        traceback.print_exc()
                        continue
                        
        except Exception as e:
            print(f"❌ Error in websocket connection: {str(e)}")
            traceback.print_exc()
        finally:
            print("\n👋 Websocket connection closed")

    async def start(self):
        """Start the trading bot with automatic reconnection"""
        while True:
            try:
                await self._start_websocket()
            except websockets.exceptions.ConnectionClosed:
                print("📡 WebSocket disconnected, reconnecting...")
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Received stop signal")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                await asyncio.sleep(1)

    async def stop(self):
        """Stop the trading bot"""
        await self.executor.close()
        stop_time = datetime.now(UTC)
        
        print("\n👋 Bot stopped")
        print(f"⏰ Stop time (UTC): {stop_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📊 Performance Tracker")
        print(f"  Wallet A trades seen   : {self.stats.trades_seen}")
        print(f"  Trades mirrored        : {self.stats.trades_mirrored}")
        print(f"  Successful mirrors     : {self.stats.successful_mirrors}")
        print(f"  Avg Mirror Latency (ms): {self.stats.avg_latency:.2f}")

    async def cleanup(self):
        """Cleanup resources when bot is stopping."""
        try:
            if hasattr(self, 'client'):
                await self.client.close()
                print("✅ Closed Solana RPC client")
                
            if hasattr(self, 'fast_executor'):
                await self.fast_executor.close()
                print("✅ Closed FastExecutor")
                
        except Exception as e:
            print(f"❌ Error during cleanup: {str(e)}")

def display_trading_menu():
    """Display trading options and handle user input"""
    while True:
        print("\n💹 Trading Menu")
        print("=" * 50)
        print("1. Execute Manual Buy")
        print("2. Execute Manual Sell")
        print("3. Start Automated Copy Trading")
        print("4. Return to Main Menu")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1" or choice == "2":
            try:
                amount = float(input("Enter amount to trade: "))
                price = input("Enter price (or press Enter for market price): ")
                price = float(price) if price else None
                
                trade_type = "buy" if choice == "1" else "sell"
                # Use the existing execute_trade function from your bot
                bot = CopyTradingBot(_load_keypair(), WALLET_A_ADDRESS)
                asyncio.run(bot.process_transaction_data(
                    versioned_tx=None,  # We'll need to create a transaction
                    tx_type=trade_type.upper(),
                    blockhash=asyncio.run(bot._get_recent_blockhash())
                ))
            except ValueError:
                print("❌ Invalid input. Please enter valid numbers.")
        elif choice == "3":
            print("\n🚀 Starting automated copy trading...")
            asyncio.run(main())
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice. Please try again.")

def main_menu():
    """Main menu of the application"""
    while True:
        print("\n🏦 Main Menu")
        print("=" * 50)
        display_system_info()  # Show current time and user
        print("1. View Wallet")
        print("2. Trade")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            # We'll need to implement wallet view functionality
            keypair = _load_keypair()
            if keypair:
                bot = CopyTradingBot(keypair, WALLET_A_ADDRESS)
                balance = asyncio.run(bot.get_sol_balance())
                print(f"\n💰 Current SOL Balance: {balance:.4f} SOL")
        elif choice == "2":
            display_trading_menu()
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

async def main():
    print("\n🚀 Welcome to Solana Trading Bot")
    print("="*50)
    print(f"Current Date and Time (UTC): {get_formatted_datetime()}")
    print(f"Current User's Login: {get_current_user()}")
    print("="*50 + "\n")
    
    try:
        # Load wallet
        keypair = _load_keypair()
        if not keypair:
            return
            
        # Create bot
        target_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"  # Wallet A address
        bot = CopyTradingBot(keypair, target_wallet)
        
        # Initialize bot
        if not await bot.initialize():
            print("❌ Bot initialization failed")
            return
            
        # Main menu loop
        while True:
            print("\n🏦 Main Menu")
            print("="*50 + "\n")
            print(f"Current Date and Time (UTC): {get_formatted_datetime()}")
            print(f"Current User's Login: {get_current_user()}\n")
            print("1. View Wallet")
            print("2. Trade")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                print(f"✅ Wallet loaded successfully: {bot.wallet.pubkey()}")
                balance = await bot.get_sol_balance()
                print(f"💰 Current SOL Balance: {balance:.9f} SOL")
                
            elif choice == "2":
                await trade_menu(bot)  # Pass bot to trade_menu
                
            elif choice == "3":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\n🛑 Received stop signal")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        traceback.print_exc()
    finally:
        if 'bot' in locals():
            await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
