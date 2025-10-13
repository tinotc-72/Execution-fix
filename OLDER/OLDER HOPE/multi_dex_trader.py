#!/usr/bin/env python3
"""
MULTI-DEX TRADING EXECUTOR
Executes trades across all major Solana DEXes including Jupiter, Raydium, Orca, etc.
"""

import asyncio
import json
import aiohttp
import base64
from typing import Dict, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.hash import Hash
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from config import WALLET, HELIUS_RPC_URL
import logging

logger = logging.getLogger(__name__)

@dataclass
class TradeRequest:
    """Trade request data structure"""
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 100  # 1% slippage
    dex_preference: str = "AUTO"  # AUTO, JUPITER, RAYDIUM, ORCA, etc.

@dataclass
class TradeResult:
    """Trade execution result"""
    success: bool
    signature: Optional[str] = None
    input_amount: int = 0
    output_amount: int = 0
    dex_used: str = ""
    error: Optional[str] = None
    tx_fee: int = 0

class MultiDexTrader:
    """
    Multi-DEX trading executor that can execute trades on:
    - Jupiter (aggregator - best for complex swaps)
    - Raydium (AMM)
    - Orca (AMM) 
    - Pump.fun (bonding curve)
    - Phoenix (CLOB)
    - OpenBook (CLOB)
    """
    
    def __init__(self, wallet: Keypair, rpc_url: str = None):
        self.wallet = wallet
        self.rpc_url = rpc_url or HELIUS_RPC_URL
        self.jupiter_api_url = "https://quote-api.jup.ag/v6"
        
        # DEX Program IDs
        self.dex_programs = {
            "JUPITER_V6": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
            "RAYDIUM": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
            "ORCA": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
            "PUMP": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
            "PHOENIX": "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY",
            "OPENBOOK": "srmqPvymJeFKQ4zGQed1GFELXCWuBvf9Ss623VQ5DA",
        }
        
        # Common token addresses
        self.tokens = {
            "SOL": "So11111111111111111111111111111111111111112",  # Wrapped SOL
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        }
        
        logger.info(f"🔄 Multi-DEX Trader initialized for wallet: {wallet.pubkey()}")
    
    async def copy_trade(self, target_trade: Dict) -> TradeResult:
        """
        Copy a trade from a target wallet across any DEX
        """
        try:
            dex = target_trade.get('dex', 'UNKNOWN')
            action = target_trade.get('action', 'UNKNOWN')
            token_mint = target_trade.get('token_mint')
            sol_amount = target_trade.get('sol_amount', 0.01)
            
            logger.info(f"🎯 Copying {dex} {action} for token {token_mint[:8]}...")
            
            if action == "BUY":
                return await self.buy_token(token_mint, sol_amount, dex)
            elif action == "SELL":
                return await self.sell_token(token_mint, percentage=100, dex=dex)
            else:
                return TradeResult(success=False, error=f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"❌ Copy trade failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def buy_token(self, token_mint: str, sol_amount: float, preferred_dex: str = "AUTO") -> TradeResult:
        """
        Buy tokens using the best available DEX
        """
        try:
            logger.info(f"💰 Buying {sol_amount} SOL worth of {token_mint[:8]}... via {preferred_dex}")
            
            # Convert SOL to lamports
            sol_lamports = int(sol_amount * 1_000_000_000)
            
            # Create trade request
            trade_request = TradeRequest(
                input_mint=self.tokens["SOL"],
                output_mint=token_mint,
                amount=sol_lamports,
                slippage_bps=100,  # 1% slippage
                dex_preference=preferred_dex
            )
            
            # Try different execution strategies based on DEX
            if preferred_dex in ["PUMP", "PUMP_NEW", "PUMP_ROUTER", "PUMP_TRADING"]:
                return await self._execute_pump_buy(token_mint, sol_amount)
            elif preferred_dex in ["JUPITER", "JUPITER_V6", "AUTO"]:
                return await self._execute_jupiter_swap(trade_request)
            elif preferred_dex == "RAYDIUM":
                return await self._execute_raydium_swap(trade_request)
            elif preferred_dex == "ORCA":
                return await self._execute_orca_swap(trade_request)
            else:
                # Default to Jupiter for unknown DEXes
                logger.info(f"🔄 Unknown DEX {preferred_dex}, using Jupiter as fallback")
                return await self._execute_jupiter_swap(trade_request)
                
        except Exception as e:
            logger.error(f"❌ Buy token failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def sell_token(self, token_mint: str, percentage: int = 100, dex: str = "AUTO") -> TradeResult:
        """
        Sell tokens using the best available DEX
        """
        try:
            logger.info(f"💸 Selling {percentage}% of {token_mint[:8]}... via {dex}")
            
            # Get current token balance
            token_balance = await self._get_token_balance(token_mint)
            if token_balance == 0:
                return TradeResult(success=False, error="No tokens to sell")
            
            # Calculate amount to sell
            sell_amount = int(token_balance * percentage / 100)
            
            # Create trade request
            trade_request = TradeRequest(
                input_mint=token_mint,
                output_mint=self.tokens["SOL"],
                amount=sell_amount,
                slippage_bps=100,
                dex_preference=dex
            )
            
            # Execute sell based on DEX
            if dex in ["PUMP", "PUMP_NEW", "PUMP_ROUTER", "PUMP_TRADING"]:
                return await self._execute_pump_sell(token_mint, sell_amount)
            elif dex in ["JUPITER", "JUPITER_V6", "AUTO"]:
                return await self._execute_jupiter_swap(trade_request)
            elif dex == "RAYDIUM":
                return await self._execute_raydium_swap(trade_request)
            elif dex == "ORCA":
                return await self._execute_orca_swap(trade_request)
            else:
                # Default to Jupiter
                return await self._execute_jupiter_swap(trade_request)
                
        except Exception as e:
            logger.error(f"❌ Sell token failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def _execute_jupiter_swap(self, trade_request: TradeRequest) -> TradeResult:
        """
        Execute swap via Jupiter aggregator (supports all tokens)
        """
        try:
            logger.info("🪐 Executing Jupiter swap...")
            
            # Get quote from Jupiter
            quote_url = f"{self.jupiter_api_url}/quote"
            quote_params = {
                "inputMint": trade_request.input_mint,
                "outputMint": trade_request.output_mint, 
                "amount": trade_request.amount,
                "slippageBps": trade_request.slippage_bps,
                "onlyDirectRoutes": False,
                "asLegacyTransaction": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(quote_url, params=quote_params) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return TradeResult(success=False, error=f"Jupiter quote failed: {error_text}")
                    
                    quote_data = await resp.json()
                    logger.info(f"📊 Jupiter quote: {quote_data.get('inAmount', 0)} → {quote_data.get('outAmount', 0)}")
                
                # Get swap transaction
                swap_url = f"{self.jupiter_api_url}/swap"
                swap_data = {
                    "quoteResponse": quote_data,
                    "userPublicKey": str(self.wallet.pubkey()),
                    "wrapAndUnwrapSol": True,
                    "computeUnitPriceMicroLamports": 100000,  # Priority fee
                }
                
                async with session.post(swap_url, json=swap_data) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return TradeResult(success=False, error=f"Jupiter swap failed: {error_text}")
                    
                    swap_response = await resp.json()
                    swap_tx_base64 = swap_response["swapTransaction"]
                    
                    # Decode and sign transaction
                    swap_tx_bytes = base64.b64decode(swap_tx_base64)
                    transaction = Transaction.from_bytes(swap_tx_bytes)
                    
                    # Sign the transaction
                    transaction.sign([self.wallet])
                    
                    # Send transaction
                    signature = await self._send_transaction(transaction)
                    
                    if signature:
                        return TradeResult(
                            success=True,
                            signature=signature,
                            input_amount=int(quote_data.get('inAmount', 0)),
                            output_amount=int(quote_data.get('outAmount', 0)),
                            dex_used="JUPITER",
                        )
                    else:
                        return TradeResult(success=False, error="Failed to send Jupiter transaction")
                        
        except Exception as e:
            logger.error(f"❌ Jupiter swap failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def _execute_pump_buy(self, token_mint: str, sol_amount: float) -> TradeResult:
        """
        Execute pump.fun buy using existing pump trading logic
        """
        try:
            # Import and use existing pump trading bot
            from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig
            
            trade_config = TradeConfig(sol_amount=sol_amount, max_retries=3)
            pump_bot = GeneralizedPumpTradingBot(trade_config)
            
            result = await pump_bot.buy_token(token_mint, sol_amount=sol_amount)
            
            if result and result.get('success'):
                return TradeResult(
                    success=True,
                    signature=result.get('signature'),
                    input_amount=int(sol_amount * 1_000_000_000),
                    output_amount=result.get('tokens_received', 0),
                    dex_used="PUMP",
                )
            else:
                return TradeResult(success=False, error=result.get('error', 'Pump buy failed'))
                
        except Exception as e:
            logger.error(f"❌ Pump buy failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def _execute_pump_sell(self, token_mint: str, amount: int) -> TradeResult:
        """
        Execute pump.fun sell using existing pump trading logic
        """
        try:
            from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig
            
            trade_config = TradeConfig(sol_amount=0.01, max_retries=3)
            pump_bot = GeneralizedPumpTradingBot(trade_config)
            
            result = await pump_bot.sell_token(token_mint, percentage=100)
            
            if result and result.get('success'):
                return TradeResult(
                    success=True,
                    signature=result.get('signature'),
                    input_amount=amount,
                    output_amount=result.get('sol_received', 0),
                    dex_used="PUMP",
                )
            else:
                return TradeResult(success=False, error=result.get('error', 'Pump sell failed'))
                
        except Exception as e:
            logger.error(f"❌ Pump sell failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def _execute_raydium_swap(self, trade_request: TradeRequest) -> TradeResult:
        """
        Execute Raydium AMM swap (basic implementation)
        """
        try:
            logger.info("🌊 Raydium swap detected but not implemented yet")
            logger.info("💡 Falling back to Jupiter for this trade")
            
            # Fallback to Jupiter for now
            return await self._execute_jupiter_swap(trade_request)
            
        except Exception as e:
            logger.error(f"❌ Raydium swap failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def _execute_orca_swap(self, trade_request: TradeRequest) -> TradeResult:
        """
        Execute Orca AMM swap (basic implementation)
        """
        try:
            logger.info("🐋 Orca swap detected but not implemented yet")
            logger.info("💡 Falling back to Jupiter for this trade")
            
            # Fallback to Jupiter for now
            return await self._execute_jupiter_swap(trade_request)
            
        except Exception as e:
            logger.error(f"❌ Orca swap failed: {e}")
            return TradeResult(success=False, error=str(e))
    
    async def _get_token_balance(self, token_mint: str) -> int:
        """Get token balance for the wallet"""
        try:
            # Use RPC to get token balance
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    str(self.wallet.pubkey()),
                    {"mint": token_mint},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        accounts = data.get("result", {}).get("value", [])
                        
                        if accounts:
                            token_amount = accounts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]
                            return int(token_amount["amount"])
                        return 0
                    else:
                        logger.error(f"Failed to get token balance: {resp.status}")
                        return 0
                        
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0
    
    async def _send_transaction(self, transaction: Transaction) -> Optional[str]:
        """Send transaction to the network"""
        try:
            # Serialize transaction
            tx_bytes = bytes(transaction)
            tx_base64 = base64.b64encode(tx_bytes).decode('utf-8')
            
            # Send via RPC
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    tx_base64,
                    {
                        "encoding": "base64",
                        "skipPreflight": False,
                        "preflightCommitment": "confirmed",
                        "maxRetries": 3
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "result" in data:
                            signature = data["result"]
                            logger.info(f"✅ Transaction sent: {signature}")
                            return signature
                        else:
                            error = data.get("error", {})
                            logger.error(f"❌ Transaction failed: {error}")
                            return None
                    else:
                        logger.error(f"❌ RPC error: {resp.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Send transaction failed: {e}")
            return None

# Create global instance
multi_dex_trader = MultiDexTrader(WALLET)

__all__ = ['MultiDexTrader', 'TradeRequest', 'TradeResult', 'multi_dex_trader']
