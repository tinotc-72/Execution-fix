#!/usr/bin/env python3
"""
Test script to debug the execution issue
"""

import asyncio
import logging
from main import CopyTradingBot
from config import CopyTradeConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_trade_processing():
    """Test the trade processing flow"""
    try:
        # Initialize bot
        config = CopyTradeConfig()
        bot = CopyTradingBot(config)
        
        # Create a mock trade_info like what would be returned from _analyze_balance_changes
        mock_trade_info = {
            "trade_type": "buy",
            "token_mint": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmpm3N",  # Example token
            "dex": "Official_Balance_Analysis",
            "signature": "test123456789abcdef",
            "method": "balance_analysis",
            "token_amount": 1000000.0,
            "sol_amount": 0.1,
            "price_per_token": 0.0000001
        }
        
        mock_source_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCXXhzj"
        
        logger.info("🧪 TESTING: Mock trade processing...")
        logger.info(f"🔍 Mock trade_info: {mock_trade_info}")
        
        # Test the _process_detected_trade function
        result = await bot._process_detected_trade(mock_trade_info, mock_source_wallet)
        
        logger.info(f"🧪 TEST RESULT: {result}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_trade_processing())
