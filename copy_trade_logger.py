#!/usr/bin/env python3
"""
Copy Trading CSV Logger
Comprehensive logging system for copy trading performance tracking
"""

import csv
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CopyTradeRecord:
    """Data structure for copy trading records"""
    timestamp: str
    date: str
    time: str
    source_wallet: str
    source_wallet_short: str  # First 8 chars for readability
    trade_type: str  # 'buy' or 'sell'
    token_mint: str
    token_mint_short: str  # First 8 chars for readability
    amount_sol: float
    amount_usd: Optional[float]  # If we can get SOL price
    executor_used: str
    execution_status: str  # 'success', 'failed', 'partial'
    failure_reason: Optional[str]
    transaction_signature: Optional[str]
    solscan_link: Optional[str]
    detection_method: str  # 'websocket', 'polling', etc.
    detected_dex: str
    slippage_used: float
    execution_time_ms: Optional[int]
    pre_sol_balance: float
    post_sol_balance: float
    sol_balance_change: float
    token_balance_before: float
    token_balance_after: float
    token_balance_change: float
    trade_count_for_token: int  # How many times we've traded this token
    portfolio_position_count: int  # Total positions after trade
    notes: str

class CopyTradeCSVLogger:
    """CSV logger for copy trading activities"""
    
    def __init__(self, log_directory: str = None):
        """Initialize the CSV logger"""
        self.log_directory = log_directory or "copy_trade_logs"
        self.ensure_log_directory()
        
        # Create filename with date
        date_str = datetime.now().strftime("%Y%m%d")
        self.csv_filename = f"copy_trades_{date_str}.csv"
        self.csv_filepath = os.path.join(self.log_directory, self.csv_filename)
        
        # Initialize CSV file with headers
        self.initialize_csv_file()
        
    def ensure_log_directory(self):
        """Ensure the log directory exists"""
        Path(self.log_directory).mkdir(parents=True, exist_ok=True)
        
    def initialize_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_filepath):
            headers = [
                'timestamp',
                'date', 
                'time',
                'source_wallet',
                'source_wallet_short',
                'trade_type',
                'token_mint',
                'token_mint_short',
                'amount_sol',
                'amount_usd',
                'executor_used',
                'execution_status',
                'failure_reason',
                'transaction_signature',
                'solscan_link',
                'detection_method',
                'detected_dex',
                'slippage_used',
                'execution_time_ms',
                'pre_sol_balance',
                'post_sol_balance',
                'sol_balance_change',
                'token_balance_before',
                'token_balance_after',
                'token_balance_change',
                'trade_count_for_token',
                'portfolio_position_count',
                'notes'
            ]
            
            with open(self.csv_filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                
            logger.info(f"✅ Created CSV log file: {self.csv_filepath}")
    
    def log_trade_attempt(self, 
                         source_wallet: str,
                         trade_type: str,
                         token_mint: str,
                         amount_sol: float,
                         detected_dex: str = "Unknown",
                         detection_method: str = "websocket",
                         notes: str = "") -> str:
        """Log a trade attempt (before execution) and return a record ID"""
        
        now = datetime.now()
        record_id = f"{source_wallet[:8]}_{token_mint[:8]}_{now.strftime('%H%M%S')}"
        
        record = CopyTradeRecord(
            timestamp=now.isoformat(),
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            source_wallet=source_wallet,
            source_wallet_short=source_wallet[:8] + "..." if len(source_wallet) > 8 else source_wallet,
            trade_type=trade_type,
            token_mint=token_mint,
            token_mint_short=token_mint[:8] + "..." if len(token_mint) > 8 else token_mint,
            amount_sol=amount_sol,
            amount_usd=None,  # Will be updated if available
            executor_used="PENDING",
            execution_status="ATTEMPTING",
            failure_reason=None,
            transaction_signature=None,
            solscan_link=None,
            detection_method=detection_method,
            detected_dex=detected_dex,
            slippage_used=0.05,  # Default 5%
            execution_time_ms=None,
            pre_sol_balance=0.0,
            post_sol_balance=0.0,
            sol_balance_change=0.0,
            token_balance_before=0.0,
            token_balance_after=0.0,
            token_balance_change=0.0,
            trade_count_for_token=1,
            portfolio_position_count=0,
            notes=notes
        )
        
        self._write_record_to_csv(record)
        logger.info(f"📝 Logged trade attempt: {record_id}")
        return record_id
    
    def log_trade_success(self,
                         source_wallet: str,
                         trade_type: str,
                         token_mint: str,
                         amount_sol: float,
                         executor_used: str,
                         transaction_signature: str,
                         pre_balances: Dict[str, float],
                         post_balances: Dict[str, float],
                         slippage_used: float = 0.05,
                         execution_time_ms: int = None,
                         detected_dex: str = "Unknown",
                         detection_method: str = "websocket",
                         trade_count_for_token: int = 1,
                         portfolio_position_count: int = 0,
                         notes: str = ""):
        """Log a successful trade"""
        
        now = datetime.now()
        
        # Calculate balance changes
        pre_sol = pre_balances.get("SOL", 0.0)
        post_sol = post_balances.get("SOL", 0.0)
        sol_change = post_sol - pre_sol
        
        token_before = pre_balances.get(token_mint, 0.0)
        token_after = post_balances.get(token_mint, 0.0)
        token_change = token_after - token_before
        
        # Create Solscan link
        solscan_link = f"https://solscan.io/tx/{transaction_signature}" if transaction_signature else None
        
        record = CopyTradeRecord(
            timestamp=now.isoformat(),
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            source_wallet=source_wallet,
            source_wallet_short=source_wallet[:8] + "..." if len(source_wallet) > 8 else source_wallet,
            trade_type=trade_type,
            token_mint=token_mint,
            token_mint_short=token_mint[:8] + "..." if len(token_mint) > 8 else token_mint,
            amount_sol=amount_sol,
            amount_usd=None,  # Could be calculated if we have SOL price
            executor_used=executor_used,
            execution_status="SUCCESS",
            failure_reason=None,
            transaction_signature=transaction_signature,
            solscan_link=solscan_link,
            detection_method=detection_method,
            detected_dex=detected_dex,
            slippage_used=slippage_used,
            execution_time_ms=execution_time_ms,
            pre_sol_balance=pre_sol,
            post_sol_balance=post_sol,
            sol_balance_change=sol_change,
            token_balance_before=token_before,
            token_balance_after=token_after,
            token_balance_change=token_change,
            trade_count_for_token=trade_count_for_token,
            portfolio_position_count=portfolio_position_count,
            notes=notes
        )
        
        self._write_record_to_csv(record)
        logger.info(f"📝 ✅ Logged successful {trade_type}: {executor_used} for {token_mint[:8]}...")
    
    def log_trade_failure(self,
                         source_wallet: str,
                         trade_type: str,
                         token_mint: str,
                         amount_sol: float,
                         executor_attempted: str,
                         failure_reason: str,
                         slippage_used: float = 0.05,
                         execution_time_ms: int = None,
                         detected_dex: str = "Unknown",
                         detection_method: str = "websocket",
                         trade_count_for_token: int = 1,
                         portfolio_position_count: int = 0,
                         notes: str = ""):
        """Log a failed trade"""
        
        now = datetime.now()
        
        record = CopyTradeRecord(
            timestamp=now.isoformat(),
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            source_wallet=source_wallet,
            source_wallet_short=source_wallet[:8] + "..." if len(source_wallet) > 8 else source_wallet,
            trade_type=trade_type,
            token_mint=token_mint,
            token_mint_short=token_mint[:8] + "..." if len(token_mint) > 8 else token_mint,
            amount_sol=amount_sol,
            amount_usd=None,
            executor_used=executor_attempted,
            execution_status="FAILED",
            failure_reason=failure_reason,
            transaction_signature=None,
            solscan_link=None,
            detection_method=detection_method,
            detected_dex=detected_dex,
            slippage_used=slippage_used,
            execution_time_ms=execution_time_ms,
            pre_sol_balance=0.0,
            post_sol_balance=0.0,
            sol_balance_change=0.0,
            token_balance_before=0.0,
            token_balance_after=0.0,
            token_balance_change=0.0,
            trade_count_for_token=trade_count_for_token,
            portfolio_position_count=portfolio_position_count,
            notes=notes
        )
        
        self._write_record_to_csv(record)
        logger.info(f"📝 ❌ Logged failed {trade_type}: {executor_attempted} for {token_mint[:8]}... - {failure_reason}")
    
    def log_multiple_executor_failure(self,
                                     source_wallet: str,
                                     trade_type: str,
                                     token_mint: str,
                                     amount_sol: float,
                                     failed_executors: Dict[str, str],  # executor -> error
                                     detected_dex: str = "Unknown",
                                     detection_method: str = "websocket",
                                     trade_count_for_token: int = 1,
                                     portfolio_position_count: int = 0,
                                     notes: str = ""):
        """Log when all executors failed"""
        
        # Create a summary of all failures
        failure_summary = "; ".join([f"{executor}: {error[:50]}..." for executor, error in failed_executors.items()])
        executor_list = ", ".join(failed_executors.keys())
        
        self.log_trade_failure(
            source_wallet=source_wallet,
            trade_type=trade_type,
            token_mint=token_mint,
            amount_sol=amount_sol,
            executor_attempted=f"ALL_FAILED: {executor_list}",
            failure_reason=f"All executors failed: {failure_summary}",
            detected_dex=detected_dex,
            detection_method=detection_method,
            trade_count_for_token=trade_count_for_token,
            portfolio_position_count=portfolio_position_count,
            notes=notes
        )
    
    def _write_record_to_csv(self, record: CopyTradeRecord):
        """Write a record to the CSV file"""
        try:
            with open(self.csv_filepath, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Convert dataclass to list of values
                record_dict = asdict(record)
                values = [record_dict[field] for field in record_dict.keys()]
                writer.writerow(values)
        except Exception as e:
            logger.error(f"❌ Error writing to CSV: {e}")
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Get daily trading summary"""
        try:
            if not os.path.exists(self.csv_filepath):
                return {"error": "No trades logged today"}
            
            summary = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "total_trades": 0,
                "successful_trades": 0,
                "failed_trades": 0,
                "buy_trades": 0,
                "sell_trades": 0,
                "executors_used": {},
                "failure_reasons": {},
                "top_tokens": {},
                "total_sol_spent": 0.0,
                "total_sol_gained": 0.0,
                "net_sol_change": 0.0
            }
            
            with open(self.csv_filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    summary["total_trades"] += 1
                    
                    # Count success/failure
                    if row["execution_status"] == "SUCCESS":
                        summary["successful_trades"] += 1
                        
                        # Track SOL changes
                        sol_change = float(row["sol_balance_change"] or 0)
                        if sol_change < 0:
                            summary["total_sol_spent"] += abs(sol_change)
                        else:
                            summary["total_sol_gained"] += sol_change
                        summary["net_sol_change"] += sol_change
                        
                    else:
                        summary["failed_trades"] += 1
                    
                    # Count trade types
                    if row["trade_type"] == "buy":
                        summary["buy_trades"] += 1
                    elif row["trade_type"] == "sell":
                        summary["sell_trades"] += 1
                    
                    # Count executors
                    executor = row["executor_used"]
                    summary["executors_used"][executor] = summary["executors_used"].get(executor, 0) + 1
                    
                    # Count failure reasons
                    if row["failure_reason"]:
                        reason = row["failure_reason"][:50]  # Truncate long reasons
                        summary["failure_reasons"][reason] = summary["failure_reasons"].get(reason, 0) + 1
                    
                    # Count tokens
                    token = row["token_mint_short"]
                    summary["top_tokens"][token] = summary["top_tokens"].get(token, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating daily summary: {e}")
            return {"error": str(e)}
    
    def print_daily_summary(self):
        """Print a formatted daily summary"""
        summary = self.get_daily_summary()
        
        if "error" in summary:
            print(f"❌ Summary error: {summary['error']}")
            return
        
        print(f"\n📊 COPY TRADING DAILY SUMMARY - {summary['date']}")
        print("=" * 60)
        print(f"📈 Total Trades: {summary['total_trades']}")
        print(f"✅ Successful: {summary['successful_trades']}")
        print(f"❌ Failed: {summary['failed_trades']}")
        print(f"📊 Success Rate: {(summary['successful_trades'] / max(1, summary['total_trades'])) * 100:.1f}%")
        print()
        print(f"🟢 Buy Trades: {summary['buy_trades']}")
        print(f"🔴 Sell Trades: {summary['sell_trades']}")
        print()
        print(f"💰 Total SOL Spent: {summary['total_sol_spent']:.6f}")
        print(f"💵 Total SOL Gained: {summary['total_sol_gained']:.6f}")
        print(f"📊 Net SOL Change: {summary['net_sol_change']:+.6f}")
        print()
        
        if summary["executors_used"]:
            print("🔧 Executors Used:")
            for executor, count in sorted(summary["executors_used"].items(), key=lambda x: x[1], reverse=True):
                print(f"   {executor}: {count} trades")
        
        if summary["failure_reasons"]:
            print("\n❌ Top Failure Reasons:")
            for reason, count in sorted(summary["failure_reasons"].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {reason}: {count} times")
        
        if summary["top_tokens"]:
            print("\n🎯 Most Traded Tokens:")
            for token, count in sorted(summary["top_tokens"].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {token}: {count} trades")
        
        print(f"\n💾 Full log: {self.csv_filepath}")
        print("=" * 60)

# Global logger instance
copy_trade_logger = None

def get_copy_trade_logger(log_directory: str = None) -> CopyTradeCSVLogger:
    """Get or create the global copy trade logger"""
    global copy_trade_logger
    if copy_trade_logger is None:
        copy_trade_logger = CopyTradeCSVLogger(log_directory)
    return copy_trade_logger

def log_successful_copy_trade(source_wallet: str, trade_type: str, token_mint: str, 
                             amount_sol: float, executor_used: str, transaction_signature: str,
                             pre_balances: Dict[str, float], post_balances: Dict[str, float],
                             **kwargs):
    """Convenience function to log successful trades"""
    logger_instance = get_copy_trade_logger()
    logger_instance.log_trade_success(
        source_wallet=source_wallet,
        trade_type=trade_type,
        token_mint=token_mint,
        amount_sol=amount_sol,
        executor_used=executor_used,
        transaction_signature=transaction_signature,
        pre_balances=pre_balances,
        post_balances=post_balances,
        **kwargs
    )

def log_failed_copy_trade(source_wallet: str, trade_type: str, token_mint: str,
                         amount_sol: float, executor_attempted: str, failure_reason: str,
                         **kwargs):
    """Convenience function to log failed trades"""
    logger_instance = get_copy_trade_logger()
    logger_instance.log_trade_failure(
        source_wallet=source_wallet,
        trade_type=trade_type,
        token_mint=token_mint,
        amount_sol=amount_sol,
        executor_attempted=executor_attempted,
        failure_reason=failure_reason,
        **kwargs
    )

if __name__ == "__main__":
    # Test the logger
    test_logger = CopyTradeCSVLogger("test_logs")
    
    # Test logging a successful trade
    test_logger.log_trade_success(
        source_wallet="suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        trade_type="buy",
        token_mint="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        amount_sol=0.1,
        executor_used="orca",
        transaction_signature="test123456789",
        pre_balances={"SOL": 1.0, "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU": 0.0},
        post_balances={"SOL": 0.9, "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU": 1000.0},
        detected_dex="Orca Whirlpool",
        notes="Test successful trade"
    )
    
    # Test logging a failed trade
    test_logger.log_trade_failure(
        source_wallet="suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        trade_type="buy",
        token_mint="8xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        amount_sol=0.1,
        executor_attempted="jupiter",
        failure_reason="Slippage tolerance exceeded",
        detected_dex="Jupiter V6",
        notes="Test failed trade"
    )
    
    # Print summary
    test_logger.print_daily_summary()
