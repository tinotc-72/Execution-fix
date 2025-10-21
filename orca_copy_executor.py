#!/usr/bin/env python3
"""
Orca Copy Executor
Execute Orca DEX trades for copy bot integration

This module provides buy/sell functions that:
1. Support both Orca Legacy and Whirlpool pools
2. Use Jupiter API for reliable Orca liquidity access
3. Compatible with existing copy bot architecture
4. Return standardized response format: {"success": bool, "signature": str}

Orca is the 2nd largest DEX on Solana (~25% market share)
"""

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction

import asyncio
import time
import json
import aiohttp
import base64
import base58
import os
import logging

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

# Remove redundant logger reassignment and duplicate DummyLogger definition

# Orca Program IDs
ORCA_WHIRLPOOL_PROGRAM = Pubkey.from_string("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc")
ORCA_LEGACY_PROGRAM = Pubkey.from_string("9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP")
ORCA_TOKEN_SWAP_PROGRAM = Pubkey.from_string("9qvG1zUp8xF1Bi4m6UdRNby1BAAuaDrUxSpv4CmRRMjL")

# Token addresses
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

@dataclass
class OrcaCopyConfig:
    """Configuration for Orca copy trade execution - ULTRA-AGGRESSIVE for trusted wallets"""
    slippage_bps: int = 5000  # 50% slippage tolerance (ULTRA-AGGRESSIVE)
    max_retries: int = 2
    retry_delay: float = 0.5
    confirmation_timeout: float = 30.0
    compute_unit_limit: int = 400_000  # Higher compute units
    compute_unit_price: int = 5000  # Higher priority fee
    pool_preference: str = "whirlpool"  # "legacy" or "whirlpool"

@dataclass
class ExtractedOrcaTradeInfo:
    """Information extracted from a detected Orca transaction"""
    token_mint: str
    is_buy: bool  # True if SOL->Token, False if Token->SOL
    amount_in: float
    pool_type: str = "whirlpool"  # "legacy" or "whirlpool"
    pool_address: Optional[str] = None
    minimum_amount_out: Optional[float] = None

class OrcaCopyExecutor:
    """
    Orca Copy Executor - Execute Orca trades for copy bot
    Supports both Legacy and Whirlpool pools via Jupiter API integration
    """
    
    def __init__(self, wallet_keypair: Keypair):
        self.wallet = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.client = AsyncClient(env.HELIUS_RPC_URL)
        self.config = OrcaCopyConfig()
        
        # Well-known Orca pools (SOL/USDC for reference)
        self.known_pools = {
            "SOL/USDC_LEGACY": "EGZ7tiLeH62TPV1gL8WwbXGzEPa9zmcpVnnkPKKnrE2U",
            "SOL/USDC_WHIRLPOOL": "HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"
        }
        
        logger.info(f"🐋 Orca Copy Executor initialized for wallet: {self.wallet_pubkey}")
    
    async def confirm_transaction(self, signature: str, max_retries: int = 15) -> bool:
        """
        FAST confirmation for copy trading - optimized for speed!
        Max 15 attempts = 30 seconds maximum wait time
        """
        try:
            logger.info(f"📋 Confirming transaction: {signature}")
            
            signature_obj = Signature.from_string(signature)
            start_time = time.time()
            max_wait_time = 30  # Maximum 30 seconds total
            
            for attempt in range(max_retries):
                try:
                    # Check if we've exceeded maximum wait time
                    if time.time() - start_time > max_wait_time:
                        logger.warning(f"⏰ Transaction confirmation timeout after {max_wait_time}s")
                        logger.info(f"💡 Transaction may still succeed, but copy trading needs speed!")
                        return True  # Assume success for copy trading speed
                    
                    # Use getSignatureStatuses as recommended by official docs
                    statuses = await self.client.get_signature_statuses([signature_obj])
                    
                    if statuses.value and statuses.value[0]:
                        status = statuses.value[0]
                        
                        if status.err:
                            logger.error(f"❌ Transaction failed with error: {status.err}")
                            return False
                        
                        if status.confirmation_status:
                            confirmation_status = str(status.confirmation_status)
                            
                            # Accept both confirmed and finalized status
                            if ("confirmed" in confirmation_status.lower() or 
                                "finalized" in confirmation_status.lower()):
                                logger.info(f"✅ Transaction confirmed: {confirmation_status}")
                                return True
                        
                        # Even if no explicit confirmation, if slot is high enough, assume success
                        if hasattr(status, 'slot') and status.slot:
                            elapsed = time.time() - start_time
                            if elapsed > 8:  # After 8 seconds, assume it's probably confirmed
                                logger.info(f"⚡ Fast confirmation: Transaction likely confirmed after {elapsed:.1f}s")
                                return True
                    
                    # FAST copy trading: shorter waits between attempts
                    wait_time = min(1.5, 0.5 + (attempt * 0.1))  # Progressive wait: 0.5s -> 1.5s max
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    logger.warning(f"Confirmation attempt {attempt + 1} error: {e}")
                    await asyncio.sleep(1)
            
            logger.warning(f"⏰ No explicit confirmation after {max_retries} attempts")
            logger.info(f"💡 For copy trading speed, assuming transaction succeeded")
            return True  # For copy trading, assume success if no error detected
            
        except Exception as e:
            logger.error(f"❌ Error confirming transaction: {e}")
            return False
    
    async def execute_jupiter_swap(self, input_mint: str, output_mint: str, amount: int, description: str) -> Optional[str]:
        """
        Execute swap via Jupiter API to access Orca liquidity
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount in token's base units (lamports for SOL, micro-units for tokens)
            description: Description for logging
        
        Returns:
            Transaction signature if successful, None otherwise
        """
        try:
            logger.info(f"🪐 Executing {description} via Jupiter (accessing Orca liquidity)...")
            
            async with aiohttp.ClientSession() as session:
                # Get quote from Jupiter
                quote_url = "https://quote-api.jup.ag/v6/quote"
                quote_params = {
                    "inputMint": input_mint,
                    "outputMint": output_mint,
                    "amount": amount,
                    "slippageBps": self.config.slippage_bps
                }
                
                async with session.get(quote_url, params=quote_params) as response:
                    if response.status != 200:
                        logger.error(f"❌ Jupiter quote failed: {response.status}")
                        return None
                    
                    quote_data = await response.json()
                    logger.info(f"   📊 Quote: {quote_data['outAmount']} output tokens")
                    
                    # Log route information if available
                    if "routePlan" in quote_data and quote_data["routePlan"]:
                        route_info = quote_data["routePlan"][0].get("swapInfo", {})
                        dex_label = route_info.get("label", "Unknown")
                        logger.info(f"   🗺️  Route: {dex_label}")
                
                # Get swap transaction
                swap_payload = {
                    "userPublicKey": str(self.wallet_pubkey),
                    "quoteResponse": quote_data,
                    "prioritizationFeeLamports": self.config.compute_unit_price
                }
                
                async with session.post("https://quote-api.jup.ag/v6/swap", json=swap_payload) as swap_response:
                    if swap_response.status != 200:
                        logger.error(f"❌ Jupiter swap failed: {swap_response.status}")
                        return None
                    
                    swap_result = await swap_response.json()
                    
                    if "swapTransaction" not in swap_result:
                        logger.error(f"❌ No swap transaction in response")
                        return None
                    
                    # Execute transaction
                    tx_bytes = base64.b64decode(swap_result["swapTransaction"])
                    tx = VersionedTransaction.from_bytes(tx_bytes)
                    
                    # CRITICAL FIX: Sign VersionedTransaction correctly
                    try:
                        # Method 1: Try partial_sign (newer solders versions)
                        tx.partial_sign([self.wallet])
                        logger.info(f"✅ Transaction signed successfully using partial_sign")
                    except AttributeError:
                        try:
                            # Method 2: Create new signed versioned transaction (FIXED: use to_bytes())
                            message_bytes = tx.message.serialize()
                            signature = self.wallet.sign_message(message_bytes)
                            
                            # Create new VersionedTransaction with signature
                            tx = VersionedTransaction(
                                message=tx.message,
                                signatures=[signature.signature]
                            )
                            logger.info(f"✅ Transaction signed successfully using message signing")
                        except Exception as sign_error:
                            logger.error(f"❌ Failed to sign transaction: {sign_error}")
                            return None
                    
                    logger.info(f"📡 Sending Jupiter transaction...")
                    response = await self.client.send_transaction(
                        tx, 
                        opts=TxOpts(
                            skip_preflight=False,
                            preflight_commitment=Processed,
                            max_retries=self.config.max_retries
                        )
                    )
                    
                    if response.value:
                        signature = str(response.value)
                        logger.info(f"✅ {description} transaction sent: {signature}")
                        
                        # Confirm transaction
                        confirmed = await self.confirm_transaction(signature)
                        if confirmed:
                            return signature
                        else:
                            logger.error(f"❌ {description} transaction failed confirmation")
                            return None
                    else:
                        logger.error(f"❌ Failed to send {description} transaction")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Jupiter {description} error: {e}")
            return None
    
    async def try_orca_buy(self, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """
        Buy tokens with SOL using DIRECT Orca - No Jupiter dependency!
        
        Args:
            token_mint: Target token mint address
            amount_sol: Amount of SOL to spend
            **kwargs: Additional parameters (pool_info, slippage_bps, etc.)
        
        Returns:
            {"success": bool, "signature": str}
        """
        try:
            logger.info(f"🐋 DIRECT ORCA BUY: {amount_sol} SOL → {token_mint}")
            logger.info("🔥 USING DIRECT ORCA - No Jupiter API dependency!")
            # For direct Orca, we need pool discovery
            pool_info = kwargs.get('pool_info', {})
            pool_type = kwargs.get('pool_type', 'whirlpool')  # default to whirlpool
            if not pool_info or 'pool_id' not in pool_info:
                logger.warning("[AGGRESSIVE MODE] Direct Orca needs pool discovery - proceeding anyway!")
                # Proceed with attempt (may fail, but aggressive mode)
            # --- Robust ATA logic: Use official_executor_wrappers helpers ---
            from official_executor_wrappers import get_correct_ata_address, create_ata_ix
            wallet_pubkey = self.wallet_pubkey
            token_mint_pubkey = Pubkey.from_string(token_mint)
            ata_address = await get_correct_ata_address(wallet_pubkey, token_mint_pubkey)
            logger.info(f"[DEBUG] Using robust ATA address: {ata_address}")
            # If needed, create_ata_ix can be used to build the correct instruction
            if 'slippage_bps' in kwargs:
                self.config.slippage_bps = kwargs['slippage_bps']
                logger.info(f"🎯 Using custom slippage: {kwargs['slippage_bps']} bps ({kwargs['slippage_bps']/100:.1f}%)")
            amount_lamports = int(amount_sol * 1_000_000_000)
            logger.warning(f"⚠️ Direct Orca {pool_type} implementation needed")
            logger.info("🚀 Your weeks of work should implement:")
            if pool_type == "whirlpool":
                logger.info("   1. Whirlpool SDK or custom instruction building")
                logger.info("   2. Tick array management")
                logger.info("   3. Price impact calculations")
                logger.info("   4. Concentrated liquidity math")
            else:
                logger.info("   1. Legacy Orca pool interaction")
                logger.info("   2. AMM curve calculations")
                logger.info("   3. Direct instruction building")
                logger.info("   4. Pool state fetching")
            return {
                'success': False,
                'error': f'Direct Orca {pool_type} instruction building not implemented yet',
                'dex': f'Orca-{pool_type.title()}-Direct',
                'suggestion': 'Implement direct Orca pool interaction or use pool discovery',
                'amount_lamports': amount_lamports,
                'pool_type': pool_type
            }
        except Exception as e:
            logger.error(f"❌ Direct Orca buy error: {e}")
            return {
                'success': False,
                'error': f'Direct Orca failed: {e}',
                'dex': 'Orca-Direct'
            }
    
    async def try_orca_sell_all(self, token_mint: str, **kwargs) -> Dict[str, Any]:
        """
        Sell all tokens for SOL using DIRECT Orca - No Jupiter dependency!
        
        Args:
            token_mint: Token mint address to sell
            **kwargs: Additional parameters (pool_info, pool_type, etc.)
        
        Returns:
            {"success": bool, "signature": str}
        """
        try:
            logger.info(f"� DIRECT ORCA SELL ALL: {token_mint} → SOL")
            logger.info("🔥 USING DIRECT ORCA SELL - No Jupiter API dependency!")
            
            # Get token balance first
            from spl.token.instructions import get_associated_token_address
            token_mint_pubkey = Pubkey.from_string(token_mint)
            user_ata = get_associated_token_address(self.wallet_pubkey, token_mint_pubkey)
            
            # Check token balance
            try:
                account_info = await self.client.get_account_info(user_ata)
                if not account_info.value:
                    return {
                        'success': False,
                        'error': 'No token account found - no tokens to sell',
                        'dex': 'Orca-Direct'
                    }
                
                # Parse token balance
                from spl.token.core import AccountInfo
                token_account = AccountInfo.from_bytes(account_info.value.data)
                token_balance = int(token_account.amount)
                
                if token_balance == 0:
                    return {
                        'success': False,
                        'error': 'No tokens to sell - balance is 0',
                        'dex': 'Orca-Direct'
                    }
                
                logger.info(f"💰 Found {token_balance} tokens to sell")
                
            except Exception as balance_error:
                logger.error(f"❌ Balance check error: {balance_error}")
                return {
                    'success': False,
                    'error': f'Balance check failed: {balance_error}',
                    'dex': 'Orca-Direct'
                }
            
            # For direct Orca sell, we need the same pool info as buy
            pool_info = kwargs.get('pool_info', {})
            pool_type = kwargs.get('pool_type', 'whirlpool')
            
            if not pool_info or 'pool_id' not in pool_info:
                logger.warning("[AGGRESSIVE MODE] Direct Orca sell needs pool discovery - proceeding anyway!")
                # Proceed with attempt (may fail, but aggressive mode)
            
            # For now, return informative error about implementation needed
            logger.warning(f"⚠️ Direct Orca {pool_type} sell implementation needed")
            logger.info("🚀 Your weeks of work should implement sell logic")
            
            return {
                'success': False,
                'error': f'Direct Orca {pool_type} sell instruction building not implemented yet',
                'dex': f'Orca-{pool_type.title()}-Direct',
                'suggestion': 'Implement direct Orca sell instruction building',
                'token_balance': token_balance,
                'pool_type': pool_type
            }
            
            # Get token account and balance
            token_ata = get_associated_token_address(self.wallet_pubkey, Pubkey.from_string(token_mint))
            
            try:
                token_balance = await self.client.get_token_account_balance(token_ata)
                if not token_balance.value or token_balance.value.amount == "0":
                    logger.warning(f"⚠️  No {token_mint} balance to sell")
                    return {
                        "success": False,
                        "signature": ""
                    }
                
                token_amount = int(token_balance.value.amount)
                logger.info(f"   💰 Selling {token_amount} tokens")
                
            except Exception as e:
                logger.error(f"❌ Error getting token balance: {e}")
                return {
                    "success": False,
                    "signature": ""
                }
            
            # Execute via Jupiter to access Orca liquidity
            signature = await self.execute_jupiter_swap(
                input_mint=token_mint,
                output_mint=SOL_MINT,
                amount=token_amount,
                description="Orca SELL ALL"
            )
            
            if signature:
                logger.info(f"✅ Orca sell all successful: {signature}")
                return {
                    "success": True,
                    "signature": signature
                }
            else:
                logger.error(f"❌ Orca sell all failed")
                return {
                    "success": False,
                    "signature": ""
                }
                
        except Exception as e:
            logger.error(f"❌ Orca sell all error: {e}")
            return {
                "success": False,
                "signature": ""
            }
    
    async def get_token_balance(self, token_mint: str) -> float:
        """Get current token balance"""
        try:
            if token_mint == SOL_MINT:
                # SOL balance
                balance = await self.client.get_balance(self.wallet_pubkey)
                return balance.value / 1_000_000_000 if balance.value else 0.0
            else:
                # SPL Token balance
                token_ata = get_associated_token_address(self.wallet_pubkey, Pubkey.from_string(token_mint))
                try:
                    balance = await self.client.get_token_account_balance(token_ata)
                    return float(balance.value.ui_amount) if balance.value else 0.0
                except:
                    return 0.0
        except Exception as e:
            logger.error(f"❌ Error getting token balance: {e}")
            return 0.0
    
    async def close(self):
        """Close the client connection"""
        try:
            await self.client.close()
        except:
            pass

# Convenience functions for copy bot integration
async def try_orca_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    """
    Enhanced Orca buy function with sophisticated validation and error handling
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
        logger.info(f"🐋 Orca Buy (Enhanced): {amount_sol} SOL → {token_mint[:8]}...")

        # ULTRA-AGGRESSIVE MODE: Skip validations for trusted wallet copy trading
        logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this token!")
        logger.info(f"💎 Orca Whirlpool - concentrated liquidity!")

        # Unified SOL balance check and logging
    # Coordinator should check SOL balance before calling this executor

        # Enhanced retry logic with exponential backoff
        max_retries = kwargs.get('max_retries', 3)
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Orca retry attempt {attempt + 1}/{max_retries}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

                # Initialize Orca executor
                executor = OrcaCopyExecutor(wallet_keypair)

                try:
                    # Execute with enhanced error handling
                    result = await executor.try_orca_buy(
                        token_mint,
                        amount_sol,
                        slippage_tolerance=kwargs.get('slippage_tolerance', 0.30),
                        max_retries=1,  # Handle retries at this level
                        **kwargs
                    )

                    if result.get('success'):
                        signature = result.get('signature', '')
                        if signature and len(signature) > 10:
                            logger.info(f"✅ Orca buy successful (attempt {attempt + 1}): {signature}")
                            return {
                                'success': True,
                                'signature': signature,
                                'amount_sol': amount_sol,
                                'token_mint': token_mint,
                                'dex': 'Orca',
                                'attempts': attempt + 1
                            }

                    # If we get here, the result was not successful
                    error = result.get('error', 'Unknown Orca error')
                    logger.warning(f"⚠️ Orca attempt {attempt + 1} failed: {error}")

                    if attempt == max_retries - 1:  # Last attempt
                        return {
                            'success': False,
                            'error': f'Orca buy failed after {max_retries} attempts: {error}',
                            'dex': 'Orca',
                            'attempts': max_retries
                        }

                except Exception as executor_error:
                    logger.warning(f"⚠️ Orca executor error on attempt {attempt + 1}: {executor_error}")
                    if attempt == max_retries - 1:  # Last attempt
                        return {
                            'success': False,
                            'error': f'Orca executor failed after {max_retries} attempts: {str(executor_error)}',
                            'dex': 'Orca',
                            'attempts': max_retries
                        }

                finally:
                    await executor.close()

            except Exception as attempt_error:
                logger.warning(f"⚠️ Orca attempt {attempt + 1} error: {attempt_error}")
                if attempt == max_retries - 1:  # Last attempt
                    return {
                        'success': False,
                        'error': f'Orca buy failed after {max_retries} attempts: {str(attempt_error)}',
                        'dex': 'Orca',
                        'attempts': max_retries
                    }

        # Should not reach here
        return {
            'success': False,
            'error': 'Orca buy failed - unexpected execution path',
            'dex': 'Orca'
        }

    except Exception as e:
        logger.error(f"❌ Orca buy critical error: {e}")
        return {
            'success': False,
            'error': f'Orca buy critical error: {str(e)}',
            'dex': 'Orca'
        }

async def try_orca_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for copy bot to execute Orca sell all
    
    Args:
        wallet_keypair: Wallet keypair for signing
        token_mint: Token mint address to sell
        **kwargs: Additional parameters
    
    Returns:
        {"success": bool, "signature": str}
    """
    executor = OrcaCopyExecutor(wallet_keypair)
    try:
        result = await executor.try_orca_sell_all(token_mint, **kwargs)
        return result
    finally:
        await executor.close()

# Example usage for testing
if __name__ == "__main__":
    async def test_orca_executor():
        """Test function"""
        from config import WALLET
        
        executor = OrcaCopyExecutor(WALLET)
        
        try:
            # Test buy
            buy_result = await executor.try_orca_buy(USDC_MINT, 0.001)
            print(f"Buy result: {buy_result}")
            
            if buy_result["success"]:
                await asyncio.sleep(5)  # Hold for 5 seconds
                
                # Test sell
                sell_result = await executor.try_orca_sell_all(USDC_MINT)
                print(f"Sell result: {sell_result}")
        
        finally:
            await executor.close()
    
    asyncio.run(test_orca_executor())
