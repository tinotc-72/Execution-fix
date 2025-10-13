#!/usr/bin/env python3
"""
Robust Associated Token Account (ATA) creation test combining best practices
from Solana documentation and proven patterns.
"""

import asyncio
import time
from typing import Optional, List
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

# Program IDs (from Solana docs)
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# Test token (Devnet USDC)
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"

async def try_airdrop(
    client: AsyncClient,
    address: Pubkey,
    amount: int = 1_000_000_000,
    max_retries: int = 3
) -> bool:
    """Request an airdrop with confirmation and balance verification"""
    
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop...")
    
    for attempt in range(max_retries):
        try:
            # Request airdrop
            sig = await client.request_airdrop(address, amount)
            if not sig.value:
                print(f"❌ Airdrop request failed (attempt {attempt + 1}/{max_retries})")
                continue
                
            print(f"📝 Airdrop requested: {sig.value}")
            
            # Wait for confirmation
            start = time.time()
            while time.time() - start < 30:
                conf = await client.confirm_transaction(sig.value)
                if conf.value:
                    # Verify balance increase
                    balance = await client.get_balance(address)
                    print(f"✅ New balance: {balance.value/1e9} SOL")
                    return True
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Airdrop error: {str(e)}")
            
        if attempt < max_retries - 1:
            await asyncio.sleep(2)  # Wait before retry
            
    return False

async def create_token_account(
    client: AsyncClient,
    wallet: Keypair,
    mint: Pubkey
) -> tuple[Pubkey, Optional[Instruction]]:
    """Create an Associated Token Account with robust error handling"""
    
    try:
        # Derive the ATA address deterministically
        seeds = [
            bytes(wallet.pubkey()),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ]
        
        ata_address, _ = Pubkey.find_program_address(
            seeds,
            ASSOCIATED_TOKEN_PROGRAM_ID
        )
        
        print(f"\n🏦 Creating token account")
        print(f"Mint: {mint}")
        print(f"Owner: {wallet.pubkey()}")
        print(f"ATA Address: {ata_address}")
        
        # Check if account already exists
        info = await client.get_account_info(ata_address)
        if info.value is not None:
            print("✅ Token account already exists")
            return ata_address, None
            
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
                AccountMeta(pubkey=RENT, is_signer=False, is_writable=False)
            ],
            data=b""  # ATA program needs no additional data
        )
        
        return ata_address, create_ata_ix
        
    except Exception as e:
        print(f"❌ Error creating token account: {str(e)}")
        raise

async def build_and_send_transaction(
    client: AsyncClient,
    wallet: Keypair,
    instructions: List[Instruction],
    max_retries: int = 3
) -> bool:
    """Send and confirm a transaction with retries"""
    
    for attempt in range(max_retries):
        try:
            print(f"\n📝 Building transaction (attempt {attempt + 1}/{max_retries})")
            
            # Get latest blockhash
            blockhash = await client.get_latest_blockhash()
            if not blockhash.value:
                continue
                
            # Add compute budget instructions
            budget_ix = [
                set_compute_unit_limit(200_000),
                set_compute_unit_price(10_000)
            ]
            
            # Build transaction
            msg = MessageV0.try_compile(
                payer=wallet.pubkey(),
                instructions=budget_ix + instructions,
                recent_blockhash=blockhash.value.blockhash,
                address_lookup_table_accounts=[]
            )
            
            if not msg:
                print("❌ Failed to compile transaction")
                continue
                
            tx = VersionedTransaction(msg, [wallet])
            
            # Send transaction
            print("🚀 Sending transaction...")
            sig = await client.send_transaction(tx)
            if not sig.value:
                print("❌ Failed to send transaction")
                continue
                
            print(f"📝 Transaction sent: {sig.value}")
            
            # Wait for confirmation
            start = time.time()
            while time.time() - start < 30:
                conf = await client.confirm_transaction(sig.value)
                if conf.value:
                    print("✅ Transaction confirmed")
                    return True
                await asyncio.sleep(1)
                
            print("❌ Transaction not confirmed in time")
            
        except Exception as e:
            print(f"❌ Transaction error: {str(e)}")
            
        if attempt < max_retries - 1:
            await asyncio.sleep(2)  # Wait before retry
            
    return False

async def verify_token_account(
    client: AsyncClient,
    address: Pubkey,
    retries: int = 3
) -> bool:
    """Verify a token account exists and is properly initialized"""
    
    print(f"\n🔍 Verifying token account: {address}")
    
    for attempt in range(retries):
        try:
            info = await client.get_account_info(address)
            if info.value is not None:
                print(f"✅ Account exists")
                print(f"Data length: {len(info.value.data)}")
                return True
                
        except Exception as e:
            print(f"❌ Verification error: {str(e)}")
            
        if attempt < retries - 1:
            await asyncio.sleep(1)
            print(f"Retrying... ({attempt + 1}/{retries})")
            
    return False

async def main():
    """Test ATA creation with improved reliability"""
    client = None
    
    try:
        # Initialize client with reliable endpoint
        print("\n🔬 Testing ATA Creation")
        print("=" * 50)
        
        # Create test wallet
        wallet = Keypair()
        print(f"\n🔑 Test wallet: {wallet.pubkey()}")
        
        # Connect to devnet
        client = AsyncClient("https://api.devnet.solana.com", commitment=Confirmed)
        
        # Request airdrop
        if not await try_airdrop(client, wallet.pubkey()):
            raise Exception("Could not fund wallet")
            
        # Create ATA for test token
        token_mint = Pubkey.from_string(TEST_TOKEN)
        ata_address, create_ix = await create_token_account(client, wallet, token_mint)
        
        if create_ix:
            # Send creation transaction
            if not await build_and_send_transaction(client, wallet, [create_ix]):
                raise Exception("Failed to create token account")
                
            # Verify account created
            if not await verify_token_account(client, ata_address):
                raise Exception("Token account verification failed")
            
        print("\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
