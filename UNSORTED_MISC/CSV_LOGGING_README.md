# Copy Trading CSV Logger Documentation

## Overview

The Copy Trading CSV Logger provides comprehensive tracking of all your copy trading activities, including successful trades, failed attempts, which executors were used, transaction signatures, and detailed performance metrics.

## Features

✅ **Complete Trade Tracking**: Every buy/sell attempt is logged  
✅ **Executor Performance**: Track which DEX executors work best  
✅ **Failure Analysis**: Detailed reasons why trades failed  
✅ **Balance Tracking**: SOL and token balance changes  
✅ **Performance Metrics**: Success rates, profit/loss tracking  
✅ **Source Wallet Tracking**: Know which target wallet triggered each trade  
✅ **Transaction Links**: Direct Solscan links for verification  

## CSV File Columns

| Column | Description |
|--------|-------------|
| `timestamp` | Full timestamp of trade |
| `date` | Trade date (YYYY-MM-DD) |
| `time` | Trade time (HH:MM:SS) |
| `source_wallet` | Full target wallet address that triggered the trade |
| `source_wallet_short` | Shortened wallet address for readability |
| `trade_type` | 'buy' or 'sell' |
| `token_mint` | Full token mint address |
| `token_mint_short` | Shortened token address for readability |
| `amount_sol` | SOL amount involved in trade |
| `amount_usd` | USD value (if available) |
| `executor_used` | Which DEX executor was used (orca, jupiter, etc.) |
| `execution_status` | 'SUCCESS', 'FAILED', or 'ATTEMPTING' |
| `failure_reason` | Detailed error message for failed trades |
| `transaction_signature` | Solana transaction signature |
| `solscan_link` | Direct link to view transaction on Solscan |
| `detection_method` | How trade was detected (websocket, polling, etc.) |
| `detected_dex` | Original DEX detected from target wallet |
| `slippage_used` | Slippage tolerance used for the trade |
| `execution_time_ms` | How long the trade took in milliseconds |
| `pre_sol_balance` | SOL balance before trade |
| `post_sol_balance` | SOL balance after trade |
| `sol_balance_change` | Net SOL change from trade |
| `token_balance_before` | Token balance before trade |
| `token_balance_after` | Token balance after trade |
| `token_balance_change` | Net token change from trade |
| `trade_count_for_token` | How many times this token has been traded |
| `portfolio_position_count` | Total positions after trade |
| `notes` | Additional context and details |

## File Location

CSV files are automatically created in the `copy_trade_logs/` directory with the naming pattern:
```
copy_trades_YYYYMMDD.csv
```

Example: `copy_trades_20250721.csv`

## Daily Summary Features

The logger provides automated daily summaries including:

- **Trade Statistics**: Total trades, success rate, buy/sell counts
- **Financial Summary**: SOL spent, SOL gained, net profit/loss
- **Executor Performance**: Which executors work best
- **Failure Analysis**: Most common failure reasons
- **Token Activity**: Most actively traded tokens

## Integration with Your Bot

The CSV logger is automatically integrated into your copy trading bot:

### Successful Trades
```python
# Automatically logged when trades succeed
self.csv_logger.log_trade_success(
    source_wallet=source_wallet,
    trade_type='buy',
    token_mint=token_mint,
    amount_sol=self.config.investment_amount_sol,
    executor_used=success.get('executor', 'unknown'),
    transaction_signature=success['signature'],
    pre_balances=pre_balances,
    post_balances=post_balances,
    # ... additional parameters
)
```

### Failed Trades
```python
# Automatically logged when trades fail
self.csv_logger.log_trade_failure(
    source_wallet=source_wallet,
    trade_type='buy',
    token_mint=token_mint,
    amount_sol=self.config.investment_amount_sol,
    executor_attempted='jupiter',
    failure_reason='Slippage tolerance exceeded',
    # ... additional parameters
)
```

### Multiple Executor Failures
```python
# Logged when ALL executors fail
self.csv_logger.log_multiple_executor_failure(
    source_wallet=source_wallet,
    trade_type='buy',
    token_mint=token_mint,
    amount_sol=self.config.investment_amount_sol,
    failed_executors={
        'jupiter': 'No routes found',
        'orca': 'Slippage exceeded',
        'raydium': 'Token not found'
    }
)
```

## Viewing Your Data

### Terminal Summary
The bot automatically shows daily summaries when stopped:
```python
await bot.show_trading_summary()  # Manual summary
# Summary is shown automatically when bot stops
```

### Excel/Google Sheets
Open the CSV file directly in Excel or Google Sheets for advanced analysis:
1. Navigate to `copy_trade_logs/`
2. Open `copy_trades_YYYYMMDD.csv`
3. Use pivot tables, charts, and filters for detailed analysis

### Example Analysis Queries

**Most Successful Executor:**
```
Filter by execution_status = "SUCCESS"
Count by executor_used
```

**Profit/Loss by Token:**
```
Group by token_mint_short
Sum sol_balance_change
```

**Average Trade Size:**
```
Filter by trade_type = "buy"
Average of amount_sol
```

**Success Rate by DEX:**
```
Pivot table: 
Rows = detected_dex
Values = Count of execution_status
Filter by SUCCESS vs FAILED
```

## Best Practices

### 📊 Daily Review
- Check the daily summary each evening
- Identify patterns in successful/failed trades
- Adjust executor priorities based on performance

### 🔍 Failure Analysis
- Review failure reasons regularly
- Update slippage settings if needed
- Identify problematic tokens or market conditions

### 💰 Performance Tracking
- Monitor net SOL changes
- Calculate ROI by comparing pre/post balances
- Track which target wallets perform best

### 📈 Optimization
- Disable poorly performing executors
- Adjust trade sizes based on success rates
- Fine-tune detection parameters

## Example Daily Summary Output

```
📊 COPY TRADING DAILY SUMMARY - 2025-07-21
============================================================
📈 Total Trades: 25
✅ Successful: 18
❌ Failed: 7
📊 Success Rate: 72.0%

🟢 Buy Trades: 20
🔴 Sell Trades: 5

💰 Total SOL Spent: 2.500000
💵 Total SOL Gained: 3.150000
📊 Net SOL Change: +0.650000

🔧 Executors Used:
   orca: 8 trades
   phoenix: 6 trades
   direct_pumpfun: 4 trades
   jupiter: 3 trades
   ALL_FAILED: raydium, cpmm: 2 trades

❌ Top Failure Reasons:
   Slippage tolerance exceeded (0x1771): 3 times
   No routes found for this token: 2 times
   Token account not found: 2 times

🎯 Most Traded Tokens:
   7xKXtg2C...: 5 trades
   ApKXtg2C...: 3 trades
   9qKXtg2C...: 2 trades

💾 Full log: copy_trade_logs/copy_trades_20250721.csv
============================================================
```

## Troubleshooting

### CSV File Not Created
- Check that `copy_trade_logs/` directory exists
- Verify write permissions
- Check for disk space

### Missing Data
- Ensure bot integration is complete
- Verify CSV logger initialization
- Check for exceptions in logs

### Performance Impact
- CSV logging is lightweight and asynchronous
- Files are appended efficiently
- Old files can be archived/deleted as needed

## Advanced Features

### Custom Analysis
Export CSV data to:
- Python pandas for data analysis
- Jupyter notebooks for visualization
- Trading dashboards and monitoring tools

### Integration with Other Tools
- Import into portfolio trackers
- Export to tax reporting software
- Feed into automated alert systems

---

**Happy Trading! 🚀**

The CSV logger gives you complete visibility into your copy trading performance. Use this data to continuously improve your strategy and maximize profits while minimizing risks.
