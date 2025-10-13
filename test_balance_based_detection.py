#!/usr/bin/env python3

"""
Test Balance-Based Buy/Sell Detection

This script tests the improved balance-based action detection to ensure:
1. Always determines action from actual token balance changes
2. Never returns 'unknown' when real token movements exist
3. Correctly identifies buy vs sell from balance deltas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_processor import TradeProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_trade_info(pre_balances, post_balances, signature="test_sig"):
    """Create test trade info with specified pre/post token balances"""
    return {
        'signature': signature,
        'wallet_address': 'test_wallet',
        'meta': {
            'preTokenBalances': pre_balances,
            'postTokenBalances': post_balances
        }
    }

def test_buy_detection():
    """Test detection of buy (token balance increase)"""
    logger.info("🧪 Testing BUY detection (token balance increase)")
    
    pre_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token456',
            'uiTokenAmount': {'amount': '1000'}  # Start with 1000 tokens
        }
    ]
    
    post_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token456', 
            'uiTokenAmount': {'amount': '1500'}  # End with 1500 tokens (bought 500)
        }
    ]
    
    trade_info = create_test_trade_info(pre_balances, post_balances, "buy_test")
    processor = TradeProcessor(['wallet123'])  # Pass target_wallets
    
    action = processor._extract_action(trade_info)
    
    logger.info(f"   Result: {action}")
    assert action == 'buy', f"Expected 'buy', got '{action}'"
    logger.info("   ✅ BUY detection PASSED")
    return True

def test_sell_detection():
    """Test detection of sell (token balance decrease)"""
    logger.info("🧪 Testing SELL detection (token balance decrease)")
    
    pre_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token456',
            'uiTokenAmount': {'amount': '2000'}  # Start with 2000 tokens
        }
    ]
    
    post_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token456',
            'uiTokenAmount': {'amount': '1500'}  # End with 1500 tokens (sold 500)
        }
    ]
    
    trade_info = create_test_trade_info(pre_balances, post_balances, "sell_test")
    processor = TradeProcessor(['wallet123'])  # Pass target_wallets
    
    action = processor._extract_action(trade_info)
    
    logger.info(f"   Result: {action}")
    assert action == 'sell', f"Expected 'sell', got '{action}'"
    logger.info("   ✅ SELL detection PASSED")
    return True

def test_sol_filtering():
    """Test that SOL (native currency) changes are filtered out"""
    logger.info("🧪 Testing SOL filtering (should ignore SOL-only changes)")
    
    pre_balances = [
        {
            'owner': 'wallet123',
            'mint': 'So11111111111111111111111111111111111111112',  # SOL mint
            'uiTokenAmount': {'amount': '1000000000'}  # 1 SOL
        }
    ]
    
    post_balances = [
        {
            'owner': 'wallet123', 
            'mint': 'So11111111111111111111111111111111111111112',  # SOL mint
            'uiTokenAmount': {'amount': '500000000'}  # 0.5 SOL (paid fee)
        }
    ]
    
    trade_info = create_test_trade_info(pre_balances, post_balances, "sol_test")
    processor = TradeProcessor(['wallet123'])  # Pass target_wallets
    
    action = processor._extract_action(trade_info)
    
    logger.info(f"   Result: {action}")
    assert action == 'unknown', f"Expected 'unknown' for SOL-only change, got '{action}'"
    logger.info("   ✅ SOL filtering PASSED")
    return True

def test_multiple_token_changes():
    """Test handling of multiple token changes (should pick primary one)"""
    logger.info("🧪 Testing multiple token changes (should pick largest delta)")
    
    pre_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token_small',
            'uiTokenAmount': {'amount': '1000'}
        },
        {
            'owner': 'wallet123',
            'mint': 'token_large',
            'uiTokenAmount': {'amount': '5000'}
        }
    ]
    
    post_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token_small',
            'uiTokenAmount': {'amount': '1100'}  # +100 (small change)
        },
        {
            'owner': 'wallet123',
            'mint': 'token_large', 
            'uiTokenAmount': {'amount': '4000'}  # -1000 (large change - sell)
        }
    ]
    
    trade_info = create_test_trade_info(pre_balances, post_balances, "multi_test")
    processor = TradeProcessor(['wallet123'])  # Pass target_wallets
    
    action = processor._extract_action(trade_info)
    
    logger.info(f"   Result: {action}")
    assert action == 'sell', f"Expected 'sell' (largest delta), got '{action}'"
    logger.info("   ✅ Multiple token changes PASSED")
    return True

def test_no_changes():
    """Test case with no token balance changes"""
    logger.info("🧪 Testing no token changes (should return unknown)")
    
    pre_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token456',
            'uiTokenAmount': {'amount': '1000'}
        }
    ]
    
    post_balances = [
        {
            'owner': 'wallet123',
            'mint': 'token456',
            'uiTokenAmount': {'amount': '1000'}  # Same amount
        }
    ]
    
    trade_info = create_test_trade_info(pre_balances, post_balances, "no_change_test")
    processor = TradeProcessor(['wallet123'])  # Pass target_wallets
    
    action = processor._extract_action(trade_info)
    
    logger.info(f"   Result: {action}")
    assert action == 'unknown', f"Expected 'unknown' for no change, got '{action}'"
    logger.info("   ✅ No changes test PASSED")
    return True

def run_all_tests():
    """Run all balance-based detection tests"""
    logger.info("🚀 Starting Balance-Based Buy/Sell Detection Tests")
    logger.info("=" * 60)
    
    tests = [
        test_buy_detection,
        test_sell_detection, 
        test_sol_filtering,
        test_multiple_token_changes,
        test_no_changes
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            logger.info("")
        except Exception as e:
            logger.error(f"   ❌ {test_func.__name__} FAILED: {e}")
            failed += 1
            logger.info("")
    
    logger.info("=" * 60)
    logger.info(f"📊 Test Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        logger.info("🎉 All tests PASSED! Balance-based detection is working correctly.")
        logger.info("✅ Your bot will now:")
        logger.info("   • Always determine buy/sell from actual token balance changes")
        logger.info("   • Never log 'cannot determine if buy/sell/swap'")
        logger.info("   • Correctly identify direction even for complex transactions")
    else:
        logger.error("❌ Some tests failed. Check the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)