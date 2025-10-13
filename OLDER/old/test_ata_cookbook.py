#!/usr/bin/env python3
"""
Associated Token Account creation following official Solana documentation pattern
Uses minimal approach with proper error handling
Author: tinotc-72
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

# Official program IDs from Solana documentation
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
TEST_TOKEN = "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"  # Devnet USDC

async def try_airdrop(address: Pubkey, amount: int = 1_000_000_000) -> bool:
    """Request airdrop using Solana's recommended signature confirmation"""
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop...")
    
    # List of devnet endpoints to try
    endpoints = [
        "https://api.devnet.solana.com",
        "https://devnet.genesysgo.net",
        "https://api.metaplex.solana.com/"
    ]
    
    for endpoint in endpoints:
        client = None
        try:
            print(f"\nTrying airdrop from {endpoint}...")
            client = AsyncClient(endpoint, commitment=Confirmed)
            
            # Check initial balance
            initial = await client.get_balance(address)
            print(f"Initial balance: {initial.value/1e9} SOL")
            
            # Add delay to avoid rate limiting
            await asyncio.sleep(2)
            
            # Request airdrop
            sig = await client.request_airdrop(address, amount)
            if not sig:
                print("No signature returned")
                continue
                
            print(f"Airdrop requested: {sig.value}")
            
            # Wait for confirmation
            for _ in range(30):
                conf = await client.get_signature_statuses([sig.value])
                if conf.value[0] is not None:
                    if conf.value[0].err:
                        print(f"❌ Airdrop failed: {conf.value[0].err}")
                        break
                        
                    if conf.value[0].confirmation_status in ["confirmed", "finalized"]:
                        # Verify balance increase
                        new_balance = await client.get_balance(address)
                        if new_balance.value > initial.value:
                            print(f"✅ Balance increased to {new_balance.value/1e9} SOL")
                            return True
                            
                await asyncio.sleep(1)
                print(".", end="", flush=True)
                
        except Exception as e:
            print(f"Error with {endpoint}: {str(e)}")
        finally:
            if client:
                await client.close()
                
    print("\n❌ All endpoints failed")
    return False
        
        # Request airdrop
        sig = await client.request_airdrop(address, amount)
        if not sig:
            return False
            
        print(f"Airdrop requested: {sig.value}")
        
        # Wait for confirmation using signature status (Solana's recommended way)
        for _ in range(30):
            conf = await client.get_signature_statuses([sig.value])
            if conf.value[0] is not None:
                if conf.value[0].err:
                    print(f"❌ Airdrop failed: {conf.value[0].err}")
                    return False
                    
                if conf.value[0].confirmation_status in ["confirmed", "finalized"]:
                    # Verify balance increase
                    new_balance = await client.get_balance(address)
                    if new_balance.value > initial.value:
                        print(f"✅ Balance increased to {new_balance.value/1e9} SOL")
                        return True
                        
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        return False
    finally:
        await client.close()

async def create_token_account(
    client: AsyncClient,
    wallet: Keypair,
    mint: Pubkey
) -> tuple[Pubkey, list[Instruction]]:
    """Create Associated Token Account using Solana's official pattern"""
    print("\n🏦 Creating Associated Token Account")
    
    try:
        # Derive ATA address (Solana's deterministic method)
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
        if info.value:
            print(f"✅ Token account exists")
            return ata_address, []
            
        # Create ATA instruction (Solana's official pattern)
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
        
        return ata_address, [create_ata_ix]
        
    except Exception as e:
        print(f"Error creating token account: {str(e)}")
        raise

async def main():
    """Run end-to-end test following Solana documentation patterns"""
    client = None
    try:
        print("\n🔬 Testing ATA Creation")
        print("=" * 50)
        
        # Create test wallet
        wallet = Keypair()
        print(f"\n🔑 Test wallet: {wallet.pubkey()}")
        
        # Get airdrop first (using dedicated devnet endpoint)
        if not await try_airdrop(wallet.pubkey()):
            raise Exception("Could not fund wallet")
            
        # Now use Helius for the actual ATA creation
        client = AsyncClient("https://api.devnet.solana.com", commitment=Confirmed)
        
        # Create ATA
        mint = Pubkey.from_string(TEST_TOKEN)
        ata_address, instructions = await create_token_account(client, wallet, mint)
        
        if instructions:
            print("\n📝 Creating Associated Token Account...")
            
            # Add compute budget
            budget_ix = [
                set_compute_unit_limit(200_000),
                set_compute_unit_price(10_000)
            ]
            
            # Build transaction (using Solana's versioned transaction)
            blockhash = await client.get_latest_blockhash(Confirmed)
            msg = MessageV0.try_compile(
                payer=wallet.pubkey(),
                instructions=budget_ix + instructions,
                recent_blockhash=blockhash.value.blockhash,
                address_lookup_table_accounts=[]
            )
            
            if not msg:
                raise Exception("Failed to compile transaction message")
                
            # Sign and send
            tx = VersionedTransaction(msg, [wallet])
            sig = await client.send_transaction(tx)
            print(f"Transaction sent: {sig.value}")
            
            # Monitor confirmation (Solana's recommended way)
            print("\n🔍 Waiting for confirmation...")
            for _ in range(30):
                conf = await client.get_signature_statuses([sig.value])
                if conf.value[0] is not None:
                    status = conf.value[0].confirmation_status
                    if status in ["confirmed", "finalized"]:
                        print(f"\n✅ Transaction confirmed ({status})")
                        
                        # Verify final state
                        info = await client.get_account_info(ata_address)
                        if info.value:
                            print("\n📊 ATA Details:")
                            print(f"Owner: {info.value.owner}")
                            print(f"Lamports: {info.value.lamports}")
                            print(f"Data length: {len(info.value.data)}")
                        return
                    elif conf.value[0].err:
                        raise Exception(f"Transaction failed: {conf.value[0].err}")
                await asyncio.sleep(1)
                print(".", end="", flush=True)
                
            raise Exception("Transaction not confirmed")
            
        else:
            print("✅ ATA already exists, no action needed")
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
