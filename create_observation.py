#!/usr/bin/env python3
"""
Create observation account for CLMM pool to enable trades
"""

import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import create_account, CreateAccountParams
from solders.transaction import Transaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from env_keys import EnvKeys
import base58
import os

async def create_observation_account():
    """Create observation account for CLMM pool"""
    
    # Get environment variables
    env = EnvKeys()
    
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    # Load wallet
    phantom_private_key = os.getenv('PHANTOM_PRIVATE_KEY')
    decoded_key = base58.b58decode(phantom_private_key)
    wallet_keypair = Keypair.from_bytes(decoded_key)
    wallet_pubkey = wallet_keypair.pubkey()
    
    # CLMM pool and program
    pool_pubkey = Pubkey.from_string("2QdhepnKRTLjjSqPL1PtKNwqrUkoLee5Gqs8bvZhRdMv")
    clmm_program = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
    
    # Derive observation account address using official seeds
    observation_seed = b"observation"
    observation_pubkey, observation_bump = Pubkey.find_program_address(
        [observation_seed, bytes(pool_pubkey)],
        clmm_program
    )
    
    print(f"🏗️  Creating CLMM Observation Account")
    print(f"Pool: {pool_pubkey}")
    print(f"Observation: {observation_pubkey}")
    print(f"Bump: {observation_bump}")
    
    # Check if it already exists
    obs_info = await client.get_account_info(observation_pubkey)
    if obs_info.value:
        print("✅ Observation account already exists!")
        await client.close()
        return
    
    # ObservationState size from official docs: 8 + 1 + 8 + 2 + 32 + (36 * 100) + 32 = 3683
    observation_size = 3683
    
    # Get rent
    rent_exempt_balance = await client.get_minimum_balance_for_rent_exemption(observation_size)
    
    print(f"💰 Creating account with {observation_size} bytes")
    print(f"💰 Rent: {rent_exempt_balance.value} lamports")
    
    # Create account instruction
    create_ix = create_account(
        CreateAccountParams(
            from_pubkey=wallet_pubkey,
            to_pubkey=observation_pubkey,
            lamports=rent_exempt_balance.value,
            space=observation_size,
            owner=clmm_program,
        )
    )
    
    # Create transaction
    recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
    
    transaction = Transaction(
        instructions=[
            set_compute_unit_limit(300_000),
            set_compute_unit_price(100_000),
            create_ix
        ],
        recent_blockhash=recent_blockhash,
        fee_payer=wallet_pubkey
    )
    
    transaction.sign([wallet_keypair])
    
    print("📡 Sending transaction...")
    try:
        response = await client.send_transaction(transaction)
        print(f"✅ Success: {response.value}")
        
        # Wait and verify
        await asyncio.sleep(5)
        
        obs_info = await client.get_account_info(observation_pubkey)
        if obs_info.value:
            print(f"🎉 Observation account created successfully!")
            print(f"   Address: {observation_pubkey}")
            print(f"   Owner: {obs_info.value.owner}")
            print(f"   Size: {len(obs_info.value.data)} bytes")
            print(f"\n✅ Now you can run CLMM trades!")
        else:
            print("❌ Account creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(create_observation_account())
