#!/usr/bin/env python3
"""
🔍 DETAILED EXECUTION TRACE
Traces exactly what happens during execution with detailed logging
"""

import asyncio
import sys
import os
import time
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import CopyTradingBot
from config import CopyTradeConfig

async def trace_execution():
    """Trace execution step by step"""
    print("🔍 DETAILED EXECUTION TRACE")
    print("=" * 50)
    
    # Initialize bot
    config = CopyTradeConfig()
    bot = CopyTradingBot(config)
    
    # Hook into the position tracking method to see if it's called
    original_update_position = bot._update_position_after_buy_success
    
    def traced_update_position(token_mint, source_wallet, dex_name):
        print(f"🎯 TRACE: _update_position_after_buy_success CALLED!")
        print(f"   Token: {token_mint}")
        print(f"   Source: {source_wallet}")
        print(f"   DEX: {dex_name}")
        result = original_update_position(token_mint, source_wallet, dex_name)
        print(f"   Result: {result}")
        print(f"   Positions after update: {len(bot.positions)}")
        return result
    
    bot._update_position_after_buy_success = traced_update_position
    
    # Test with a simple trade
    test_trade = {
        'action': 'buy',
        'wallet_address': 'HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH',
        'signature': 'trace_test_signature',
        'token_mint': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',  # Bonk
        'dex': 'pumpfun',
        'timestamp': datetime.now(timezone.utc)
    }
    
    print(f"🧪 Testing execution with token: {test_trade['token_mint'][:8]}...")
    print(f"📊 Initial positions: {len(bot.positions)}")
    
    try:
        # Process the trade
        result = await bot._process_detected_trade(test_trade, test_trade['wallet_address'])
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   ✅ Execution result: {result}")
        print(f"   📈 Final positions: {len(bot.positions)}")
        
        if bot.positions:
            print(f"   🎯 Positions created:")
            for token, pos in bot.positions.items():
                print(f"      {token[:8]}... - {pos.current_amount} SOL via {pos.entry_dex}")
        else:
            print(f"   ⚠️ No positions found in bot.positions")
            
        # Check if specific token is in positions
        if test_trade['token_mint'] in bot.positions:
            print(f"   ✅ Test token found in positions!")
        else:
            print(f"   ❌ Test token NOT found in positions")
            
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trace_execution())
