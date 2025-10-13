#!/usr/bin/env python3
"""
Test the CLMM Hybrid Copy Executor
"""
import asyncio
import logging
from config import WALLET
from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clmm_hybrid_test")

# Test configuration
MINT = "FV6Xcw9K5GZRb2jDN7e6xXgzs4ZDgJM1BE6nWRqRbonk"  # Replace with your test mint
SOL_AMOUNT = 0.0001
HOLD_SECONDS = 5

async def test_clmm_hybrid_execution():
    """Test the CLMM Hybrid executor with buy and sell cycle"""
    logger.info("🚀 Starting CLMM Hybrid Copy Executor Test")
    logger.info(f"  Token Mint: {MINT}")
    logger.info(f"  SOL Amount: {SOL_AMOUNT}")
    logger.info(f"  Wallet: {WALLET.pubkey()}")
    
    try:
        # Test Buy
        logger.info("\n📈 Testing CLMM Hybrid Buy...")
        buy_result = await try_clmm_hybrid_buy(MINT, WALLET, SOL_AMOUNT)
        
        if buy_result and buy_result.get('success'):
            logger.info(f"✅ Buy successful: {buy_result.get('signature', 'No signature')}")
            
            # Hold for a few seconds
            logger.info(f"⏳ Holding position for {HOLD_SECONDS} seconds...")
            await asyncio.sleep(HOLD_SECONDS)
            
            # Test Sell
            logger.info("\n📉 Testing CLMM Hybrid Sell All...")
            sell_result = await try_clmm_hybrid_sell_all(MINT, WALLET)
            
            if sell_result and sell_result.get('success'):
                logger.info(f"✅ Sell successful: {sell_result.get('signature', 'No signature')}")
                logger.info("🎉 CLMM Hybrid Copy Executor test completed successfully!")
                return True
            else:
                logger.error(f"❌ Sell failed: {sell_result}")
                return False
        else:
            logger.error(f"❌ Buy failed: {buy_result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_clmm_hybrid_execution()
    if success:
        logger.info("\n🎯 All tests passed! CLMM Hybrid Copy Executor is working correctly.")
    else:
        logger.error("\n💥 Tests failed! Check the logs above for details.")

if __name__ == "__main__":
    asyncio.run(main())
