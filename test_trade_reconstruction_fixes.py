#!/usr/bin/env python3
"""
Test script to validate trade reconstruction and execution fixes.

Tests the fixes implemented for:
1. Missing mint data extraction (3-tier fallback)
2. Jupiter API endpoint corrections
3. Raydium pool resolution error handling
4. Transaction type error fixes
5. Enhanced logging for skipped trades

Based on problem statement requirements from Log analysis.
"""

import re
import sys


def test_jupiter_endpoints():
    """Test that Jupiter API endpoints are corrected."""
    print("=" * 80)
    print("TEST 1: Jupiter API Endpoint Corrections")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        jupiter = f.read()
    
    checks = [
        (
            'https://quote-api.jup.ag/v6/quote',
            '✅ Primary quote endpoint is correct (quote-api.jup.ag/v6)'
        ),
        (
            'https://quote-api.jup.ag/v6/swap',
            '✅ Primary swap endpoint is correct (quote-api.jup.ag/v6)'
        ),
        (
            'JUPITER_QUOTE_ENDPOINTS = [',
            '✅ Multiple quote endpoints configured for fallback'
        ),
        (
            'JUPITER_SWAP_ENDPOINTS = [',
            '✅ Multiple swap endpoints configured for fallback'
        ),
        (
            'for endpoint_idx, endpoint_url in enumerate(JUPITER_QUOTE_ENDPOINTS',
            '✅ Quote endpoint iteration with fallback logic'
        ),
        (
            'for endpoint_idx, endpoint_url in enumerate(JUPITER_SWAP_ENDPOINTS',
            '✅ Swap endpoint iteration with fallback logic'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in jupiter:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_jupiter_return_types():
    """Test that Jupiter functions return None instead of error dicts."""
    print("=" * 80)
    print("TEST 2: Jupiter Return Type Fixes (None instead of error dicts)")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        jupiter = f.read()
    
    checks = [
        (
            'def get_best_route(input_mint: str, output_mint: str, amount: int, slippage_bps: int = 300) -> Optional[dict]:',
            '✅ get_best_route returns Optional[dict]'
        ),
        (
            'def get_swap_transaction(route: dict, user_pubkey: Pubkey) -> Optional[str]:',
            '✅ get_swap_transaction returns Optional[str]'
        ),
        (
            re.compile(r'return None.*# All endpoints failed', re.DOTALL),
            '✅ Returns None on failure (not error dict)'
        ),
        (
            'if not isinstance(route, dict) or \'success\' in route and not route[\'success\']:',
            '✅ Validates route input to prevent passing error dicts'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if isinstance(pattern, re.Pattern):
            if pattern.search(jupiter):
                print(f"  {description}")
                passed += 1
            else:
                print(f"  ❌ {description.replace('✅', '')}")
        else:
            if pattern in jupiter:
                print(f"  {description}")
                passed += 1
            else:
                print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_mint_extraction_fallbacks():
    """Test 3-tier mint extraction fallback strategy."""
    print("=" * 80)
    print("TEST 3: 3-Tier Mint Extraction Fallback")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    checks = [
        (
            '_extract_mint_from_logs_enhanced',
            '✅ Tier 1: Enhanced log parsing for mint extraction'
        ),
        (
            '_extract_mint_from_token_balances',
            '✅ Tier 2: Balance delta-based mint extraction'
        ),
        (
            '_extract_mint_from_instruction_accounts',
            '✅ Tier 3: Instruction account parsing for mint'
        ),
        (
            'mint = self._extract_mint_from_logs_enhanced(logs)',
            '✅ Tier 1 called in inference pipeline'
        ),
        (
            'mint = self._extract_mint_from_token_balances(trade_info)',
            '✅ Tier 2 called as fallback'
        ),
        (
            'mint = self._extract_mint_from_instruction_accounts(trade_info)',
            '✅ Tier 3 called as last resort'
        ),
        (
            'Methods tried: log parsing, balance deltas, instruction accounts',
            '✅ Comprehensive error message lists all methods tried'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in processor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_enhanced_mint_extraction():
    """Test enhanced mint extraction features."""
    print("=" * 80)
    print("TEST 4: Enhanced Mint Extraction Features")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    checks = [
        (
            'from collections import Counter',
            '✅ Uses Counter for frequency analysis in log parsing'
        ),
        (
            'mint_counts = Counter(potential_mints)',
            '✅ Counts mint mentions in logs for reliability'
        ),
        (
            'if count >= 2:  # Mentioned at least twice',
            '✅ Requires mint mentioned 2+ times for confidence'
        ),
        (
            'buys = [m for m in changed_mints if m[\'delta\'] > 0]',
            '✅ Identifies buy/sell from balance deltas'
        ),
        (
            'best_buy = max(buys, key=lambda x: x[\'delta\'])',
            '✅ Finds token with largest positive delta (bought)'
        ),
        (
            'if prog_id not in DEX_PROGRAMS:',
            '✅ Filters instruction accounts to DEX programs only'
        ),
        (
            'excluded_programs = set(DEX_PROGRAMS.keys()) | TOKEN_PROGRAMS',
            '✅ Excludes known system programs from mint candidates'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in processor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_raydium_error_messages():
    """Test Raydium pool resolution error improvements."""
    print("=" * 80)
    print("TEST 5: Raydium Pool Resolution Error Messages")
    print("=" * 80)
    
    with open('mev_raydium_executor.py', 'r') as f:
        raydium = f.read()
    
    checks = [
        (
            'missing_fields = []',
            '✅ Tracks which Raydium fields are missing'
        ),
        (
            'if not pool_state: missing_fields.append("pool_state")',
            '✅ Identifies missing pool_state'
        ),
        (
            'if not pool_config: missing_fields.append("pool_config")',
            '✅ Identifies missing pool_config'
        ),
        (
            '[RAYDIUM_POOL] ❌ Incomplete Raydium account set - missing:',
            '✅ Logs specific missing fields for debugging'
        ),
        (
            'Consider using Jupiter executor as fallback for broader DEX support',
            '✅ Suggests Jupiter fallback in error message'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in raydium:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_skipped_trade_logging():
    """Test enhanced logging for skipped trades."""
    print("=" * 80)
    print("TEST 6: Enhanced Logging for Skipped Trades")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    checks = [
        (
            'logger.error(f"❌ [SKIPPED_TRADE] Signature: {sig}")',
            '✅ Logs signature of skipped trade'
        ),
        (
            'logger.error(f"❌ [SKIPPED_TRADE] Reason: Validation failed',
            '✅ Logs reason for skipping'
        ),
        (
            'validation_issues = []',
            '✅ Collects all validation issues'
        ),
        (
            'if not mint or mint in [\'UNKNOWN\', \'PENDING_ANALYSIS\']:',
            '✅ Identifies invalid/missing mint as issue'
        ),
        (
            'if not action or action == \'unknown\':',
            '✅ Identifies invalid/missing action as issue'
        ),
        (
            '[SKIPPED_TRADE] Validation issues:',
            '✅ Logs all validation issues together'
        ),
        (
            'logger.error(f"❌ [SKIPPED_TRADE] Raw transaction keys:',
            '✅ Logs raw transaction data for analysis'
        ),
        (
            'log_failed_trade_analysis',
            '✅ Calls log_failed_trade_analysis for offline debugging'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in main:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_documentation_references():
    """Test that official documentation is referenced in code."""
    print("=" * 80)
    print("TEST 7: Official Documentation References")
    print("=" * 80)
    
    docs_found = []
    
    # Check trade_processor.py
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
        if 'https://docs.solana.com/developing/programming-model/transactions' in processor:
            docs_found.append('✅ Solana transaction structure docs in trade_processor.py')
        if 'https://spl.solana.com/token' in processor:
            docs_found.append('✅ SPL Token Program docs in trade_processor.py')
        if 'https://github.com/raydium-io/raydium-sdk' in processor:
            docs_found.append('✅ Raydium SDK docs in trade_processor.py')
    
    # Check mev_jupiter_executor.py
    with open('mev_jupiter_executor.py', 'r') as f:
        jupiter = f.read()
        if 'https://station.jup.ag/docs/apis/swap-api' in jupiter:
            docs_found.append('✅ Jupiter API docs in mev_jupiter_executor.py')
        if 'https://docs.solana.com/developing/versioned-transactions' in jupiter:
            docs_found.append('✅ VersionedTransaction docs in mev_jupiter_executor.py')
    
    for doc in docs_found:
        print(f"  {doc}")
    
    total_expected = 5
    print(f"\n  Result: {len(docs_found)}/{total_expected} documentation references found\n")
    return len(docs_found) >= total_expected


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TRADE RECONSTRUCTION AND EXECUTION FIXES TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        test_jupiter_endpoints,
        test_jupiter_return_types,
        test_mint_extraction_fallbacks,
        test_enhanced_mint_extraction,
        test_raydium_error_messages,
        test_skipped_trade_logging,
        test_documentation_references,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}\n")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
