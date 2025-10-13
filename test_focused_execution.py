#!/usr/bin/env python3
"""
🔬 FOCUSED EXECUTION FLOW TEST
Tests the specific execution path when a trade is detected
"""

import asyncio
import sys
import os
import time
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import CopyTradingBot
from config import CopyTradeConfig

async def test_execution_flow():
    """Test what happens when bot detects a trade"""
    print("🔬 FOCUSED EXECUTION FLOW TEST")
    print("=" * 50)
    
    # Initialize bot
    print("🚀 Initializing bot...")
    config = CopyTradeConfig()
    bot = CopyTradingBot(config)
    print("✅ Bot initialized")
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'PUMP.FUN Token (New Meme Coin)',
            'trade': {
                'action': 'buy',
                'wallet_address': 'HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH',
                'signature': 'pump_test_sig_12345',
                'token_mint': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',  # Bonk (pump.fun style)
                'dex': 'pumpfun',
                'timestamp': datetime.now(timezone.utc)
            }
        },
        {
            'name': 'Jupiter Swap (Established Token)',
            'trade': {
                'action': 'buy',
                'wallet_address': 'HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH',
                'signature': 'jupiter_test_sig_67890',
                'token_mint': 'So11111111111111111111111111111111111111112',  # WSOL
                'dex': 'jupiter',
                'timestamp': datetime.now(timezone.utc)
            }
        },
        {
            'name': 'Raydium Pool (DEX Token)',
            'trade': {
                'action': 'buy',
                'wallet_address': 'HN7cABqLq46Es1jh92dQQisAq662SmxELLLsHHe4YWrH',
                'signature': 'raydium_test_sig_54321',
                'token_mint': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',  # RAY
                'dex': 'raydium',
                'timestamp': datetime.now(timezone.utc)
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 SCENARIO {i}: {scenario['name']}")
        print("-" * 40)
        
        trade = scenario['trade']
        print(f"🎯 Token: {trade['token_mint'][:8]}...")
        print(f"🏪 DEX: {trade['dex']}")
        print(f"👤 Source: {trade['wallet_address'][:8]}...")
        
        start_time = time.time()
        
        try:
            # Step 1: Validate trade
            print("\n📋 STEP 1: Validating trade...")
            is_valid = bot._validate_trade_info(trade)
            print(f"   ✅ Validation: {is_valid}")
            
            if is_valid:
                # Step 2: Process the trade (this is the main execution path)
                print("\n⚡ STEP 2: Processing trade (MAIN EXECUTION PATH)...")
                print("   🔄 Calling _process_detected_trade...")
                
                result = await bot._process_detected_trade(trade, trade['wallet_address'])
                
                execution_time = time.time() - start_time
                print(f"\n📊 RESULTS:")
                print(f"   ✅ Execution success: {result}")
                print(f"   ⏱️ Total time: {execution_time:.2f}s")
                print(f"   📈 Positions created: {len(bot.positions)}")
                
                # Show position details if created
                if trade['token_mint'] in bot.positions:
                    pos = bot.positions[trade['token_mint']]
                    print(f"   💰 Position amount: {pos.current_amount} SOL")
                    print(f"   🏪 Entry DEX: {pos.entry_dex}")
            else:
                print("❌ Trade validation failed - execution skipped")
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ EXECUTION ERROR after {execution_time:.2f}s:")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n" + "="*50)
    
    # Final summary
    print(f"\n🎯 EXECUTION FLOW SUMMARY:")
    print(f"   🤖 Bot Status: Operational")
    print(f"   📊 Total positions: {len(bot.positions)}")
    print(f"   🏭 Available executors: {len(bot.dex_executors)}")
    print(f"   💰 Investment per trade: {bot.config.investment_amount_sol} SOL")
    
    if bot.positions:
        print(f"\n📈 POSITIONS CREATED:")
        for token, pos in bot.positions.items():
            print(f"   🪙 {token[:8]}... - {pos.current_amount} SOL via {pos.entry_dex}")

if __name__ == "__main__":
    asyncio.run(test_execution_flow())
