#!/usr/bin/env python3
"""
🧪 TEST ROUTER EXTRACTION FIX
Quick test to verify that the RPC client fix resolves router extraction issues
"""

import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from transaction_analyzer import TransactionAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_router_extraction():
    """Test router extraction with proper RPC client"""
    
    try:
        # Import env keys
        from env_keys import EnvKeys
        env_keys = EnvKeys()
        
        # Initialize proper RPC client (not string!)
        rpc_client = AsyncClient(env_keys.HELIUS_RPC_URL)
        logger.info(f"✅ RPC client initialized: {type(rpc_client)}")
        
        # Initialize transaction analyzer with proper client
        analyzer = TransactionAnalyzer(rpc_client, env_keys)
        logger.info(f"✅ Transaction analyzer initialized with RPC client type: {type(analyzer.rpc_client)}")
        
        # Test with a known transaction signature from the logs
        test_signature = "GkDYs3EoDnE7YixrPdDM6KCBk6xhPEcvVhTHs8KzN8Wa2mS8tYNf9nZqS5E2dP3eVpG7YZCpzH8kJ2W9dN7XnM1"
        test_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
        
        logger.info(f"🧪 Testing router extraction for signature: {test_signature[:8]}...")
        
        # This should no longer fail with 'str' object error
        result = await analyzer.analyze_transaction_with_balance_detection(test_signature, test_wallet)
        
        if result:
            logger.info("✅ Transaction analysis completed successfully!")
            if 'router_program_id' in result:
                logger.info(f"✅ Router program extracted: {result['router_program_id']}")
            else:
                logger.warning("⚠️ No router program found in result")
        else:
            logger.warning("⚠️ Transaction analysis returned None")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        # Clean up
        if 'rpc_client' in locals():
            await rpc_client.close()

if __name__ == "__main__":
    asyncio.run(test_router_extraction())