#!/usr/bin/env python3
"""
ATA creation test using our proven successful patterns
"""

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

# Constants from the working tests
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"  # Devnet USDC

# RPC Configuration - Using all available endpoints
DEVNET_ENDPOINTS = [
    "https://api.devnet.solana.com",  # Public devnet
    "https://valry-c5zjvr-fast-devnet.helius-rpc.com",  # Secure RPC
    "https://devnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315",  # RPC with API key
    "https://eclipse.helius-rpc.com/"  # Shared Eclipse URL
]

async def try_airdrop(wallet: Pubkey, amount: int = 1_000_000_000) -> bool:
    """Our proven airdrop function that worked"""
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop...")
    
    # Only try public devnet for airdrop - it's the only one that should work
    endpoint = "https://api.devnet.solana.com"
    client = None
    
    try:
        print(f"\nRequesting airdrop from {endpoint}...")
        client = AsyncClient(endpoint, commitment=Confirmed)
        
        # Get initial balance
        initial_balance = await client.get_balance(wallet)
        print(f"Current balance: {initial_balance.value/1e9} SOL")
        
        # Try multiple times with the same endpoint
        for attempt in range(3):
            try:
                print(f"\nAttempt {attempt + 1}...")
                
                # Request airdrop
                sig = await client.request_airdrop(wallet, amount)
                if not sig or not hasattr(sig, 'value'):
                    print("No valid signature returned")
                    continue
                    
                print(f"Airdrop requested: {sig.value}")
                print("Waiting for confirmation", end="")
                
                # Wait for confirmation using balance check
                start_time = time.time()
                while time.time() - start_time < 30:
                    try:
                        new_balance = await client.get_balance(wallet)
                        if new_balance.value > initial_balance.value:
                            print(f"\n✅ Balance increased to {new_balance.value/1e9} SOL")
                            return True
                            
                        status = await client.get_signature_statuses([sig.value])
                        if status and status.value[0]:
                            if status.value[0].err:
                                print(f"\n❌ Transaction failed: {status.value[0].err}")
                                break
                                
                    except Exception as e:
                        print(f"\nError checking status: {type(e).__name__}: {str(e)}")
                        
                    await asyncio.sleep(1)
                    print(".", end="", flush=True)
                    
                print("\nTiming out, will retry...")
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"\nError on attempt {attempt + 1}: {type(e).__name__}: {str(e)}")
                if attempt < 2:
                    await asyncio.sleep(2)
                    
        print("\n❌ All airdrop attempts failed")
        return False
        
    except Exception as e:
        print(f"\n❌ Airdrop error: {type(e).__name__}: {str(e)}")
        return False
        
    finally:
        if client:
            await client.close()

async def create_ata(client: AsyncClient, wallet: Keypair, mint: Pubkey) -> bool:
    """Create Associated Token Account with minimal complexity"""
    try:
        # Derive ATA address
        seeds = [
            bytes(wallet.pubkey()),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ]
        
        ata_address, _ = Pubkey.find_program_address(
            seeds,
            ASSOCIATED_TOKEN_PROGRAM_ID
        )
        
        print(f"\n🏦 Creating ATA at: {ata_address}")
        
        # Check if account exists
        info = await client.get_account_info(ata_address)
        if info.value is not None:
            print("✅ ATA already exists")
            return True
            
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
            data=b""
        )
        
        # Add compute budget
        budget_ix = [
            set_compute_unit_limit(200_000),
            set_compute_unit_price(10_000)
        ]
        
        # Get blockhash
        blockhash = await client.get_latest_blockhash(Confirmed)
        
        # Build transaction
        msg = MessageV0.try_compile(
            payer=wallet.pubkey(),
            instructions=budget_ix + [create_ata_ix],
            recent_blockhash=blockhash.value.blockhash,
            address_lookup_table_accounts=[]
        )
        
        tx = VersionedTransaction(msg, [wallet])
        
        # Send transaction
        print("\n📡 Sending transaction...")
        sig = await client.send_transaction(tx)
        print(f"Transaction sent: {sig.value}")
        
        # Wait for confirmation
        for _ in range(30):
            status = await client.get_signature_statuses([sig.value])
            if status.value[0] is not None:
                if status.value[0].err:
                    raise Exception(f"Transaction failed: {status.value[0].err}")
                if status.value[0].confirmation_status in ['confirmed', 'finalized']:
                    print(f"\n✅ ATA created successfully!")
                    return True
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        raise Exception("Transaction not confirmed")
        
    except Exception as e:
        print(f"\n❌ Error creating ATA: {e}")
        return False

async def main():
    """End-to-end test using proven patterns"""
    try:
        print("\n🔬 Testing ATA Creation")
        print("=" * 50)
        
        # Create test wallet
        wallet = Keypair()
        print(f"\n🔑 Test wallet: {wallet.pubkey()}")
        
        # Get airdrop using our proven method
        if not await try_airdrop(wallet.pubkey()):
            print("❌ Could not fund wallet")
            return
            
        # Create ATA using Helius endpoint
        client = AsyncClient(DEVNET_ENDPOINTS[1], commitment=Confirmed)
        try:
            # Create ATA for test token
            mint = Pubkey.from_string(TEST_TOKEN)
            if await create_ata(client, wallet, mint):
                print("\n✅ Test completed successfully!")
            else:
                print("\n❌ Failed to create ATA")
        finally:
            await client.close()
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
