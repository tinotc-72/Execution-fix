#!/usr/bin/env python3
"""
Test RPC Execution Methods - Compare Jito vs Direct RPC
This demonstrates how to use the new RPC execution options
"""

import asyncio
import logging
from main import CopyTradingBot, CopyTradeConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rpc_execution_modes():
    """Test different execution modes: Jito-first vs Direct RPC"""
    
    # Test wallets (use your actual target wallets)
    target_wallets = [
        "YOUR_TARGET_WALLET_1",  # Replace with actual wallet addresses
        "YOUR_TARGET_WALLET_2"
    ]
    
    logger.info("🚀 Testing RPC Execution Methods")
    logger.info("=" * 60)
    
    # Test 1: Jito-first with RPC fallback (Default behavior)
    logger.info("\n📊 TEST 1: Jito-first with RPC fallback")
    logger.info("-" * 40)
    
    config_jito = CopyTradeConfig(
        target_wallets=target_wallets,
        investment_amount_sol=0.001,
        use_jito=True,                      # Enable Jito
        use_direct_rpc_fallback=True,       # Enable RPC fallback when Jito fails
        force_rpc_only=False,               # Don't force RPC-only
        rpc_priority_fee=1                  # Minimal fee for RPC fallback
    )
    
    bot_jito = CopyTradingBot(config_jito)
    logger.info("✅ Jito-first bot created")
    logger.info(f"   Jito enabled: {config_jito.use_jito}")
    logger.info(f"   RPC fallback: {config_jito.use_direct_rpc_fallback}")
    logger.info(f"   Force RPC only: {config_jito.force_rpc_only}")
    
    # Test 2: Force Direct RPC only (Hope Latest style)
    logger.info("\n⚡ TEST 2: Force Direct RPC only (Hope Latest style)")
    logger.info("-" * 40)
    
    config_rpc = CopyTradeConfig(
        target_wallets=target_wallets,
        investment_amount_sol=0.001,
        use_jito=True,                      # Jito service available but bypassed
        use_direct_rpc_fallback=True,       # Not relevant when forcing RPC
        force_rpc_only=True,                # 🚀 FORCE RPC-ONLY (Hope Latest style)
        rpc_priority_fee=1                  # Minimal fee like Hope Latest
    )
    
    bot_rpc = CopyTradingBot(config_rpc)
    logger.info("✅ Direct RPC bot created")
    logger.info(f"   Jito enabled: {config_rpc.use_jito}")
    logger.info(f"   RPC fallback: {config_rpc.use_direct_rpc_fallback}")
    logger.info(f"   Force RPC only: {config_rpc.force_rpc_only}")
    
    # Test 3: Demonstrate direct RPC execution method
    logger.info("\n🔧 TEST 3: Direct RPC execution method")
    logger.info("-" * 40)
    
    try:
        # Example of calling the direct RPC method manually
        from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
        
        # Create minimal test instructions (just compute budget - won't actually trade)
        test_instructions = [
            set_compute_unit_limit(200_000),
            set_compute_unit_price(1)
        ]
        
        # Test the direct RPC execution method
        result = await bot_rpc._try_direct_rpc_execution(
            test_instructions, 
            "Test Direct RPC Method"
        )
        
        if result:
            logger.info(f"✅ Direct RPC method test successful: {result[:12]}...")
        else:
            logger.info(f"ℹ️ Direct RPC method test completed (expected for test instructions)")
            
    except Exception as e:
        logger.info(f"ℹ️ Direct RPC test completed: {e}")
    
    # Summary
    logger.info("\n📋 EXECUTION METHOD SUMMARY")
    logger.info("=" * 60)
    logger.info("🚀 Jito-first mode (default):")
    logger.info("   - Tries Jito first for MEV protection")
    logger.info("   - Falls back to direct RPC if Jito fails")
    logger.info("   - Best for copy trading with MEV protection")
    
    logger.info("\n⚡ Direct RPC mode (Hope Latest style):")
    logger.info("   - Bypasses Jito entirely")
    logger.info("   - Uses minimal fees (1 lamport priority fee)")
    logger.info("   - Fastest execution but no MEV protection")
    logger.info("   - Best for speed-critical trades")
    
    logger.info("\n🔧 Configuration options:")
    logger.info("   force_rpc_only=True   -> Always use direct RPC")
    logger.info("   force_rpc_only=False  -> Use Jito-first with RPC fallback")
    logger.info("   rpc_priority_fee=1    -> Minimal fees like Hope Latest")
    
    logger.info("\n✅ RPC Execution Test Complete!")

async def main():
    """Main test function"""
    try:
        await test_rpc_execution_modes()
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
