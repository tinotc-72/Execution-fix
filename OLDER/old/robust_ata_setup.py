import asyncio
import time
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.associated_token import ID as ASSOCIATED_TOKEN_PROGRAM_ID
from solders.token.instructions import create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
import base58
from env_keys import kz

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
COMPUTE_UNIT_LIMIT = 200_000
COMPUTE_UNIT_PRICE = 1_000

async def get_working_client():
    """Try multiple RPC endpoints until we find one that works"""
    endpoints = [
        kz.HELIUS_RPC_URL,
        "https://api.devnet.solana.com",  # Public devnet
        "https://api.mainnet-beta.solana.com",  # Public mainnet
    ]
    
    for endpoint in endpoints:
        try:
            client = AsyncClient(endpoint)
            # Test the connection
            await client.get_health()
            print(f"✅ Connected to {endpoint}")
            return client
        except Exception as e:
            print(f"⚠️ Failed to connect to {endpoint}: {str(e)}")
            continue
    
    raise Exception("❌ No working RPC endpoint found")

async def verify_ata(client: AsyncClient, wallet: Pubkey, token_mint: Pubkey) -> tuple[bool, Pubkey]:
    """Verify if ATA exists and return its address"""
    try:
        ata = Pubkey.find_program_address(
            [
                bytes(wallet),
                bytes(TOKEN_PROGRAM_ID),
                bytes(token_mint)
            ],
            ASSOCIATED_TOKEN_PROGRAM_ID
        )[0]
        
        info = await client.get_account_info(ata)
        return bool(info.value), ata
    except Exception as e:
        print(f"⚠️ Error checking ATA: {str(e)}")
        return False, None

async def create_ata(client: AsyncClient, keypair: Keypair, token_mint: Pubkey) -> bool:
    """Create ATA with proper compute budget and retry logic"""
    try:
        # Get the ATA address
        wallet_pubkey = keypair.pubkey()
        exists, ata = await verify_ata(client, wallet_pubkey, token_mint)
        
        if exists:
            print(f"✅ ATA already exists for {token_mint}")
            return True
            
        print(f"🔄 Creating ATA for {token_mint}...")
        
        # Create the instruction
        create_ata_ix = create_associated_token_account(
            payer=wallet_pubkey,
            owner=wallet_pubkey,
            mint=token_mint
        )
        
        # Add compute budget instructions
        compute_ix = [
            set_compute_unit_limit(COMPUTE_UNIT_LIMIT),
            set_compute_unit_price(COMPUTE_UNIT_PRICE)
        ]
        
        # Build and send transaction
        txn = await client.send_transaction(
            compute_ix + [create_ata_ix],
            keypair,
            opts={"skip_preflight": True, "max_retries": 5}
        )
        
        print(f"📝 Transaction sent: {txn.value}")
        
        # Wait for confirmation with timeout
        timeout = time.time() + 30
        while time.time() < timeout:
            conf = await client.confirm_transaction(txn.value)
            if conf.value:
                print(f"✅ ATA created successfully")
                return True
            await asyncio.sleep(1)
            
        print("⚠️ Transaction confirmation timeout")
        return False
            
    except Exception as e:
        print(f"❌ Error creating ATA: {str(e)}")
        return False

async def main():
    print("\n🔍 Advanced Trading Account Setup")
    print("================================")
    
    try:
        # Load wallet
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        print(f"✅ Loaded wallet: {keypair.pubkey()}")
        
        # Get working client
        client = await get_working_client()
        
        # Common trading tokens
        tokens_to_check = [
            "So11111111111111111111111111111111111111112",   # Wrapped SOL
        ]
        
        for token in tokens_to_check:
            print(f"\n🔍 Processing {token}")
            token_mint = Pubkey.from_string(token)
            success = await create_ata(client, keypair, token_mint)
            if not success:
                print(f"⚠️ Failed to setup ATA for {token}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
