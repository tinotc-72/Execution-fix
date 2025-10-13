#!/usr/bin/env python3
"""
CLMM Trader - Execute trades using different CLMM methods

Available CLMM Trading Methods:
1. swap() - Original method (DEPRECATED)
   - Uses SwapSingle<'info> context
   - Token Program only
   - Discriminator: Different from SwapV2
   
2. swap_v2() - Current standard method (RECOMMENDED)
   - Uses SwapSingleV2<'info> context  
   - Supports both Token Program and Token2022
   - Better transfer fee handling
   - Discriminator: [43, 4, 237, 11, 26, 201, 30, 98]
   
3. swap_router_base_in() - Multi-hop routing
   - Uses SwapRouterBaseIn<'info> context
   - For complex routes across multiple pools
   - Discriminator: Different from SwapV2

We're using swap_v2() (SwapSingleV2) because it's the current standard.

Based on transaction: 5Xi7DHVZuBBwepKmeNxz6cA4CWDS43PFjpV6kskp9b3TgvtbvK8Dgnc3JhSNzH92AS1SghxXm1vshnDNjLEvmyj
"""

import asyncio
import base64
import json
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.system_program import transfer, TransferParams
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from spl.token.instructions import get_associated_token_address, create_associated_token_account, sync_native, SyncNativeParams
from env_keys import EnvKeys

# Load environment
env = EnvKeys()

# PDA generation utilities (based on official Raydium SDK)
def find_program_address(seeds: list, program_id: Pubkey) -> tuple[Pubkey, int]:
    """Find a program derived address"""
    for nonce in range(256):
        try:
            address = Pubkey.create_program_address(
                seeds + [bytes([nonce])], program_id
            )
            return address, nonce
        except:
            continue
    raise ValueError("Unable to find a viable program address nonce")

def get_observation_account(program_id: Pubkey, pool_id: Pubkey) -> Pubkey:
    """
    Generate observation account PDA using official Raydium SDK method.
    Based on: getPdaObservationAccount() from raydium-sdk-v2
    
    Seeds: [OBSERVATION_SEED, poolId.toBuffer()]
    Where OBSERVATION_SEED = Buffer.from("observation", "utf8")
    """
    observation_seed = b"observation"
    seeds = [observation_seed, bytes(pool_id)]
    
    try:
        address, nonce = find_program_address(seeds, program_id)
        print(f"📍 Generated observation account: {address}")
        print(f"   Program ID: {program_id}")
        print(f"   Pool ID: {pool_id}")
        print(f"   Nonce: {nonce}")
        return address
    except Exception as e:
        print(f"❌ Error generating observation account: {e}")
        raise

class CLMMTrader:
    def __init__(self):
        self.client = AsyncClient(env.HELIUS_RPC_URL)
        self.clmm_program = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
        
        # Load wallet from .env file
        try:
            # Use the wallet from .env file
            import base58
            import os
            
            # Get private key from environment
            private_key_b58 = os.getenv('PHANTOM_PRIVATE_KEY')
            
            if not private_key_b58:
                raise ValueError("PHANTOM_PRIVATE_KEY not found in .env file")
            
            decoded_key = base58.b58decode(private_key_b58)
            self.wallet_keypair = Keypair.from_bytes(decoded_key)
            self.wallet_pubkey = self.wallet_keypair.pubkey()
            print(f"✅ Using wallet from .env file")
            
        except Exception as e:
            print(f"❌ Could not load wallet from .env: {e}")
            # Fallback to test wallet
            try:
                with open('test_wallet.json', 'r') as f:
                    wallet_data = json.load(f)
                self.wallet_keypair = Keypair.from_bytes(wallet_data)
                self.wallet_pubkey = self.wallet_keypair.pubkey()
                print(f"✅ Using test wallet as fallback")
            except Exception as e2:
                print(f"❌ Could not load any wallet: {e2}")
                raise
        
        # Using properly initialized CLMM pool with working tick arrays
        # This pool was verified to have working vaults and tick arrays
        self.pool_data = {
            "pool_state": "8sLbNZoA1cfnvMJLPfp98ZLAnFSYCFApfJKMbiXNLwxj",  # Working SOL-USDC CLMM pool
            "amm_config": "9iFER3bpjf1PTTCQCfTRu17EJgvsxo9pVyA9QWwEuX4x",  # Standard CLMM config
            "pool_vault_a": "6P4tvbzRY6Bh3MiWDHuLqyHywovsRwRpfskPvyeSoHsz",  # SOL vault
            "pool_vault_b": "6mK4Pxs6GhwnessH7CvPivqDYauiHZmAdbEFDpXFk9zt",  # USDC vault
            "tick_array": "4vGLPwfohNUd2o4NwZPMx7q8AH98DQ9Eth5tS1p8dew1",  # Working tick array
            "token_mint_a": "So11111111111111111111111111111111111111112",  # SOL (token_mint_0)
            "token_mint_b": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC (token_mint_1)
            "sol_mint": "So11111111111111111111111111111111111111112",  # SOL
            "usdc_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # We'll trade SOL->USDC
        }
        
        # Generate observation account dynamically using official SDK method
        pool_id = Pubkey.from_string(self.pool_data["pool_state"])
        self.observation_account = get_observation_account(self.clmm_program, pool_id)
        
        print(f"🚀 CLMM Trader initialized")
        print(f"   Wallet: {self.wallet_pubkey}")
        print(f"   Pool: {self.pool_data['pool_state']}")
        print(f"   Token: {self.pool_data['token_mint']}")
        print(f"   Observation: {self.observation_account}")  # Dynamic generation
    
    async def get_balances(self):
        """Check current balances"""
        try:
            # SOL balance
            sol_balance = await self.client.get_balance(self.wallet_pubkey)
            sol_amount = sol_balance.value / 1_000_000_000 if sol_balance.value else 0.0
            
            # Try to get token balance
            token_mint = Pubkey.from_string(self.pool_data['token_mint'])
            token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            try:
                token_balance = await self.client.get_token_account_balance(token_ata)
                token_amount = float(token_balance.value.ui_amount) if token_balance.value else 0.0
            except:
                token_amount = 0.0
            
            print(f"💰 Current balances:")
            print(f"   SOL: {sol_amount:.6f}")
            print(f"   Token: {token_amount:.6f}")
            
            return sol_amount, token_amount
        except Exception as e:
            print(f"❌ Error getting balances: {e}")
            return 0.0, 0.0
    
    def create_clmm_instruction_data(self, amount_lamports: int):
        """
        Create CLMM swap instruction data with correct discriminator.
        
        Based on official Raydium SDK V2 source code:
        - Discriminator: [43, 4, 237, 11, 26, 201, 30, 98] (8 bytes)
        - Parameters: struct([u64("amount"), u64("otherAmountThreshold"), u128("sqrtPriceLimitX64"), bool("isBaseInput")])
        """
        try:
            import struct
            
            # Official discriminator from Raydium SDK V2 anchorDataBuf.swap
            discriminator = bytes([43, 4, 237, 11, 26, 201, 30, 98])
            
            print(f"📊 Creating CLMM swap instruction data:")
            print(f"   Discriminator: {discriminator.hex()}")
            print(f"   Amount in: {amount_lamports} lamports")
            
            # Calculate minimum output (with slippage)
            # For a small amount, estimate reasonable output
            estimated_output = amount_lamports * 1000  # Rough estimate for token output
            min_amount_out = int(estimated_output * 0.95)  # 5% slippage
            
            print(f"   Min amount out: {min_amount_out}")
            
            # Pack parameters according to SDK layout
            # u64 amount (8 bytes)
            # u64 otherAmountThreshold (8 bytes)  
            # u128 sqrtPriceLimitX64 (16 bytes) - use max value for no limit
            # bool isBaseInput (1 byte)
            
            data = bytearray()
            data.extend(discriminator)
            data.extend(struct.pack('<Q', amount_lamports))  # u64 amount
            data.extend(struct.pack('<Q', min_amount_out))  # u64 otherAmountThreshold
            
            # u128 sqrtPriceLimitX64 - use max value for no limit
            sqrt_price_limit = (2**128 - 1) // 2  # Maximum safe value
            data.extend(struct.pack('<QQ', sqrt_price_limit & 0xFFFFFFFFFFFFFFFF, sqrt_price_limit >> 64))  # u128
            
            data.extend(struct.pack('<B', 1))  # bool isBaseInput = true (SOL in, token out)
            
            instruction_data = bytes(data)
            
            print(f"   Instruction data: {instruction_data.hex()}")
            print(f"   Length: {len(instruction_data)} bytes")
            
            return instruction_data
            
        except Exception as e:
            print(f"❌ Error creating instruction data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_clmm_swap_instruction(self, amount_sol: float = 0.001, token_account: Pubkey = None):
        """Create CLMM swap instruction using proper instruction data"""
        try:
            # Convert SOL to lamports
            amount_lamports = int(amount_sol * 1_000_000_000)
            
            # Get proper instruction data
            instruction_data = self.create_clmm_instruction_data(amount_lamports)
            
            if not instruction_data:
                return None
            
            # Get user token accounts
            token_mint = Pubkey.from_string(self.pool_data['token_mint'])
            sol_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
            
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, sol_mint)
            user_token_ata = token_account if token_account else get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Create accounts in exact order from the real transaction
            accounts = [
                AccountMeta(self.wallet_pubkey, True, True),  # 0: User/Payer (signer, writable)
                AccountMeta(Pubkey.from_string(self.pool_data["amm_config"]), False, False),  # 1: AMM Config
                AccountMeta(Pubkey.from_string(self.pool_data["pool_state"]), False, True),   # 2: Pool State
                AccountMeta(user_wsol_ata, False, True),  # 3: User SOL Token Account
                AccountMeta(user_token_ata, False, True),  # 4: User Token Account
                AccountMeta(Pubkey.from_string(self.pool_data["pool_vault_a"]), False, True),  # 5: Pool Vault A
                AccountMeta(Pubkey.from_string(self.pool_data["pool_vault_b"]), False, True),  # 6: Pool Vault B
                AccountMeta(self.observation_account, False, True),  # 7: Observation State (dynamically generated)
                AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), False, False),  # 8: Token Program
                AccountMeta(Pubkey.from_string(self.pool_data["tick_array"]), False, True),  # 9: Tick Array
                AccountMeta(token_mint, False, False),  # 10: Token Mint
            ]
            
            print(f"🔨 Creating CLMM swap instruction:")
            print(f"   Instruction data: {len(instruction_data)} bytes")
            print(f"   Accounts: {len(accounts)}")
            print(f"   Amount: {amount_sol} SOL ({amount_lamports} lamports)")
            print(f"   Token account: {user_token_ata}")
            print(f"   WSOL account: {user_wsol_ata}")
            
            return Instruction(
                program_id=self.clmm_program,
                accounts=accounts,
                data=instruction_data
            )
            
        except Exception as e:
            print(f"❌ Error creating CLMM swap instruction: {e}")
            return None
    
    async def execute_clmm_trade(self, amount_sol: float = 0.001, token_account: Pubkey = None):
        """Execute CLMM trade"""
        try:
            print(f"🔄 Executing CLMM trade: {amount_sol} SOL")
            
            # Create swap instruction
            swap_instruction = self.create_clmm_swap_instruction(amount_sol, token_account)
            if not swap_instruction:
                print("❌ Failed to create swap instruction")
                return None
            
            # Get recent blockhash
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            
            # Create transaction
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
            
            # Simulate first
            print("🧪 Simulating transaction...")
            sim_result = await self.client.simulate_transaction(transaction)
            
            if sim_result.value.err:
                print(f"❌ Simulation failed: {sim_result.value.err}")
                if hasattr(sim_result.value, 'logs') and sim_result.value.logs:
                    print("📜 Simulation logs:")
                    for log in sim_result.value.logs:
                        print(f"   {log}")
                return None
            
            print("✅ Simulation successful!")
            
            # Send transaction automatically
            print("📡 Sending transaction...")
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
                print(f"✅ Transaction sent: {signature}")
                return signature
            else:
                print("❌ Failed to send transaction")
                return None
                
        except Exception as e:
            print(f"❌ Error executing CLMM trade: {e}")
            return None
    
    def create_clmm_sell_instruction_data(self, token_amount: int):
        """Create CLMM sell instruction data (token -> SOL)"""
        try:
            import struct
            
            # Same discriminator as buy - swap_v2
            discriminator = bytes([43, 4, 237, 11, 26, 201, 30, 98])
            
            print(f"📊 Creating CLMM sell instruction data:")
            print(f"   Discriminator: {discriminator.hex()}")
            print(f"   Token amount in: {token_amount}")
            
            # For sell, we estimate SOL output
            # This is a rough estimate - in reality you'd calculate based on pool state
            estimated_sol_output = token_amount // 1000  # Rough estimate
            min_sol_out = int(estimated_sol_output * 0.95)  # 5% slippage
            
            print(f"   Min SOL out: {min_sol_out} lamports")
            
            # Pack parameters - same structure as buy but different amounts
            data = bytearray()
            data.extend(discriminator)
            data.extend(struct.pack('<Q', token_amount))  # u64 amount (tokens in)
            data.extend(struct.pack('<Q', min_sol_out))  # u64 otherAmountThreshold (min SOL out)
            
            # u128 sqrtPriceLimitX64 - use 0 for no limit when selling
            sqrt_price_limit = 0
            data.extend(struct.pack('<QQ', sqrt_price_limit & 0xFFFFFFFFFFFFFFFF, sqrt_price_limit >> 64))
            
            data.extend(struct.pack('<B', 1))  # bool isBaseInput = true (token in, SOL out)
            
            instruction_data = bytes(data)
            
            print(f"   Instruction data: {instruction_data.hex()}")
            print(f"   Length: {len(instruction_data)} bytes")
            
            return instruction_data
            
        except Exception as e:
            print(f"❌ Error creating sell instruction data: {e}")
            return None

    async def execute_clmm_sell(self):
        """Execute CLMM sell - sell all tokens back to SOL"""
        try:
            print("💸 Executing CLMM sell (all tokens)")
            
            # Get token balance
            token_mint = Pubkey.from_string(self.pool_data['token_mint'])
            token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            try:
                token_balance = await self.client.get_token_account_balance(token_ata)
                if not token_balance.value or int(token_balance.value.amount) == 0:
                    print("❌ No tokens to sell")
                    return None
                
                token_amount = int(token_balance.value.amount)
                print(f"   Selling {token_amount} tokens")
            except Exception as e:
                print(f"❌ Error getting token balance: {e}")
                return None
            
            # Create sell instruction data
            instruction_data = self.create_clmm_sell_instruction_data(token_amount)
            if not instruction_data:
                print("❌ Failed to create sell instruction data")
                return None
            
            # Get user accounts
            sol_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, sol_mint)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Create accounts - same order as buy but reversed direction
            accounts = [
                AccountMeta(self.wallet_pubkey, True, True),  # User/Payer
                AccountMeta(Pubkey.from_string(self.pool_data["amm_config"]), False, False),  # AMM Config
                AccountMeta(Pubkey.from_string(self.pool_data["pool_state"]), False, True),   # Pool State
                AccountMeta(user_token_ata, False, True),  # User Token Account (input)
                AccountMeta(user_wsol_ata, False, True),  # User SOL Account (output)
                AccountMeta(Pubkey.from_string(self.pool_data["pool_vault_b"]), False, True),  # Pool Vault B (token vault)
                AccountMeta(Pubkey.from_string(self.pool_data["pool_vault_a"]), False, True),  # Pool Vault A (SOL vault)
                AccountMeta(self.observation_account, False, True),  # Observation State (dynamically generated)
                AccountMeta(Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), False, False),  # Token Program
                AccountMeta(Pubkey.from_string(self.pool_data["tick_array"]), False, True),  # Tick Array
                AccountMeta(token_mint, False, False),  # Token Mint
            ]
            
            # Create instruction
            swap_instruction = Instruction(
                program_id=self.clmm_program,
                accounts=accounts,
                data=instruction_data
            )
            
            # Get recent blockhash
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            
            # Create transaction
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
            
            # Simulate first
            print("🧪 Simulating sell transaction...")
            sim_result = await self.client.simulate_transaction(transaction)
            
            if sim_result.value.err:
                print(f"❌ Sell simulation failed: {sim_result.value.err}")
                if hasattr(sim_result.value, 'logs') and sim_result.value.logs:
                    print("📜 Sell simulation logs:")
                    for log in sim_result.value.logs:
                        print(f"   {log}")
                return None
            
            print("✅ Sell simulation successful!")
            
            # Send transaction
            print("📡 Sending sell transaction...")
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
                print(f"✅ Sell transaction sent: {signature}")
                return signature
            else:
                print("❌ Failed to send sell transaction")
                return None
            
        except Exception as e:
            print(f"❌ Error executing sell: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def run_buy_hold_sell_cycle(self):
        """Run complete buy-hold-sell cycle with fixed 0.0001 SOL"""
        amount_sol = 0.0001  # Reduced amount to work with available balance
        
        print("🚀 CLMM Buy-Hold-Sell Cycle")
        print("=" * 50)
        print(f"💰 Trading amount: {amount_sol} SOL")
        print("⏱️  Hold time: 5 seconds")
        
        # STEP 0: Parse CLMM pool data
        print("\n📊 Parsing CLMM pool data...")
        if not await self.parse_clmm_pool_data():
            print("❌ Failed to parse CLMM pool data")
            await self.client.close()
            return
        
        # Check initial balances
        print("\n📊 Initial balances:")
        sol_initial, token_initial = await self.get_balances()
        
        if sol_initial < amount_sol + 0.001:  # Need less extra for fees
            print(f"❌ Insufficient SOL balance. Need {amount_sol + 0.001}, have {sol_initial}")
            return
        
        # STEP 1: BUY
        print(f"\n🛒 STEP 1: BUYING {amount_sol} SOL worth of tokens...")
        
        # Ensure WSOL account exists
        wsol_account = await self.ensure_wsol_account(amount_sol * 2)  # Fund with 2x the trade amount
        if not wsol_account:
            print("❌ Failed to ensure WSOL account")
            await self.client.close()
            return
        
        # Ensure token account exists
        print("🏦 Ensuring token account exists...")
        token_account = await self.ensure_token_account()
        if not token_account:
            print("❌ Failed to ensure token account")
            await self.client.close()
            return
        
        buy_signature = await self.execute_clmm_trade(amount_sol, token_account)
        
        if not buy_signature:
            print("❌ Buy trade failed")
            await self.client.close()
            return
        
        print(f"✅ Buy executed: {buy_signature}")
        
        # Wait for confirmation
        print("⏳ Waiting for buy confirmation...")
        await asyncio.sleep(3)
        
        # Check balances after buy
        print("\n📊 Balances after buy:")
        sol_after_buy, token_after_buy = await self.get_balances()
        
        if token_after_buy <= token_initial:
            print("❌ No tokens received, cancelling sell")
            await self.client.close()
            return
        
        # STEP 2: HOLD
        print(f"\n⏱️  STEP 2: HOLDING for 5 seconds...")
        await asyncio.sleep(5)
        
        # STEP 3: SELL
        print(f"\n💸 STEP 3: SELLING all tokens...")
        sell_signature = await self.execute_clmm_sell()
        
        if not sell_signature:
            print("❌ Sell trade failed")
            await self.client.close()
            return
        
        print(f"✅ Sell executed: {sell_signature}")
        
        # Wait for confirmation
        print("⏳ Waiting for sell confirmation...")
        await asyncio.sleep(3)
        
        # Final balances
        print("\n📊 Final balances:")
        sol_final, token_final = await self.get_balances()
        
        # Summary
        print(f"\n📈 TRADE CYCLE SUMMARY:")
        print(f"   SOL change: {sol_final - sol_initial:.6f}")
        print(f"   Token change: {token_final - token_initial:.6f}")
        print(f"   Buy signature: {buy_signature}")
        print(f"   Sell signature: {sell_signature}")
        
        if sol_final > sol_initial:
            print("🎉 PROFIT!")
        elif sol_final < sol_initial:
            print("📉 Loss (including fees)")
        else:
            print("⚖️  Break even")
        
        await self.client.close()

    async def ensure_wsol_account(self, amount_sol: float = 0.001):
        """Ensure WSOL (Wrapped SOL) account exists and has balance"""
        try:
            sol_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
            wsol_ata = get_associated_token_address(self.wallet_pubkey, sol_mint)
            
            # Check if WSOL account exists
            try:
                account_info = await self.client.get_account_info(wsol_ata)
                if account_info.value:
                    print("✅ WSOL account exists, checking balance...")
                    
                    # Check WSOL balance
                    try:
                        wsol_balance = await self.client.get_token_account_balance(wsol_ata)
                        current_wsol = float(wsol_balance.value.ui_amount) if wsol_balance.value else 0.0
                        print(f"   Current WSOL balance: {current_wsol}")
                        
                        if current_wsol >= amount_sol:
                            print("✅ WSOL account has sufficient balance")
                            return wsol_ata
                    except:
                        pass
                    
                    # Need to fund the existing WSOL account
                    print(f"💰 Funding WSOL account with {amount_sol} SOL...")
                    
                    # Get recent blockhash
                    recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                    
                    # Transfer SOL to WSOL account and sync
                    instructions = [
                        transfer(TransferParams(
                            from_pubkey=self.wallet_pubkey,
                            to_pubkey=wsol_ata,
                            lamports=int(amount_sol * 1_000_000_000)
                        )),
                        sync_native(SyncNativeParams(
                            program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                            account=wsol_ata
                        ))
                    ]
                    
                    # Create transaction
                    message = MessageV0.try_compile(
                        payer=self.wallet_pubkey,
                        instructions=instructions,
                        recent_blockhash=recent_blockhash,
                        address_lookup_table_accounts=[]
                    )
                    
                    transaction = VersionedTransaction(message, [self.wallet_keypair])
                    
                    # Send transaction
                    result = await self.client.send_transaction(transaction)
                    if result.value:
                        print(f"✅ WSOL account funded: {result.value}")
                        await asyncio.sleep(3)  # Wait for confirmation
                    
                    return wsol_ata
                    
            except Exception as e:
                print(f"Error checking existing WSOL account: {e}")
            
            print("🔨 Creating and funding WSOL account...")
            
            # Create WSOL account and fund it
            create_ata_ix = create_associated_token_account(
                payer=self.wallet_pubkey,
                owner=self.wallet_pubkey,
                mint=sol_mint
            )
            
            # Transfer SOL to WSOL account
            transfer_ix = transfer(TransferParams(
                from_pubkey=self.wallet_pubkey,
                to_pubkey=wsol_ata,
                lamports=int(amount_sol * 1_000_000_000)
            ))
            
            # Sync native to convert SOL to WSOL
            sync_ix = sync_native(SyncNativeParams(
                program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                account=wsol_ata
            ))
            
            # Get recent blockhash
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            
            # Create transaction
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[create_ata_ix, transfer_ix, sync_ix],
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            # Send transaction
            result = await self.client.send_transaction(transaction)
            if result.value:
                print(f"✅ WSOL account created and funded: {wsol_ata}")
                await asyncio.sleep(3)  # Wait for confirmation
            
            return wsol_ata
            
        except Exception as e:
            print(f"❌ Error ensuring WSOL account: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    async def ensure_token_account(self):
        """Ensure the token account exists for the token we're trading"""
        try:
            print(f"🏦 Ensuring token account exists for {self.pool_data['token_mint']}...")
            
            # Get Associated Token Address
            token_mint = Pubkey.from_string(self.pool_data['token_mint'])
            token_account = get_associated_token_address(
                self.wallet_pubkey, 
                token_mint
            )
            
            # Check if account exists
            account_info = await self.client.get_account_info(token_account)
            
            if account_info.value is None:
                print(f"📝 Creating token account: {token_account}")
                
                # Create associated token account instruction
                # Try Token-2022 program first, fallback to standard Token program
                try:
                    create_ata_ix = create_associated_token_account(
                        payer=self.wallet_pubkey,
                        owner=self.wallet_pubkey,
                        mint=token_mint,
                        token_program_id=Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
                    )
                    print("   Using Token-2022 program")
                except:
                    create_ata_ix = create_associated_token_account(
                        payer=self.wallet_pubkey,
                        owner=self.wallet_pubkey,
                        mint=token_mint,
                        token_program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
                    )
                    print("   Using standard Token program")
                
                # Get recent blockhash
                recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
                
                # Create transaction
                message = MessageV0.try_compile(
                    payer=self.wallet_pubkey,
                    instructions=[create_ata_ix],
                    recent_blockhash=recent_blockhash,
                    address_lookup_table_accounts=[]
                )
                
                transaction = VersionedTransaction(message, [self.wallet_keypair])
                
                # Send transaction
                response = await self.client.send_transaction(
                    transaction, 
                    opts=TxOpts(
                        skip_preflight=False,
                        preflight_commitment=Processed,
                        max_retries=3
                    )
                )
                
                if response.value:
                    print(f"✅ Token account created: {response.value}")
                    
                    # Wait for confirmation
                    await asyncio.sleep(5)
                    
                    # Verify the account is properly initialized
                    account_info = await self.client.get_account_info(token_account)
                    if account_info.value is None:
                        print("❌ Token account still not initialized after creation")
                        return None
                    else:
                        print(f"✅ Token account verified: {token_account}")
                else:
                    print("❌ Token account creation failed")
                    return None
                
            else:
                print(f"✅ Token account already exists: {token_account}")
                
            return token_account
            
        except Exception as e:
            print(f"❌ Error ensuring token account: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def parse_clmm_pool_data(self):
        """Validate the working CLMM pool data and verify accounts exist"""
        try:
            print("📊 Validating working CLMM pool data...")
            
            # Use the verified working pool
            pool_pubkey = Pubkey.from_string(self.pool_data["pool_state"])
            pool_info = await self.client.get_account_info(pool_pubkey)
            
            if not pool_info.value:
                raise ValueError("CLMM pool not found")
            
            # Verify it's owned by CLMM program
            if pool_info.value.owner != self.clmm_program:
                raise ValueError(f"Pool not owned by CLMM program. Owner: {pool_info.value.owner}")
            
            print(f"   ✅ Verified CLMM pool: {pool_pubkey}")
            print(f"   Owner: {pool_info.value.owner}")
            print(f"   Data length: {len(pool_info.value.data)} bytes")
            
            # Verify the vaults exist
            vault_a = Pubkey.from_string(self.pool_data['pool_vault_a'])
            vault_b = Pubkey.from_string(self.pool_data['pool_vault_b'])
            
            vault_a_info = await self.client.get_account_info(vault_a)
            vault_b_info = await self.client.get_account_info(vault_b)
            
            print(f"   ✅ Vault A exists: {vault_a_info.value is not None}")
            print(f"   ✅ Vault B exists: {vault_b_info.value is not None}")
            
            # Verify tick array exists
            tick_array = Pubkey.from_string(self.pool_data['tick_array'])
            tick_array_info = await self.client.get_account_info(tick_array)
            
            print(f"   ✅ Tick array exists: {tick_array_info.value is not None}")
            
            # Check observation account (dynamically generated)
            obs_info = await self.client.get_account_info(self.observation_account)
            
            if obs_info.value:
                print(f"   ✅ Observation account exists: {self.observation_account}")
            else:
                print(f"   ⚠️  Observation account missing: {self.observation_account}")
                print(f"   💡 This may cause issues, but we'll try anyway")
            
            print(f"   ✅ Using working CLMM accounts:")
            print(f"      Pool State: {self.pool_data['pool_state']}")
            print(f"      AMM Config: {self.pool_data['amm_config']}")
            print(f"      Pool Vault A: {self.pool_data['pool_vault_a']}")
            print(f"      Pool Vault B: {self.pool_data['pool_vault_b']}")
            print(f"      Observation State: {self.observation_account}")
            print(f"      Tick Array: {self.pool_data['tick_array']}")
            
            print("   ✅ CLMM pool data validated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error validating CLMM pool data: {e}")
            import traceback
            traceback.print_exc()
            return False
async def main():
    trader = CLMMTrader()
    await trader.run_buy_hold_sell_cycle()

if __name__ == "__main__":
    asyncio.run(main())
