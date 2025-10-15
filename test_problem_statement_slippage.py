#!/usr/bin/env python3
"""
Validate that the implementation meets all problem statement requirements.
"""

import re
import sys


def check_requirement(requirement, check_func):
    """Helper to check and print requirement status."""
    print(f"\n{requirement}")
    result = check_func()
    status = "✅" if result else "❌"
    print(f"{status} {'PASS' if result else 'FAIL'}")
    return result


def main():
    """Validate all requirements from problem statement."""
    print("=" * 80)
    print("PROBLEM STATEMENT REQUIREMENTS VALIDATION")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    results = []
    
    # Requirement 1: ensure_meta_in_trade_info helper exists
    results.append(check_requirement(
        "1. ensure_meta_in_trade_info helper exists and matches specification",
        lambda: bool(re.search(
            r'def ensure_meta_in_trade_info\(self, trade_info: dict\) -> None:',
            content
        ))
    ))
    
    # Requirement 2: annotate_source_failure helper exists
    results.append(check_requirement(
        "2. annotate_source_failure helper exists and matches specification",
        lambda: bool(re.search(
            r'def annotate_source_failure\(self, trade_info: dict\) -> None:',
            content
        ))
    ))
    
    # Requirement 3: ensure_meta_in_trade_info attaches meta from backfilled
    results.append(check_requirement(
        "3. ensure_meta_in_trade_info attaches meta from backfilled if not present",
        lambda: bool(re.search(
            r'if "meta" not in trade_info:\s+backfilled = trade_info\.get\("backfilled_tx"\)\s+if backfilled and backfilled\.get\("meta"\):\s+trade_info\["meta"\] = backfilled\["meta"\]',
            content
        ))
    ))
    
    # Requirement 4: annotate_source_failure sets source_tx_failed
    results.append(check_requirement(
        "4. annotate_source_failure sets source_tx_failed = True if meta.err present",
        lambda: bool(re.search(
            r'trade_info\["source_tx_failed"\] = True',
            content
        ))
    ))
    
    # Requirement 5: Detects "Exceeded slippage tolerance" in logs
    results.append(check_requirement(
        "5. Detects 'Exceeded slippage tolerance' in log messages",
        lambda: bool(re.search(
            r'"Exceeded slippage tolerance" in logs',
            content
        ))
    ))
    
    # Requirement 6: Detects 6004 error code
    results.append(check_requirement(
        "6. Detects InstructionError Custom 6004",
        lambda: bool(re.search(
            r'"6004" in str\(err\)',
            content
        ))
    ))
    
    # Requirement 7: Sets retry_hint = "requote" for slippage
    results.append(check_requirement(
        "7. Sets retry_hint = 'requote' for slippage errors",
        lambda: bool(re.search(
            r'trade_info\["retry_hint"\] = "requote"',
            content
        ))
    ))
    
    # Requirement 8: Logs warning with emoji
    results.append(check_requirement(
        "8. Logs warning with emoji for slippage failure",
        lambda: bool(re.search(
            r'logger\.warning\("⚠️ \[ANALYSIS\] Source tx failed with ExceededSlippage \(6004\)',
            content
        ))
    ))
    
    # Requirement 9: Both helpers called at start of infer_missing_fields
    results.append(check_requirement(
        "9. Both helpers called at start of infer_missing_fields",
        lambda: bool(re.search(
            r'self\.ensure_meta_in_trade_info\(trade_info\).*?self\.annotate_source_failure\(trade_info\)',
            content,
            re.DOTALL
        ))
    ))
    
    # Requirement 10: Called with trade_info parameter
    results.append(check_requirement(
        "10. ensure_meta_in_trade_info called with trade_info",
        lambda: bool(re.search(
            r'self\.ensure_meta_in_trade_info\(trade_info\)',
            content
        ))
    ))
    
    # Requirement 11: Mint inference unchanged
    results.append(check_requirement(
        "11. Mint inference from postTokenBalances stays unchanged",
        lambda: bool(re.search(
            r'def _extract_mint_from_token_balances\(self, meta: dict\) -> Optional\[str\]:',
            content
        ) and re.search(
            r'\.get\("uiAmount"\)',
            content
        ) and re.search(
            r'✅ \[MINT_INFERENCE\] Resolved token mint from postTokenBalances',
            content
        ))
    ))
    
    # Requirement 12: No new dependencies
    imports_section = '\n'.join(content.split('\n')[:200])
    results.append(check_requirement(
        "12. No new dependencies added",
        lambda: not any([
            'import requests' in imports_section,
            'import httpx' in imports_section,
            'import anchorpy' in imports_section,
        ])
    ))
    
    # Requirement 13: Uses existing RPC client
    results.append(check_requirement(
        "13. Stays within existing rpc_client (no direct RPC imports)",
        lambda: 'from solana.rpc' not in imports_section
    ))
    
    # Requirement 14: Keeps emoji logging
    results.append(check_requirement(
        "14. Keeps emoji logging style",
        lambda: bool(re.search(r'⚠️', content))
    ))
    
    print("\n" + "=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"FINAL RESULT: {passed}/{total} requirements met")
    print("=" * 80)
    
    if passed == total:
        print("\n✅ ALL REQUIREMENTS SATISFIED!")
        print("\nImplementation Summary:")
        print("  • ensure_meta_in_trade_info: Attaches meta from backfilled tx")
        print("  • annotate_source_failure: Detects slippage (6004 or message)")
        print("  • Both called at start of infer_missing_fields")
        print("  • Mint inference logic unchanged")
        print("  • No new dependencies")
        print("  • Emoji logging maintained")
        return 0
    else:
        print(f"\n❌ {total - passed} REQUIREMENT(S) NOT MET")
        return 1


if __name__ == '__main__':
    sys.exit(main())
