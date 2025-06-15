# wallet_tx_parser.py

import asyncio
import aiohttp
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from utils import WALLET_A, RPC_URL
from config import WALLET_A_ADDRESS, RPC_URL
from log_utils import extract_mint_from_logs
from tx_builder import (
    build_buy_tx,
    build_sell_tx,
    build_wallet_a_tx,
    build_meteora_tx,
    build_raydium_tx,
)

DEBUG = True

# === Platform Detection ===
KNOWN_PROGRAMS = {
    "Pump.fun": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
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


# wallet_tx_parser.py

# wallet_tx_parser.py

class WalletATxParser:
    def __init__(self, wallet: Keypair):
        self.wallet = wallet
        self.pubkey = wallet.pubkey()
        self.last_signature = None
        self.session = None
        self.processed_signatures = set()
        print(f"📝 Initialized TX parser for wallet: {self.pubkey}")
        print(f"👀 Monitoring Wallet A: {WALLET_A}")

    async def create_session(self):
        """Create aiohttp session if it doesn't exist"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            print("📡 Created new HTTP session")
        return self.session

    async def close_session(self):
        """Close aiohttp session if it exists"""
        if self.session and not self.session.closed:
            await self.session.close()
            print("📡 Closed HTTP session")
            self.session = None

    async def get_next_transaction(self) -> Optional[Dict]:
        """Monitor and get the next transaction from Wallet A"""
        try:
            # Ensure we have a session
            if not self.session or self.session.closed:
                self.session = await self.create_session()

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

            async with self.session.post(RPC_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and data["result"]:
                        signature = data["result"][0]["signature"]
                        
                        # Skip if already processed
                        if signature in self.processed_signatures:
                            return None
                            
                        self.last_signature = signature
                        self.processed_signatures.add(signature)

                        tx_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getTransaction",
                            "params": [
                                signature,
                                {
                                    "encoding": "base64",
                                    "maxSupportedTransactionVersion": 0,
                                    "commitment": "confirmed",
                                    "rewards": False
                                }
                            ]
                        }

                        async with self.session.post(RPC_URL, json=tx_payload) as tx_response:
                            if tx_response.status == 200:
                                tx_data = await tx_response.json()
                                if "result" in tx_data and tx_data["result"]:
                                    print(f"🔍 Found new transaction from Wallet A: {signature[:8]}...")
                                    result = tx_data["result"]
                                    result["signature"] = signature
                                    return result

            return None

        except aiohttp.ClientError as e:
            print(f"❌ Network error: {str(e)}")
            # Recreate session on network errors
            await self.close_session()
            return None
        except Exception as e:
            print(f"❌ Error monitoring Wallet A: {str(e)}")
            traceback.print_exc()
            return None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.session and not self.session.closed:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close_session())
            except Exception:
                pass       

def parse_transaction_logs(logs: list) -> Optional[Dict[str, Any]]:
    if not logs:
        return None
    try:
        result = {
            "program_id": None,
            "instruction": None,
            "dex": None,
            "type": None
        }
        for log in logs:
            if "Program " in log and " invoke" in log:
                program = log.split("Program ")[1].split(" invoke")[0].strip()
                for dex_name, program_ids in KNOWN_PROGRAMS.items():
                    if isinstance(program_ids, list) and program in program_ids:
                        result["dex"] = dex_name
                        result["program_id"] = program
                        break
                    elif program == program_ids:
                        result["dex"] = dex_name
                        result["program_id"] = program
                        break
                if result["program_id"]:
                    break
        if not result["program_id"]:
            return None
        for log in logs:
            for keyword in BUY_KEYWORDS:
                if keyword in log:
                    result["instruction"] = "Buy"
                    result["type"] = keyword
                    return result
            for keyword in SELL_KEYWORDS:
                if keyword in log:
                    result["instruction"] = "Sell"
                    result["type"] = keyword
                    return result
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
