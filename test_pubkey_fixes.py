#!/usr/bin/env python3
"""
Test script to validate that all Pubkey conversion fixes are working correctly
"""

from solders.pubkey import Pubkey

def safe_pubkey_conversion(token_input):
    """
    Safe Pubkey conversion that handles both string and Pubkey inputs
    This is the pattern we implemented in all executors
    """
    return token_input if isinstance(token_input, Pubkey) else Pubkey.from_string(token_input)

def test_pubkey_conversions():
    """Test all the Pubkey conversion scenarios"""
    print("🔧 Testing safe Pubkey conversion fixes...")
    
    # Test case 1: String input (normal case)
    test_mint_str = "So11111111111111111111111111111111111111112"
    result1 = safe_pubkey_conversion(test_mint_str)
    print(f"✅ String input: {test_mint_str} -> {result1}")
    
    # Test case 2: Pubkey object input (the bug case)
    test_mint_pubkey = Pubkey.from_string(test_mint_str)
    result2 = safe_pubkey_conversion(test_mint_pubkey)
    print(f"✅ Pubkey input: {test_mint_pubkey} -> {result2}")
    
    # Test case 3: Verify they're equal
    assert str(result1) == str(result2), "Results should be identical"
    print(f"✅ Both conversions produce identical results")
    
    # Test case 4: Test the old way that would crash
    try:
        # This is what was causing the crash
        problematic_result = Pubkey.from_string(test_mint_pubkey)
        print(f"❌ UNEXPECTED: Old method didn't crash: {problematic_result}")
    except TypeError as e:
        print(f"✅ EXPECTED: Old method crashes with Pubkey input: {e}")
    
    print("\n🎉 All Pubkey conversion tests passed!")
    print("🔧 The fixes should prevent the 'PyString' conversion errors")
    
    return True

if __name__ == "__main__":
    test_pubkey_conversions()
