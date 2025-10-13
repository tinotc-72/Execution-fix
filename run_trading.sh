#!/bin/bash

echo "🚀 Running Raydium CPMM Trading Script"
echo "======================================"

# Check if the script exists
if [ ! -f "1_raydium_cpmm_trade_cycle_fixed_v2.py" ]; then
    echo "❌ Script file not found!"
    exit 1
fi

# Run the script with output capture
echo "Starting trading script..."
python 1_raydium_cpmm_trade_cycle_fixed_v2.py 2>&1 | tee trading_output.log

echo "Script execution completed. Check trading_output.log for details."
