#!/usr/bin/env python3
"""
Minimal Working Bot - Start here to verify environment
"""

import asyncio
import logging
import time
from datetime import datetime

# Setup logging to show activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Simple bot that shows activity"""
    logger.info("🚀 Minimal Copy Trading Bot Starting...")
    
    for i in range(10):
        logger.info(f"🔄 Bot Status Check #{i+1}/10")
        logger.info(f"   ⏰ Time: {datetime.now()}")
        logger.info(f"   📊 Bot is active and monitoring...")
        await asyncio.sleep(2)
    
    logger.info("✅ Minimal bot test completed successfully!")

if __name__ == "__main__":
    print("🔧 Starting minimal bot...")
    asyncio.run(main())
