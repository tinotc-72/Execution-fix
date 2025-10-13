#!/usr/bin/env python3
"""
Simple test for Associated Token Account (ATA) creation
Uses GenesysGo devnet endpoint for better reliability
"""

import asyncio
import time
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

# Use GenesysGo devnet endpoint which is more reliable for airdrops
DEVNET_URL = "https://devnet.genesysgo.net"

async def try_airdrop(client: AsyncClient, address: Pubkey, amount: int = 1_000_000_000) -> bool:
    """Request airdrop with improved reliability"""
    print(f"\n💸 Requesting {amount/1e9} SOL airdrop...")
    
    try:
        # Get initial balance
        initial_balance = await client.get_balance(address)
        print(f"Initial balance: {initial_balance.value/1e9} SOL")
        
        # Request airdrop
        print("Sending airdrop request...")
        sig = await client.request_airdrop(address, amount)
        
        if not sig:
            print("❌ Airdrop request failed")
            return False
            
        print(f"🔍 Monitoring transaction: {sig.value}")
        
        # Wait for confirmation
        status = None
        for _ in range(30):
            try:
                resp = await client.get_signature_statuses([sig.value])
                if resp.value[0] is not None:
                    status = resp.value[0].confirmation_status
                    if status == "confirmed" or status == "finalized":
                        # Verify balance increase
                        new_balance = await client.get_balance(address)
                        if new_balance.value > initial_balance.value:
                            print(f"✅ Airdrop confirmed! New balance: {new_balance.value/1e9} SOL")
                            return True
                    elif resp.value[0].err:
                        print(f"❌ Transaction failed: {resp.value[0].err}")
                        return False
            except Exception as e:
                print(f"Error checking status: {e}")
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        print(f"\n❌ Airdrop not confirmed. Last status: {status}")
        return False
        
    except Exception as e:
        print(f"❌ Airdrop error: {str(e)}")
        return False

async def main():
    """Run ATA creation test with improved reliability"""
    client = None
    try:
        print("\n🔬 Testing ATA Creation")
        print("=" * 50)
        
        # Create test wallet
        wallet = Keypair()
        print(f"\n🔑 Test wallet: {wallet.pubkey()}")
        
        # Initialize client
        client = AsyncClient(DEVNET_URL, commitment=Confirmed)
        
        # Get airdrop funding
        if not await try_airdrop(client, wallet.pubkey()):
            raise Exception("Could not fund wallet")
            
        # Create ATA for test token
        print("\n🏦 Creating Associated Token Account...")
        mint = Pubkey.from_string(TEST_TOKEN)
        
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
            return
            
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
        
        # Build and send transaction
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
        
        # Monitor for confirmation
        print("\n🔍 Waiting for confirmation...")
        for _ in range(30):
            confirm = await client.get_signature_statuses([result.value])
            if confirm.value[0] is not None:
                status = confirm.value[0].confirmation_status
                if status == "confirmed" or status == "finalized":
                    print(f"\n✅ Transaction confirmed ({status})")
                    
                    # Verify final state
                    info = await client.get_account_info(ata_address)
                    if info.value:
                        print("\n📊 ATA Details:")
                        print(f"Owner: {info.value.owner}")
                        print(f"Lamports: {info.value.lamports}")
                        print(f"Data length: {len(info.value.data)}")
                    return
                elif confirm.value[0].err:
                    raise Exception(f"Transaction failed: {confirm.value[0].err}")
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        print("\n❌ Transaction not confirmed")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
