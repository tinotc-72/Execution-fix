# replicator.py

from datetime import datetime, timezone
import asyncio
import traceback
from typing import Optional, Dict, Any
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from wallet_tx_parser import (
    WalletATxParser, 
    extract_mint_from_meta,
    BUY_KEYWORDS,
    parse_transaction_logs,
    SELL_KEYWORDS
)
from simulate_clone import clone_transaction_from_wallet_a
from tx_builder import wallet_owns_token

HoldingsDict = Dict[str, Dict[str, Any]]

class Replicator:
    def __init__(self, wallet: Keypair):
        self.wallet = wallet
        self.parser: Optional[WalletATxParser] = None
        self.holdings: HoldingsDict = {}
        self.current_user = "tinotc-72"
        self.last_tx_signature: Optional[str] = None

    def get_timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    async def initialize(self) -> bool:
        try:
            self.parser = WalletATxParser(wallet=self.wallet)
            # Create initial session
            await self.parser.create_session()
            print(f"[{self.get_timestamp()}] ✅ Replicator initialized")
            print(f"👤 User: {self.current_user}")
            print(f"💼 Wallet: {self.wallet.pubkey()}")
            return True
        except Exception as e:
            print(f"[{self.get_timestamp()}] ❌ Failed to initialize: {e}")
            traceback.print_exc()
            return False

    async def handle_trade(self) -> Optional[Dict]:
        try:
            tx_data = await self.parser.get_next_transaction()
            if not tx_data:
                return None

            # Get transaction metadata and platform data
            tx_signature = tx_data.get("signature")
            if not tx_signature:
                print("❌ No signature in transaction data")
                return None

            # Skip if we've already processed this transaction
            if tx_signature and tx_signature == self.last_tx_signature:
                return None
            self.last_tx_signature = tx_signature

            # Get platform data from logs
            logs = tx_data.get("meta", {}).get("logMessages", [])
            platform_data = parse_transaction_logs(logs)
            if not platform_data:
                print("❌ Could not determine transaction type from logs")
                return None

            # Get transaction type from platform data
            tx_type = platform_data.get("instruction")
            if not tx_type:
                return None

            # Extract mint
            mint = extract_mint_from_meta(tx_data)
            if not mint:
                print("❌ Could not extract mint")
                return None

            # Log transaction details
            print(f"\n[{self.get_timestamp()}] 🔄 {tx_type} detected")
            print(f"🎯 Token: {mint}")
            print(f"📝 Signature: {tx_signature[:8]}...")
            print(f"🏢 Platform: {platform_data.get('dex', 'Unknown')}")
            print(f"📋 Type: {platform_data.get('type', 'Unknown')}")

            # Check token ownership
            print(f"\n[{self.get_timestamp()} UTC] 🔍 Checking token ownership...")
            print(f"Wallet: {self.wallet.pubkey()}")
            print(f"Token mint: {mint}")
            
            owns_token = await wallet_owns_token(mint, self.wallet.pubkey())
            
            print("✅ Token check complete")
            print(f"⏱️ Latency: {tx_data.get('latency', 0):.2f}ms")
            print(f"🎯 Result: {'Owns token' if owns_token else 'Does not own token'}")

            # Fast-path execution checks
            if tx_type == "Buy" and owns_token:  # Note: Changed from "BUY" to "Buy" to match parser
                print(f"⚠️ Already own {mint}")
                return None
                
            if tx_type == "Sell" and not owns_token:  # Note: Changed from "SELL" to "Sell"
                print(f"⚠️ Don't own {mint}")
                return None

            # Clone and execute immediately
            print(f"\n[{self.get_timestamp()}] 🔄 Cloning {tx_type} transaction...")
            print(f"🏢 Platform: {platform_data.get('dex', 'Unknown')}")
            
            result = await self.clone_transaction(tx_data, tx_type)
            if result:
                print(f"✅ {tx_type} executed successfully")
                print(f"🏢 Platform: {platform_data.get('dex', 'Unknown')}")
                print(f"⏱️ Total time: {(datetime.now(UTC) - datetime.fromisoformat(self.get_timestamp())).total_seconds() * 1000:.2f}ms")
            
            return result

        except Exception as e:
            print(f"[{self.get_timestamp()}] ❌ Trade error: {e}")
            traceback.print_exc()
            return None
    
    async def clone_transaction(self, tx_data: Dict, tx_type: str) -> Optional[Dict]:
        try:
            start_time = datetime.now(timezone.utc)
            cloned_tx = await clone_transaction_from_wallet_a(tx_data, self.wallet)
            
            if not cloned_tx:
                print("❌ Failed to clone transaction")
                return None

            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            size = len(bytes(cloned_tx))
            
            print(f"✅ {tx_type} cloned:")
            print(f"📏 Size: {size} bytes")
            print(f"⚡ Clone time: {elapsed:.2f}ms")

            return {
                "original_tx": tx_data,
                "cloned_tx": cloned_tx,
                "platform": "GenericClone",
                "tx_type": tx_type,
                "clone_time_ms": elapsed
            }

        except Exception as e:
            print(f"❌ Clone error: {e}")
            traceback.print_exc()
            return None

    def determine_transaction_type(self, tx_data: Dict) -> Optional[str]:
        try:
            logs = tx_data.get("meta", {}).get("logMessages", [])
            if not logs:
                return None

            for log in logs:
                if any(keyword in log for keyword in BUY_KEYWORDS):
                    return "BUY"
                if any(keyword in log for keyword in SELL_KEYWORDS):
                    return "SELL"
            return None
            
        except Exception as e:
            print(f"❌ Error determining transaction type: {e}")
            return None

    async def update_holdings(self, result: Dict):
        try:
            mint = extract_mint_from_meta(result["original_tx"])
            if not mint:
                return

            if result["tx_type"] == "BUY":
                self.holdings[mint] = {
                    "buy_time": self.get_timestamp(),
                    "following": result["original_tx"].get("from"),
                    "clone_time_ms": result.get("clone_time_ms")
                }
                print(f"📝 Now tracking {mint}")
                print(f"💰 Total holdings: {len(self.holdings)}")
                
            elif result["tx_type"] == "SELL":
                if mint in self.holdings:
                    hold_time = datetime.now(timezone.utc) - datetime.strptime(
                        self.holdings[mint]["buy_time"], 
                        '%Y-%m-%d %H:%M:%S'
                    ).replace(tzinfo=timezone.utc)
                    
                    print(f"📊 Hold time: {hold_time}")
                    self.holdings.pop(mint, None)
                    print(f"📝 Stopped tracking {mint}")
                    print(f"💰 Remaining holdings: {len(self.holdings)}")

        except Exception as e:
            print(f"❌ Holdings update error: {e}")
            traceback.print_exc()

    async def cleanup(self):
        """Cleanup resources"""
        if self.parser:
            await self.parser.close_session()

    async def run(self):
        if not self.parser:
            print("❌ Not initialized")
            return

        try:
            print(f"\n[{self.get_timestamp()}] 🚀 Starting instant copy bot")
            print(f"👤 User: {self.current_user}")

            while True:
                try:
                    result = await self.handle_trade()
                    if result:
                        await self.update_holdings(result)
                except Exception as e:
                    print(f"❌ Error: {e}")
                    traceback.print_exc()
                    # Recreate session if needed
                    if self.parser.session.closed:
                        await self.parser.create_session()
        finally:
            await self.cleanup()