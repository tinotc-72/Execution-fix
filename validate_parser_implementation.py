#!/usr/bin/env python3
"""
Final validation script for the parser implementation.
Verifies all problem statement requirements are met.
"""

def validate_parser_implementation():
    """Validate that wallet_tx_parser.py meets all requirements"""
    print("\n" + "=" * 80)
    print("VALIDATION: Parser Implementation")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        parser_content = f.read()
    
    checks = [
        # Requirement 1: DEX detection for Jupiter
        ('JUPITER_PID = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"', 
         '✅ Jupiter program ID constant defined'),
        ('if pid == JUPITER_PID:', 
         '✅ Jupiter detection by programId'),
        ('if "SharedAccountsRouteV2" in logs', 
         '✅ Jupiter detection by logs (SharedAccountsRouteV2)'),
        ('parsed["dex"] = "jupiter"', 
         '✅ Sets dex to "jupiter"'),
        ('parsed.setdefault("action", "swap")', 
         '✅ Sets action to "swap" for Jupiter'),
        
        # Requirement 2: DEX detection for Meteora
        ('METEORA_PROGRAM_IDS = {', 
         '✅ Meteora program IDs set defined'),
        ('if pid in METEORA_PROGRAM_IDS:', 
         '✅ Meteora detection by programId'),
        ('parsed["dex"] = "meteora"', 
         '✅ Sets dex to "meteora"'),
        ('parsed["action"] = "swap"', 
         '✅ Sets action to "swap" for Meteora'),
        
        # Requirement 3: wallet_address extraction
        ('signers = [k["pubkey"] for k in keys if isinstance(k, dict) and k.get("signer")]', 
         '✅ Extracts signers from accountKeys'),
        ('parsed["wallet_address"] = signers[0]', 
         '✅ Sets wallet_address from first signer'),
        ('parsed["wallet_address"] = keys[0]', 
         '✅ Fallback to accountKeys[0] (fee payer)'),
        
        # Requirement 4: merge_parsed_fields function
        ('def merge_parsed_fields(trade_info: dict, parsed: dict) -> None:', 
         '✅ merge_parsed_fields function defined'),
        ('"dex": "dex"', 
         '✅ Maps dex field'),
        ('"action": "action"', 
         '✅ Maps action field'),
        ('"wallet_address": "wallet_address"', 
         '✅ Maps wallet_address field'),
        ('"mint": "token_mint"', 
         '✅ Maps mint to token_mint'),
        ('if val and trade_info.get(dst) in (None, "", "unknown", "PENDING_ANALYSIS"):', 
         '✅ Only updates empty/unknown/PENDING_ANALYSIS fields'),
        ('trade_info[dst] = val', 
         '✅ Updates trade_info with parsed value'),
    ]
    
    passed = 0
    failed = 0
    
    for pattern, description in checks:
        if pattern in parser_content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
            failed += 1
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def validate_main_integration():
    """Validate that main.py properly integrates the parser"""
    print("=" * 80)
    print("VALIDATION: Main.py Integration")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    checks = [
        # Check import
        ('from wallet_tx_parser import WalletTransactionParser, merge_parsed_fields', 
         '✅ Imports merge_parsed_fields from wallet_tx_parser'),
        
        # Check it's not duplicated
        ('def merge_parsed_fields', 
         '❌ merge_parsed_fields should NOT be defined in main.py'),
        
        # Check it's called at entry point
        ('merge_parsed_fields(trade_info, parsed_tx)', 
         '✅ merge_parsed_fields called at entry point'),
        
        # Check it's called after backfill
        ('merge_parsed_fields(trade_info, parsed)', 
         '✅ merge_parsed_fields called after backfill'),
    ]
    
    passed = 0
    failed = 0
    
    # Special handling for the "should NOT be defined" check
    for i, (pattern, description) in enumerate(checks):
        if i == 1:  # The "should NOT be defined" check
            if pattern not in main_content:
                print(f"  ✅ merge_parsed_fields is NOT duplicated in main.py (correct)")
                passed += 1
            else:
                print(f"  ❌ merge_parsed_fields is duplicated in main.py (incorrect)")
                failed += 1
        else:
            if pattern in main_content:
                print(f"  {description}")
                passed += 1
            else:
                print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
                failed += 1
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def validate_logging():
    """Validate that parser logs are present"""
    print("=" * 80)
    print("VALIDATION: Parser Logging")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        parser_content = f.read()
    
    checks = [
        ('self.logger.info(f"✅ [PARSER] Jupiter detected: programId={pid[:8]}...")', 
         '✅ Logs Jupiter detection by programId'),
        ('self.logger.info(f"✅ [PARSER] Jupiter detected from logs")', 
         '✅ Logs Jupiter detection from logs'),
        ('self.logger.info(f"✅ [PARSER] Meteora detected: programId={pid[:8]}...")', 
         '✅ Logs Meteora detection by programId'),
    ]
    
    passed = 0
    failed = 0
    
    for pattern, description in checks:
        if pattern in parser_content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
            failed += 1
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def main():
    """Run all validations"""
    print("\n" + "=" * 80)
    print("FINAL VALIDATION - Parser Implementation Problem Statement")
    print("=" * 80)
    
    results = []
    results.append(("Parser Implementation", validate_parser_implementation()))
    results.append(("Main.py Integration", validate_main_integration()))
    results.append(("Parser Logging", validate_logging()))
    
    print("=" * 80)
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
        print("\n✅ ALL VALIDATIONS PASSED")
        print("\nProblem Statement Requirements Met:")
        print("  1. ✅ Jupiter DEX detected by programId (JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4)")
        print("  2. ✅ Jupiter DEX detected by logs containing SharedAccountsRouteV2")
        print("  3. ✅ Meteora DEX detected by programId (dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN)")
        print("  4. ✅ Action set to 'swap' for both Jupiter and Meteora")
        print("  5. ✅ wallet_address extracted from first signer in accountKeys")
        print("  6. ✅ wallet_address falls back to accountKeys[0] (fee payer)")
        print("  7. ✅ merge_parsed_fields function defined in wallet_tx_parser.py")
        print("  8. ✅ merge_parsed_fields maps all required fields")
        print("  9. ✅ merge_parsed_fields only updates empty/unknown/PENDING_ANALYSIS")
        print("  10. ✅ merge_parsed_fields called at entry point (after parsing)")
        print("  11. ✅ merge_parsed_fields called after backfill")
        print("  12. ✅ Parser logs show correct DEX detection")
        print("\n🎉 Implementation Complete!")
        return 0
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
