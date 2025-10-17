#!/usr/bin/env python3
"""
Test the updated _have_all_fields function specification.

Per problem statement, _have_all_fields should:
1. Check only dex and wallet_address (NOT action)
2. Check token_mint or mint
3. Normalize mint to token_mint
"""

def _have_all_fields(ti: dict) -> bool:
    """Implementation from problem statement"""
    tok = ti.get("token_mint") or ti.get("mint")
    ok = all(ti.get(k) not in (None, "", "unknown", "PENDING_ANALYSIS") for k in ("dex","wallet_address")) and bool(tok)
    if tok and not ti.get("token_mint"):
        ti["token_mint"] = tok
    return ok


def test_complete_fields():
    """Test with all required fields present"""
    print("\n=== Test 1: Complete Fields ===")
    ti = {
        "dex": "jupiter",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
    }
    result = _have_all_fields(ti)
    print(f"Input: {ti}")
    print(f"Result: {result}")
    assert result == True, "Should return True for complete fields"
    print("✅ PASS")


def test_mint_normalization():
    """Test normalization of mint to token_mint"""
    print("\n=== Test 2: Mint Normalization ===")
    ti = {
        "dex": "jupiter",
        "wallet_address": "ABC123",
        "mint": "XYZ789"
    }
    result = _have_all_fields(ti)
    print(f"Input (before): {{'dex': 'jupiter', 'wallet_address': 'ABC123', 'mint': 'XYZ789'}}")
    print(f"Result: {result}")
    print(f"Output (after): {ti}")
    assert result == True, "Should return True"
    assert ti.get("token_mint") == "XYZ789", "Should normalize mint to token_mint"
    print("✅ PASS")


def test_missing_dex():
    """Test with missing dex"""
    print("\n=== Test 3: Missing DEX ===")
    ti = {
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
    }
    result = _have_all_fields(ti)
    print(f"Input: {ti}")
    print(f"Result: {result}")
    assert result == False, "Should return False for missing dex"
    print("✅ PASS")


def test_unknown_dex():
    """Test with dex=unknown"""
    print("\n=== Test 4: DEX=unknown ===")
    ti = {
        "dex": "unknown",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
    }
    result = _have_all_fields(ti)
    print(f"Input: {ti}")
    print(f"Result: {result}")
    assert result == False, "Should return False for dex=unknown"
    print("✅ PASS")


def test_missing_wallet():
    """Test with missing wallet_address"""
    print("\n=== Test 5: Missing wallet_address ===")
    ti = {
        "dex": "jupiter",
        "token_mint": "XYZ789"
    }
    result = _have_all_fields(ti)
    print(f"Input: {ti}")
    print(f"Result: {result}")
    assert result == False, "Should return False for missing wallet_address"
    print("✅ PASS")


def test_missing_token_mint():
    """Test with missing token_mint and mint"""
    print("\n=== Test 6: Missing token_mint/mint ===")
    ti = {
        "dex": "jupiter",
        "wallet_address": "ABC123"
    }
    result = _have_all_fields(ti)
    print(f"Input: {ti}")
    print(f"Result: {result}")
    assert result == False, "Should return False for missing token_mint"
    print("✅ PASS")


def test_action_not_required():
    """Test that action is NOT required (key difference from old spec)"""
    print("\n=== Test 7: Action NOT Required (NEW SPEC) ===")
    ti = {
        "dex": "jupiter",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
        # NO action field
    }
    result = _have_all_fields(ti)
    print(f"Input: {ti}")
    print(f"Result: {result}")
    assert result == True, "Should return True even without action field"
    print("✅ PASS - action is not required in new spec")


def test_unknown_action_ok():
    """Test that action=unknown does not affect result (action not checked)"""
    print("\n=== Test 8: action=unknown OK (NEW SPEC) ===")
    ti = {
        "dex": "jupiter",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789",
        "action": "unknown"  # should be ignored
    }
    result = _have_all_fields(ti)
    print(f"Input: {ti}")
    print(f"Result: {result}")
    assert result == True, "Should return True (action not checked)"
    print("✅ PASS - action field is ignored in new spec")


if __name__ == "__main__":
    print("=" * 80)
    print("Testing _have_all_fields - NEW SPECIFICATION")
    print("=" * 80)
    print("\nPer problem statement:")
    print("- Checks: dex, wallet_address, token_mint/mint")
    print("- Does NOT check: action")
    print("- Normalizes mint to token_mint")
    
    tests = [
        test_complete_fields,
        test_mint_normalization,
        test_missing_dex,
        test_unknown_dex,
        test_missing_wallet,
        test_missing_token_mint,
        test_action_not_required,
        test_unknown_action_ok,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("✅ All tests passed!")
        print("\nKey changes from old spec:")
        print("- action field is NO LONGER checked")
        print("- Only dex, wallet_address, and token_mint are required")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
