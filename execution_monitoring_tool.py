#!/usr/bin/env python3
"""
🔍 EXECUTION MONITORING TOOL
Monitor your bot during live trading to catch execution issues
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExecutionMonitor:
    """Monitor execution success/failure rates during live trading"""
    
    def __init__(self):
        self.stats = {
            'trades_detected': 0,
            'trades_executed': 0,
            'trades_failed': 0,
            'validation_failures': 0,
            'timeout_failures': 0,
            'dex_failures': {},
            'execution_times': [],
            'start_time': time.time()
        }
        self.last_trade_time = None
        
    def log_trade_detected(self, trade_info: Dict[str, Any]):
        """Log when a trade is detected"""
        self.stats['trades_detected'] += 1
        self.last_trade_time = time.time()
        
        token = trade_info.get('token_mint', 'Unknown')[:8]
        action = trade_info.get('action', 'Unknown')
        
        logger.info(f"📊 TRADE #{self.stats['trades_detected']}: {action.upper()} {token}...")
        
    def log_validation_failure(self, reason: str):
        """Log validation failures"""
        self.stats['validation_failures'] += 1
        logger.warning(f"⚠️ VALIDATION FAILURE #{self.stats['validation_failures']}: {reason}")
        
    def log_execution_success(self, execution_time: float, dex_used: str):
        """Log successful execution"""
        self.stats['trades_executed'] += 1
        self.stats['execution_times'].append(execution_time)
        
        logger.info(f"✅ EXECUTION SUCCESS #{self.stats['trades_executed']}: {execution_time:.2f}s via {dex_used}")
        
    def log_execution_failure(self, reason: str, dex_attempted: str = None):
        """Log execution failures"""
        self.stats['trades_failed'] += 1
        
        if 'timeout' in reason.lower():
            self.stats['timeout_failures'] += 1
        
        if dex_attempted:
            self.stats['dex_failures'][dex_attempted] = self.stats['dex_failures'].get(dex_attempted, 0) + 1
            
        logger.error(f"❌ EXECUTION FAILURE #{self.stats['trades_failed']}: {reason}")
        
    def get_stats_summary(self) -> str:
        """Generate stats summary"""
        runtime = time.time() - self.stats['start_time']
        runtime_hours = runtime / 3600
        
        success_rate = 0
        if self.stats['trades_detected'] > 0:
            success_rate = (self.stats['trades_executed'] / self.stats['trades_detected']) * 100
        
        avg_execution_time = 0
        if self.stats['execution_times']:
            avg_execution_time = sum(self.stats['execution_times']) / len(self.stats['execution_times'])
        
        summary = f"""
🔍 EXECUTION MONITORING SUMMARY
========================================
Runtime: {runtime_hours:.1f} hours
Trades Detected: {self.stats['trades_detected']}
Trades Executed: {self.stats['trades_executed']}
Trades Failed: {self.stats['trades_failed']}
Success Rate: {success_rate:.1f}%

FAILURE BREAKDOWN:
- Validation Failures: {self.stats['validation_failures']}
- Timeout Failures: {self.stats['timeout_failures']}
- DEX Failures: {dict(self.stats['dex_failures'])}

PERFORMANCE:
- Average Execution Time: {avg_execution_time:.2f}s
- Last Trade: {time.time() - self.last_trade_time:.1f}s ago (if any)

HEALTH STATUS:
"""
        
        if success_rate >= 80:
            summary += "🟢 EXCELLENT - System performing well"
        elif success_rate >= 60:
            summary += "🟡 GOOD - Minor issues to monitor"
        elif success_rate >= 40:
            summary += "🟠 FAIR - Some execution problems"
        else:
            summary += "🔴 POOR - Significant execution issues"
            
        return summary
        
    def check_execution_health(self) -> Dict[str, Any]:
        """Check if execution is healthy"""
        issues = []
        
        # Check success rate
        if self.stats['trades_detected'] > 5:  # Only after some trades
            success_rate = (self.stats['trades_executed'] / self.stats['trades_detected']) * 100
            if success_rate < 50:
                issues.append(f"Low success rate: {success_rate:.1f}%")
        
        # Check timeout issues
        if self.stats['timeout_failures'] > 3:
            issues.append(f"High timeout failures: {self.stats['timeout_failures']}")
        
        # Check DEX failures
        total_dex_failures = sum(self.stats['dex_failures'].values())
        if total_dex_failures > 10:
            issues.append(f"High DEX failures: {total_dex_failures}")
        
        # Check if no trades detected recently
        if self.last_trade_time and (time.time() - self.last_trade_time) > 3600:  # 1 hour
            issues.append("No trades detected in last hour")
            
        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'stats': self.stats
        }

# Global monitor instance
monitor = ExecutionMonitor()

async def start_monitoring():
    """Start monitoring execution health"""
    logger.info("🔍 Starting execution monitoring...")
    
    while True:
        try:
            # Check health every 5 minutes
            await asyncio.sleep(300)
            
            health = monitor.check_execution_health()
            
            if not health['healthy']:
                logger.warning("⚠️ EXECUTION HEALTH ISSUES DETECTED:")
                for issue in health['issues']:
                    logger.warning(f"   - {issue}")
            else:
                logger.info("✅ Execution health check: All systems operational")
                
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")

if __name__ == "__main__":
    # Example usage
    print("🔍 EXECUTION MONITORING TOOL")
    print("=" * 40)
    print("To use this tool:")
    print("1. Import: from execution_monitoring_tool import monitor")
    print("2. In your trade detection: monitor.log_trade_detected(trade_info)")
    print("3. In your execution success: monitor.log_execution_success(time, dex)")
    print("4. In your execution failure: monitor.log_execution_failure(reason)")
    print("5. Get stats: print(monitor.get_stats_summary())")
    
    # Start monitoring
    asyncio.run(start_monitoring())
