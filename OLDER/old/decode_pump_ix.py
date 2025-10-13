import base58
import base64
from pprint import pprint

# Our current instruction data (hex)
our_data = bytes.fromhex("bddb7fd34ee661ee") + bytes.fromhex("bc07c56e60ad3d3f177382eac6548fba1fd32cfd90ca02b3e7cfa185fdce7398") + (10000000).to_bytes(8, 'little')

# Working instruction data (base58)
working_data = "57rQahYVzDKpAxTmJ5dZtsfoPzp1AVfuxRq6b2wUaxxGACKqxoXxeNK"

print("Our instruction data:")
print(f"Raw (hex): {our_data.hex()}")
print(f"Base58: {base58.b58encode(our_data).decode()}")

print("\nWorking instruction data:")
print(f"Base58: {working_data}")
working_bytes = base58.b58decode(working_data)
print(f"Raw (hex): {working_bytes.hex()}")

print("\nFirst 8 bytes (discriminator):")
print(f"Ours: {our_data[:8].hex()}")
print(f"Working: {working_bytes[:8].hex()}")
