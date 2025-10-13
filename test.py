from solders.pubkey import Pubkey
import base58  # Add this import

try:
    # First decode and slice
    decoded_bytes = base58.b58decode("PFcqD6d4DMEhSTnwYEpRDrhHVE6dpPHNGsFGjspx9Bow")[1:]
    print(f"Decoded length: {len(decoded_bytes)}")
    print(f"Decoded bytes: {decoded_bytes.hex()}")
    
    # Then try to create the Pubkey
    program_id = Pubkey.from_bytes(decoded_bytes)
    print(f"Success! Program ID: {program_id}")
    
except Exception as e:
    print(f"Error: {e}")