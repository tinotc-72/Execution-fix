"""
Raydium V4 AMM Trading Implementation
====================================

This module implements direct trading with Raydium V4 AMM pools.
This is the most common and established trading method on Raydium.

Program ID: 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
"""

import asyncio
import struct
import logging
from typing import Optional, Tuple
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import AccountMeta, Instruction
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solana.rpc.async_api import AsyncClient
from spl.token.instructions import get_associated_token_address

logger = logging.getLogger(__name__)

# Constants
LAMPORTS_PER_SOL = 1_000_000_000
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
SYSVAR_RENT_PUBKEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

# Raydium V4 AMM Program
RAYDIUM_V4_AMM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")

class RaydiumV4AMMTrader:
    """Direct Raydium V4 AMM trading implementation"""
    
    def __init__(self, client: AsyncClient, wallet_keypair: Keypair):
        self.client = client
        self.wallet_keypair = wallet_keypair
        
    async def find_sol_usdc_pool(self) -> Optional[dict]:
        """Find SOL-USDC V4 AMM pool"""
        try:
            # Known SOL-USDC V4 AMM pool addresses
            pool_info = {
                "pool_id": Pubkey.from_string("58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"),
                "base_vault": Pubkey.from_string("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"),
                "quote_vault": Pubkey.from_string("36c6YqAwyGKQG66XEp2dJc5JqjaBNv7sVghEtJv4c7u6"),
                "base_mint": NATIVE_MINT,
                "quote_mint": Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
                "authority": None  # Will be derived
            }
            
            # Derive AMM authority
            seeds = [b"amm_authority"]
            authority, _ = Pubkey.find_program_address(seeds, RAYDIUM_V4_AMM)
            pool_info["authority"] = authority
            
            # Verify pool exists
            if await self._verify_pool_exists(pool_info):
                logger.info("✅ Found SOL-USDC V4 AMM pool")
                return pool_info
            else:
                logger.warning("⚠️ SOL-USDC V4 AMM pool not found")
                return None
                
        except Exception as e:
            logger.error(f"Error finding SOL-USDC pool: {e}")
            return None
            
    async def _verify_pool_exists(self, pool_info: dict) -> bool:
        """Verify that pool exists and is valid"""
        try:
            # Check pool state
            pool_account = await self.client.get_account_info(pool_info["pool_id"])
            if not pool_account.value:
                logger.warning(f"Pool state not found: {pool_info['pool_id']}")
                return False
                
            # Check vaults
            base_vault = await self.client.get_account_info(pool_info["base_vault"])
            quote_vault = await self.client.get_account_info(pool_info["quote_vault"])
            
            if not base_vault.value or not quote_vault.value:
                logger.warning("One or more vaults not found")
                return False
                
            logger.info(f"✅ Pool verification successful")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying pool: {e}")
            return False
            
    async def create_wsol_account(self, amount: int) -> Tuple[Pubkey, Keypair]:
        """Create and fund a WSOL account"""
        try:
            # Generate new keypair for WSOL account
            wsol_keypair = Keypair()
            wsol_pubkey = wsol_keypair.pubkey()
            
            # Account creation parameters
            space = 165  # Token account size
            rent = 2_039_280  # Rent exemption amount
            
            # Create account instruction
            create_account_ix = Instruction(
                program_id=SYSTEM_PROGRAM_ID,
                data=struct.pack("<IQQ32s", 0, rent, space, bytes(TOKEN_PROGRAM_ID)),
                accounts=[
                    AccountMeta(self.wallet_keypair.pubkey(), True, True),
                    AccountMeta(wsol_pubkey, True, True)
                ]
            )
            
            # Initialize token account instruction
            init_account_ix = Instruction(
                program_id=TOKEN_PROGRAM_ID,
                data=bytes([1]),  # InitializeAccount
                accounts=[
                    AccountMeta(wsol_pubkey, False, True),
                    AccountMeta(NATIVE_MINT, False, False),
                    AccountMeta(self.wallet_keypair.pubkey(), False, False),
                    AccountMeta(SYSVAR_RENT_PUBKEY, False, False)
                ]
            )
            
            # Transfer SOL instruction (if amount > 0)
            instructions = [create_account_ix, init_account_ix]
            if amount > 0:
                transfer_ix = Instruction(
                    program_id=SYSTEM_PROGRAM_ID,
                    data=struct.pack("<IQ", 2, amount),
                    accounts=[
                        AccountMeta(self.wallet_keypair.pubkey(), True, True),
                        AccountMeta(wsol_pubkey, False, True)
                    ]
                )
                instructions.append(transfer_ix)
            
            # Send transaction
            signature = await self._send_transaction(instructions, [wsol_keypair])
            
            if signature:
                logger.info(f"✅ WSOL account created: {wsol_pubkey}")
                return wsol_pubkey, wsol_keypair
            else:
                raise Exception("Failed to create WSOL account")
                
        except Exception as e:
            logger.error(f"Error creating WSOL account: {e}")
            raise
            
    async def create_ata_if_needed(self, mint: Pubkey) -> Pubkey:
        """Create Associated Token Account if it doesn't exist"""
        try:
            ata = get_associated_token_address(self.wallet_keypair.pubkey(), mint)
            
            # Check if ATA exists
            account_info = await self.client.get_account_info(ata)
            if account_info.value:
                logger.info(f"✅ ATA already exists: {ata}")
                return ata
                
            # Create ATA instruction
            create_ata_ix = Instruction(
                program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
                data=bytes([]),
                accounts=[
                    AccountMeta(self.wallet_keypair.pubkey(), True, True),
                    AccountMeta(ata, False, True),
                    AccountMeta(self.wallet_keypair.pubkey(), False, False),
                    AccountMeta(mint, False, False),
                    AccountMeta(SYSTEM_PROGRAM_ID, False, False),
                    AccountMeta(TOKEN_PROGRAM_ID, False, False),
                    AccountMeta(SYSVAR_RENT_PUBKEY, False, False)
                ]
            )
            
            # Send transaction
            signature = await self._send_transaction([create_ata_ix])
            
            if signature:
                logger.info(f"✅ ATA created: {ata}")
                return ata
            else:
                raise Exception("Failed to create ATA")
                
        except Exception as e:
            logger.error(f"Error creating ATA: {e}")
            raise
            
    async def build_v4_amm_swap_instruction(
        self,
        pool_info: dict,
        source_token: Pubkey,
        destination_token: Pubkey,
        amount_in: int,
        minimum_amount_out: int,
        is_buy: bool
    ) -> Instruction:
        """Build V4 AMM swap instruction"""
        try:
            # V4 AMM swap instruction data
            # Format: [instruction_type, amount_in, minimum_amount_out]
            instruction_type = 9  # Swap instruction
            data = struct.pack("<BQQ", instruction_type, amount_in, minimum_amount_out)
            
            # Account metas for V4 AMM swap
            accounts = [
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(pool_info["pool_id"], False, True),
                AccountMeta(pool_info["authority"], False, False),
                AccountMeta(pool_info["base_vault"], False, True),
                AccountMeta(pool_info["quote_vault"], False, True),
                AccountMeta(source_token, False, True),
                AccountMeta(destination_token, False, True),
                AccountMeta(self.wallet_keypair.pubkey(), True, False),
            ]
            
            return Instruction(
                program_id=RAYDIUM_V4_AMM,
                data=data,
                accounts=accounts
            )
            
        except Exception as e:
            logger.error(f"Error building V4 AMM swap instruction: {e}")
            raise
            
    async def execute_buy(self, pool_info: dict, amount: int) -> Tuple[bool, int]:
        """Execute a buy trade (SOL -> Token)"""
        try:
            logger.info(f"🔄 Executing V4 AMM buy: {amount/LAMPORTS_PER_SOL:.6f} SOL")
            
            # Create WSOL account
            wsol_pubkey, wsol_keypair = await self.create_wsol_account(amount)
            
            # Create token ATA
            token_ata = await self.create_ata_if_needed(pool_info["quote_mint"])
            
            # Estimate minimum output (simplified)
            min_out = int(amount * 0.95)  # 5% slippage tolerance
            
            # Build swap instruction
            swap_ix = await self.build_v4_amm_swap_instruction(
                pool_info,
                wsol_pubkey,
                token_ata,
                amount,
                min_out,
                is_buy=True
            )
            
            # Send transaction
            signature = await self._send_transaction([swap_ix], [wsol_keypair])
            
            if signature:
                # Check token balance
                token_balance = await self._get_token_balance(token_ata)
                
                # Close WSOL account
                await self._close_wsol_account(wsol_pubkey, wsol_keypair)
                
                logger.info(f"✅ Buy successful: {token_balance} tokens")
                return True, token_balance
            else:
                logger.error("❌ Buy transaction failed")
                return False, 0
                
        except Exception as e:
            logger.error(f"❌ Buy execution failed: {e}")
            return False, 0
            
    async def execute_sell(self, pool_info: dict, amount: int) -> Tuple[bool, int]:
        """Execute a sell trade (Token -> SOL)"""
        try:
            logger.info(f"🔄 Executing V4 AMM sell: {amount} tokens")
            
            # Create WSOL account (for receiving SOL)
            wsol_pubkey, wsol_keypair = await self.create_wsol_account(0)
            
            # Get token ATA
            token_ata = get_associated_token_address(self.wallet_keypair.pubkey(), pool_info["quote_mint"])
            
            # Estimate minimum output (simplified)
            min_out = int(amount * 0.95)  # 5% slippage tolerance
            
            # Build swap instruction
            swap_ix = await self.build_v4_amm_swap_instruction(
                pool_info,
                token_ata,
                wsol_pubkey,
                amount,
                min_out,
                is_buy=False
            )
            
            # Send transaction
            signature = await self._send_transaction([swap_ix], [wsol_keypair])
            
            if signature:
                # Check WSOL balance
                wsol_balance = await self._get_token_balance(wsol_pubkey)
                
                # Close WSOL account (this recovers the SOL)
                await self._close_wsol_account(wsol_pubkey, wsol_keypair)
                
                logger.info(f"✅ Sell successful: {wsol_balance/LAMPORTS_PER_SOL:.6f} SOL")
                return True, wsol_balance
            else:
                logger.error("❌ Sell transaction failed")
                return False, 0
                
        except Exception as e:
            logger.error(f"❌ Sell execution failed: {e}")
            return False, 0
            
    async def _close_wsol_account(self, wsol_pubkey: Pubkey, wsol_keypair: Keypair):
        """Close WSOL account and recover SOL"""
        try:
            close_ix = Instruction(
                program_id=TOKEN_PROGRAM_ID,
                data=bytes([9]),  # CloseAccount
                accounts=[
                    AccountMeta(wsol_pubkey, False, True),
                    AccountMeta(self.wallet_keypair.pubkey(), False, True),
                    AccountMeta(self.wallet_keypair.pubkey(), True, False)
                ]
            )
            
            await self._send_transaction([close_ix], [wsol_keypair])
            logger.info(f"✅ WSOL account closed: {wsol_pubkey}")
            
        except Exception as e:
            logger.error(f"Error closing WSOL account: {e}")
            
    async def _get_token_balance(self, token_account: Pubkey) -> int:
        """Get token balance for an account"""
        try:
            account_info = await self.client.get_account_info(token_account)
            if not account_info.value:
                return 0
                
            # Parse token account data (simplified)
            data = account_info.value.data
            if len(data) >= 72:  # Minimum token account size
                amount = int.from_bytes(data[64:72], 'little')
                return amount
                
            return 0
            
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0
            
    async def _send_transaction(self, instructions: list, extra_signers: list = None) -> Optional[str]:
        """Send transaction with error handling"""
        if extra_signers is None:
            extra_signers = []
            
        try:
            # Get recent blockhash
            blockhash_resp = await self.client.get_latest_blockhash()
            if not blockhash_resp.value:
                raise Exception("Failed to get blockhash")
                
            # Add compute budget instructions
            compute_instructions = [
                set_compute_unit_limit(200_000),
                set_compute_unit_price(1)
            ]
            
            all_instructions = compute_instructions + instructions
            
            # Build transaction
            message = MessageV0.try_compile(
                payer=self.wallet_keypair.pubkey(),
                instructions=all_instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=blockhash_resp.value.blockhash
            )
            
            tx = VersionedTransaction(message, [self.wallet_keypair] + extra_signers)
            
            # Send transaction
            response = await self.client.send_transaction(
                tx,
                opts=TxOpts(skip_preflight=True)
            )
            
            if hasattr(response, 'value'):
                signature = response.value
            else:
                signature = str(response)
                
            # Confirm transaction
            confirmed = await self.client.confirm_transaction(signature, commitment=Confirmed)
            
            if confirmed.value:
                logger.info(f"✅ Transaction confirmed: {signature}")
                return signature
            else:
                logger.error("❌ Transaction failed to confirm")
                return None
                
        except Exception as e:
            logger.error(f"❌ Transaction error: {e}")
            return None

# Example usage
async def test_v4_amm_trading():
    """Test V4 AMM trading"""
    from env_keys import load_wallet_from_private_key, validate_env_vars
    
    # Load environment
    env_vars = validate_env_vars()
    wallet_keypair = load_wallet_from_private_key(env_vars["PHANTOM_PRIVATE_KEY"])
    
    async with AsyncClient(env_vars["RPC_URL"]) as client:
        trader = RaydiumV4AMMTrader(client, wallet_keypair)
        
        # Find pool
        pool_info = await trader.find_sol_usdc_pool()
        if not pool_info:
            logger.error("❌ No pool found")
            return
            
        # Execute buy
        buy_success, token_amount = await trader.execute_buy(pool_info, 1_000_000)  # 0.001 SOL
        
        if buy_success:
            # Hold for 5 seconds
            await asyncio.sleep(5)
            
            # Execute sell
            sell_success, sol_amount = await trader.execute_sell(pool_info, token_amount)
            
            if sell_success:
                logger.info(f"✅ Complete cycle successful")
            else:
                logger.error("❌ Sell failed")
        else:
            logger.error("❌ Buy failed")

if __name__ == "__main__":
    asyncio.run(test_v4_amm_trading())
