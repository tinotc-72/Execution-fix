#!/usr/bin/env python3
"""
Jupiter Utilities for Jito Transaction Building
Provides Jupiter API integration for Jito-first execution in main.py
"""

import asyncio
import base64
import requests
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient

# Configure logging
logger = logging.getLogger(__name__)

# Jupiter API endpoints
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
WSOL_MINT = "So11111111111111111111111111111111111111112"

@dataclass
class JupiterQuoteResult:
    """Result from Jupiter quote API"""
    quote: Optional[Dict] = None
    error: Optional[str] = None
    success: bool = False

@dataclass
class JupiterTransactionResult:
    """Result from Jupiter transaction API"""
    transaction: Optional[VersionedTransaction] = None
    error: Optional[str] = None
    success: bool = False

async def get_jupiter_quote(
    input_mint: str,
    output_mint: str, 
    amount: int,
    slippage_bps: int = 5000,  # 50% default for copy trading
    wallet_pubkey: Optional[str] = None,
    max_retries: int = 3
) -> JupiterQuoteResult:
    """
    Get Jupiter quote for SOL -> Token trade with retry logic
    
    Args:
        input_mint: Input token mint (usually SOL)
        output_mint: Output token mint (target token)
        amount: Amount in lamports/base units
        slippage_bps: Slippage tolerance in basis points
        wallet_pubkey: Wallet public key (optional)
        max_retries: Maximum number of retry attempts
    """
    for attempt in range(max_retries):
        try:
            # Ensure SOL mint is correct format
            if input_mint == "SOL" or input_mint == "11111111111111111111111111111111":
                input_mint = SOL_MINT
            
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": str(slippage_bps),
                "onlyDirectRoutes": "false",
                "maxAccounts": "20",
                "platformFeeBps": "0"
            }
            
            retry_suffix = f" (attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""
            logger.info(f"🔍 Jupiter quote request: {amount} {input_mint[:8]}... -> {output_mint[:8]}...{retry_suffix}")
            
            # Add headers to match working requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(JUPITER_QUOTE_URL, params=params, headers=headers, timeout=15)
            
            # Don't raise for status immediately - check response first
            logger.info(f"🔍 Jupiter response: Status {response.status_code}, Length: {len(response.text)}")
            
            # Parse JSON regardless of status code to see what Jupiter returned
            try:
                quote = response.json()
                logger.info(f"🔍 Jupiter JSON response: {list(quote.keys()) if quote else 'Empty'}")
            except Exception as json_error:
                error_msg = f"Failed to parse Jupiter response as JSON: {json_error}"
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0 * (2 ** attempt))  # Exponential backoff
                    continue
                return JupiterQuoteResult(error=error_msg, success=False)
            
            # Handle different response scenarios
            if response.status_code == 200:
                # Success case - continue to validation
                pass
            elif response.status_code == 400 and quote.get('errorCode') == 'COULD_NOT_FIND_ANY_ROUTE':
                # No route found - this is expected for some tokens, don't retry
                error_msg = f"Jupiter: No route found for {output_mint[:8]}... (this token may not have sufficient liquidity)"
                logger.warning(error_msg)
                return JupiterQuoteResult(error=error_msg, success=False)
            elif response.status_code >= 500 or response.status_code == 429:
                # Server errors or rate limiting - retry
                error_msg = f"Jupiter quote failed: {response.status_code} - {quote.get('error', 'Server error')}"
                logger.warning(f"{error_msg} - will retry")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0 * (2 ** attempt))  # Exponential backoff
                    continue
                return JupiterQuoteResult(error=error_msg, success=False)
            else:
                # Other client errors - don't retry
                error_msg = f"Jupiter quote failed: {response.status_code} - {quote.get('error', 'Unknown error')}"
                logger.error(error_msg)
                return JupiterQuoteResult(error=error_msg, success=False)
            
            # Validate quote response
            if "inAmount" not in quote or "outAmount" not in quote:
                error_msg = f"Invalid Jupiter quote response: {quote}"
                logger.error(error_msg)
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0 * (2 ** attempt))  # Exponential backoff
                    continue
                return JupiterQuoteResult(error=error_msg, success=False)
            
            logger.info(f"✅ Jupiter quote success: {quote['inAmount']} -> {quote['outAmount']}")
            return JupiterQuoteResult(quote=quote, success=True)
            
        except requests.exceptions.Timeout:
            error_msg = f"Jupiter quote request timed out (attempt {attempt + 1})"
            logger.warning(error_msg)
            if attempt < max_retries - 1:
                await asyncio.sleep(1.0 * (2 ** attempt))  # Exponential backoff
                continue
            return JupiterQuoteResult(error="Jupiter quote request timed out after retries", success=False)
        except requests.exceptions.RequestException as e:
            error_msg = f"Jupiter quote request failed: {e} (attempt {attempt + 1})"
            logger.warning(error_msg)
            if attempt < max_retries - 1:
                await asyncio.sleep(1.0 * (2 ** attempt))  # Exponential backoff
                continue
            return JupiterQuoteResult(error=f"Jupiter quote request failed after retries: {e}", success=False)
        except Exception as e:
            error_msg = f"Unexpected error in Jupiter quote: {e} (attempt {attempt + 1})"
            logger.warning(error_msg)
            if attempt < max_retries - 1:
                await asyncio.sleep(1.0 * (2 ** attempt))  # Exponential backoff
                continue
            return JupiterQuoteResult(error=f"Unexpected error in Jupiter quote after retries: {e}", success=False)

async def get_jupiter_transaction(
    quote: Dict,
    wallet_pubkey: str,
    priority_fee_lamports: int = 50000  # Higher priority for copy trading
) -> JupiterTransactionResult:
    """
    Get Jupiter swap transaction from quote
    
    Args:
        quote: Quote response from get_jupiter_quote
        wallet_pubkey: User's wallet public key
        priority_fee_lamports: Priority fee in lamports
    """
    try:
        body = {
            "quoteResponse": quote,
            "userPublicKey": wallet_pubkey,
            "wrapAndUnwrapSol": True,
            "useSharedAccounts": True,
            "asLegacyTransaction": False,
            "dynamicComputeUnitLimit": True,
            "prioritizationFeeLamports": priority_fee_lamports
        }
        
        logger.info(f"🔍 Jupiter transaction request for {wallet_pubkey[:8]}...")
        
        response = requests.post(JUPITER_SWAP_URL, json=body, timeout=15)
        response.raise_for_status()
        
        tx_data = response.json()
        
        # Extract transaction data
        swap_tx_b64 = None
        if "swapTransaction" in tx_data:
            swap_tx_b64 = tx_data["swapTransaction"]
        elif "transaction" in tx_data:
            swap_tx_b64 = tx_data["transaction"]
        
        if not swap_tx_b64:
            error_msg = f"No transaction in Jupiter response: {tx_data.keys()}"
            logger.error(error_msg)
            return JupiterTransactionResult(error=error_msg, success=False)
        
        # Decode transaction
        tx = VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))
        
        logger.info(f"✅ Jupiter transaction built successfully")
        return JupiterTransactionResult(transaction=tx, success=True)
        
    except requests.exceptions.Timeout:
        error_msg = "Jupiter transaction request timed out"
        logger.error(error_msg)
        return JupiterTransactionResult(error=error_msg, success=False)
    except requests.exceptions.RequestException as e:
        error_msg = f"Jupiter transaction request failed: {e}"
        logger.error(error_msg)
        return JupiterTransactionResult(error=error_msg, success=False)
    except Exception as e:
        error_msg = f"Unexpected error in Jupiter transaction: {e}"
        logger.error(error_msg)
        return JupiterTransactionResult(error=error_msg, success=False)

async def get_jupiter_sell_quote(
    input_mint: str,
    output_mint: str = SOL_MINT,
    amount: int = None,
    amount_percentage: float = 100.0,  # Sell 100% by default
    slippage_bps: int = 5000,
    wallet_pubkey: Optional[str] = None
) -> JupiterQuoteResult:
    """
    Get Jupiter quote for Token -> SOL trade (selling)
    
    Args:
        input_mint: Input token mint (token to sell)
        output_mint: Output token mint (usually SOL)
        amount: Specific amount to sell (if None, uses percentage)
        amount_percentage: Percentage of token balance to sell
        slippage_bps: Slippage tolerance in basis points
        wallet_pubkey: Wallet public key (for balance lookup if needed)
    """
    try:
        # For sell trades, we typically sell tokens for SOL
        if output_mint == "SOL" or output_mint == "11111111111111111111111111111111":
            output_mint = SOL_MINT
        
        # If amount not specified, we'd need to get token balance
        if amount is None:
            error_msg = "Amount must be specified for sell quotes (balance lookup not implemented)"
            logger.error(error_msg)
            return JupiterQuoteResult(error=error_msg, success=False)
        
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": str(slippage_bps),
            "onlyDirectRoutes": "false",
            "maxAccounts": "20",
            "platformFeeBps": "0"
        }
        
        logger.info(f"🔍 Jupiter sell quote: {amount} {input_mint[:8]}... -> {output_mint[:8]}...")
        
        response = requests.get(JUPITER_QUOTE_URL, params=params, timeout=15)
        response.raise_for_status()
        
        quote = response.json()
        
        # Validate quote response
        if "inAmount" not in quote or "outAmount" not in quote:
            error_msg = f"Invalid Jupiter sell quote response: {quote}"
            logger.error(error_msg)
            return JupiterQuoteResult(error=error_msg, success=False)
        
        logger.info(f"✅ Jupiter sell quote success: {quote['inAmount']} -> {quote['outAmount']}")
        return JupiterQuoteResult(quote=quote, success=True)
        
    except Exception as e:
        error_msg = f"Error in Jupiter sell quote: {e}"
        logger.error(error_msg)
        return JupiterQuoteResult(error=error_msg, success=False)

async def get_jupiter_sell_transaction(
    quote: Dict,
    wallet_pubkey: str,
    priority_fee_lamports: int = 50000
) -> JupiterTransactionResult:
    """
    Get Jupiter sell transaction from quote
    Same as get_jupiter_transaction but with explicit sell context
    """
    return await get_jupiter_transaction(quote, wallet_pubkey, priority_fee_lamports)

# Utility functions for common copy trading patterns

async def create_jupiter_buy_transaction(
    token_mint: str,
    sol_amount: float,
    wallet_pubkey: str,
    slippage_bps: int = 5000
) -> JupiterTransactionResult:
    """
    Convenience function to create a SOL -> Token buy transaction
    
    Args:
        token_mint: Target token mint address
        sol_amount: Amount of SOL to spend
        wallet_pubkey: User's wallet public key
        slippage_bps: Slippage tolerance in basis points
    """
    try:
        # Convert SOL to lamports
        lamports = int(sol_amount * 1e9)
        
        # Get quote
        quote_result = await get_jupiter_quote(
            input_mint=SOL_MINT,
            output_mint=token_mint,
            amount=lamports,
            slippage_bps=slippage_bps,
            wallet_pubkey=wallet_pubkey
        )
        
        if not quote_result.success:
            return JupiterTransactionResult(error=quote_result.error, success=False)
        
        # Get transaction
        tx_result = await get_jupiter_transaction(
            quote=quote_result.quote,
            wallet_pubkey=wallet_pubkey
        )
        
        return tx_result
        
    except Exception as e:
        error_msg = f"Error creating Jupiter buy transaction: {e}"
        logger.error(error_msg)
        return JupiterTransactionResult(error=error_msg, success=False)

async def create_jupiter_sell_transaction(
    token_mint: str,
    token_amount: int,
    wallet_pubkey: str,
    slippage_bps: int = 5000
) -> JupiterTransactionResult:
    """
    Convenience function to create a Token -> SOL sell transaction
    
    Args:
        token_mint: Token mint address to sell
        token_amount: Amount of tokens to sell (in base units)
        wallet_pubkey: User's wallet public key
        slippage_bps: Slippage tolerance in basis points
    """
    try:
        # Get quote
        quote_result = await get_jupiter_sell_quote(
            input_mint=token_mint,
            output_mint=SOL_MINT,
            amount=token_amount,
            slippage_bps=slippage_bps,
            wallet_pubkey=wallet_pubkey
        )
        
        if not quote_result.success:
            return JupiterTransactionResult(error=quote_result.error, success=False)
        
        # Get transaction
        tx_result = await get_jupiter_sell_transaction(
            quote=quote_result.quote,
            wallet_pubkey=wallet_pubkey
        )
        
        return tx_result
        
    except Exception as e:
        error_msg = f"Error creating Jupiter sell transaction: {e}"
        logger.error(error_msg)
        return JupiterTransactionResult(error=error_msg, success=False)
