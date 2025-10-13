#!/usr/bin/env python3
"""
🎯 VERIFICATION SCRIPT
Tests that the Raydium CPMM routing fix is working correctly
"""

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_processor import TradeProcessor
from execution_coordinator import ExecutionCoordinator
from solana.rpc.async_api import AsyncClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def verify_fix():
    """Verify the Raydium CPMM routing fix is working"""
    
    logger.info("🔍 VERIFYING RAYDIUM CPMM ROUTING FIX")
    logger.info("=" * 50)
    
    # The problematic transaction that was being routed to Pump.fun instead of Raydium
    signature = "3fmwcJWcVoE7qtdFJSz9UQhpXjJohbGa3H79aqLzXhPHJhArxU2rBHZewmEKhdVD7ekSTcheABJzpov1iVgivAzi"
    wallet_address = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    
    rpc_client = AsyncClient("https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315")
    
    try:
        # Step 1: Test trade processor analysis
        logger.info("📊 STEP 1: Testing Trade Processor Analysis")
        trade_processor = TradeProcessor(target_wallets=[wallet_address], rpc_client=rpc_client)
        trade_info = await trade_processor.analyze_trade_simple(signature, wallet_address)
        
        if trade_info:
            detected_dex = trade_info.get('dex_type', 'unknown')
            logger.info(f"  ✅ Trade Analysis Complete:")
            logger.info(f"    - Token: {trade_info.get('token_mint', 'N/A')[:12]}...")
            logger.info(f"    - DEX Type: {detected_dex}")
            logger.info(f"    - Action: {trade_info.get('action', 'N/A')}")
            
            if detected_dex == 'raydium_cpmm':
                logger.info("  ✅ SUCCESS: Correctly detected as Raydium CPMM")
            else:
                logger.error(f"  ❌ FAILURE: Expected 'raydium_cpmm', got '{detected_dex}'")
                return False
        else:
            logger.error("  ❌ FAILURE: Trade analysis returned no results")
            return False
        
        # Step 2: Test execution coordinator routing
        logger.info("\\n🎯 STEP 2: Testing Execution Coordinator Routing")
        
        class MockConfig:
            def __init__(self):
                self.sol_per_trade = 0.001
                
        class MockWallet:
            def __init__(self):
                pass
                
        execution_coordinator = ExecutionCoordinator(MockConfig(), MockWallet())
        detected_platform = await execution_coordinator._detect_token_platform(
            trade_info.get('token_mint'), trade_info
        )
        
        logger.info(f"  ✅ Platform Detection Complete:")
        logger.info(f"    - Input DEX Type: {trade_info.get('dex_type')}")
        logger.info(f"    - Detected Platform: {detected_platform}")
        
        if detected_platform == 'meteora_damm_v2':
            logger.info("  ✅ SUCCESS: Will route to Meteora DAMM v2 (correct for Raydium CPMM)")
        else:
            logger.error(f"  ❌ FAILURE: Expected 'meteora_damm_v2', got '{detected_platform}'")
            return False
        
        # Step 3: Final verification
        logger.info("\\n🎉 STEP 3: Final Verification")
        logger.info("  ✅ Transaction analysis: WORKING")
        logger.info("  ✅ DEX detection: WORKING") 
        logger.info("  ✅ Platform routing: WORKING")
        logger.info("\\n🎊 FIX VERIFICATION COMPLETE!")
        logger.info("🔧 Previous issue: Bot tried to execute Raydium CPMM trades on Pump.fun → Failed")
        logger.info("✅ Current behavior: Bot correctly routes Raydium CPMM trades to Meteora executor → Success")
        logger.info("\\n🚀 The bot will now correctly handle Raydium CPMM transactions!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await rpc_client.close()

if __name__ == "__main__":
    success = asyncio.run(verify_fix())
    if success:
        print("\\n🎉 VERIFICATION PASSED - Fix is working correctly!")
    else:
        print("\\n❌ VERIFICATION FAILED - Fix needs more work")
        sys.exit(1)
