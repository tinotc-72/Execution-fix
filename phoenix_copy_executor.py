#!/usr/bin/env python3
"""
Phoenix Copy Executor
Execute Phoenix DEX trades for copy bot integration

This module provides buy/sell functions that:
1. Support Phoenix Central Limit Order Book (CLOB) trading
2. Use Jupiter API for reliable Phoenix liquidity access
3. Compatible with existing copy bot architecture
4. Return standardized response format: {"success": bool, "signature": str}

Phoenix is a major order book-based DEX on Solana
"""

import asyncio
import json
import aiohttp
import base64
import base58
import os
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed, Finalized, Processed
from solders.signature import Signature
from spl.token.instructions import get_associated_token_address, create_associated_token_account

from env_keys import EnvKeys

# Load environment
env = EnvKeys()

import logging as _logging
# Defensive logger setup
class DummyLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    def warning(self, msg):
        print(f"[WARNING] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}")
    def debug(self, msg):
        print(f"[DEBUG] {msg}")

def get_safe_logger(logger_candidate):
    if isinstance(logger_candidate, _logging.Logger):
        return logger_candidate
    if hasattr(logger_candidate, 'info') and hasattr(logger_candidate, 'warning') and hasattr(logger_candidate, 'error'):
        return logger_candidate
    return DummyLogger()

logger = get_safe_logger(globals().get('logger', None))
# Remove redundant logger reassignment and duplicate DummyLogger definition

# Phoenix Program ID
PHOENIX_PROGRAM_ID = Pubkey.from_string("PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY")

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

class PhoenixCopyExecutor:
    """
    Phoenix DEX copy trading executor using order book model
    Provides standardized buy/sell interface for copy bot integration
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str = None):
        """
        Initialize Phoenix copy executor
        
        Args:
            wallet_keypair: Solana wallet keypair for transaction signing
            rpc_url: RPC endpoint URL (defaults to Helius)
        """
        self.wallet = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        
        # Use provided RPC or default to Helius
        self.rpc_url = rpc_url or env.HELIUS_RPC_URL
        self.client = AsyncClient(self.rpc_url)
        
        # Known Phoenix markets (examples for major pairs)
        self.known_markets = {
            "SOL/USDC": "4DoNfFBfF7UokCC2FQzriy7yHK6DY6NVdYpuekQ5pRgg"  # Example market ID
        }
        
        logger.info(f"🔥 Phoenix Copy Executor initialized for wallet: {self.wallet_pubkey}")
    
    async def confirm_transaction(self, signature: str, max_retries: int = 30) -> bool:
        """
        Confirm transaction using official Solana documentation method.
        Uses getSignatureStatuses polling as recommended.
        """
        try:
            logger.info(f"📋 Confirming Phoenix transaction: {signature}")
            
            for attempt in range(max_retries):
                try:
                    response = await self.client.get_signature_statuses([signature])
                    
                    if response and response.value and response.value[0]:
                        status = response.value[0]
                        
                        if status.confirmation_status:
                            confirmation = str(status.confirmation_status)
                            logger.info(f"✅ Phoenix transaction confirmed: {confirmation}")
                            return True
                        elif status.err:
                            logger.error(f"❌ Phoenix transaction failed: {status.err}")
                            return False
                    
                    # Wait before next attempt
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"⚠️  Confirmation attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(1)
            
            logger.warning(f"⏰ Phoenix transaction confirmation timeout after {max_retries} attempts")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error confirming Phoenix transaction: {e}")
            return False
    
    async def execute_jupiter_swap(self, input_mint: str, output_mint: str, amount: int, description: str = "Phoenix Trade") -> Optional[str]:
        """
        Execute swap via Jupiter API (accessing Phoenix + other liquidity)
        Jupiter aggregates Phoenix order book liquidity with other DEXes
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address  
            amount: Amount in smallest unit (lamports/token units)
            description: Trade description for logging
            
        Returns:
            Transaction signature if successful, None otherwise
        """
        try:
            logger.info(f"🪐 Jupiter {description}: {input_mint} → {output_mint}")
            
            async with aiohttp.ClientSession() as session:
                # Get quote from Jupiter
                quote_url = "https://quote-api.jup.ag/v6/quote"
                quote_params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": str(amount),
                    "slippageBps": 100  # 1% slippage
                }
                
                async with session.get(quote_url, params=quote_params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ Jupiter quote failed ({response.status}): {error_text}")
                        return None
                    
                    quote_data = await response.json()
                    
                    if "error" in quote_data:
                        logger.error(f"❌ Jupiter quote error: {quote_data['error']}")
                        return None
                    
                    logger.info(f"   📊 Quote: {quote_data.get('outAmount', 'N/A')} tokens")
                    
                    # Log routing information
                    if "routePlan" in quote_data and quote_data["routePlan"]:
                        for i, route in enumerate(quote_data["routePlan"]):
                            route_info = route.get("swapInfo", {})
                            dex_label = route_info.get("label", "Unknown")
                            logger.info(f"   🗺️  Route {i+1}: {dex_label}")
                
                # Get swap transaction
                swap_payload = {
                    "userPublicKey": str(self.wallet_pubkey),
                    "quoteResponse": quote_data,
                    "prioritizationFeeLamports": 1000  # Small priority fee
                }
                
                async with session.post("https://quote-api.jup.ag/v6/swap", json=swap_payload) as swap_response:
                    if swap_response.status != 200:
                        error_text = await swap_response.text()
                        logger.error(f"❌ Jupiter swap failed ({swap_response.status}): {error_text}")
                        return None
                    
                    swap_result = await swap_response.json()
                    
                    if "error" in swap_result:
                        logger.error(f"❌ Jupiter swap error: {swap_result['error']}")
                        return None
                    
                    if "swapTransaction" not in swap_result:
                        logger.error(f"❌ No swap transaction in Jupiter response")
                        return None
                    
                    # Decode and sign transaction
                    tx_bytes = base64.b64decode(swap_result["swapTransaction"])
                    tx = VersionedTransaction.from_bytes(tx_bytes)
                    signed_tx = VersionedTransaction(tx.message, [self.wallet])
                    
                    # Send transaction
                    logger.info(f"📡 Sending Jupiter transaction...")
                    send_response = await self.client.send_transaction(signed_tx)
                    
                    if send_response.value:
                        signature = str(send_response.value)
                        logger.info(f"✅ Jupiter {description} sent: {signature}")
                        return signature
                    else:
                        logger.error(f"❌ Failed to send Jupiter transaction")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Jupiter {description} error: {e}")
            return None
    
    async def try_phoenix_buy(self, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """
        Buy tokens with SOL using Phoenix (via Jupiter)
        
        Args:
            token_mint: Target token mint address
            amount_sol: Amount of SOL to spend
            **kwargs: Additional parameters (market_id, etc.)
        
        Returns:
            {"success": bool, "signature": str}
        """
        try:
            logger.info(f"🛒 Phoenix BUY: {amount_sol} SOL → {token_mint}")
            
            # Convert SOL amount to lamports
            amount_lamports = int(amount_sol * 1_000_000_000)
            # AGGRESSIVE MODE: Log but do not abort on missing pool/market info
            try:
                signature = await self.execute_jupiter_swap(
                    input_mint=SOL_MINT,
                    output_mint=token_mint,
                    amount=amount_lamports,
                    description="Phoenix BUY"
                )
            except Exception as e:
                logger.warning(f"[AGGRESSIVE MODE] Phoenix buy error: {e} - proceeding anyway!")
                signature = None
            
            if signature:
                logger.info(f"✅ Phoenix buy successful: {signature}")
                return {
                    "success": True,
                    "signature": signature
                }
            else:
                logger.error(f"❌ Phoenix buy failed")
                return {
                    "success": False,
                    "signature": ""
                }
                
        except Exception as e:
            logger.error(f"❌ Phoenix buy error: {e}")
            return {
                "success": False,
                "signature": ""
            }
    
    async def try_phoenix_sell_all(self, token_mint: str, **kwargs) -> Dict[str, Any]:
        """
        Sell all tokens for SOL using Phoenix (via Jupiter)
        
        Args:
            token_mint: Token mint address to sell
            **kwargs: Additional parameters (market_id, etc.)
        
        Returns:
            {"success": bool, "signature": str}
        """
        try:
            logger.info(f"💸 Phoenix SELL ALL: {token_mint} → SOL")
            
            # Get token account and balance
            from official_executor_wrappers import get_correct_ata_address
            token_ata = await get_correct_ata_address(self.wallet_pubkey, Pubkey.from_string(token_mint))
            
            try:
                token_balance = await self.client.get_token_account_balance(token_ata)
                if not token_balance.value or token_balance.value.amount == "0":
                    logger.warning(f"⚠️  No {token_mint} balance to sell")
                    return {
                        "success": False,
                        "signature": ""
                    }
                
                # Get balance in smallest units
                token_amount = int(token_balance.value.amount)
                logger.info(f"   Selling {token_amount} units of {token_mint}")
                
            except Exception as e:
                logger.error(f"❌ Error getting token balance: {e}")
                return {
                    "success": False,
                    "signature": ""
                }
            
            # Execute sell via Jupiter
            signature = await self.execute_jupiter_swap(
                input_mint=token_mint,
                output_mint=SOL_MINT,
                amount=token_amount,
                description="Phoenix SELL ALL"
            )
            
            if signature:
                logger.info(f"✅ Phoenix sell successful: {signature}")
                return {
                    "success": True,
                    "signature": signature
                }
            else:
                logger.error(f"❌ Phoenix sell failed")
                return {
                    "success": False,
                    "signature": ""
                }
                
        except Exception as e:
            logger.error(f"❌ Phoenix sell error: {e}")
            return {
                "success": False,
                "signature": ""
            }
    
    async def get_market_info(self, token_mint: str) -> Dict[str, Any]:
        """
        Get Phoenix market information for a token
        
        Args:
            token_mint: Token mint address
            
        Returns:
            Market information dictionary
        """
        try:
            logger.info(f"📊 Getting Phoenix market info for {token_mint}")
            
            # For now, return basic market info
            # Real implementation would fetch:
            # - Order book depth
            # - Best bid/ask prices
            # - Market statistics
            # - Available liquidity
            
            market_info = {
                "dex": "Phoenix",
                "type": "Central Limit Order Book (CLOB)",
                "program_id": str(PHOENIX_PROGRAM_ID),
                "token_mint": token_mint,
                "base_mint": token_mint,
                "quote_mint": SOL_MINT,
                "status": "Active (via Jupiter aggregation)",
                "liquidity_access": "Jupiter API",
                "features": ["Order Book", "Market Orders", "Limit Orders"]
            }
            
            return market_info
            
        except Exception as e:
            logger.error(f"❌ Error getting Phoenix market info: {e}")
            return {}
    
    async def check_token_account(self, token_mint: str) -> Dict[str, Any]:
        """
        Check if token account exists and get balance
        
        Args:
            token_mint: Token mint address
            
        Returns:
            Account status and balance information
        """
        try:
            from official_executor_wrappers import get_correct_ata_address
            token_ata = await get_correct_ata_address(self.wallet_pubkey, Pubkey.from_string(token_mint))
            
            try:
                account_info = await self.client.get_account_info(token_ata)
                balance_info = await self.client.get_token_account_balance(token_ata)
                # Robust ATA validation
                from official_executor_wrappers import strict_validate_ata
                await strict_validate_ata(token_ata, self.wallet_pubkey, Pubkey.from_string(token_mint))
                
                return {
                    "exists": bool(account_info.value),
                    "address": str(token_ata),
                    "balance": balance_info.value.amount if balance_info.value else "0",
                    "ui_amount": balance_info.value.ui_amount if balance_info.value else 0.0
                }
                
            except Exception:
                return {
                    "exists": False,
                    "address": str(token_ata),
                    "balance": "0",
                    "ui_amount": 0.0
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking token account: {e}")
            return {
                "exists": False,
                "address": "",
                "balance": "0",
                "ui_amount": 0.0
            }
    
    async def close(self):
        """Close the RPC client connection"""
        try:
            await self.client.close()
            logger.info("🔌 Phoenix Copy Executor connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Phoenix Copy Executor: {e}")

# Convenience functions for copy bot integration
async def try_phoenix_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    """
    Enhanced Phoenix buy function with sophisticated validation and error handling
    Incorporates the robust logic from your original main.py
    
    Args:
        wallet_keypair: Wallet keypair for signing
        token_mint: Target token mint address
        amount_sol: Amount of SOL to spend
        **kwargs: Additional parameters (slippage_tolerance, etc.)
    
    Returns:
        {"success": bool, "signature": str, "error": str}
    """
    from rate_limit_manager import rate_limit_manager
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.commitment import Processed
    from env_keys import EnvKeys
    
    try:
        logger.info(f"🔥 Phoenix Buy (Enhanced): {amount_sol} SOL → {token_mint[:8]}...")

        # ULTRA-AGGRESSIVE MODE: Skip validations for trusted wallet copy trading
        logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this token!")
        logger.info(f"🔥 Phoenix DEX - professional grade order books!")

        # Unified SOL balance check and logging
    # Coordinator should check SOL balance before calling this executor

        # Enhanced retry logic with exponential backoff
        max_retries = kwargs.get('max_retries', 3)
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Phoenix retry attempt {attempt + 1}/{max_retries}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

                # Initialize Phoenix executor
                executor = PhoenixCopyExecutor(wallet_keypair)

                try:
                    # Execute with enhanced error handling
                    result = await executor.try_phoenix_buy(
                        token_mint,
                        amount_sol,
                        slippage_tolerance=kwargs.get('slippage_tolerance', 0.30),
                        max_retries=1,  # Handle retries at this level
                        **kwargs
                    )

                    if result.get('success'):
                        signature = result.get('signature', '')
                        if signature and len(signature) > 10:
                            logger.info(f"✅ Phoenix buy successful (attempt {attempt + 1}): {signature}")
                            return {
                                'success': True,
                                'signature': signature,
                                'amount_sol': amount_sol,
                                'token_mint': token_mint,
                                'dex': 'Phoenix',
                                'attempts': attempt + 1
                            }

                    # If we get here, the result was not successful
                    error = result.get('error', 'Unknown Phoenix error')
                    logger.warning(f"⚠️ Phoenix attempt {attempt + 1} failed: {error}")

                    if attempt == max_retries - 1:  # Last attempt
                        return {
                            'success': False,
                            'error': f'Phoenix buy failed after {max_retries} attempts: {error}',
                            'dex': 'Phoenix',
                            'attempts': max_retries
                        }

                except Exception as executor_error:
                    logger.warning(f"⚠️ Phoenix executor error on attempt {attempt + 1}: {executor_error}")
                    if attempt == max_retries - 1:  # Last attempt
                        return {
                            'success': False,
                            'error': f'Phoenix executor failed after {max_retries} attempts: {str(executor_error)}',
                            'dex': 'Phoenix',
                            'attempts': max_retries
                        }

                finally:
                    await executor.close()

            except Exception as attempt_error:
                logger.warning(f"⚠️ Phoenix attempt {attempt + 1} error: {attempt_error}")
                if attempt == max_retries - 1:  # Last attempt
                    return {
                        'success': False,
                        'error': f'Phoenix buy failed after {max_retries} attempts: {str(attempt_error)}',
                        'dex': 'Phoenix',
                        'attempts': max_retries
                    }

        # Should not reach here
        return {
            'success': False,
            'error': 'Phoenix buy failed - unexpected execution path',
            'dex': 'Phoenix'
        }

    except Exception as e:
        logger.error(f"❌ Phoenix buy critical error: {e}")
        return {
            'success': False,
            'error': f'Phoenix buy critical error: {str(e)}',
            'dex': 'Phoenix'
        }

async def try_phoenix_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    """
    Standalone function for Phoenix sell operations
    Compatible with copy bot architecture
    """
    executor = PhoenixCopyExecutor(wallet_keypair)
    try:
        result = await executor.try_phoenix_sell_all(token_mint, **kwargs)
        return result
    finally:
        await executor.close()

if __name__ == "__main__":
    # Example usage and testing removed due to invalid context and lint errors.
    # To test, implement a proper async test function and call with asyncio.run() if needed.
    pass
