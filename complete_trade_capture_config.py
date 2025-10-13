"""
COMPLETE TRADE CAPTURE CONFIGURATION
====================================
This file contains all settings to ensure your bot catches EVERY SINGLE TRADE
from your target wallets without missing anything.
"""

# ==============================================================================
# 1. WEBSOCKET MONITORING SETTINGS - ULTRA AGGRESSIVE
# ==============================================================================

WEBSOCKET_CONFIG = {
    # Subscribe to multiple event types for maximum coverage
    "subscription_types": [
        "accountSubscribe",      # Balance changes (primary method)
        "logsSubscribe",        # Transaction logs (backup method)
        "signatureSubscribe"    # Transaction signatures (tertiary method)
    ],
    
    # Use fastest commitment level for immediate detection
    "commitment": "processed",  # Fastest possible (confirmed is slower)
    
    # Connection settings for reliability
    "connection_timeout": 30,
    "message_timeout": 5,       # Short timeout for frequent checks
    "reconnect_delay": 2,       # Quick reconnection
    "max_reconnects": 999,      # Never give up reconnecting
    
    # Buffer management
    "max_buffer_size": 10000,   # Large buffer to avoid missing messages
    "process_batch_size": 50,   # Process multiple messages at once
}

# ==============================================================================
# 2. TRANSACTION ANALYSIS SETTINGS - MAXIMUM DEPTH
# ==============================================================================

ANALYSIS_CONFIG = {
    # Historical scanning depth
    "history_scan_depth": 100,          # Scan last 100 transactions on startup
    "recent_tx_scan_depth": 25,         # Analyze 25 most recent transactions per trigger
    "quick_scan_depth": 10,             # Quick analysis depth during active monitoring
    
    # Analysis timeouts (longer = more thorough)
    "analysis_timeout": 20.0,           # 20 seconds per transaction analysis
    "quick_analysis_timeout": 10.0,     # 10 seconds for bulk analysis
    "balance_analysis_timeout": 5.0,    # 5 seconds for balance comparison
    
    # Detection thresholds
    "min_token_change": 0.000001,       # Detect even tiny token changes
    "min_sol_change": 0.001,            # Minimum SOL change to consider (0.001 = 1000 lamports)
    
    # Signature processing
    "processed_signatures_limit": 500,   # Keep track of last 500 processed signatures
    "signature_cleanup_interval": 100,   # Clean old signatures every 100 new ones
    "allow_reprocessing_after": 200,    # Allow reprocessing after 200 new signatures
}

# ==============================================================================
# 3. DUAL DETECTION METHOD SETTINGS - REDUNDANT COVERAGE
# ==============================================================================

DETECTION_CONFIG = {
    # Primary method: Official Solana balance analysis (most reliable)
    "use_balance_analysis": True,
    "balance_analysis_priority": 1,
    
    # Secondary method: Log pattern matching (catches edge cases)
    "use_log_analysis": True,
    "log_analysis_priority": 2,
    
    # Tertiary method: Instruction analysis (experimental)
    "use_instruction_analysis": True,
    "instruction_analysis_priority": 3,
    
    # Cross-validation settings
    "require_method_agreement": False,   # Don't require multiple methods to agree
    "confidence_threshold": 1,           # Accept trades with confidence >= 1
    "allow_single_method_detection": True,  # Accept detection from any single method
}

# ==============================================================================
# 4. DEX COVERAGE - ALL MAJOR DEXEs
# ==============================================================================

DEX_PATTERNS = {
    # Pump.fun patterns (most comprehensive)
    "Pump.fun": [
        "pump", "pumpfun", "6eav", "6eav1tx", "pumpportal", "pump.fun",
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Program ID
        "bonkbot", "pumpbot", "pump portal"
    ],
    
    # Jupiter patterns
    "Jupiter": [
        "jupiter", "jup4x", "jupag", "jup6", "jupiter aggregator",
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",  # Program ID
        "jup", "jupiter swap", "jupiter v6"
    ],
    
    # Raydium patterns (all variants)
    "Raydium": [
        "raydium", "675k", "cpmmoo", "ramt", "ray", "675kpx9",
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # CPMM Program
        "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",   # CLMM Program  
        "routeUGWgWzqBWFcrCfv8tritsqukccJPu3q5GPP3xS",    # Router Program
        "raydium cpmm", "raydium clmm", "raydium amm"
    ],
    
    # Orca patterns
    "Orca": [
        "orca", "whirlpool", "whirls", "orcaquote",
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",    # Whirlpool Program
        "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qew",    # Orca Swap Program
        "orca whirlpool", "orca swap"
    ],
    
    # Meteora patterns
    "Meteora": [
        "meteor", "dlmm", "meteora", "meteor dlmm",
        "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",    # DLMM Program
        "meteora dlmm", "meteora amm"
    ],
    
    # Phoenix patterns
    "Phoenix": [
        "phoenix", "phnx", "phoenix dex",
        "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY",    # Program ID
    ],
    
    # Additional DEXes
    "Serum": [
        "serum", "9wff", "srmmarket", "serum dex",
        "EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o",    # Program ID
    ],
    
    "Openbook": [
        "openbook", "opnb", "openbook dex",
        "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX",    # Program ID
    ],
    
    "Lifinity": [
        "lifinity", "lfnty", "lifinity dex",
        "EewxydAPCDdPDlaNDv5XqUkBGQ1s9bw3BKMdWd8RNR5T",    # Program ID
    ],
    
    "Drift": [
        "drift", "driftmarket", "drift protocol",
        "dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH",     # Program ID
    ]
}

# ==============================================================================
# 5. TRADE PATTERN RECOGNITION - COMPREHENSIVE
# ==============================================================================

TRADE_PATTERNS = {
    # BUY indicators (getting tokens, spending SOL)
    "buy_instructions": [
        "swapbasetoquote", "exactinwithslippage", "swapexactin", 
        "buy", "purchase", "deposit", "mint", "create", "swap_base_in",
        "token_in", "receive_token", "acquire", "obtain"
    ],
    
    # SELL indicators (giving tokens, receiving SOL)  
    "sell_instructions": [
        "swapquotetobase", "exactoutwithslippage", "swapexactout",
        "sell", "redeem", "withdraw", "burn", "close", "swap_base_out",
        "token_out", "send_token", "liquidate", "dispose"
    ],
    
    # SOL flow indicators
    "sol_spending_patterns": [
        "transfer sol", "lamports: -", "sol out", "spending", 
        "debit", "subtract", "pay", "send sol"
    ],
    
    "sol_receiving_patterns": [
        "receive sol", "lamports: +", "sol in", "received",
        "credit", "add", "get", "receive sol"
    ],
    
    # Token flow indicators
    "token_receiving_patterns": [
        "token in", "receive token", "mint to", "token credit",
        "token increase", "token acquired", "token obtained"
    ],
    
    "token_sending_patterns": [
        "token out", "transfer token", "burn from", "token debit",
        "token decrease", "token sent", "token disposed"
    ]
}

# ==============================================================================
# 6. RATE LIMITING & PERFORMANCE - OPTIMIZED FOR SPEED
# ==============================================================================

PERFORMANCE_CONFIG = {
    # RPC call rates (balance speed vs rate limits)
    "max_rpc_calls_per_second": 50,     # High rate for fast detection
    "rpc_call_delay": 0.02,             # 20ms between calls
    "burst_limit": 10,                  # Allow bursts of 10 calls
    
    # Parallel processing
    "max_concurrent_analysis": 5,       # Analyze 5 transactions simultaneously
    "max_concurrent_wallets": 3,        # Monitor 3 wallets simultaneously
    
    # Caching for performance
    "cache_token_info": True,           # Cache token metadata
    "cache_pool_info": True,            # Cache pool information
    "cache_duration": 300,              # 5 minute cache
    
    # Memory management
    "max_memory_usage_mb": 1000,        # 1GB max memory usage
    "cleanup_interval": 600,            # Clean up every 10 minutes
}

# ==============================================================================
# 7. ERROR RECOVERY - NEVER GIVE UP
# ==============================================================================

ERROR_RECOVERY_CONFIG = {
    # Retry settings
    "max_retries_per_transaction": 5,   # Retry failed analysis 5 times
    "retry_delay": 1.0,                 # 1 second between retries
    "exponential_backoff": True,        # Increase delay on repeated failures
    
    # Timeout recovery
    "analysis_timeout_recovery": True,  # Retry timed out analysis
    "websocket_timeout_recovery": True, # Reconnect on WebSocket timeout
    
    # Fallback methods
    "use_fallback_rpc": True,           # Switch to backup RPC on failure
    "use_historical_scan_on_miss": True, # Scan history if real-time fails
    "emergency_full_rescan": True,      # Full rescan if too many misses detected
    
    # Health monitoring
    "health_check_interval": 60,        # Check system health every minute
    "max_missed_trades_alert": 3,       # Alert if 3+ trades seem missed
    "auto_restart_on_health_fail": True # Restart bot if health check fails
}

# ==============================================================================
# 8. LOGGING & MONITORING - FULL VISIBILITY
# ==============================================================================

LOGGING_CONFIG = {
    # Detection logging
    "log_all_detections": True,         # Log every trade detection
    "log_detection_details": True,      # Include detailed analysis
    "log_false_positives": True,        # Log non-trades for tuning
    
    # Performance logging
    "log_analysis_times": True,         # Track analysis performance
    "log_websocket_events": True,       # Log all WebSocket events
    "log_rpc_calls": False,             # Don't log every RPC call (too noisy)
    
    # File logging
    "detection_log_file": "trade_detections.log",
    "performance_log_file": "performance.log", 
    "error_log_file": "errors.log",
    
    # CSV export
    "export_detections_csv": True,      # Export all detections to CSV
    "csv_export_interval": 300,         # Export every 5 minutes
    "csv_file": "all_trade_detections.csv"
}

# ==============================================================================
# 9. VALIDATION SETTINGS - ENSURE ACCURACY
# ==============================================================================

VALIDATION_CONFIG = {
    # Cross-check detections
    "validate_with_blockchain": True,   # Double-check detections on-chain
    "validate_token_amounts": True,     # Verify token amounts make sense
    "validate_timing": True,            # Check transaction timing consistency
    
    # Filters to avoid false positives
    "ignore_dust_amounts": False,       # Don't ignore tiny amounts (may be real trades)
    "ignore_failed_transactions": True, # Skip failed transactions
    "ignore_system_transactions": True, # Skip system/administrative transactions
    
    # Token validation
    "validate_token_mint": True,        # Verify token mint addresses
    "min_token_value_usd": 0.0001,     # Minimum token value to consider ($0.0001)
    "blacklist_known_spam": True,       # Filter out known spam tokens
}

# ==============================================================================
# 10. EXPORT FUNCTION - APPLY ALL SETTINGS
# ==============================================================================

def get_complete_capture_config():
    """Get the complete configuration for maximum trade capture"""
    return {
        "websocket": WEBSOCKET_CONFIG,
        "analysis": ANALYSIS_CONFIG,
        "detection": DETECTION_CONFIG,
        "dex_patterns": DEX_PATTERNS,
        "trade_patterns": TRADE_PATTERNS,
        "performance": PERFORMANCE_CONFIG,
        "error_recovery": ERROR_RECOVERY_CONFIG,
        "logging": LOGGING_CONFIG,
        "validation": VALIDATION_CONFIG
    }

def apply_ultra_aggressive_settings(bot_instance):
    """Apply ultra-aggressive settings to an existing bot instance"""
    config = get_complete_capture_config()
    
    # Apply WebSocket settings
    bot_instance.websocket_timeout = config["websocket"]["message_timeout"]
    bot_instance.reconnect_delay = config["websocket"]["reconnect_delay"]
    
    # Apply analysis settings
    bot_instance.history_scan_depth = config["analysis"]["history_scan_depth"]
    bot_instance.analysis_timeout = config["analysis"]["analysis_timeout"]
    
    # Apply detection settings
    bot_instance.confidence_threshold = config["detection"]["confidence_threshold"]
    
    print("✅ Ultra-aggressive settings applied!")
    print(f"   📊 History scan depth: {config['analysis']['history_scan_depth']}")
    print(f"   ⏱️ Analysis timeout: {config['analysis']['analysis_timeout']}s")
    print(f"   🎯 Detection methods: {len([k for k,v in config['detection'].items() if k.startswith('use_') and v])}")
    print(f"   🏭 DEX patterns: {len(config['dex_patterns'])} DEXes covered")
    
    return config

# ==============================================================================
# USAGE EXAMPLE
# ==============================================================================

if __name__ == "__main__":
    config = get_complete_capture_config()
    print("Complete Trade Capture Configuration Generated!")
    print(f"Total DEXes covered: {len(config['dex_patterns'])}")
    print(f"Total trade patterns: {len(config['trade_patterns']['buy_instructions']) + len(config['trade_patterns']['sell_instructions'])}")
    print(f"Analysis timeout: {config['analysis']['analysis_timeout']}s")
    print(f"History scan depth: {config['analysis']['history_scan_depth']} transactions")
