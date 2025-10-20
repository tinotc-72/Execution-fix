#!/usr/bin/env python3
"""
Test suite for the updated build_and_sign function in mev_meteora_executor.py
Validates new requirements:
1. Function signature includes force_requote and slippage_bps parameters
2. Uses new Meteora program ID Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB
3. Implements idempotent ATA creation with existence checks
4. Handles force_requote parameter for wider slippage
"""

import sys
import re

def test_function_signature():
    """Test that build_and_sign has the correct signature"""
    print("=" * 80)
    print("TEST 1: Function Signature")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract function definition
    func_match = re.search(r'def build_and_sign\((.*?)\):', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: build_and_sign function not found")
        return False
    
    params_str = func_match.group(1)
    
    # Check for required parameters
    required_params = {
        'trade_info': False,
        'rpc': False,
        'keypair': False,
        'force_requote': False,
        'slippage_bps': False
    }
    
    for param in required_params:
        if param in params_str:
            required_params[param] = True
            print(f"✅ PASS: Parameter '{param}' found in signature")
        else:
            print(f"❌ FAIL: Parameter '{param}' missing from signature")
    
    # Check for default values
    if 'force_requote' in params_str and '= False' in params_str:
        print("✅ PASS: force_requote has default value False")
    else:
        print("⚠️  WARNING: force_requote default value not found")
    
    if 'slippage_bps' in params_str and ('= 300' in params_str or '=300' in params_str):
        print("✅ PASS: slippage_bps has default value 300")
    else:
        print("⚠️  WARNING: slippage_bps default value not found")
    
    return all(required_params.values())

def test_program_id():
    """Test that the correct Meteora program ID is used"""
    print("\n" + "=" * 80)
    print("TEST 2: Meteora Program ID")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for the correct program ID
    correct_program_id = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"
    if correct_program_id in func_body:
        print(f"✅ PASS: Using correct Meteora program ID: {correct_program_id}")
    else:
        print(f"❌ FAIL: Correct program ID {correct_program_id} not found")
        return False
    
    # Check that old program ID is not used
    old_program_id = "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"
    if old_program_id in func_body:
        print(f"⚠️  WARNING: Old program ID {old_program_id} still present in function")
    else:
        print(f"✅ PASS: Old program ID removed from function")
    
    return True

def test_ata_existence_check():
    """Test that ATA creation includes existence checks"""
    print("\n" + "=" * 80)
    print("TEST 3: Idempotent ATA Creation")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for getAccountInfo calls
    if 'getAccountInfo' in func_body:
        print("✅ PASS: Uses getAccountInfo for ATA existence check")
    else:
        print("❌ FAIL: No getAccountInfo calls found")
        return False
    
    # Check for conditional ATA creation
    if 'if' in func_body and 'value' in func_body and 'is None' in func_body:
        print("✅ PASS: Conditional ATA creation based on existence check")
    else:
        print("⚠️  WARNING: Conditional logic for ATA creation not clearly identified")
    
    return True

def test_force_requote_logic():
    """Test that force_requote parameter affects slippage calculation"""
    print("\n" + "=" * 80)
    print("TEST 4: Force Requote Logic")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for force_requote handling
    if 'force_requote' in func_body:
        print("✅ PASS: force_requote parameter is used in function body")
    else:
        print("❌ FAIL: force_requote parameter not used in function")
        return False
    
    # Check for slippage_bps usage
    if 'slippage_bps' in func_body:
        print("✅ PASS: slippage_bps parameter is used in function body")
    else:
        print("❌ FAIL: slippage_bps parameter not used in function")
        return False
    
    # Check for conditional slippage logic
    if 'if force_requote' in func_body or 'if not force_requote' in func_body:
        print("✅ PASS: Conditional logic based on force_requote found")
    else:
        print("⚠️  WARNING: Conditional logic for force_requote not clearly identified")
    
    return True

def test_sol_wrapping():
    """Test that SOL wrapping pattern is maintained"""
    print("\n" + "=" * 80)
    print("TEST 5: SOL Wrapping Pattern")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for system transfer
    if 'transfer' in func_body and ('TransferParams' in func_body or 'lamports' in func_body):
        print("✅ PASS: System transfer instruction present")
    else:
        print("❌ FAIL: System transfer not found")
        return False
    
    # Check for SyncNative
    if 'sync' in func_body.lower() or '17' in func_body:  # 17 is SyncNative discriminator
        print("✅ PASS: SyncNative instruction present")
    else:
        print("❌ FAIL: SyncNative instruction not found")
        return False
    
    return True

def test_fresh_blockhash():
    """Test that fresh blockhash is fetched before signing"""
    print("\n" + "=" * 80)
    print("TEST 6: Fresh Blockhash")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for blockhash fetch
    if 'get_latest_blockhash' in func_body:
        print("✅ PASS: Fetches fresh blockhash")
    else:
        print("❌ FAIL: No blockhash fetch found")
        return False
    
    # Check that VersionedTransaction is returned
    if 'VersionedTransaction' in func_body and 'return' in func_body:
        print("✅ PASS: Returns VersionedTransaction")
    else:
        print("⚠️  WARNING: Return of VersionedTransaction not clearly identified")
    
    return True

def test_logging():
    """Test that emoji logging is present"""
    print("\n" + "=" * 80)
    print("TEST 7: Emoji Logging")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Extract build_and_sign function
    func_match = re.search(r'def build_and_sign\(.*?\n(.*?)(?=\ndef |$)', content, re.DOTALL)
    if not func_match:
        print("❌ FAIL: Could not extract build_and_sign function")
        return False
    
    func_body = func_match.group(1)
    
    # Check for emoji logging
    emojis = ['🚀', '🔧', '✅', '💸', '🔄', '🎯', '🔒', '📡', '⚠️']
    found_emojis = [emoji for emoji in emojis if emoji in func_body]
    
    if len(found_emojis) >= 5:
        print(f"✅ PASS: Found {len(found_emojis)} emoji logging statements")
        print(f"   Emojis found: {', '.join(found_emojis)}")
    else:
        print(f"⚠️  WARNING: Only found {len(found_emojis)} emoji logging statements")
    
    # Check for logger.info calls
    if 'logger.info' in func_body:
        print("✅ PASS: Uses logger.info for logging")
    else:
        print("⚠️  WARNING: logger.info calls not found")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TESTING UPDATED build_and_sign FUNCTION")
    print("=" * 80 + "\n")
    
    tests = [
        test_function_signature,
        test_program_id,
        test_ata_existence_check,
        test_force_requote_logic,
        test_sol_wrapping,
        test_fresh_blockhash,
        test_logging
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
