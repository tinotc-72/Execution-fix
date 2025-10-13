import json
from solders.keypair import Keypair

with open("my_wallet.json", "r") as f:
    secret_bytes = bytes(json.load(f))

wallet = Keypair.from_bytes(secret_bytes)
print("✅ Loaded wallet with public key:", wallet.pubkey())
