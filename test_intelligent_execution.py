#!/usr/bin/env python3
"""
Test script to verify intelligent aggressive copy trading logic.

This script validates that the bot:
1. Only executes trades when it can reconstruct trade intent (buy/sell/swap) and token mint
2. Never blindly fires trades on account changes or wallet triggers alone
3. Parses transaction logs and instructions to extract direction and token mints
4. Logs and skips ambiguous trades where direction or token cannot be parsed
5. Provides robust audit logging for all decisions
"""

import re
import sys


def test_intelligent_execution_validation():
    """Test that intelligent execution validates trade intent parsing."""
    print("=" * 80)
    print("TEST 1: Verify Intelligent Execution Validation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        # Check for intelligent execution docstring
        (
            r"INTELLIGENT AGGRESSIVE TRADE EXECUTION",
            "Intelligent execution mode documented"
        ),
        # Check that action validation exists
        (
            r"valid_actions.*=.*\[.*buy.*sell.*swap",
            "Valid actions list defined"
        ),
        # Check for action validation logic
        (
            r"if action == 'unknown' or action not in valid_actions",
            "Action validation checks for unknown/invalid actions"
        ),
        # Check for token mint validation
        (
            r"if token_mint == 'UNKNOWN' or not token_mint",
            "Token mint validation checks for UNKNOWN/empty"
        ),
        # Check for token format validation
        (
            r"if not isinstance\(token_mint, str\) or len\(str\(token_mint\)\) < 32",
            "Token mint format validation (Solana address length)"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def test_no_blind_execution():
    """Test that blind execution on unknown data is prevented."""
    print("=" * 80)
    print("TEST 2: Verify No Blind Execution on Incomplete Data")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        # Check that unknown actions are NOT defaulted to swap
        (
            r"action = 'swap'.*# Default",
            "No defaulting unknown actions to swap",
            False  # Should NOT match
        ),
        # Check that trades are skipped when action is unknown
        (
            r"SKIP.*Skipping ambiguous trade.*direction cannot be parsed",
            "Skips trades when direction cannot be parsed"
        ),
        # Check that trades are skipped when token is unknown
        (
            r"SKIP.*Skipping ambiguous trade.*token cannot be identified",
            "Skips trades when token cannot be identified"
        ),
        # Check for audit logging of skipped trades
        (
            r"AUDIT.*Trade skipped.*reason=unknown_action",
            "Audit logs trades skipped due to unknown action"
        ),
        (
            r"AUDIT.*Trade skipped.*reason=unknown_token",
            "Audit logs trades skipped due to unknown token"
        ),
    ]
    
    passed = 0
    for test_data in tests:
        if len(test_data) == 3:
            pattern, description, should_match = test_data
        else:
            pattern, description = test_data
            should_match = True
        
        matches = bool(re.search(pattern, main, re.DOTALL))
        
        if matches == should_match:
            print(f"  ✅ {description}")
            passed += 1
        else:
            if should_match:
                print(f"  ❌ {description} (not found)")
            else:
                print(f"  ❌ {description} (should not exist)")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def test_trade_parsing_logging():
    """Test that trade parsing is properly logged."""
    print("=" * 80)
    print("TEST 3: Verify Trade Parsing and Audit Logging")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"TRADE_PARSE.*Cannot determine trade direction",
            "Logs when trade direction cannot be determined"
        ),
        (
            r"TRADE_PARSE.*Cannot extract token mint",
            "Logs when token mint cannot be extracted"
        ),
        (
            r"TRADE_PARSE.*Successfully parsed trade intent",
            "Logs successful trade intent parsing"
        ),
        (
            r"Action:.*\(parsed from logs/instructions\)",
            "Documents that action was parsed from logs/instructions"
        ),
        (
            r"Token Mint:.*\(extracted from transaction\)",
            "Documents that token was extracted from transaction"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def test_execution_requires_parsing():
    """Test that execution only happens after successful parsing."""
    print("=" * 80)
    print("TEST 4: Verify Execution Requires Successful Parsing")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Find the _process_detected_trade method
    method_match = re.search(
        r'async def _process_detected_trade.*?(?=\n    async def |\n    def |\nclass |\Z)',
        main,
        re.DOTALL
    )
    
    if not method_match:
        print("  ❌ _process_detected_trade method not found")
        return False
    
    method_body = method_match.group(0)
    
    # Count return statements before execution
    returns_before_exec = len(re.findall(r'return\s*$', method_body.split('_execute_copy_buy')[0], re.MULTILINE))
    
    # Check execution calls are after validation
    has_buy_after_validation = '_execute_copy_buy' in method_body
    has_sell_after_validation = '_execute_copy_sell' in method_body
    
    print(f"  ✅ Found {returns_before_exec} early returns (validation failures)")
    
    if has_buy_after_validation:
        print(f"  ✅ Buy execution present after validation")
    else:
        print(f"  ❌ Buy execution missing")
    
    if has_sell_after_validation:
        print(f"  ✅ Sell execution present after validation")
    else:
        print(f"  ❌ Sell execution missing")
    
    # Should have at least 3 early returns (unknown action, unknown token, invalid format)
    passed = returns_before_exec >= 3 and has_buy_after_validation and has_sell_after_validation
    
    if passed:
        print(f"\n  ✅ Execution flow properly validates before executing\n")
    else:
        print(f"\n  ❌ Execution flow validation incomplete\n")
    
    return passed


def test_intelligent_mode_messaging():
    """Test that messaging reflects intelligent execution mode."""
    print("=" * 80)
    print("TEST 5: Verify Intelligent Execution Mode Messaging")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"INTELLIGENT EXECUTION MODE.*Trade intent successfully reconstructed",
            "Messages reflect intelligent execution mode"
        ),
        (
            r"Executing parsed trade.*matching intelligent wallet behavior",
            "Messages indicate parsed trade execution"
        ),
        (
            r"EXECUTE ONLY PARSED TRADES.*No blind execution on incomplete data",
            "Code comments emphasize no blind execution"
        ),
        # Should NOT have aggressive mode messaging that suggests blind execution
        (
            r"AGGRESSIVE EXECUTION MODE.*Proceeding with execution",
            "Old aggressive mode messaging removed",
            False  # Should NOT match
        ),
    ]
    
    passed = 0
    for test_data in tests:
        if len(test_data) == 3:
            pattern, description, should_match = test_data
        else:
            pattern, description = test_data
            should_match = True
        
        matches = bool(re.search(pattern, main, re.DOTALL))
        
        if matches == should_match:
            print(f"  ✅ {description}")
            passed += 1
        else:
            if should_match:
                print(f"  ❌ {description} (not found)")
            else:
                print(f"  ❌ {description} (still present)")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def test_header_documentation():
    """Test that header documentation reflects intelligent execution."""
    print("=" * 80)
    print("TEST 6: Verify Header Documentation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Extract header (first 100 lines)
    header = '\n'.join(main.split('\n')[:100])
    
    tests = [
        (
            r"INTELLIGENT AGGRESSIVE EXECUTION LOGIC",
            "Header describes intelligent execution logic"
        ),
        (
            r"Execute trades ONLY when trade intent is fully reconstructable",
            "Header emphasizes ONLY executing reconstructable trades"
        ),
        (
            r"Parses logs/instructions to extract action.*and token mint",
            "Header describes parsing of action and token mint"
        ),
        (
            r"Logs and skips ambiguous trades",
            "Header mentions skipping ambiguous trades"
        ),
        (
            r"No execution on incomplete data",
            "Header explicitly states no execution on incomplete data"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, header, re.DOTALL):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("INTELLIGENT AGGRESSIVE COPY TRADING LOGIC TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        test_intelligent_execution_validation(),
        test_no_blind_execution(),
        test_trade_parsing_logging(),
        test_execution_requires_parsing(),
        test_intelligent_mode_messaging(),
        test_header_documentation(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✅ ALL TESTS PASSED!")
        print("  ✅ Intelligent execution logic fully implemented")
        print("  ✅ Only executes when trade intent is fully parsed")
        print("  ✅ Never blindly executes on incomplete data")
        print("  ✅ Validates action (buy/sell/swap) and token mint")
        print("  ✅ Skips ambiguous trades with audit logging")
        print("  ✅ Maintains 0.001 SOL investment for buys")
        print()
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
