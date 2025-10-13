#!/usr/bin/env python3
"""
MEV Bot Real Trading Test
Safe testing with real meme coins using small amounts
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any

from config import WALLET
from mev_pumpfun_executor import MEVPumpFunExecutor, MEVExecutorConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MEVRealTradeTest:
    """Safe real trading test for MEV bot"""
    
    def __init__(self):
        # Safe test configuration - small amounts only
        self.config = MEVExecutorConfig(
            buy_priority_fee=500_000,      # MEV priority for buys
            sell_priority_fee=750_000,     # Higher priority for sells
            buy_compute_limit=149_700,     # Optimized from analysis
            sell_compute_limit=200_000,    # Higher for sells
            max_buy_sol=0.01,             # SAFE: Max 0.01 SOL per test ($1-2)
            min_buy_sol=0.001,            # Min 0.001 SOL
            skip_preflight=True,          # MEV speed optimization
            debug_mode=True               # Detailed logging
        )
        
        # Create MEV executor
        from env_keys import EnvKeys
        env = EnvKeys()
        self.executor = MEVPumpFunExecutor(env.PHANTOM_PRIVATE_KEY, self.config)
        
        print("🧪 MEV Real Trade Test Initialized")
        print("=" * 50)
        print(f"⚠️  SAFETY LIMITS:")
        print(f"   Max buy: {self.config.max_buy_sol} SOL")
        print(f"   MEV buy priority: {self.config.buy_priority_fee:,} μ-lamports")
        print(f"   MEV sell priority: {self.config.sell_priority_fee:,} μ-lamports")
        print("=" * 50)
        
    async def test_meme_coin_buy(self, mint_address: str, test_amount: float = 0.005) -> Optional[str]:
        """
        Test MEV buy with a real meme coin
        """
        try:
            # Safety check
            if test_amount > self.config.max_buy_sol:
                print(f"❌ Amount {test_amount} exceeds safety limit {self.config.max_buy_sol}")
                return None
                
            print(f"\n🎯 MEV BUY TEST")
            print(f"   Mint: {mint_address}")
            print(f"   Amount: {test_amount} SOL")
            print(f"   Timestamp: {datetime.now()}")
            
            # Check SOL balance first
            sol_balance = await self.executor.get_sol_balance()
            print(f"   SOL Balance: {sol_balance:.6f}")
            
            if sol_balance < test_amount:
                print(f"❌ Insufficient SOL balance for test")
                return None
                
            # Execute MEV buy
            start_time = time.time()
            result = await self.executor.execute_buy_copy(mint_address, test_amount)
            execution_time = time.time() - start_time
            
            if result["success"]:
                print(f"✅ MEV BUY SUCCESS!")
                print(f"   Signature: {result['signature']}")
                print(f"   Execution time: {execution_time:.2f}s")
                print(f"   MEV Optimizations Applied: ✅")
                
                # Check token balance after buy
                await asyncio.sleep(3)  # Wait for confirmation
                token_balance = await self.executor.get_token_balance(mint_address)
                print(f"   Tokens received: {token_balance:,}")
                
                return result['signature']
            else:
                print(f"❌ MEV buy failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Buy test failed: {e}")
            return None
            
    async def test_meme_coin_sell(self, mint_address: str) -> Optional[str]:
        """
        Test MEV sell with a real meme coin
        """
        try:
            print(f"\n🎯 MEV SELL TEST")
            print(f"   Mint: {mint_address}")
            print(f"   Timestamp: {datetime.now()}")
            
            # Check token balance
            token_balance = await self.executor.get_token_balance(mint_address)
            print(f"   Token Balance: {token_balance:,}")
            
            if token_balance == 0:
                print(f"❌ No tokens to sell")
                return None
                
            # Execute MEV sell
            start_time = time.time()
            result = await self.executor.execute_sell_all(mint_address)
            execution_time = time.time() - start_time
            
            if result["success"]:
                print(f"✅ MEV SELL SUCCESS!")
                print(f"   Signature: {result['signature']}")
                print(f"   Execution time: {execution_time:.2f}s")
                print(f"   Tokens sold: {result.get('token_amount', 0):,}")
                print(f"   MEV Router Used: ✅")
                
                # Check SOL balance after sell
                await asyncio.sleep(3)  # Wait for confirmation
                new_sol_balance = await self.executor.get_sol_balance()
                print(f"   New SOL Balance: {new_sol_balance:.6f}")
                
                return result['signature']
            else:
                print(f"❌ MEV sell failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Sell test failed: {e}")
            return None
            
    async def full_cycle_test(self, mint_address: str, test_amount: float = 0.005):
        """
        Complete buy-sell cycle test
        """
        print(f"\n🔄 FULL CYCLE MEV TEST")
        print(f"=" * 50)
        
        # Get initial balances
        initial_sol = await self.executor.get_sol_balance()
        initial_tokens = await self.executor.get_token_balance(mint_address)
        
        print(f"📊 INITIAL STATE:")
        print(f"   SOL: {initial_sol:.6f}")
        print(f"   Tokens: {initial_tokens:,}")
        
        # Test buy
        buy_signature = await self.test_meme_coin_buy(mint_address, test_amount)
        
        if buy_signature:
            print(f"\n⏳ Waiting 5 seconds before sell test...")
            await asyncio.sleep(5)
            
            # Test sell
            sell_signature = await self.test_meme_coin_sell(mint_address)
            
            if sell_signature:
                # Final balances
                final_sol = await self.executor.get_sol_balance()
                final_tokens = await self.executor.get_token_balance(mint_address)
                
                print(f"\n📊 FINAL STATE:")
                print(f"   SOL: {final_sol:.6f}")
                print(f"   Tokens: {final_tokens:,}")
                
                # Calculate results
                sol_change = final_sol - initial_sol
                print(f"\n💰 TRADE RESULT:")
                print(f"   SOL Change: {sol_change:+.6f}")
                print(f"   Buy Signature: {buy_signature}")
                print(f"   Sell Signature: {sell_signature}")
                
                # Show stats
                stats = self.executor.get_stats()
                print(f"\n📈 MEV EXECUTOR STATS:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                    
                return {"buy": buy_signature, "sell": sell_signature, "profit": sol_change}
        
        return None

# Popular meme coins for testing (replace with current ones)
POPULAR_MEME_COINS = {
    "FWOG": "A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump",  # Example - replace with current
    "GOAT": "CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump",  # Example - replace with current  
    "PEPE": "BJUgcMdEYmAdN6kF4xHmFNzNVGxKs8jPz8t8K1YGpump",  # Example - replace with current
}

async def main():
    """Main test function"""
    try:
        tester = MEVRealTradeTest()
        
        # Show current balance
        sol_balance = await tester.executor.get_sol_balance()
        print(f"\n💰 Current SOL Balance: {sol_balance:.6f}")
        
        if sol_balance < 0.01:
            print(f"❌ Insufficient balance for testing. Need at least 0.01 SOL")
            return
            
        print(f"\n🎯 AVAILABLE TEST OPTIONS:")
        print(f"1. Quick buy test (0.005 SOL)")
        print(f"2. Full buy-sell cycle test")
        print(f"3. Custom amount test")
        
        # For demo, let's use a placeholder mint - YOU NEED TO REPLACE THIS
        test_mint = "YourActualMemeTokenMintAddressHere"  # REPLACE WITH REAL MINT
        
        print(f"\n⚠️  REPLACE 'test_mint' WITH A REAL MEME COIN MINT!")
        print(f"Current test mint: {test_mint}")
        
        # Uncomment to run tests (after setting real mint):
        
        # Option 1: Quick buy test
        # await tester.test_meme_coin_buy(test_mint, 0.005)
        
        # Option 2: Full cycle test  
        # await tester.full_cycle_test(test_mint, 0.005)
        
        print(f"\n✅ MEV test system ready!")
        print(f"💡 To test:")
        print(f"   1. Find a real meme coin mint address")
        print(f"   2. Replace 'test_mint' variable")  
        print(f"   3. Uncomment the test you want to run")
        print(f"   4. Run: python3 mev_real_trade_test.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
