"""
Private Key Verification Script
Created: 2025-06-19 00:42:39 UTC
Author: tinotc-72
"""

from env_keys import kz
import base58

def verify_private_key(key, show_pattern=True):
    print("\n=== Private Key Verification Report ===")
    
    # Step 1: Basic validation
    print("\nStep 1: Basic Validation")
    if not key:
        print("❌ ERROR: Key is empty or None")
        return False
    
    # Step 2: Length check
    print("\nStep 2: Length Check")
    key_length = len(key)
    if key_length == 88:
        print("✅ Correct length (88 characters)")
    else:
        print(f"❌ ERROR: Expected 88 characters, got {key_length}")
        return False

    # Step 3: Character validation
    print("\nStep 3: Character Validation")
    valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    invalid_chars = set(char for char in key if char not in valid_chars)
    
    if invalid_chars:
        print("❌ ERROR: Found invalid characters:")
        print(f"   Invalid characters: {sorted(invalid_chars)}")
        return False
    else:
        print("✅ All characters are valid base58")

    # Step 4: Base58 decode test
    print("\nStep 4: Base58 Decode Test")
    try:
        decoded = base58.b58decode(key)
        if len(decoded) == 64:
            print("✅ Successfully decoded to 64 bytes")
        else:
            print(f"❌ ERROR: Decoded to {len(decoded)} bytes (expected 64)")
            return False
    except Exception as e:
        print(f"❌ ERROR: Failed to decode: {str(e)}")
        return False

    # Step 5: Security pattern
    if show_pattern:
        print("\nStep 5: Key Pattern (for verification)")
        print(f"First 4 chars: {key[:4]}")
        print(f"Last 4 chars: {key[-4:]}")
        print(f"Pattern: {key[:4]}{'*' * 80}{key[-4:]}")

    return True

if __name__ == "__main__":
    print("Loading and verifying private key...")
    key = kz.BULLX_NEO_PRIVATE_KEY_QM
    success = verify_private_key(key)
    
    if success:
        print("\n✅ SUCCESS: Private key is valid and properly formatted!")
    else:
        print("\n❌ ERROR: Private key validation failed!")
        print("\nCommon fixes:")
        print("1. Ensure key is exactly 88 characters")
        print("2. Remove any quotes, spaces, or special characters")
        print("3. Only use base58 characters (1-9, A-Z except I,O, a-z except l)")