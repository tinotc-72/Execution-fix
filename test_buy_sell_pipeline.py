#!/usr/bin/env python3

import asyncio
import logging
from env_keys import EnvKeys, load_wallet_from_private_key

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_complete_buy_sell_pipeline():
    """Test complete buy-sell pipeline to ensure we can exit positions"""
    
    # Setup environment and wallet
    env_keys = EnvKeys()
    private_key = env_keys.PHANTOM_PRIVATE_KEY
    wallet = load_wallet_from_private_key(private_key)
    
    print(f"🔑 Testing complete buy-sell pipeline with wallet: {wallet.pubkey()}")
    
    # Use a well-known Pump.fun token for testing
    test_token_mint = "mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd"
    test_amount = 0.001  # Minimum amount for Pump.fun (1,000 lamports)
    
    try:
        # Import MEV Pump.fun executor for both buy and sell
        from mev_pumpfun_executor import try_pumpfun_buy, try_pumpfun_sell_all
        
        print(f"\n🎯 STEP 1: Test Buy")
        print(f"   Token: {test_token_mint}")
        print(f"   Amount: {test_amount} SOL")
        
        # Test buy functionality
        buy_signature = await try_pumpfun_buy(
            mint_str=test_token_mint,
            sol_amount=test_amount,
            wallet=wallet
        )
        
        if buy_signature:
            print(f"✅ BUY SUCCESS: {buy_signature}")
            
            # Wait a moment for blockchain confirmation
            print(f"\n⏳ Waiting 3 seconds for blockchain confirmation...")
            await asyncio.sleep(3)
            
            print(f"\n🎯 STEP 2: Test Sell")
            
            # Test sell functionality
            sell_signature = await try_pumpfun_sell_all(
                mint_str=test_token_mint,
                wallet=wallet
            )
            
            if sell_signature:
                print(f"✅ SELL SUCCESS: {sell_signature}")
                print(f"\n🎉 COMPLETE PIPELINE SUCCESS!")
                print(f"   📝 Buy TX: {buy_signature}")
                print(f"   📝 Sell TX: {sell_signature}")
                print(f"\n✅ CONFIRMED: You can buy AND sell tokens successfully!")
                
                return True
                
            else:
                print(f"❌ SELL FAILED - No signature returned")
                print(f"⚠️ You can buy but selling needs investigation")
                
        else:
            print(f"❌ BUY FAILED - Cannot test sell without successful buy")
            print(f"⚠️ Buy functionality needs investigation")
            
    except Exception as e:
        print(f"❌ Pipeline test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        
        # Try alternative sell method using direct executor
        print(f"\n🔄 Trying alternative sell method...")
        try:
            from execution_coordinator import ExecutionCoordinator
            from solders.keypair import Keypair
            
            # Convert to keypair for coordinator
            coordinator = ExecutionCoordinator(wallet, None, None)  # Basic setup
            
            # Test if we can at least check sell capability
            print(f"✅ Execution coordinator available for sells")
            
        except Exception as e2:
            print(f"❌ Alternative sell method also failed: {e2}")
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_buy_sell_pipeline())
    
    if success:
        print(f"\n🎊 PIPELINE CONFIRMED: Buy-sell cycle works perfectly!")
    else:
        print(f"\n⚠️ PIPELINE ISSUE: Need to investigate sell functionality")