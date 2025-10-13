#!/usr/bin/env python3
"""
Test script to demonstrate CSV logging functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from copy_trade_logger import CopyTradeCSVLogger

async def test_csv_logging():
    """Test the CSV logging system"""
    print("🧪 Testing Copy Trading CSV Logger")
    print("=" * 50)
    
    # Initialize logger
    logger = CopyTradeCSVLogger("test_copy_trade_logs")
    print(f"✅ CSV Logger initialized")
    print(f"📁 Log directory: test_copy_trade_logs/")
    print(f"📄 Log file: {logger.csv_filename}")
    print()
    
    # Test successful buy trade
    print("📝 Testing successful BUY trade logging...")
    logger.log_trade_success(
        source_wallet="suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        trade_type="buy",
        token_mint="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        amount_sol=0.1,
        executor_used="orca",
        transaction_signature="5J8n1XNQK7gGEagjKr9rw9QnrRjb6YGQUzMH3K8T4W9X",
        pre_balances={"SOL": 1.0, "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU": 0.0},
        post_balances={"SOL": 0.895, "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU": 1000000.0},
        detected_dex="Orca Whirlpool",
        slippage_used=0.05,
        execution_time_ms=1250,
        trade_count_for_token=1,
        portfolio_position_count=1,
        notes="First buy of this token - copy trading success!"
    )
    
    # Test successful sell trade
    print("📝 Testing successful SELL trade logging...")
    logger.log_trade_success(
        source_wallet="suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        trade_type="sell",
        token_mint="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        amount_sol=0.1,
        executor_used="phoenix",
        transaction_signature="3H7m9XNQK7gGEagjKr9rw9QnrRjb6YGQUzMH3K8T4W9Y",
        pre_balances={"SOL": 0.895, "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU": 1000000.0},
        post_balances={"SOL": 1.15, "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU": 0.0},
        detected_dex="Phoenix",
        slippage_used=0.10,
        execution_time_ms=890,
        trade_count_for_token=1,
        portfolio_position_count=0,
        notes="Sell all following target wallet - profit taken!"
    )
    
    # Test failed single executor
    print("📝 Testing FAILED single executor trade...")
    logger.log_trade_failure(
        source_wallet="DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        trade_type="buy",
        token_mint="8pKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsV",
        amount_sol=0.1,
        executor_attempted="jupiter",
        failure_reason="Slippage tolerance exceeded (0x1771)",
        detected_dex="Jupiter V6",
        slippage_used=0.05,
        execution_time_ms=750,
        trade_count_for_token=1,
        portfolio_position_count=1,
        notes="Target wallet bought but we failed on first executor"
    )
    
    # Test multiple executor failures
    print("📝 Testing MULTIPLE executor failures...")
    failed_executors = {
        "jupiter": "No routes found for this token",
        "orca": "Slippage tolerance exceeded",
        "phoenix": "Insufficient liquidity",
        "raydium": "Token account not found",
        "pumpfun": "Bonding curve graduated - use DEX instead"
    }
    logger.log_multiple_executor_failure(
        source_wallet="DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        trade_type="buy",
        token_mint="9qKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsW",
        amount_sol=0.1,
        failed_executors=failed_executors,
        detected_dex="Unknown",
        trade_count_for_token=2,
        portfolio_position_count=1,
        notes="All executors failed - token may be untradeable"
    )
    
    # Test another successful trade for variety
    print("📝 Testing another successful trade with different executor...")
    logger.log_trade_success(
        source_wallet="DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        trade_type="buy",
        token_mint="ApKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsX",
        amount_sol=0.15,
        executor_used="direct_pumpfun",
        transaction_signature="6L9p2XNQK7gGEagjKr9rw9QnrRjb6YGQUzMH3K8T4W9Z",
        pre_balances={"SOL": 1.0},
        post_balances={"SOL": 0.845, "ApKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsX": 50000000.0},
        detected_dex="Pump.fun",
        slippage_used=0.15,
        execution_time_ms=2100,
        trade_count_for_token=1,
        portfolio_position_count=2,
        notes="Direct Pump.fun trade - bonding curve purchase"
    )
    
    print()
    print("✅ All test trades logged successfully!")
    print()
    
    # Show summary
    print("📊 Generated Trading Summary:")
    print("=" * 50)
    logger.print_daily_summary()
    
    print()
    print("🎉 CSV Logging Test Complete!")
    print(f"📁 Check the file: {logger.csv_filepath}")
    print("💡 You can open this CSV file in Excel or Google Sheets!")

if __name__ == "__main__":
    asyncio.run(test_csv_logging())
