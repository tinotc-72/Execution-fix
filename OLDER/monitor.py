import asyncio
import logging
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from env_keys import kz
from fast_executor import FastExecutor
from dataclasses import dataclass
from enum import Enum, auto
import time
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)

class ErrorType(Enum):
    """Classification of possible trading errors."""
    RPC_ERROR = auto()
    JITO_ERROR = auto()
    TRANSACTION_ERROR = auto()
    BALANCE_ERROR = auto()
    NETWORK_ERROR = auto()
    UNKNOWN_ERROR = auto()

@dataclass
class HealthMetrics:
    """System health metrics."""
    rpc_latency: float = 0.0
    jito_latency: float = 0.0
    success_rate: float = 100.0
    balance: float = 0.0
    error_rate: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None

class TradingMonitor:
    def __init__(self, keypair: Keypair):
        self.keypair = keypair
        self.executor = None
        self.start_time = datetime.now()
        self.trades: List[Dict] = []
        self.initial_balance = 0.0
        self.metrics = HealthMetrics()
        
        # Enhanced alerts configuration
        self.alerts = {
            'balance': 0.05,      # Alert if balance drops below 0.05 SOL
            'latency': 500,       # Alert if RPC latency > 500ms
            'error_rate': 10,     # Alert if error rate exceeds 10%
            'success_rate': 90,   # Alert if success rate drops below 90%
            'consecutive_errors': 3  # Alert after 3 consecutive errors
        }
        
        # Error tracking
        self.error_count = 0
        self.error_history: List[Dict] = []
        self.recovery_attempts = 0
        self.last_recovery = None
        
        # Performance tracking
        self.performance_metrics = {
            'trades_total': 0,
            'trades_successful': 0,
            'total_fees': 0,
            'avg_latency': 0,
            'peak_latency': 0
        }
        
    async def initialize(self):
        """Initialize monitor with FastExecutor and verify setup."""
        try:
            self.executor = FastExecutor(self.keypair)
            await self.executor.initialize()
            
            # Get initial state with retries
            retry_count = 0
            while retry_count < 3:
                self.initial_balance = await self.get_balance_with_retry()
                if self.initial_balance > 0:
                    break
                retry_count += 1
                await asyncio.sleep(1)
                
            self.metrics.balance = self.initial_balance
            
            # Log initialization
            logging.info(f"\n🚀 Trading Monitor Initialized:")
            logging.info(f"Wallet: {self.keypair.pubkey()}")
            logging.info(f"Initial Balance: {self.initial_balance:.4f} SOL")
            
            # Check if balance is sufficient for testing
            if self.initial_balance < self.alerts['balance']:
                logging.warning(f"⚠️ Low balance warning: {self.initial_balance:.4f} SOL")
                # Continue anyway for testing
            
            # Verify RPC health
            health = await self.check_health()
            if not health:
                logging.warning("⚠️ Initial health check failed - continuing with monitoring")
                
            return True
            
        except Exception as e:
            logging.error(f"❌ Monitor initialization error: {str(e)}")
            traceback.print_exc()
            return False
            
    async def get_balance_with_retry(self, max_retries: int = 3) -> float:
        """Get wallet balance with retries and fallback."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                balance = await self.executor.get_sol_balance()
                if balance is not None:
                    return balance
            except Exception as e:
                last_error = e
                await asyncio.sleep(0.5 * (attempt + 1))
                
        logging.error(f"Failed to get balance after {max_retries} attempts: {str(last_error)}")
        return 0.0
            
    async def check_health(self) -> bool:
        """Enhanced system health check with metrics."""
        try:
            start_time = time.time()
            
            # Check RPC health
            blockhash = await self.executor.get_latest_blockhash()
            self.metrics.rpc_latency = (time.time() - start_time) * 1000
            
            # Check Jito connection
            start_time = time.time()
            jito_status = await self.executor.jito_client.check_connection()
            self.metrics.jito_latency = (time.time() - start_time) * 1000
            
            # Update metrics
            self.metrics.balance = await self.get_balance_with_retry()
            if self.performance_metrics['trades_total'] > 0:
                self.metrics.success_rate = (
                    self.performance_metrics['trades_successful'] /
                    self.performance_metrics['trades_total'] * 100
                )
            
            # Check for alert conditions
            alerts = []
            if self.metrics.balance < self.alerts['balance']:
                alerts.append(f"⚠️ Low balance: {self.metrics.balance:.4f} SOL")
            if self.metrics.rpc_latency > self.alerts['latency']:
                alerts.append(f"⚠️ High RPC latency: {self.metrics.rpc_latency:.2f}ms")
            if self.metrics.success_rate < self.alerts['success_rate']:
                alerts.append(f"⚠️ Low success rate: {self.metrics.success_rate:.1f}%")
            
            if alerts:
                logging.warning("\n".join(alerts))
                
            return len(alerts) == 0
                
        except Exception as e:
            logging.error(f"Health check failed: {str(e)}")
            self.record_error(ErrorType.NETWORK_ERROR, str(e))
            return False
            
    def record_error(self, error_type: ErrorType, details: str):
        """Record and classify an error for analysis."""
        now = datetime.now()
        error_entry = {
            'type': error_type,
            'details': details,
            'timestamp': now,
            'balance': self.metrics.balance,
            'metrics': self.metrics.__dict__.copy()
        }
        
        self.error_history.append(error_entry)
        self.error_count += 1
        self.metrics.last_error = details
        self.metrics.last_error_time = now
        
        # Update error rate
        time_window = (now - self.start_time).total_seconds() / 3600  # hours
        self.metrics.error_rate = len(self.error_history) / max(1, time_window)
        
        # Check if recovery is needed
        if self.error_count >= self.alerts['consecutive_errors']:
            asyncio.create_task(self.attempt_recovery(error_type))
            
    async def attempt_recovery(self, error_type: ErrorType):
        """Attempt to recover from errors based on type."""
        if self.last_recovery and (datetime.now() - self.last_recovery) < timedelta(minutes=5):
            return  # Avoid too frequent recovery attempts
            
        self.last_recovery = datetime.now()
        self.recovery_attempts += 1
        
        try:
            logging.warning(f"\n🔄 Attempting system recovery ({self.recovery_attempts})...")
            
            if error_type == ErrorType.RPC_ERROR:
                # Reinitialize RPC connection
                await self.executor.initialize()
                
            elif error_type == ErrorType.JITO_ERROR:
                # Reinitialize Jito client
                await self.executor.jito_client.initialize()
                
            elif error_type == ErrorType.BALANCE_ERROR:
                # Verify balance and transaction history
                current_balance = await self.get_balance_with_retry()
                logging.info(f"Balance verification: {current_balance:.4f} SOL")
                
            # Check if recovery was successful
            if await self.check_health():
                logging.info("✅ System recovery successful")
                self.error_count = 0
            else:
                logging.error("❌ System recovery failed")
                
        except Exception as e:
            logging.error(f"Recovery attempt failed: {str(e)}")
            traceback.print_exc()
            
    def log_trade(self, trade_data: Dict):
        """Log trade details for monitoring."""
        self.trades.append({
            'timestamp': datetime.now().isoformat(),
           
        })
        
    async def generate_report(self) -> Dict:
        """Generate monitoring report."""
        current_balance = await self.executor.get_balance(self.keypair.pubkey())
        pnl = current_balance - self.initial_balance
        
        return {
            'start_time': self.start_time.isoformat(),
            'uptime': str(datetime.now() - self.start_time),
            'initial_balance': self.initial_balance,
            'current_balance': current_balance,
            'pnl': pnl,
            'trade_count': len(self.trades),
            'error_count': self.error_count,
            'last_trades': self.trades[-5:] if self.trades else []
        }
        
    async def track_trade(self, signature: str, amount: float):
        """Track and analyze a trade execution."""
        try:
            start_time = time.time()
            
            # Get transaction info with retries
            tx_info = None
            for attempt in range(3):
                success, info = await self.executor.verify_transaction_status(signature)
                if success:
                    tx_info = info
                    break
                await asyncio.sleep(0.5 * (attempt + 1))
            
            if not tx_info:
                self.record_error(
                    ErrorType.TRANSACTION_ERROR,
                    f"Failed to verify transaction {signature}"
                )
                return
            
            # Calculate metrics
            execution_time = (time.time() - start_time) * 1000
            fee = tx_info.get('fee', 0) / 1e9
            status = tx_info.get('status', 'unknown')
            
            # Record trade
            trade_record = {
                'signature': signature,
                'amount': amount,
                'fee': fee,
                'status': status,
                'execution_time': execution_time,
                'timestamp': datetime.now(),
                'balance_after': await self.get_balance_with_retry()
            }
            self.trades.append(trade_record)
            
            # Update performance metrics
            self.performance_metrics['trades_total'] += 1
            if status == 'confirmed':
                self.performance_metrics['trades_successful'] += 1
            self.performance_metrics['total_fees'] += fee
            
            # Update latency metrics
            self.performance_metrics['avg_latency'] = (
                (self.performance_metrics['avg_latency'] * (len(self.trades) - 1) + execution_time) /
                len(self.trades)
            )
            self.performance_metrics['peak_latency'] = max(
                self.performance_metrics['peak_latency'],
                execution_time
            )
            
            # Log trade summary
            logging.info(f"\n📊 Trade Summary ({signature}):")
            logging.info(f"Status: {status}")
            logging.info(f"Amount: {amount:.4f} SOL")
            logging.info(f"Fee: {fee:.6f} SOL")
            logging.info(f"Execution Time: {execution_time:.2f}ms")
            
        except Exception as e:
            logging.error(f"Error tracking trade {signature}: {str(e)}")
            self.record_error(ErrorType.UNKNOWN_ERROR, str(e))

    async def monitor_loop(self):
        """Main monitoring loop."""
        update_interval = 5  # seconds
        health_check_interval = 30  # seconds
        last_health_check = 0
        
        logging.info("\n🔄 Starting monitoring service...")
        
        while True:
            try:
                now = time.time()
                
                # Regular health check
                if now - last_health_check >= health_check_interval:
                    await self.check_health()
                    last_health_check = now
                    
                    # Log system status
                    logging.info(f"\n📈 System Status:")
                    logging.info(f"Uptime: {datetime.now() - self.start_time}")
                    logging.info(f"Balance: {self.metrics.balance:.4f} SOL")
                    logging.info(f"Success Rate: {self.metrics.success_rate:.1f}%")
                    logging.info(f"Error Rate: {self.metrics.error_rate:.2f}/hour")
                    logging.info(f"RPC Latency: {self.metrics.rpc_latency:.2f}ms")
                    logging.info(f"Total Trades: {self.performance_metrics['trades_total']}")
                    logging.info(f"Total Fees: {self.performance_metrics['total_fees']:.6f} SOL")
                
                await asyncio.sleep(update_interval)
                
            except asyncio.CancelledError:
                logging.info("Monitoring service stopped")
                break
            except Exception as e:
                logging.error(f"Monitor loop error: {str(e)}")
                traceback.print_exc()
                await asyncio.sleep(update_interval)
                
    async def start(self):
        """Start the monitoring service with error handling."""
        try:
            if not await self.initialize():
                logging.warning("Monitor initialization issues - attempting to continue")
            
            self.monitor_task = asyncio.create_task(self.monitor_loop())
            logging.info("\n🚀 Monitoring service started")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start monitoring: {str(e)}")
            await self.cleanup()
            raise

    async def cleanup(self):
        """Clean up resources properly."""
        try:
            if self.executor:
                await self.executor.cleanup()
            
            # Close any other resources here
            
        except Exception as e:
            logging.error(f"Cleanup error: {str(e)}")
            traceback.print_exc()
            
    async def stop(self):
        """Stop the monitoring service."""
        if hasattr(self, 'monitor_task'):
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            
        if self.executor:
            await self.executor.cleanup()
            
        # Log final statistics
        runtime = datetime.now() - self.start_time
        final_balance = await self.get_balance_with_retry()
        balance_change = final_balance - self.initial_balance
        
        logging.info(f"\n📊 Final Statistics:")
        logging.info(f"Runtime: {runtime}")
        logging.info(f"Initial Balance: {self.initial_balance:.4f} SOL")
        logging.info(f"Final Balance: {final_balance:.4f} SOL")
        logging.info(f"Balance Change: {balance_change:.4f} SOL")
        logging.info(f"Total Trades: {self.performance_metrics['trades_total']}")
        logging.info(f"Successful Trades: {self.performance_metrics['trades_successful']}")
        logging.info(f"Success Rate: {self.metrics.success_rate:.1f}%")
        logging.info(f"Total Fees: {self.performance_metrics['total_fees']:.6f} SOL")
        logging.info(f"Average Latency: {self.performance_metrics['avg_latency']:.2f}ms")
        logging.info(f"Peak Latency: {self.performance_metrics['peak_latency']:.2f}ms")
        logging.info("Monitoring service stopped")
        
    async def close(self):
        """Cleanup monitor resources"""
        try:
            # Save final statistics
            self._save_metrics()
            
            # Close any active sessions
            if hasattr(self, 'session'):
                await self.session.close()
            
            logging.info("Monitor shutdown complete")
        except Exception as e:
            logging.error(f"Error during monitor shutdown: {e}")
            
    def _save_metrics(self):
        """Save performance metrics to file"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'uptime': str(datetime.now() - self.start_time),
                'trades_total': self.performance_metrics['trades_total'],
                'trades_successful': self.performance_metrics['trades_successful'],
                'total_fees': self.performance_metrics['total_fees'],
                'avg_latency': self.performance_metrics['avg_latency']
            }
            
            with open('logs/performance_metrics.json', 'w') as f:
                json.dump(metrics, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving metrics: {e}")
            
    def get_statistics(self) -> dict:
        """Get current trading statistics"""
        stats = {
            'Uptime': str(datetime.now() - self.start_time),
            'Balance': f"{self.metrics.balance:.4f} SOL",
            'Success Rate': f"{self.metrics.success_rate:.1f}%",
            'Error Rate': f"{self.metrics.error_rate:.2f}/hour",
            'RPC Latency': f"{self.metrics.rpc_latency:.2f}ms",
            'Total Trades': self.performance_metrics['trades_total'],
            'Total Fees': f"{self.performance_metrics['total_fees']:.6f} SOL"
        }
        return stats

async def main():
    """Run monitor as standalone for testing."""
    try:
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        
        monitor = TradingMonitor(keypair)
        await monitor.initialize()
        
        print("\n📡 Starting Trading Monitor")
        print("==========================")
        
        # Run monitor for test period
        try:
            await asyncio.wait_for(monitor.monitor_loop(), timeout=300)  # 5 minute test
        except asyncio.TimeoutError:
            print("\n✅ Monitor test completed")
            
        # Generate final report
        report = await monitor.generate_report()
        print(f"\n📊 Final Report:\n{json.dumps(report, indent=2)}")
        
    except Exception as e:
        logging.error(f"Monitor test failed: {str(e)}")
    finally:
        if monitor:
            await monitor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
