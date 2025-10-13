"""
Private Key Debug Script
Created: 2025-06-19 00:38:16 UTC
Author: tinotc-72
"""

from env_keys import kz

def debug_private_key(key):
    print("\n=== Private Key Debug Report ===")
    
    # Step 1: Check if key exists
    print("\nStep 1: Checking if key exists")
    if key is None:
        print("❌ ERROR: Key is None - check your .env file")
        return
    print("✅ Key exists")

    # Step 2: Check length
    print("\nStep 2: Checking key length")
    print(f"Length: {len(key)} characters")
    if len(key) == 88:
        print("✅ Correct length (88 characters)")
    else:
        print(f"❌ WARNING: Expected 88 characters, got {len(key)}")

    # Step 3: Check for whitespace
    print("\nStep 3: Checking for whitespace")
    if key != key.strip():
        print("❌ WARNING: Key has leading or trailing whitespace")
        print(f"Key with whitespace: '{key}'")
        print(f"Key without whitespace: '{key.strip()}'")
    else:
        print("✅ No leading/trailing whitespace")

    # Step 4: Check for quotes
    print("\nStep 4: Checking for quotes")
    if '"' in key or "'" in key:
        print("❌ ERROR: Key contains quotes - remove them from .env file")
    else:
        print("✅ No quotes found")

    # Step 5: Check for invalid characters
    print("\nStep 5: Checking for invalid characters")
    valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    invalid_chars = []
    for i, char in enumerate(key):
        if char not in valid_chars:
            invalid_chars.append((i, char))
    
    if invalid_chars:
        print("❌ Found invalid characters:")
        for pos, char in invalid_chars:
            print(f"   Position {pos}: '{char}'")
    else:
        print("✅ All characters are valid base58")

    # Step 6: Print key visualization
    print("\nStep 6: Key visualization")
    print("First 4 characters:", key[:4])
    print("Last 4 characters:", key[-4:])
    print("Key pattern:", "*" * (len(key) - 8) + key[-4:])

if __name__ == "__main__":
    print("Loading private key from .env file...")
    key = kz.BULLX_NEO_PRIVATE_KEY_QM
    debug_private_key(key)
    
    print("\n=== How to fix common issues ===")
    print("1. Make sure your .env file has the key without quotes:")
    print("   BULLX_NEO_PRIVATE_KEY_QM=YourKeyHereWithoutQuotes")
    print("\n2. Make sure there are no spaces around the =:")
    print("   BULLX_NEO_PRIVATE_KEY_QM=YourKey  ✅")
    print("   BULLX_NEO_PRIVATE_KEY_QM = YourKey  ❌")
    print("\n3. Make sure the key is on a single line with no line breaks")