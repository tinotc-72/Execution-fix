#!/usr/bin/env python3

"""
Debug script to find where fake signatures are coming from
"""

import asyncio
import sys
sys.path.append('.')

from fast_executor import FastExecutor
from config import WALLET
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction
from solders.pubkey import Pubkey
from solders.hash import Hash
import base64

async def test_fake_signature_source():
    """Test where fake signatures come from"""
    
    print("🔍 DEBUGGING FAKE SIGNATURE SOURCE")
    print("=" * 50)
    
    # Get wallet from config
    wallet_keypair = WALLET
    
    # Initialize FastExecutor
    fast_executor = FastExecutor(wallet_keypair)
    await fast_executor.initialize()
    
    # Create a minimal test transaction
    try:
        from solana.rpc.async_api import AsyncClient
        client = AsyncClient("https://api.mainnet-beta.solana.com")
        
        # Get recent blockhash
        blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = blockhash_resp.value.blockhash
        
        # Create minimal instruction (transfer 1 lamport to self)
        from solders.instruction import AccountMeta
        instruction = Instruction(
            program_id=Pubkey.from_string("11111111111111111111111111111111"),  # System program
            accounts=[
                AccountMeta(pubkey=wallet_keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=wallet_keypair.pubkey(), is_signer=False, is_writable=True)
            ],
            data=bytes([2, 0, 0, 0]) + (1).to_bytes(8, byteorder='little')  # Transfer instruction
        )
        
        # Build message
        message = MessageV0.try_compile(
            payer=wallet_keypair.pubkey(),
            instructions=[instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash
        )
        
        # Create transaction
        transaction = VersionedTransaction(message, [wallet_keypair])
        
        print(f"✅ Created test transaction")
        print(f"   Payer: {wallet_keypair.pubkey()}")
        print(f"   Message: {type(message)}")
        print(f"   Transaction: {type(transaction)}")
        
        # Submit through FastExecutor
        print(f"\n🚀 Submitting via FastExecutor...")
        signature = await fast_executor.submit_transaction(transaction)
        
        print(f"\n📝 RESULT:")
        print(f"   Signature type: {type(signature)}")
        print(f"   Signature length: {len(signature) if signature else 0}")
        print(f"   Signature: {signature}")
        
        # Check if it's the fake signature
        if signature == "1111111111111111111111111111111111111111111111111111111111111111":
            print(f"\n🚨 FAKE SIGNATURE DETECTED!")
            print(f"   This is the problematic placeholder signature")
        elif signature and len(signature) >= 64:
            print(f"\n✅ REAL SIGNATURE DETECTED!")
            print(f"   This is a valid Solana transaction signature")
        else:
            print(f"\n❌ INVALID SIGNATURE!")
            print(f"   Signature is None or too short")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await fast_executor.close()

if __name__ == "__main__":
    asyncio.run(test_fake_signature_source())
