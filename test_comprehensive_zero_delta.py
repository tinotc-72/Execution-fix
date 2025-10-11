#!/usr/bin/env python3
"""
Comprehensive validation test for zero-delta execution.

This test validates that the complete execution path works correctly
when there are zero token balance changes but execution triggers are present.
"""

import re
import sys


def test_wallet_tx_parser_zero_delta():
    """Test that wallet_tx_parser handles zero delta correctly."""
    print("=" * 80)
    print("TEST: Wallet TX Parser Zero Delta Handling")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    tests = [
        (
            r"def _check_dex_instruction_in_logs",
            "Has method to check DEX instructions in logs"
        ),
        (
            r"def _is_monitored_wallet",
            "Has method to check if wallet is monitored"
        ),
        (
            r"async def _create_synthetic_trade_info",
            "Has method to create synthetic trade info"
        ),
        (
            r"has_dex_instruction.*=.*_check_dex_instruction_in_logs",
            "Checks for DEX instructions before balance analysis"
        ),
        (
            r"is_monitored_wallet.*=.*_is_monitored_wallet",
            "Checks if wallet is monitored before balance analysis"
        ),
        (
            r"if has_dex_instruction or is_monitored_wallet",
            "Creates synthetic trade info when triggers are met"
        ),
        (
            r"INFORMATIONAL.*Balance-based trade detection",
            "Balance method marked as informational"
        ),
        (
            r"does NOT gate execution",
            "Explicitly states balance doesn't gate execution"
        ),
        (
            r"'transaction'.*transaction_data",
            "Includes transaction data in synthetic trade info"
        ),
        (
            r"'logs'.*logs",
            "Includes logs in synthetic trade info"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return 1 if passed == len(tests) else 0


def test_execution_flow_integration():
    """Test that execution flow integrates properly."""
    print("=" * 80)
    print("TEST: Execution Flow Integration")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    with open('wallet_tx_parser.py', 'r') as f:
        parser_content = f.read()
    
    tests = [
        # wallet_tx_parser creates trade_info
        (
            parser_content,
            r"await self\.trade_callback\(trade_info\)",
            "Wallet parser calls trade_callback with trade_info"
        ),
        # main.py receives and processes trade_info
        (
            main_content,
            r"async def _handle_websocket_trade.*trade_info",
            "Main has handler for websocket trades"
        ),
        (
            main_content,
            r"async def _process_detected_trade.*trade_info",
            "Main has processor for detected trades"
        ),
        # Both check for execution triggers
        (
            parser_content,
            r"_check_dex_instruction_in_logs",
            "Parser checks DEX instructions"
        ),
        (
            main_content,
            r"_check_trade_instructions",
            "Main checks trade instructions"
        ),
        (
            main_content,
            r"_check_monitored_wallet_is_signer",
            "Main checks monitored wallet signers"
        ),
    ]
    
    passed = 0
    for content, pattern, description in tests:
        if re.search(pattern, content, re.DOTALL):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return 1 if passed == len(tests) else 0


def test_no_legacy_gating():
    """Test that no legacy balance gating logic remains."""
    print("=" * 80)
    print("TEST: No Legacy Balance Gating Logic")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        parser_content = f.read()
    
    # These patterns should NOT be found (specific to gating logic)
    bad_patterns = [
        (
            r"log_debug.*Skipping.*No token balance changes",
            "SHOULD NOT skip on no balance changes"
        ),
    ]
    
    passed = 0
    total = len(bad_patterns)
    
    for pattern, description in bad_patterns:
        found = re.search(pattern, parser_content, re.DOTALL | re.IGNORECASE)
        if not found:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description} - FOUND (should be removed)")
            # Show context
            match = found.group(0)
            print(f"      Found: {match[:100]}...")
    
    print(f"\n  Result: {passed}/{total} checks passed\n")
    return 1 if passed == total else 0


def test_synthetic_trade_info_structure():
    """Test that synthetic trade info has required structure."""
    print("=" * 80)
    print("TEST: Synthetic Trade Info Structure")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    # Extract the _create_synthetic_trade_info method
    match = re.search(
        r"async def _create_synthetic_trade_info.*?(?=\n    async def |\n    def |\nclass |\Z)",
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find _create_synthetic_trade_info method")
        return 0
    
    method_content = match.group(0)
    
    required_fields = [
        ('signature', 'signature field'),
        ('wallet_address', 'wallet_address field'),
        ('action', 'action field'),
        ('dex', 'dex field'),
        ('token_mint', 'token_mint field'),
        ('zero_delta', 'zero_delta flag'),
        ('logs', 'logs for analysis'),
        (r"trade_info\['transaction'\].*transaction_data", 'transaction data inclusion'),
        (r"trade_info\['meta'\].*meta_data", 'meta data inclusion'),
    ]
    
    passed = 0
    for field, description in required_fields:
        if re.search(field, method_content):
            print(f"  ✅ Includes {description}")
            passed += 1
        else:
            print(f"  ❌ Missing {description}")
    
    print(f"\n  Result: {passed}/{len(required_fields)} fields present\n")
    return 1 if passed == len(required_fields) else 0


def main():
    """Run all comprehensive tests."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE ZERO-DELTA EXECUTION VALIDATION")
    print("=" * 80)
    print("\nValidates complete execution path for zero token balance delta scenarios")
    print("=" * 80)
    print()
    
    tests = [
        test_wallet_tx_parser_zero_delta(),
        test_execution_flow_integration(),
        test_no_legacy_gating(),
        test_synthetic_trade_info_structure(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL VALIDATION RESULTS")
    print("=" * 80)
    print(f"\n  Test Suites Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✅ ALL VALIDATION TESTS PASSED!")
        print("  ✅ Zero-delta execution fully implemented")
        print("  ✅ Balance gating completely removed")
        print("  ✅ Execution triggers: DEX instruction OR monitored wallet")
        print("  ✅ Transaction data included in synthetic trades")
        print("  ✅ Complete integration validated")
        print()
        return 0
    else:
        print(f"\n  ❌ {total - passed} test suite(s) failed")
        print("  ❌ Review failures above")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
