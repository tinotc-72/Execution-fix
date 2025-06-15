# jito_executor.py
import asyncio
import aiohttp
import base64
import time
from typing import List, Optional, Dict
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

class JitoExecutor:
    def __init__(self, auth_keypair: Keypair):
        self.auth_keypair = auth_keypair
        # Updated with verified working endpoints
        self.primary_endpoint = "https://mainnet.block-engine.jito.wtf/api/v1/bundles"
        
        self.headers = {
            "Content-Type": "application/json",
            "x-jito-auth": "4d08ea10-2b60-11f0-858a-6bee29fce9c1"
        }
        
        self.session = None
        print("🚀 Jito Executor Initialized with endpoint:", self.primary_endpoint)

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create a single persistent session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(
                ssl=True,
                force_close=False,  # Keep connection alive
                limit=10
            )
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout,
                connector=connector
            )
        return self.session

    async def submit_bundle(self, transactions: List[VersionedTransaction], max_retries: int = 2) -> Optional[Dict]:
        """Submit bundle following Jito docs"""
        try:
            bundle_transactions = []
            for tx in transactions:
                tx_bytes = bytes(tx)
                encoded_tx = base64.b64encode(tx_bytes).decode('utf-8')
                bundle_transactions.append(encoded_tx)

            bundle_data = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "sendBundle",
                "params": [{
                    "transactions": bundle_transactions,
                    "header": {
                        "tip_percentage": 90  # Recommended by Jito
                    }
                }]
            }

            print(f"\n🔄 Submitting bundle with {len(bundle_transactions)} transaction(s)")
            
            session = await self.get_session()
            async with session.post(
                self.primary_endpoint,
                json=bundle_data,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Bundle submitted successfully")
                    return result
                else:
                    print(f"❌ Bundle submission failed: {response.status}")
                    return None

        except Exception as e:
            print(f"❌ Bundle submission error: {str(e)}")
            traceback.print_exc()
            return None

    async def submit_transaction(self, transaction: VersionedTransaction) -> Optional[Dict]:
        """Submit a single transaction"""
        try:
            print("\n🚀 Submitting transaction...")
            print(f"💰 Fee payer: {transaction.message.account_keys[0]}")
            print(f"📏 Size: {len(bytes(transaction))} bytes")
            
            result = await self.submit_bundle([transaction])
            return result

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def __aenter__(self):
        await self.get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()