#!/usr/bin/env python3

import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestBot:
    def __init__(self):
        self.is_running = False
        
    async def start_monitoring(self):
        """Test start_monitoring function to isolate the hang"""
        try:
            logger.info("DEBUG: start_monitoring called")
            logger.info("Starting WebSocket monitoring with auto-restart...")
            self.is_running = True
            logger.info(f"DEBUG: self.is_running = {self.is_running}")
            
            # Main monitoring loop with auto-restart
            logger.info("DEBUG: About to enter while loop")
            loop_count = 0
            while self.is_running and loop_count < 3:  # Limit to 3 iterations for testing
                logger.info(f"DEBUG: Inside while loop iteration {loop_count + 1}")
                loop_count += 1
                try:
                    logger.info("DEBUG: About to start WebSocket monitoring")
                    logger.info("INSTANT MODE: Starting real-time WebSocket monitoring immediately")
                    
                    # Simulate the WebSocket call
                    logger.info("DEBUG: Calling _monitor_wallets_via_websocket")
                    await self._test_websocket_monitor()
                    logger.info("DEBUG: _monitor_wallets_via_websocket returned")
                    
                    # Break out for testing
                    break
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    break
                    
            logger.info("DEBUG: Exited while loop")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def _test_websocket_monitor(self):
        """Test WebSocket monitor function"""
        logger.info("DEBUG: Inside _test_websocket_monitor")
        await asyncio.sleep(1)  # Simulate some work
        logger.info("DEBUG: _test_websocket_monitor completed")

async def main():
    logger.info("DEBUG: main() function started!")
    
    bot = TestBot()
    logger.info("DEBUG: TestBot created")
    
    logger.info("DEBUG: Calling start_monitoring()...")
    await bot.start_monitoring()
    logger.info("DEBUG: start_monitoring() completed")

if __name__ == "__main__":
    asyncio.run(main())
