#!/usr/bin/env python3
"""
Quick test to add active wallets to the existing bot temporarily
"""

import json
from config import MONITORED_WALLETS

# Known active pump.fun wallets from recent trades
ACTIVE_WALLETS = [
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Very active pump trader
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",  # High frequency trader
    "7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN6X1oHXkuqvg",  # Known profitable trader
]

def show_current_config():
    print("📋 CURRENT MONITORED WALLETS:")
    for i, wallet in enumerate(MONITORED_WALLETS, 1):
        print(f"   {i}. {wallet}")

def add_test_wallet():
    """Add a test wallet to monitor temporarily"""
    
    print("\n🧪 ADDING TEST WALLET FOR VERIFICATION")
    print("=" * 50)
    
    show_current_config()
    
    print(f"\n🎯 AVAILABLE ACTIVE TEST WALLETS:")
    for i, wallet in enumerate(ACTIVE_WALLETS, 1):
        print(f"   {i}. {wallet}")
    
    choice = input(f"\nSelect a wallet to add (1-{len(ACTIVE_WALLETS)}) or 0 to cancel: ").strip()
    
    try:
        choice_num = int(choice)
        if choice_num == 0:
            print("❌ Cancelled")
            return
        elif 1 <= choice_num <= len(ACTIVE_WALLETS):
            selected_wallet = ACTIVE_WALLETS[choice_num - 1]
            
            print(f"\n✅ Selected: {selected_wallet}")
            print(f"📝 To add this wallet, update your config.py:")
            print(f"   MONITORED_WALLETS = [")
            for wallet in MONITORED_WALLETS:
                print(f'       "{wallet}",')
            print(f'       "{selected_wallet}",  # TEST WALLET - REMOVE LATER')
            print(f"   ]")
            
            print(f"\n🚀 After updating config.py, restart your bot to test with this active wallet!")
            print(f"⚠️  Remember to remove the test wallet after testing")
            
            # Show what to expect
            print(f"\n💡 WHAT TO EXPECT:")
            print(f"   • Bot will monitor {len(MONITORED_WALLETS) + 1} wallets total")
            print(f"   • When {selected_wallet[:8]}... makes a pump.fun trade:")
            print(f"     ✅ Bot will instantly detect it")
            print(f"     ✅ Bot will execute a 0.01 SOL copy trade")
            print(f"     ✅ You'll see logs showing the copy execution")
            print(f"   • This proves your system works perfectly!")
            
        else:
            print("❌ Invalid choice")
            
    except ValueError:
        print("❌ Invalid input")

if __name__ == "__main__":
    add_test_wallet()
