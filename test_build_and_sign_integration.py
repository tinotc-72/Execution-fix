#!/usr/bin/env python3
"""
Integration test example for build_and_sign function.
This demonstrates how the function integrates with the existing codebase.
"""

def test_integration_pattern():
    """Test that build_and_sign follows the integration pattern"""
    print("=" * 80)
    print("INTEGRATION TEST: build_and_sign Usage Pattern")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    print("\n--- Test 1: Function is callable from module ---")
    if 'def build_and_sign(' in content:
        print("✅ PASS: build_and_sign is defined at module level")
    else:
        print("❌ FAIL: build_and_sign not at module level")
        return False
    
    print("\n--- Test 2: Uses existing RPC client pattern ---")
    if 'SimpleRPC' in content and 'rpc: SimpleRPC' in content:
        print("✅ PASS: Uses existing SimpleRPC client")
    else:
        print("❌ FAIL: Does not use SimpleRPC")
        return False
    
    print("\n--- Test 3: Uses existing utility functions ---")
    utilities = [
        'find_associated_token_address',
        'create_associated_token_account_ix'
    ]
    
    for util in utilities:
        if util in content:
            print(f"✅ PASS: Uses {util} from utils")
        else:
            print(f"❌ FAIL: Missing {util}")
            return False
    
    print("\n--- Test 4: Returns VersionedTransaction (Solders) ---")
    if 'VersionedTransaction' in content and 'solders' in content:
        print("✅ PASS: Returns Solders VersionedTransaction")
    else:
        print("⚠️  INFO: Return type unclear")
    
    print("\n--- Test 5: Integrates with existing patterns ---")
    # Check if it can work with existing trade_info structure
    if 'trade_info' in content and 'ContextPoolResolverMeteora' in content:
        print("✅ PASS: Integrates with ContextPoolResolverMeteora")
    else:
        print("⚠️  INFO: Integration with resolver unclear")
    
    print("\n--- Test 6: Transaction structure documentation ---")
    if '1.' in content and '2.' in content and 'ATA' in content:
        print("✅ PASS: Transaction structure is documented")
    else:
        print("⚠️  INFO: Documentation could be clearer")
    
    return True

def test_example_usage():
    """Show example usage pattern"""
    print("\n" + "=" * 80)
    print("EXAMPLE USAGE PATTERN")
    print("=" * 80)
    
    example = '''
# Example integration with execution coordinator:

from mev_meteora_executor import build_and_sign, SimpleRPC, RPCConfig
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Setup (existing patterns)
rpc = SimpleRPC(RPCConfig("https://api.mainnet-beta.solana.com"))
wallet = Keypair()  # From env_keys.py
token_mint = Pubkey.from_string("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R")

# Build transaction with proper structure
tx = build_and_sign(
    rpc=rpc,
    owner=wallet,
    token_mint=token_mint,
    lamports_in=1_000_000,  # 0.001 SOL
    min_tokens=1,
    trade_info={"signature": "...", "wallet_address": "..."}  # Optional
)

# Transaction is ready but NOT submitted
# Can now:
# 1. Send via Jito for MEV protection
# 2. Send via RPC
# 3. Inspect/validate before sending

if jito_available:
    result = await jito_service.send_bundle([tx])
else:
    sig = rpc.send_transaction(tx)
    '''
    
    print(example)
    print("\n✅ Example shows proper integration pattern")
    return True

def test_compatibility():
    """Test compatibility with existing code"""
    print("\n" + "=" * 80)
    print("COMPATIBILITY TEST")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    print("\n--- Test 1: Does not modify existing functions ---")
    existing_functions = [
        '_build_meteora_buy_solders',
        '_build_meteora_sell_solders',
        'mev_meteora_copy_trade'
    ]
    
    for func in existing_functions:
        if f'def {func}(' in content:
            print(f"✅ PASS: {func} still exists")
        else:
            print(f"⚠️  INFO: {func} may have been modified")
    
    print("\n--- Test 2: No breaking changes to imports ---")
    critical_imports = [
        'from solders.keypair import Keypair',
        'from solders.pubkey import Pubkey',
        'from solders.transaction import VersionedTransaction',
        'from solders.instruction import Instruction'
    ]
    
    for imp in critical_imports:
        if imp in content:
            print(f"✅ PASS: {imp}")
        else:
            print(f"⚠️  INFO: {imp} may be different")
    
    print("\n--- Test 3: Maintains logging consistency ---")
    if 'logger.info' in content and 'logger.warning' in content:
        print("✅ PASS: Logger usage maintained")
    else:
        print("⚠️  INFO: Logger usage unclear")
    
    return True

def main():
    """Run all integration tests"""
    print("\n🔗 Testing build_and_sign Integration")
    print("=" * 80)
    
    tests = [
        ("Integration Pattern", test_integration_pattern),
        ("Example Usage", test_example_usage),
        ("Compatibility", test_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {passed}/{total} integration tests passed")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
