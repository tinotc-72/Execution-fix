#!/usr/bin/env python3
"""
Test Jupiter routing implementation in maybe_execute.
Validates:
1. Jupiter route when dex=="jupiter" and use_universal_cloner==False
2. Jupiter detection from logs/meta when dex=="unknown"
3. Fallback to direct_copy on Jupiter build failure
"""

import sys
import re


def test_jupiter_routing_exists():
    """Test that Jupiter routing logic exists"""
    print("=" * 80)
    print("TEST 1: Jupiter Routing Logic Exists")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'if dex == "jupiter" and not prefer_clone:', "Checks for jupiter with no clone preference"),
        (r'🧭 \[COORDINATOR\] Route=jupiter', "Logs Jupiter route"),
        (r'jupiter_build_and_sign', "Calls jupiter_build_and_sign"),
        (r'❌ \[JUPITER\] build error:', "Logs Jupiter build errors"),
        (r'⚠️ Jupiter build failed — falling back to direct_copy', "Logs fallback to direct_copy"),
        (r'return await execute_direct_copy', "Falls back to direct_copy"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, content):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_jupiter_detection_from_logs():
    """Test Jupiter detection from logs when dex is unknown"""
    print("\n" + "=" * 80)
    print("TEST 2: Jupiter Detection from Logs")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'if dex == "unknown":', "Checks for unknown dex"),
        (r'logs = trade_info\.get\("logs", \[\]\)', "Gets logs from trade_info"),
        (r'meta = trade_info\.get\("meta", \{\}\)', "Gets meta from trade_info"),
        (r'JUP6.*in log_text', "Checks for JUP6 in logs"),
        (r'JUP6.*in meta_str', "Checks for JUP6 in meta"),
        (r'dex = "jupiter"', "Sets dex to jupiter when detected"),
        (r'🧭 \[COORDINATOR\] Detected Jupiter from logs', "Logs Jupiter detection from logs"),
        (r'🧭 \[COORDINATOR\] Detected Jupiter from meta', "Logs Jupiter detection from meta"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, content):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_build_and_sign_function():
    """Test that build_and_sign exists in Jupiter executor"""
    print("\n" + "=" * 80)
    print("TEST 3: Jupiter build_and_sign Function")
    print("=" * 80)
    
    try:
        with open('mev_jupiter_executor.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("  ❌ mev_jupiter_executor.py not found")
        return False
    
    checks = [
        (r'def build_and_sign\(', "build_and_sign function exists"),
        (r'trade_info.*rpc.*keypair', "Has correct parameters"),
        (r'token_mint = trade_info\.get\("token_mint"\)', "Extracts token_mint from trade_info"),
        (r'amount_sol = trade_info\.get\("amount_sol"', "Extracts amount_sol from trade_info"),
        (r'return build_buy_tx', "Calls build_buy_tx"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, content):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_jupiter_before_meteora():
    """Test that Jupiter routing comes before Meteora routing"""
    print("\n" + "=" * 80)
    print("TEST 4: Jupiter Route Priority")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Find positions of Jupiter and Meteora routing
    jupiter_match = re.search(r'if dex == "jupiter" and not prefer_clone:', content)
    meteora_match = re.search(r'if dex == "meteora":', content)
    
    if not jupiter_match:
        print("  ❌ Jupiter routing not found")
        return False
    
    if not meteora_match:
        print("  ❌ Meteora routing not found")
        return False
    
    jupiter_pos = jupiter_match.start()
    meteora_pos = meteora_match.start()
    
    if jupiter_pos < meteora_pos:
        print(f"  ✅ Jupiter routing (pos {jupiter_pos}) comes before Meteora (pos {meteora_pos})")
        return True
    else:
        print(f"  ❌ Jupiter routing (pos {jupiter_pos}) should come before Meteora (pos {meteora_pos})")
        return False


def test_import_statement():
    """Test that Jupiter executor is imported correctly"""
    print("\n" + "=" * 80)
    print("TEST 5: Jupiter Import Statement")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Check for import inside the Jupiter routing block
    import_pattern = r'from mev_jupiter_executor import build_and_sign as jupiter_build_and_sign'
    
    if re.search(import_pattern, content):
        print("  ✅ Jupiter build_and_sign is imported correctly")
        return True
    else:
        print("  ❌ Jupiter build_and_sign import not found")
        return False


def main():
    """Run all tests"""
    print("\n🚀 Testing Jupiter Routing Implementation")
    print("=" * 80)
    
    tests = [
        ("Jupiter Routing Exists", test_jupiter_routing_exists),
        ("Jupiter Detection from Logs", test_jupiter_detection_from_logs),
        ("build_and_sign Function", test_build_and_sign_function),
        ("Jupiter Route Priority", test_jupiter_before_meteora),
        ("Jupiter Import Statement", test_import_statement),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  The Jupiter routing implementation includes:")
        print("  ✅ Jupiter route when dex=='jupiter' and use_universal_cloner==False")
        print("  ✅ Jupiter detection from logs/meta when dex=='unknown'")
        print("  ✅ build_and_sign function in Jupiter executor")
        print("  ✅ Fallback to direct_copy on Jupiter build failure")
        print("  ✅ Jupiter routing has priority over Meteora")
        return 0
    else:
        print(f"\n  ❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
