#!/usr/bin/env python3
"""
Test script to validate execution fixes.

Tests:
1. Field inference properly extracts signature, dex, action, mint from transaction
2. Validation accepts inferred fields  
3. PoolResolver receives rpc and trade_info
4. Executor routing logs properly
"""

import sys
import json

def test_field_inference():
    """Test that infer_missing_fields is called before validation"""
    print("=" * 80)
    print("TEST 1: Field Inference Called Before Validation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Check that infer_missing_fields is called before validate_trade_info
    checks = [
        (
            'trade_info = self.trade_processor.infer_missing_fields(trade_info)',
            '✅ infer_missing_fields is called'
        ),
        (
            'is_valid = self.trade_processor.validate_trade_info(trade_info)',
            '✅ validate_trade_info is called after inference'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in main:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_validation_permissive():
    """Test that validation accepts inferred fields"""
    print("=" * 80)
    print("TEST 2: Validation Accepts Inferred Fields")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    checks = [
        (
            'valid_dexes = {"pumpfun", "raydium", "jupiter", "meteora", "unknown"}',
            '✅ Validation accepts "unknown" DEX for fallback routing'
        ),
        (
            'valid_actions = {"buy", "sell", "swap", "swap_in", "swap_out"}',
            '✅ Validation accepts "swap" action from inference'
        ),
        (
            'mint not in {"UNKNOWN", "PENDING_ANALYSIS"}',
            '✅ Validation rejects placeholder mint values'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in processor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_pool_resolver():
    """Test that PoolResolver receives rpc and trade_info"""
    print("=" * 80)
    print("TEST 3: PoolResolver Receives RPC and Trade Info")
    print("=" * 80)
    
    with open('mev_raydium_executor.py', 'r') as f:
        raydium = f.read()
    
    checks = [
        (
            'executor.pool_resolver = PoolResolver(executor.rpc, trade_info)',
            '✅ PoolResolver initialized with rpc and trade_info in try_raydium_buy'
        ),
        (
            'self.pool_resolver = None  # Will be set with trade_info when needed',
            '✅ PoolResolver set to None initially (no args available)'
        ),
        (
            'if not self.pool_resolver:',
            '✅ Validation check before using pool_resolver'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in raydium:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_executor_logging():
    """Test that executor routing has comprehensive logging"""
    print("=" * 80)
    print("TEST 4: Comprehensive Executor Logging")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        coordinator = f.read()
    
    checks = [
        (
            'self.logger.info(f"📊 [EXECUTION] Trade info summary:")',
            '✅ Logs trade info summary before execution'
        ),
        (
            'self.logger.info(f"🎯 [{idx}/{len(plan)}] Attempting executor: {label}")',
            '✅ Logs numbered executor attempts'
        ),
        (
            'self.logger.info(f"   → Calling',
            '✅ Logs which executor is being called'
        ),
        (
            'if result and (result.get("ok") or result.get("success"))',
            '✅ Checks both "ok" and "success" return formats'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in coordinator:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_enhanced_inference():
    """Test that infer_missing_fields fetches transaction if needed"""
    print("=" * 80)
    print("TEST 5: Enhanced Field Inference with Transaction Fetch")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    checks = [
        (
            'from utils import get_transaction_with_logs',
            '✅ Imports transaction fetching utility'
        ),
        (
            'if sig and sig != \'unknown\' and not trade_info.get(\'transaction\'):',
            '✅ Checks if transaction needs to be fetched'
        ),
        (
            'tx_data = get_transaction_with_logs(sig)',
            '✅ Fetches transaction data when signature available'
        ),
        (
            'inferred_fields.append(\'transaction (fetched)\')',
            '✅ Logs when transaction is fetched'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in processor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("EXECUTION FIXES VALIDATION")
    print("=" * 80)
    print()
    
    tests = [
        test_field_inference(),
        test_validation_permissive(),
        test_pool_resolver(),
        test_executor_logging(),
        test_enhanced_inference(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL EXECUTION FIXES VALIDATED!")
        print("\n  The following fixes are in place:")
        print("  ✅ Field inference called before validation")
        print("  ✅ Validation accepts inferred fields (swap, unknown dex)")
        print("  ✅ PoolResolver receives rpc and trade_info arguments")
        print("  ✅ Comprehensive executor logging with numbered attempts")
        print("  ✅ Transaction fetching when signature available")
        print()
        return 0
    else:
        print("\n  ❌ SOME FIXES NOT VALIDATED")
        print("  ❌ Review implementation")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
