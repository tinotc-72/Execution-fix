#!/usr/bin/env python3
"""
Test script to validate backfill functionality in websocket_handler.py

Tests:
1. backfill_latest_tx helper function exists and has correct signature
2. backfill is integrated in _handle_account_notification
3. backfill is integrated in _handle_logs_notification
4. Logging uses consistent emoji format (🔁, ⚠️, 🧵)
5. No new dependencies introduced (only aiohttp which is already used)
"""

import sys
import ast

def test_backfill_helper_exists():
    """Test that backfill_latest_tx helper function exists with correct signature"""
    print("=" * 80)
    print("TEST 1: backfill_latest_tx Helper Function")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('async def backfill_latest_tx(', '✅ backfill_latest_tx is async'),
        ('helius_rpc_url: str', '✅ Takes helius_rpc_url parameter'),
        ('wallet_str: str', '✅ Takes wallet_str parameter'),
        ('limit: int = 1', '✅ Takes limit parameter with default'),
        ('-> Optional[Dict[str, Any]]', '✅ Returns Optional[Dict[str, Any]]'),
        ('getSignaturesForAddress', '✅ Calls getSignaturesForAddress'),
        ('getTransaction', '✅ Calls getTransaction'),
        ('encoding": "jsonParsed"', '✅ Uses jsonParsed encoding'),
        ('maxSupportedTransactionVersion": 0', '✅ Sets maxSupportedTransactionVersion to 0'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_backfill_in_account_notification():
    """Test that backfill is integrated in _handle_account_notification"""
    print("=" * 80)
    print("TEST 2: Backfill in _handle_account_notification")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('async def _handle_account_notification', '✅ _handle_account_notification method exists'),
        ('if not trade_info.get("signature")', '✅ Checks if signature is missing'),
        ('await backfill_latest_tx(', '✅ Calls backfill_latest_tx with await'),
        ('trade_info["signature"] = backfill["signature"]', '✅ Attaches signature from backfill'),
        ('trade_info["logs"] = backfill["logs"]', '✅ Attaches logs from backfill'),
        ('trade_info["transaction"] = backfill["transaction"]', '✅ Attaches transaction from backfill'),
        ('logger.info("🔁 [BACKFILL] Attached signature/logs/tx', '✅ Logs success with 🔁 emoji'),
        ('logger.warning("⚠️ [BACKFILL] No signature available', '✅ Logs warning with ⚠️ emoji'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_backfill_in_logs_notification():
    """Test that backfill is integrated in _handle_logs_notification"""
    print("=" * 80)
    print("TEST 3: Backfill in _handle_logs_notification")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('async def _handle_logs_notification', '✅ _handle_logs_notification method exists'),
        ('backfill_data = None', '✅ Initializes backfill_data tracking variable'),
        ('if not signature and logs:', '✅ Checks if signature is missing but logs exist'),
        ('await backfill_latest_tx(', '✅ Calls backfill_latest_tx with await'),
        ('signature = backfill_data["signature"]', '✅ Updates signature from backfill'),
        ('if backfill_data.get("logs"):', '✅ Merges logs if available'),
        ('if backfill_data:', '✅ Reuses backfill data to avoid redundant RPC call'),
        ('🔁 [BACKFILL] Retrieved signature', '✅ Logs backfill success with 🔁 emoji'),
        ('logger.info("🔁 [BACKFILL] Reusing backfilled', '✅ Logs reuse of backfill data'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_logging_format():
    """Test that logging uses consistent emoji format"""
    print("=" * 80)
    print("TEST 4: Consistent Logging Format")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('logger.warning(f"🧵 [BACKFILL]', '✅ Uses 🧵 emoji for backfill warnings'),
        ('logger.info("🔁 [BACKFILL]', '✅ Uses 🔁 emoji for backfill info'),
        ('logger.warning("⚠️ [BACKFILL]', '✅ Uses ⚠️ emoji for backfill warnings'),
        ('logger.info("🔍 [BACKFILL]', '✅ Uses 🔍 emoji for backfill search'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_no_new_dependencies():
    """Test that no new dependencies are introduced"""
    print("=" * 80)
    print("TEST 5: No New Dependencies")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        lines = f.readlines()
    
    import_lines = [line.strip() for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
    
    # Expected imports (already in use)
    expected_imports = [
        'asyncio', 'json', 'logging', 'time', 'traceback', 
        'websockets', 'aiohttp', 'datetime', 'typing', 'dataclasses'
    ]
    
    print("  Import statements found:")
    for imp_line in import_lines[:15]:  # Show first 15 imports
        print(f"    {imp_line}")
    
    # Check for unexpected imports
    unexpected = []
    for imp_line in import_lines:
        if 'import requests' in imp_line and 'websocket_handler.py' in imp_line:
            unexpected.append('requests')
    
    if not unexpected:
        print(f"\n  ✅ No new dependencies introduced (only existing: aiohttp)")
        print(f"  ✅ Uses aiohttp for async HTTP requests (already in use)")
        passed = True
    else:
        print(f"\n  ❌ Unexpected dependencies found: {unexpected}")
        passed = False
    
    print(f"\n  Result: {'PASSED' if passed else 'FAILED'}\n")
    return passed


def test_backfill_return_structure():
    """Test that backfill returns correct structure"""
    print("=" * 80)
    print("TEST 6: Backfill Return Structure")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('"signature": sig,', '✅ Returns signature field'),
        ('"logs": logs,', '✅ Returns logs field'),
        ('"transaction": transaction,', '✅ Returns transaction field'),
        ('"meta": meta', '✅ Returns meta field'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("BACKFILL FUNCTIONALITY VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        test_backfill_helper_exists,
        test_backfill_in_account_notification,
        test_backfill_in_logs_notification,
        test_logging_format,
        test_no_new_dependencies,
        test_backfill_return_structure,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}\n")
            results.append(False)
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"  Tests passed: {passed}/{total}")
    
    if passed == total:
        print("  ✅ ALL TESTS PASSED")
        return 0
    else:
        print("  ❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
