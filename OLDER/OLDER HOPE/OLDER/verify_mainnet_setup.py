import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
import base58
from env_keys import kz

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def verify_mainnet_setup(client: AsyncClient, pubkey: Pubkey):
    """Verify the mainnet setup and account state"""
    try:
        # Check connection
        version = await client.get_version()
        print(f"✅ Connected to Solana {version.value}")
        
        # Check current slot
        slot = await client.get_slot()
        print(f"✅ Current slot: {slot.value}")
        
        # Check balance
        balance = await get_balance(client, pubkey)
        print(f"💰 Wallet balance: {balance:.4f} SOL")
        
        if balance < 0.05:
            print("⚠️  Warning: Balance is low. For trading, recommend at least 0.05 SOL")
        else:
            print("✅ Balance is sufficient for trading")
            
        # Check recent blockhash (needed for transactions)
        recent = await client.get_latest_blockhash()
        print(f"✅ Latest blockhash: {recent.value.blockhash}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def main():
    print("🚀 Mainnet Trading Setup Check")
    print("==============================")
    
    # Load wallet
    try:
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
    except Exception as e:
        print(f"❌ Failed to load wallet: {str(e)}")
        return False

    # Connect to mainnet
    client = AsyncClient(kz.HELIUS_RPC_URL)
    try:
        success = await verify_mainnet_setup(client, keypair.pubkey())
        if success:
            print("\n✅ Mainnet setup verification complete!")
            print("\nNext steps:")
            print("1. Transfer a small amount of SOL (0.05-0.1) to your trading wallet")
            print("2. Run this check again to verify the transfer")
            print("3. Once verified, we can proceed with trading setup")
        else:
            print("\n❌ Mainnet setup verification failed!")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
