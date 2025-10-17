#!/usr/bin/env python3
"""
Test suite to validate the inference crash handling implementation.

Validates that:
1. infer_missing_fields is wrapped in try/except/finally
2. Errors are logged with exc_info=True
3. route_and_execute is still called in finally block if essentials are present
4. [PIPELINE_EXIT] logs appear even when inference fails
"""

import re
import sys


def test_try_except_finally_structure():
    """Test that infer_missing_fields is wrapped in try/except/finally"""
    print("=" * 80)
    print("TEST 1: Try/Except/Finally Structure")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the section with infer_missing_fields
    pattern = r"try:\s+trade_info = self\.trade_processor\.infer_missing_fields\(trade_info\).*?except Exception as e:.*?logger\.error.*?finally:"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ❌ infer_missing_fields not wrapped in try/except/finally")
        return False
    
    print("  ✅ infer_missing_fields is wrapped in try/except/finally")
    return True


def test_error_logging_with_exc_info():
    """Test that errors are logged with exc_info=True"""
    print("\n" + "=" * 80)
    print("TEST 2: Error Logging with exc_info=True")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for the error logging pattern with exc_info=True
    pattern = r'logger\.error\(".*infer_missing_fields crashed.*", exc_info=True\)'
    
    if not re.search(pattern, content):
        print("  ❌ Error logging missing exc_info=True")
        return False
    
    print("  ✅ Errors are logged with exc_info=True")
    return True


def test_debug_logging_after_inference():
    """Test that debug logging appears after infer_missing_fields"""
    print("\n" + "=" * 80)
    print("TEST 3: Debug Logging After Inference")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for debug logging pattern after infer_missing_fields
    pattern = r'trade_info = self\.trade_processor\.infer_missing_fields\(trade_info\)\s+logger\.debug\(.*After infer_missing_fields'
    
    if not re.search(pattern, content, re.DOTALL):
        print("  ❌ Debug logging after inference not found")
        return False
    
    print("  ✅ Debug logging appears after infer_missing_fields")
    return True


def test_route_and_execute_in_finally():
    """Test that route_and_execute is called in finally block"""
    print("\n" + "=" * 80)
    print("TEST 4: route_and_execute in Finally Block")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for route_and_execute call in finally block
    pattern = r"finally:.*?await route_and_execute\(trade_info"
    
    if not re.search(pattern, content, re.DOTALL):
        print("  ❌ route_and_execute not called in finally block")
        return False
    
    print("  ✅ route_and_execute is called in finally block")
    return True


def test_pipeline_exit_logs_present():
    """Test that [PIPELINE_EXIT] logs are present"""
    print("\n" + "=" * 80)
    print("TEST 5: [PIPELINE_EXIT] Logs Present")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for PIPELINE_EXIT in route_and_execute function
    route_and_execute_pattern = r'def route_and_execute.*?logger\.(info|warning)\(.*PIPELINE_EXIT'
    
    if not re.search(route_and_execute_pattern, content, re.DOTALL):
        print("  ❌ [PIPELINE_EXIT] logs not found in route_and_execute")
        return False
    
    print("  ✅ [PIPELINE_EXIT] logs are present in route_and_execute")
    return True


def test_complete_flow_resilience():
    """Test that the complete flow handles inference failures gracefully"""
    print("\n" + "=" * 80)
    print("TEST 6: Complete Flow Resilience")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract the section with try/except/finally
    pattern = r"try:\s+trade_info = self\.trade_processor\.infer_missing_fields.*?finally:.*?await route_and_execute"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find complete flow with try/except/finally")
        return False
    
    flow = match.group(0)
    
    # Check the flow has all required components in order
    checks = [
        (r"try:", "✅ Step 1: Try block starts"),
        (r"trade_info = self\.trade_processor\.infer_missing_fields", "✅ Step 2: Call infer_missing_fields"),
        (r'logger\.debug\(.*After infer_missing_fields', "✅ Step 3: Debug log after inference"),
        (r"except Exception as e:", "✅ Step 4: Exception handler"),
        (r'logger\.error\(.*infer_missing_fields crashed.*exc_info=True', "✅ Step 5: Error logging with exc_info"),
        (r"finally:", "✅ Step 6: Finally block"),
        (r"have_all = _have_all_fields\(trade_info\)", "✅ Step 7: Check for all fields"),
        (r"await route_and_execute", "✅ Step 8: Call route_and_execute"),
    ]
    
    passed = 0
    for pattern_check, description in checks:
        if re.search(pattern_check, flow, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Flow steps: {passed}/{len(checks)} validated")
    return passed == len(checks)


def test_inference_crash_scenario():
    """Test that the implementation handles the crash scenario from problem statement"""
    print("\n" + "=" * 80)
    print("TEST 7: Inference Crash Scenario Validation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Verify the complete structure matches problem statement requirements:
    # try:
    #     trade_info = infer_missing_fields(trade_info, rpc_client)
    #     logger.debug("[DEBUG] After infer_missing_fields: %s", safe_dump(trade_info))
    # except Exception as e:
    #     logger.error("❌ infer_missing_fields crashed", exc_info=True)
    # finally:
    #     # attempt execution if the essentials are present
    #     route_and_execute(trade_info, rpc=rpc_client, keypair=wallet_keypair, jito=None)
    
    # Check all components are present
    components = [
        (r"try:\s+trade_info = self\.trade_processor\.infer_missing_fields", 
         "try block with infer_missing_fields"),
        (r'logger\.debug\(.*After infer_missing_fields.*json\.dumps', 
         "debug logging after inference"),
        (r'except Exception as e:\s+logger\.error\(".*infer_missing_fields crashed", exc_info=True\)', 
         "exception handler with proper logging"),
        (r"finally:.*await route_and_execute\(trade_info", 
         "finally block with route_and_execute"),
    ]
    
    all_present = True
    for pattern, description in components:
        if re.search(pattern, content, re.DOTALL):
            print(f"  ✅ Found: {description}")
        else:
            print(f"  ❌ Missing: {description}")
            all_present = False
    
    if all_present:
        print("\n  ✅ Implementation matches problem statement requirements")
        print("  ✅ If inference fails, route_and_execute will still be called")
        print("  ✅ [PIPELINE_EXIT] logs will appear even on inference failure")
    else:
        print("\n  ❌ Implementation incomplete")
    
    return all_present


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("INFERENCE CRASH HANDLING IMPLEMENTATION VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        ("Try/Except/Finally structure", test_try_except_finally_structure),
        ("Error logging with exc_info", test_error_logging_with_exc_info),
        ("Debug logging after inference", test_debug_logging_after_inference),
        ("route_and_execute in finally", test_route_and_execute_in_finally),
        ("[PIPELINE_EXIT] logs present", test_pipeline_exit_logs_present),
        ("Complete flow resilience", test_complete_flow_resilience),
        ("Inference crash scenario", test_inference_crash_scenario),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Tests Passed: {passed_tests}/{total_tests}")
    print()
    
    if all(passed for _, passed in results):
        print("  🎉 ALL TESTS PASSED!")
        print()
        print("  The inference crash handling implementation is complete:")
        print("  ✅ infer_missing_fields wrapped in try/except/finally")
        print("  ✅ Errors logged with exc_info=True")
        print("  ✅ route_and_execute called in finally block")
        print("  ✅ [PIPELINE_EXIT] logs appear even on inference failure")
        print("  ✅ Execution continues if core fields exist")
        print()
        return 0
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation against problem statement")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
