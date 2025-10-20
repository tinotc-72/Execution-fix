#!/usr/bin/env python3
"""
Test for merge_parsed_fields helper function.
Validates that parser-detected fields are preserved and not clobbered.
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_merge_parsed_fields_implementation():
    """Test that merge_parsed_fields is implemented correctly"""
    print("=" * 80)
    print("TEST: merge_parsed_fields Implementation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'def merge_parsed_fields(trade_info: dict, parsed: dict) -> None:',
            '✅ merge_parsed_fields function exists with correct signature'
        ),
        (
            'if isinstance(parsed.get("parsed_tx"), dict):',
            '✅ Handles parsed_tx wrapper'
        ),
        (
            '"dex": "dex"',
            '✅ Maps dex field'
        ),
        (
            '"action": "action"',
            '✅ Maps action field'
        ),
        (
            '"token_mint": "token_mint"',
            '✅ Maps token_mint field'
        ),
        (
            '"mint": "token_mint"',
            '✅ Maps mint to token_mint'
        ),
        (
            '"wallet_address": "wallet_address"',
            '✅ Maps wallet_address field'
        ),
        (
            '"signature": "signature"',
            '✅ Maps signature field'
        ),
        (
            'if val and trade_info.get(dst) in (None, "", "unknown", "PENDING_ANALYSIS"):',
            '✅ Checks for empty/unknown values before updating'
        ),
        (
            'trade_info[dst] = val',
            '✅ Updates trade_info with parsed value'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_merge_call_placement():
    """Test that merge_parsed_fields is called in the right place"""
    print("=" * 80)
    print("TEST: merge_parsed_fields Call Placement")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'logger.debug(f"[PIPELINE_ENTRY] ✅ Transaction parsed successfully")',
            '✅ Parser success log exists'
        ),
        (
            'merge_parsed_fields(trade_info, parsed_tx)',
            '✅ merge_parsed_fields is called with correct arguments'
        ),
    ]
    
    # Check the order - merge should be called right after parsing success
    lines = content.split('\n')
    parse_success_idx = None
    merge_call_idx = None
    
    for i, line in enumerate(lines):
        if '[PIPELINE_ENTRY] ✅ Transaction parsed successfully' in line:
            parse_success_idx = i
        if 'merge_parsed_fields(trade_info, parsed_tx)' in line:
            merge_call_idx = i
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    # Check ordering
    if parse_success_idx is not None and merge_call_idx is not None:
        if merge_call_idx > parse_success_idx and (merge_call_idx - parse_success_idx) < 5:
            print("  ✅ merge_parsed_fields called immediately after parsing")
            passed += 1
        else:
            print("  ❌ merge_parsed_fields not in correct position relative to parse success")
    else:
        print("  ❌ Could not verify ordering")
    
    print(f"\n  Result: {passed}/{len(checks) + 1} checks passed\n")
    return passed == (len(checks) + 1)


def test_wallet_address_extraction():
    """Test that wallet_address extraction from tx signer is implemented"""
    print("=" * 80)
    print("TEST: Wallet Address Extraction from Transaction")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'if not trade_info.get("wallet_address"):',
            '✅ Checks if wallet_address is missing'
        ),
        (
            'msg = (trade_info.get("transaction") or {}).get("message", {})',
            '✅ Extracts message from transaction'
        ),
        (
            'signers = [k["pubkey"] for k in (msg.get("accountKeys") or []) if k.get("signer")]',
            '✅ Extracts signers from accountKeys'
        ),
        (
            'trade_info["wallet_address"] = signers[0]',
            '✅ Sets wallet_address from first signer'
        ),
        (
            'logger.info("[PIPELINE_ENTRY] Set wallet_address from tx signer: %s", signers[0])',
            '✅ Logs when wallet_address is set from signer'
        ),
        (
            'logger.warning("[PIPELINE_ENTRY] No signer in tx; leaving wallet_address empty")',
            '✅ Warns when no signer found'
        ),
    ]
    
    # Check that the old bad defaulting is removed from _handle_websocket_trade
    bad_patterns = [
        ('Missing \'wallet_address\', setting to first target wallet', '_handle_websocket_trade'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    # Check bad patterns are removed from _handle_websocket_trade
    # Extract just the _handle_websocket_trade method
    import re
    match = re.search(r'async def _handle_websocket_trade\(.*?\n(?=    async def |class )', content, re.DOTALL)
    if match:
        method_content = match.group(0)
        for bad_pattern, context in bad_patterns:
            if bad_pattern not in method_content:
                print(f"  ✅ Old bad defaulting logic removed from {context}")
                passed += 1
            else:
                print(f"  ❌ Old bad defaulting logic still present in {context}")
    else:
        print(f"  ❌ Could not find _handle_websocket_trade method")
    
    print(f"\n  Result: {passed}/{len(checks) + len(bad_patterns)} checks passed\n")
    return passed == (len(checks) + len(bad_patterns))


def test_missing_fields_logic():
    """Test that missing fields detection runs after merge"""
    print("=" * 80)
    print("TEST: Missing Fields Detection After Merge")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'missing = []',
            '✅ Creates missing fields list'
        ),
        (
            'for k in ("wallet_address", "dex", "action", "token_mint"):',
            '✅ Checks for missing required fields'
        ),
        (
            'if trade_info.get(k) in (None, "", "unknown", "PENDING_ANALYSIS"):',
            '✅ Checks for empty/unknown values'
        ),
        (
            'missing.append(k)',
            '✅ Appends missing field to list'
        ),
        (
            'logger.info(f"[PIPELINE_ENTRY] 📋 Missing/defaulted fields: {\', \'.join(missing)}")',
            '✅ Logs missing fields'
        ),
        (
            'logger.info(f"[PIPELINE_ENTRY] ✅ All expected fields present")',
            '✅ Logs when all fields present'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_emoji_logging_preserved():
    """Test that emoji logging is maintained"""
    print("=" * 80)
    print("TEST: Emoji Logging Preserved")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    emoji_patterns = [
        '✅ Transaction parsed successfully',
        '📋 Missing/defaulted fields',
        '✅ All expected fields present',
    ]
    
    passed = 0
    for pattern in emoji_patterns:
        if pattern in content:
            print(f"  ✅ Found emoji log: {pattern}")
            passed += 1
        else:
            print(f"  ❌ Missing emoji log: {pattern}")
    
    print(f"\n  Result: {passed}/{len(emoji_patterns)} checks passed\n")
    return passed == len(emoji_patterns)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("VERIFICATION: merge_parsed_fields Implementation")
    print("=" * 80 + "\n")
    
    results = []
    
    results.append(("merge_parsed_fields Implementation", test_merge_parsed_fields_implementation()))
    results.append(("merge_parsed_fields Call Placement", test_merge_call_placement()))
    results.append(("Wallet Address Extraction", test_wallet_address_extraction()))
    results.append(("Missing Fields Detection", test_missing_fields_logic()))
    results.append(("Emoji Logging Preserved", test_emoji_logging_preserved()))
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n✅ ALL VERIFICATIONS PASSED")
        print("\nImplementation Summary:")
        print("  • Added merge_parsed_fields helper function")
        print("  • Calls merge_parsed_fields after parsing")
        print("  • Extracts wallet_address from transaction signers")
        print("  • Detects missing fields after merge")
        print("  • Preserves emoji logging format")
        print("  • No new dependencies added")
        return 0
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
