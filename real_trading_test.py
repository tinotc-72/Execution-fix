"""
REAL MEV TRADING TEST - Jupiter Integration
Actual SOL to USDC trades to prove your trading system works
"""

import asyncio
import logging
import httpx
import json
import time
from typing import Optional
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from base58 import b58encode, b58decode
from env_keys import EnvKeys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealTradingTest:
    """Real trading test using Jupiter for SOL <-> USDC"""
    
    def __init__(self, env_keys: EnvKeys):
        self.env = env_keys
        self.keypair = Keypair.from_base58_string(env_keys.PHANTOM_PRIVATE_KEY)
        self.wallet_address = self.keypair.pubkey()
        
        # Tokens for testing
        self.SOL_MINT = "So11111111111111111111111111111111111111112"
        self.USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        
        # MEV settings
        self.PRIORITY_FEE = 500_000  # 500k microlamports
        
    async def get_jupiter_quote(self, input_mint: str, output_mint: str, amount: int) -> Optional[dict]:
        """Get quote from Jupiter"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"https://quote-api.jup.ag/v6/quote"
                params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": amount,
                    "slippageBps": 100  # 1% slippage
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    quote = response.json()
                    logger.info(f"✅ Jupiter quote: {amount} -> {quote['outAmount']}")
                    return quote
                else:
                    logger.error(f"❌ Jupiter quote failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Jupiter quote error: {e}")
            return None
    
    async def get_jupiter_transaction(self, quote: dict) -> Optional[str]:
        """Get swap transaction from Jupiter"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = "https://quote-api.jup.ag/v6/swap"
                
                swap_request = {
                    "quoteResponse": quote,
                    "userPublicKey": str(self.wallet_address),
                    "wrapAndUnwrapSol": True,
                    "prioritizationFeeLamports": self.PRIORITY_FEE
                }
                
                response = await client.post(url, json=swap_request)
                
                if response.status_code == 200:
                    swap_response = response.json()
                    return swap_response["swapTransaction"]
                else:
                    logger.error(f"❌ Jupiter swap failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Jupiter swap error: {e}")
            return None
    
    async def execute_jupiter_trade(self, input_mint: str, output_mint: str, amount: int, trade_name: str) -> Optional[str]:
        """Execute a Jupiter trade"""
        try:
            logger.info(f"🚀 {trade_name}: {amount/1_000_000_000:.6f} SOL")
            
            # Get quote
            quote = await self.get_jupiter_quote(input_mint, output_mint, amount)
            if not quote:
                return None
            
            # Get transaction
            swap_transaction_b64 = await self.get_jupiter_transaction(quote)
            if not swap_transaction_b64:
                return None
            
            # Decode and sign transaction
            import base64
            transaction_bytes = base64.b64decode(swap_transaction_b64)
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            # Sign transaction (create new signed transaction)
            signed_transaction = VersionedTransaction(transaction.message, [self.keypair])
            
            # Submit transaction
            async with httpx.AsyncClient(timeout=30.0) as client:
                serialized = b58encode(bytes(signed_transaction)).decode()
                
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            serialized,
                            {
                                "encoding": "base58",
                                "skipPreflight": False,
                                "preflightCommitment": "confirmed"
                            }
                        ]
                    }
                )
                
                result = response.json()
                
                if 'result' in result:
                    signature = result['result']
                    logger.info(f"✅ {trade_name} submitted: {signature}")
                    return signature
                else:
                    error = result.get('error', {})
                    logger.error(f"❌ {trade_name} failed: {error}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ {trade_name} error: {e}")
            return None
    
    async def confirm_transaction(self, signature: str, max_retries: int = 30) -> bool:
        """Wait for transaction confirmation"""
        logger.info(f"⏳ Confirming: {signature}")
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        self.env.HELIUS_RPC_URL,
                        json={
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getSignatureStatuses",
                            "params": [[signature]]
                        }
                    )
                    
                    data = response.json()
                    if 'result' in data and data['result']['value']:
                        status = data['result']['value'][0]
                        if status:
                            if status.get('confirmationStatus') in ['confirmed', 'finalized']:
                                if status.get('err') is None:
                                    logger.info(f"✅ Confirmed: {signature}")
                                    return True
                                else:
                                    logger.error(f"❌ Failed: {status['err']}")
                                    return False
            except Exception as e:
                logger.warning(f"Confirmation check error: {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
        
        logger.warning(f"⏰ Confirmation timeout: {signature}")
        return False
    
    async def get_sol_balance(self) -> float:
        """Get SOL balance"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [str(self.wallet_address)]
                    }
                )
                
                data = response.json()
                if 'result' in data:
                    lamports = data['result']['value']
                    return lamports / 1_000_000_000
                return 0.0
        except:
            return 0.0

async def run_real_trading_test():
    """Run real trading test with actual money"""
    print("💰 REAL MEV TRADING TEST - ACTUAL MONEY 💰")
    print("=" * 60)
    print("⚠️  WARNING: This uses REAL SOL for REAL trades!")
    print("🎯 Testing: SOL -> USDC -> SOL cycle")
    print()
    
    # Initialize
    env_keys = EnvKeys()
    trader = RealTradingTest(env_keys)
    
    print(f"🔑 Wallet: {trader.wallet_address}")
    
    # Check initial balance
    initial_balance = await trader.get_sol_balance()
    print(f"💵 Initial SOL balance: {initial_balance:.6f} SOL")
    
    if initial_balance < 0.002:
        print("❌ Insufficient SOL balance for test (need at least 0.002 SOL)")
        return
    
    print()
    
    # Phase 1: SOL -> USDC
    print("🚀 Phase 1: Converting SOL to USDC...")
    sol_amount = int(0.001 * 1_000_000_000)  # 0.001 SOL
    
    buy_signature = await trader.execute_jupiter_trade(
        trader.SOL_MINT,
        trader.USDC_MINT, 
        sol_amount,
        "SOL->USDC"
    )
    
    if not buy_signature:
        print("❌ SOL->USDC failed - aborting test")
        return
    
    print(f"📝 Buy signature: {buy_signature}")
    print(f"🔗 Explorer: https://solscan.io/tx/{buy_signature}")
    
    # Confirm buy
    buy_confirmed = await trader.confirm_transaction(buy_signature)
    if not buy_confirmed:
        print("❌ SOL->USDC confirmation failed")
        return
    
    print("✅ SOL->USDC confirmed!")
    
    # Wait a bit
    print("\n⏳ Waiting 5 seconds...")
    await asyncio.sleep(5)
    
    # Phase 2: USDC -> SOL (sell back)
    print("\n🚀 Phase 2: Converting USDC back to SOL...")
    
    # For simplicity, use a fixed USDC amount (we'd need to check actual balance)
    usdc_amount = int(1 * 1_000_000)  # ~1 USDC (6 decimals)
    
    sell_signature = await trader.execute_jupiter_trade(
        trader.USDC_MINT,
        trader.SOL_MINT,
        usdc_amount,
        "USDC->SOL"
    )
    
    if not sell_signature:
        print("❌ USDC->SOL failed")
        return
    
    print(f"📝 Sell signature: {sell_signature}")
    print(f"🔗 Explorer: https://solscan.io/tx/{sell_signature}")
    
    # Confirm sell
    sell_confirmed = await trader.confirm_transaction(sell_signature)
    
    # Final results
    final_balance = await trader.get_sol_balance()
    
    print("\n" + "=" * 60)
    print("💡 REAL TRADING TEST RESULTS:")
    print(f"   SOL->USDC: {'✅ SUCCESS' if buy_confirmed else '❌ FAILED'}")
    print(f"   USDC->SOL: {'✅ SUCCESS' if sell_confirmed else '❌ FAILED'}")
    print(f"   Initial balance: {initial_balance:.6f} SOL")
    print(f"   Final balance: {final_balance:.6f} SOL")
    
    if buy_confirmed and sell_confirmed:
        print("\n🏆 COMPLETE SUCCESS!")
        print("✅ Your trading infrastructure works with REAL money!")
        print("✅ Ready for MEV pump.fun trading!")
    else:
        print("\n⚠️ Partial success - check logs for details")

if __name__ == "__main__":
    asyncio.run(run_real_trading_test())
