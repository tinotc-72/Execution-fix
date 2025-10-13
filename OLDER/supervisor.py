import asyncio
import logging
import signal
import sys
from datetime import datetime
import base58
from solders.keypair import Keypair
from env_keys import kz
from monitor import TradingMonitor
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('supervisor.log'),
        logging.StreamHandler()
    ]
)

class TradingSupervisor:
    def __init__(self):
        self.monitor = None
        self.bot_process = None
        self.running = False
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        logging.info("Received shutdown signal. Cleaning up...")
        self.running = False
        if self.bot_process:
            self.bot_process.terminate()
        asyncio.create_task(self.cleanup())
        
    async def run_preflight_check(self) -> bool:
        """Run preflight checks before starting bot."""
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, 'preflight_check.py',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logging.error(f"Preflight check failed:\n{stderr.decode()}")
                return False
                
            logging.info(f"Preflight check passed:\n{stdout.decode()}")
            return True
            
        except Exception as e:
            logging.error(f"Error running preflight check: {str(e)}")
            return False
            
    async def start_bot(self):
        """Start the main trading bot."""
        try:
            self.bot_process = await asyncio.create_subprocess_exec(
                sys.executable, 'main.py',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logging.info("Trading bot started")
            
            # Monitor bot output
            while self.running:
                line = await self.bot_process.stdout.readline()
                if not line:
                    break
                logging.info(f"Bot: {line.decode().strip()}")
                
        except Exception as e:
            logging.error(f"Error starting bot: {str(e)}")
            
    async def supervise(self):
        """Main supervision loop with enhanced monitoring"""
        try:
            restart_delay = 5
            max_restart_delay = 300  # 5 minutes
            consecutive_failures = 0
            max_failures = 5
            
            while True:
                try:
                    # Run preflight check
                    if not await self.run_preflight_check():
                        logging.error("Preflight check failed. Waiting before retry...")
                        await asyncio.sleep(restart_delay)
                        continue
                        
                    # Initialize monitor with retry
                    retry_count = 0
                    while retry_count < 3:
                        try:
                            private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
                            keypair = Keypair.from_bytes(private_key)
                            self.monitor = TradingMonitor(keypair)
                            await self.monitor.initialize()
                            break
                        except Exception as e:
                            retry_count += 1
                            logging.error(f"Monitor initialization failed (attempt {retry_count}): {e}")
                            await asyncio.sleep(2)
                            
                    if retry_count >= 3:
                        raise Exception("Failed to initialize monitor after 3 attempts")
                        
                    # Start monitoring and bot
                    self.running = True
                    monitor_task = asyncio.create_task(self.monitor.monitor_loop())
                    bot_task = asyncio.create_task(self.start_bot())
                    
                    # Wait for either task to complete or fail
                    done, pending = await asyncio.wait(
                        [monitor_task, bot_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # Cancel pending tasks
                    for task in pending:
                        task.cancel()
                        
                    # Check what happened
                    for task in done:
                        try:
                            await task
                        except Exception as e:
                            logging.error(f"Task failed with error: {e}")
                            
                    # If we get here, something failed
                    consecutive_failures += 1
                    logging.warning(f"Bot or monitor failed. Consecutive failures: {consecutive_failures}")
                    
                    # Apply exponential backoff if we're having repeated failures
                    if consecutive_failures >= max_failures:
                        restart_delay = min(restart_delay * 2, max_restart_delay)
                        logging.warning(f"Multiple failures detected. Increasing restart delay to {restart_delay}s")
                    else:
                        restart_delay = 5  # Reset delay if we've had some success
                        
                    # Cleanup before restart
                    await self.cleanup()
                    await asyncio.sleep(restart_delay)
                    
                except Exception as e:
                    logging.error(f"Error in supervision loop: {e}")
                    await asyncio.sleep(restart_delay)
                    
        except Exception as e:
            logging.error(f"Critical error in supervisor: {e}")
            
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.monitor:
                await self.monitor.cleanup()
            
            if self.bot_process:
                try:
                    self.bot_process.terminate()
                    await asyncio.wait_for(self.bot_process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    self.bot_process.kill()
                    
            self.running = False
            logging.info("Cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            
    async def _check_bot_health(self):
        """Check if the bot is healthy"""
        if not self.bot_process:
            return False
            
        try:
            # Check if process is still running
            if self.bot_process.returncode is not None:
                return False
                
            # Check recent log output
            while True:
                line = await self.bot_process.stdout.readline()
                if not line:
                    break
                    
                # Log and check for error indicators
                log_line = line.decode().strip()
                logging.info(f"Bot output: {log_line}")
                
                if "error" in log_line.lower() or "exception" in log_line.lower():
                    logging.warning(f"Potential issue detected: {log_line}")
                    
            return True
            
        except Exception as e:
            logging.error(f"Error checking bot health: {e}")
            return False

async def main():
    print("\n🎮 Starting Trading Supervisor")
    print("============================")
    
    supervisor = TradingSupervisor()
    await supervisor.supervise()

if __name__ == "__main__":
    asyncio.run(main())
