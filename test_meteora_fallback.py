#!/usr/bin/env python3
"""
Test for Meteora fallback to direct_copy implementation.

Validates that when Meteora executor fails:
1. Logs with proper emojis (🧭, ❌, ⚠️)
2. Immediately tries direct_copy as fallback
3. Maintains consistent logging format
"""

import re

def test_meteora_fallback_logic():
    """Test that Meteora branch has fallback to direct_copy"""
    print("=" * 80)
    print("TEST: Meteora Fallback to Direct Copy")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'elif label == "meteora":',
            '✅ Checks for meteora in executor routing'
        ),
        (
            r'self\.logger\.info\("🧭 \[COORDINATOR\] Route=meteora → trying Meteora executor"\)',
            '✅ Logs with 🧭 emoji when Meteora route is selected'
        ),
        (
            r'try:.*result = await self\._execute_meteora_buy\(',
            '✅ Wraps Meteora executor call in try/except'
        ),
        (
            r'except Exception as e:.*self\.logger\.error\(f"❌ \[METEORA\] Build failed: \{e\}"\)',
            '✅ Catches Meteora exceptions and logs with ❌ emoji'
        ),
        (
            r'if not result or not \(result\.get\("ok"\) or result\.get\("success"\)\):',
            '✅ Checks if Meteora result is None or unsuccessful'
        ),
        (
            r'self\.logger\.warning\("⚠️ \[COORDINATOR\] Meteora build returned no tx — falling back to direct_copy"\)',
            '✅ Logs fallback warning with ⚠️ emoji'
        ),
        (
            r'result = await self\._execute_direct_copy_buy\(',
            '✅ Calls direct_copy as fallback when Meteora fails'
        ),
        (
            r'except Exception as e:.*self\.logger\.error\(f"❌ \[COORDINATOR\] Direct copy fallback also failed: \{e\}"\)',
            '✅ Catches direct_copy fallback exceptions with ❌ emoji'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)

def test_logging_format():
    """Test that logging follows consistent emoji format"""
    print("=" * 80)
    print("TEST: Logging Format Consistency")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    # Extract the meteora section
    meteora_start = code.find('elif label == "meteora":')
    if meteora_start == -1:
        print("  ❌ Could not find meteora section")
        return False
    
    # Get the meteora section (next ~20 lines)
    meteora_section = code[meteora_start:meteora_start + 1500]
    
    tests = [
        (r'🧭 \[COORDINATOR\]', '✅ Uses 🧭 emoji for route selection'),
        (r'❌ \[METEORA\]', '✅ Uses ❌ emoji for Meteora errors'),
        (r'⚠️ \[COORDINATOR\]', '✅ Uses ⚠️ emoji for fallback warning'),
        (r'❌ \[COORDINATOR\]', '✅ Uses ❌ emoji for fallback errors'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, meteora_section):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)

def test_route_map_unchanged():
    """Test that ROUTE_MAP is unchanged"""
    print("=" * 80)
    print("TEST: Route Map Unchanged")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    # Check that ROUTE_MAP still has meteora route
    meteora_route_pattern = r'"meteora":\s*\["meteora",\s*"raydium",\s*"jupiter",\s*"direct_copy"\]'
    
    if re.search(meteora_route_pattern, code):
        print("  ✅ ROUTE_MAP for meteora is unchanged")
        print("  ✅ Route prioritizes meteora executor first")
        print("\n  Result: 2/2 checks passed\n")
        return True
    else:
        print("  ❌ ROUTE_MAP for meteora has changed - NOT FOUND")
        print("\n  Result: 0/2 checks passed\n")
        return False

def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("METEORA FALLBACK TO DIRECT_COPY TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("Meteora Fallback Logic", test_meteora_fallback_logic()),
        ("Logging Format Consistency", test_logging_format()),
        ("Route Map Unchanged", test_route_map_unchanged()),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  Implementation verified:")
        print("  ✅ Meteora branch tries executor first")
        print("  ✅ Falls back to direct_copy if Meteora fails")
        print("  ✅ Logs with proper emojis (🧭, ❌, ⚠️)")
        print("  ✅ ROUTE_MAP remains unchanged")
        print("  ✅ Consistent logging format")
        print("\n" + "=" * 80)
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
