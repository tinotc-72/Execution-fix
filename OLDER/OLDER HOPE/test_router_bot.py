#!/usr/bin/env python3
"""
Quick test of the router trade handling
"""

import asyncio
import logging
from datetime import datetime

from advanced_copy_trading_bot import PumpCopyTradingBot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_router_trade():
    """Test the router trade execution"""
    
    print("🧪 Testing Router Trade Handling")
    print("=" * 50)
    
    # Create bot
    copy_config = {
        'fixed_buy_amount': 0.01,
        'delay_seconds': 0,
        'enable_sells': True,
        'enable_buys': True,
        'proportional_selling': True
    }
    
    bot = PumpCopyTradingBot(copy_config)
    
    # Test token from the logs
    test_token = "HhFjrSRqakLmmGjkPqAZMH5cGSWhbEd3fG4o15sibonk"
    test_amount = 0.01
    
    # Create a mock target trade
    target_trade = {
        'action': 'buy',
        'token_mint': test_token,
        'sol_amount': 2.02,
        'token_amount': 23141793137186,
        'dex': 'PUMP_ROUTER',
        'signature': 'test_signature'
    }
    
    print(f"🎯 Testing router trade for token: {test_token[:8]}...")
    print(f"💰 Amount: {test_amount} SOL")
    
    try:
        # Test the router trade execution
        result = await bot._execute_router_trade(test_token, test_amount, target_trade)
        
        print(f"\n📊 Result:")
        print(f"   Success: {result.result.value == 'success'}")
        print(f"   Error: {result.error_message}")
        print(f"   Signature: {result.signature}")
        print(f"   Amount: {result.tokens_amount}")
        
        if result.result.value == 'success':
            print("✅ Router trade test successful!")
        else:
            print("❌ Router trade test failed, but this is expected for account validation issues")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_router_trade())
