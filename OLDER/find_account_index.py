from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from solders.keypair import Keypair
import os
from dotenv import load_dotenv

# Load mnemonic from .env
load_dotenv()
mnemonic = os.getenv("MNEMONIC")
passphrase = os.getenv("BIP39_PASSPHRASE", "")

TARGET_ADDRESS = "zX74rvF1LsrqEHhXxskFEephVL4bnDdUrFDfAwvjpmA"

print(f"\n🔍 Searching for wallet derivation path...")
print(f"🎯 Target address: {TARGET_ADDRESS}")
print(f"📝 Using mnemonic: {mnemonic}")
print(f"🔑 Using passphrase: {'[empty]' if not passphrase else '[redacted]'}\n")

# Try different derivation patterns
def try_derivation_patterns(seed_bytes, account_index):
    patterns = [
        # Standard Solana path
        lambda: (
            Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
            .Purpose()
            .Coin()
            .Account(account_index)
        ),
        # With change level
        lambda: (
            Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
            .Purpose()
            .Coin()
            .Account(account_index)
            .Change(Bip44Changes.CHAIN_EXT)
        ),
        # With address index
        lambda: (
            Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)
            .Purpose()
            .Coin()
            .Account(account_index)
            .Change(Bip44Changes.CHAIN_EXT)
            .AddressIndex(0)
        )
    ]
    
    for i, pattern in enumerate(patterns):
        try:
            ctx = pattern()
            priv = ctx.PrivateKey().Raw().ToBytes()
            keypair = Keypair.from_seed(priv)
            path = f"m/44'/501'/{account_index}'" + ("" if i == 0 else "/0'" if i == 1 else "/0'/0'")
            print(f"[{account_index}][Path: {path}] 👉 {keypair.pubkey()}")
            
            if str(keypair.pubkey()) == TARGET_ADDRESS:
                print(f"\n✅ FOUND MATCH!")
                print(f"Account Index: {account_index}")
                print(f"Derivation Path: {path}")
                return True
                
        except Exception as e:
            print(f"[{account_index}][Pattern {i}] ❌ Error: {e}")
    return False

# Generate seed
seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)

# Try first 50 account indices
for account_index in range(50):
    if try_derivation_patterns(seed_bytes, account_index):
        break
