# trade_executor.py

import asyncio
import aiohttp
import base64
import json
import time
from typing import Optional
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
import keyZ as kz

class FastExecutor:
    def __init__(self, wallet: Keypair, tracker=None):
        self.wallet = wallet
        self.tracker = tracker
        self.session = None
        
    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self
        
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def submit_transaction(self, tx: VersionedTransaction) -> Optional[str]:
        """Submit transaction to RPC"""
        try:
            if not self.session:
                await self.initialize()
                
            encoded_tx = base64.b64encode(bytes(tx)).decode('utf-8')
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    encoded_tx,
                    {"encoding": "base64", "skipPreflight": True, "maxRetries": 0}
                ]
            }
            
            start_time = time.time()
            
            async with self.session.post(kz.HELIUS_RPC_URL, json=payload) as response:
                result = await response.json()
                if "result" in result:
                    if self.tracker:
                        self.tracker.track_execution(time.time() - start_time)
                    return result["result"]
                else:
                    print(f"❌ RPC error: {result.get('error', {}).get('message', 'Unknown error')}")
                    return None
                    
        except Exception as e:
            print(f"❌ Transaction submission error: {str(e)}")
            return None

class JitoExecutor:
    def __init__(self, wallet: Keypair, tracker=None):
        self.wallet = wallet
        self.tracker = tracker
        self.endpoint = "https://mainnet.block-engine.jito.wtf/api/v1/bundles"
        self.auth_uuid = kz.JITO_UUID
        self.max_retries = 2
        self.retry_delay = 0.5
        self.rate_limiter = RateLimiter()
        
    async def submit_bundle(self, tx: VersionedTransaction) -> Optional[str]:
        """Submit transaction as a bundle to Jito"""
        try:
            await self.rate_limiter.wait()
            
            encoded_tx = base64.b64encode(bytes(tx)).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.auth_uuid}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "sendBundle",
                "params": [{"bundle": [encoded_tx]}]
            }
            
            print(f"\n🚀 Submitting transaction...")
            print(f"💰 Fee payer: {self.wallet.pubkey()}")
            print(f"📏 Size: {len(bytes(tx))} bytes\n")
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                for attempt in range(self.max_retries):
                    try:
                        print(f"🔄 Attempt {attempt + 1}/{self.max_retries}")
                        print(f"📦 Bundle size: 1 tx(s)")
                        print(f"🎯 Sending to: {self.endpoint}")
                        
                        async with session.post(self.endpoint, json=payload, headers=headers) as response:
                            if response.status == 200:
                                result = await response.json()
                                if "result" in result:
                                    if self.tracker:
                                        self.tracker.track_execution(time.time() - start_time)
                                    return result["result"]
                            else:
                                text = await response.text()
                                print(f"⚠️ HTTP {response.status}: {text}")
                                
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)
                            
                    except Exception as e:
                        print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)
                            
            return None
            
        except Exception as e:
            print(f"❌ Bundle submission error: {str(e)}")
            return None

class RateLimiter:
    def __init__(self, max_requests: int = 2, window_seconds: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        
    async def wait(self):
        """Wait if rate limited"""
        now = time.time()
        
        # Remove old requests
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.requests[0] + self.window_seconds - now
            if wait_time > 0:
                print(f"⏳ Rate limit hit, waiting {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
                
        self.requests.append(now)

class TradeExecutor:
    def __init__(self, wallet: Keypair, tracker=None):
        self.wallet = wallet
        self.tracker = tracker
        self.jito_executor = JitoExecutor(wallet, tracker)
        self.fast_executor = FastExecutor(wallet, tracker)
        
    async def initialize(self):
        """Initialize executors"""
        await self.fast_executor.initialize()
        
    async def close(self):
        """Clean up resources"""
        await self.fast_executor.close()

    def validate_transaction(self, tx: VersionedTransaction) -> bool:
        """Validate transaction before execution"""
        try:
            # Check if transaction is properly signed
            if not tx.signatures or len(tx.signatures) == 0:
                print("❌ Transaction is not signed")
                return False
                
            # Check transaction size
            tx_size = len(bytes(tx))
            if tx_size > 1232:  # Solana transaction size limit
                print(f"❌ Transaction too large: {tx_size} bytes")
                return False
                
            # Check if our wallet is the fee payer
            if tx.message.static_account_keys[0] != self.wallet.pubkey():
                print("❌ Invalid fee payer")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {str(e)}")
            return False
        
    async def execute_trade(self, tx: VersionedTransaction) -> Optional[str]:  # Changed from execute_transaction
        """Execute trade with fallback"""
        try:
            # Try Jito first
            print("\n🚀 Attempting Jito submission...")
            sig = await self.jito_executor.submit_bundle(tx)
            if sig:
                print(f"✅ Jito submission successful: {sig[:8]}...")
                if self.tracker:
                    self.tracker.track_successful_mirror()
                return sig
                
            # Fallback to FastExecutor
            print("\n🔄 Falling back to FastExecutor...")
            sig = await self.fast_executor.submit_transaction(tx)
            if sig:
                print(f"✅ FastExecutor submission successful: {sig[:8]}...")
                if self.tracker:
                    self.tracker.track_successful_mirror()
                return sig
                
            print("❌ All submission attempts failed")
            return None
            
        except Exception as e:
            print(f"❌ Execution error: {str(e)}")
            return None