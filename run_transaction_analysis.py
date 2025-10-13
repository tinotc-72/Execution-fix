#!/usr/bin/env python3
"""
Run comprehensive transaction history analysis for target wallets
"""

import asyncio
import sys
from transaction_history_analyzer import TransactionHistoryAnalyzer
from env_keys import EnvKeys

async def run_analysis():
    """Run the comprehensive transaction analysis"""
    print("🚀 Starting Comprehensive Transaction History Analysis")
    print("=" * 60)
    
    # Initialize environment keys
    env_keys = EnvKeys()
    
    # Target wallets (your actual target wallets)
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Wallet 1
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Wallet 2
    ]
    
    print(f"🎯 Target wallets:")
    for i, wallet in enumerate(target_wallets, 1):
        print(f"   {i}. {wallet}")
    
    # Analysis parameters
    limit = 50  # Number of transactions to analyze per wallet
    days_back = 3  # Days to look back
    
    print(f"\n📊 Analysis Parameters:")
    print(f"   • Transactions per wallet: {limit}")
    print(f"   • Days to look back: {days_back}")
    print(f"   • Total wallets: {len(target_wallets)}")
    
    # Initialize analyzer
    analyzer = TransactionHistoryAnalyzer(env_keys.HELIUS_RPC_URL, target_wallets)
    
    try:
        print(f"\n🔍 Starting analysis...")
        print("=" * 60)
        
        # Get all trades for all wallets
        all_trades = await analyzer.get_all_trades_for_all_wallets(limit, days_back)
        
        # Save results to file
        filename = await analyzer.save_analysis_to_file(all_trades)
        
        print("\n📈 ANALYSIS RESULTS:")
        print("=" * 60)
        
        # Print summary for each wallet
        for wallet, trades in all_trades.items():
            print(f"\n🎯 WALLET: {wallet}")
            print(f"   {'='*50}")
            
            if 'error' in trades:
                print(f"   ❌ Error: {trades['error']}")
                continue
                
            total_transactions = trades.get('total_transactions', 0)
            analyzed_transactions = trades.get('analyzed_transactions', 0)
            buys = trades.get('buys', [])
            sells = trades.get('sells', [])
            
            print(f"   📊 Total transactions found: {total_transactions}")
            print(f"   📊 Transactions analyzed: {analyzed_transactions}")
            print(f"   🟢 Buy transactions: {len(buys)}")
            print(f"   🔴 Sell transactions: {len(sells)}")
            print(f"   💹 Total trades: {len(buys) + len(sells)}")
            
            # Show recent buys
            if buys:
                print(f"\n   🟢 RECENT BUY TRANSACTIONS:")
                for i, buy in enumerate(buys[-5:], 1):  # Show last 5 buys
                    print(f"      {i}. {buy['amount']:.4f} SOL → {buy['token_mint'][:12]}...")
                    print(f"         🏢 DEX: {buy.get('dex', 'Unknown')}")
                    print(f"         🕐 Time: {buy['timestamp']}")
                    print(f"         🔗 Tx: {buy['signature'][:20]}...")
                    print()
            
            # Show recent sells
            if sells:
                print(f"   🔴 RECENT SELL TRANSACTIONS:")
                for i, sell in enumerate(sells[-5:], 1):  # Show last 5 sells
                    print(f"      {i}. {sell['token_mint'][:12]}... → {sell['amount']:.4f} SOL")
                    print(f"         🏢 DEX: {sell.get('dex', 'Unknown')}")
                    print(f"         🕐 Time: {sell['timestamp']}")
                    print(f"         🔗 Tx: {sell['signature'][:20]}...")
                    print()
        
        # Overall summary
        total_buys = sum(len(trades.get('buys', [])) for trades in all_trades.values() if 'buys' in trades)
        total_sells = sum(len(trades.get('sells', [])) for trades in all_trades.values() if 'sells' in trades)
        
        print(f"\n🎉 OVERALL SUMMARY:")
        print(f"   {'='*40}")
        print(f"   📊 Total wallets analyzed: {len(target_wallets)}")
        print(f"   🟢 Total buys across all wallets: {total_buys}")
        print(f"   🔴 Total sells across all wallets: {total_sells}")
        print(f"   💹 Grand total trades: {total_buys + total_sells}")
        if filename:
            print(f"   💾 Results saved to: {filename}")
        
        return all_trades
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return None
    
    finally:
        await analyzer.close()

def main():
    """Main function to run the analysis"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python run_transaction_analysis.py [--help]")
            print("\nThis script analyzes transaction history for your target wallets")
            print("and identifies all buy/sell transactions.\n")
            return
    
    try:
        asyncio.run(run_analysis())
    except KeyboardInterrupt:
        print("\n⏸️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
