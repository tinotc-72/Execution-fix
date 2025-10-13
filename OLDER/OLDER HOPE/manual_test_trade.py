#!/usr/bin/env python3
"""
Manual Test Trade - Trigger Copy Trading Bot
Create a test trade to verify the copy trading system works
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def perform_test_trade():
    """Perform a small test trade to trigger the copy trading bot"""
    
    print("🧪 MANUAL TEST TRADE")
    print("="*50)
    print("This will perform a small test trade to trigger the copy trading bot")
    print("ONLY proceed if you want to test with real SOL!")
    
    response = input("\nDo you want to proceed with a test trade? (yes/no): ")
    if response.lower() != 'yes':
        print("Test trade cancelled.")
        return
    
    # Create trading bot
    config = TradeConfig(
        sol_amount=0.005,  # Very small test amount
        max_retries=2,
        slippage_tolerance=0.15,
        retry_delay=1.0
    )
    
    bot = GeneralizedPumpTradingBot(config)
    
    try:
        # Get a popular token to trade (this is just an example)
        test_token = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"  # Bonk token
        
        print(f"🎯 Performing test buy of {test_token[:8]}... with 0.005 SOL")
        
        # Perform buy
        result = await bot.buy_token(test_token, sol_amount=0.005)
        
        if result.result.value == 'success':
            print(f"✅ Test buy successful!")
            print(f"📊 TX: https://solscan.io/tx/{result.signature}")
            print(f"🪙 Tokens received: {result.tokens_amount:,}")
            
            # Wait a moment then sell (optional)
            sell_response = input("\nDo you want to sell the tokens back? (yes/no): ")
            if sell_response.lower() == 'yes':
                print(f"💸 Selling {result.tokens_amount:,} tokens...")
                sell_result = await bot.sell_token(test_token, result.tokens_amount)
                
                if sell_result.result.value == 'success':
                    print(f"✅ Test sell successful!")
                    print(f"📊 TX: https://solscan.io/tx/{sell_result.signature}")
                    print(f"💰 SOL received: {sell_result.sol_amount:.6f}")
                else:
                    print(f"❌ Test sell failed: {sell_result.error_message}")
        else:
            print(f"❌ Test buy failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Error during test trade: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    print("⚠️  WARNING: This will use real SOL for testing!")
    print("Only run this if you understand the risks.")
    asyncio.run(perform_test_trade())
