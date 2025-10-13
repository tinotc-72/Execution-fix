#!/usr/bin/env python3
"""
Quick start script for the copy trading bot
Run this when you're ready to monitor your target wallet
"""

import asyncio
import sys
from main import main

if __name__ == "__main__":
    print("🤖 SOLANA COPY TRADING BOT - STARTING...")
    print("=" * 60)
    print("🎯 Primary Target Wallet: suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK")
    print("🎯 Secondary Target Wallet: [ADD YOUR SECOND WALLET]")
    print("💰 Investment per trade: 0.001 SOL")
    print("🚀 Aggressive copy trading mode: ENABLED")
    print("⚡ Jito MEV protection: ENABLED")
    print("=" * 60)
    print("📡 Waiting for target wallet activity...")
    print("🔴 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        sys.exit(1)
