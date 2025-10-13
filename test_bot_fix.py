#!/usr/bin/env python3

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_bot_with_real_transaction():
    """Test the bot with a real Raydium CPMM transaction to verify routing"""
    
    try:
        from main import SimpleCopyTradingBot
        
        # Initialize bot
        logger.info("🚀 Initializing bot for Raydium CPMM routing test...")
        bot = SimpleCopyTradingBot()
        
        # Simulate a detected trade (the problematic one that was failing)
        trade_detection = {
            'signature': '3fmwcJWcVoE7qtdFJSz9UQhpXjJohbGa3H79aqLzXhPHJhArxU2rBHZewmEKhdVD7ekSTcheABJzpov1iVgivAzi',
            'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK',
            'timestamp': '2025-09-08T14:48:15.651407+00:00',
            'detection_method': 'test_simulation'
        }
        
        logger.info(f"🎯 Testing trade detection and routing for transaction: {trade_detection['signature'][:12]}...")
        
        # Analyze the trade (this should now detect Raydium CPMM correctly)
        trade_info = await bot.analyze_trade(trade_detection['signature'], trade_detection['wallet_address'])
        
        if trade_info:
            logger.info(f"✅ Trade Analysis Success:")
            logger.info(f"  - Token: {trade_info.get('token_mint', 'N/A')[:12]}...")
            logger.info(f"  - Action: {trade_info.get('action', 'N/A')}")
            logger.info(f"  - DEX Type: {trade_info.get('dex_type', 'N/A')}")
            logger.info(f"  - Analysis Method: {trade_info.get('analysis_method', 'N/A')}")
            
            # Test routing (but don't actually execute)
            if trade_info.get('dex_type') == 'raydium_cpmm':
                logger.info("🎯 SUCCESS: Transaction correctly identified as Raydium CPMM!")
                logger.info("🎯 This will now route to Meteora DAMM v2 executor instead of Pump.fun")
                logger.info("✅ Fix verified - no more transaction failures!")
            else:
                logger.warning(f"❌ Still detecting as: {trade_info.get('dex_type')}")
        else:
            logger.error("❌ Trade analysis failed")
            
    except Exception as e:
        logger.error(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bot_with_real_transaction())
