#!/usr/bin/env python3
"""
Quick startup test for copy trading bot
"""

import sys
import traceback

def test_imports():
    """Test if all critical imports work"""
    try:
        print("🔧 Testing basic imports...")
        import asyncio
        import logging
        import time
        print("✅ Basic imports successful")
        
        print("🔧 Testing main.py imports...")
        import main
        print("✅ main.py imports successful")
        
        print("🔧 Testing CopyTradingBot class...")
        from main import CopyTradingBot, CopyTradeConfig
        print("✅ CopyTradingBot class import successful")
        
        print("🔧 Testing configuration creation...")
        config = CopyTradeConfig(
            target_wallets=["test_wallet"],
            investment_amount_sol=0.001,
            use_jito=False  # Disable Jito for testing
        )
        print("✅ Configuration creation successful")
        
        print("🔧 Testing bot instance creation...")
        bot = CopyTradingBot(config)
        print("✅ Bot instance creation successful")
        
        print("🎉 ALL STARTUP TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ STARTUP TEST FAILED: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting copy bot startup test...")
    success = test_imports()
    if success:
        print("✅ Bot is ready to run!")
        sys.exit(0)
    else:
        print("❌ Bot has startup issues that need to be fixed")
        sys.exit(1)
