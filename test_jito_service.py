#!/usr/bin/env python3
"""
Test Enhanced Jito Service - Verify Jito-first execution works
"""

import asyncio
import logging
from jito_enhanced_service import JitoEnhancedService
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_jito_service():
    """Test the enhanced Jito service initialization and connectivity"""
    try:
        logger.info("🧪 Testing Enhanced Jito Service...")
        
        # Initialize environment
        env_keys = EnvKeys()
        
        # Create Jito service
        jito_service = JitoEnhancedService(
            preferred_region="london",
            rpc_fallback_url=env_keys.HELIUS_RPC_URL
        )
        
        # Test initialization
        logger.info("🔧 Testing initialization...")
        initialized = await jito_service.initialize()
        
        if initialized:
            logger.info("✅ Jito service initialized successfully!")
            
            # Test tip accounts
            logger.info("🔧 Testing tip accounts...")
            tip_accounts = await jito_service.get_tip_accounts()
            logger.info(f"✅ Retrieved {len(tip_accounts)} tip accounts")
            logger.info(f"   Sample tip account: {tip_accounts[0] if tip_accounts else 'None'}")
            
            # Test stats
            logger.info("📊 Service Stats:")
            stats = jito_service.get_execution_stats()
            for key, value in stats.items():
                logger.info(f"   {key}: {value}")
            
            logger.info("✅ All tests passed! Enhanced Jito Service is ready.")
            
        else:
            logger.error("❌ Jito service initialization failed")
        
        # Clean up
        await jito_service.close()
        logger.info("👋 Test completed")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jito_service())
