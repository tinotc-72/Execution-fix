#!/usr/bin/env python3
"""
Minimal bot test to identify startup issues
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_minimal_startup():
    """Test minimal startup"""
    
    try:
        print("🧪 Testing minimal startup...")
        
        # Test imports
        print("1. Testing imports...")
        from advanced_copy_trading_bot import PumpCopyTradingBot
        print("✅ Imports successful")
        
        # Test config
        print("2. Testing config...")
        copy_config = {
            'fixed_buy_amount': 0.01,
            'delay_seconds': 0,
            'enable_sells': True,
            'enable_buys': True,
            'proportional_selling': True
        }
        print("✅ Config created")
        
        # Test bot creation
        print("3. Testing bot creation...")
        bot = PumpCopyTradingBot(copy_config)
        print("✅ Bot created")
        
        # Test close
        print("4. Testing close...")
        await bot.close()
        print("✅ Bot closed")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal_startup())
