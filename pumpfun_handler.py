#!/usr/bin/env python3
"""
Pump.fun Token Handler - Special handling for Pump.fun tokens
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from solders.pubkey import Pubkey

logger = logging.getLogger(__name__)

class PumpFunHandler:
    """Handle Pump.fun specific tokens"""
    
    # Known Pump.fun program IDs
    PUMP_FUN_PROGRAMS = [
        "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",
        "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",
        "5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump"
    ]
    
    @classmethod
    def is_likely_pumpfun_token(cls, token_mint: str, transaction_accounts: list = None) -> bool:
        """Check if a token is likely from Pump.fun"""
        try:
            # Check if any Pump.fun program IDs are in the transaction
            if transaction_accounts:
                account_strs = [str(acc) for acc in transaction_accounts]
                for program_id in cls.PUMP_FUN_PROGRAMS:
                    if program_id in account_strs:
                        logger.info(f"🚀 Pump.fun program detected: {program_id}")
                        return True
            
            # Additional heuristics for Pump.fun tokens
            # These tokens often have specific patterns or characteristics
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking Pump.fun token: {e}")
            return False
    
    @classmethod
    def should_skip_untradable_token(cls, token_mint: str, error_message: str = "") -> bool:
        """Decide if we should skip a token that appears untradable"""
        
        # For copy trading, be very aggressive - only skip if clearly invalid
        if "TOKEN_NOT_TRADABLE" in error_message:
            logger.warning(f"⚠️ Token {token_mint} marked as not tradable by Jupiter")
            
            # For copy trading new meme tokens, Jupiter often doesn't have liquidity yet
            # This is EXACTLY what we want to trade early!
            logger.info(f"💎 This might be a new meme token - perfect for early entry!")
            logger.info(f"🚀 Continuing with Pump.fun and other DEX attempts...")
            return False  # Don't skip - keep trying other DEXes
        
        # Only skip on clear format errors or system issues
        if any(phrase in error_message.lower() for phrase in [
            "invalid", "malformed", "system error", "network error"
        ]):
            return True
        
        return False  # Default: don't skip, keep trying
    
    @classmethod 
    def get_fallback_strategy(cls, token_mint: str) -> str:
        """Get fallback trading strategy for problematic tokens"""
        
        # For tokens that fail on all DEXes, we could:
        # 1. Wait and retry later
        # 2. Try direct Pump.fun interaction
        # 3. Skip entirely
        
        return "skip"  # Conservative approach
