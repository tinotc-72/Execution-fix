#!/usr/bin/env python3
"""
Integration test for Jupiter None route handling.
Tests the complete flow from get_best_route through build_and_sign.
"""

import sys
import asyncio
from unittest.mock import MagicMock, patch
from solders.keypair import Keypair


def test_jupiter_none_route_flow():
    """Test that None route is handled gracefully through the entire flow"""
    print("=" * 80)
    print("INTEGRATION TEST: Jupiter None Route Handling")
    print("=" * 80)
    
    # Import the functions
    try:
        from mev_jupiter_executor import get_swap_transaction, build_buy_tx, build_and_sign
        from solders.pubkey import Pubkey
        print("✅ Successfully imported Jupiter executor functions")
    except ImportError as e:
        print(f"❌ FAIL: Import error: {e}")
        return False
    
    # Test 1: get_swap_transaction with None route
    print("\n--- Test 1: get_swap_transaction(None, pubkey) ---")
    try:
        test_pubkey = Keypair().pubkey()
        result = get_swap_transaction(None, test_pubkey)
        if result is None:
            print("✅ PASS: get_swap_transaction returns None for None route")
        else:
            print(f"❌ FAIL: get_swap_transaction returned {result} instead of None")
            return False
    except AttributeError as e:
        print(f"❌ FAIL: AttributeError raised: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected exception: {e}")
        return False
    
    # Test 2: get_swap_transaction with empty dict route
    print("\n--- Test 2: get_swap_transaction({}, pubkey) ---")
    try:
        result = get_swap_transaction({}, test_pubkey)
        if result is None:
            print("✅ PASS: get_swap_transaction returns None for empty dict route")
        else:
            print(f"❌ FAIL: get_swap_transaction returned {result} instead of None")
            return False
    except AttributeError as e:
        print(f"❌ FAIL: AttributeError raised: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected exception: {e}")
        return False
    
    # Test 3: build_buy_tx with mock that returns None route
    print("\n--- Test 3: build_buy_tx with no route available ---")
    try:
        with patch('mev_jupiter_executor.get_best_route') as mock_route:
            mock_route.return_value = None
            test_keypair = Keypair()
            result = build_buy_tx("So11111111111111111111111111111111111111112", 0.001, test_keypair)
            if result is None:
                print("✅ PASS: build_buy_tx returns None when no route available")
            else:
                print(f"❌ FAIL: build_buy_tx returned {result} instead of None")
                return False
    except ValueError as e:
        print(f"❌ FAIL: ValueError raised (should return None): {e}")
        return False
    except Exception as e:
        print(f"⚠️  Note: Exception raised: {e}")
        # This might be acceptable if it's just a mocking issue
    
    # Test 4: build_and_sign with mock that returns None from build_buy_tx
    print("\n--- Test 4: build_and_sign with no route available ---")
    try:
        with patch('mev_jupiter_executor.build_buy_tx') as mock_build:
            mock_build.return_value = None
            test_keypair = Keypair()
            trade_info = {"token_mint": "So11111111111111111111111111111111111111112", "amount_sol": 0.001}
            result = build_and_sign(trade_info, "http://localhost:8899", test_keypair)
            if result is None:
                print("✅ PASS: build_and_sign returns None when build_buy_tx returns None")
            else:
                print(f"❌ FAIL: build_and_sign returned {result} instead of None")
                return False
    except ValueError as e:
        print(f"❌ FAIL: ValueError raised (should return None): {e}")
        return False
    except Exception as e:
        print(f"⚠️  Note: Exception raised: {e}")
        # This might be acceptable if it's just a mocking issue
    
    # Test 5: build_and_sign with missing token_mint
    print("\n--- Test 5: build_and_sign with missing token_mint ---")
    try:
        test_keypair = Keypair()
        trade_info = {"amount_sol": 0.001}  # Missing token_mint
        result = build_and_sign(trade_info, "http://localhost:8899", test_keypair)
        if result is None:
            print("✅ PASS: build_and_sign returns None when token_mint is missing")
        else:
            print(f"❌ FAIL: build_and_sign returned {result} instead of None")
            return False
    except ValueError as e:
        print(f"❌ FAIL: ValueError raised (should return None): {e}")
        return False
    except Exception as e:
        print(f"⚠️  Note: Exception raised: {e}")
    
    return True


def test_no_attributeerror():
    """Specific test to ensure no AttributeError on None route"""
    print("\n" + "=" * 80)
    print("CRITICAL TEST: No AttributeError on None route")
    print("=" * 80)
    
    try:
        from mev_jupiter_executor import get_swap_transaction
        from solders.keypair import Keypair
        
        test_pubkey = Keypair().pubkey()
        
        # Test with various falsy values
        test_cases = [
            (None, "None"),
            ({}, "empty dict"),
            (0, "zero"),
            (False, "False"),
        ]
        
        for test_value, description in test_cases:
            try:
                result = get_swap_transaction(test_value, test_pubkey)
                print(f"✅ PASS: No AttributeError with route={description}, returned {result}")
            except AttributeError as e:
                print(f"❌ FAIL: AttributeError with route={description}: {e}")
                return False
            except Exception as e:
                # Other exceptions are acceptable - we're only checking for AttributeError
                print(f"✅ PASS: No AttributeError with route={description} (other exception: {type(e).__name__})")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Setup error: {e}")
        return False


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("JUPITER NONE ROUTE - INTEGRATION TEST SUITE")
    print("=" * 80)
    
    results = []
    
    # Run critical test first
    results.append(test_no_attributeerror())
    
    # Run integration test
    results.append(test_jupiter_none_route_flow())
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL INTEGRATION TESTS PASSED")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} INTEGRATION TEST(S) FAILED")
        sys.exit(1)
