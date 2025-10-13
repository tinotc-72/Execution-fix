import base64
import struct

# The successful trade program data
encoded_data = 'vdt/007mYe54baTH8YZAzX2YK7dmS6MzE76uVcW1yCCNjc1GM6SpP5PnRa8AAAAAv4YT+0JKAAABDQrJSOqMzHXMXQxQqrnfCaHHahKftcI3VjpunWx2xnqiuFZoAAAAAHpv90YIAAAAbjL0k4Y3AwB6w9NKAQAAAG6a4Uf1OAIAg4R0KS5nWpS0NuywqZiJQjKKg93GIzgClhJnxc1hF8tfAAAAAAAAAJxDqgEAAAAAASLoKwMOQcY6slkkLP6yfWzEKjSaGq2fX1KlaE+0MTkFAAAAAAAAAFpvFgAAAAAA'
data = base64.b64decode(encoded_data)

print(f"Total data length: {len(data)} bytes")
print(f"\nHex dump:")

# Print hex dump in 32-byte chunks
for i in range(0, len(data), 32):
    chunk = data[i:i+32]
    print(f"{i:04x}: {chunk.hex()}")

# Try to identify known structures
print("\nPossible structure analysis:")
print(f"First 4 bytes (discriminator?): {data[:4].hex()}")
print(f"Next 4 bytes (padding?): {data[4:8].hex()}")
print(f"Next 8 bytes: {data[8:16].hex()}")
print(f"Next 32 bytes (pubkey?): {data[16:48].hex()}")
print(f"Next 8 bytes: {data[48:56].hex()}")

# Try to decode any u64/u32 values
try:
    amount = int.from_bytes(data[56:64], 'little')
    print(f"\nPossible amount (u64): {amount} lamports ({amount/1e9:.9f} SOL)")
except:
    print("Failed to decode amount")
