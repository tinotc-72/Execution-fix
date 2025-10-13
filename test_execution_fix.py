#!/usr/bin/env python3
"""Test execution fix by manually triggering the fixed _process_detected_trade method"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

from main import CopyTradingBot
from datetime import datetime, timezone

async def test_execution_fix():
    """Test if the execution fix works by simulating a detected trade"""
    print("🧪 Testing execution fix...")
    
    # Create bot instance
    try:
        bot = CopyTradingBot()
        print("✅ Bot created successfully")
        
        # Create a simulated trade info (matching the WebSocket format)
        test_trade_info = {
            'signature': '3BDRFWidjU7SYwsQT7ZGMDNBuGSbfWuyZuVsAuTPBE4Vg62YbBcBAfU18fGJ6GJPNe16MJsbLxwoFGipWuUdkSUE',
            'wallet_address': 'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK',
            'action': 'buy',  # ← This is the key that was causing the issue
            'dex': 'Jupiter',
            'token_mint': 'MkErHJb78zVczh9ZsNmLKsOaTDK4Y6inXkGIAfSJIBGL',
            'timestamp': datetime.now(timezone.utc),
            'instruction_type': 'GetAccountDataSize'
        }
        
        print(f"🎯 Testing with trade info:")
        print(f"   Action: {test_trade_info['action']}")
        print(f"   Token: {test_trade_info['token_mint'][:8]}...")
        print(f"   DEX: {test_trade_info['dex']}")
        
        # Call the fixed _process_detected_trade method directly
        print("🚀 Calling _process_detected_trade...")
        result = await bot._process_detected_trade(test_trade_info, test_trade_info['wallet_address'])
        
        print(f"✅ Result: {result}")
        print(f"🔍 Expected: Should see debug prints from _execute_copy_buy if fix worked")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 EXECUTION FIX TEST")
    print("=" * 50)
    result = asyncio.run(test_execution_fix())
    print("=" * 50)
    if result:
        print("✅ TEST PASSED: Execution was attempted")
    else:
        print("❌ TEST FAILED: Execution was not attempted or failed")
