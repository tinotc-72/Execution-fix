#!/usr/bin/env python3
"""
Test buy/sell inference based on token balance changes.

Tests the enhanced detect_buy_sell method to ensure:
1. WSOL decreases + token increases → action="buy"
2. Token decreases + WSOL increases → action="sell"
3. mint_in and mint_out are correctly saved
4. Logging includes "🎯 Detected action=%s"
"""

import sys
import os

# Add current directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging

# Set up logging to capture the specific log message
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_buy_inference():
    """Test BUY detection: WSOL decreases, token increases"""
    from trade_processor import TradeProcessor
    
    WSOL = "So11111111111111111111111111111111111111112"
    TOKEN_MINT = "TokenMint1111111111111111111111111111111111"
    WALLET = "WalletAddress111111111111111111111111111111"
    
    # Mock RPC client
    class MockRPC:
        rpc_url = "http://mock"
    
    processor = TradeProcessor([WALLET], MockRPC())
    
    # Create meta with balance changes: WSOL down, token up (BUY)
    meta = {
        'preTokenBalances': [
            {
                'owner': WALLET,
                'mint': WSOL,
                'uiTokenAmount': {'uiAmount': 1.0}
            },
            {
                'owner': WALLET,
                'mint': TOKEN_MINT,
                'uiTokenAmount': {'uiAmount': 0.0}
            }
        ],
        'postTokenBalances': [
            {
                'owner': WALLET,
                'mint': WSOL,
                'uiTokenAmount': {'uiAmount': 0.5}  # Decreased by 0.5
            },
            {
                'owner': WALLET,
                'mint': TOKEN_MINT,
                'uiTokenAmount': {'uiAmount': 100.0}  # Increased by 100
            }
        ]
    }
    
    actions = processor.detect_buy_sell(meta, [WALLET])
    
    print("\n🧪 Test 1: BUY Inference")
    print("=" * 50)
    
    if not actions:
        print("❌ FAIL: No actions detected")
        return False
    
    action = actions[0]
    
    # Check action type
    if action['action'] != 'buy':
        print(f"❌ FAIL: Expected action='buy', got '{action['action']}'")
        return False
    print(f"✅ PASS: action = '{action['action']}'")
    
    # Check mint_in (should be WSOL for buy)
    if action.get('mint_in') != WSOL:
        print(f"❌ FAIL: Expected mint_in='{WSOL}', got '{action.get('mint_in')}'")
        return False
    print(f"✅ PASS: mint_in = '{action['mint_in']}'")
    
    # Check mint_out (should be token for buy)
    if action.get('mint_out') != TOKEN_MINT:
        print(f"❌ FAIL: Expected mint_out='{TOKEN_MINT}', got '{action.get('mint_out')}'")
        return False
    print(f"✅ PASS: mint_out = '{action['mint_out']}'")
    
    print("✅ Test 1 PASSED: BUY inference working correctly\n")
    return True

def test_sell_inference():
    """Test SELL detection: token decreases, WSOL increases"""
    from trade_processor import TradeProcessor
    
    WSOL = "So11111111111111111111111111111111111111112"
    TOKEN_MINT = "TokenMint1111111111111111111111111111111111"
    WALLET = "WalletAddress111111111111111111111111111111"
    
    # Mock RPC client
    class MockRPC:
        rpc_url = "http://mock"
    
    processor = TradeProcessor([WALLET], MockRPC())
    
    # Create meta with balance changes: token down, WSOL up (SELL)
    meta = {
        'preTokenBalances': [
            {
                'owner': WALLET,
                'mint': WSOL,
                'uiTokenAmount': {'uiAmount': 0.5}
            },
            {
                'owner': WALLET,
                'mint': TOKEN_MINT,
                'uiTokenAmount': {'uiAmount': 100.0}
            }
        ],
        'postTokenBalances': [
            {
                'owner': WALLET,
                'mint': WSOL,
                'uiTokenAmount': {'uiAmount': 1.0}  # Increased by 0.5
            },
            {
                'owner': WALLET,
                'mint': TOKEN_MINT,
                'uiTokenAmount': {'uiAmount': 0.0}  # Decreased by 100
            }
        ]
    }
    
    actions = processor.detect_buy_sell(meta, [WALLET])
    
    print("🧪 Test 2: SELL Inference")
    print("=" * 50)
    
    if not actions:
        print("❌ FAIL: No actions detected")
        return False
    
    action = actions[0]
    
    # Check action type
    if action['action'] != 'sell':
        print(f"❌ FAIL: Expected action='sell', got '{action['action']}'")
        return False
    print(f"✅ PASS: action = '{action['action']}'")
    
    # Check mint_in (should be token for sell)
    if action.get('mint_in') != TOKEN_MINT:
        print(f"❌ FAIL: Expected mint_in='{TOKEN_MINT}', got '{action.get('mint_in')}'")
        return False
    print(f"✅ PASS: mint_in = '{action['mint_in']}'")
    
    # Check mint_out (should be WSOL for sell)
    if action.get('mint_out') != WSOL:
        print(f"❌ FAIL: Expected mint_out='{WSOL}', got '{action.get('mint_out')}'")
        return False
    print(f"✅ PASS: mint_out = '{action['mint_out']}'")
    
    print("✅ Test 2 PASSED: SELL inference working correctly\n")
    return True

def test_logging_format():
    """Test that logging includes the required format"""
    import io
    import logging
    from trade_processor import TradeProcessor
    
    WSOL = "So11111111111111111111111111111111111111112"
    TOKEN_MINT = "TokenMint1111111111111111111111111111111111"
    WALLET = "WalletAddress111111111111111111111111111111"
    
    # Mock RPC client
    class MockRPC:
        rpc_url = "http://mock"
    
    # Capture log output
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)
    
    # Get the trade_processor logger
    tp_logger = logging.getLogger('trade_processor')
    tp_logger.addHandler(handler)
    tp_logger.setLevel(logging.INFO)
    
    processor = TradeProcessor([WALLET], MockRPC())
    
    # Create meta with BUY scenario
    meta = {
        'preTokenBalances': [
            {
                'owner': WALLET,
                'mint': WSOL,
                'uiTokenAmount': {'uiAmount': 1.0}
            },
            {
                'owner': WALLET,
                'mint': TOKEN_MINT,
                'uiTokenAmount': {'uiAmount': 0.0}
            }
        ],
        'postTokenBalances': [
            {
                'owner': WALLET,
                'mint': WSOL,
                'uiTokenAmount': {'uiAmount': 0.5}
            },
            {
                'owner': WALLET,
                'mint': TOKEN_MINT,
                'uiTokenAmount': {'uiAmount': 100.0}
            }
        ]
    }
    
    actions = processor.detect_buy_sell(meta, [WALLET])
    
    print("🧪 Test 3: Logging Format")
    print("=" * 50)
    
    # Check log output
    log_output = log_capture.getvalue()
    
    # Check for the specific log format: "🎯 Detected action=%s"
    if "🎯 Detected action=buy" not in log_output:
        print(f"❌ FAIL: Expected log '🎯 Detected action=buy' not found")
        print(f"Log output:\n{log_output}")
        return False
    print(f"✅ PASS: Found required log message '🎯 Detected action=buy'")
    
    # Check for mint_in and mint_out in logs
    if "Mint In:" not in log_output:
        print(f"❌ FAIL: Expected 'Mint In:' in log output")
        return False
    print(f"✅ PASS: Found 'Mint In:' in log output")
    
    if "Mint Out:" not in log_output:
        print(f"❌ FAIL: Expected 'Mint Out:' in log output")
        return False
    print(f"✅ PASS: Found 'Mint Out:' in log output")
    
    print("✅ Test 3 PASSED: Logging format correct\n")
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 BUY/SELL INFERENCE TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    try:
        results.append(("BUY Inference", test_buy_inference()))
    except Exception as e:
        print(f"❌ Test 1 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("BUY Inference", False))
    
    try:
        results.append(("SELL Inference", test_sell_inference()))
    except Exception as e:
        print(f"❌ Test 2 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("SELL Inference", False))
    
    try:
        results.append(("Logging Format", test_logging_format()))
    except Exception as e:
        print(f"❌ Test 3 FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Logging Format", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nPassed: {passed_count}/{total_count}")
    print("=" * 60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if all(passed for _, passed in results) else 1)

if __name__ == "__main__":
    main()
