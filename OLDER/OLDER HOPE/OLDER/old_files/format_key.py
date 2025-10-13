"""
Private Key Formatter
Created: 2025-06-19 00:49:07 UTC
Author: tinotc-72
"""

def format_private_key(key):
    # Remove any whitespace
    key = key.strip()
    
    # Remove any variable interpolation syntax
    key = key.replace('${', '').replace('}', '')
    
    # Check length
    if len(key) != 88:
        print(f"❌ WARNING: Key length is {len(key)}, should be 88")
    
    # Check for valid base58 characters
    valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    invalid_chars = [char for char in key if char not in valid_chars]
    if invalid_chars:
        print(f"❌ WARNING: Found invalid characters: {invalid_chars}")
    
    return key

if __name__ == "__main__":
    print("Enter your private key (it will be masked):")
    key = input().strip()
    
    formatted_key = format_private_key(key)
    
    print("\nFormatted key check:")
    print(f"Length: {len(formatted_key)} characters")
    print(f"First 4 chars: {formatted_key[:4]}")
    print(f"Last 4 chars: {formatted_key[-4:]}")
    
    print("\nCopy this line into your .env file:")
    print(f"BULLX_NEO_PRIVATE_KEY_QM={formatted_key}")