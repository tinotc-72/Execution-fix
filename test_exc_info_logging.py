#!/usr/bin/env python3
"""
Test to verify exc_info=True is used in all error logging in maybe_execute.
This ensures better debugging with full stack traces.
"""

import re
import sys


def test_exc_info_in_error_logs():
    """Test that error logs in exception handlers use exc_info=True"""
    print("=" * 80)
    print("TEST: exc_info=True in Error Logging")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract maybe_execute function
    match = re.search(r'async def maybe_execute.*?(?=\n(?:async def|def|class|\Z))', content, re.DOTALL)
    if not match:
        print("❌ FAIL: Could not find maybe_execute function")
        return False
    
    maybe_execute_content = match.group(0)
    
    # Check specific exception handlers that should have exc_info=True
    checks = [
        (r'except Exception as e:.*?logger\.error\(f"❌ \[EXECUTION\] submission failed:.*?exc_info=True', 
         "try_submit exception handler"),
        (r'except Exception as e:.*?logger\.error\(f"❌ \[DIRECT_COPY\] Clone failed:.*?exc_info=True', 
         "direct_copy exception handler"),
        (r'except Exception as e:.*?logger\.error\(f"❌ \[METEORA\] build error:.*?exc_info=True', 
         "Meteora build exception handler"),
        (r'except Exception as e:.*?logger\.error\(f"❌ \[JUPITER\] build error:.*?exc_info=True', 
         "Jupiter build exception handler (meteora path)"),
    ]
    
    print("\nChecking exception handlers with exc_info=True:\n")
    
    all_present = True
    for pattern, description in checks:
        if re.search(pattern, maybe_execute_content, re.DOTALL):
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - missing exc_info=True")
            all_present = False
    
    print()
    if all_present:
        print("✅ PASS: All exception handlers use exc_info=True for better debugging")
        return True
    else:
        print("❌ FAIL: Some exception handlers missing exc_info=True")
        return False


def test_fallback_logging():
    """Test that fallback paths have clear warning logging"""
    print("\n" + "=" * 80)
    print("TEST: Clear Fallback Logging")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract maybe_execute function
    match = re.search(r'async def maybe_execute.*?(?=\n(?:async def|def|class|\Z))', content, re.DOTALL)
    if not match:
        print("❌ FAIL: Could not find maybe_execute function")
        return False
    
    maybe_execute_content = match.group(0)
    
    fallback_warnings = [
        ("⚠️ Meteora build failed — trying Jupiter", "Meteora → Jupiter fallback"),
        ("⚠️ Builders failed — falling back to direct_copy", "Builder → direct_copy fallback"),
        ("⚠️ No builder available — falling back to direct_copy", "No builder → direct_copy"),
    ]
    
    print("\nChecking fallback warning messages:\n")
    
    all_present = True
    for warning_text, description in fallback_warnings:
        if warning_text in maybe_execute_content:
            print(f"  ✅ {description}: '{warning_text}'")
        else:
            print(f"  ❌ {description}: Missing")
            all_present = False
    
    print()
    if all_present:
        print("✅ PASS: All fallback paths have clear warning logging")
        return True
    else:
        print("❌ FAIL: Some fallback warnings are missing")
        return False


def main():
    """Run all tests"""
    print("\n🚀 Testing Logging Enhancements in maybe_execute")
    print("=" * 80)
    
    tests = [
        ("exc_info in Error Logs", test_exc_info_in_error_logs),
        ("Clear Fallback Logging", test_fallback_logging),
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
        print("\n  Logging improvements implemented:")
        print("  ✅ All error logs use exc_info=True for stack traces")
        print("  ✅ Clear fallback logging with emoji warnings")
        print("  ✅ Visible execution path for debugging")
        return 0
    else:
        print(f"\n  ❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
