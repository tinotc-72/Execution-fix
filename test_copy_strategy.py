#!/usr/bin/env python3
"""
Quick test of copy trading strategy
"""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_copy_trading_strategy():
    """Test the copy trading approach"""
    
    logger.info("🎯 COPY TRADING STRATEGY TEST")
    logger.info("=" * 50)
    
    # Test token from your logs
    test_token = "5eYKhMfyHtdTbCsW2qUUQomdgsHft5GMazjjy7nowVgb"
    target_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    
    logger.info(f"📊 Target Wallet: {target_wallet}")
    logger.info(f"🪙 Detected Token: {test_token}")
    logger.info(f"⏰ Time: {datetime.now()}")
    
    # Simulate the new logic
    logger.info("🎯 COPY TRADING MODE: Target wallet already traded this token")
    logger.info("💪 Following the lead - if they could trade it, so can we!")
    logger.info("🚀 Proceeding with aggressive copy trade strategy")
    
    # Simulate token compatibility check
    logger.warning("⚠️  Token compatibility issue: Non-SPL token detected - owned by System Program")
    logger.warning("⚠️  Non-SPL token detected: 5eYKhMfyHtdTbCsW2qUUQomdgsHft5GMazjjy7nowVgb")
    logger.info("💪 BUT... target wallet traded it successfully!")
    logger.info("🎯 COPY TRADING MODE: Attempting trade anyway with specialized executors")
    logger.info("💡 Will prioritize Pump.fun-specific executors for this token")
    
    # Simulate smart routing
    logger.info("💡 Non-SPL token strategy: Using only Pump.fun compatible executors")
    logger.info("🔄 Trying DIRECT_PUMPFUN...")
    logger.info("🔄 Trying PUMPFUN...")
    
    # Show the difference
    logger.info("")
    logger.info("🔄 KEY DIFFERENCE:")
    logger.info("   ❌ OLD: Would skip non-SPL tokens")  
    logger.info("   ✅ NEW: Attempts trade with specialized executors")
    logger.info("   🎯 REASON: Target wallet already validated this token!")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_copy_trading_strategy())
