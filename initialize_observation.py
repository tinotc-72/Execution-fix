#!/usr/bin/env python3
"""
Initialize CLMM Observation Account
This script creates the observation account needed for CLMM trades
"""

import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.system_program import create_account, CreateAccountParams
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from env_keys import EnvKeys
import base58
import os

# Load environment
env = EnvKeys()

class ObservationInitializer:
    def __init__(self):
        self.client = AsyncClient(env.HELIUS_RPC_URL)
        self.clmm_program = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
        
        # Load wallet from .env file
        private_key_b58 = os.getenv('PHANTOM_PRIVATE_KEY')
        if not private_key_b58:
            raise ValueError("PHANTOM_PRIVATE_KEY not found in .env file")
        
        decoded_key = base58.b58decode(private_key_b58)
        self.wallet_keypair = Keypair.from_bytes(decoded_key)
        self.wallet_pubkey = self.wallet_keypair.pubkey()
        
        # CLMM pool we're working with
        self.pool_pubkey = Pubkey.from_string("2QdhepnKRTLjjSqPL1PtKNwqrUkoLee5Gqs8bvZhRdMv")
        
        print(f"🔧 Observation Account Initializer")
        print(f"   Wallet: {self.wallet_pubkey}")
        print(f"   Pool: {self.pool_pubkey}")
        print(f"   CLMM Program: {self.clmm_program}")
    
    async def create_observation_account(self):
        """Create the observation account for the CLMM pool"""
        try:
            # Derive the observation account address
            observation_seed = b"observation"
            observation_pubkey, bump = Pubkey.find_program_address(
                [observation_seed, bytes(self.pool_pubkey)],
                self.clmm_program
            )
            
            print(f"📊 Creating observation account:")
            print(f"   Address: {observation_pubkey}")
            print(f"   Bump: {bump}")
            
            # Check if it already exists
            account_info = await self.client.get_account_info(observation_pubkey)
            if account_info.value:
                print(f"✅ Observation account already exists!")
                print(f"   Owner: {account_info.value.owner}")
                print(f"   Data length: {len(account_info.value.data)} bytes")
                return observation_pubkey
            
            # Calculate rent for observation account
            observation_size = 3683  # Size from Raydium CLMM source
            
            rent_response = await self.client.get_minimum_balance_for_rent_exemption(observation_size)
            rent_lamports = rent_response.value
            
            print(f"   Size: {observation_size} bytes")
            print(f"   Rent: {rent_lamports} lamports")
            
            # Create the observation account
            create_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=self.wallet_pubkey,
                    to_pubkey=observation_pubkey,
                    lamports=rent_lamports,
                    space=observation_size,
                    owner=self.clmm_program
                )
            )
            
            # Get recent blockhash
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            
            # Create transaction
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[create_account_ix],
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            # Simulate first
            print("🧪 Simulating observation account creation...")
            sim_result = await self.client.simulate_transaction(transaction)
            
            if sim_result.value.err:
                print(f"❌ Simulation failed: {sim_result.value.err}")
                if hasattr(sim_result.value, 'logs') and sim_result.value.logs:
                    print("📜 Simulation logs:")
                    for log in sim_result.value.logs:
                        print(f"   {log}")
                return None
            
            print("✅ Simulation successful!")
            
            # Send transaction
            print("📡 Creating observation account...")
            response = await self.client.send_transaction(
                transaction,
                opts=TxOpts(
                    skip_preflight=True,
                    preflight_commitment=Processed,
                    max_retries=3
                )
            )
            
            if response.value:
                signature = str(response.value)
                print(f"✅ Observation account created: {signature}")
                
                # Wait for confirmation
                await asyncio.sleep(5)
                
                # Verify the account was created
                account_info = await self.client.get_account_info(observation_pubkey)
                if account_info.value and account_info.value.owner == self.clmm_program:
                    print(f"✅ Observation account verified!")
                    print(f"   Owner: {account_info.value.owner}")
                    print(f"   Data length: {len(account_info.value.data)} bytes")
                    return observation_pubkey
                else:
                    print("❌ Observation account not properly created")
                    return None
            else:
                print("❌ Failed to create observation account")
                return None
                
        except Exception as e:
            print(f"❌ Error creating observation account: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def run(self):
        """Run the observation account initialization"""
        print("🚀 Starting Observation Account Initialization")
        print("=" * 50)
        
        # Create observation account
        observation_account = await self.create_observation_account()
        
        if observation_account:
            print(f"\n✅ SUCCESS! Observation account ready: {observation_account}")
            print("🎉 CLMM trades can now be executed!")
        else:
            print("\n❌ Failed to create observation account")
            print("   Check the logs above for details")
        
        await self.client.close()

async def main():
    initializer = ObservationInitializer()
    await initializer.run()

if __name__ == "__main__":
    asyncio.run(main())
