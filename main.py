# main.py

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

# Solana imports
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta

# Jito imports
from models import Bundle   # Only import Bundle once
from jito_service import JitoClient  # From our local file

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

def get_current_user() -> str:
    """Get current user's login name"""
    return os.getlogin()

def get_formatted_datetime() -> str:
    """Get current UTC datetime formatted as YYYY-MM-DD HH:MM:SS"""
    return datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

@dataclass
class PerformanceStats:
    trades_seen: int = 0
    trades_mirrored: int = 0
    successful_mirrors: int = 0
    mirror_latencies: List[float] = None

    def __post_init__(self):
        self.mirror_latencies = []

    @property
    def avg_latency(self) -> float:
        if not self.mirror_latencies:
            return 0.0
        return mean(self.mirror_latencies)

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
        
async def fetch_transaction(signature: str, rpc_url: str) -> Optional[dict]:
    """Fetch full transaction details from a signature"""
    try:
        async with aiohttp.ClientSession() as session:
            json_data = {
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
            async with session.post(rpc_url, json=json_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result and result["result"]:
                        return result["result"]
                    print(f"❌ No transaction data found for signature: {signature}")
                    return None
                print(f"❌ Failed to fetch transaction: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"❌ Error fetching transaction: {str(e)}")
        return None

class CopyTradingBot:
    def __init__(self, keypair: Keypair, target_wallet: str):
        self.keypair = keypair
        self.target_wallet = target_wallet
        self.CURRENT_TIME = get_formatted_datetime()
        self.CURRENT_USER = get_current_user()
        self.rpc_url = RPC_URL
        self.ws_url = WS_URL
        self.stats = PerformanceStats()
        self.executor = FastExecutor(keypair)

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
        

    async def process_transaction_data(self, data: str):
        try:
            start_time = time.time()
            print("\n📥 Processing transaction")
            print(f"📝 Data type: {type(data)}")
            print(f"📝 String length: {len(data)}")
            print(f"📝 Preview: {data[:64]}...")

            # Decode transaction
            try:
                decoded = base64.b64decode(data)
                print(f"✅ Base64 decode successful ({len(decoded)} bytes)")
                versioned_tx = VersionedTransaction.from_bytes(decoded)
                message = versioned_tx.message
                
                # Get blockhash
                blockhash = await self.get_recent_blockhash()
                print(f"✅ Got blockhash: {blockhash[:10]}...")
                
                # Create new instructions
                new_instructions = []
                print(f"\n🔄 Converting {len(message.instructions)} instructions...")
                
                for idx, ix in enumerate(message.instructions):
                    program_id = message.account_keys[ix.program_id_index]
                    accounts = []
                    for acc_idx in ix.accounts:
                        if acc_idx < len(message.account_keys):
                            pubkey = message.account_keys[acc_idx]
                            is_signer = acc_idx < message.header.num_required_signatures
                            is_writable = (
                                acc_idx < (message.header.num_required_signatures - 
                                        message.header.num_readonly_signed_accounts) or
                                (acc_idx >= message.header.num_required_signatures and 
                                acc_idx < (len(message.account_keys) - 
                                        message.header.num_readonly_unsigned_accounts))
                            )
                            meta = AccountMeta(
                                pubkey=pubkey,
                                is_signer=is_signer,
                                is_writable=is_writable
                            )
                            accounts.append(meta)
                    
                    new_ix = Instruction(
                        program_id=program_id,
                        accounts=accounts,
                        data=ix.data
                    )
                    new_instructions.append(new_ix)
                    print(f"✅ Instruction {idx + 1} converted")

                # Create transaction with instructions
                tx = create_and_sign_transaction(
                    keypair=self.keypair,
                    instructions=new_instructions,
                    recent_blockhash=blockhash
                )
                
                if tx:  # If transaction was created successfully
                    # Create bundle using the official Jito Bundle
                    bundle = Bundle(transactions=[tx])
                    self.stats.trades_mirrored += 1
                    print("\n✅ Transaction created successfully")
                    
                    # Submit bundle
                    signature = await self.executor.submit_transaction(bundle)
                    if signature:
                        self.stats.successful_mirrors += 1
                        end_time = time.time()
                        latency = (end_time - start_time) * 1000
                        self.stats.mirror_latencies.append(latency)
                        print(f"🎯 Transaction submitted: {signature}")
                        print(f"⚡ Execution time: {latency:.2f}ms")
                    else:
                        print("❌ Transaction submission failed")
                else:
                    print("❌ Failed to create transaction")

            except Exception as e:
                print(f"❌ Error processing transaction: {str(e)}")
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            traceback.print_exc()
        finally:
            self.log_stats()

    # Update the initialization message
    async def start(self):
        print("\n🚀 Copy Trading Bot Initialization")
        print(f"👤 User: {self.CURRENT_USER}")
        print(f"🎯 Target: Wallet A ({self.target_wallet})")
        print(f"💰 Your Wallet: {self.keypair.pubkey()}")
        print(f"⏰ Start time (UTC): {self.CURRENT_TIME}")

    def _analyze_transaction_logs(self, logs: List[str]) -> bool:
        """Analyze transaction logs to determine if they're relevant."""
        relevant_instructions = {
            "PumpAmmSwap", "Swap", "Exchange", "Transfer",
            "TransferChecked", "Sell", "Buy", "PumpSell", "PumpBuy"
        }
        
        for log in logs:
            # Check for specific instructions
            if "Instruction:" in log:
                instruction = log.split("Instruction: ")[-1].strip()
                if instruction in relevant_instructions:
                    print(f"✅ Found relevant instruction: {instruction}")
                    return True
                
            # Check for our target wallet
            if self.target_wallet in log:
                print(f"✅ Found target wallet in log")
                return True
                
            # Check for specific program invocations
            if "Program" in log and any(
                program in log for program in [
                    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
                    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # Swap program
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"   # Additional swap program
                ]
            ):
                print(f"✅ Found relevant program invocation")
                return True
        
        return False

    async def _start_websocket(self):
        """Internal method to handle WebSocket connection and message processing"""
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
            
            print("\n🚀 Bot running - Press Ctrl+C to stop")
            print(f"📊 Waiting for ANY Wallet A trades...\n")
            
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                print(f"🔍 Full message: {json.dumps(data, indent=2)}")
                
                if "params" in data and "result" in data["params"]:
                    result = data["params"]["result"]
                    if "value" in result:
                        value = result["value"]
                        
                        if "signature" in value and "err" in value and value["err"] is None:
                            signature = value["signature"]
                            print(f"📝 Found transaction signature: {signature}")
                            
                            if "logs" in value:
                                logs = value["logs"]
                                if self._analyze_transaction_logs(logs):
                                    print("✅ Found relevant transaction")
                                    tx_data = await fetch_transaction(signature, self.rpc_url)
                                    if tx_data and "transaction" in tx_data:
                                        print("✅ Retrieved transaction data")
                                        transaction_data = tx_data["transaction"][0]
                                        if transaction_data:
                                            self.stats.trades_seen += 1
                                            await self.process_transaction_data(transaction_data)
                                        else:
                                            print("❌ Empty transaction data")
                                    else:
                                        print("❌ Failed to fetch transaction details")
                                else:
                                    print("ℹ️ Transaction not relevant to our trading strategy")
                        else:
                            if "signature" in value and value["err"] is not None:
                                print(f"⚠️ Transaction failed: {value['err']}")
                            else:
                                print("ℹ️ Non-transaction log message received")

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
    """Main entry point"""
    print("\n🚀 Starting Copy Trading Bot")
    print("=" * 50)
    print(f"Current Date and Time (UTC): {get_formatted_datetime()}")
    print(f"Current User's Login: {get_current_user()}")
    print("=" * 50)
    
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
        
        # Start bot
        await bot.start()
        
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