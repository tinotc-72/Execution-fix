#!/usr/bin/env python3
"""
Test the listener with any wallet address to verify trade information extraction
"""

import asyncio
from listener import listen_to_wallet_a, handle_trade
import sys

async def main():
    if len(sys.argv) > 1:
        # Override the wallet address if provided
        from listener import WALLET_A_ADDRESS
        global WALLET_A_ADDRESS
        WALLET_A_ADDRESS = sys.argv[1]
        print(f"🔄 Using custom wallet address: {WALLET_A_ADDRESS}")
    
    print("🎯 Starting listener test...")
    print("📝 Will display detailed information for any trades detected")
    print("Press Ctrl+C to stop\n")
    
    try:
        await listen_to_wallet_a(handle_trade)
    except KeyboardInterrupt:
        print("\n👋 Listener test stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
