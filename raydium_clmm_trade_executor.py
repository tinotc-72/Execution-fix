#!/usr/bin/env python3
"""
Raydium CLMM Trade Executor using the correct program ID
Uses the official Raydium CLMM program ID: CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK
Adapted from proven working raydium_trade_executor.py pattern
"""

import asyncio
import sys
import os
import struct
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

from env_keys import load_wallet_from_private_key, kz
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Correct Raydium CLMM program ID
CLMM_PROGRAM_ID = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

class TradeAction(Enum):
    BUY = "buy"
    SELL = "sell"

class TradeResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"

@dataclass
class CLMMTradeConfig:
    """Configuration for CLMM trade execution"""
    sol_amount: float = 0.001
    slippage_tolerance: float = 0.05
    max_retries: int = 2
    retry_delay: float = 1.0
    confirmation_timeout: float = 30.0
    compute_unit_limit: int = 200_000
    compute_unit_price: int = 100_000

class RaydiumCLMMTradeExecutor:
    """
    Raydium CLMM (Concentrated Liquidity Market Maker) trade executor
    Based on the proven working pattern from raydium_trade_executor.py
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: CLMMTradeConfig = None):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.client = AsyncClient(rpc_url)
        self.config = config or CLMMTradeConfig()
        
        # Cache for pool information
        self.pool_cache = {}
        
        # Known mints
        self.NATIVE_MINT = SOL_MINT
        self.USDC_MINT = USDC_MINT
        
        # Known SOL/USDC CLMM pool (this would need to be discovered or hardcoded)
        # For testing purposes, we'll use a placeholder
        self.SOL_USDC_CLMM_POOL = None  # To be discovered
        
        logger.info(f"🚀 Raydium CLMM Executor initialized")
        logger.info(f"   Wallet: {self.wallet_pubkey}")
        logger.info(f"   CLMM Program: {CLMM_PROGRAM_ID}")
        
    async def get_sol_balance(self) -> float:
        """Get current SOL balance"""
        try:
            balance = await self.client.get_balance(self.wallet_pubkey)
            return balance.value / 1_000_000_000 if balance.value else 0.0
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0

    async def get_token_balance(self, token_mint: Pubkey) -> int:
        """Get current token balance for a specific mint"""
        try:
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            balance_result = await self.client.get_token_account_balance(token_account)
            if balance_result.value:
                return int(balance_result.value.amount)
            return 0
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0

    async def ensure_token_account_exists(self, token_mint: Pubkey) -> Pubkey:
        """
        ENHANCED: Check first, create only if needed - ELIMINATES IllegalOwner errors
        """
        # Calculate ATA address
        ata = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        # 🔍 STEP 1: CHECK IF ATA ALREADY EXISTS
        logger.info(f"🔍 Checking if ATA exists for token {str(token_mint)[:8]}...")
        try:
            account_info = await self.client.get_account_info(ata)
            if account_info.value is not None:
                logger.info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                return ata
        except Exception as e:
            logger.debug(f"Error checking ATA existence: {e}")
        
        # 🔨 STEP 2: CREATE ATA ONLY IF IT DOESN'T EXIST
        logger.info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
        
        logger.info(f"🔨 Creating ATA for token: {token_mint}")
        
        # Create ATA instruction
        create_ata_ix = create_associated_token_account(
            payer=self.wallet_pubkey,
            owner=self.wallet_pubkey,
            mint=token_mint
        )
        
        try:
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[
                    set_compute_unit_limit(self.config.compute_unit_limit),
                    set_compute_unit_price(self.config.compute_unit_price),
                    create_ata_ix
                ],
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            result = await self.client.send_transaction(transaction)
            if result.value:
                logger.info(f"✅ ATA created: {ata}")
                await asyncio.sleep(2)  # Wait for confirmation
            return ata
        except Exception as e:
            logger.error(f"Error creating ATA: {e}")
            return ata

    async def find_clmm_pool_for_tokens(self, token_a: Pubkey, token_b: Pubkey) -> Optional[Dict[str, Any]]:
        """Find CLMM pool for a given token pair"""
        # This is a simplified implementation
        # In a real implementation, you would:
        # 1. Query Raydium's API for pool information
        # 2. Use the official pool discovery endpoints
        # 3. Or maintain a database of known pools
        
        logger.info(f"🔍 Finding CLMM pool for {token_a} / {token_b}")
        
        # For SOL/USDC, we can use known pool information
        # This would normally be fetched from Raydium's API
        if ((str(token_a) == str(self.NATIVE_MINT) and str(token_b) == str(self.USDC_MINT)) or
            (str(token_a) == str(self.USDC_MINT) and str(token_b) == str(self.NATIVE_MINT))):
            
            # Placeholder pool info - in reality this would be discovered
            # You would need to query Raydium's API or use their SDK
            logger.warning("⚠️ Using placeholder pool info - implement pool discovery")
            
            return {
                "pool_id": "PLACEHOLDER_POOL_ID",  # Would be actual pool address
                "token_a": token_a,
                "token_b": token_b,
                "tick_spacing": 60,  # Common tick spacing for SOL/USDC
                "pool_state": "PLACEHOLDER_POOL_STATE",
                "token_vault_a": "PLACEHOLDER_VAULT_A",
                "token_vault_b": "PLACEHOLDER_VAULT_B",
                "observation_state": "PLACEHOLDER_OBSERVATION",
                "bitmap_a": "PLACEHOLDER_BITMAP_A",
                "bitmap_b": "PLACEHOLDER_BITMAP_B"
            }
        
        return None

    async def execute_buy_trade(self, token_mint: Pubkey, sol_amount: Optional[float] = None) -> Optional[str]:
        """Execute a buy trade on Raydium CLMM"""
        sol_amount = sol_amount or self.config.sol_amount
        logger.info(f"🛒 Executing CLMM BUY trade: {sol_amount} SOL for {token_mint}")
        
        try:
            # Find CLMM pool
            pool_info = await self.find_clmm_pool_for_tokens(self.NATIVE_MINT, token_mint)
            if not pool_info:
                logger.error(f"❌ No CLMM pool found for {token_mint}")
                return None
            
            # Ensure token account exists
            await self.ensure_token_account_exists(token_mint)
            
            # For now, return a placeholder indicating the framework is ready
            logger.info("🏗️ CLMM buy trade framework ready")
            logger.info("💡 Next step: Implement actual CLMM swap instruction")
            logger.info("📚 This requires:")
            logger.info("   - Proper pool discovery via Raydium API")
            logger.info("   - CLMM swap instruction data format")
            logger.info("   - Tick calculation for concentrated liquidity")
            logger.info("   - Price impact calculation")
            
            return "CLMM_BUY_READY"
            
        except Exception as e:
            logger.error(f"❌ CLMM buy trade error: {e}")
            return None

    async def execute_sell_trade(self, token_mint: Pubkey, token_amount: Optional[int] = None, **kwargs) -> Optional[str]:
        """Execute a sell trade on Raydium CLMM with proportional selling support"""
        logger.info(f"💸 Executing CLMM SELL trade: {token_amount or 'ALL'} tokens for {token_mint}")
        
        try:
            # Get token balance if amount not specified
            if token_amount is None:
                token_amount = await self.get_token_balance(token_mint)
            
            if token_amount <= 0:
                logger.error(f"❌ No tokens to sell for {token_mint}")
                return None

            # Proportional sell calculation
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            if sell_percentage <= 0 or sell_percentage > 100.0:
                logger.warning(f"⚠️ Invalid sell_percentage {sell_percentage}, defaulting to 100%.")
                sell_percentage = 100.0
            
            # Calculate proportional amount to sell
            proportional_amount = int(token_amount * (sell_percentage / 100.0))
            logger.info(f"🎯 CLMM PROPORTIONAL SELL:\n   Total balance: {token_amount} tokens\n   Amount to sell: {proportional_amount} tokens\n   Sell percentage: {sell_percentage:.2f}%")
            
            # Use proportional amount
            token_amount = proportional_amount
            
            # Find CLMM pool
            pool_info = await self.find_clmm_pool_for_tokens(token_mint, self.NATIVE_MINT)
            if not pool_info:
                logger.error(f"❌ No CLMM pool found for {token_mint}")
                return None
            
            # For now, return a placeholder indicating the framework is ready
            logger.info("🏗️ CLMM sell trade framework ready")
            logger.info("💡 Next step: Implement actual CLMM swap instruction")
            
            return "CLMM_SELL_READY"
            
        except Exception as e:
            logger.error(f"❌ CLMM sell trade error: {e}")
            return None

    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with specified timeout"""
        try:
            sig = Signature.from_string(signature)
            
            for i in range(int(timeout)):
                try:
                    status = await self.client.get_transaction(sig, max_supported_transaction_version=0)
                    if status.value:
                        if hasattr(status.value, 'meta') and status.value.meta and status.value.meta.err:
                            logger.error(f"Transaction failed: {status.value.meta.err}")
                            return False
                        else:
                            logger.info(f"✅ Transaction confirmed: {signature}")
                            return True
                except:
                    pass
                await asyncio.sleep(1)
            
            logger.warning("⚠️ Transaction confirmation timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error confirming transaction: {e}")
            return False

    async def close(self):
        """Close the client connection"""
        await self.client.close()

async def test_clmm_executor():
    """Test the CLMM executor"""
    print("🚀 Testing Raydium CLMM Trade Executor...")
    
    # Load wallet
    try:
        wallet_keypair = load_wallet_from_private_key()
        if not wallet_keypair:
            print("❌ Failed to load wallet keypair")
            return
        
        print(f"✅ Wallet loaded: {wallet_keypair.pubkey()}")
        
    except Exception as e:
        print(f"❌ Error loading wallet: {e}")
        return
    
    # Create CLMM executor
    config = CLMMTradeConfig(
        sol_amount=0.001,
        slippage_tolerance=0.05,
        max_retries=2,
        confirmation_timeout=30.0
    )
    
    executor = RaydiumCLMMTradeExecutor(
        wallet_keypair=wallet_keypair,
        rpc_url=kz.HELIUS_RPC_URL,
        config=config
    )
    
    print(f"💰 Current SOL balance: {await executor.get_sol_balance():.6f} SOL")
    print(f"💰 Current USDC balance: {await executor.get_token_balance(USDC_MINT):.6f} USDC")
    
    try:
        # Test buy trade framework
        print("\n🛒 Testing CLMM BUY trade framework...")
        buy_result = await executor.execute_buy_trade(USDC_MINT, 0.001)
        
        if buy_result == "CLMM_BUY_READY":
            print("✅ CLMM buy trade framework is ready!")
        
        # Test sell trade framework
        print("\n💸 Testing CLMM SELL trade framework...")
        sell_result = await executor.execute_sell_trade(USDC_MINT)
        
        if sell_result == "CLMM_SELL_READY":
            print("✅ CLMM sell trade framework is ready!")
        
        print("\n🎯 CLMM Trade Executor Framework Complete!")
        print("📋 Next steps to complete implementation:")
        print("   1. Implement Raydium API integration for pool discovery")
        print("   2. Add CLMM swap instruction building")
        print("   3. Implement tick calculation for concentrated liquidity")
        print("   4. Add price impact and slippage calculations")
        print("   5. Test with actual CLMM pools")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        logger.error(f"Test error: {e}")
        
    finally:
        await executor.close()

if __name__ == "__main__":
    asyncio.run(test_clmm_executor())
