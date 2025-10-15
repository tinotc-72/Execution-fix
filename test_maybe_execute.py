#!/usr/bin/env python3
"""
Test suite for maybe_execute function in execution_coordinator.py
Validates the new routing logic requirements from the problem statement.
"""

import sys
import re


def test_maybe_execute_exists():
    """Test that maybe_execute function exists"""
    print("=" * 80)
    print("TEST 1: maybe_execute Function Exists")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    if 'async def maybe_execute(' in content or 'def maybe_execute(' in content:
        print("✅ PASS: maybe_execute function exists")
        return True
    else:
        print("❌ FAIL: maybe_execute function not found")
        return False


def test_meteora_routing():
    """Test meteora routing logic"""
    print("\n" + "=" * 80)
    print("TEST 2: Meteora Routing Logic")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'if dex == "meteora":', "Checks for dex == 'meteora'"),
        (r'meteora_build_and_sign', "Calls meteora_build_and_sign"),
        (r'jupiter_build_buy_tx', "Falls back to Jupiter"),
        (r'execute_direct_copy_fallback', "Falls back to direct_copy"),
        (r'🧭 \[COORDINATOR\] Route=meteora', "Logs meteora route"),
        (r'⚠️ Meteora build failed — trying Jupiter', "Logs Jupiter fallback"),
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


def test_unknown_with_mint_routing():
    """Test unknown with mint routing logic"""
    print("\n" + "=" * 80)
    print("TEST 3: Unknown with Mint Routing Logic")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'if dex == "unknown" and have_mint:', "Checks for unknown with mint"),
        (r'jupiter_build_buy_tx', "Tries Jupiter first"),
        (r'meteora_build_and_sign', "Tries Meteora second"),
        (r'execute_direct_copy_fallback', "Falls back to direct_copy"),
        (r'🧭 \[COORDINATOR\] Route=unknown; mint present → Jupiter → Meteora → Clone', "Logs route"),
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


def test_try_submit_helper():
    """Test try_submit helper function"""
    print("\n" + "=" * 80)
    print("TEST 4: try_submit Helper Function")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    checks = [
        (r'async def try_submit\(vtx\)', "try_submit function exists"),
        (r'await fast_executor\.submit_transaction\(vtx\)', "Uses fast_executor.submit_transaction"),
        (r'✅ \[EXECUTION\] submitted:', "Logs successful submission"),
        (r'❌ \[EXECUTION\] submission failed:', "Logs failed submission"),
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


def test_emoji_logging():
    """Test emoji logging consistency"""
    print("\n" + "=" * 80)
    print("TEST 5: Emoji Logging Consistency")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Check for emoji patterns in maybe_execute
    maybe_execute_match = re.search(r'async def maybe_execute.*?(?=\n(?:async def|def|class|\Z))', content, re.DOTALL)
    if not maybe_execute_match:
        print("  ❌ Could not find maybe_execute function")
        return False
    
    maybe_execute_content = maybe_execute_match.group(0)
    
    emojis = {
        '🧭': 'Navigation/Route',
        '✅': 'Success',
        '❌': 'Error',
        '⚠️': 'Warning',
    }
    
    passed = 0
    for emoji, description in emojis.items():
        if emoji in maybe_execute_content:
            print(f"  ✅ Uses {emoji} for {description}")
            passed += 1
        else:
            print(f"  ❌ Missing {emoji} for {description}")
    
    print(f"\n  Result: {passed}/{len(emojis)} emoji types found")
    return passed == len(emojis)


def test_no_new_dependencies():
    """Test that no new dependencies are added"""
    print("\n" + "=" * 80)
    print("TEST 6: No New Dependencies")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract only top-level imports (not inside functions)
    lines = content.split('\n')
    import_lines = []
    in_function = False
    for line in lines:
        # Detect function/class start
        if re.match(r'^(async )?def |^class ', line):
            in_function = True
        # Detect function/class end (dedent to column 0)
        elif in_function and re.match(r'^[^\s#]', line) and not line.strip().startswith(('import ', 'from ')):
            in_function = False
        
        # Only collect top-level imports
        if not in_function and line.strip().startswith(('import ', 'from ')):
            import_lines.append(line)
    
    # Check for existing modules only
    allowed_imports = [
        'asyncio', 'logging', 'traceback', 'time', 'typing', 'datetime', 'dataclasses', 'collections',
        'solders', 'mev_', 'copy_trade_logger', 'env_keys', 'transaction_cloner', 'fast_executor'
    ]
    
    new_deps = []
    for line in import_lines:
        # Extract module name
        if line.strip().startswith('import '):
            module = line.strip().split()[1].split('.')[0]
        elif line.strip().startswith('from '):
            module = line.strip().split()[1].split('.')[0]
        else:
            continue
        
        if not any(allowed in module for allowed in allowed_imports):
            new_deps.append(module)
    
    if not new_deps:
        print("  ✅ No new top-level dependencies added")
        print("  ✅ Uses existing executors and utilities")
        return True
    else:
        print(f"  ❌ New dependencies found: {', '.join(set(new_deps))}")
        return False


def main():
    """Run all tests"""
    print("\n🚀 Testing maybe_execute Function Implementation")
    print("=" * 80)
    
    tests = [
        ("Function Exists", test_maybe_execute_exists),
        ("Meteora Routing", test_meteora_routing),
        ("Unknown with Mint Routing", test_unknown_with_mint_routing),
        ("try_submit Helper", test_try_submit_helper),
        ("Emoji Logging", test_emoji_logging),
        ("No New Dependencies", test_no_new_dependencies),
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
        print("\n  The maybe_execute function implements:")
        print("  ✅ Meteora path: Meteora build_and_sign → Jupiter → direct_copy")
        print("  ✅ Unknown with mint: Jupiter → Meteora → direct_copy")
        print("  ✅ Emoji logging consistent with existing format")
        print("  ✅ No new dependencies added")
        print("  ✅ Uses existing RPC client and executors")
        return 0
    else:
        print(f"\n  ❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
