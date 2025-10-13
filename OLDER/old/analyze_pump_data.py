"""
Analyze PUMP router instruction data format.
"""
import base64
import binascii

# Instruction data from mainnet tx
ix_data_b64 = "57rQahYVzDKpAxTmJ5dZtsfoPzp1AVfuxRq6b2wUaxxGACKqxoXxeNK"

try:
    # Try decoding with padding
    decoded = base64.b64decode(ix_data_b64 + "==")
    print(f"Decoded (with padding):")
    print(f"Hex: {decoded.hex()}")
    print(f"Length: {len(decoded)} bytes")
except binascii.Error as e:
    print(f"Error with padding: {e}")

try:
    # Try URL-safe base64
    decoded = base64.urlsafe_b64decode(ix_data_b64 + "==")
    print(f"\nDecoded (URL-safe):")
    print(f"Hex: {decoded.hex()}")
    print(f"Length: {len(decoded)} bytes")
except binascii.Error as e:
    print(f"Error with URL-safe: {e}")

# Also analyze the data from index 4 instruction
other_data = "AJTQ2h9DXrBfpLXbk5khAgHwKWDyLGKVR"
try:
    # Try URL-safe base64
    decoded = base64.urlsafe_b64decode(other_data + "==")
    print(f"\nAlternate data (URL-safe):")
    print(f"Hex: {decoded.hex()}")
    print(f"Length: {len(decoded)} bytes")
except binascii.Error as e:
    print(f"Error with alternate: {e}")
