# Automatic Position Liquidation Feature

This feature automatically sells all your remaining positions when you stop the copy trading bot. This ensures you don't hold positions that the copied wallet may have already sold.

## How It Works

### 1. Automatic Liquidation on Shutdown
When you stop the bot (Ctrl+C or any shutdown), it will:
- ✅ Detect all current positions in your tracking system
- ✅ Attempt to sell each position using all available DEX executors
- ✅ Provide detailed liquidation reports
- ✅ Show SOL recovered from sales
- ✅ Handle partial failures gracefully

### 2. Graceful Shutdown Process
1. **Signal Detection**: Bot detects shutdown signal (Ctrl+C, SIGTERM)
2. **Position Scanning**: Identifies all tracked positions
3. **Sequential Liquidation**: Sells each position one by one
4. **Balance Recovery**: Calculates total SOL recovered
5. **Final Report**: Shows liquidation success/failure summary

### 3. Safety Features
- **Non-blocking**: Failed sales won't prevent other liquidations
- **Detailed Logging**: Every liquidation attempt is logged
- **Error Handling**: Graceful handling of network/DEX issues
- **Manual Override**: Emergency liquidation function available

## Usage Examples

### Normal Operation
```bash
# Start the bot normally
python main.py

# When you want to stop (Ctrl+C), positions will be automatically liquidated
```

### Manual Position Check
```bash
# Check what positions you currently hold
python test_liquidation.py --check
```

### Emergency Liquidation
```bash
# Force liquidate all positions immediately (be careful!)
python test_liquidation.py --emergency
```

### Test Simulation
```bash
# Test the liquidation logic safely (no real trades)
python test_liquidation.py --simulate
```

## Expected Output

### During Normal Shutdown:
```
🛑 Stopping copy trading bot...
💸 EMERGENCY LIQUIDATION: Selling all 3 remaining positions
🔄 This ensures no positions are left behind when copied wallet may have already sold

💸 Liquidating position: EPjFWdd5... (0.001000 SOL invested)
✅ Successfully liquidated EPjFWdd5...
   🔗 Transaction: https://solscan.io/tx/[signature]

📊 LIQUIDATION SUMMARY:
   ✅ Successful sales: 3
   ❌ Failed sales: 0
   💰 SOL recovered: +0.00283 SOL
   🏦 Final SOL balance: 0.045230 SOL
   📍 Remaining positions: 0
```

### If Some Sales Fail:
```
📊 LIQUIDATION SUMMARY:
   ✅ Successful sales: 2
   ❌ Failed sales: 1
   💰 SOL recovered: +0.00180 SOL
   📍 Remaining positions: 1

⚠️ 1 positions failed to liquidate - may require manual intervention
   🔴 7vfCXTUX...: Token not tradable on available DEXes
```

## Configuration

The liquidation feature uses the same DEX executors as your main bot:

```python
# In main.py - CopyTradeConfig
enable_dexes={
    "orca": True,           # Prioritized for liquidation
    "phoenix": True,        # Good backup option
    "raydium": True,        # Reliable DEX
    "jupiter": True,        # Comprehensive routing
    "cpmm": True,          # Alternative Raydium
    "clmm": True,          # Concentrated liquidity
    "pumpfun": True,       # For Pump.fun tokens
    "direct_pumpfun": True # Direct Pump.fun access
}
```

## Benefits

1. **Never Miss Exits**: Automatically sell when you stop the bot
2. **Risk Management**: Prevents holding positions after copied wallet exits
3. **Peace of Mind**: Know that positions will be closed when you're away
4. **Comprehensive Coverage**: Uses all available DEXes for maximum success
5. **Detailed Tracking**: Full liquidation reports for transparency

## Technical Details

### Liquidation Process:
1. **Position Discovery**: Scans `self.positions` dictionary
2. **Balance Verification**: Checks actual wallet token balances
3. **Sequential Execution**: Processes each position individually
4. **DEX Fallback**: Tries multiple DEXes if one fails
5. **Result Tracking**: Records success/failure for each position

### Error Scenarios Handled:
- Network connectivity issues
- DEX unavailability
- Token liquidity problems
- Rate limiting
- Insufficient gas/fees

### Integration Points:
- **Signal Handlers**: Catches Ctrl+C and SIGTERM
- **Bot Lifecycle**: Integrated into `stop()` method
- **DEX Executors**: Uses existing trading infrastructure
- **Logging System**: Full integration with bot logging

## Tips

1. **Test First**: Use `--simulate` mode to test liquidation logic
2. **Monitor Output**: Watch for failed liquidations that need manual intervention
3. **Multiple DEXes**: Enable multiple DEXes for better liquidation success
4. **Emergency Use**: Use `--emergency` flag only when necessary
5. **Regular Checks**: Use `--check` to monitor position status

This feature ensures that your copy trading never leaves you holding positions that the target wallet has already exited!
