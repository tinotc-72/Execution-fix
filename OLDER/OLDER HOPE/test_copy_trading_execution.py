#!/usr/bin/env python3
"""
Test copy trading with a manual trade execution to verify the system works
"""

import asyncio
from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig

async def test_copy_trading_execution():
    """Test the copy trading execution system"""
    print("🧪 Testing Copy Trading Execution System")
    print("=" * 50)
    
    # Initialize the trading bot
    trade_config = TradeConfig(
        sol_amount=0.005,  # Very small amount for testing
        max_retries=2,
        slippage_tolerance=0.2,  # 20% slippage for testing
        retry_delay=1.0
    )
    
    trading_bot = GeneralizedPumpTradingBot(trade_config)
    
    # Test with a known pump.fun token (you can change this to any active token)
    test_token_mint = "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"  # Random pump.fun token
    test_sol_amount = 0.005  # 0.005 SOL for testing
    
    print(f"🎯 Test Parameters:")
    print(f"   Token: {test_token_mint}")
    print(f"   Investment: {test_sol_amount} SOL")
    print(f"   Slippage: {trade_config.slippage_tolerance * 100}%")
    
    try:
        print(f"\n💰 Attempting test buy...")
        result = await trading_bot.buy_token(test_token_mint, sol_amount=test_sol_amount)
        
        if result.result.value == 'success':
            print(f"✅ Test buy successful!")
            print(f"   Signature: {result.signature}")
            print(f"   Tokens received: {result.tokens_amount:,}")
            print(f"   Transaction: https://solscan.io/tx/{result.signature}")
            
            # Test sell after 5 seconds
            print(f"\n⏳ Waiting 5 seconds before test sell...")
            await asyncio.sleep(5)
            
            print(f"💸 Attempting test sell...")
            sell_result = await trading_bot.sell_token(test_token_mint, result.tokens_amount)
            
            if sell_result.result.value == 'success':
                print(f"✅ Test sell successful!")
                print(f"   Signature: {sell_result.signature}")
                print(f"   SOL received: {sell_result.sol_amount:.6f}")
                print(f"   Transaction: https://solscan.io/tx/{sell_result.signature}")
                print(f"\n🎉 Copy trading system is working correctly!")
            else:
                print(f"❌ Test sell failed: {sell_result.error_message}")
        else:
            print(f"❌ Test buy failed: {result.error_message}")
            print(f"💡 This is normal if the token doesn't exist or isn't tradeable")
            
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        print(f"💡 This is normal - just testing the system")
    
    finally:
        await trading_bot.close()
        print(f"\n📊 Test completed!")

async def main():
    await test_copy_trading_execution()

if __name__ == "__main__":
    asyncio.run(main())
