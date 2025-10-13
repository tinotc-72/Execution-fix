"""
Pool Discovery Service - Extract pool information from successful target wallet transactions
This service analyzes target wallet transactions to extract the exact pool/bonding curve information
needed by independent DEX executors.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solders.pubkey import Pubkey

logger = logging.getLogger(__name__)

@dataclass
class DiscoveredPoolInfo:
    """Information discovered from target wallet transactions"""
    dex_type: str  # 'raydium', 'pump.fun', 'orca', etc.
    token_mint: str
    
    # Common fields
    pool_id: Optional[str] = None
    base_mint: Optional[str] = None
    quote_mint: Optional[str] = None
    
    # Raydium specific
    pool_coin_token_account: Optional[str] = None
    pool_pc_token_account: Optional[str] = None
    pool_withdraw_queue: Optional[str] = None
    pool_temp_lp_token_account: Optional[str] = None
    amm_id: Optional[str] = None
    amm_authority: Optional[str] = None
    amm_open_orders: Optional[str] = None
    amm_target_orders: Optional[str] = None
    
    # Pump.fun specific  
    bonding_curve: Optional[str] = None
    associated_bonding_curve: Optional[str] = None
    creator: Optional[str] = None
    
    # Orca specific
    vault_a: Optional[str] = None
    vault_b: Optional[str] = None
    tick_array_0: Optional[str] = None
    tick_array_1: Optional[str] = None
    tick_array_2: Optional[str] = None
    sqrt_price: Optional[int] = None
    tick_current_index: Optional[int] = None
    
    # Transaction info
    original_signature: Optional[str] = None
    block_slot: Optional[int] = None

class PoolDiscoveryService:
    """
    Service to discover pool information from target wallet transactions
    Analyzes successful trades to extract exact pool addresses needed by direct executors
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
        
        # Known program IDs
        self.RAYDIUM_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
        self.RAYDIUM_CPMM = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
        self.PUMP_FUN = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        self.ORCA_WHIRLPOOL = "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc"
        self.ORCA_LEGACY = "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP"
        self.JUPITER_V6 = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
    
    async def discover_pool_from_transaction(self, signature: str, token_mint: str) -> Optional[DiscoveredPoolInfo]:
        """
        Analyze a successful transaction to discover pool information
        """
        try:
            logger.info(f"🔍 Discovering pool info from transaction: {signature}")
            logger.info(f"   Token: {token_mint}")
            
            # Convert string signature to Signature object
            from solders.signature import Signature
            signature_obj = Signature.from_string(signature)
            
            # Get transaction details
            tx_response = await self.rpc_client.get_transaction(
                signature_obj, 
                commitment="confirmed",
                max_supported_transaction_version=0
            )
            
            if not tx_response.value:
                logger.warning(f"❌ Transaction not found: {signature}")
                return None
            
            # Handle encoded transaction format properly
            if hasattr(tx_response.value, 'transaction'):
                transaction_data = tx_response.value.transaction
                transaction = transaction_data.transaction
                meta = transaction_data.meta
            else:
                logger.warning(f"❌ Unexpected transaction format for: {signature}")
                return None
            
            if not meta or meta.err:
                logger.warning(f"❌ Transaction failed or no meta: {signature}")
                return None
            
            # Get message from transaction
            if hasattr(transaction, 'message'):
                message = transaction.message
            else:
                logger.warning(f"❌ Transaction has no message field: {signature}")
                return None
            
            # Analyze instructions to determine DEX and extract pool info
            pool_info = None
            
            for instruction in message.instructions:
                program_id = str(message.account_keys[instruction.program_id_index])
                logger.info(f"📋 Found program: {program_id}")
                logger.info(f"   Instruction accounts: {len(instruction.accounts)}")
                
                if program_id == self.PUMP_FUN:
                    logger.info(f"🟡 Attempting Pump.fun discovery")
                    pool_info = await self._discover_pumpfun_info(instruction, message, token_mint, signature)
                elif program_id == self.RAYDIUM_V4:
                    logger.info(f"🔵 Attempting Raydium V4 discovery")
                    pool_info = await self._discover_raydium_v4_info(instruction, message, token_mint, signature)
                elif program_id == self.RAYDIUM_CPMM:
                    logger.info(f"🔵 Attempting Raydium CPMM discovery")
                    pool_info = await self._discover_raydium_cpmm_info(instruction, message, token_mint, signature)
                elif program_id in [self.ORCA_WHIRLPOOL, self.ORCA_LEGACY]:
                    logger.info(f"🐋 Attempting Orca discovery")
                    pool_info = await self._discover_orca_info(instruction, message, token_mint, signature, program_id)
                elif program_id == self.JUPITER_V6:
                    # Jupiter routing - need to analyze inner instructions
                    logger.info(f"🪐 Attempting Jupiter routing discovery")
                    pool_info = await self._discover_jupiter_routed_info(instruction, message, meta, token_mint, signature)
                
                if pool_info:
                    break
            
            if pool_info:
                logger.info(f"✅ Pool discovery successful!")
                logger.info(f"   DEX: {pool_info.dex_type}")
                logger.info(f"   Pool ID: {pool_info.pool_id}")
                return pool_info
            else:
                logger.warning(f"❌ No pool information found in transaction")
                return None
                
        except Exception as e:
            logger.error(f"❌ Pool discovery error: {e}")
            return None
            
    async def close(self):
        """Close the RPC client connection"""
        if hasattr(self.rpc_client, 'close'):
            await self.rpc_client.close()
    
    async def _discover_pumpfun_info(self, instruction, message, token_mint: str, signature: str) -> Optional[DiscoveredPoolInfo]:
        """Discover Pump.fun bonding curve information"""
        try:
            # For Pump.fun, we need to extract bonding curve accounts from instruction accounts
            account_keys = message.account_keys
            
            # Typical Pump.fun buy instruction account layout:
            # 0: fee_recipient
            # 1: mint
            # 2: bonding_curve  
            # 3: associated_bonding_curve
            # 4: global
            # 5: mpl_token_metadata
            # 6: user
            # 7: user_token_account
            # 8: user_sol_account
            # 9: system_program
            # 10: token_program
            # 11: rent
            # 12: event_authority
            # 13: program
            
            if len(instruction.accounts) >= 4:
                bonding_curve = str(account_keys[instruction.accounts[2]])
                associated_bonding_curve = str(account_keys[instruction.accounts[3]])
                creator = str(account_keys[instruction.accounts[6]])  # user who initiated
                
                logger.info(f"🚀 Pump.fun pool discovery:")
                logger.info(f"   Bonding curve: {bonding_curve}")
                logger.info(f"   Associated bonding curve: {associated_bonding_curve}")
                logger.info(f"   Creator: {creator}")
                
                return DiscoveredPoolInfo(
                    dex_type="pump.fun",
                    token_mint=token_mint,
                    bonding_curve=bonding_curve,
                    associated_bonding_curve=associated_bonding_curve,
                    creator=creator,
                    original_signature=signature
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Pump.fun discovery error: {e}")
            return None
    
    async def _discover_raydium_v4_info(self, instruction, message, token_mint: str, signature: str) -> Optional[DiscoveredPoolInfo]:
        """Discover Raydium V4 AMM pool information"""
        try:
            # Extract Raydium V4 pool accounts
            account_keys = message.account_keys
            
            # This is a simplified extraction - real implementation would need
            # to parse the instruction data and account layout properly
            if len(instruction.accounts) >= 10:
                amm_id = str(account_keys[instruction.accounts[1]])
                amm_authority = str(account_keys[instruction.accounts[2]])
                amm_open_orders = str(account_keys[instruction.accounts[3]])
                pool_coin_token_account = str(account_keys[instruction.accounts[4]])
                pool_pc_token_account = str(account_keys[instruction.accounts[5]])
                
                logger.info(f"🟣 Raydium V4 pool discovery:")
                logger.info(f"   AMM ID: {amm_id}")
                logger.info(f"   Pool coin account: {pool_coin_token_account}")
                logger.info(f"   Pool PC account: {pool_pc_token_account}")
                
                return DiscoveredPoolInfo(
                    dex_type="raydium_v4",
                    token_mint=token_mint,
                    pool_id=amm_id,
                    amm_id=amm_id,
                    amm_authority=amm_authority,
                    amm_open_orders=amm_open_orders,
                    pool_coin_token_account=pool_coin_token_account,
                    pool_pc_token_account=pool_pc_token_account,
                    original_signature=signature
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Raydium V4 discovery error: {e}")
            return None
    
    async def _discover_raydium_cpmm_info(self, instruction, message, token_mint: str, signature: str) -> Optional[DiscoveredPoolInfo]:
        """Discover Raydium CPMM pool information"""
        try:
            # Extract CPMM pool accounts
            account_keys = message.account_keys
            
            logger.info(f"🔵 Raydium CPMM analysis:")
            logger.info(f"   Total accounts in instruction: {len(instruction.accounts)}")
            logger.info(f"   Total account keys: {len(account_keys)}")
            
            if len(instruction.accounts) >= 8:
                # Convert bytes to list of account indexes
                account_indexes = list(instruction.accounts)
                
                logger.info(f"🔍 Account indexes in instruction: {account_indexes[:10]}")
                logger.info(f"🔍 Total account_keys available: {len(account_keys)}")
                
                # Safely access accounts with bounds checking
                pool_id = None
                pool_coin_token_account = None
                pool_pc_token_account = None
                
                # Try different account positions for pool ID (sometimes it's in different positions)
                for pos in [0, 1, 2, 13]:  # Check common positions
                    if len(account_indexes) > pos and account_indexes[pos] < len(account_keys):
                        candidate = str(account_keys[account_indexes[pos]])
                        if len(candidate) > 40:  # Pool IDs are typically long addresses
                            pool_id = candidate
                            logger.info(f"   Found pool ID at position {pos}: {pool_id}")
                            break
                
                if len(account_indexes) > 4 and account_indexes[4] < len(account_keys):
                    pool_coin_token_account = str(account_keys[account_indexes[4]])
                    
                if len(account_indexes) > 5 and account_indexes[5] < len(account_keys):
                    pool_pc_token_account = str(account_keys[account_indexes[5]])
                
                logger.info(f"🔵 Raydium CPMM pool discovery:")
                logger.info(f"   Pool ID: {pool_id}")
                logger.info(f"   Coin account: {pool_coin_token_account}")
                logger.info(f"   PC account: {pool_pc_token_account}")
                
                if pool_id:
                    return DiscoveredPoolInfo(
                        dex_type="raydium_cpmm", 
                        token_mint=token_mint,
                        pool_id=pool_id,
                        pool_coin_token_account=pool_coin_token_account,
                        pool_pc_token_account=pool_pc_token_account,
                        original_signature=signature
                    )
            else:
                logger.warning(f"❌ Insufficient accounts for CPMM ({len(instruction.accounts)} < 8)")
                # Try to extract what we can with fewer accounts
                if len(instruction.accounts) >= 2:
                    pool_id = str(account_keys[instruction.accounts[1]])
                    logger.info(f"🔵 Partial CPMM info - Pool ID: {pool_id}")
                    
                    return DiscoveredPoolInfo(
                        dex_type="raydium_cpmm",
                        token_mint=token_mint,
                        pool_id=pool_id,
                        original_signature=signature
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Raydium CPMM discovery error: {e}")
            return None
    
    async def _discover_orca_info(self, instruction, message, token_mint: str, signature: str, program_id: str) -> Optional[DiscoveredPoolInfo]:
        """Discover Orca pool information"""
        try:
            account_keys = message.account_keys
            
            if program_id == self.ORCA_WHIRLPOOL:
                # Whirlpool pool discovery
                if len(instruction.accounts) >= 8:
                    pool_id = str(account_keys[instruction.accounts[1]])
                    vault_a = str(account_keys[instruction.accounts[4]])
                    vault_b = str(account_keys[instruction.accounts[5]])
                    
                    logger.info(f"🐋 Orca Whirlpool pool discovery:")
                    logger.info(f"   Pool ID: {pool_id}")
                    logger.info(f"   Vault A: {vault_a}")
                    logger.info(f"   Vault B: {vault_b}")
                    
                    return DiscoveredPoolInfo(
                        dex_type="orca_whirlpool",
                        token_mint=token_mint,
                        pool_id=pool_id,
                        vault_a=vault_a,
                        vault_b=vault_b,
                        original_signature=signature
                    )
            else:
                # Legacy pool discovery
                if len(instruction.accounts) >= 6:
                    pool_id = str(account_keys[instruction.accounts[1]])
                    vault_a = str(account_keys[instruction.accounts[3]])
                    vault_b = str(account_keys[instruction.accounts[4]])
                    
                    logger.info(f"🐋 Orca Legacy pool discovery:")
                    logger.info(f"   Pool ID: {pool_id}")
                    logger.info(f"   Vault A: {vault_a}")
                    logger.info(f"   Vault B: {vault_b}")
                    
                    return DiscoveredPoolInfo(
                        dex_type="orca_legacy",
                        token_mint=token_mint,
                        pool_id=pool_id,
                        vault_a=vault_a,
                        vault_b=vault_b,
                        original_signature=signature
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Orca discovery error: {e}")
            return None
    
    async def _discover_jupiter_routed_info(self, instruction, message, meta, token_mint: str, signature: str) -> Optional[DiscoveredPoolInfo]:
        """Discover pool info from Jupiter-routed transactions"""
        try:
            # When Jupiter routes through other DEXes, we need to analyze inner instructions
            # to find the actual DEX that was used
            
            if not meta.inner_instructions:
                return None
            
            for inner_instruction_group in meta.inner_instructions:
                for inner_instruction in inner_instruction_group.instructions:
                    program_id = str(message.account_keys[inner_instruction.program_id_index])
                    
                    # Check if Jupiter routed through Pump.fun
                    if program_id == self.PUMP_FUN:
                        logger.info(f"🎯 Jupiter routed through Pump.fun")
                        return await self._discover_pumpfun_info(inner_instruction, message, token_mint, signature)
                    
                    # Check other DEXes Jupiter might route through
                    elif program_id == self.RAYDIUM_V4:
                        logger.info(f"🎯 Jupiter routed through Raydium V4")
                        return await self._discover_raydium_v4_info(inner_instruction, message, token_mint, signature)
                    
                    elif program_id == self.RAYDIUM_CPMM:
                        logger.info(f"🎯 Jupiter routed through Raydium CPMM")
                        return await self._discover_raydium_cpmm_info(inner_instruction, message, token_mint, signature)
                    
                    elif program_id in [self.ORCA_WHIRLPOOL, self.ORCA_LEGACY]:
                        logger.info(f"🎯 Jupiter routed through Orca")
                        return await self._discover_orca_info(inner_instruction, message, token_mint, signature, program_id)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Jupiter routing discovery error: {e}")
            return None

# Global pool discovery cache
_pool_cache = {}

async def get_pool_info_for_token(rpc_client: AsyncClient, token_mint: str, target_signature: str = None) -> Optional[DiscoveredPoolInfo]:
    """
    Get pool information for a token, with caching
    """
    cache_key = f"{token_mint}:{target_signature}"
    
    if cache_key in _pool_cache:
        logger.debug(f"✅ Using cached pool info for {token_mint}")
        return _pool_cache[cache_key]
    
    if target_signature:
        discovery_service = PoolDiscoveryService(rpc_client)
        pool_info = await discovery_service.discover_pool_from_transaction(target_signature, token_mint)
        
        if pool_info:
            _pool_cache[cache_key] = pool_info
            logger.info(f"✅ Cached pool info for {token_mint}")
            return pool_info
    
    logger.warning(f"❌ No pool info available for {token_mint}")
    return None
