#!/usr/bin/env python3
"""Test the problematic address at position 15"""

from solders.pubkey import Pubkey

def test_position_15_address():
    """Test the address that's causing Base58 error"""
    
    problematic_address = "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"
    
    print(f"Testing address: {problematic_address}")
    print(f"Length: {len(problematic_address)}")
    
    try:
        pubkey = Pubkey.from_string(problematic_address)
        print(f"✅ Valid Base58: {pubkey}")
    except Exception as e:
        print(f"❌ Invalid Base58: {e}")
        
        # Check if it's a truncation issue
        if len(problematic_address) != 44:
            print(f"⚠️  Address length is {len(problematic_address)}, expected 44")
            
        # Check each character
        import base58
        valid_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        for i, char in enumerate(problematic_address):
            if char not in valid_chars:
                print(f"❌ Invalid character '{char}' at position {i}")

if __name__ == "__main__":
    test_position_15_address()