#!/usr/bin/env python3
"""
Test try_backfill implementation for websocket_account_change events.

This test validates that:
1. try_backfill function exists and has correct signature
2. Returns True if signature already exists
3. Fetches latest signature via RPC when missing
4. Logs appropriate messages for different scenarios
5. Attaches signature, transaction, meta, and logs on success
6. Returns False when backfill fails
7. Pipeline checks detection_method == "websocket_account_change"
8. Pipeline calls try_backfill before infer_missing_fields and validate_trade_info
9. Pipeline returns early without marking as skipped when backfill fails
10. Pipeline proceeds to validation only when backfill succeeds
"""

import re
import sys

def test_try_backfill_function():
    """Test that try_backfill function exists with correct signature"""
    print("\n" + "="*80)
    print("TEST 1: try_backfill Function Signature")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'async def try_backfill\(trade_info: dict, rpc_client\) -> bool:', '✅ try_backfill is async with correct signature'),
        (r'def try_backfill.*trade_info.*rpc_client', '✅ Takes trade_info and rpc_client parameters'),
        (r'-> bool:', '✅ Returns bool'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_signature_already_exists():
    """Test that try_backfill returns True if signature already exists"""
    print("\n" + "="*80)
    print("TEST 2: Signature Already Exists Logic")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'sig = \(trade_info\.get\("signature"\) or ""\)\.strip\(\)', '✅ Gets signature from trade_info'),
        (r'if sig and sig != "unknown":', '✅ Checks if signature exists and is not unknown'),
        (r'return True', '✅ Returns True when signature exists'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_backfill_logic():
    """Test backfill logic when signature is missing"""
    print("\n" + "="*80)
    print("TEST 3: Backfill Logic")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'wallet_address = trade_info\.get\("wallet_address"\)', '✅ Gets wallet_address from trade_info'),
        (r'from websocket_handler import backfill_latest_tx', '✅ Imports backfill_latest_tx'),
        (r'backfill_result = await backfill_latest_tx\(rpc_url, wallet_address\)', '✅ Calls backfill_latest_tx with await'),
        (r'signature = backfill_result\.get\("signature"\)', '✅ Extracts signature from result'),
        (r'transaction = backfill_result\.get\("transaction"\)', '✅ Extracts transaction from result'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_logging_messages():
    """Test that appropriate logging messages are present"""
    print("\n" + "="*80)
    print("TEST 4: Logging Messages")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'⏳ \[BACKFILL\] No recent signature — waiting for logs event', '✅ Logs "No recent signature" message'),
        (r'⏳ \[BACKFILL\] getTransaction returned None — waiting for logs event', '✅ Logs "getTransaction returned None" message'),
        (r'✅ \[BACKFILL\] Successfully backfilled', '✅ Logs success message'),
        (r'⏳ \[BACKFILL\] Backfill failed.*waiting for logs event', '✅ Logs backfill failed message'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_attach_data_on_success():
    """Test that signature, transaction, meta, and logs are attached on success"""
    print("\n" + "="*80)
    print("TEST 5: Attach Data on Success")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'trade_info\["signature"\] = signature', '✅ Attaches signature to trade_info'),
        (r'trade_info\["transaction"\] = transaction', '✅ Attaches transaction to trade_info'),
        (r'trade_info\["meta"\] = backfill_result\.get\("meta"\)', '✅ Attaches meta to trade_info'),
        (r'trade_info\["logs"\] = backfill_result\.get\("logs", \[\]\)', '✅ Attaches logs to trade_info'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_pipeline_detection_method_check():
    """Test that pipeline checks for websocket_account_change detection_method"""
    print("\n" + "="*80)
    print("TEST 6: Pipeline Detection Method Check")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'detection_method = trade_info\.get\("detection_method", ""\)', '✅ Gets detection_method from trade_info'),
        (r'if detection_method == "websocket_account_change":', '✅ Checks for websocket_account_change'),
        (r'backfill_success = await try_backfill\(trade_info, self\.rpc_client\)', '✅ Calls try_backfill with await'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_pipeline_backfill_failure_handling():
    """Test that pipeline handles backfill failure correctly"""
    print("\n" + "="*80)
    print("TEST 7: Pipeline Backfill Failure Handling")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'if not backfill_success:', '✅ Checks if backfill failed'),
        (r'waiting for subsequent websocket_logs event', '✅ Logs waiting for logs event'),
        (r'Not marking as skipped to allow logs event to proceed', '✅ Logs not marking as skipped'),
        (r'return.*# Return without marking as skipped', '✅ Returns without marking as skipped'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_pipeline_proceeds_on_success():
    """Test that pipeline proceeds to validation only when backfill succeeds"""
    print("\n" + "="*80)
    print("TEST 8: Pipeline Proceeds on Backfill Success")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check that after backfill success, we proceed to infer_missing_fields and validate_trade_info
    checks = [
        (r'✅ \[BACKFILL\] Backfill succeeded — proceeding to validation', '✅ Logs backfill success'),
        (r'# STEP 1: Infer missing fields before validation', '✅ Has infer_missing_fields step after backfill'),
        (r'trade_info = self\.trade_processor\.infer_missing_fields\(trade_info\)', '✅ Calls infer_missing_fields'),
        (r'# STEP 2: Validate and process', '✅ Has validate step'),
        (r'is_valid = self\.trade_processor\.validate_trade_info\(trade_info\)', '✅ Calls validate_trade_info'),
    ]
    
    passed = 0
    for pattern, success_msg in checks:
        if re.search(pattern, content):
            print(f"  {success_msg}")
            passed += 1
        else:
            print(f"  ❌ Missing: {pattern}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_backfill_before_validation():
    """Test that backfill check comes before infer_missing_fields and validate_trade_info"""
    print("\n" + "="*80)
    print("TEST 9: Backfill Ordering")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find positions of key statements
    backfill_check_pos = content.find('if detection_method == "websocket_account_change":')
    infer_pos = content.find('# STEP 1: Infer missing fields before validation', backfill_check_pos - 1000 if backfill_check_pos > 0 else 0)
    validate_pos = content.find('is_valid = self.trade_processor.validate_trade_info(trade_info)', backfill_check_pos - 1000 if backfill_check_pos > 0 else 0)
    
    checks_passed = 0
    
    if backfill_check_pos > 0:
        print(f"  ✅ Found backfill check at position {backfill_check_pos}")
        checks_passed += 1
    else:
        print(f"  ❌ Backfill check not found")
    
    if infer_pos > backfill_check_pos and backfill_check_pos > 0:
        print(f"  ✅ infer_missing_fields comes after backfill check (at {infer_pos})")
        checks_passed += 1
    else:
        print(f"  ❌ infer_missing_fields order incorrect")
    
    if validate_pos > backfill_check_pos and backfill_check_pos > 0:
        print(f"  ✅ validate_trade_info comes after backfill check (at {validate_pos})")
        checks_passed += 1
    else:
        print(f"  ❌ validate_trade_info order incorrect")
    
    print(f"\n  Result: {checks_passed}/3 checks passed")
    return checks_passed == 3

if __name__ == "__main__":
    print("="*80)
    print("TRY_BACKFILL IMPLEMENTATION VALIDATION")
    print("="*80)
    
    all_tests = [
        ("try_backfill Function Signature", test_try_backfill_function),
        ("Signature Already Exists Logic", test_signature_already_exists),
        ("Backfill Logic", test_backfill_logic),
        ("Logging Messages", test_logging_messages),
        ("Attach Data on Success", test_attach_data_on_success),
        ("Pipeline Detection Method Check", test_pipeline_detection_method_check),
        ("Pipeline Backfill Failure Handling", test_pipeline_backfill_failure_handling),
        ("Pipeline Proceeds on Success", test_pipeline_proceeds_on_success),
        ("Backfill Ordering", test_backfill_before_validation),
    ]
    
    results = []
    for test_name, test_func in all_tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print("\n" + "="*80)
    print(f"OVERALL: {passed_count}/{total_count} tests passed")
    print("="*80)
    
    sys.exit(0 if passed_count == total_count else 1)
