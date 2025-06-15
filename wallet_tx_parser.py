# wallet_tx_parser.py

import asyncio
import aiohttp
import traceback
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from simulate_clone import clone_transaction_from_wallet_a
from tx_builder import (
    build_buy_tx,
    build_sell_tx,
    build_wallet_a_tx,
    build_meteora_tx,
    build_raydium_tx,
)
from log_utils import extract_mint_from_logs
from utils import WALLET_A, RPC_URL
import json

from config import WALLET_A_ADDRESS, RPC_URL

# Debug settings
DEBUG = True
TRACE_LOGS = True

def log_debug(msg: str):
    if DEBUG:
        print(f"🔍 {msg}")

def trace_logs(logs: list):
    if TRACE_LOGS:
        print("\nTransaction Logs:")
        for i, log in enumerate(logs[:10]):
            print(f"{i}: {log}")

# === Platform Detection ===
KNOWN_PROGRAMS = {
    "Pump.fun": [
        "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # new router
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # core trading program
        "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj"    # trading program
    ],
    "Photon": "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi",
    "Meteora": "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi",
    "Raydium": "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",
    "Jupiter": [
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
        "ComputeBudget111111111111111111111111111111"
    ],
    "Orca": [
        "9WwGxj1rPMZZg4KhzWsxRxij3hiKkZyzN1TfXR8zzGzv",
        "DJGjxez7UAnj5aDStQuFGkkZLC7zfnjK1zxKnXxjGqGp"
    ],
    "Mango": [
        "4MEXyRtP4zXcrnUKHxJu4EeZnm8ekep4iXAgGzFn1MMm",
        "98TxMnAZwZmjffEyjcBLv8Z1mdFyPLkXbdLeaAZuavY8"
    ]
}

BUY_KEYWORDS = [
    "Buy", "PumpBuy", "Swap", "SwapBaseInput", "PumpAmmSwap",
    "BuyExactIn",  # Common keyword
    "SwapExactInput", "Instruction: Swap", "Instruction: MintTo",
    "Instruction: BuyExactIn",  # Explicit instruction
    "Instruction: Deposit", "Instruction: Transfer", "Instruction: TransferChecked",
    "Instruction: InitializeAccount", "CreateIdempotent", "InitializeAccount3",
    "PerpPlaceOrderV2", "PerpUpdateFunding", "HealthRegionBegin"
]

SELL_KEYWORDS = [
    "Sell", "PumpSell", "SwapBaseOutput", "SwapExactOutput",
    "SellExactIn",  # Common keyword
    "Instruction: SellExactIn",  # Explicit instruction
    "Instruction: Burn", "Instruction: Withdraw", "Instruction: CloseAccount",
    "Instruction: CollectFee"
]

class WalletATxParser:
    def __init__(self, wallet: Keypair):
        self.wallet = wallet
        self.pubkey = wallet.pubkey()
        self.last_signature = None
        self.session = None
        print(f"📝 Initialized TX parser for wallet: {self.pubkey}")
        print(f"👀 Monitoring Wallet A: {WALLET_A}")
        print(f"⏰ Current Time (UTC): 2025-06-15 14:30:51")
        print(f"👤 Current User: tinotc-72")

    async def create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def parse_transaction_logs(self, logs: list) -> Optional[Dict[str, Any]]:
        """Parse transaction logs to identify trade information"""
        if not logs:
            return None

        try:
            # Initialize result dictionary
            result = {
                "program_id": None,
                "instruction": None,
                "dex": None,
                "type": None
            }

            # First pass - look for Pump.fun or LanMV9 programs
            for i, log in enumerate(logs):
                if "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke" in log:
                    result["dex"] = "Pump.fun"
                    result["program_id"] = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
                    break
                elif "Program LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj invoke" in log:
                    result["dex"] = "Pump.fun"
                    result["program_id"] = "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj"
                    break

            if result["program_id"]:
                # Second pass - look for instruction type
                for log in logs:
                    # Check for buy instructions
                    if "Instruction: BuyExactIn" in log:
                        result["instruction"] = "Buy"
                        result["type"] = "BuyExactIn"
                        print("✅ Detected Pump.fun BUY (BuyExactIn) - Processing trade...")
                        return result
                    # Check for sell instructions
                    elif "Instruction: SellExactIn" in log:
                        result["instruction"] = "Sell"
                        result["type"] = "SellExactIn"
                        print("✅ Detected Pump.fun SELL (SellExactIn) - Processing trade...")
                        return result

                # If we haven't returned yet, check other keywords
                for log in logs:
                    for keyword in BUY_KEYWORDS:
                        if keyword in log:
                            result["instruction"] = "Buy"
                            result["type"] = keyword
                            print(f"✅ Detected Pump.fun BUY ({keyword}) - Processing trade...")
                            return result
                    for keyword in SELL_KEYWORDS:
                        if keyword in log:
                            result["instruction"] = "Sell"
                            result["type"] = keyword
                            print(f"✅ Detected Pump.fun SELL ({keyword}) - Processing trade...")
                            return result

            if DEBUG and result["program_id"]:
                print(f"⚠️ Unknown instruction type for program: {result['program_id']}")
                print("First few logs:")
                for log in logs[:5]:
                    print(f"  {log[:100]}...")

            return None

        except Exception as e:
            print(f"❌ Error parsing transaction logs: {str(e)}")
            traceback.print_exc()
            return None

    async def get_next_transaction(self):
        """Monitor and get the next transaction from Wallet A"""
        try:
            session = await self.create_session()
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    # Get recent signatures for Wallet A
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignaturesForAddress",
                        "params": [
                            str(WALLET_A),
                            {
                                "limit": 1,
                                "before": self.last_signature
                            }
                        ]
                    }

                    async with session.post(RPC_URL, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if "result" in data and data["result"]:
                                signature = data["result"][0]["signature"]
                                
                                # If this is a new transaction
                                if signature != self.last_signature:
                                    self.last_signature = signature
                                    
                                    # Get transaction details with improved error handling
                                    tx_data = await self.get_transaction_details(signature)
                                    if tx_data:
                                        print(f"🔍 Found new transaction from Wallet A: {signature[:8]}...")
                                        
                                        # Parse logs to determine if it's a relevant trade
                                        if "meta" in tx_data and "logMessages" in tx_data["meta"]:
                                            trade_info = self.parse_transaction_logs(tx_data["meta"]["logMessages"])
                                            if trade_info:  # If it's a relevant trade
                                                print(f"📊 Trade Details:")
                                                print(f"   DEX: {trade_info['dex']}")
                                                print(f"   Type: {trade_info['type']}")
                                                print(f"   Instruction: {trade_info['instruction']}")
                                                return tx_data
                                        
                                    return None

                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        
                except Exception as e:
                    print(f"⚠️ Attempt {attempt + 1} error: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
            
            return None

        except Exception as e:
            print(f"❌ Error monitoring Wallet A: {e}")
            traceback.print_exc()
            return None

    async def get_transaction_details(self, signature: str) -> Optional[dict]:
        """Get detailed transaction information with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        signature,
                        {
                            "encoding": "json",
                            "maxSupportedTransactionVersion": 0,
                            "commitment": "confirmed"
                        }
                    ]
                }
                
                async with self.session.post(RPC_URL, json=tx_payload) as tx_response:
                    if tx_response.status == 200:
                        tx_data = await tx_response.json()
                        if "result" in tx_data and tx_data["result"]:
                            return tx_data["result"]
                    
                    print(f"⚠️ Attempt {attempt + 1}: Failed to fetch transaction details")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} error: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))
                
        return None

    async def __aenter__(self):
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()
        
def extract_mint_from_meta(data: dict) -> str | None:
    post_balances = data.get("meta", {}).get("postTokenBalances", [])
    if post_balances and "mint" in post_balances[0]:
        return post_balances[0]["mint"]

    instructions = data.get("transaction", {}).get("message", {}).get("instructions", [])
    for ix in instructions:
        parsed = ix.get("parsed", {})
        if isinstance(parsed, dict) and parsed.get("type") == "transferChecked":
            return parsed.get("info", {}).get("mint")
    return None

def get_program_ids(data: dict) -> list[str]:
    try:
        transaction = data.get("transaction", {})
        message = transaction.get("message", {})
        instructions = message.get("instructions", [])
        return [
            ix.get("programId")
            for ix in instructions
            if isinstance(ix, dict) and "programId" in ix
        ]
    except Exception as e:
        print(f"⚠️ get_program_ids failed: {e}")
        return []