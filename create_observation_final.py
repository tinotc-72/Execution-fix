"""
Create observation account using proper system program interface
"""

import os
import sys
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from env_keys import EnvKeys
import base58
import asyncio
import struct

# Load environment
env = EnvKeys()

RPC_URL = env.HELIUS_RPC_URL
client = AsyncClient(RPC_URL, commitment=Commitment("confirmed"))

# Load wallet from environment
try:
    private_key_str = env.PHANTOM_PRIVATE_KEY
    # Handle base58 or hex format
    if len(private_key_str) == 88:  # Base58 format
        private_key_bytes = base58.b58decode(private_key_str)
    else:  # Hex format
        private_key_bytes = bytes.fromhex(private_key_str)
    
    if len(private_key_bytes) != 64:
        raise ValueError("Private key must be 64 bytes")
    
    wallet = Keypair.from_bytes(private_key_bytes)
    print(f"✅ Using wallet from .env file")
except Exception as e:
    print(f"❌ Error loading wallet: {e}")
    sys.exit(1)

# CLMM program constants
CLMM_PROGRAM = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
OBSERVATION_SEED = "observation"
OBSERVATION_ACCOUNT_SIZE = 3683  # From official docs

# Pool and observation account
POOL_ADDRESS = Pubkey.from_string("2QdhepnKRTLjjSqPL1PtKNwqrUkoLee5Gqs8bvZhRdMv")

# Derive observation account
observation_key, observation_bump = Pubkey.find_program_address(
    [OBSERVATION_SEED.encode(), bytes(POOL_ADDRESS)],
    CLMM_PROGRAM
)

print(f"Creating observation account: {observation_key}")
print(f"Bump: {observation_bump}")

def create_account_instruction(from_pubkey, new_account_pubkey, lamports, space, program_id):
    """Create a system program CreateAccount instruction"""
    # CreateAccount instruction data format:
    # - 4 bytes: instruction discriminator (0)
    # - 8 bytes: lamports
    # - 8 bytes: space
    # - 32 bytes: program_id
    
    instruction_data = struct.pack(
        '<I',  # 4 bytes: instruction discriminator (0 for CreateAccount)
        0
    )
    instruction_data += struct.pack('<Q', lamports)  # 8 bytes: lamports
    instruction_data += struct.pack('<Q', space)     # 8 bytes: space
    instruction_data += bytes(program_id)            # 32 bytes: program_id
    
    return Instruction(
        program_id=SYSTEM_PROGRAM_ID,
        accounts=[
            AccountMeta(from_pubkey, is_signer=True, is_writable=True),
            AccountMeta(new_account_pubkey, is_signer=False, is_writable=True),
        ],
        data=instruction_data
    )

async def create_observation_account():
    """Create the observation account for CLMM pool"""
    try:
        # Get rent exemption
        rent_response = await client.get_minimum_balance_for_rent_exemption(
            OBSERVATION_ACCOUNT_SIZE
        )
        rent_amount = rent_response.value
        print(f"Required rent: {rent_amount} lamports")
        
        # Check if account already exists
        account_info = await client.get_account_info(observation_key)
        if account_info.value is not None:
            print("✅ Observation account already exists")
            return True
        
        # Create account instruction
        create_instruction = create_account_instruction(
            from_pubkey=wallet.pubkey(),
            new_account_pubkey=observation_key,
            lamports=rent_amount,
            space=OBSERVATION_ACCOUNT_SIZE,
            program_id=CLMM_PROGRAM
        )
        
        # Build transaction using VersionedTransaction pattern from working script
        instructions = [
            set_compute_unit_limit(200_000),
            set_compute_unit_price(1_000_000),
            create_instruction
        ]
        
        # Get recent blockhash
        recent_blockhash = await client.get_latest_blockhash()
        
        # Create message
        message = MessageV0.try_compile(
            wallet.pubkey(),
            instructions,
            [],
            recent_blockhash.value.blockhash
        )
        
        # Create transaction
        transaction = VersionedTransaction(message, [wallet])
        
        # Send transaction
        print("🚀 Sending observation account creation transaction...")
        result = await client.send_transaction(
            transaction,
            opts=TxOpts(skip_preflight=False, preflight_commitment=Commitment("confirmed"))
        )
        
        print(f"✅ Transaction sent: {result.value}")
        
        # Wait for confirmation
        await client.confirm_transaction(result.value)
        print("✅ Observation account created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating observation account: {e}")
        return False

async def main():
    """Main execution"""
    print("🔧 Creating observation account for CLMM pool...")
    success = await create_observation_account()
    
    if success:
        print("✅ Observation account ready for CLMM trading!")
        print("🚀 Now you can run the CLMM trader successfully")
    else:
        print("❌ Failed to create observation account")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
