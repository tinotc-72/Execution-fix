import asyncio
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58
from config import kz

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

async def find_ata(wallet: Pubkey, mint: Pubkey) -> Pubkey:
    """Find the associated token account address"""
    return Pubkey.find_program_address(
        [
            bytes(wallet),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )[0]

async def check_token_accounts():
    """Check the state of token accounts"""
    print("\n🔍 Checking Token Accounts")
    print("=" * 50)
    
    try:
        # Initialize client
        client = AsyncClient(kz.HELIUS_RPC_URL)
        
        # Load wallet
        key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        decoded_key = base58.b58decode(key)
        keypair = Keypair.from_bytes(decoded_key)
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
        
        # Check USDC ATA
        usdc_ata = await find_ata(keypair.pubkey(), USDC_MINT)
        print(f"\n📝 USDC ATA: {usdc_ata}")
        
        # Get account info
        account = await client.get_account_info(usdc_ata)
        
        if account.value:
            print("✅ USDC ATA exists")
            print(f"Owner: {account.value.owner}")
            print(f"Lamports: {account.value.lamports}")
            print(f"Data length: {len(account.value.data)}")
            
            # Get token balance
            balance = await client.get_token_account_balance(usdc_ata)
            if balance.value:
                amount = int(balance.value.amount)
                decimals = balance.value.decimals
                print(f"💰 Balance: {amount / (10 ** decimals):.6f} USDC")
            else:
                print("⚠️ Could not fetch token balance")
        else:
            print("❌ USDC ATA does not exist")
            print("ℹ️ You need to create this account before trading")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(check_token_accounts())