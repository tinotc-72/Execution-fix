#!/usr/bin/env python3
"""
Copy Trade Logger - Simple CSV logging for copy trading activities
"""

import csv
import logging
import os
from datetime import datetime
from typing import Dict, Any

def get_copy_trade_logger(name: str):
    """
    Get a copy trade logger for CSV logging
    """
    logger = logging.getLogger(f"copy_trade_{name}")
    return logger

def log_successful_copy_trade(trade_data: Dict[str, Any]):
    """Log successful copy trade to CSV"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # CSV file path
        csv_file = f"logs/successful_trades_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Check if file exists to write header
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='') as f:
            fieldnames = ['timestamp', 'action', 'token_mint', 'signature', 'method', 'dex']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'action': trade_data.get('action', 'unknown'),
                'token_mint': trade_data.get('token_mint', 'unknown'),
                'signature': trade_data.get('signature', 'unknown'),
                'method': trade_data.get('method', 'unknown'),
                'dex': trade_data.get('dex', 'unknown')
            })
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to log successful trade: {e}")

def log_failed_copy_trade(wallet: str, action: str, token_mint: str, amount: float, executor: str, error: str):
    """Log failed copy trade to CSV"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # CSV file path
        csv_file = f"logs/failed_trades_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Check if file exists to write header
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='') as f:
            fieldnames = ['timestamp', 'wallet', 'action', 'token_mint', 'amount', 'executor', 'error']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'wallet': wallet,
                'action': action,
                'token_mint': token_mint,
                'amount': amount,
                'executor': executor,
                'error': error
            })
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to log failed trade: {e}")
