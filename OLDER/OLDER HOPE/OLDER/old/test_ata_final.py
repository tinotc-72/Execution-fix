#!/usr/bin/env python3
"""
Final, production-ready test for Associated Token Account (ATA) creation
Implements best practices from Solana cookbook with improved reliability
Author: tinotc-72
"""

import asyncio
import traceback
from typing import List, Optional, Tuple
import time
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import AccountMeta, Instruction
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed, Finalized
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.types import TxOpts
from solana.exceptions import SolanaRpcException

# Import Helius configuration
from config import kz

# Program IDs and Constants
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"  # Devnet USDC

# RPC Configuration with Helius endpoints
DEVNET_ENDPOINTS = [
    kz.SECURE_RPC_URL,     # Fast secure endpoint for transactions
    kz.RPC_URL,            # Standard endpoint
    "https://api.devnet.solana.com"  # Public fallback for airdrops
]

async def with_retries(fn, max_retries=3, initial_delay=1):
    """Execute a function with exponential backoff retries"""
    delay = initial_delay
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception as e:
            last_error = e
            if attempt == max_retries - 1:
                raise
            print(f"⚠️ Attempt {attempt + 1} failed, retrying in {delay}s...")
            await asyncio.sleep(delay)
            delay *= 2
    
    raise last_error

async def try_airdrop(address: Pubkey, amount: int = 1_000_000_000) -> bool:
    """Request airdrop using multiple devnet endpoints"""
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop for {address}")
    
    # Try different devnet endpoints for airdrop
    endpoints = [
        "https://api.devnet.solana.com",
        "https://devnet.genesysgo.net",
        kz.RPC_URL  # Try Helius as last resort
    ]
    
    for endpoint in endpoints:
        client = None
        try:
            print(f"\nTrying airdrop from {endpoint}...")
            client = AsyncClient(endpoint, commitment=Confirmed)
            
            # Get initial balance
            initial_balance = await client.get_balance(address)
            print(f"Initial balance: {initial_balance.value/1e9} SOL")
            
            # Request airdrop
            sig = await client.request_airdrop(address, amount)
            
            if not sig or not sig.value:
                print("Airdrop request failed")
                continue
                
            print(f"Airdrop requested: {sig.value}")
            
            # Wait for confirmation via balance check
            for _ in range(30):
                try:
                    new_balance = await client.get_balance(address)
                    if new_balance.value > initial_balance.value:
                        print(f"✅ Balance increased to {new_balance.value/1e9} SOL")
                        return True
                except Exception as e:
                    print(f"Error checking balance: {str(e)}")
                await asyncio.sleep(1)
                print(".", end="", flush=True)
                
            print(f"\nAirdrop not confirmed on {endpoint}")
            
        except Exception as e:
            print(f"Error with {endpoint}: {str(e)}")
        finally:
            if client:
                await client.close()
    
    return False
    
    try:
        # Get initial balance
        initial_balance = await client.get_balance(address)
        print(f"Initial balance: {initial_balance.value/1e9} SOL")
        
        # Try airdrop with retries
        for attempt in range(3):
            try:
                print(f"\nAirdrop attempt {attempt + 1}...")
                sig = await client.request_airdrop(address, amount)
                
                if not sig:
                    print("No signature returned")
                    continue
                    
                print(f"Airdrop requested: {sig.value}")
                
                # Wait for confirmation via balance check
                print("Waiting for confirmation", end="", flush=True)
                for _ in range(30):
                    try:
                        new_balance = await client.get_balance(address)
                        if new_balance.value > initial_balance.value:
                            print(f"\n✅ Balance increased to {new_balance.value/1e9} SOL")
                            return True
                    except Exception as e:
                        print(f"\nError checking balance: {str(e)}")
                    await asyncio.sleep(1)
                    print(".", end="", flush=True)
                
                print(f"\nAttempt {attempt + 1} timed out")
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"\nError on attempt {attempt + 1}: {str(e)}")
                print(f"Error details: {type(e).__name__}")
                if hasattr(e, '__dict__'):
                    print(f"Error attributes: {e.__dict__}")
                if attempt < 2:  # Don't sleep on last attempt
                    await asyncio.sleep(2)
        
        print("\n❌ All airdrop attempts failed")
        return False
        
    except Exception as e:
        print(f"\n❌ Airdrop error: {str(e)}")
        return False
    finally:
        await client.close()

async def send_and_confirm_tx(client: AsyncClient, tx: VersionedTransaction, max_retries: int = 3) -> bool:
    """Send and confirm a transaction with robust error handling"""
    try:
        # Send with retries
        sig = await with_retries(
            lambda: client.send_transaction(tx),
            max_retries=max_retries
        )
        
        print(f"Transaction sent: {sig.value}")
        
        # Monitor for confirmation
        start_time = time.time()
        while time.time() - start_time < 30:
            conf = await client.get_signature_statuses([sig.value])
            if conf.value[0] is not None:
                status = conf.value[0].confirmation_status
                if status == "confirmed" or status == "finalized":
                    print(f"✅ Transaction confirmed ({status})")
                    return True
                elif conf.value[0].err:
                    print(f"❌ Transaction failed: {conf.value[0].err}")
                    return False
            await asyncio.sleep(1)
            
        print("❌ Transaction confirmation timeout")
        return False
        
    except Exception as e:
        print(f"❌ Transaction error: {str(e)}")
        return False

async def build_versioned_transaction(
    client: AsyncClient,
    payer: Keypair,
    instructions: List[Instruction],
    priority_fee: int = 10000
) -> VersionedTransaction:
    """Build a versioned transaction with compute budget and priority fees"""
    
    # Add compute budget instructions
    budget_ix = [
        set_compute_unit_limit(200_000),  # Conservative limit
        set_compute_unit_price(priority_fee)  # Priority fee in micro-lamports
    ]
    
    # Get latest blockhash
    blockhash = await client.get_latest_blockhash(Confirmed)
    
    # Build message
    message = MessageV0.try_compile(
        payer=payer.pubkey(),
        instructions=budget_ix + instructions,
        recent_blockhash=blockhash.value.blockhash,
        address_lookup_table_accounts=[]
    )
    
    if not message:
        raise Exception("Failed to compile transaction message")
        
    return VersionedTransaction(message, [payer])

async def create_token_account(
    client: AsyncClient,
    wallet: Keypair,
    mint: Pubkey
) -> Tuple[Pubkey, Optional[Instruction]]:
    """Create an Associated Token Account with production-ready reliability"""
    
    try:
        print(f"\n🏦 Creating token account")
        print(f"Mint: {mint}")
        print(f"Owner: {wallet.pubkey()}")
        
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
        
        print(f"ATA Address: {ata_address}")
        
        # Check if account exists
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
            data=b""  # No additional data needed
        )
        
        return ata_address, create_ata_ix
        
    except Exception as e:
        print(f"Error creating token account: {str(e)}")
        traceback.print_exc()
        raise

async def main():
    """Run end-to-end test of ATA creation with production reliability"""
    client = None
    try:
        print("\n🔬 Testing ATA Creation")
        print("=" * 50)
        
        # Create test wallet
        wallet = Keypair()
        print(f"\n🔑 Test wallet: {wallet.pubkey()}")
        
        # Initialize client with Helius endpoint
        client = AsyncClient(DEVNET_ENDPOINTS[0], commitment=Confirmed)
        
        # Check and fund wallet
        balance = await client.get_balance(wallet.pubkey())
        print(f"Initial balance: {balance.value/1e9} SOL")
        
        if balance.value < 1_000_000_000:  # Need 1 SOL minimum
            print("\nRequesting airdrop...")
            if not await try_airdrop(wallet.pubkey()):
                print("❌ Could not fund wallet")
                return
                
            # Verify funding
            balance = await client.get_balance(wallet.pubkey())
            print(f"New balance: {balance.value/1e9} SOL")
        
        # Create ATA for test token
        token_mint = Pubkey.from_string(TEST_TOKEN)
        ata_address, create_ata_ix = await create_token_account(client, wallet, token_mint)
        
        if create_ata_ix:
            print("\n🏗️ Creating Associated Token Account...")
            
            # Build and send transaction
            tx = await build_versioned_transaction(
                client,
                wallet,
                [create_ata_ix],
                priority_fee=10000
            )
            
            if await send_and_confirm_tx(client, tx):
                print(f"\n✅ Successfully created ATA: {ata_address}")
                
                # Verify the account exists and is correct
                info = await client.get_account_info(ata_address)
                if info.value:
                    print("\n📊 ATA Details:")
                    print(f"Owner: {info.value.owner}")
                    print(f"Lamports: {info.value.lamports}")
                    print(f"Data length: {len(info.value.data)}")
                else:
                    print("⚠️ Warning: Could not verify ATA details")
            else:
                print("❌ Failed to create ATA")
        else:
            print("✅ ATA already exists, no action needed")
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        traceback.print_exc()
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
