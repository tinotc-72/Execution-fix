#!/usr/bin/env python3
"""
Real MEV Test - 0.001 SOL Buy/Sell
Actual blockchain transactions with your specified meme coin
"""

import asyncio
import json
from datetime import datetime
from mev_pumpfun_executor import MEVPumpFunExecutor
from env_keys import EnvKeys

class RealMEVTest:
    def __init__(self):
        # Load environment keys
        env_keys = EnvKeys()
        private_key = env_keys.PHANTOM_PRIVATE_KEY
        
        self.executor = MEVPumpFunExecutor(private_key)
        self.test_amount = 0.005  # SOL - increased from 0.001
        
    async def test_real_buy_sell(self, mint_address: str):
        """Execute real buy and sell with 0.001 SOL"""
        
        print("🎯 REAL MEV TEST - 0.005 SOL")
        print("=" * 50)
        print(f"Mint: {mint_address}")
        print(f"Amount: {self.test_amount} SOL")
        print(f"Time: {datetime.now()}")
        print("=" * 50)
        
        # Check initial balance
        initial_sol = await self.executor.get_sol_balance()
        initial_tokens = await self.executor.get_token_balance(mint_address)
        
        print(f"\n📊 INITIAL BALANCES:")
        print(f"SOL: {initial_sol:.6f}")
        print(f"Tokens: {initial_tokens:,}")
        
        if initial_sol < 0.007:  # Need extra for fees (0.005 + fees)
            print(f"❌ Need at least 0.007 SOL (0.005 + fees)")
            return
            
        print(f"\n🚀 STEP 1: MEV BUY")
        print(f"Buying {self.test_amount} SOL worth of {mint_address[:8]}...")
        
        # Execute MEV buy
        buy_result = await self.executor.execute_buy_copy(
            mint_address=mint_address,
            sol_amount=self.test_amount,
            slippage_percent=10
        )
        
        if buy_result and 'signature' in buy_result:
            print(f"✅ BUY SUCCESS!")
            print(f"Signature: {buy_result['signature']}")
            print(f"Explorer: https://solscan.io/tx/{buy_result['signature']}")
            
            # Wait a moment for transaction to settle
            await asyncio.sleep(3)
            
            # Check new balances
            mid_sol = await self.executor.get_sol_balance()
            mid_tokens = await self.executor.get_token_balance(mint_address)
            tokens_bought = mid_tokens - initial_tokens
            
            print(f"\n📊 AFTER BUY:")
            print(f"SOL: {mid_sol:.6f} (spent: {initial_sol - mid_sol:.6f})")
            print(f"Tokens: {mid_tokens:,} (bought: {tokens_bought:,})")
            
            if tokens_bought > 0:
                print(f"\n🚀 STEP 2: MEV SELL")
                print(f"Selling {tokens_bought:,} tokens...")
                
                # Execute MEV sell
                sell_result = await self.executor.execute_sell_all(
                    mint_address=mint_address,
                    slippage_percent=10
                )
                
                if sell_result and 'signature' in sell_result:
                    print(f"✅ SELL SUCCESS!")
                    print(f"Signature: {sell_result['signature']}")
                    print(f"Explorer: https://solscan.io/tx/{sell_result['signature']}")
                    
                    # Wait for settlement
                    await asyncio.sleep(3)
                    
                    # Check final balances
                    final_sol = await self.executor.get_sol_balance()
                    final_tokens = await self.executor.get_token_balance(mint_address)
                    
                    print(f"\n📊 FINAL RESULTS:")
                    print(f"SOL: {final_sol:.6f}")
                    print(f"Tokens: {final_tokens:,}")
                    print(f"Net SOL change: {final_sol - initial_sol:.6f}")
                    print(f"Total fees paid: {initial_sol - final_sol:.6f}")
                    
                    # Calculate performance
                    if final_sol > initial_sol - 0.002:  # Account for reasonable fees
                        print(f"🎉 TEST SUCCESSFUL - MEV bot working!")
                    else:
                        print(f"⚠️  High fees, but transactions executed")
                        
                    return {
                        'buy_signature': buy_result['signature'],
                        'sell_signature': sell_result['signature'],
                        'initial_sol': initial_sol,
                        'final_sol': final_sol,
                        'tokens_traded': tokens_bought,
                        'success': True
                    }
                else:
                    print(f"❌ SELL FAILED: {sell_result}")
                    return {'success': False, 'error': 'Sell failed'}
            else:
                print(f"❌ No tokens received from buy")
                return {'success': False, 'error': 'No tokens bought'}
        else:
            print(f"❌ BUY FAILED: {buy_result}")
            return {'success': False, 'error': 'Buy failed'}

async def main():
    """Main test function"""
    
    # USER-SPECIFIED MEME COIN
    MINT_ADDRESS = "4SXJJw2GKVTeoxqjrcrFNb3S59632wXjVRSJN8kFpump"  # User's chosen meme coin
        
    tester = RealMEVTest()
    result = await tester.test_real_buy_sell(MINT_ADDRESS)
    
    print(f"\n🎯 TEST COMPLETE")
    print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
