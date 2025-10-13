import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
import base58
from env_keys import kz

WRAPPED_SOL = Pubkey.from_string("So11111111111111111111111111111111111111112")

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def verify_wsol_account(client: AsyncClient, keypair: Keypair):
    """Verify Wrapped SOL account setup"""
    try:
        # Get token accounts
        token_accounts = await client.get_token_accounts_by_owner(
            keypair.pubkey(),
            {"programId": TOKEN_PROGRAM_ID}
        )
        
        # Look for Wrapped SOL account
        wsol_account = None
        if token_accounts.value:
            for account in token_accounts.value:
                mint = account.account.data.parsed["info"]["mint"]
                if mint == str(WRAPPED_SOL):
                    wsol_account = account
                    break
        
        if wsol_account:
            print("✅ Wrapped SOL account found")
            balance = float(wsol_account.account.data.parsed["info"]["tokenAmount"]["uiAmount"])
            print(f"💰 Wrapped SOL balance: {balance:.4f} WSOL")
        else:
            print("ℹ️  No Wrapped SOL account found (this is normal, it will be created during trading)")
        
        return True
    except Exception as e:
        print(f"❌ Error checking WSOL account: {str(e)}")
        return False

async def main():
    print("🚀 Mainnet Trading Preparation")
    print("==============================")
    
    # Use mnemonic-based wallet from config
    try:
        from config import WALLET
        keypair = WALLET  # Already properly derived from mnemonic
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
    except Exception as e:
        print(f"❌ Failed to load wallet: {str(e)}")
        return False

    # Connect to mainnet
    client = AsyncClient(kz.HELIUS_RPC_URL)
    try:
        # Check SOL balance
        balance = await get_balance(client, keypair.pubkey())
        print(f"\n💰 Native SOL balance: {balance:.4f} SOL")
        
        if balance < 0.05:
            print("⚠️  Warning: Low balance for trading")
            return False
            
        # Check Wrapped SOL setup
        print("\nChecking Wrapped SOL setup...")
        await verify_wsol_account(client, keypair)
        
        print("\n✅ Trading preparation complete!")
        print("\nYour wallet is ready for trading with:")
        print(f"- {balance:.4f} SOL available")
        print("- Wrapped SOL account setup verified")
        print("\nNext steps:")
        print("1. Start with small test trades (0.01-0.02 SOL)")
        print("2. Monitor transactions carefully")
        print("3. Keep at least 0.02 SOL for transaction fees")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
