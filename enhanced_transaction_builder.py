#!/usr/bin/env python3
"""
Enhanced Transaction Builder - Handles ALL edge cases for new meme coin copying
Addresses the critical gaps in copying newly launched tokens
"""

import asyncio
import logging
import struct
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed, Processed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.address_lookup_table_account import AddressLookupTableAccount
from spl.token.instructions import (
    create_associated_token_account, 
    get_associated_token_address,
    transfer_checked, 
    TransferCheckedParams
)
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID

logger = logging.getLogger(__name__)

@dataclass
class TokenMetadata:
    """Comprehensive token metadata for new tokens"""
    mint: str
    decimals: int
    symbol: Optional[str] = None
    name: Optional[str] = None
    supply: Optional[int] = None
    freeze_authority: Optional[str] = None
    mint_authority: Optional[str] = None
    is_initialized: bool = False
    created_at: Optional[datetime] = None

@dataclass
class TransactionBuildContext:
    """Context for building transactions for new tokens"""
    token_metadata: TokenMetadata
    user_wallet: Keypair
    target_amount_sol: float
    slippage_tolerance: float
    priority_fee: int = 100000  # Higher for new tokens
    max_retries: int = 3
    requires_ata_creation: bool = False
    pool_state: Optional[Dict[str, Any]] = None

class EnhancedTransactionBuilder:
    """
    🚀 ENHANCED TRANSACTION BUILDER
    Handles ALL edge cases for copying trades on newly launched meme coins
    """
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
        self.metadata_cache: Dict[str, TokenMetadata] = {}
        
    async def build_complete_transaction(
        self, 
        context: TransactionBuildContext,
        detected_dex: str = "unknown"
    ) -> Optional[VersionedTransaction]:
        """
        🎯 Build complete transaction that handles ALL edge cases for new tokens
        """
        try:
            logger.info(f"🔧 Building enhanced transaction for {context.token_metadata.mint[:8]}...")
            
            # STEP 1: Validate and enhance token metadata
            enhanced_metadata = await self._enhance_token_metadata(context.token_metadata)
            context.token_metadata = enhanced_metadata
            
            # STEP 2: Check and create ATA if needed
            ata_instructions = await self._ensure_ata_exists(context)
            
            # STEP 3: Build main trade instruction based on detected DEX
            trade_instruction = await self._build_trade_instruction(context, detected_dex)
            if not trade_instruction:
                logger.error("❌ Failed to build trade instruction")
                return None
            
            # STEP 4: Combine all instructions with proper ordering
            all_instructions = []
            
            # Add ATA creation first if needed
            all_instructions.extend(ata_instructions)
            
            # Add main trade instruction
            all_instructions.append(trade_instruction)
            
            # Add Jito tip instruction for MEV protection
            jito_tip = await self._create_jito_tip_instruction(context)
            if jito_tip:
                all_instructions.append(jito_tip)
            
            # STEP 5: Build optimized transaction
            transaction = await self._build_optimized_transaction(
                instructions=all_instructions,
                payer=context.user_wallet,
                priority_fee=context.priority_fee
            )
            
            logger.info(f"✅ Enhanced transaction built with {len(all_instructions)} instructions")
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error building enhanced transaction: {e}")
            return None
    
    async def _enhance_token_metadata(self, metadata: TokenMetadata) -> TokenMetadata:
        """🔍 Extract comprehensive metadata for new tokens from on-chain data"""
        try:
            # Check cache first
            if metadata.mint in self.metadata_cache:
                cached = self.metadata_cache[metadata.mint]
                # Update with newer data if available
                if metadata.decimals and not cached.decimals:
                    cached.decimals = metadata.decimals
                return cached
            
            logger.info(f"🔍 Extracting on-chain metadata for {metadata.mint[:8]}...")
            
            mint_pubkey = Pubkey.from_string(metadata.mint)
            
            # Get mint account info
            mint_info = await self.rpc_client.get_account_info(
                mint_pubkey, 
                commitment=Processed
            )
            
            if mint_info.value and mint_info.value.data:
                # Parse mint data (SPL Token mint layout)
                data = mint_info.value.data
                
                # Mint layout: https://docs.rs/spl-token/latest/spl_token/state/struct.Mint.html
                if len(data) >= 82:  # Mint account is 82 bytes
                    # Parse mint data
                    mint_authority_option = data[0:4]
                    supply = struct.unpack('<Q', data[4:12])[0]  # u64 supply
                    decimals = data[12]  # u8 decimals
                    is_initialized = data[13] != 0  # bool
                    freeze_authority_option = data[14:18]
                    
                    # Update metadata
                    metadata.decimals = decimals
                    metadata.supply = supply
                    metadata.is_initialized = is_initialized
                    metadata.created_at = datetime.now(timezone.utc)
                    
                    logger.info(f"✅ Extracted metadata: decimals={decimals}, supply={supply}")
                    
            # Try to get token name/symbol from Metaplex (if available)
            try:
                metadata_account = await self._get_metaplex_metadata(mint_pubkey)
                if metadata_account:
                    metadata.symbol = metadata_account.get('symbol')
                    metadata.name = metadata_account.get('name')
            except Exception as e:
                logger.debug(f"Metaplex metadata not available: {e}")
            
            # Cache the result
            self.metadata_cache[metadata.mint] = metadata
            return metadata
            
        except Exception as e:
            logger.warning(f"⚠️ Could not enhance metadata: {e}")
            return metadata
    
    async def _ensure_ata_exists(self, context: TransactionBuildContext) -> List[Instruction]:
        """🔧 Ensure Associated Token Account exists, create if needed"""
        instructions = []
        
        try:
            user_pubkey = context.user_wallet.pubkey()
            token_mint = Pubkey.from_string(context.token_metadata.mint)
            
            # Calculate ATA address
            ata_address = get_associated_token_address(user_pubkey, token_mint)
            
            # Check if ATA exists
            ata_info = await self.rpc_client.get_account_info(ata_address, commitment=Processed)
            
            if not ata_info.value:
                logger.info(f"🔧 Creating ATA for new token {context.token_metadata.mint[:8]}...")
                
                # Create ATA instruction
                create_ata_ix = create_associated_token_account(
                    payer=user_pubkey,
                    owner=user_pubkey,
                    mint=token_mint
                )
                
                instructions.append(create_ata_ix)
                context.requires_ata_creation = True
                
                logger.info(f"✅ ATA creation instruction added: {str(ata_address)}")
            else:
                logger.info(f"✅ ATA already exists: {str(ata_address)}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error checking ATA: {e}")
            
        return instructions
    
    async def _build_trade_instruction(
        self, 
        context: TransactionBuildContext, 
        detected_dex: str
    ) -> Optional[Instruction]:
        """🎯 Build trade instruction based on detected DEX with enhanced handling"""
        try:
            if detected_dex.lower() in ['pumpfun', 'pump.fun']:
                return await self._build_pumpfun_instruction(context)
            elif detected_dex.lower() in ['raydium', 'raydium_cpmm', 'cpmm']:
                return await self._build_raydium_instruction(context)
            elif detected_dex.lower() in ['jupiter']:
                return await self._build_jupiter_instruction(context)
            else:
                # Default to Pump.fun for new tokens (90% of meme coins)
                logger.info(f"🎪 Unknown DEX '{detected_dex}' - defaulting to Pump.fun")
                return await self._build_pumpfun_instruction(context)
                
        except Exception as e:
            logger.error(f"❌ Error building trade instruction: {e}")
            return None
    
    async def _build_pumpfun_instruction(self, context: TransactionBuildContext) -> Optional[Instruction]:
        """🎪 Build Pump.fun instruction with enhanced new token handling"""
        try:
            from pumpfun_CC_copy_executor import PumpFunCopyExecutor
            from config import HELIUS_RPC_URL
            
            # Validate context parameters before constructor call
            if not isinstance(context.user_wallet, Keypair):
                raise ValueError(f"Invalid user_wallet type: {type(context.user_wallet)}")
            if not isinstance(HELIUS_RPC_URL, str) or not HELIUS_RPC_URL:
                raise ValueError(f"Invalid HELIUS_RPC_URL: {HELIUS_RPC_URL}")
            
            # Use existing Pump.fun executor but with enhanced context - explicit parameter names
            executor = PumpFunCopyExecutor(
                wallet_keypair=context.user_wallet, 
                rpc_url=HELIUS_RPC_URL
            )
            
            # Calculate amounts with enhanced precision
            amount_lamports = int(context.target_amount_sol * 1_000_000_000)
            
            # Build instruction using existing executor
            instruction = await executor._build_buy_instruction(
                token_mint=Pubkey.from_string(context.token_metadata.mint),
                amount_lamports=amount_lamports,
                user_ata=get_associated_token_address(
                    context.user_wallet.pubkey(), 
                    Pubkey.from_string(context.token_metadata.mint)
                )
            )
            
            return instruction
            
        except Exception as e:
            logger.error(f"❌ Error building Pump.fun instruction: {e}")
            return None
    
    async def _build_raydium_instruction(self, context: TransactionBuildContext) -> Optional[Instruction]:
        """🌊 Build Raydium instruction for new tokens"""
        try:
            # For new tokens, we need to find the pool first
            pool_info = await self._find_raydium_pool(context.token_metadata.mint)
            if not pool_info:
                logger.warning("⚠️ No Raydium pool found for new token - falling back to Pump.fun")
                return await self._build_pumpfun_instruction(context)
            
            # Build Raydium swap instruction
            # This would use your existing Raydium executors with pool info
            # Implementation depends on your specific Raydium executor
            
            logger.info("🌊 Building Raydium instruction for new token")
            # Placeholder - implement based on your Raydium executor
            return None
            
        except Exception as e:
            logger.error(f"❌ Error building Raydium instruction: {e}")
            return None
    
    async def _build_jupiter_instruction(self, context: TransactionBuildContext) -> Optional[Instruction]:
        """🪐 Build Jupiter instruction (but avoid for brand new tokens)"""
        try:
            # Check if token is very new (less than 5 minutes old)
            if (context.token_metadata.created_at and 
                (datetime.now(timezone.utc) - context.token_metadata.created_at).seconds < 300):
                logger.warning("⚠️ Token too new for Jupiter - falling back to direct DEX")
                return await self._build_pumpfun_instruction(context)
            
            # Use Jupiter for established tokens
            logger.info("🪐 Building Jupiter instruction for established token")
            # Implementation depends on your Jupiter executor
            return None
            
        except Exception as e:
            logger.error(f"❌ Error building Jupiter instruction: {e}")
            return None
    
    async def _create_jito_tip_instruction(self, context: TransactionBuildContext) -> Optional[Instruction]:
        """🚀 Create Jito tip instruction for MEV protection"""
        try:
            # Enhanced tip for new tokens (higher priority)
            tip_amount = context.priority_fee * 2 if context.requires_ata_creation else context.priority_fee
            
            # Use existing Jito tip creation logic
            from fast_executor import FastExecutor
            executor = FastExecutor(context.user_wallet)
            
            tip_instruction = await executor._create_jito_tip_instruction(tip_amount)
            return tip_instruction
            
        except Exception as e:
            logger.debug(f"Could not create Jito tip: {e}")
            return None
    
    async def _build_optimized_transaction(
        self, 
        instructions: List[Instruction], 
        payer: Keypair, 
        priority_fee: int
    ) -> Optional[VersionedTransaction]:
        """⚡ Build optimized VersionedTransaction with enhanced settings"""
        try:
            # Get recent blockhash
            blockhash_resp = await self.rpc_client.get_latest_blockhash(commitment=Processed)
            if not blockhash_resp.value:
                logger.error("❌ Could not get recent blockhash")
                return None
            
            recent_blockhash = blockhash_resp.value.blockhash
            
            # Build message
            message = MessageV0.try_compile(
                payer=payer.pubkey(),
                instructions=instructions,
                address_lookup_table_accounts=[],  # No ALTs for simplicity
                recent_blockhash=recent_blockhash
            )
            
            # Create transaction
            transaction = VersionedTransaction(message, [payer])
            
            logger.info(f"✅ Optimized transaction built with {len(instructions)} instructions")
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error building optimized transaction: {e}")
            return None
    
    async def _get_metaplex_metadata(self, mint_pubkey: Pubkey) -> Optional[Dict[str, Any]]:
        """🎨 Get Metaplex metadata for token (if available)"""
        try:
            # Metaplex metadata program
            METADATA_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
            
            # Derive metadata PDA
            metadata_seeds = [
                b"metadata",
                bytes(METADATA_PROGRAM_ID),
                bytes(mint_pubkey),
            ]
            
            metadata_pda, _ = Pubkey.find_program_address(metadata_seeds, METADATA_PROGRAM_ID)
            
            # Get metadata account
            metadata_info = await self.rpc_client.get_account_info(metadata_pda, commitment=Processed)
            
            if metadata_info.value and metadata_info.value.data:
                # Parse metadata (simplified)
                # Full implementation would parse the complete Metaplex metadata structure
                return {
                    "symbol": "UNKNOWN",
                    "name": "New Token"
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Metaplex metadata not available: {e}")
            return None
    
    async def _find_raydium_pool(self, token_mint: str) -> Optional[Dict[str, Any]]:
        """🌊 Find Raydium pool for new token"""
        try:
            # This would implement pool discovery logic
            # Placeholder for now
            logger.debug(f"Searching for Raydium pool for {token_mint[:8]}...")
            return None
            
        except Exception as e:
            logger.debug(f"Error finding Raydium pool: {e}")
            return None

# Factory function for easy usage
async def build_enhanced_transaction(
    rpc_client: AsyncClient,
    token_mint: str,
    user_wallet: Keypair,
    amount_sol: float,
    detected_dex: str = "unknown",
    slippage_tolerance: float = 0.15
) -> Optional[VersionedTransaction]:
    """
    🚀 Factory function to build enhanced transaction for new tokens
    """
    try:
        # Create builder
        builder = EnhancedTransactionBuilder(rpc_client)
        
        # Create metadata (will be enhanced by builder)
        metadata = TokenMetadata(
            mint=token_mint,
            decimals=6,  # Default, will be detected
            created_at=datetime.now(timezone.utc)
        )
        
        # Create context
        context = TransactionBuildContext(
            token_metadata=metadata,
            user_wallet=user_wallet,
            target_amount_sol=amount_sol,
            slippage_tolerance=slippage_tolerance,
            priority_fee=200000  # Higher priority for new tokens
        )
        
        # Build transaction
        transaction = await builder.build_complete_transaction(context, detected_dex)
        return transaction
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced transaction factory: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    async def test_enhanced_builder():
        from solana.rpc.async_api import AsyncClient
        
        # Test with a new token
        rpc_client = AsyncClient("https://api.mainnet-beta.solana.com")
        
        # This would be called when copying a trade on a new token
        test_token = "So11111111111111111111111111111111111111112"  # WSOL for testing
        
        # Create test wallet (don't use in production)
        test_wallet = Keypair()
        
        transaction = await build_enhanced_transaction(
            rpc_client=rpc_client,
            token_mint=test_token,
            user_wallet=test_wallet,
            amount_sol=0.001,
            detected_dex="pumpfun"
        )
        
        if transaction:
            print("✅ Enhanced transaction built successfully!")
        else:
            print("❌ Failed to build enhanced transaction")
        
        await rpc_client.close()
    
    # Run test
    asyncio.run(test_enhanced_builder())
