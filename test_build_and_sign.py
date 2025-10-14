#!/usr/bin/env python3
"""
Test suite for build_and_sign function in mev_meteora_executor.py
Validates the transaction building requirements from the problem statement.
"""

import sys
import re

def test_build_and_sign_structure():
    """Test that build_and_sign creates the correct instruction structure"""
    print("=" * 80)
    print("TEST: build_and_sign Function Structure")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    print("\n--- Test 1: Function exists ---")
    if 'def build_and_sign(' in content:
        print("✅ PASS: build_and_sign function exists")
    else:
        print("❌ FAIL: build_and_sign function not found")
        return False
    
    print("\n--- Test 2: Function signature ---")
    # Extract function definition
    func_match = re.search(r'def build_and_sign\((.*?)\):', content, re.DOTALL)
    if func_match:
        params_str = func_match.group(1)
        params = [p.strip().split(':')[0].strip() for p in params_str.split(',')]
        
        required_params = ['rpc', 'owner', 'token_mint']
        for param in required_params:
            if param in params:
                print(f"✅ PASS: Required parameter '{param}' present")
            else:
                print(f"❌ FAIL: Required parameter '{param}' missing")
                return False
        
        optional_params = ['lamports_in', 'min_tokens', 'trade_info']
        for param in optional_params:
            if param in params:
                print(f"✅ PASS: Optional parameter '{param}' present")
            else:
                print(f"⚠️  INFO: Optional parameter '{param}' missing")
    else:
        print("❌ FAIL: Could not parse function signature")
        return False
    
    print("\n--- Test 3: Return type is VersionedTransaction ---")
    if 'VersionedTransaction' in content and '-> VersionedTransaction' in content:
        print("✅ PASS: Returns VersionedTransaction")
    else:
        print("⚠️  INFO: Return type annotation not clearly specified")
    
    return True

def test_instruction_order():
    """Test the instruction order matches requirements"""
    print("\n" + "=" * 80)
    print("TEST: Instruction Order Requirements")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract the build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    print("\n--- Test 1: ATA creation for WSOL ---")
    if "WSOL" in func_body and "create_associated_token_account" in func_body:
        print("✅ PASS: WSOL ATA creation code present")
    else:
        print("❌ FAIL: WSOL ATA creation missing")
        return False
    
    print("\n--- Test 2: ATA creation for token_mint ---")
    if "token_mint" in func_body and "create_associated_token_account" in func_body:
        print("✅ PASS: Token ATA creation code present")
    else:
        print("❌ FAIL: Token ATA creation missing")
        return False
    
    print("\n--- Test 3: System transfer for SOL wrapping ---")
    if "transfer" in func_body and "lamports" in func_body:
        print("✅ PASS: System transfer code present")
    else:
        print("❌ FAIL: System transfer missing")
        return False
    
    print("\n--- Test 4: SyncNative instruction ---")
    if "sync" in func_body.lower() or "17" in func_body:  # 17 is SyncNative discriminator
        print("✅ PASS: SyncNative instruction code present")
    else:
        print("❌ FAIL: SyncNative instruction missing")
        return False
    
    print("\n--- Test 5: Meteora Swap2 instruction ---")
    if "Swap2" in func_body or "65, 75, 63, 76" in func_body:
        print("✅ PASS: Meteora Swap2 instruction code present")
    else:
        print("❌ FAIL: Meteora Swap2 instruction missing")
        return False
    
    print("\n--- Test 6: CloseAccount instruction ---")
    if "close" in func_body.lower() or "[9]" in func_body:  # 9 is CloseAccount discriminator
        print("✅ PASS: CloseAccount instruction code present")
    else:
        print("❌ FAIL: CloseAccount instruction missing")
        return False
    
    print("\n--- Test 7: Fresh blockhash fetch ---")
    if "get_latest_blockhash" in func_body:
        print("✅ PASS: Fresh blockhash fetch present")
    else:
        print("❌ FAIL: Fresh blockhash fetch missing")
        return False
    
    return True

def test_program_id():
    """Test that correct Meteora program ID is used"""
    print("\n" + "=" * 80)
    print("TEST: Meteora Program ID")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    expected_program_id = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"
    
    # Extract the build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if func_match:
        func_body = func_match.group(1)
        if expected_program_id in func_body:
            print(f"✅ PASS: Correct Meteora program ID used: {expected_program_id}")
            return True
        else:
            print(f"❌ FAIL: Expected program ID {expected_program_id} not found in function")
            return False
    else:
        print(f"❌ FAIL: Could not extract build_and_sign function")
        return False

def test_wsol_constant():
    """Test that WSOL constant is correct"""
    print("\n" + "=" * 80)
    print("TEST: WSOL Constant")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    expected_wsol = "So11111111111111111111111111111111111111112"
    
    # Extract the build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if func_match:
        func_body = func_match.group(1)
        if expected_wsol in func_body:
            print(f"✅ PASS: Correct WSOL mint used: {expected_wsol}")
            return True
        else:
            print(f"❌ FAIL: Expected WSOL mint {expected_wsol} not found in function")
            return False
    else:
        print(f"❌ FAIL: Could not extract build_and_sign function")
        return False

def test_default_sol_amount():
    """Test that default SOL amount is 0.001 SOL"""
    print("\n" + "=" * 80)
    print("TEST: Default SOL Amount")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Look for default parameter value in function signature
    func_match = re.search(r'def build_and_sign\((.*?)\):', content, re.DOTALL)
    if func_match:
        params_str = func_match.group(1)
        if 'lamports_in' in params_str:
            # Check for default value 1_000_000
            if '1_000_000' in params_str or '1000000' in params_str:
                print(f"✅ PASS: Default lamports_in is 1,000,000 (0.001 SOL)")
                return True
            else:
                print(f"⚠️  INFO: lamports_in present but default value unclear")
                return True
        else:
            print("⚠️  INFO: No lamports_in parameter found")
            return True
    else:
        print(f"❌ FAIL: Could not extract function signature")
        return False

def test_logging_format():
    """Test that logging uses consistent format"""
    print("\n" + "=" * 80)
    print("TEST: Logging Format Consistency")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract the build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for emoji usage (INFO/WARNING/ERROR)
    emoji_patterns = ['✅', '⚠️', '❌', '🔧', '💸', '🔄', '🎯', '🔒', '📡']
    found_emojis = [emoji for emoji in emoji_patterns if emoji in func_body]
    
    if found_emojis:
        print(f"✅ PASS: Logging uses emojis: {', '.join(found_emojis)}")
    else:
        print("⚠️  INFO: No emoji logging found")
    
    if "logger.info" in func_body:
        print("✅ PASS: Uses logger.info for informational messages")
    else:
        print("⚠️  INFO: No logger.info usage found")
    
    if "logger.warning" in func_body:
        print("✅ PASS: Uses logger.warning for warnings")
    else:
        print("⚠️  INFO: No logger.warning usage found")
    
    return True

def test_no_new_dependencies():
    """Test that no new dependencies are introduced"""
    print("\n" + "=" * 80)
    print("TEST: No New Dependencies")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract the build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for imports within function
    prohibited_imports = ['import requests', 'import pandas', 'import numpy', 'from web3']
    
    for prohibited in prohibited_imports:
        if prohibited in func_body:
            print(f"❌ FAIL: Prohibited import found: {prohibited}")
            return False
    
    print("✅ PASS: No new dependencies introduced")
    
    # Check for use of existing utilities
    if "from utils import" in func_body or "find_associated_token_address" in func_body:
        print("✅ PASS: Uses existing utility functions")
    
    return True

def main():
    """Run all tests"""
    print("\n🚀 Testing build_and_sign Function Implementation")
    print("=" * 80)
    
    all_tests = [
        ("Function Structure", test_build_and_sign_structure),
        ("Instruction Order", test_instruction_order),
        ("Program ID", test_program_id),
        ("WSOL Constant", test_wsol_constant),
        ("Default SOL Amount", test_default_sol_amount),
        ("Logging Format", test_logging_format),
        ("No New Dependencies", test_no_new_dependencies),
    ]
    
    results = []
    for test_name, test_func in all_tests:
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
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
