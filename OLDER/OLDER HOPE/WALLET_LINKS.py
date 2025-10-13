#!/usr/bin/env python3
"""
WALLET ACTIVITY CHECKER
Provides easy links to check wallet activity on Solscan
"""

from config import MONITORED_WALLETS
from datetime import datetime

def display_wallet_links():
    """Display all wallet links for manual monitoring"""
    print("\n" + "="*80)
    print("🔍 WALLET ACTIVITY CHECKER")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    wallet_names = [
        "Your Original Wallet #1",
        "Your Original Wallet #2",
        "🔥 ACTIVE TRADER (High Volume)",
        "⚡ SPEED TRADER (High Frequency)", 
        "💎 VOLUME TRADER (Large Positions)",
        "🎯 PUMP SPECIALIST (Active Trader)",
        "🚀 FREQUENT TRADER (Regular Activity)"
    ]
    
    print("\n📊 ALL MONITORED WALLETS WITH DIRECT LINKS:")
    print("-" * 80)
    
    for i, (wallet, name) in enumerate(zip(MONITORED_WALLETS, wallet_names), 1):
        print(f"\n{i}. {name}")
        print(f"   📍 Address: {wallet}")
        print(f"   🔗 Transactions: https://solscan.io/account/{wallet}")
        print(f"   📈 Portfolio: https://solscan.io/account/{wallet}#portfolio")
        print(f"   💸 Token Transfers: https://solscan.io/account/{wallet}#tokenTransfers")
        print(f"   🎯 Sol Transfers: https://solscan.io/account/{wallet}#solTransfers")
    
    print("\n" + "="*80)
    print("💡 MONITORING TIPS:")
    print("- Click on any Solscan link to check recent activity")
    print("- Look for recent pump.fun transactions")
    print("- Bot will INSTANTLY copy any detected trades")
    print("- Monitor the logs for real-time detection")
    print("="*80)
    
    print("\n🎯 YOUR TRADING WALLET (Where copies will execute):")
    print(f"📍 A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
    print(f"🔗 https://solscan.io/account/A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
    print(f"📈 https://solscan.io/account/A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB#portfolio")

if __name__ == "__main__":
    display_wallet_links()
