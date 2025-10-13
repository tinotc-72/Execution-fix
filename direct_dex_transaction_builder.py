#!/usr/bin/env python3
"""
Direct DEX Transaction Builder for Jito Execution
Builds transactions directly for specific DEXs without relying on Jupiter
Optimized for new meme coins that may not have Jupiter liquidity yet
"""

import asyncio
import base64
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.system_program import transfer
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

# Configure logging
logger = logging.getLogger(__name__)

# DEX Program IDs
RAYDIUM_CPMM_PROGRAM_ID = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
RAYDIUM_AMM_PROGRAM_ID = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
PUMPFUN_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMPFUN_ROUTER_ID = Pubkey.from_string("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW")
ORCA_WHIRLPOOL_ID = Pubkey.from_string("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc")

# Common tokens
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

@dataclass
class DirectTransactionResult:
    """Result from direct DEX transaction building"""
    transaction: Optional[VersionedTransaction] = None
    error: Optional[str] = None
    success: bool = False
    dex_used: Optional[str] = None

class DirectDEXTransactionBuilder:
    """Builds transactions directly for specific DEXs for Jito execution"""
    
    def __init__(self, rpc_client: AsyncClient, wallet: Keypair):
        self.rpc_client = rpc_client
        self.wallet = wallet
        self.wallet_pubkey = wallet.pubkey()
    
    async def build_transaction(
        self,
        token_mint: str,
        detected_dex: str,
        amount_sol: float,
        extra_params: Dict[str, Any] = None
    ) -> DirectTransactionResult:
        """
        Build transaction for the specified DEX
        
        Args:
            token_mint: Target token mint address
            detected_dex: DEX to use (Raydium, Pump.fun, Orca, etc.)
            amount_sol: Amount of SOL to spend
            extra_params: Additional parameters
        """
        try:
            logger.info(f"🚀 Building direct {detected_dex} transaction for {token_mint[:8]}...")
            
            # Convert to standard format
            dex = detected_dex.lower().strip()
            
            if "raydium" in dex:
                return await self._build_raydium_transaction(token_mint, amount_sol, extra_params)
            elif "pump" in dex or "pumpfun" in dex:
                return await self._build_pumpfun_transaction(token_mint, amount_sol, extra_params)
            elif "orca" in dex:
                return await self._build_orca_transaction(token_mint, amount_sol, extra_params)
            else:
                error_msg = f"Unsupported DEX for direct transaction building: {detected_dex}"
                logger.warning(error_msg)
                return DirectTransactionResult(error=error_msg, success=False)
                
        except Exception as e:
            error_msg = f"Error building direct {detected_dex} transaction: {e}"
            logger.error(error_msg)
            return DirectTransactionResult(error=error_msg, success=False)
    
    async def _build_raydium_transaction(
        self,
        token_mint: str,
        amount_sol: float,
        extra_params: Dict[str, Any] = None
    ) -> DirectTransactionResult:
        """Build direct Raydium CPMM transaction"""
        try:
            logger.info(f"   📦 Building Raydium CPMM transaction...")
            
            # For new meme coins, try to use your existing Raydium executor
            # to build the transaction instructions
            from official_executor_wrappers import execute_raydium_buy
            
            # Get the pool info first
            token_pubkey = Pubkey.from_string(token_mint)
            
            # Try to find the pool for this token
            pool_info = await self._find_raydium_pool(token_mint)
            if not pool_info:
                logger.warning(f"   ⚠️ No Raydium pool found for {token_mint[:8]}...")
                return DirectTransactionResult(
                    error=f"No Raydium pool found for {token_mint}",
                    success=False
                )
            
            logger.info(f"   ✅ Found Raydium pool: {pool_info.get('pool_id', 'Unknown')[:8]}...")
            
            # Build the swap instruction
            instructions = await self._build_raydium_swap_instructions(
                token_mint, amount_sol, pool_info
            )
            
            if not instructions:
                return DirectTransactionResult(
                    error="Failed to build Raydium swap instructions",
                    success=False
                )
            
            # Create the transaction
            transaction = await self._create_versioned_transaction(instructions)
            
            logger.info(f"   ✅ Raydium transaction built successfully!")
            return DirectTransactionResult(
                transaction=transaction,
                success=True,
                dex_used="Raydium"
            )
            
        except Exception as e:
            error_msg = f"Error building Raydium transaction: {e}"
            logger.error(error_msg)
            return DirectTransactionResult(error=error_msg, success=False)
    
    async def _build_pumpfun_transaction(
        self,
        token_mint: str,
        amount_sol: float,
        extra_params: Dict[str, Any] = None
    ) -> DirectTransactionResult:
        """Build direct Pump.fun transaction - FASTEST for new meme coins"""
        try:
            logger.info(f"   🎪 Building Pump.fun transaction...")
            
            # Pump.fun is often the first DEX for new meme coins
            # Use direct Pump.fun instructions for maximum speed
            
            # Convert SOL amount to lamports
            lamports = int(amount_sol * 1e9)
            
            # Build Pump.fun buy instruction
            instructions = await self._build_pumpfun_buy_instructions(
                token_mint, lamports
            )
            
            if not instructions:
                return DirectTransactionResult(
                    error="Failed to build Pump.fun buy instructions",
                    success=False
                )
            
            # Create the transaction
            transaction = await self._create_versioned_transaction(instructions)
            
            logger.info(f"   ✅ Pump.fun transaction built successfully!")
            return DirectTransactionResult(
                transaction=transaction,
                success=True,
                dex_used="Pump.fun"
            )
            
        except Exception as e:
            error_msg = f"Error building Pump.fun transaction: {e}"
            logger.error(error_msg)
            return DirectTransactionResult(error=error_msg, success=False)
    
    async def _build_orca_transaction(
        self,
        token_mint: str,
        amount_sol: float,
        extra_params: Dict[str, Any] = None
    ) -> DirectTransactionResult:
        """Build direct Orca transaction"""
        try:
            logger.info(f"   🐳 Building Orca transaction...")
            
            # Similar approach for Orca
            # Find the whirlpool for this token
            pool_info = await self._find_orca_pool(token_mint)
            if not pool_info:
                return DirectTransactionResult(
                    error=f"No Orca pool found for {token_mint}",
                    success=False
                )
            
            # Build Orca swap instructions
            instructions = await self._build_orca_swap_instructions(
                token_mint, amount_sol, pool_info
            )
            
            if not instructions:
                return DirectTransactionResult(
                    error="Failed to build Orca swap instructions",
                    success=False
                )
            
            # Create the transaction
            transaction = await self._create_versioned_transaction(instructions)
            
            logger.info(f"   ✅ Orca transaction built successfully!")
            return DirectTransactionResult(
                transaction=transaction,
                success=True,
                dex_used="Orca"
            )
            
        except Exception as e:
            error_msg = f"Error building Orca transaction: {e}"
            logger.error(error_msg)
            return DirectTransactionResult(error=error_msg, success=False)
    
    async def _create_versioned_transaction(
        self,
        instructions: List[Instruction]
    ) -> VersionedTransaction:
        """Create a VersionedTransaction from instructions"""
        try:
            # Add compute budget instructions for higher fees
            compute_instructions = [
                set_compute_unit_limit(300_000),  # Higher limit for complex swaps
                set_compute_unit_price(100_000),  # Higher priority fee (0.0001 SOL)
            ]
            
            # Combine all instructions
            all_instructions = compute_instructions + instructions
            
            # Get recent blockhash
            recent_blockhash = await self.rpc_client.get_latest_blockhash()
            
            # Create message
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=all_instructions,
                address_lookup_tables=[],
                recent_blockhash=recent_blockhash.value.blockhash
            )
            
            # Create transaction
            transaction = VersionedTransaction(message, [])
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating versioned transaction: {e}")
            raise
    
    async def _find_raydium_pool(self, token_mint: str) -> Optional[Dict[str, Any]]:
        """Find Raydium pool for the token"""
        try:
            # This would typically query Raydium's pool data
            # For now, return a placeholder that indicates we should try
            # the official executor instead
            
            # Try to use your existing Raydium pool finding logic
            from cpmm_pool_scanner import find_pool_for_token
            
            pool_info = await find_pool_for_token(token_mint)
            return pool_info
            
        except Exception as e:
            logger.debug(f"Error finding Raydium pool: {e}")
            return None
    
    async def _find_orca_pool(self, token_mint: str) -> Optional[Dict[str, Any]]:
        """Find Orca pool for the token"""
        try:
            # Similar to Raydium, this would query Orca's pool data
            # Implementation depends on your existing Orca integration
            return None
            
        except Exception as e:
            logger.debug(f"Error finding Orca pool: {e}")
            return None
    
    async def _build_raydium_swap_instructions(
        self,
        token_mint: str,
        amount_sol: float,
        pool_info: Dict[str, Any]
    ) -> Optional[List[Instruction]]:
        """Build Raydium swap instructions"""
        try:
            # This would build the actual Raydium swap instructions
            # For now, return None to fall back to existing executors
            logger.info(f"   🔧 Building Raydium swap instructions...")
            return None
            
        except Exception as e:
            logger.error(f"Error building Raydium swap instructions: {e}")
            return None
    
    async def _build_pumpfun_buy_instructions(
        self,
        token_mint: str,
        lamports: int
    ) -> Optional[List[Instruction]]:
        """Build Pump.fun buy instructions"""
        try:
            # This would build the actual Pump.fun buy instructions
            # For now, return None to fall back to existing executors
            logger.info(f"   🔧 Building Pump.fun buy instructions...")
            return None
            
        except Exception as e:
            logger.error(f"Error building Pump.fun buy instructions: {e}")
            return None
    
    async def _build_orca_swap_instructions(
        self,
        token_mint: str,
        amount_sol: float,
        pool_info: Dict[str, Any]
    ) -> Optional[List[Instruction]]:
        """Build Orca swap instructions"""
        try:
            # This would build the actual Orca swap instructions
            logger.info(f"   🔧 Building Orca swap instructions...")
            return None
            
        except Exception as e:
            logger.error(f"Error building Orca swap instructions: {e}")
            return None
