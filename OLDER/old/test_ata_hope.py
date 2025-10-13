import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import AccountMeta, Instruction
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"  # Devnet USDC

async def get_airdrop(client: AsyncClient, wallet: Pubkey) -> bool:
    """Get airdrop with balance verification"""
    try:
        initial_balance = await client.get_balance(wallet)
        print(f"\n💰 Current balance: {initial_balance.value/1e9} SOL")
        
        if initial_balance.value >= 1_000_000_000:
            print("✅ Wallet already funded")
            return True
            
        print("Requesting 1 SOL airdrop...")
        sig = await client.request_airdrop(wallet, 1_000_000_000)
        print(f"✅ Airdrop requested: {sig.value}")
        
        for _ in range(30):  # 30 second timeout
            new_balance = await client.get_balance(wallet)
            if new_balance.value > initial_balance.value:
                print(f"✅ Balance increased to {new_balance.value/1e9} SOL")
                return True
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        return False
    except Exception as e:
        print(f"❌ Airdrop error: {str(e)}")
        return False

async def create_ata(client: AsyncClient, wallet: Keypair, mint: Pubkey) -> bool:
    """Create Associated Token Account"""
    try:
        # Derive ATA address
        seeds = [
            bytes(wallet.pubkey()),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ]
        
        # Find PDA
        bump = 255
        while bump >= 0:
            try:
                seeds_with_bump = seeds + [bytes([bump])]
                ata_address = Pubkey.create_program_address(seeds_with_bump, ASSOCIATED_TOKEN_PROGRAM_ID)
                print(f"\n📍 Found ATA address: {ata_address}")
                break
            except:
                bump -= 1
                
        if bump < 0:
            raise Exception("Could not find valid PDA")
            
        # Check if account exists
        info = await client.get_account_info(ata_address)
        if info.value is not None:
            print("✅ ATA already exists")
            return True
            
        print("\n🏗️ Creating ATA...")
        
        # Create ATA instruction
        create_ata_ix = Instruction(
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=wallet.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=ata_address, is_signer=False, is_writable=True),
                AccountMeta(pubkey=wallet.pubkey(), is_signer=False, is_writable=False),
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
            ],
            data=b""
        )
        
        # Add compute budget
        budget_ix = [
            set_compute_unit_limit(200_000),
            set_compute_unit_price(10_000)
        ]
        
        # Build transaction
        blockhash = await client.get_latest_blockhash(Confirmed)
        msg = MessageV0.try_compile(
            payer=wallet.pubkey(),
            instructions=budget_ix + [create_ata_ix],
            recent_blockhash=blockhash.value.blockhash,
            address_lookup_table_accounts=[]
        )
        
        tx = VersionedTransaction(msg, [wallet])
        print("\n📡 Sending transaction...")
        result = await client.send_transaction(tx)
        print(f"Transaction sent: {result.value}")
        
        # Wait for confirmation
        for _ in range(30):  # 30 second timeout
            confirm = await client.get_transaction(result.value)
            if confirm and confirm.value:
                meta = getattr(confirm.value, 'meta', None)
                if meta:
                    if meta.err:
                        raise Exception(f"Transaction failed: {meta.err}")
                    print("\n✅ ATA created successfully!")
                    
                    # Verify account
                    info = await client.get_account_info(ata_address)
                    if info.value:
                        print("\n📊 ATA Details:")
                        print(f"Owner: {info.value.owner}")
                        print(f"Lamports: {info.value.lamports}")
                        print(f"Data length: {len(info.value.data)}")
                    return True
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        return False
        
    except Exception as e:
        print(f"\n❌ Error creating ATA: {str(e)}")
        return False

async def main():
    # Create test wallet
    wallet = Keypair()
    print(f"🔑 Test wallet created: {wallet.pubkey()}")
    
    # Try various devnet endpoints for airdrop
    for endpoint in [
        "https://api.devnet.solana.com",
        "https://devnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315",
        "https://valry-c5zjvr-fast-devnet.helius-rpc.com"
    ]:
        print(f"\nTrying endpoint: {endpoint}")
        client = AsyncClient(endpoint, commitment=Confirmed)
        try:
            if await get_airdrop(client, wallet.pubkey()):
                break
        finally:
            await client.close()
    
    # Verify funding before proceeding
    client = AsyncClient("https://devnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315", commitment=Confirmed)
    try:
        balance = await client.get_balance(wallet.pubkey())
        if balance.value < 1_000_000_000:
            print(f"\n❌ Insufficient balance: {balance.value/1e9} SOL")
            return
    try:
        mint = Pubkey.from_string(TEST_TOKEN)
        if await create_ata(client, wallet, mint):
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Failed to create ATA")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
