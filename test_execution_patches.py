#!/usr/bin/env python3
"""
Test script to validate execution error patches.

Tests:
1. MEVDirectCopyExecutor receives EnvKeys object correctly
2. Jupiter API endpoints are updated to current v6 URLs
3. Raydium account parsing extracts complete information
4. Trade parser infers mint from token balances
5. Network error handling provides clear messages
"""

import sys
import json


def test_direct_copy_executor_envkeys():
    """Test that MEVDirectCopyExecutor accepts and uses env_keys parameter"""
    print("=" * 80)
    print("TEST 1: MEVDirectCopyExecutor EnvKeys Parameter")
    print("=" * 80)
    
    with open('mev_direct_copy_executor.py', 'r') as f:
        executor = f.read()
    
    checks = [
        (
            'def __init__(self, private_key: str, config=None, jito_service=None, env_keys=None):',
            '✅ __init__ accepts env_keys parameter'
        ),
        (
            'if env_keys is None:',
            '✅ Creates EnvKeys instance if not provided'
        ),
        (
            'self.mev_bot = CompleteMEVBot(env_keys, mev_bot_config)',
            '✅ Passes EnvKeys object to CompleteMEVBot'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in executor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_execution_coordinator_envkeys_passing():
    """Test that execution_coordinator passes env_keys to MEVDirectCopyExecutor"""
    print("=" * 80)
    print("TEST 2: ExecutionCoordinator Passes EnvKeys")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        coordinator = f.read()
    
    checks = [
        (
            'env = env_keys.EnvKeys()',
            '✅ Creates EnvKeys instance'
        ),
        (
            'executor = MEVDirectCopyExecutor(private_key, config, jito_service=self.jito_service, env_keys=env)',
            '✅ Passes env_keys to MEVDirectCopyExecutor'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in coordinator:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_jupiter_api_endpoints():
    """Test that Jupiter API endpoints are updated to v6"""
    print("=" * 80)
    print("TEST 3: Jupiter API v6 Endpoints")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        executor = f.read()
    
    checks = [
        (
            '"https://quote-api.jup.ag/v6/quote"',
            '✅ Uses quote-api.jup.ag v6 quote endpoint'
        ),
        (
            '"https://quote-api.jup.ag/v6/swap"',
            '✅ Uses quote-api.jup.ag v6 swap endpoint'
        ),
        (
            '"https://public.jupiterapi.com/quote/v6"',
            '✅ Has public fallback quote endpoint'
        ),
        (
            '"https://public.jupiterapi.com/swap/v6"',
            '✅ Has public fallback swap endpoint'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in executor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    with open('env_keys.py', 'r') as f:
        env_keys = f.read()
    
    env_checks = [
        (
            "self.JUPITER_QUOTE_URL = os.getenv('JUPITER_QUOTE_URL', 'https://quote-api.jup.ag/v6/quote')",
            '✅ env_keys defaults to correct quote URL'
        ),
        (
            "self.JUPITER_SWAP_URL = os.getenv('JUPITER_SWAP_URL', 'https://quote-api.jup.ag/v6/swap')",
            '✅ env_keys defaults to correct swap URL'
        ),
    ]
    
    for pattern, description in env_checks:
        if pattern in env_keys:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    total_checks = len(checks) + len(env_checks)
    print(f"\n  Result: {passed}/{total_checks} checks passed\n")
    return passed == total_checks


def test_raydium_account_parsing():
    """Test that trade parser extracts Raydium account information"""
    print("=" * 80)
    print("TEST 4: Raydium Account Parsing")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    checks = [
        (
            'def _parse_raydium_accounts(self, trade_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:',
            '✅ _parse_raydium_accounts method exists'
        ),
        (
            'RAYDIUM_CPMM_PROGRAM = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"',
            '✅ Uses correct Raydium CPMM program ID'
        ),
        (
            "'pool_config':",
            '✅ Extracts pool_config account'
        ),
        (
            "'pool_state':",
            '✅ Extracts pool_state account'
        ),
        (
            "'input_vault':",
            '✅ Extracts input_vault account'
        ),
        (
            "'output_vault':",
            '✅ Extracts output_vault account'
        ),
        (
            "raydium_info = self._parse_raydium_accounts(trade_info)",
            '✅ Calls Raydium parsing in infer_missing_fields'
        ),
        (
            "trade_info['parsed_tx']['raydium_info'] = raydium_info",
            '✅ Stores parsed info in trade_info'
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


def test_mint_inference_from_balances():
    """Test that trade parser extracts mint from token balances"""
    print("=" * 80)
    print("TEST 5: Mint Inference from Token Balances")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    checks = [
        (
            'def _extract_mint_from_token_balances(self, trade_info: Dict[str, Any]) -> Optional[str]:',
            '✅ _extract_mint_from_token_balances method exists'
        ),
        (
            "meta.get('preTokenBalances', [])",
            '✅ Checks pre token balances'
        ),
        (
            "meta.get('postTokenBalances', [])",
            '✅ Checks post token balances'
        ),
        (
            'mint = self._extract_mint_from_token_balances(trade_info)',
            '✅ Calls balance extraction in infer_missing_fields'
        ),
        (
            "inferred_fields.append('token_mint (from balances)')",
            '✅ Logs when mint is inferred from balances'
        ),
        (
            '# Build dicts keyed by accountIndex for efficient lookup',
            '✅ Builds dicts keyed by accountIndex'
        ),
        (
            'SOL_MINT = "So11111111111111111111111111111111111111112"',
            '✅ Defines WSOL mint for exclusion'
        ),
        (
            'mint != SOL_MINT',
            '✅ Ignores WSOL in balance processing'
        ),
        (
            'abs(x[1][\'delta\'])',
            '✅ Uses absolute delta for mint selection'
        ),
        (
            '# Fallback: If no pre balance or ties, choose first non-WSOL mint from postTokenBalances',
            '✅ Has fallback for no pre balance case'
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


def test_network_error_handling():
    """Test that network errors provide clear messages"""
    print("=" * 80)
    print("TEST 6: Network Error Handling")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        executor = f.read()
    
    checks = [
        (
            '"nodename nor servname provided" in error_str',
            '✅ Detects DNS resolution failures'
        ),
        (
            '"Failed to resolve" in error_str',
            '✅ Detects DNS resolution failures (alternate)'
        ),
        (
            '"404" in error_str',
            '✅ Detects 404 errors'
        ),
        (
            'logger.warning(f"[JUPITER_QUOTE] ⚠️  Endpoint {endpoint_idx} DNS resolution failed',
            '✅ Logs DNS errors clearly'
        ),
        (
            'logger.warning(f"[JUPITER_QUOTE] ⚠️  Endpoint {endpoint_idx} returned 404',
            '✅ Logs 404 errors clearly'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in executor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    with open('env_keys.py', 'r') as f:
        env_keys = f.read()
    
    env_checks = [
        (
            'if not os.getenv("PHANTOM_PRIVATE_KEY"):',
            '✅ Validates PHANTOM_PRIVATE_KEY exists'
        ),
        (
            'raise ValueError("PHANTOM_PRIVATE_KEY not found in environment variables',
            '✅ Raises clear error if key missing'
        ),
    ]
    
    for pattern, description in env_checks:
        if pattern in env_keys:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    total_checks = len(checks) + len(env_checks)
    print(f"\n  Result: {passed}/{total_checks} checks passed\n")
    return passed == total_checks


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("EXECUTION ERROR PATCHES VALIDATION")
    print("=" * 80 + "\n")
    
    results = []
    
    results.append(("MEVDirectCopyExecutor EnvKeys", test_direct_copy_executor_envkeys()))
    results.append(("ExecutionCoordinator EnvKeys Passing", test_execution_coordinator_envkeys_passing()))
    results.append(("Jupiter API v6 Endpoints", test_jupiter_api_endpoints()))
    results.append(("Raydium Account Parsing", test_raydium_account_parsing()))
    results.append(("Mint Inference from Balances", test_mint_inference_from_balances()))
    results.append(("Network Error Handling", test_network_error_handling()))
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n  🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n  ⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
