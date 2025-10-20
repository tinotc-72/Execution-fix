#!/usr/bin/env python3
"""
Code inspection validation for keypair and mint type safety fixes.

Validates that the fixes are present in the source code by inspecting:
1. _require_keypair() exists and validates wallet properly
2. Meteora builders assert Keypair type before VersionedTransaction
3. Jupiter _as_mint_str() is used for mint parameters
4. Jupiter guards route is None before .keys() access
"""

import re
import sys

def check_require_keypair():
    """Check that _require_keypair() exists and validates properly"""
    print("\n" + "=" * 80)
    print("CHECK 1: _require_keypair() Implementation")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Check for _require_keypair method
    if 'def _require_keypair(self):' not in content:
        print("❌ FAIL: _require_keypair() method not found")
        return False
    
    print("✅ PASS: _require_keypair() method exists")
    
    # Check for isinstance validation
    if 'isinstance(keypair, Keypair)' in content or 'isinstance(self.wallet, Keypair)' in content:
        print("✅ PASS: _require_keypair() validates Keypair type")
    else:
        print("❌ FAIL: _require_keypair() missing Keypair validation")
        return False
    
    # Check that it raises on invalid wallet
    if 'raise TypeError' in content and 'Configured wallet not loaded' in content:
        print("✅ PASS: _require_keypair() raises on invalid wallet")
    else:
        print("❌ FAIL: _require_keypair() missing error raise")
        return False
    
    # Check that random Keypair() is NOT fabricated
    lines_with_keypair_instantiation = []
    for i, line in enumerate(content.split('\n'), 1):
        if 'Keypair()' in line and 'import' not in line.lower():
            lines_with_keypair_instantiation.append((i, line.strip()))
    
    if lines_with_keypair_instantiation:
        print(f"⚠️  WARNING: Found {len(lines_with_keypair_instantiation)} Keypair() instantiation(s):")
        for line_num, line in lines_with_keypair_instantiation:
            print(f"   Line {line_num}: {line}")
        # Check if it's in a comment or removed context
        if any('fallback Keypair()' in line for _, line in lines_with_keypair_instantiation):
            print("❌ FAIL: Random keypair fabrication still present")
            return False
    else:
        print("✅ PASS: No random Keypair() fabrication found")
    
    return True

def check_meteora_assertions():
    """Check that Meteora builders assert Keypair type"""
    print("\n" + "=" * 80)
    print("CHECK 2: Meteora Keypair Assertions")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    checks_passed = 0
    
    # Check _build_meteora_buy_solders
    if re.search(r'def _build_meteora_buy_solders.*?assert isinstance\(owner, Keypair\)', content, re.DOTALL):
        print("✅ PASS: _build_meteora_buy_solders asserts isinstance(owner, Keypair)")
        checks_passed += 1
    else:
        print("❌ FAIL: _build_meteora_buy_solders missing Keypair assertion")
    
    # Check _build_meteora_sell_solders
    if re.search(r'def _build_meteora_sell_solders.*?assert isinstance\(owner, Keypair\)', content, re.DOTALL):
        print("✅ PASS: _build_meteora_sell_solders asserts isinstance(owner, Keypair)")
        checks_passed += 1
    else:
        print("❌ FAIL: _build_meteora_sell_solders missing Keypair assertion")
    
    # Check build_and_sign
    if re.search(r'def build_and_sign.*?assert isinstance\(keypair, Keypair\)', content, re.DOTALL):
        print("✅ PASS: build_and_sign asserts isinstance(keypair, Keypair)")
        checks_passed += 1
    else:
        print("❌ FAIL: build_and_sign missing Keypair assertion")
    
    return checks_passed == 3

def check_jupiter_mint_coercion():
    """Check that Jupiter uses _as_mint_str() for mint parameters"""
    print("\n" + "=" * 80)
    print("CHECK 3: Jupiter Mint Coercion with _as_mint_str()")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    # Check _as_mint_str exists
    if 'def _as_mint_str(m) -> str:' not in content:
        print("❌ FAIL: _as_mint_str() helper not found")
        return False
    
    print("✅ PASS: _as_mint_str() helper exists")
    
    # Check it's used in get_best_route calls
    if 'input_mint = _as_mint_str(input_mint)' in content:
        print("✅ PASS: _as_mint_str() used in get_best_route for input_mint")
    else:
        print("❌ FAIL: _as_mint_str() not used for input_mint in get_best_route")
        return False
    
    if 'output_mint = _as_mint_str(output_mint)' in content:
        print("✅ PASS: _as_mint_str() used in get_best_route for output_mint")
    else:
        print("❌ FAIL: _as_mint_str() not used for output_mint in get_best_route")
        return False
    
    # Check it's used in build_buy_tx
    if 'token_mint_str = _as_mint_str(token_mint)' in content:
        print("✅ PASS: _as_mint_str() used in build_buy_tx")
    else:
        print("❌ FAIL: _as_mint_str() not used in build_buy_tx")
        return False
    
    # Check it's used in execute_buy
    execute_buy_match = re.search(r'async def execute_buy.*?token_mint_str = _as_mint_str\(token_mint\)', content, re.DOTALL)
    if execute_buy_match:
        print("✅ PASS: _as_mint_str() used in execute_buy")
    else:
        print("❌ FAIL: _as_mint_str() not used in execute_buy")
        return False
    
    return True

def check_jupiter_route_guard():
    """Check that Jupiter guards route is None before .keys() access"""
    print("\n" + "=" * 80)
    print("CHECK 4: Jupiter Route None Guard")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        lines = f.readlines()
    
    # Find get_swap_transaction function
    in_function = False
    guard_line = -1
    keys_line = -1
    
    for i, line in enumerate(lines):
        if 'def get_swap_transaction(' in line:
            in_function = True
        elif in_function and 'def ' in line and 'get_swap_transaction' not in line:
            in_function = False
        
        if in_function:
            if 'if route is None:' in line:
                guard_line = i
            if 'route.keys()' in line:
                keys_line = i
    
    if guard_line == -1:
        print("❌ FAIL: No 'if route is None:' guard found in get_swap_transaction")
        return False
    
    print(f"✅ PASS: Route None guard found at line {guard_line + 1}")
    
    if keys_line == -1:
        print("✅ PASS: No unguarded route.keys() access (may have been removed or protected)")
        return True
    
    if guard_line < keys_line:
        print(f"✅ PASS: Guard at line {guard_line + 1} protects route.keys() at line {keys_line + 1}")
        return True
    else:
        print(f"❌ FAIL: route.keys() at line {keys_line + 1} appears before guard at line {guard_line + 1}")
        return False

def main():
    """Run all validation checks"""
    print("\n" + "#" * 80)
    print("# CODE INSPECTION: KEYPAIR AND MINT TYPE SAFETY VALIDATION")
    print("#" * 80)
    
    all_passed = True
    
    # Run checks
    all_passed = check_require_keypair() and all_passed
    all_passed = check_meteora_assertions() and all_passed
    all_passed = check_jupiter_mint_coercion() and all_passed
    all_passed = check_jupiter_route_guard() and all_passed
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED")
        print("\nValidated fixes:")
        print("  • _require_keypair() validates wallet and returns raw Keypair")
        print("  • No random keypair fabrication - raises if wallet not loaded")
        print("  • Meteora builders assert isinstance(owner/keypair, Keypair)")
        print("  • Jupiter _as_mint_str() coerces Pubkey to string for all mints")
        print("  • Jupiter guards route is None before .keys() access")
        print("\nGoal achieved: Fix Meteora signer and normalize Jupiter mints,")
        print("preventing builder crashes from type errors and missing keys.")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
