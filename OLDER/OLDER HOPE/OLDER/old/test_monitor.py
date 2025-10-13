import asyncio
import logging
import json
from datetime import datetime
from solders.keypair import Keypair
from monitor import TradingMonitor
from fast_executor import FastExecutor
from solders.system_program import TransferParams, transfer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_test.log'),
        logging.StreamHandler()
    ]
)

def get_keypair_from_env():
    """Get Solana keypair from test wallet."""
    try:
        # Use test wallet key (for development/testing only)
        with open('test-wallet.json', 'r') as f:
            private_key = json.loads(f.read())
        return Keypair.from_bytes(bytes(private_key))
    except Exception as e:
        logging.error(f"Failed to load keypair: {str(e)}")
        raise

async def run_test_trades(monitor: TradingMonitor, amounts: list[float]):
    """Execute a series of test trades with monitoring."""
    for amount in amounts:
        try:
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=monitor.keypair.pubkey(),
                    to_pubkey=monitor.keypair.pubkey(),
                    lamports=int(amount * 1e9)
                )
            )
            
            # Execute trade
            signature = await monitor.executor.build_and_execute(
                instructions=[transfer_ix],
                use_jito=True,
                jito_retries=2,
                jito_timeout=1.0
            )
            
            if signature:
                # Track trade execution
                await monitor.track_trade(signature, amount)
                await asyncio.sleep(2)  # Wait for confirmation
            else:
                logging.error(f"Failed to execute {amount} SOL trade")
                
        except Exception as e:
            logging.error(f"Error executing {amount} SOL trade: {str(e)}")

async def test_monitoring():
    """Test the monitoring system."""
    try:
        # Get keypair from environment
        keypair = get_keypair_from_env()
        logging.info(f"Using wallet: {keypair.pubkey()}")
        
        # Initialize monitor
        monitor = TradingMonitor(keypair)
        await monitor.start()
        
        logging.info("\n🧪 Starting Monitor Test")
        
        # Test trades with different amounts
        test_amounts = [0.001, 0.01, 0.1]
        await run_test_trades(monitor, test_amounts)
        
        # Let monitor run for a bit to collect metrics
        await asyncio.sleep(10)
        
        # Stop monitoring
        await monitor.stop()
        
    except Exception as e:
        logging.error(f"Monitor test failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test_monitoring())
    except KeyboardInterrupt:
        logging.info("\n👋 Test interrupted by user")
    except Exception as e:
        logging.error(f"Test error: {str(e)}")
