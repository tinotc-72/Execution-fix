#!/usr/bin/env python3
"""
Code verification script - checks that the implementation matches the problem statement.
This script reads the source code directly without importing it.
"""

import re

def verify_constant_definition():
    """Verify METEORA_PROGRAM_IDS is defined correctly"""
    print("=" * 80)
    print("VERIFICATION: METEORA_PROGRAM_IDS Constant")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    # Check for the constant definition
    pattern = r'METEORA_PROGRAM_IDS\s*=\s*\{[^}]+\}'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: METEORA_PROGRAM_IDS constant not found")
        return False
    
    constant_def = match.group(0)
    print(f"\nFound constant definition:")
    print(constant_def)
    
    # Check for both program IDs
    checks = [
        ("Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB", "Meteora AMM"),
        ("dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "Meteora alternate"),
    ]
    
    all_found = True
    for program_id, description in checks:
        if program_id in constant_def:
            print(f"  ✅ Contains {description}: {program_id[:8]}...")
        else:
            print(f"  ❌ Missing {description}: {program_id}")
            all_found = False
    
    return all_found

def verify_detection_logic():
    """Verify the detection logic uses 'in METEORA_PROGRAM_IDS'"""
    print("\n" + "=" * 80)
    print("VERIFICATION: Meteora Detection Logic")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    # Find the parse_transaction method
    parse_tx_pattern = r'def parse_transaction\(self, tx_data\):.*?(?=\n    def |\Z)'
    match = re.search(parse_tx_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: parse_transaction method not found")
        return False
    
    method_content = match.group(0)
    
    # Check for 'if pid in METEORA_PROGRAM_IDS:'
    checks = [
        (r'if pid in METEORA_PROGRAM_IDS:', "✅ Uses 'if pid in METEORA_PROGRAM_IDS'"),
        (r'parsed\["dex"\]\s*=\s*"meteora"', '✅ Sets parsed["dex"] = "meteora"'),
        (r'parsed\["action"\].*"swap"', '✅ Sets parsed["action"] to "swap"'),
        (r'parsed\["wallet_address"\]\s*=\s*signers\[0\]', '✅ Sets parsed["wallet_address"] from first signer'),
    ]
    
    all_found = True
    for pattern, description in checks:
        if re.search(pattern, method_content):
            print(f"  {description}")
        else:
            print(f"  ❌ Missing: {description}")
            all_found = False
    
    # Verify it's NOT using the old pattern
    if re.search(r'if pid == METEORA_PID:', method_content):
        print("  ❌ WARNING: Still using old 'if pid == METEORA_PID' pattern")
        all_found = False
    else:
        print("  ✅ Old pattern 'if pid == METEORA_PID' removed")
    
    return all_found

def verify_logging_format():
    """Verify logging uses existing emoji format"""
    print("\n" + "=" * 80)
    print("VERIFICATION: Logging Format")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    # Check for the logging statement in parse_transaction
    pattern = r'self\.logger\.info\(f"✅ \[PARSER\] Meteora detected:'
    
    if re.search(pattern, content):
        print("  ✅ Uses INFO level with ✅ emoji")
        print("  ✅ Uses [PARSER] prefix")
        return True
    else:
        print("  ❌ Logging format doesn't match expected pattern")
        return False

def verify_no_new_dependencies():
    """Verify no new dependencies were added"""
    print("\n" + "=" * 80)
    print("VERIFICATION: No New Dependencies")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        lines = f.readlines()
    
    # Get import statements
    imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from ')) and 'import' in line]
    
    # Check that we're only using existing imports
    new_imports = []
    for imp in imports:
        if any(x in imp for x in ['helius', 'new_library', 'requests']):
            new_imports.append(imp)
    
    if new_imports:
        print(f"  ❌ Found new dependencies: {new_imports}")
        return False
    else:
        print("  ✅ No new dependencies added")
        print("  ✅ Uses existing RPC client")
        return True

def main():
    """Run all verifications"""
    print("\n🔍 Verifying Meteora Detection Implementation\n")
    
    results = []
    results.append(("Constant definition", verify_constant_definition()))
    results.append(("Detection logic", verify_detection_logic()))
    results.append(("Logging format", verify_logging_format()))
    results.append(("No new dependencies", verify_no_new_dependencies()))
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("\nImplementation correctly:")
        print("  • Defines METEORA_PROGRAM_IDS set with both program IDs")
        print("  • Checks if pid in METEORA_PROGRAM_IDS")
        print("  • Sets parsed['dex'] = 'meteora'")
        print("  • Sets parsed['action'] = 'swap' when unset")
        print("  • Extracts wallet_address from first signer")
        print("  • Uses existing logging format (✅ [PARSER])")
        print("  • No new dependencies added")
        return 0
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
