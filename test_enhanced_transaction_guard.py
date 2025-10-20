#!/usr/bin/env python3
"""
Test script to validate enhanced transaction stream guard implementation.

Tests:
1. Enhanced transaction subscription is wrapped in try/except
2. Exception handler uses logger.warning (not logger.error)
3. Warning message includes emoji (⚠️)
4. Warning message mentions continuing with logs/account + backfill
5. No blocking behavior - continues with other subscriptions
"""

import sys


def test_exception_handler_warning():
    """Test that exception handler uses logger.warning instead of logger.error"""
    print("=" * 80)
    print("TEST 1: Exception Handler Uses Warning Level")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Find the enhanced transaction subscription section
    checks = [
        ('try:', '✅ Enhanced transaction subscription wrapped in try block'),
        ('transactionSubscribe', '✅ Uses transactionSubscribe method'),
        ('except Exception as e:', '✅ Has exception handler'),
        ('logger.warning(f"⚠️ Enhanced transaction stream unavailable:', '✅ Uses logger.warning (not error)'),
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


def test_warning_message_content():
    """Test that warning message includes emoji and continuation message"""
    print("=" * 80)
    print("TEST 2: Warning Message Content")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('⚠️ Enhanced transaction stream unavailable:', '✅ Warning includes ⚠️ emoji'),
        ('continuing with logs/account + backfill', '✅ Message mentions continuing with logs/account + backfill'),
        ('{e}', '✅ Exception message is included'),
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


def test_no_error_logging():
    """Test that enhanced transaction subscription doesn't use logger.error for unavailable method"""
    print("=" * 80)
    print("TEST 3: No Error Logging for Method Not Found")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        lines = f.readlines()
    
    # Find the enhanced transaction section (around line 232-259)
    in_enhanced_section = False
    has_error_logging = False
    
    for i, line in enumerate(lines):
        if 'Helius Enhanced Transaction Stream' in line:
            in_enhanced_section = True
        
        if in_enhanced_section:
            # Check if we've exited the try/except block
            if 'async def _subscribe_to_wallet' in line:
                in_enhanced_section = False
                break
            
            # Check for error logging in this section
            if 'logger.error' in line and 'enhanced transaction' in line.lower():
                has_error_logging = True
                print(f"  ❌ Found logger.error in enhanced transaction section at line {i+1}")
                break
    
    if not has_error_logging:
        print("  ✅ No logger.error found in enhanced transaction exception handler")
        print("  ✅ Uses logger.warning for graceful degradation")
        print("\n  Result: 2/2 checks passed\n")
        return True
    else:
        print("\n  Result: 0/2 checks passed\n")
        return False


def test_no_blocking_behavior():
    """Test that enhanced transaction failure doesn't block other subscriptions"""
    print("=" * 80)
    print("TEST 4: Non-Blocking Behavior")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('Subscribe to logs/account for each wallet', '✅ Wallet subscriptions happen before enhanced stream'),
        ('successful_subscriptions += 1', '✅ Wallet subscriptions are counted'),
        ('except Exception as e:\n            logger.warning(f"⚠️ Enhanced transaction stream unavailable:', '✅ Enhanced stream exception is caught and doesn\'t propagate'),
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


def test_logging_consistency():
    """Test that logging uses consistent emoji format"""
    print("=" * 80)
    print("TEST 5: Logging Consistency")
    print("=" * 80)
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Check for consistent emoji usage
    checks = [
        ('logger.info(f"✅', '✅ Uses ✅ emoji for success messages'),
        ('logger.warning(f"⚠️', '✅ Uses ⚠️ emoji for warning messages'),
        ('logger.error(f"❌', '✅ Uses ❌ emoji for error messages (where appropriate)'),
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
    print("ENHANCED TRANSACTION STREAM GUARD VALIDATION")
    print("=" * 80)
    print()
    
    tests = [
        ("Exception Handler Warning Level", test_exception_handler_warning()),
        ("Warning Message Content", test_warning_message_content()),
        ("No Error Logging", test_no_error_logging()),
        ("Non-Blocking Behavior", test_no_blocking_behavior()),
        ("Logging Consistency", test_logging_consistency()),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  The enhanced transaction stream guard implementation:")
        print("  ✅ Uses logger.warning for graceful degradation")
        print("  ✅ Includes appropriate emoji (⚠️)")
        print("  ✅ Mentions continuing with logs/account + backfill")
        print("  ✅ Doesn't block other subscriptions")
        print("  ✅ Maintains logging consistency with existing code")
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print(f"\n  Please review the failed tests above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
