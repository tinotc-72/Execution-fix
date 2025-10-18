#!/usr/bin/env python3
"""
Test the merge_parsed_fields function in wallet_tx_parser.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wallet_tx_parser import merge_parsed_fields

def test_merge_basic():
    """Test basic field merging"""
    print("\n=== TEST: Basic field merging ===")
    
    trade_info = {
        "dex": None,
        "action": "unknown",
        "token_mint": None,
        "wallet_address": "PENDING_ANALYSIS",
        "signature": None,
    }
    
    parsed = {
        "dex": "jupiter",
        "action": "swap",
        "mint": "TokenMint123",
        "wallet_address": "Wallet456",
        "signature": "Sig789",
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    print(f"Before merge: dex=None, action=unknown, token_mint=None")
    print(f"After merge: dex={trade_info['dex']}, action={trade_info['action']}, token_mint={trade_info['token_mint']}")
    
    assert trade_info["dex"] == "jupiter", f"Expected dex='jupiter', got '{trade_info['dex']}'"
    assert trade_info["action"] == "swap", f"Expected action='swap', got '{trade_info['action']}'"
    assert trade_info["token_mint"] == "TokenMint123", f"Expected token_mint='TokenMint123', got '{trade_info['token_mint']}'"
    assert trade_info["wallet_address"] == "Wallet456", f"Expected wallet_address='Wallet456', got '{trade_info['wallet_address']}'"
    assert trade_info["signature"] == "Sig789", f"Expected signature='Sig789', got '{trade_info['signature']}'"
    
    print("✅ PASS: All fields merged correctly")
    return True

def test_merge_preserve_existing():
    """Test that existing valid values are preserved"""
    print("\n=== TEST: Preserve existing valid values ===")
    
    trade_info = {
        "dex": "raydium",  # Already set
        "action": "buy",    # Already set
        "token_mint": "ExistingToken",  # Already set
    }
    
    parsed = {
        "dex": "jupiter",  # Should NOT override
        "action": "swap",  # Should NOT override
        "mint": "NewToken",  # Should NOT override
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    print(f"Input: dex=raydium, action=buy, token_mint=ExistingToken")
    print(f"After merge: dex={trade_info['dex']}, action={trade_info['action']}, token_mint={trade_info['token_mint']}")
    
    assert trade_info["dex"] == "raydium", "Should preserve existing dex"
    assert trade_info["action"] == "buy", "Should preserve existing action"
    assert trade_info["token_mint"] == "ExistingToken", "Should preserve existing token_mint"
    
    print("✅ PASS: Existing values preserved")
    return True

def test_merge_empty_parsed():
    """Test with empty parsed dict"""
    print("\n=== TEST: Empty parsed dict ===")
    
    trade_info = {
        "dex": "unknown",
        "action": "unknown",
    }
    
    parsed = {}
    
    merge_parsed_fields(trade_info, parsed)
    
    print(f"Input: dex=unknown, action=unknown, parsed={{}}")
    print(f"After merge: dex={trade_info['dex']}, action={trade_info['action']}")
    
    # Should still be unknown since parsed is empty
    assert trade_info["dex"] == "unknown"
    assert trade_info["action"] == "unknown"
    
    print("✅ PASS: Handles empty parsed dict")
    return True

def test_merge_with_parsed_tx_wrapper():
    """Test with parsed_tx wrapper"""
    print("\n=== TEST: parsed_tx wrapper ===")
    
    trade_info = {
        "dex": None,
        "action": None,
    }
    
    parsed = {
        "parsed_tx": {
            "dex": "meteora",
            "action": "swap",
        }
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    print(f"Input: parsed with parsed_tx wrapper")
    print(f"After merge: dex={trade_info['dex']}, action={trade_info['action']}")
    
    assert trade_info["dex"] == "meteora", "Should extract from parsed_tx wrapper"
    assert trade_info["action"] == "swap", "Should extract from parsed_tx wrapper"
    
    print("✅ PASS: Handles parsed_tx wrapper")
    return True

def main():
    """Run all tests"""
    print("=" * 70)
    print("TEST: merge_parsed_fields Function")
    print("=" * 70)
    
    tests = [
        ("Basic field merging", test_merge_basic),
        ("Preserve existing values", test_merge_preserve_existing),
        ("Empty parsed dict", test_merge_empty_parsed),
        ("parsed_tx wrapper", test_merge_with_parsed_tx_wrapper),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ merge_parsed_fields function works correctly!")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
