#!/bin/bash

# Script to run the trading bot and capture output
echo "Starting Raydium CPMM Trading Bot..."
echo "Working directory: $(pwd)"
echo "Python executable: ./hopeII/bin/python"
echo "Script: 1_raydium_cpmm_trade_cycle_fixed_v2.py"
echo "=" * 50

# Run the script and capture both stdout and stderr
./hopeII/bin/python 1_raydium_cpmm_trade_cycle_fixed_v2.py 2>&1

echo ""
echo "Script execution completed."
echo "Exit code: $?"
