#!/usr/bin/env python3
"""
Standalone test for _have_all_fields logic (without importing main.py).
"""

def _have_all_fields(trade_info: dict) -> bool:
    """
    Check if trade_info has all required fields for execution.
    
    Accepts both "mint" and "token_mint" to avoid naming mismatches.
    Normalizes field names by ensuring token_mint is set if mint exists.
    
    Args:
        trade_info: Trade information dictionary
        
    Returns:
        bool: True if all required fields are present and valid
    """
    # Accept both "mint" and "token_mint" to avoid naming mismatches
    token_mint = trade_info.get("token_mint") or trade_info.get("mint")
    dex = trade_info.get("dex")
    action = trade_info.get("action")
    wallet = trade_info.get("wallet_address")
    ok = all(v not in (None, "", "unknown", "PENDING_ANALYSIS") for v in (dex, action, wallet, token_mint))
    if ok and trade_info.get("token_mint") is None and token_mint:
        trade_info["token_mint"] = token_mint  # normalize
    return ok


def test_complete_fields():
    """Test with complete fields"""
    trade_info = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
    }
    result = _have_all_fields(trade_info)
    assert result == True, f"Should return True for complete fields, got {result}"
    print("✅ Complete fields test passed")


def test_mint_normalization():
    """Test mint to token_mint normalization"""
    trade_info = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "mint": "XYZ789"
    }
    result = _have_all_fields(trade_info)
    assert result == True, f"Should return True after normalization, got {result}"
    assert trade_info.get("token_mint") == "XYZ789", f"Should normalize mint to token_mint, got {trade_info.get('token_mint')}"
    print("✅ Mint normalization test passed")


def test_incomplete_fields():
    """Test with incomplete/invalid fields"""
    test_cases = [
        {"dex": "unknown", "action": "buy", "wallet_address": "ABC", "token_mint": "XYZ"},
        {"dex": "jupiter", "action": "unknown", "wallet_address": "ABC", "token_mint": "XYZ"},
        {"dex": "jupiter", "action": "buy", "wallet_address": "", "token_mint": "XYZ"},
        {"dex": "jupiter", "action": "buy", "wallet_address": "ABC", "token_mint": None},
        {"dex": "jupiter", "action": "buy", "wallet_address": "ABC", "token_mint": "PENDING_ANALYSIS"},
    ]
    
    for trade_info in test_cases:
        result = _have_all_fields(trade_info.copy())
        assert result == False, f"Should return False for {trade_info}, got {result}"
    
    print("✅ Incomplete fields test passed")


def test_missing_fields():
    """Test with missing required fields"""
    test_cases = [
        {"action": "buy", "wallet_address": "ABC", "token_mint": "XYZ"},
        {"dex": "jupiter", "wallet_address": "ABC", "token_mint": "XYZ"},
        {"dex": "jupiter", "action": "buy", "token_mint": "XYZ"},
        {"dex": "jupiter", "action": "buy", "wallet_address": "ABC"},
    ]
    
    for trade_info in test_cases:
        result = _have_all_fields(trade_info.copy())
        assert result == False, f"Should return False for {trade_info}, got {result}"
    
    print("✅ Missing fields test passed")


def test_both_mint_and_token_mint():
    """Test when both mint and token_mint are present"""
    trade_info = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "token_mint": "PRIMARY",
        "mint": "SECONDARY"
    }
    result = _have_all_fields(trade_info)
    assert result == True, f"Should return True, got {result}"
    assert trade_info.get("token_mint") == "PRIMARY", f"Should preserve token_mint, got {trade_info.get('token_mint')}"
    print("✅ Both mint and token_mint test passed")


if __name__ == "__main__":
    print("Testing _have_all_fields implementation...")
    print()
    
    test_complete_fields()
    test_mint_normalization()
    test_incomplete_fields()
    test_missing_fields()
    test_both_mint_and_token_mint()
    
    print()
    print("🎉 All _have_all_fields tests passed!")
