import asyncio
import time
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction

from solana.rpc.commitment import Confirmed
import base58
from env_keys import kz

# Constants
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
ASSOCIATED_TOKEN_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
WRAPPED_SOL_MINT = "So11111111111111111111111111111111111111112"
COMPUTE_UNIT_LIMIT = 200_000
COMPUTE_UNIT_PRICE = 1_000

async def get_working_client():
    """Try multiple RPC endpoints until we find one that works"""
    endpoints = [
        kz.HELIUS_RPC_URL,
        "https://api.mainnet-beta.solana.com",  # Public mainnet
    ]
    
    for endpoint in endpoints:
        try:
            client = AsyncClient(endpoint, commitment=Confirmed)
            # Test the connection
            await client.get_health()
            print(f"✅ Connected to {endpoint}")
            return client
        except Exception as e:
            print(f"⚠️ Failed to connect to {endpoint}: {str(e)}")
            continue
    
    raise Exception("❌ No working RPC endpoint found")

async def get_token_accounts(client: AsyncClient, wallet_pubkey: str):
    """Get all token accounts for a wallet"""
    try:
        response = await client.get_token_accounts_by_owner(
            wallet_pubkey,
            {"programId": TOKEN_PROGRAM_ID},
        )
        print(f"\n📝 Found {len(response.value)} token accounts:")
        for account in response.value:
            print(f"- Account: {account.pubkey}")
            print(f"  Data: {account.account.data}")
        return response.value
    except Exception as e:
        print(f"⚠️ Error fetching token accounts: {str(e)}")
        return []

async def main():
    print("\n🔍 Advanced Trading Account Setup")
    print("================================")
    
    try:
        # Load wallet
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        print(f"✅ Loaded wallet key")
        
        # Get working client
        client = await get_working_client()
        
        # Check wallet balance first
        balance = await client.get_balance(str(kz.BULLX_NEO_ADDRESS))
        print(f"\n💰 Wallet balance: {balance.value / 1e9:.4f} SOL")
        
        # Get all token accounts
        print("\n🔍 Checking existing token accounts...")
        token_accounts = await get_token_accounts(client, str(kz.BULLX_NEO_ADDRESS))
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
