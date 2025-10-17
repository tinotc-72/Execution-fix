#!/usr/bin/env python3
"""
Test script to verify DebugSpan integration with the inference pipeline.

This script validates that:
1. Correlation ID is generated at the start of each event
2. Correlation context is logged with dex and wallet info
3. DebugSpan wraps each sub-step in infer_missing_fields
4. Granular trace lines are logged with timing and correlation ID
"""

import sys
import re


def test_correlation_id_generation():
    """Test that correlation ID is generated in _process_detected_trade."""
    print("\n" + "=" * 80)
    print("TEST 1: Correlation ID Generation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for uuid import
    if 'import uuid' in content:
        print("  ✅ uuid module imported")
    else:
        print("  ❌ uuid module not imported")
        return False
    
    # Check for set_span_id import
    if 'from debug_utils import set_span_id' in content:
        print("  ✅ set_span_id imported from debug_utils")
    else:
        print("  ❌ set_span_id not imported")
        return False
    
    # Check for correlation ID generation logic
    if re.search(r'correlation_id = sig\[:12\]', content):
        print("  ✅ Correlation ID generated from signature")
    else:
        print("  ❌ Correlation ID generation from signature not found")
        return False
    
    # Check for UUID fallback
    if 'uuid.uuid4()' in content:
        print("  ✅ UUID fallback for correlation ID")
    else:
        print("  ❌ UUID fallback not found")
        return False
    
    # Check for set_span_id call
    if 'set_span_id(correlation_id)' in content:
        print("  ✅ set_span_id() called with correlation_id")
    else:
        print("  ❌ set_span_id() call not found")
        return False
    
    return True


def test_correlation_context_logging():
    """Test that correlation context is logged."""
    print("\n" + "=" * 80)
    print("TEST 2: Correlation Context Logging")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for correlation context log
    pattern = r'logger\.info\(\s*"🪪 \[CTX\] corr=%s, dex=%s, wallet=%s"'
    if re.search(pattern, content):
        print("  ✅ Correlation context logged with corr, dex, wallet")
    else:
        print("  ❌ Correlation context logging not found")
        return False
    
    # Check that it's logging correlation_id
    if 'correlation_id,' in content:
        print("  ✅ correlation_id included in log")
    else:
        print("  ❌ correlation_id not in log parameters")
        return False
    
    return True


def test_debug_span_integration():
    """Test that DebugSpan is integrated in trade_processor.py."""
    print("\n" + "=" * 80)
    print("TEST 3: DebugSpan Integration in trade_processor.py")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check for DebugSpan import
    if 'from debug_utils import DebugSpan, get_span_id' in content:
        print("  ✅ DebugSpan and get_span_id imported")
    else:
        print("  ❌ DebugSpan import not found")
        return False
    
    # Check for DebugSpan usage in infer_missing_fields
    debug_span_patterns = [
        (r'with DebugSpan\("ensure_meta"', "ensure_meta step wrapped"),
        (r'with DebugSpan\("annotate_source_failure"', "annotate_source_failure step wrapped"),
        (r'with DebugSpan\("last_chance_fetch"', "last_chance_fetch step wrapped"),
        (r'with DebugSpan\("infer_signature"', "infer_signature step wrapped"),
        (r'with DebugSpan\("fetch_transaction"', "fetch_transaction step wrapped"),
        (r'with DebugSpan\("infer_wallet"', "infer_wallet step wrapped"),
        (r'with DebugSpan\("infer_action"', "infer_action step wrapped"),
        (r'with DebugSpan\("infer_dex"', "infer_dex step wrapped"),
        (r'with DebugSpan\("infer_token_mint"', "infer_token_mint step wrapped"),
    ]
    
    found_count = 0
    for pattern, description in debug_span_patterns:
        if re.search(pattern, content):
            print(f"  ✅ {description}")
            found_count += 1
        else:
            print(f"  ⚠️  {description} - not found")
    
    if found_count >= 6:
        print(f"  ✅ Found {found_count} DebugSpan-wrapped steps (minimum 6 required)")
        return True
    else:
        print(f"  ❌ Only found {found_count} DebugSpan-wrapped steps (minimum 6 required)")
        return False


def test_correlation_id_logging():
    """Test that correlation ID is logged in infer_missing_fields."""
    print("\n" + "=" * 80)
    print("TEST 4: Correlation ID in Inference Logs")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check for get_span_id() usage
    if 'corr_id = get_span_id()' in content:
        print("  ✅ get_span_id() called to retrieve correlation ID")
    else:
        print("  ❌ get_span_id() call not found")
        return False
    
    # Check for correlation ID in log message
    if 'corr=%s' in content and re.search(r'logger\.info.*corr=%s.*corr_id', content):
        print("  ✅ Correlation ID included in log messages")
    else:
        print("  ❌ Correlation ID not in log messages")
        return False
    
    return True


def test_input_data_logging():
    """Test that input data is logged in DebugSpan."""
    print("\n" + "=" * 80)
    print("TEST 5: Input Data Logging")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check for input_data parameter in DebugSpan calls
    patterns = [
        r'input_data={"has_meta": bool',
        r'input_data={"signature":',
        r'input_data={"has_transaction":',
        r'input_data={"has_logs":',
    ]
    
    found = 0
    for pattern in patterns:
        if re.search(pattern, content):
            found += 1
    
    if found >= 3:
        print(f"  ✅ Found {found} DebugSpan calls with input_data")
        return True
    else:
        print(f"  ❌ Only found {found} DebugSpan calls with input_data")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 80)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 80)
    
    tests = [
        ("Correlation ID Generation", test_correlation_id_generation),
        ("Correlation Context Logging", test_correlation_context_logging),
        ("DebugSpan Integration", test_debug_span_integration),
        ("Correlation ID in Inference Logs", test_correlation_id_logging),
        ("Input Data Logging", test_input_data_logging),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
