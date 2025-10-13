#!/usr/bin/env python3

import asyncio
import logging
import time
from config import CopyTradeConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalCopyTradingBot:
    def __init__(self, config: CopyTradeConfig):
        logger.info("MINIMAL BOT: Initializing...")
        self.config = config
        self.is_running = False
        self.target_wallets = config.target_wallets
        logger.info(f"MINIMAL BOT: Loaded {len(self.target_wallets)} target wallets")
        
    async def start_monitoring(self):
        """Minimal start_monitoring to test the hang"""
        try:
            logger.info("MINIMAL BOT: start_monitoring called")
            logger.info("MINIMAL BOT: Setting is_running to True")
            self.is_running = True
            logger.info(f"MINIMAL BOT: is_running = {self.is_running}")
            
            logger.info("MINIMAL BOT: About to enter while loop")
            iteration = 0
            while self.is_running and iteration < 5:  # Limit iterations for testing
                iteration += 1
                logger.info(f"MINIMAL BOT: While loop iteration {iteration}")
                
                try:
                    logger.info("MINIMAL BOT: Simulating WebSocket monitoring...")
                    # Simulate some work
                    await asyncio.sleep(2)
                    logger.info("MINIMAL BOT: WebSocket monitoring simulation complete")
                    
                    # Break after one iteration for testing
                    break
                    
                except Exception as e:
                    logger.error(f"MINIMAL BOT: Error in monitoring: {e}")
                    break
            
            logger.info("MINIMAL BOT: Exited while loop")
            
        except Exception as e:
            logger.error(f"MINIMAL BOT: Error in start_monitoring: {e}")
            import traceback
            logger.error(traceback.format_exc())

async def main():
    try:
        logger.info("MINIMAL BOT: Starting main()")
        
        # Create minimal config
        config = CopyTradeConfig()
        logger.info("MINIMAL BOT: Config created")
        
        # Create bot instance
        bot = MinimalCopyTradingBot(config)
        logger.info("MINIMAL BOT: Bot instance created")
        
        # Start monitoring
        logger.info("MINIMAL BOT: Calling start_monitoring...")
        await bot.start_monitoring()
        logger.info("MINIMAL BOT: start_monitoring completed")
        
    except Exception as e:
        logger.error(f"MINIMAL BOT: Error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
