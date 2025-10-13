#!/usr/bin/env python3
"""
Manual test to simulate trade detection and execution
"""

import asyncio
import logging
from config import CopyTradeConfig
from main import CopyTradingBot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_trade_execution():
    """Test the trade execution pipeline manually"""
    try:
        logger.info("🧪 Starting trade execution test...")
        
        # Initialize bot
        config = CopyTradeConfig()
        bot = CopyTradingBot(config)
        
        # Test data - simulating a detected buy trade
        fake_trade_info = {
            "trade_type": "buy",
            "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC for testing
            "dex": "Test_Manual",
            "signature": "test123456",
            "method": "manual_test",
            "token_amount": 1000000,
            "sol_amount": 0.01,
            "price_per_token": 0.00001
        }
        
        source_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"  # From config
        
        logger.info("🎯 Testing _process_detected_trade with fake trade data...")
        logger.info(f"   Trade info: {fake_trade_info}")
        logger.info(f"   Source wallet: {source_wallet[:8]}...")
        
        # Call the trade processing function directly
        result = await bot._process_detected_trade(fake_trade_info, source_wallet)
        
        logger.info(f"✅ Trade processing result: {result}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_trade_execution())
