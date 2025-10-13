import asyncio
import json
import subprocess
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
import base58

# Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"  # Devnet USDC

async def main():
    try:
        # Create test wallet
        wallet = Keypair()
        print(f"🔑 Test wallet created: {wallet.pubkey()}")
        
        # Save keypair to file for solana CLI
        keypair_bytes = bytes(wallet)
        keypair_b58 = base58.b58encode(keypair_bytes).decode()
        with open("test-wallet.json", "w") as f:
            json.dump([int(b) for b in keypair_bytes], f)
            
        print("\n💸 Requesting airdrop via solana CLI...")
        try:
            subprocess.run(
                ["solana", "airdrop", "1", str(wallet.pubkey()), "--keypair", "test-wallet.json", "--url", "devnet"],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"Airdrop failed: {e.stderr}")
            
        # Switch to Helius secure endpoint for ATA creation
        print("\n🔄 Connecting to Helius endpoint...")
        client = AsyncClient("https://valry-c5zjvr-fast-devnet.helius-rpc.com", commitment=Confirmed)
        
        # Verify balance
        balance = await client.get_balance(wallet.pubkey())
        print(f"💰 Balance: {balance.value/1e9} SOL")
        
        if balance.value < 1_000_000_000:
            raise Exception("Insufficient balance after airdrop")
            
        # Create ATA
        mint = Pubkey.from_string(TEST_TOKEN)
        owner = wallet.pubkey()
        
        seeds = [
            bytes(owner),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ]
        
        # Find ATA address
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
            return
            
        print("\n🏗️ Creating ATA...")
        
        # Create ATA instruction
        create_ata_ix = Instruction(
            program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=wallet.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=ata_address, is_signer=False, is_writable=True),
                AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
            ],
            data=b""
        )
        
        # Add compute budget instructions
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
        
        # Send and confirm
        print("\n📡 Sending transaction...")
        result = await client.send_transaction(tx)
        print(f"Transaction sent: {result.value}")
        
        # Wait for confirmation
        for i in range(30):
            try:
                confirm = await client.get_transaction(result.value)
                if confirm.value:
                    if hasattr(confirm.value, 'meta') and confirm.value.meta:
                        if confirm.value.meta.err:
                            raise Exception(f"Transaction failed: {confirm.value.meta.err}")
                        print("\n✅ ATA created successfully!")
                        
                        # Verify account exists
                        info = await client.get_account_info(ata_address)
                        if info.value:
                            print("\n📊 ATA Details:")
                            print(f"Owner: {info.value.owner}")
                            print(f"Lamports: {info.value.lamports}")
                            print(f"Data length: {len(info.value.data)}")
                        break
            except Exception as e:
                print(f"Error checking status: {str(e)}")
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        try:
            if client:
                await client.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
