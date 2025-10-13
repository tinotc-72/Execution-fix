"""
Create observation account through CLMM program using direct invoke
"""

import os
import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from env_keys import EnvKeys
import base58

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
    exit(1)

# CLMM program constants
CLMM_PROGRAM = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
POOL_ADDRESS = Pubkey.from_string("2QdhepnKRTLjjSqPL1PtKNwqrUkoLee5Gqs8bvZhRdMv")

# Derive observation account
observation_key, observation_bump = Pubkey.find_program_address(
    [b"observation", bytes(POOL_ADDRESS)],
    CLMM_PROGRAM
)

print(f"Pool: {POOL_ADDRESS}")
print(f"Observation account: {observation_key}")
print(f"Bump: {observation_bump}")

async def initialize_observation_account():
    """Initialize observation account by simulating the SwapV2 instruction"""
    try:
        # Check if account already exists
        account_info = await client.get_account_info(observation_key)
        if account_info.value is not None:
            print("✅ Observation account already exists")
            return True
        
        # Create a minimal SwapV2 instruction to trigger observation account initialization
        # This instruction will fail but might initialize the observation account
        
        # SwapV2 instruction discriminator
        instruction_data = bytes.fromhex("2b04ed0b1ac91e62")  # SwapV2 discriminator
        instruction_data += (100000).to_bytes(8, 'little')  # amount
        instruction_data += (95000000).to_bytes(8, 'little')  # min_amount_out
        instruction_data += (2**127 - 1).to_bytes(16, 'little')  # sqrt_price_limit_x64
        instruction_data += (1).to_bytes(1, 'little')  # is_base_input
        
        # Create minimal accounts for the instruction
        accounts = [
            AccountMeta(wallet.pubkey(), True, True),  # payer
            AccountMeta(Pubkey.from_string("9iFER3bpjf1PTTCQCfTRu17EJgvsxo9pVyA9QWwEuX4x"), False, False),  # amm_config
            AccountMeta(POOL_ADDRESS, False, True),  # pool_state
            AccountMeta(Pubkey.from_string("F8CypSVrH9W4qyU4PcJdjLpgaMa795uKHdMpF5X6WxE3"), False, True),  # input_token_account
            AccountMeta(Pubkey.from_string("GEpRsN8Uc3q1yrWj3p95emcfWEpBU7sJEcN4pJ1ez438"), False, True),  # output_token_account
            AccountMeta(Pubkey.from_string("5QnvoBzmqhWSm5zSFEBgF1WcYbFBkS885GbcDUwuNXSY"), False, True),  # input_vault
            AccountMeta(Pubkey.from_string("3sm1m6NTLsi9Zi7NZ9RJGdqMp5hzseYpP2yHrUbbDrAZ"), False, True),  # output_vault
            AccountMeta(observation_key, False, True),  # observation_state
            AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), False, False),  # token_program
            AccountMeta(Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"), False, False),  # token_program_2022
        ]
        
        instruction = Instruction(
            program_id=CLMM_PROGRAM,
            accounts=accounts,
            data=instruction_data
        )
        
        # Build transaction
        instructions = [
            set_compute_unit_limit(200_000),
            set_compute_unit_price(1_000_000),
            instruction
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
        
        # Simulate transaction to see if it initializes the observation account
        print("🧪 Simulating transaction to check observation account initialization...")
        sim_result = await client.simulate_transaction(transaction)
        
        if sim_result.value.err:
            print(f"❌ Simulation failed: {sim_result.value.err}")
            if sim_result.value.logs:
                print("📜 Simulation logs:")
                for log in sim_result.value.logs:
                    print(f"   {log}")
        else:
            print("✅ Simulation successful")
            
        # Check if observation account was created during simulation
        account_info = await client.get_account_info(observation_key)
        if account_info.value is not None:
            print("✅ Observation account was initialized!")
            return True
        else:
            print("❌ Observation account was not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing observation account: {e}")
        return False

async def main():
    """Main execution"""
    print("🔧 Initializing observation account for CLMM pool...")
    success = await initialize_observation_account()
    
    if success:
        print("✅ Observation account ready for CLMM trading!")
        print("🚀 Now you can run the CLMM trader successfully")
    else:
        print("❌ Failed to initialize observation account")
        print("💡 The observation account might be initialized on first successful trade")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
