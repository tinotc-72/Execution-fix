#!/usr/bin/env python3
"""
⚡ REAL-TIME COVERAGE MONITOR
Live monitoring tool to track copy trading performance and identify missed trades in real-time
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
import logging
import websockets
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realtime_coverage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradeEvent:
    """Real-time trade event"""
    timestamp: datetime
    wallet: str
    signature: str
    program_id: str
    token_mint: Optional[str]
    detected: bool = False
    executed: bool = False
    execution_time: Optional[float] = None
    failure_reason: Optional[str] = None

@dataclass
class CoverageMetrics:
    """Real-time coverage metrics"""
    total_events: int
    detected_events: int
    executed_events: int
    detection_rate: float
    execution_rate: float
    overall_rate: float
    avg_execution_time: float
    recent_misses: List[TradeEvent]

class RealTimeCoverageMonitor:
    """Real-time copy trading coverage monitor"""
    
    def __init__(self):
        self.target_wallets = {
            "HvnE6QF6ke2Yos6xSgtiqW2kuquxkJkMQMkKzgL3ipCj",
            "your_second_wallet_here"  # Add your second target wallet
        }
        
        # Tracking data structures
        self.trade_events: Dict[str, TradeEvent] = {}  # signature -> TradeEvent
        self.recent_events = deque(maxlen=1000)  # Last 1000 events
        self.metrics_history = deque(maxlen=100)  # Last 100 metric snapshots
        
        # Performance tracking
        self.detection_times = deque(maxlen=100)
        self.execution_times = deque(maxlen=100)
        self.failure_counts = defaultdict(int)
        
        # WebSocket connection
        self.ws_connection = None
        self.monitoring_active = False
        
    async def start_monitoring(self, duration_hours: int = 6):
        """Start real-time monitoring for specified duration"""
        logger.info(f"🚀 Starting real-time coverage monitoring for {duration_hours} hours")
        
        self.monitoring_active = True
        end_time = datetime.now() + timedelta(hours=duration_hours)
        
        # Start monitoring tasks
        tasks = [
            self.monitor_target_wallets(),
            self.monitor_bot_execution(),
            self.generate_periodic_reports(),
            self.track_performance_metrics()
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("⚠️ Monitoring interrupted by user")
        finally:
            self.monitoring_active = False
            await self.generate_final_report()
    
    async def monitor_target_wallets(self):
        """Monitor target wallets for new transactions"""
        logger.info("👀 Starting target wallet monitoring...")
        
        while self.monitoring_active:
            try:
                # Connect to Solana WebSocket for account monitoring
                # This is a simplified version - you'd need to implement actual WebSocket connection
                await self.check_wallet_transactions()
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Error in wallet monitoring: {e}")
                await asyncio.sleep(5)
    
    async def check_wallet_transactions(self):
        """Check for new transactions from target wallets"""
        # This would connect to your actual transaction detection system
        # For now, this is a placeholder that simulates transaction detection
        
        # Simulate detecting a transaction (replace with actual detection logic)
        if hasattr(self, '_last_check'):
            time_since_last = time.time() - self._last_check
            if time_since_last > 30:  # Simulate transaction every 30 seconds
                await self.simulate_transaction_detection()
        
        self._last_check = time.time()
    
    async def simulate_transaction_detection(self):
        """Simulate transaction detection for testing"""
        # This is just for testing - replace with actual detection
        signature = f"sim_{int(time.time())}"
        wallet = list(self.target_wallets)[0]
        
        trade_event = TradeEvent(
            timestamp=datetime.now(),
            wallet=wallet,
            signature=signature,
            program_id="11111111111111111111111111111112",
            token_mint="So11111111111111111111111111111111111111112",
            detected=True
        )
        
        self.trade_events[signature] = trade_event
        self.recent_events.append(trade_event)
        
        logger.info(f"📊 Detected transaction: {signature[:16]}...")
    
    async def monitor_bot_execution(self):
        """Monitor bot execution logs for trade confirmations"""
        logger.info("🤖 Starting bot execution monitoring...")
        
        # Monitor bot log file for execution confirmations
        try:
            await self.tail_bot_log()
        except Exception as e:
            logger.error(f"❌ Error monitoring bot execution: {e}")
    
    async def tail_bot_log(self):
        """Tail bot log file for real-time execution tracking"""
        log_file = "bot_output.log"
        
        try:
            with open(log_file, 'r') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while self.monitoring_active:
                    line = f.readline()
                    if line:
                        await self.process_bot_log_line(line.strip())
                    else:
                        await asyncio.sleep(0.1)  # Brief pause if no new lines
                        
        except FileNotFoundError:
            logger.warning(f"⚠️ Bot log file {log_file} not found, using simulation")
            await self.simulate_bot_execution()
    
    async def simulate_bot_execution(self):
        """Simulate bot execution for testing"""
        while self.monitoring_active:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            # Simulate execution of detected trades
            for signature, event in self.trade_events.items():
                if event.detected and not event.executed:
                    # Simulate 85% success rate
                    success = time.time() % 7 != 0  # ~85% success
                    
                    if success:
                        event.executed = True
                        event.execution_time = 0.5 + (time.time() % 10) / 10  # 0.5-1.5s
                        logger.info(f"✅ Executed trade: {signature[:16]}...")
                    else:
                        event.failure_reason = "simulated_failure"
                        logger.warning(f"❌ Failed to execute: {signature[:16]}...")
    
    async def process_bot_log_line(self, line: str):
        """Process a line from bot log to track execution"""
        try:
            # Parse log line for execution information
            # Customize this based on your actual log format
            
            if "EXECUTED" in line or "SUCCESS" in line:
                # Extract signature and timing info
                # This needs to match your actual log format
                signature = self.extract_signature_from_log(line)
                
                if signature and signature in self.trade_events:
                    event = self.trade_events[signature]
                    event.executed = True
                    
                    # Calculate execution time
                    if event.timestamp:
                        execution_time = (datetime.now() - event.timestamp).total_seconds()
                        event.execution_time = execution_time
                        self.execution_times.append(execution_time)
                    
                    logger.info(f"✅ Confirmed execution: {signature[:16]}...")
            
            elif "FAILED" in line or "ERROR" in line:
                signature = self.extract_signature_from_log(line)
                if signature and signature in self.trade_events:
                    event = self.trade_events[signature]
                    event.failure_reason = self.extract_failure_reason(line)
                    self.failure_counts[event.failure_reason] += 1
                    
                    logger.warning(f"❌ Execution failed: {signature[:16]}...")
                    
        except Exception as e:
            logger.error(f"Error processing log line: {e}")
    
    def extract_signature_from_log(self, line: str) -> Optional[str]:
        """Extract transaction signature from log line"""
        # Implement based on your log format
        # This is a placeholder
        import re
        match = re.search(r'[A-Za-z0-9]{64,}', line)
        return match.group(0) if match else None
    
    def extract_failure_reason(self, line: str) -> str:
        """Extract failure reason from log line"""
        # Implement based on your log format
        if "slippage" in line.lower():
            return "slippage_exceeded"
        elif "insufficient" in line.lower():
            return "insufficient_balance"
        elif "timeout" in line.lower():
            return "timeout"
        elif "rpc" in line.lower():
            return "rpc_error"
        else:
            return "unknown_error"
    
    async def track_performance_metrics(self):
        """Track performance metrics continuously"""
        while self.monitoring_active:
            try:
                metrics = self.calculate_current_metrics()
                self.metrics_history.append(metrics)
                
                # Log metrics every 5 minutes
                if len(self.metrics_history) % 30 == 0:  # Every 30 cycles (5 minutes if 10s intervals)
                    await self.log_current_performance(metrics)
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error tracking metrics: {e}")
                await asyncio.sleep(10)
    
    def calculate_current_metrics(self) -> CoverageMetrics:
        """Calculate current coverage metrics"""
        recent_events = list(self.recent_events)[-100:]  # Last 100 events
        
        total_events = len(recent_events)
        detected_events = sum(1 for event in recent_events if event.detected)
        executed_events = sum(1 for event in recent_events if event.executed)
        
        detection_rate = detected_events / total_events if total_events > 0 else 0
        execution_rate = executed_events / detected_events if detected_events > 0 else 0
        overall_rate = executed_events / total_events if total_events > 0 else 0
        
        # Calculate average execution time
        execution_times = [e.execution_time for e in recent_events if e.execution_time]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Get recent misses
        recent_misses = [e for e in recent_events if e.detected and not e.executed][-10:]
        
        return CoverageMetrics(
            total_events=total_events,
            detected_events=detected_events,
            executed_events=executed_events,
            detection_rate=detection_rate,
            execution_rate=execution_rate,
            overall_rate=overall_rate,
            avg_execution_time=avg_execution_time,
            recent_misses=recent_misses
        )
    
    async def log_current_performance(self, metrics: CoverageMetrics):
        """Log current performance metrics"""
        logger.info(f"""
📊 CURRENT PERFORMANCE SNAPSHOT:
   Overall Coverage: {metrics.overall_rate:.2%}
   Detection Rate: {metrics.detection_rate:.2%}
   Execution Rate: {metrics.execution_rate:.2%}
   Avg Execution Time: {metrics.avg_execution_time:.2f}s
   Recent Events: {metrics.total_events}
   Recent Misses: {len(metrics.recent_misses)}
""")
    
    async def generate_periodic_reports(self):
        """Generate periodic coverage reports"""
        while self.monitoring_active:
            await asyncio.sleep(3600)  # Every hour
            await self.generate_hourly_report()
    
    async def generate_hourly_report(self):
        """Generate hourly coverage report"""
        logger.info("📋 Generating hourly coverage report...")
        
        metrics = self.calculate_current_metrics()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = f"""
🕐 HOURLY COVERAGE REPORT - {datetime.now().strftime('%H:%M:%S')}
{'=' * 50}

📊 PERFORMANCE METRICS:
   Overall Coverage: {metrics.overall_rate:.2%}
   Detection Rate: {metrics.detection_rate:.2%}
   Execution Rate: {metrics.execution_rate:.2%}
   Average Execution Time: {metrics.avg_execution_time:.2f}s

📈 TRADE STATISTICS:
   Total Events (last 100): {metrics.total_events}
   Successfully Executed: {metrics.executed_events}
   Recent Misses: {len(metrics.recent_misses)}

❌ FAILURE BREAKDOWN:
"""
        
        for reason, count in self.failure_counts.items():
            report += f"   {reason.replace('_', ' ').title()}: {count}\n"
        
        report += f"""
🎯 PERFORMANCE TREND:
   Last 10 execution times: {list(self.execution_times)[-10:]}
   
⚡ RECOMMENDATIONS:
"""
        
        if metrics.overall_rate < 0.90:
            report += "   ⚠️ Coverage below 90% - investigate failures\n"
        elif metrics.overall_rate < 0.95:
            report += "   📈 Good coverage - optimize for 95%+\n"
        else:
            report += "   🎉 Excellent coverage! Maintain performance\n"
        
        # Save report
        with open(f'hourly_report_{timestamp}.txt', 'w') as f:
            f.write(report)
        
        logger.info(f"✅ Hourly report saved: hourly_report_{timestamp}.txt")
    
    async def generate_final_report(self):
        """Generate final comprehensive report"""
        logger.info("📋 Generating final coverage report...")
        
        final_metrics = self.calculate_current_metrics()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Comprehensive analysis
        total_signatures = len(self.trade_events)
        total_detected = sum(1 for event in self.trade_events.values() if event.detected)
        total_executed = sum(1 for event in self.trade_events.values() if event.executed)
        
        report = f"""
🎯 FINAL REAL-TIME COVERAGE ANALYSIS
{'=' * 50}
Session Duration: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SESSION TOTALS:
   Total Trade Events: {total_signatures}
   Successfully Detected: {total_detected}
   Successfully Executed: {total_executed}
   
   Final Detection Rate: {total_detected/total_signatures:.2%}
   Final Execution Rate: {total_executed/total_detected:.2%} (of detected)
   Final Overall Coverage: {total_executed/total_signatures:.2%}

⚡ PERFORMANCE ANALYSIS:
   Average Execution Time: {final_metrics.avg_execution_time:.2f}s
   Execution Times Range: {min(self.execution_times) if self.execution_times else 0:.2f}s - {max(self.execution_times) if self.execution_times else 0:.2f}s

❌ FAILURE ANALYSIS:
"""
        
        for reason, count in self.failure_counts.items():
            percentage = count / total_signatures if total_signatures > 0 else 0
            report += f"   {reason.replace('_', ' ').title()}: {count} ({percentage:.1%})\n"
        
        report += f"""
🔍 TOP MISSED TRANSACTIONS:
"""
        
        missed_events = [e for e in self.trade_events.values() if e.detected and not e.executed]
        for i, event in enumerate(missed_events[:5]):
            report += f"""   {i+1}. {event.signature[:16]}... at {event.timestamp}
      Reason: {event.failure_reason or 'unknown'}
      Token: {event.token_mint[:16] if event.token_mint else 'unknown'}...
      
"""
        
        report += f"""
🎯 FINAL ASSESSMENT:
"""
        
        if final_metrics.overall_rate >= 0.95:
            report += "   🎉 EXCELLENT! Achieved 95%+ coverage target!\n"
            report += "   🚀 Bot is performing at optimal level\n"
        elif final_metrics.overall_rate >= 0.90:
            report += "   📈 GOOD coverage - close to 95% target\n"
            report += "   🔧 Focus on optimizing failure points\n"
        else:
            report += "   ⚠️ Coverage below target - requires optimization\n"
            report += "   🛠️ Address main failure causes identified above\n"
        
        # Save final results
        with open(f'final_coverage_report_{timestamp}.txt', 'w') as f:
            f.write(report)
        
        # Save raw data
        with open(f'final_coverage_data_{timestamp}.json', 'w') as f:
            data = {
                'events': [asdict(event) for event in self.trade_events.values()],
                'metrics': asdict(final_metrics),
                'failure_counts': dict(self.failure_counts)
            }
            # Convert datetime objects to strings
            for event in data['events']:
                event['timestamp'] = event['timestamp'].isoformat()
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"✅ Final report saved: final_coverage_report_{timestamp}.txt")
        logger.info(f"📊 Final Coverage: {final_metrics.overall_rate:.2%}")

async def main():
    """Run real-time coverage monitoring"""
    print("⚡ REAL-TIME COPY TRADING COVERAGE MONITOR")
    print("=" * 50)
    
    monitor = RealTimeCoverageMonitor()
    
    # Get monitoring duration from user
    try:
        hours = int(input("Enter monitoring duration in hours (default 6): ") or "6")
    except ValueError:
        hours = 6
    
    print(f"🚀 Starting {hours}-hour monitoring session...")
    print("Press Ctrl+C to stop monitoring early")
    
    await monitor.start_monitoring(duration_hours=hours)

if __name__ == "__main__":
    asyncio.run(main())
