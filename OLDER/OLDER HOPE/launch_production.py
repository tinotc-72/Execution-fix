#!/usr/bin/env python3
"""
Production launcher for the trading system.
Handles environment verification, system startup, and logging.
"""

import os
import sys
import asyncio
import logging
import signal
from datetime import datetime
import subprocess
from supervisor import TradingSupervisor

# Configure production logging
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Setup rotating log files with timestamps
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/production_{timestamp}.log'),
        logging.StreamHandler()
    ]
)

async def verify_environment():
    """Verify all required components are in place."""
    required_files = [
        'main.py',
        'supervisor.py',
        'monitor.py',
        'preflight_check.py',
        'fast_executor.py',
        'jito_service.py',
        'env_keys.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logging.error(f"Missing required files: {', '.join(missing_files)}")
        return False
        
    logging.info("✅ Environment verification passed")
    return True

async def main():
    print("\n🚀 Production Trading System Launch")
    print("=================================")
    
    try:
        # Verify environment
        if not await verify_environment():
            logging.error("Environment verification failed")
            return
            
        # Log system info
        logging.info("System Configuration:")
        logging.info(f"Python version: {sys.version}")
        logging.info(f"Working directory: {os.getcwd()}")
        logging.info(f"Log directory: {os.path.abspath(LOG_DIR)}")
        
        # Start supervisor
        logging.info("\nStarting trading supervisor...")
        supervisor = TradingSupervisor()
        await supervisor.supervise()
        
    except KeyboardInterrupt:
        logging.info("\nReceived shutdown signal")
    except Exception as e:
        logging.error(f"Launch error: {str(e)}")
        raise
    finally:
        logging.info("Trading system shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"Fatal error: {str(e)}")
        sys.exit(1)
