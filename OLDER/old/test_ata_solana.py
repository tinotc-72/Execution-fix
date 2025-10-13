#!/usr/bin/env python3
"""
Test Associated Token Account (ATA) creation following official Solana documentation
"""

import asyncio
import time
from typing import Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import AccountMeta, Instruction
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

# Program IDs (from Solana docs)
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# Test token (Devnet USDC)
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"

async def find_ata_address(wallet: Pubkey, mint: Pubkey) -> tuple[Pubkey, int]:
    """Find the Associated Token Account address deterministically"""
    seeds = [
        bytes(wallet),
        bytes(TOKEN_PROGRAM_ID),
        bytes(mint)
    ]
    
    return Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)

async def get_minimum_balance_for_rent_exemption(client: AsyncClient, data_size: int) -> int:
    """Get minimum balance for rent exemption"""
    resp = await client.get_minimum_balance_for_rent_exemption(data_size)
    return resp.value

async def create_associated_token_account(
    client: AsyncClient,
    payer: Keypair,
    wallet: Pubkey,
    mint: Pubkey
) -> tuple[Pubkey, Optional[Instruction]]:
    """Create ATA following Solana documentation pattern"""
    
    # Find ATA address deterministically
    ata_address, _ = await find_ata_address(wallet, mint)
    print(f"\n🔍 Derived ATA address: {ata_address}")
    
    # Check if account already exists
    info = await client.get_account_info(ata_address)
    if info.value is not None:
        print("✅ ATA already exists")
        return ata_address, None
        
    print("\n🏗️ Creating ATA...")
    
    # Create ATA instruction exactly as specified in Solana docs
    instruction = Instruction(
        program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
        accounts=[
            AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=ata_address, is_signer=False, is_writable=True),
            AccountMeta(pubkey=wallet, is_signer=False, is_writable=False),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=RENT, is_signer=False, is_writable=False)
        ],
        data=b""  # No additional data needed
    )
    
    return ata_address, instruction

async def try_airdrop(client: AsyncClient, address: Pubkey, amount: int = 1_000_000_000) -> bool:
    """Request airdrop with verification"""
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop...")
    
    # Get initial balance
    initial_balance = await client.get_balance(address)
    print(f"Initial balance: {initial_balance.value/1e9} SOL")
    
    try:
        # Request airdrop
        sig = await client.request_airdrop(address, amount)
        print(f"Airdrop requested: {sig.value}")
        
        # Wait for confirmation via balance check
        start_time = time.time()
        while time.time() - start_time < 30:
            new_balance = await client.get_balance(address)
            if new_balance.value > initial_balance.value:
                print(f"✅ Airdrop confirmed! New balance: {new_balance.value/1e9} SOL")
                return True
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        print(f"\n❌ Airdrop not confirmed after 30 seconds")
        return False
        
    except Exception as e:
        print(f"Error requesting airdrop: {str(e)}")
        return False

async def main():
    """Test ATA creation with Solana documentation pattern"""
    client = None
    
    try:
        # Setup
        print("\n🔬 Testing ATA Creation (Solana Docs Pattern)")
        print("=" * 50)
        
        # Create test wallet
        wallet = Keypair()
        print(f"\n🔑 Test wallet: {wallet.pubkey()}")
        
        # Connect to devnet
        client = AsyncClient("https://api.devnet.solana.com", commitment=Confirmed)
        
        # Fund wallet
        if not await try_airdrop(client, wallet.pubkey()):
            raise Exception("Could not fund wallet")
            
        # Verify funding
        balance = await client.get_balance(wallet.pubkey())
        print(f"Wallet balance: {balance.value/1e9} SOL")
        
        # Create ATA for test token
        token_mint = Pubkey.from_string(TEST_TOKEN)
        ata_address, create_ix = await create_associated_token_account(
            client,
            wallet,
            wallet.pubkey(),
            token_mint
        )
        
        if create_ix:
            # Create transaction
            blockhash = await client.get_latest_blockhash()
            
            msg = MessageV0.try_compile(
                payer=wallet.pubkey(),
                instructions=[create_ix],
                recent_blockhash=blockhash.value.blockhash,
                address_lookup_table_accounts=[]
            )
            
            tx = VersionedTransaction(msg, [wallet])
            
            # Send and confirm
            print("\n📡 Sending transaction...")
            sig = await client.send_transaction(tx)
            print(f"Transaction sent: {sig.value}")
            
            # Monitor for confirmation
            for _ in range(30):
                conf = await client.get_signature_statuses([sig.value])
                if conf.value[0] is not None:
                    status = conf.value[0].confirmation_status
                    if status == "confirmed" or status == "finalized":
                        print(f"\n✅ Transaction confirmed ({status})")
                        
                        # Verify ATA exists
                        info = await client.get_account_info(ata_address)
                        if info.value:
                            print("\n📊 ATA Details:")
                            print(f"Owner: {info.value.owner}")
                            print(f"Data length: {len(info.value.data)}")
                            return
                        
                    elif conf.value[0].err:
                        raise Exception(f"Transaction failed: {conf.value[0].err}")
                        
                await asyncio.sleep(1)
                print(".", end="", flush=True)
                
            print("\n❌ Transaction confirmation timeout")
            
        else:
            print("✅ ATA already exists, no action needed")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
