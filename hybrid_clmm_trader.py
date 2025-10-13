#!/usr/bin/env python3
"""
Hybrid CLMM Trader - Uses Jupiter API as fallback when observation accounts are missing

This trader implements a hybrid approach:
1. Try direct CLMM trading first (fastest)
2. Fall back to Jupiter API when CLMM fails (reliable)
3. Provide production-ready reliability for copy trading
"""

import asyncio
import json
import aiohttp
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from env_keys import EnvKeys
import base64
import base58
import struct
import os

# Load environment
env = EnvKeys()

class HybridCLMMTrader:
    def __init__(self):
        self.client = AsyncClient(env.HELIUS_RPC_URL)
        self.clmm_program = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
        
        # Load wallet
        try:
            private_key_b58 = os.getenv('PHANTOM_PRIVATE_KEY')
            if not private_key_b58:
                raise ValueError("PHANTOM_PRIVATE_KEY not found in .env file")
            
            decoded_key = base58.b58decode(private_key_b58)
            self.wallet_keypair = Keypair.from_bytes(decoded_key)
            self.wallet_pubkey = self.wallet_keypair.pubkey()
            print(f"✅ Using wallet from .env file")
            
        except Exception as e:
            print(f"❌ Could not load wallet: {e}")
            raise
        
        # Working CLMM pool configuration (but with missing observation account)
        self.pool_data = {
            "pool_state": "8sLbNZoA1cfnvMJLPfp98ZLAnFSYCFApfJKMbiXNLwxj",
            "amm_config": "9iFER3bpjf1PTTCQCfTRu17EJgvsxo9pVyA9QWwEuX4x",
            "observation_state": "caNpYLajzNJ7akcJmixhKX8N1cUAt6kb3bVPGKydWN4",
            "pool_vault_a": "6P4tvbzRY6Bh3MiWDHuLqyHywovsRwRpfskPvyeSoHsz",
            "pool_vault_b": "6mK4Pxs6GhwnessH7CvPivqDYauiHZmAdbEFDpXFk9zt",
            "tick_array": "4vGLPwfohNUd2o4NwZPMx7q8AH98DQ9Eth5tS1p8dew1",
            "token_mint_a": "So11111111111111111111111111111111111111112",  # SOL
            "token_mint_b": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        }
        
        # Token mints for easy access
        self.sol_mint = "So11111111111111111111111111111111111111112"
        self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        
        print(f"🚀 Hybrid CLMM Trader initialized")
        print(f"   Wallet: {self.wallet_pubkey}")
        print(f"   Primary: Direct CLMM")
        print(f"   Fallback: Jupiter API")
    
    async def get_balances(self):
        """Check current balances"""
        try:
            # SOL balance
            sol_balance = await self.client.get_balance(self.wallet_pubkey)
            sol_amount = sol_balance.value / 1_000_000_000 if sol_balance.value else 0.0
            
            # USDC balance
            usdc_ata = get_associated_token_address(self.wallet_pubkey, Pubkey.from_string(self.usdc_mint))
            
            try:
                usdc_balance = await self.client.get_token_account_balance(usdc_ata)
                usdc_amount = float(usdc_balance.value.ui_amount) if usdc_balance.value else 0.0
            except:
                usdc_amount = 0.0
            
            print(f"💰 Current balances:")
            print(f"   SOL: {sol_amount:.6f}")
            print(f"   USDC: {usdc_amount:.6f}")
            
            return sol_amount, usdc_amount
        except Exception as e:
            print(f"❌ Error getting balances: {e}")
            return 0.0, 0.0
    
    async def execute_jupiter_swap(self, amount_sol: float, slippage_bps: int = 100):
        """Execute swap using Jupiter API"""
        try:
            print(f"🔄 Executing Jupiter swap: {amount_sol} SOL")
            
            amount_lamports = int(amount_sol * 1_000_000_000)
            
            async with aiohttp.ClientSession() as session:
                # Get quote from Jupiter
                quote_url = f"https://quote-api.jup.ag/v6/quote?inputMint={self.sol_mint}&outputMint={self.usdc_mint}&amount={amount_lamports}&slippageBps={slippage_bps}"
                
                async with session.get(quote_url) as response:
                    if response.status != 200:
                        print(f"❌ Jupiter quote failed: {response.status}")
                        return None
                    
                    quote_data = await response.json()
                    
                    print(f"   Quote received: {quote_data['outAmount']} USDC")
                    
                    # Get swap transaction
                    swap_payload = {
                        "userPublicKey": str(self.wallet_pubkey),
                        "quoteResponse": quote_data,
                        "wrapAndUnwrapSol": True,
                        "useSharedAccounts": True,
                        "feeAccount": None,
                        "trackingAccount": None,
                        "skipUserAccountsRpcCalls": False,
                        "useTokenLedger": False,
                        "asLegacyTransaction": False,
                        "allowOptimizedWrappedSolTokenAccount": True,
                        "skipUserAccountsRpcCalls": False
                    }
                    
                    swap_url = "https://quote-api.jup.ag/v6/swap"
                    
                    async with session.post(swap_url, json=swap_payload) as swap_response:
                        if swap_response.status != 200:
                            print(f"❌ Jupiter swap failed: {swap_response.status}")
                            return None
                        
                        swap_data = await swap_response.json()
                        
                        # Deserialize transaction
                        transaction_data = swap_data['swapTransaction']
                        raw_transaction = base64.b64decode(transaction_data)
                        
                        # Parse as VersionedTransaction
                        transaction = VersionedTransaction.from_bytes(raw_transaction)
                        
                        # Sign transaction - create a new signed transaction
                        signed_transaction = VersionedTransaction(transaction.message, [self.wallet_keypair])
                        
                        # Send transaction
                        print("📡 Sending Jupiter transaction...")
                        response = await self.client.send_transaction(
                            signed_transaction,
                            opts=TxOpts(
                                skip_preflight=True,
                                preflight_commitment=Processed,
                                max_retries=3
                            )
                        )
                        
                        if response.value:
                            signature = str(response.value)
                            print(f"✅ Jupiter transaction sent: {signature}")
                            return signature
                        else:
                            print("❌ Failed to send Jupiter transaction")
                            return None
                            
        except Exception as e:
            print(f"❌ Jupiter swap error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def try_direct_clmm_swap(self, amount_sol: float):
        """Try direct CLMM swap (will likely fail due to observation account)"""
        try:
            print(f"🧪 Attempting direct CLMM swap: {amount_sol} SOL")
            
            # This is the same code as before - it will fail due to observation account
            # but we keep it here for when observation accounts are fixed
            
            amount_lamports = int(amount_sol * 1_000_000_000)
            
            # Create instruction data
            discriminator = bytes([43, 4, 237, 11, 26, 201, 30, 98])
            estimated_output = amount_lamports * 1000
            min_amount_out = int(estimated_output * 0.95)
            
            data = bytearray()
            data.extend(discriminator)
            data.extend(struct.pack('<Q', amount_lamports))
            data.extend(struct.pack('<Q', min_amount_out))
            
            sqrt_price_limit = (2**128 - 1) // 2
            data.extend(struct.pack('<QQ', sqrt_price_limit & 0xFFFFFFFFFFFFFFFF, sqrt_price_limit >> 64))
            data.extend(struct.pack('<B', 1))
            
            instruction_data = bytes(data)
            
            # Create accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, Pubkey.from_string(self.sol_mint))
            user_usdc_ata = get_associated_token_address(self.wallet_pubkey, Pubkey.from_string(self.usdc_mint))
            
            accounts = [
                AccountMeta(self.wallet_pubkey, True, True),
                AccountMeta(Pubkey.from_string(self.pool_data["amm_config"]), False, False),
                AccountMeta(Pubkey.from_string(self.pool_data["pool_state"]), False, True),
                AccountMeta(user_wsol_ata, False, True),
                AccountMeta(user_usdc_ata, False, True),
                AccountMeta(Pubkey.from_string(self.pool_data["pool_vault_a"]), False, True),
                AccountMeta(Pubkey.from_string(self.pool_data["pool_vault_b"]), False, True),
                AccountMeta(Pubkey.from_string(self.pool_data["observation_state"]), False, True),
                AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), False, False),
                AccountMeta(Pubkey.from_string(self.pool_data["tick_array"]), False, True),
                AccountMeta(Pubkey.from_string(self.usdc_mint), False, False),
            ]
            
            swap_instruction = Instruction(
                program_id=self.clmm_program,
                accounts=accounts,
                data=instruction_data
            )
            
            # Create transaction
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            
            instructions = [
                set_compute_unit_limit(200_000),
                set_compute_unit_price(1),
                swap_instruction
            ]
            
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=instructions,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            # Simulate
            sim_result = await self.client.simulate_transaction(transaction)
            
            if sim_result.value.err:
                print(f"   ❌ Direct CLMM simulation failed: {sim_result.value.err}")
                return None
            
            # If simulation succeeds, send transaction
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
                print(f"✅ Direct CLMM transaction sent: {signature}")
                return signature
            else:
                print("❌ Failed to send direct CLMM transaction")
                return None
                
        except Exception as e:
            print(f"❌ Direct CLMM error: {e}")
            return None
    
    async def reliable_swap(self, amount_sol: float):
        """Perform reliable swap using hybrid approach"""
        try:
            print(f"🔄 Executing reliable hybrid swap: {amount_sol} SOL")
            
            # Step 1: Try direct CLMM (faster but likely to fail)
            print("🚀 Attempting direct CLMM swap...")
            direct_result = await self.try_direct_clmm_swap(amount_sol)
            
            if direct_result:
                print("✅ Direct CLMM swap successful!")
                return direct_result
            
            # Step 2: Fall back to Jupiter API (reliable but slower)
            print("🔄 Falling back to Jupiter API...")
            jupiter_result = await self.execute_jupiter_swap(amount_sol)
            
            if jupiter_result:
                print("✅ Jupiter swap successful!")
                return jupiter_result
            
            print("❌ Both direct CLMM and Jupiter failed")
            return None
            
        except Exception as e:
            print(f"❌ Reliable swap error: {e}")
            return None
    
    async def ensure_accounts(self):
        """Ensure required token accounts exist"""
        try:
            # Ensure USDC account exists
            usdc_ata = get_associated_token_address(self.wallet_pubkey, Pubkey.from_string(self.usdc_mint))
            
            account_info = await self.client.get_account_info(usdc_ata)
            
            if account_info.value is None:
                print("🔨 Creating USDC account...")
                
                create_ata_ix = create_associated_token_account(
                    payer=self.wallet_pubkey,
                    owner=self.wallet_pubkey,
                    mint=Pubkey.from_string(self.usdc_mint),
                    token_program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
                )
                
                recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                
                message = MessageV0.try_compile(
                    payer=self.wallet_pubkey,
                    instructions=[create_ata_ix],
                    recent_blockhash=recent_blockhash,
                    address_lookup_table_accounts=[]
                )
                
                transaction = VersionedTransaction(message, [self.wallet_keypair])
                
                response = await self.client.send_transaction(
                    transaction, 
                    opts=TxOpts(
                        skip_preflight=False,
                        preflight_commitment=Processed,
                        max_retries=3
                    )
                )
                
                if response.value:
                    print(f"✅ USDC account created: {response.value}")
                    await asyncio.sleep(3)  # Wait for confirmation
                else:
                    print("❌ USDC account creation failed")
                    return False
            else:
                print("✅ USDC account already exists")
            
            return True
            
        except Exception as e:
            print(f"❌ Error ensuring accounts: {e}")
            return False
    
    async def run_test_trade(self, amount_sol: float = 0.001):
        """Run a test trade using the hybrid approach"""
        try:
            print("🚀 Hybrid CLMM Test Trade")
            print("=" * 50)
            print(f"💰 Trading amount: {amount_sol} SOL")
            
            # Ensure accounts
            if not await self.ensure_accounts():
                print("❌ Failed to ensure accounts")
                return
            
            # Check initial balances
            print("\\n📊 Initial balances:")
            sol_initial, usdc_initial = await self.get_balances()
            
            if sol_initial < amount_sol + 0.01:
                print(f"❌ Insufficient SOL balance. Need {amount_sol + 0.01}, have {sol_initial}")
                return
            
            # Execute hybrid swap
            print(f"\\n🔄 Executing hybrid swap...")
            signature = await self.reliable_swap(amount_sol)
            
            if signature:
                print(f"✅ Swap executed: {signature}")
                
                # Wait for confirmation
                print("⏳ Waiting for confirmation...")
                await asyncio.sleep(5)
                
                # Check final balances
                print("\\n📊 Final balances:")
                sol_final, usdc_final = await self.get_balances()
                
                # Summary
                print(f"\\n📈 TRADE SUMMARY:")
                print(f"   SOL change: {sol_final - sol_initial:.6f}")
                print(f"   USDC change: {usdc_final - usdc_initial:.6f}")
                print(f"   Transaction: {signature}")
                
                if usdc_final > usdc_initial:
                    print("🎉 Trade successful - received USDC!")
                else:
                    print("❌ Trade may have failed - no USDC received")
            else:
                print("❌ All swap methods failed")
                
        except Exception as e:
            print(f"❌ Test trade error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.client.close()

async def main():
    trader = HybridCLMMTrader()
    await trader.run_test_trade(0.001)  # Test with 0.001 SOL

if __name__ == "__main__":
    asyncio.run(main())
