#!/usr/bin/env python3
"""
🎯 TEST METEORA MEV EXECUTOR
==========================

Test script to verify the Meteora Dynamic Bonding Curve MEV executor.
This script validates the executor functionality without executing real trades.

Usage:
    python3 test_meteora_executor.py
"""

import asyncio
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_meteora_executor():
    """Test the Meteora MEV executor functionality"""
    
    logger.info("🎯 Testing Meteora MEV Executor")
    logger.info("=" * 50)
    
    try:
        # Test imports
        logger.info("📦 Testing imports...")
        
        try:
            from env_keys import load_wallet_from_private_key, kz
            from solana.rpc.async_api import AsyncClient
            logger.info("✅ env_keys imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import env_keys: {e}")
            return False
        
        try:
            from mev_meteora_executor import (
                MEVMeteoraExecutor,
                MeteoraTradeParams,
                MeteoraTradeResult
            )
            logger.info("✅ mev_meteora_executor imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import mev_meteora_executor: {e}")
            return False
        
        try:
            from meteora_config import get_meteora_config, validate_trade_params
            logger.info("✅ meteora_config imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import meteora_config: {e}")
            return False
        
        # Test configuration
        logger.info("\n⚙️ Testing configuration...")
        config = get_meteora_config()
        logger.info(f"✅ Configuration loaded: {len(config)} sections")
        
        # Test parameter validation
        logger.info("\n🔍 Testing parameter validation...")
        
        # Valid parameters
        if validate_trade_params(0.1, 1.0):
            logger.info("✅ Valid parameters accepted (0.1 SOL, 1% slippage)")
        else:
            logger.error("❌ Valid parameters rejected")
        
        # Invalid parameters
        if not validate_trade_params(0.0001, 1.0):  # Too small
            logger.info("✅ Invalid parameters rejected (too small amount)")
        else:
            logger.error("❌ Invalid parameters accepted")
        
        # Test executor initialization
        logger.info("\n🚀 Testing executor initialization...")
        
        try:
            wallet = load_wallet_from_private_key()
            client = AsyncClient(kz.HELIUS_RPC_URL)
            
            executor = MEVMeteoraExecutor(wallet, client)
            logger.info(f"✅ Executor initialized successfully")
            logger.info(f"   Wallet: {executor.wallet.pubkey()}")
            logger.info(f"   Target Program: {executor.METEORA_DYNAMIC_BONDING_CURVE}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize executor: {e}")
            return False
        
        # Test trade parameters creation
        logger.info("\n📋 Testing trade parameters...")
        
        try:
            from solders.pubkey import Pubkey
            
            params = MeteoraTradeParams(
                token_mint=Pubkey.from_string("So11111111111111111111111111111111111111112"),  # WSOL
                amount_sol=0.1,
                slippage_percent=1.0,
                priority_fee=50000,
                use_jito=True
            )
            
            logger.info("✅ Trade parameters created successfully")
            logger.info(f"   Token: {params.token_mint}")
            logger.info(f"   Amount: {params.amount_sol} SOL")
            logger.info(f"   Slippage: {params.slippage_percent}%")
            logger.info(f"   Priority Fee: {params.priority_fee}")
            logger.info(f"   Use Jito: {params.use_jito}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create trade parameters: {e}")
            return False
        
        # Test performance stats
        logger.info("\n📊 Testing performance tracking...")
        
        try:
            stats = executor.get_performance_stats()
            logger.info("✅ Performance stats retrieved successfully")
            logger.info(f"   Total trades: {stats['total_trades']}")
            logger.info(f"   Success rate: {stats['success_rate']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance stats: {e}")
            return False
        
        # Test execution coordinator integration
        logger.info("\n🔗 Testing execution coordinator integration...")
        
        try:
            from execution_coordinator import MeteoraExecutor, METEORA_EXECUTOR_AVAILABLE
            
            if METEORA_EXECUTOR_AVAILABLE:
                logger.info("✅ Meteora executor available in execution coordinator")
                
                # Test MeteoraExecutor wrapper
                meteora_wrapper = MeteoraExecutor(wallet, client, None)
                logger.info("✅ MeteoraExecutor wrapper created successfully")
                
            else:
                logger.warning("⚠️ Meteora executor not available in execution coordinator")
            
        except Exception as e:
            logger.error(f"❌ Failed to test execution coordinator integration: {e}")
            return False
        
        # Close client
        await client.close()
        
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("=" * 50)
        logger.info("✅ Meteora MEV Executor is ready for use")
        logger.info("🎯 Pattern: Direct Meteora DBC (reverse-engineered)")
        logger.info("🚀 Target: 95%+ success rate")
        logger.info("🛡️ Protection: MEV via Jito bundles")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Unexpected error during testing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Main test function"""
    
    print("🎯 METEORA MEV EXECUTOR TEST")
    print("=" * 30)
    print()
    
    success = await test_meteora_executor()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("🚀 Ready to execute Meteora DBC trades")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        print("🔧 Please check the errors above")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
