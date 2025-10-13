"""
Analyze the successful pump.fun transaction instruction data.
"""

import base58
import base64

# Successful transaction instruction data
successful_data = "5487SCD3m9Dep9RQnbBkkRAv8JamV49Qs"

print(f"Successful instruction data: {successful_data}")

# Try to decode as base58
try:
    decoded_b58 = base58.b58decode(successful_data)
    print(f"Base58 decoded (hex): {decoded_b58.hex()}")
    print(f"Base58 decoded (length): {len(decoded_b58)} bytes")
    
    # Check if this matches our discriminator
    if len(decoded_b58) >= 8:
        discriminator = decoded_b58[:8]
        print(f"Discriminator (hex): {discriminator.hex()}")
        
        if len(decoded_b58) > 8:
            payload = decoded_b58[8:]
            print(f"Payload (hex): {payload.hex()}")
            print(f"Payload (length): {len(payload)} bytes")
            
            # Try to parse as amounts (little-endian u64)
            if len(payload) >= 8:
                amount = int.from_bytes(payload[:8], 'little')
                print(f"First amount: {amount} lamports ({amount/1e9:.6f} SOL)")
                
            if len(payload) >= 16:
                amount2 = int.from_bytes(payload[8:16], 'little')
                print(f"Second amount: {amount2} lamports ({amount2/1e9:.6f} SOL)")
                
except Exception as e:
    print(f"Base58 decode failed: {e}")

# Try base64 decode as fallback
try:
    decoded_b64 = base64.b64decode(successful_data + "==")  # Add padding
    print(f"Base64 decoded (hex): {decoded_b64.hex()}")
except Exception as e:
    print(f"Base64 decode failed: {e}")

# Our current discriminator
our_discriminator = "52e177e74e1d2d46"
print(f"\nOur discriminator: {our_discriminator}")
print(f"Our bytes: {bytes.fromhex(our_discriminator)}")
