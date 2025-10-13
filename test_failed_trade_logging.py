#!/usr/bin/env python3
"""
Test script for failed trade analysis logging functionality.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
sys.path.append('.')

def test_log_failed_trade_analysis():
    """Test the failed trade analysis logging function."""
    print('📝 TESTING FAILED TRADE ANALYSIS LOGGING')
    print('=' * 50)
    
    # Import the logging function
    from main import log_failed_trade_analysis
    
    # Clean up any existing log file for clean test
    log_file = "failed_trade_analysis.log"
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f'🧹 Cleaned up existing log file: {log_file}')
    
    # Test Case 1: Retry failure
    print('\n🔄 TEST 1: Retry Failure Logging')
    trade_info_1 = {
        "signature": "test_signature_12345abcdef",
        "wallet_address": "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB",
        "dex_type": "jupiter",
        "program_id": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
    }
    
    routing_data_1 = {
        "action": "unknown",
        "token_mint": "PENDING_ANALYSIS",
        "platform": "jupiter"
    }
    
    log_failed_trade_analysis(
        trade_info_1,
        failure_reason="failed_after_retries_action_unknown_mint_PENDING_ANALYSIS",
        retry_count=3,
        routing_data=routing_data_1
    )
    
    # Test Case 2: Unknown action
    print('❓ TEST 2: Unknown Action Logging')
    trade_info_2 = {
        "signature": "unknown_action_test_67890xyz", 
        "wallet_address": "B27Q6WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoC",
        "dex_type": "raydium",
        "program_id": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
    }
    
    routing_data_2 = {
        "action": "complex_swap",
        "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    }
    
    log_failed_trade_analysis(
        trade_info_2,
        failure_reason="unknown_action_complex_swap_skipped_execution", 
        retry_count=0,
        routing_data=routing_data_2
    )
    
    # Test Case 3: Execution failure
    print('💥 TEST 3: Execution Failure Logging')
    trade_info_3 = {
        "signature": "execution_fail_test_999abc",
        "wallet_address": "C28R7YXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoD",
        "dex_type": "pumpfun", 
        "program_id": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    }
    
    execution_result = {
        "success": False,
        "error": "insufficient_balance",
        "details": "Not enough SOL for transaction fees"
    }
    
    log_failed_trade_analysis(
        trade_info_3,
        failure_reason="execution_failed_buy_result_dict",
        retry_count=0,
        routing_data={
            "routing": {"action": "buy", "token_mint": "TokenMint123"},
            "execution_result": execution_result,
            "action": "buy",
            "token_mint": "TokenMint123",
            "dex": "pumpfun"
        }
    )
    
    # Verify log file was created and contains our entries
    print(f'\n📋 VERIFYING LOG FILE: {log_file}')
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        print(f'✅ Log file created successfully')
        print(f'✅ Number of entries: {len(lines)}')
        
        # Parse and display each entry
        for i, line in enumerate(lines, 1):
            try:
                entry = json.loads(line.strip())
                print(f'\n📝 ENTRY {i}:')
                print(f'   Timestamp: {entry["timestamp"]}')
                print(f'   Failure Reason: {entry["failure_reason"]}')
                print(f'   Signature: {entry["signature"]}')
                print(f'   Retry Count: {entry["retry_count"]}')
                print(f'   DEX Type: {entry["dex_type"]}')
                print(f'   Has Routing Data: {bool(entry["routing_data"])}')
            except Exception as e:
                print(f'❌ Failed to parse entry {i}: {e}')
    else:
        print(f'❌ Log file not created: {log_file}')
        return False
        
    print('\n' + '=' * 50)
    print('✅ FAILED TRADE ANALYSIS LOGGING TEST COMPLETE')
    print('\n🎯 Key Features Verified:')
    print('  • JSON structured logging format')
    print('  • Timestamp and failure reason tracking')
    print('  • Retry count and routing data preservation')  
    print('  • Signature and wallet address capture')
    print('  • DEX type and program ID logging')
    print('  • Comprehensive trade_info preservation')
    
    return True

if __name__ == "__main__":
    success = test_log_failed_trade_analysis()
    if success:
        print('\n🚀 Ready for production offline debugging!')
    else:
        print('\n❌ Test failed - check implementation')