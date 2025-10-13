#!/usr/bin/env python3
"""
Simple transaction scanner using existing main.py logic
"""

import asyncio
from main import CopyTradingBot, CopyTradeConfig
from env_keys import EnvKeys

async def scan_wallets_for_trades():
    """Use the existing copy trading bot logic to scan for transactions"""
    print("🔍 WALLET TRANSACTION SCANNER")
    print("=" * 50)
    
    # Initialize environment
    env_keys = EnvKeys()
    
    # Target wallets
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    ]
    
    print(f"🎯 Target wallets:")
    for i, wallet in enumerate(target_wallets, 1):
        print(f"   {i}. {wallet}")
    
    # Create config
    config = CopyTradeConfig(target_wallets=target_wallets)
    
    # Initialize the copy trading bot
    bot = CopyTradingBot(config)
    
    try:
        print(f"\n🔍 Scanning for recent transactions using main.py logic...")
        
        # Use the bot's built-in transaction analysis method
        for wallet in target_wallets:
            print(f"\n📊 Analyzing wallet: {wallet}")
            
            try:
                # Use the existing check_wallet_transactions method
                await bot.check_wallet_transactions(wallet)
                
                print(f"✅ Wallet {wallet[:8]}... scan completed")
                
            except Exception as e:
                print(f"❌ Error scanning {wallet[:8]}...: {e}")
        
        # Also try the comprehensive analysis from the new methods
        print(f"\n🔍 Running comprehensive analysis...")
        try:
            analysis_result = await bot.get_comprehensive_transaction_history(limit=50, days_back=3)
            
            if 'error' not in analysis_result:
                summary = analysis_result['summary']
                print(f"📊 Analysis Summary:")
                print(f"   Wallets: {summary['total_wallets']}")
                print(f"   Total buys: {summary['total_buys']}")
                print(f"   Total sells: {summary['total_sells']}")
                print(f"   Most active DEX: {summary['most_active_dex']}")
            else:
                print(f"❌ Analysis error: {analysis_result['error']}")
                
        except Exception as e:
            print(f"❌ Comprehensive analysis error: {e}")
        
        # Try the recent trades analysis
        print(f"\n🎯 Looking for recent copy opportunities...")
        try:
            opportunities = await bot.analyze_recent_trades_and_copy(limit=20, days_back=1)
            
            if 'error' not in opportunities:
                print(f"🚀 Copy opportunities found: {len(opportunities.get('new_opportunities', []))}")
                print(f"⚪ Existing positions: {len(opportunities.get('existing_positions', []))}")
            else:
                print(f"❌ Copy analysis error: {opportunities['error']}")
                
        except Exception as e:
            print(f"❌ Copy opportunity analysis error: {e}")
        
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
    
    finally:
        try:
            await bot.stop()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(scan_wallets_for_trades())
