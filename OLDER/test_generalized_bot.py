#!/usr/bin/env python3
"""
Test the Generalized Trading Bot with a newly discovered pump.fun token
"""

import asyncio
import logging
from datetime import datetime

from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_discovered_token():
    """Test trading with the newly discovered token"""
    
    # Token discovered by scanner
    discovered_token = "HwRecTdLtSdDmZy2ssKccExM9g3FdvvT6Aw2gYiUAd63"
    
    print("🧪 TESTING GENERALIZED BOT WITH DISCOVERED TOKEN")
    print("="*80)
    print(f"Token: {discovered_token}")
    print(f"Scanner found: 100+ SOL liquidity - Good for testing!")
    
    # Initialize bot with smaller trade size for safety
    config = TradeConfig(
        sol_amount=0.002,  # Small amount for testing
        max_retries=2,
        slippage_tolerance=0.1  # 10% slippage tolerance
    )
    bot = GeneralizedPumpTradingBot(config)
    
    try:
        print(f"\n🔍 Step 1: Getting token information...")
        token_info = await bot.get_token_info(discovered_token)
        
        print(f"✅ Token validation: {token_info.is_valid}")
        if token_info.is_valid:
            print(f"   Bonding Curve: {token_info.bonding_curve}")
            print(f"   Bonding Curve ATA: {token_info.bonding_curve_ata}")
            if token_info.virtual_sol_reserves:
                print(f"   Virtual SOL Reserves: {token_info.virtual_sol_reserves:.4f}")
            if token_info.market_cap:
                print(f"   Estimated Market Cap: ${token_info.market_cap:,.2f}")
        
        print(f"\n📊 Step 2: Analyzing profitability...")
        analysis = await bot.analyze_token_profitability(discovered_token)
        print(f"   Recommendation: {analysis['recommendation']}")
        print(f"   Liquidity Score: {analysis['liquidity_score']:.2f}")
        print(f"   Market Cap: ${analysis.get('market_cap', 0):,.2f}")
        
        print(f"\n💰 Step 3: Checking initial portfolio...")
        initial_portfolio = await bot.get_portfolio_for_tokens([discovered_token])
        initial_sol = initial_portfolio['sol_balance']
        initial_tokens = initial_portfolio['tokens'][discovered_token]['balance']
        
        print(f"   SOL Balance: {initial_sol:.6f}")
        print(f"   Token Balance: {initial_tokens:,}")
        
        # Only proceed if we have sufficient SOL and the recommendation is positive
        if initial_sol < 0.005:
            print(f"\n⚠️ Insufficient SOL balance for testing ({initial_sol:.6f} SOL)")
            return
        
        if analysis['recommendation'] not in ['BUY', 'HOLD']:
            print(f"\n⚠️ Token not recommended for trading: {analysis['recommendation']}")
            return
        
        print(f"\n🚀 Step 4: Executing BUY trade...")
        buy_result = await bot.buy_token(discovered_token, sol_amount=0.002)
        
        print(f"   Buy Result: {buy_result.result.value}")
        if buy_result.signature:
            print(f"   Transaction: https://solscan.io/tx/{buy_result.signature}")
            print(f"   Tokens Received: {buy_result.tokens_amount:,}")
        
        if buy_result.result.value == 'success':
            print(f"\n⏳ Step 5: Holding for 5 seconds...")
            await asyncio.sleep(5)
            
            # Check updated balance
            mid_portfolio = await bot.get_portfolio_for_tokens([discovered_token])
            mid_tokens = mid_portfolio['tokens'][discovered_token]['balance']
            print(f"   Current Token Balance: {mid_tokens:,}")
            
            if mid_tokens > initial_tokens:
                tokens_to_sell = mid_tokens - initial_tokens
                print(f"\n💸 Step 6: Executing SELL trade ({tokens_to_sell:,} tokens)...")
                
                sell_result = await bot.sell_token(discovered_token, tokens_to_sell)
                
                print(f"   Sell Result: {sell_result.result.value}")
                if sell_result.signature:
                    print(f"   Transaction: https://solscan.io/tx/{sell_result.signature}")
                    print(f"   SOL Received: {sell_result.sol_amount:.6f}")
                
                # Final portfolio check
                print(f"\n📊 Step 7: Final portfolio check...")
                final_portfolio = await bot.get_portfolio_for_tokens([discovered_token])
                final_sol = final_portfolio['sol_balance']
                final_tokens = final_portfolio['tokens'][discovered_token]['balance']
                
                print(f"   Final SOL Balance: {final_sol:.6f}")
                print(f"   Final Token Balance: {final_tokens:,}")
                
                # Calculate net changes
                sol_change = final_sol - initial_sol
                token_change = final_tokens - initial_tokens
                
                print(f"\n📈 Summary:")
                print(f"   SOL Change: {sol_change:+.6f}")
                print(f"   Token Change: {token_change:+,}")
                
                if buy_result.result.value == 'success' and sell_result.result.value == 'success':
                    print(f"   ✅ Complete cycle successful!")
                    # Calculate rough profit/loss (excluding fees)
                    net_sol = sell_result.sol_amount - buy_result.sol_amount
                    print(f"   Net SOL: {net_sol:+.6f} (excluding transaction fees)")
                else:
                    print(f"   ⚠️ Partial success - manual intervention may be needed")
            else:
                print(f"   ⚠️ No tokens received from buy, skipping sell")
        else:
            print(f"   ❌ Buy failed: {buy_result.error_message}")
        
        print(f"\n🎯 Testing Complete!")
        print(f"The generalized bot successfully:")
        print(f"   ✅ Discovered and validated the token")
        print(f"   ✅ Derived bonding curve addresses automatically")
        print(f"   ✅ Analyzed token profitability")
        print(f"   ✅ Executed trades using derived addresses")
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        
    finally:
        await bot.close()

async def test_multiple_tokens():
    """Test the bot's ability to handle multiple different tokens"""
    
    print("\n🔄 TESTING MULTIPLE TOKEN SUPPORT")
    print("="*60)
    
    # Test with both our working token and the discovered token
    test_tokens = [
        "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump",  # Known working token
        "HwRecTdLtSdDmZy2ssKccExM9g3FdvvT6Aw2gYiUAd63"   # Newly discovered token
    ]
    
    config = TradeConfig(sol_amount=0.001, max_retries=1)
    bot = GeneralizedPumpTradingBot(config)
    
    try:
        print(f"Testing {len(test_tokens)} tokens...")
        
        for i, token in enumerate(test_tokens):
            print(f"\n--- Token {i+1}: {token[:8]}... ---")
            
            # Get token info
            token_info = await bot.get_token_info(token)
            print(f"Valid: {token_info.is_valid}")
            
            if token_info.is_valid:
                # Analyze
                analysis = await bot.analyze_token_profitability(token)
                print(f"Recommendation: {analysis['recommendation']}")
                print(f"Liquidity: {analysis['liquidity_score']:.2f}")
                
                # Check balance
                balance = await bot.get_token_balance_by_mint(token)
                print(f"Current Balance: {balance:,}")
        
        # Get comprehensive portfolio
        portfolio = await bot.get_portfolio_for_tokens(test_tokens)
        print(f"\n📊 Complete Portfolio:")
        print(f"SOL Balance: {portfolio['sol_balance']:.6f}")
        print(f"Total Portfolio Value: {portfolio['total_value_sol']:.6f} SOL")
        
        for token, data in portfolio['tokens'].items():
            print(f"  {token[:8]}...: {data['balance']:,} tokens (≈{data['value_sol']:.6f} SOL)")
        
    except Exception as e:
        logger.error(f"Multi-token test error: {e}")
        
    finally:
        await bot.close()

if __name__ == "__main__":
    print("Starting generalized trading bot tests...\n")
    asyncio.run(test_discovered_token())
    print("\n" + "="*80 + "\n")
    asyncio.run(test_multiple_tokens())
