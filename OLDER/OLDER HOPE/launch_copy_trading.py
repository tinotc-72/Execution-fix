#!/usr/bin/env python3
"""
Launch script for the advanced copy trading bot
Always buys 0.05 SOL worth of tokens and sells proportionally
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import main

if __name__ == "__main__":
    try:
        print("🚀 Launching Advanced Copy Trading Bot")
        print("=====================================")
        print("📋 Features:")
        print("   • Fixed 0.05 SOL buy amount")
        print("   • Proportional selling")
        print("   • Monitoring 2 target wallets")
        print("   • Uses proven pump.fun direct trading")
        print("=====================================")
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n👋 Copy trading bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
