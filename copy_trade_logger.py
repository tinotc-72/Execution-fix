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

def log_failed_copy_trade(wallet: str, action: str, token_mint: str, amount: float, executor: str, error: str, **kwargs):
    """
    Log failed copy trade to CSV with enhanced debugging information
    
    Args:
        wallet: Source wallet address
        action: Trade action (buy/sell/swap)
        token_mint: Token mint address
        amount: Trade amount
        executor: Executor that failed
        error: Error message
        **kwargs: Additional fields to log (signature, dex, missing_fields, etc.)
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # CSV file path
        csv_file = f"logs/failed_trades_{datetime.now().strftime('%Y%m%d')}.csv"
        
        # Check if file exists to write header
        file_exists = os.path.exists(csv_file)
        
        # Enhanced fieldnames with additional debugging info
        fieldnames = [
            'timestamp', 'wallet', 'action', 'token_mint', 'amount', 
            'executor', 'error', 'signature', 'dex', 'missing_fields', 
            'failure_reason', 'additional_info'
        ]
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            # Build row with all available information
            row = {
                'timestamp': datetime.now().isoformat(),
                'wallet': wallet or 'unknown',
                'action': action or 'unknown',
                'token_mint': token_mint or 'unknown',
                'amount': amount if amount is not None else 0.0,
                'executor': executor or 'unknown',
                'error': error or 'unknown error',
                'signature': kwargs.get('signature', 'N/A'),
                'dex': kwargs.get('dex', 'unknown'),
                'missing_fields': kwargs.get('missing_fields', ''),
                'failure_reason': kwargs.get('failure_reason', 'execution_error'),
                'additional_info': str(kwargs.get('additional_info', ''))
            }
            
            writer.writerow(row)
            
        # Also log to console for immediate visibility
        logger = logging.getLogger(__name__)
        logger.error(f"❌ FAILED TRADE LOGGED:")
        logger.error(f"   Wallet: {wallet[:8] if wallet else 'unknown'}...")
        logger.error(f"   Action: {action}")
        logger.error(f"   Token: {token_mint[:8] if token_mint else 'unknown'}...")
        logger.error(f"   Error: {error}")
        if kwargs.get('missing_fields'):
            logger.error(f"   Missing Fields: {kwargs['missing_fields']}")
            
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to log failed trade: {e}")
        logging.getLogger(__name__).error(f"  Original error was: {error}")
