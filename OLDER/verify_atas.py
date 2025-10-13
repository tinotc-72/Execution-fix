import asyncio
from initialize_trading import AccountSetup
from solders.keypair import Keypair
import base58
from env_keys import kz
from solders.pubkey import Pubkey

async def main():
    print("🔍 Verifying Trading Account Setup")
    print("==================================")
    
    # Load wallet
    try:
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
    except Exception as e:
        print(f"❌ Failed to load wallet: {str(e)}")
        return

    # Initialize account setup
    setup = AccountSetup(keypair)
    
    # Common tokens to verify
    tokens_to_check = [
        "So11111111111111111111111111111111111111112",   # Wrapped SOL
    ]
    
    for token in tokens_to_check:
        token_mint = Pubkey.from_string(token)
        print(f"\n🔍 Checking ATA for token: {token}")
        exists = await setup.check_and_create_ata(token_mint)
        if exists:
            print(f"✅ ATA verified for {token}")
        else:
            print(f"❌ ATA needs creation for {token}")
    
    await setup.client.close()

if __name__ == "__main__":
    asyncio.run(main())
