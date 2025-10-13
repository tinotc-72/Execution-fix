import os
import base58
from solders.keypair import Keypair
from dotenv import load_dotenv

load_dotenv()

phantom_key = os.getenv("PHANTOM_PRIVATE_KEY")
if not phantom_key:
    raise ValueError("PHANTOM_PRIVATE_KEY")

private_key_bytes = base58.b58decode(phantom_key)
wallet = Keypair.from_bytes(private_key_bytes)

print("✅ Loaded wallet from Phantom private key:", wallet.pubkey())
