#!/usr/bin/env python3
"""
🎯 METEORA EXECUTOR CONFIGURATION
===============================

Configuration and constants for the Meteora Dynamic Bonding Curve MEV executor.
Based on reverse-engineered patterns from successful trading wallets.

Key Configuration:
- Program IDs and addresses
- Trading parameters and limits
- MEV protection settings
- Performance tuning parameters
"""

from solders.pubkey import Pubkey as PublicKey
from typing import Dict, Any

# Meteora Program IDs
METEORA_DYNAMIC_BONDING_CURVE = PublicKey.from_string("dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN")

# Standard Solana Programs
SYSTEM_PROGRAM = PublicKey.from_string("11111111111111111111111111111112")
TOKEN_PROGRAM = PublicKey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM = PublicKey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# Raydium Program IDs (for reference)
RAYDIUM_LIQUIDITY_POOL_V4 = PublicKey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")

# Native SOL
NATIVE_SOL = PublicKey.from_string("So11111111111111111111111111111111111111112")

# Program Collections
METEORA_PROGRAMS = {
    "DYNAMIC_BONDING_CURVE": METEORA_DYNAMIC_BONDING_CURVE
}

SOLANA_PROGRAMS = {
    "SYSTEM": SYSTEM_PROGRAM,
    "TOKEN": TOKEN_PROGRAM,
    "ASSOCIATED_TOKEN": ASSOCIATED_TOKEN_PROGRAM
}

# Trading Configuration
TRADING_CONFIG = {
    # Default trading parameters
    "DEFAULT_SLIPPAGE_PERCENT": 1.0,
    "DEFAULT_PRIORITY_FEE": 50000,  # microlamports
    "MAX_PRIORITY_FEE": 500000,  # microlamports
    
    # MEV Protection
    "USE_JITO_BY_DEFAULT": True,
    "JITO_TIP_AMOUNT": 10000,  # microlamports
    
    # Execution limits
    "MAX_SOL_PER_TRADE": 10.0,
    "MIN_SOL_PER_TRADE": 0.001,
    "MAX_RETRIES": 3,
    "CONFIRMATION_TIMEOUT": 30,  # seconds
    
    # Performance targets (based on analysis)
    "TARGET_SUCCESS_RATE": 95.0,  # percent
    "TARGET_EXECUTION_TIME": 5.0,  # seconds
}

# Pool Discovery Configuration
POOL_CONFIG = {
    # Pool derivation seeds
    "POOL_SEED": "pool",
    "DBC_SEED": "meteora_dbc",
    
    # Pool validation
    "MIN_SOL_RESERVES": 0.1,  # SOL
    "MIN_TOKEN_RESERVES": 1000,  # tokens
    "MAX_POOL_AGE": 3600,  # seconds (1 hour)
}

# Instruction Configuration
INSTRUCTION_CONFIG = {
    # Meteora DBC instruction types
    "BUY_INSTRUCTION": 0,
    "SELL_INSTRUCTION": 1,
    "CREATE_POOL_INSTRUCTION": 2,
    
    # Compute budget settings
    "COMPUTE_UNITS": 400000,
    "HEAP_SIZE": 32768,
}

# Error Handling Configuration
ERROR_CONFIG = {
    # Retryable errors
    "RETRYABLE_ERRORS": [
        "BlockhashNotFound",
        "TransactionExpired", 
        "NodeIsBehind",
        "SlotSkipped",
        "InsufficientFundsForRent",
    ],
    
    # Non-retryable errors
    "FATAL_ERRORS": [
        "InsufficientFunds",
        "InvalidInstruction",
        "InvalidAccountData",
        "ProgramFailedToComplete",
    ],
    
    # Retry configuration
    "RETRY_DELAY": 1.0,  # seconds
    "BACKOFF_MULTIPLIER": 1.5,
    "MAX_RETRY_DELAY": 10.0,  # seconds
}

# Monitoring Configuration
MONITORING_CONFIG = {
    # Performance monitoring
    "LOG_LEVEL": "INFO",
    "LOG_TRADES": True,
    "LOG_PERFORMANCE": True,
    
    # Metrics tracking
    "TRACK_GAS_USAGE": True,
    "TRACK_EXECUTION_TIME": True,
    "TRACK_SLIPPAGE": True,
    
    # Alerting thresholds
    "LOW_SUCCESS_RATE_THRESHOLD": 90.0,  # percent
    "HIGH_EXECUTION_TIME_THRESHOLD": 10.0,  # seconds
    "HIGH_SLIPPAGE_THRESHOLD": 5.0,  # percent
}

def get_meteora_config() -> Dict[str, Any]:
    """
    Get complete Meteora executor configuration.
    
    Returns:
        Complete configuration dictionary
    """
    return {
        "programs": METEORA_PROGRAMS,
        "solana_programs": SOLANA_PROGRAMS,
        "trading": TRADING_CONFIG,
        "pools": POOL_CONFIG,
        "instructions": INSTRUCTION_CONFIG,
        "errors": ERROR_CONFIG,
        "monitoring": MONITORING_CONFIG,
    }

def get_program_id(program_name: str) -> PublicKey:
    """
    Get program ID by name.
    
    Args:
        program_name: Name of the program
        
    Returns:
        PublicKey of the program
        
    Raises:
        KeyError: If program name not found
    """
    all_programs = {**METEORA_PROGRAMS, **SOLANA_PROGRAMS}
    
    if program_name not in all_programs:
        raise KeyError(f"Program '{program_name}' not found in configuration")
    
    return PublicKey(all_programs[program_name])

def validate_trade_params(amount_sol: float, slippage_percent: float) -> bool:
    """
    Validate trade parameters against configuration limits.
    
    Args:
        amount_sol: SOL amount to trade
        slippage_percent: Slippage percentage
        
    Returns:
        True if valid, False otherwise
    """
    if amount_sol < TRADING_CONFIG["MIN_SOL_PER_TRADE"]:
        return False
    
    if amount_sol > TRADING_CONFIG["MAX_SOL_PER_TRADE"]:
        return False
    
    if slippage_percent < 0 or slippage_percent > 50:
        return False
    
    return True

def get_priority_fee(urgency_level: str = "normal") -> int:
    """
    Get priority fee based on urgency level.
    
    Args:
        urgency_level: "low", "normal", "high", or "urgent"
        
    Returns:
        Priority fee in microlamports
    """
    fees = {
        "low": 10000,
        "normal": 50000,
        "high": 100000,
        "urgent": 500000,
    }
    
    return fees.get(urgency_level, TRADING_CONFIG["DEFAULT_PRIORITY_FEE"])

# Reverse-engineered patterns from successful wallets
SUCCESSFUL_PATTERNS = {
    "pattern_name": "Direct Meteora DBC",
    "confidence": "High",
    "success_rate": "100%",
    "details": "Direct interaction with Meteora Dynamic Bonding Curve for new token trading (early launch strategy)",
    
    # Key characteristics observed
    "characteristics": {
        "uses_jito": True,
        "high_priority_fees": True,
        "direct_protocol_interaction": True,
        "no_aggregators": True,
        "professional_timing": True,
    },
    
    # Typical transaction structure
    "transaction_structure": {
        "instruction_count": 2,  # Usually create ATA + buy
        "programs_used": [
            "Meteora Dynamic Bonding Curve",
            "System Program", 
            "Associated Token Program"
        ],
        "average_execution_time": 3.2,  # seconds
    }
}
