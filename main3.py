# main.py3 - uses Replicator.py 

import os
import asyncio
import json
import base64
import statistics
import time
from typing import List, Dict, Union, Optional
from dataclasses import dataclass
from datetime import datetime, UTC
from statistics import mean
import websockets
from websockets.client import connect
import aiohttp
import traceback
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from base64 import b64decode
from utils import fetch_json_rpc
from simulate_clone import clone_transaction_from_wallet_a
from logger import log_mirrored_trade

# Solana imports
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta

# Jito imports
from models import Bundle   # Only import Bundle once
from jito_service import JitoClient  # From our local file
from datetime import datetime, timezone
from solders.signature import Signature
from replicator import Replicator

# Local imports
import keyZ as kz
from fast_executor import FastExecutor
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

WALLET_A_ADDRESS = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"  # Your target wallet
# main.py

import asyncio
import base58
from solders.keypair import Keypair
from replicator import Replicator
from datetime import datetime, timezone

# Configuration
PRIVATE_KEY = kz.BULLX_NEO_PRIVATE_KEY_QM


def get_current_user() -> str:
    """Get current user's login name"""
    return os.getlogin()

def get_formatted_datetime() -> str:
    """Get current UTC datetime formatted as YYYY-MM-DD HH:MM:SS"""
    return datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

def get_timestamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

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
        self.client = AsyncClient(self.rpc_url)
        print("✅ Initialized Solana RPC client")
        self.RELEVANT_PROGRAMS = {
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # Pump program
            "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95",  # Trading program
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"    # Core trading program
        }

    async def initialize(self):
        """Initialize bot components"""
        try:
            print("\n🔧 Initializing bot components...")
            
            # Initialize FastExecutor
            await self.executor.initialize()
            print("✅ FastExecutor initialized")
            
            # Initialize JitoClient
            self.jito_client = JitoClient()
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
    
    def _analyze_transaction_logs(self, logs: List[str]) -> bool:
        """
        Analyze transaction logs to determine if they're relevant for our trading strategy.
        
        Args:
            logs (List[str]): Transaction logs to analyze
            
        Returns:
            bool: True if transaction is relevant, False otherwise
        """
        try:
            # Define programs we're interested in
            RELEVANT_PROGRAMS = {
                "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # Pump program
                "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95",  # Trading program
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"    # Core trading program
            }
            
            # Check if any of our target programs are involved
            program_found = False
            for log in logs:
                for program in RELEVANT_PROGRAMS:
                    if f"Program {program} invoke" in log:
                        program_found = True
                        break
                if program_found:
                    break
                    
            if not program_found:
                print("ℹ️ No relevant programs found in transaction")
                return False

            # Look for specific instructions
            for log in logs:
                # Check for Buy/Sell instructions
                if "Instruction: Buy" in log or "Instruction: Sell" in log:
                    print("✅ Found Buy/Sell instruction")
                    return True
                    
                # Check for Pump instructions
                if "Instruction: PumpBuy" in log or "Instruction: PumpSell" in log:
                    print("✅ Found Pump Buy/Sell instruction")
                    return True
                    
                # Check for AMM instructions
                if "Instruction: PumpAmmSwap" in log:
                    print("✅ Found AMM Swap instruction")
                    return True

            print("ℹ️ No relevant instructions found")
            return False

        except Exception as e:
            print(f"❌ Error analyzing transaction logs: {str(e)}")
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

    def _determine_transaction_type(self, logs: List[str]) -> str:
        """Determine transaction type from logs."""
        for log in logs:
            if "Instruction: Buy" in log or "Instruction: PumpBuy" in log:
                print("✅ Detected BUY transaction")
                return "BUY"
            elif "Instruction: Sell" in log or "Instruction: PumpSell" in log:
                print("✅ Detected SELL transaction")
                return "SELL"
        print("⚠️ Unknown transaction type")
        return "UNKNOWN"
        
    async def process_transaction_data(self, versioned_tx: VersionedTransaction, tx_type: str, blockhash: str) -> None:
        """
        Process and submit a transaction copy.
        
        Args:
            versioned_tx (VersionedTransaction): The transaction to process
            tx_type (str): Type of transaction ("BUY" or "SELL")
            blockhash (str): Recent blockhash to use
        """
        try:
            start_time = time.time()
            print(f"\n📥 Processing {tx_type} transaction at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🔑 Your wallet: {self.keypair.pubkey()}")
            print(f"🎯 Following wallet: {WALLET_A_ADDRESS}")

            # Get current balance
            try:
                balance = await self.get_sol_balance()  # Make this async
                print(f"\n💰 Current balance: {balance:.9f} SOL")
                
                # Add balance check
                if balance < 0.1:  # Adjust minimum balance as needed
                    print("⚠️ Warning: Low balance")
            except Exception as e:
                print(f"⚠️ Could not fetch balance: {str(e)}")

            # Log transaction info
            print(f"✅ Decoded VersionedTransaction ({len(bytes(versioned_tx))} bytes)")
            print(f"📦 Using blockhash: {blockhash}")

            try:
                # Get message for better readability
                msg = versioned_tx.message
                
                # Enhanced validation
                if not msg:
                    print("❌ Invalid message: Message is None")
                    return
                if not msg.instructions:
                    print("❌ Invalid message: No instructions")
                    return
                if not msg.account_keys:
                    print("❌ Invalid message: No account keys")
                    return

                print("\n🔍 Pre-processing Analysis:")
                print(f"Instructions count: {len(msg.instructions)}")
                print(f"Account keys count: {len(msg.account_keys)}")
                print(f"Required signatures: {msg.header.num_required_signatures}")
                
                # Log programs
                print("\nPrograms involved:")
                for idx, ix in enumerate(msg.instructions):
                    program_id = msg.account_keys[ix.program_id_index]
                    print(f"{idx+1}. {program_id}")

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

                # Verify transaction
                print("\n🔍 Post-creation verification:")
                print(f"Transaction size: {len(bytes(tx))} bytes")
                if not tx.signatures:
                    print("❌ Error: No signature present")
                    return
                print(f"Signature: {tx.signatures[0]}")

                # Simulate transaction
                print("\n🧪 Simulating transaction...")
                sim_result = await self.simulate_transaction(tx)  # Make this async
                if not sim_result:
                    print("❌ Transaction simulation failed")
                    return

                print("✅ Simulation successful")

                # Create and verify bundle
                print("\n📦 Creating bundle...")
                bundle = Bundle(tx)
                
                if not isinstance(bundle, Bundle):
                    print("❌ Error: Invalid bundle type")
                    return
                    
                if not bundle.transactions:
                    print("❌ Error: Empty bundle")
                    return

                print("✅ Bundle created successfully")
                print(f"Bundle transaction count: {len(bundle.transactions)}")

                # Submit transaction
                print("\n🚀 Submitting transaction...")
                print(f"💰 Fee payer: {self.keypair.pubkey()}")
                print(f"📝 Transaction size: {len(bytes(tx))} bytes")

                result = await self.fast_executor.send_bundle(bundle)  # Make this async
                
                if not result:
                    print("❌ Transaction submission failed")
                    self.stats.failed_mirrors += 1
                    return

                # Update stats on success
                self.stats.successful_mirrors += 1
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                print(f"\n✅ Transaction submitted successfully")
                print(f"⏱️ Processing time: {latency:.2f}ms")

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

def _load_keypair() -> Optional[Keypair]:
    """Load keypair from private key"""
    try:
        keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        print(f"✅ Wallet loaded successfully: {keypair.pubkey()}")
        return keypair
        
    except Exception as e:
        print(f"❌ Failed to load wallet: {e}")
        return None

async def main():
    try:
        print("\n=== Copy Trading Bot ===")
        print(f"Start Time (UTC): {get_timestamp()}")
        print(f"User: tinotc-72")
        
        # Initialize wallet
        private_key_bytes = base58.b58decode(PRIVATE_KEY)
        wallet = Keypair.from_bytes(private_key_bytes)
        print(f"Wallet: {wallet.pubkey()}")
        
        # Create and initialize replicator
        replicator = Replicator(wallet)
        
        if await replicator.initialize():
            print("\n🚀 Starting copy trading...")
            await replicator.run()
        else:
            print("❌ Failed to initialize replicator")
            
    except KeyboardInterrupt:
        print("\n👋 Stopping bot...")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
