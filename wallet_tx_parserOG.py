# wallet_tx_parser.py - delete the files being used as wallet_tx_parser.py after replicator attempt using main3.py (delete that too)

# wallet_tx_parser.py

import asyncio
import aiohttp
from datetime import datetime, UTC
from typing import Optional, Dict, Any
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
from typing import Dict, Any, List
import json

from config import WALLET_A_ADDRESS, RPC_URL
# Add near the top with other imports
DEBUG = True

# === Platform Detection ===
KNOWN_PROGRAMS = {
    "Pump.fun": [
    "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",  # old router
    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"   # ✅ new router seen in Wallet A's buy
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
    "BuyExactIn", "SwapExactInput", "Instruction: Swap", "Instruction: MintTo",
    "Instruction: Deposit", "Instruction: Transfer", "Instruction: TransferChecked",
    "Instruction: InitializeAccount", "CreateIdempotent", "InitializeAccount3",
    "PerpPlaceOrderV2", "PerpUpdateFunding", "HealthRegionBegin"
]

SELL_KEYWORDS = [
    "Sell", "PumpSell", "SwapBaseOutput", "SwapExactOutput",
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

    async def create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

async def parse_transaction_logs(logs: List[str]) -> Dict[str, Any]:
    """Parse transaction logs from websocket data"""
    try:
        # Your existing parsing logic here
        pass
    except Exception as e:
        print(f"❌ Error parsing transaction logs: {str(e)}")
        return {}
    
    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_next_transaction(self):
        """Monitor and get the next transaction from Wallet A"""
        try:
            session = await self.create_session()
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
                            
                            # Get transaction details
                            tx_payload = {
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "getTransaction",
                                "params": [
                                    signature,
                                    {
                                        "encoding": "base64",
                                        "maxSupportedTransactionVersion": 0,
                                        "commitment": "confirmed",  # Add this
                                        "rewards": False,           # Add this
                                        "encoding": "json"         # Change to json instead of base64
                                    }
                                ]
                            }
                            
                            async with session.post(RPC_URL, json=tx_payload) as tx_response:
                                if tx_response.status == 200:
                                    tx_data = await tx_response.json()
                                    if "result" in tx_data and tx_data["result"]:
                                        print(f"🔍 Found new transaction from Wallet A: {signature[:8]}...")
                                        return tx_data["result"]
            
            return None

        except Exception as e:
            print(f"❌ Error monitoring Wallet A: {e}")
            return None

    # Keep your existing parse_transaction method with all the platform detection logic

    async def __aenter__(self):
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()

def parse_transaction_logs(logs: list) -> Optional[Dict[str, Any]]:
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

        # Check for program invocation
        for log in logs:
            # Find program invocation
            if "Program " in log and " invoke" in log:
                program = log.split("Program ")[1].split(" invoke")[0].strip()
                
                # Match program to known DEX
                for dex_name, program_ids in KNOWN_PROGRAMS.items():
                    if isinstance(program_ids, list):
                        if program in program_ids:
                            result["dex"] = dex_name
                            result["program_id"] = program
                            break
                    elif program == program_ids:
                        result["dex"] = dex_name
                        result["program_id"] = program
                        break

                if result["program_id"]:
                    break

        # No known program found
        if not result["program_id"]:
            return None

        # Find instruction type
        for log in logs:
            # Check for buy keywords
            for keyword in BUY_KEYWORDS:
                if keyword in log:
                    result["instruction"] = "Buy"
                    result["type"] = keyword
                    return result

            # Check for sell keywords
            for keyword in SELL_KEYWORDS:
                if keyword in log:
                    result["instruction"] = "Sell"
                    result["type"] = keyword
                    return result

        # If we found a program but no instruction type, it might be a trade we don't recognize
        if result["program_id"]:
            print(f"⚠️ Unknown instruction type for program: {result['program_id']}")
            if DEBUG:
                print("First few logs:")
                for log in logs[:3]:
                    print(f"  {log[:100]}...")

        return None

    except Exception as e:
        print(f"❌ Error parsing transaction logs: {str(e)}")
        return None
    
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

# Add to existing wallet_tx_parser.py
async def analyze_transaction_type(logs: list, wallet_a: str) -> tuple[bool, str, bool]:
    """Analyze transaction logs to determine trade type"""
    try:
        parsed_tx = parse_transaction_logs(logs)
        if not parsed_tx:
            return False, "", False
            
        is_trade = parsed_tx.get('type') in TRADE_KEYWORDS
        if not is_trade:
            return False, "", False
            
        trade_desc = f"{parsed_tx['dex']}:{parsed_tx['type']}:{parsed_tx['direction']}"
        is_wallet_a_trade = parsed_tx.get('trader') == wallet_a
        
        return is_trade, trade_desc, is_wallet_a_trade
    except Exception as e:
        print(f"❌ Error analyzing transaction: {str(e)}")
        return False, "", False
    
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
