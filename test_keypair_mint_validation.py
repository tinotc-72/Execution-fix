#!/usr/bin/env python3
"""
Test validation for keypair and mint type safety fixes.

Tests that:
1. _require_keypair() validates and returns proper Keypair
2. Meteora builder asserts Keypair type before VersionedTransaction
3. Jupiter _as_mint_str() coerces Pubkey to string
4. Jupiter guards route is None before .keys() access
"""

import sys
import os

# Mock solders types for testing without installation
class MockKeypair:
    """Mock Keypair class"""
    def pubkey(self):
        return "MockPubkey123"

class MockPubkey:
    """Mock Pubkey class"""
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return self.value
    
    @staticmethod
    def from_string(s):
        return MockPubkey(s)

# Patch the imports
sys.modules['solders'] = type(sys)('solders')
sys.modules['solders.keypair'] = type(sys)('solders.keypair')
sys.modules['solders.pubkey'] = type(sys)('solders.pubkey')
sys.modules['solders.keypair'].Keypair = MockKeypair
sys.modules['solders.pubkey'].Pubkey = MockPubkey

def test_require_keypair_validation():
    """Test _require_keypair() validates wallet properly"""
    print("\n" + "=" * 80)
    print("TEST 1: _require_keypair() Validation")
    print("=" * 80)
    
    # Import after patching
    from execution_coordinator import ExecutionCoordinator
    
    # Test 1a: Valid Keypair wrapper
    class WalletWrapper:
        def __init__(self):
            self.keypair = MockKeypair()
    
    coordinator = ExecutionCoordinator(WalletWrapper(), None, None, None)
    try:
        kp = coordinator._require_keypair()
        if isinstance(kp, MockKeypair):
            print("✅ PASS: _require_keypair() returns Keypair from wrapper")
        else:
            print(f"❌ FAIL: Expected MockKeypair, got {type(kp)}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False
    
    # Test 1b: Direct Keypair
    coordinator2 = ExecutionCoordinator(MockKeypair(), None, None, None)
    try:
        kp = coordinator2._require_keypair()
        if isinstance(kp, MockKeypair):
            print("✅ PASS: _require_keypair() accepts direct Keypair")
        else:
            print(f"❌ FAIL: Expected MockKeypair, got {type(kp)}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False
    
    # Test 1c: Invalid wallet (should raise)
    class InvalidWallet:
        pass
    
    coordinator3 = ExecutionCoordinator(InvalidWallet(), None, None, None)
    try:
        kp = coordinator3._require_keypair()
        print(f"❌ FAIL: Should have raised TypeError for invalid wallet")
        return False
    except TypeError as e:
        print(f"✅ PASS: _require_keypair() raises TypeError for invalid wallet: {e}")
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {e}")
        return False
    
    return True

def test_as_mint_str_coercion():
    """Test _as_mint_str() coerces Pubkey to string"""
    print("\n" + "=" * 80)
    print("TEST 2: _as_mint_str() Coercion")
    print("=" * 80)
    
    # Import after patching
    from mev_jupiter_executor import _as_mint_str
    
    # Test 2a: String input
    result = _as_mint_str("SomeTokenMint123")
    if result == "SomeTokenMint123":
        print(f"✅ PASS: _as_mint_str() preserves string input")
    else:
        print(f"❌ FAIL: Expected 'SomeTokenMint123', got '{result}'")
        return False
    
    # Test 2b: Pubkey input
    pubkey = MockPubkey("TokenPubkey456")
    result = _as_mint_str(pubkey)
    if result == "TokenPubkey456":
        print(f"✅ PASS: _as_mint_str() coerces Pubkey to string")
    else:
        print(f"❌ FAIL: Expected 'TokenPubkey456', got '{result}'")
        return False
    
    # Test 2c: Object with __str__
    class CustomObject:
        def __str__(self):
            return "CustomTokenMint789"
    
    result = _as_mint_str(CustomObject())
    if result == "CustomTokenMint789":
        print(f"✅ PASS: _as_mint_str() coerces object to string")
    else:
        print(f"❌ FAIL: Expected 'CustomTokenMint789', got '{result}'")
        return False
    
    return True

def test_route_none_guard():
    """Test that route is None is guarded before .keys() access"""
    print("\n" + "=" * 80)
    print("TEST 3: Route None Guard")
    print("=" * 80)
    
    # This test verifies the fix by checking the code directly
    import mev_jupiter_executor
    import inspect
    
    # Get source of get_swap_transaction
    source = inspect.getsource(mev_jupiter_executor.get_swap_transaction)
    
    # Check for guard before route.keys() access
    if "if route is None:" in source:
        lines = source.split('\n')
        guard_line = -1
        keys_line = -1
        
        for i, line in enumerate(lines):
            if "if route is None:" in line:
                guard_line = i
            if "route.keys()" in line:
                keys_line = i
        
        if guard_line >= 0 and keys_line > guard_line:
            print(f"✅ PASS: Route None guard exists before .keys() access")
            print(f"   Guard at line {guard_line}, .keys() at line {keys_line}")
            return True
        else:
            print(f"❌ FAIL: Guard exists but not before .keys() access")
            return False
    else:
        print(f"❌ FAIL: No 'if route is None:' guard found")
        return False

def test_meteora_keypair_assertion():
    """Test that Meteora builder asserts Keypair type"""
    print("\n" + "=" * 80)
    print("TEST 4: Meteora Keypair Assertion")
    print("=" * 80)
    
    # This test verifies the fix by checking the code directly
    import mev_meteora_executor
    import inspect
    
    # Get source of _build_meteora_buy_solders
    source = inspect.getsource(mev_meteora_executor._build_meteora_buy_solders)
    
    # Check for assertion
    if "assert isinstance(owner, Keypair)" in source:
        print(f"✅ PASS: Meteora buy builder asserts isinstance(owner, Keypair)")
    else:
        print(f"❌ FAIL: No Keypair assertion found in buy builder")
        return False
    
    # Get source of _build_meteora_sell_solders
    source = inspect.getsource(mev_meteora_executor._build_meteora_sell_solders)
    
    # Check for assertion
    if "assert isinstance(owner, Keypair)" in source:
        print(f"✅ PASS: Meteora sell builder asserts isinstance(owner, Keypair)")
    else:
        print(f"❌ FAIL: No Keypair assertion found in sell builder")
        return False
    
    # Get source of build_and_sign
    source = inspect.getsource(mev_meteora_executor.build_and_sign)
    
    # Check for assertion
    if "assert isinstance(keypair, Keypair)" in source:
        print(f"✅ PASS: Meteora build_and_sign asserts isinstance(keypair, Keypair)")
    else:
        print(f"❌ FAIL: No Keypair assertion found in build_and_sign")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "#" * 80)
    print("# KEYPAIR AND MINT TYPE SAFETY VALIDATION")
    print("#" * 80)
    
    all_passed = True
    
    # Run tests
    all_passed = test_require_keypair_validation() and all_passed
    all_passed = test_as_mint_str_coercion() and all_passed
    all_passed = test_route_none_guard() and all_passed
    all_passed = test_meteora_keypair_assertion() and all_passed
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nValidated:")
        print("  • _require_keypair() validates wallet and returns raw Keypair")
        print("  • No random keypair fabrication - raises if wallet not loaded")
        print("  • Meteora builders assert isinstance(owner/keypair, Keypair)")
        print("  • Jupiter _as_mint_str() coerces Pubkey to string")
        print("  • Jupiter guards route is None before .keys() access")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
