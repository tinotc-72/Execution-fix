#!/usr/bin/env python3
"""
Generalized Pump.Fun Trading Bot
Extends the production trading bot to work with arbitrary pump.fun tokens
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solana.rpc.async_api import AsyncClient
from spl.token.instructions import get_associated_token_address, create_associated_token_account
import struct
import aiohttp

from config import WALLET
from env_keys import EnvKeys

# Import base classes from production bot
from production_pump_trading_bot import (
    TradeAction, TradeResult, TradeConfig, TradeExecutionResult, PumpFunTradingBot
)

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('generalized_pump_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TokenInfo:
    """Information about a pump.fun token"""
    mint: Pubkey
    bonding_curve: Pubkey
    bonding_curve_ata: Pubkey
    is_valid: bool = False
    market_cap: Optional[float] = None
    virtual_sol_reserves: Optional[float] = None
    virtual_token_reserves: Optional[int] = None
    real_sol_reserves: Optional[float] = None
    real_token_reserves: Optional[int] = None

class GeneralizedPumpTradingBot(PumpFunTradingBot):
    """
    Generalized Pump.Fun trading bot that can work with any pump.fun token
    """
    
    def __init__(self, config: TradeConfig = None):
        super().__init__(config)
        self._token_cache: Dict[str, TokenInfo] = {}
        logger.info("🌟 Generalized PumpFun Trading Bot initialized")

    def derive_bonding_curve_address(self, token_mint: Pubkey) -> Tuple[Pubkey, int]:
        """
        Derive the bonding curve address for any pump.fun token
        
        Args:
            token_mint: The token mint address
            
        Returns:
            Tuple of (bonding_curve_address, bump_seed)
        """
        # Standard pump.fun bonding curve derivation pattern
        seeds = [b"bonding-curve", bytes(token_mint)]
        
        try:
            bonding_curve, bump = Pubkey.find_program_address(seeds, self.PUMP_PROGRAM)
            logger.debug(f"Derived bonding curve: {bonding_curve} (bump: {bump})")
            return bonding_curve, bump
        except Exception as e:
            logger.error(f"Failed to derive bonding curve: {e}")
            raise

    def derive_associated_bonding_curve(self, bonding_curve: Pubkey, token_mint: Pubkey) -> Pubkey:
        """
        Derive the associated token account for the bonding curve
        
        Args:
            bonding_curve: The bonding curve address
            token_mint: The token mint address
            
        Returns:
            The associated token account address
        """
        return get_associated_token_address(bonding_curve, token_mint)

    async def get_token_info(self, token_mint: str) -> TokenInfo:
        """
        Get comprehensive token information for a pump.fun token
        
        Args:
            token_mint: Token mint address as string
            
        Returns:
            TokenInfo object with all derived addresses and market data
        """
        # Check cache first
        if token_mint in self._token_cache:
            return self._token_cache[token_mint]
        
        logger.info(f"🔍 Getting token info for: {token_mint}")
        
        try:
            mint_pubkey = Pubkey.from_string(token_mint)
            
            # Derive bonding curve and associated accounts
            bonding_curve, bump = self.derive_bonding_curve_address(mint_pubkey)
            bonding_curve_ata = self.derive_associated_bonding_curve(bonding_curve, mint_pubkey)
            
            # Create token info object
            token_info = TokenInfo(
                mint=mint_pubkey,
                bonding_curve=bonding_curve,
                bonding_curve_ata=bonding_curve_ata
            )
            
            # Validate that the bonding curve exists on-chain
            is_valid = await self.validate_token_accounts(token_info)
            token_info.is_valid = is_valid
            
            if is_valid:
                # Get market data if available
                await self.fetch_market_data(token_info)
            
            # Cache the result
            self._token_cache[token_mint] = token_info
            
            logger.info(f"✅ Token info cached for {token_mint}")
            logger.info(f"   Bonding Curve: {bonding_curve}")
            logger.info(f"   Bonding Curve ATA: {bonding_curve_ata}")
            logger.info(f"   Valid: {is_valid}")
            
            return token_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get token info for {token_mint}: {e}")
            # Return invalid token info
            return TokenInfo(
                mint=Pubkey.from_string("11111111111111111111111111111111"),
                bonding_curve=Pubkey.from_string("11111111111111111111111111111111"),
                bonding_curve_ata=Pubkey.from_string("11111111111111111111111111111111"),
                is_valid=False
            )

    async def validate_token_accounts(self, token_info: TokenInfo) -> bool:
        """
        Validate that the derived token accounts exist on-chain
        
        Args:
            token_info: TokenInfo object to validate
            
        Returns:
            True if all required accounts exist
        """
        try:
            # Check bonding curve account
            bonding_curve_info = await self.client.get_account_info(token_info.bonding_curve)
            if not bonding_curve_info.value:
                logger.warning(f"Bonding curve account does not exist: {token_info.bonding_curve}")
                return False
            
            # Check bonding curve ATA
            bonding_curve_ata_info = await self.client.get_account_info(token_info.bonding_curve_ata)
            if not bonding_curve_ata_info.value:
                logger.warning(f"Bonding curve ATA does not exist: {token_info.bonding_curve_ata}")
                return False
            
            # Check token mint
            mint_info = await self.client.get_account_info(token_info.mint)
            if not mint_info.value:
                logger.warning(f"Token mint does not exist: {token_info.mint}")
                return False
            
            logger.debug(f"✅ All accounts validated for token: {token_info.mint}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating token accounts: {e}")
            return False

    async def fetch_market_data(self, token_info: TokenInfo) -> None:
        """
        Fetch market data for the token (reserves, market cap, etc.)
        
        Args:
            token_info: TokenInfo object to update with market data
        """
        try:
            # Get bonding curve account data to extract reserves
            bonding_curve_info = await self.client.get_account_info(token_info.bonding_curve)
            
            if bonding_curve_info.value and bonding_curve_info.value.data:
                # Parse bonding curve data (pump.fun specific format)
                data = bonding_curve_info.value.data
                if len(data) >= 64:  # Minimum expected size
                    # Parse reserves from bonding curve data
                    # This is pump.fun specific format - may need adjustment
                    virtual_token_reserves = struct.unpack('<Q', data[8:16])[0]
                    virtual_sol_reserves = struct.unpack('<Q', data[16:24])[0] / 1_000_000_000
                    real_token_reserves = struct.unpack('<Q', data[24:32])[0]
                    real_sol_reserves = struct.unpack('<Q', data[32:40])[0] / 1_000_000_000
                    
                    token_info.virtual_token_reserves = virtual_token_reserves
                    token_info.virtual_sol_reserves = virtual_sol_reserves
                    token_info.real_token_reserves = real_token_reserves
                    token_info.real_sol_reserves = real_sol_reserves
                    
                    # Calculate approximate market cap
                    if virtual_sol_reserves > 0 and virtual_token_reserves > 0:
                        sol_price = 150  # Approximate SOL price in USD
                        token_price_sol = virtual_sol_reserves / virtual_token_reserves
                        token_supply = 1_000_000_000  # Standard pump.fun supply
                        token_info.market_cap = token_price_sol * token_supply * sol_price
                    
                    logger.debug(f"Market data updated for {token_info.mint}")
                    
        except Exception as e:
            logger.warning(f"Could not fetch market data: {e}")

    async def buy_token(self, token_mint: str, sol_amount: Optional[float] = None) -> TradeExecutionResult:
        """
        Buy any pump.fun token
        
        Args:
            token_mint: Token mint address as string
            sol_amount: Amount of SOL to spend (defaults to config amount)
            
        Returns:
            TradeExecutionResult with transaction details
        """
        token_info = await self.get_token_info(token_mint)
        
        if not token_info.is_valid:
            logger.error(f"❌ Invalid token or not a pump.fun token: {token_mint}")
            return TradeExecutionResult(
                action=TradeAction.BUY,
                result=TradeResult.FAILED,
                signature=None,
                tokens_amount=0,
                sol_amount=sol_amount or self.config.sol_amount,
                timestamp=datetime.now(),
                error_message="Invalid token or not a pump.fun token"
            )
        
        return await self.execute_buy_trade(
            token_info.mint,
            token_info.bonding_curve,
            token_info.bonding_curve_ata,
            sol_amount
        )

    async def sell_token(self, token_mint: str, token_amount: int, min_sol_out: Optional[int] = None) -> TradeExecutionResult:
        """
        Sell any pump.fun token
        
        Args:
            token_mint: Token mint address as string
            token_amount: Amount of tokens to sell
            min_sol_out: Minimum SOL to accept (optional)
            
        Returns:
            TradeExecutionResult with transaction details
        """
        token_info = await self.get_token_info(token_mint)
        
        if not token_info.is_valid:
            logger.error(f"❌ Invalid token or not a pump.fun token: {token_mint}")
            return TradeExecutionResult(
                action=TradeAction.SELL,
                result=TradeResult.FAILED,
                signature=None,
                tokens_amount=0,
                sol_amount=0.0,
                timestamp=datetime.now(),
                error_message="Invalid token or not a pump.fun token"
            )
        
        return await self.execute_sell_trade(
            token_info.mint,
            token_info.bonding_curve,
            token_info.bonding_curve_ata,
            token_amount,
            min_sol_out
        )

    async def complete_token_cycle(
        self, 
        token_mint: str, 
        hold_duration: float = 10.0,
        buy_amount: Optional[float] = None
    ) -> Dict[str, TradeExecutionResult]:
        """
        Execute a complete buy-hold-sell cycle for any pump.fun token
        
        Args:
            token_mint: Token mint address as string
            hold_duration: How long to hold the token (seconds)
            buy_amount: Amount of SOL to spend on buy
            
        Returns:
            Dictionary with 'buy' and 'sell' TradeExecutionResults
        """
        token_info = await self.get_token_info(token_mint)
        
        if not token_info.is_valid:
            logger.error(f"❌ Invalid token or not a pump.fun token: {token_mint}")
            return {
                'buy': TradeExecutionResult(
                    action=TradeAction.BUY,
                    result=TradeResult.FAILED,
                    signature=None,
                    tokens_amount=0,
                    sol_amount=buy_amount or self.config.sol_amount,
                    timestamp=datetime.now(),
                    error_message="Invalid token or not a pump.fun token"
                )
            }
        
        return await self.execute_complete_trade_cycle(
            token_info.mint,
            token_info.bonding_curve,
            token_info.bonding_curve_ata,
            hold_duration,
            buy_amount
        )

    async def get_token_balance_by_mint(self, token_mint: str) -> int:
        """
        Get token balance for any token mint
        
        Args:
            token_mint: Token mint address as string
            
        Returns:
            Token balance as integer
        """
        try:
            mint_pubkey = Pubkey.from_string(token_mint)
            return await self.get_token_balance(mint_pubkey)
        except Exception as e:
            logger.error(f"Error getting token balance for {token_mint}: {e}")
            return 0

    async def discover_pump_tokens(self, limit: int = 10) -> List[str]:
        """
        Discover recently created pump.fun tokens
        
        Args:
            limit: Maximum number of tokens to return
            
        Returns:
            List of token mint addresses
        """
        try:
            # This would typically use pump.fun API or scan recent transactions
            # For now, return some known active tokens
            logger.info(f"🔍 Discovering recent pump.fun tokens (limit: {limit})")
            
            # Placeholder - in a real implementation, you'd:
            # 1. Query pump.fun API for recent tokens
            # 2. Scan recent pump.fun program transactions
            # 3. Filter by market cap, volume, etc.
            
            return [
                # Add discovered token mints here
            ]
            
        except Exception as e:
            logger.error(f"Error discovering tokens: {e}")
            return []

    async def analyze_token_profitability(self, token_mint: str) -> Dict[str, Any]:
        """
        Analyze token profitability metrics
        
        Args:
            token_mint: Token mint address as string
            
        Returns:
            Dictionary with profitability metrics
        """
        token_info = await self.get_token_info(token_mint)
        
        analysis = {
            'token_mint': token_mint,
            'is_valid': token_info.is_valid,
            'market_cap': token_info.market_cap,
            'virtual_sol_reserves': token_info.virtual_sol_reserves,
            'virtual_token_reserves': token_info.virtual_token_reserves,
            'real_sol_reserves': token_info.real_sol_reserves,
            'real_token_reserves': token_info.real_token_reserves,
            'liquidity_score': 0.0,
            'volatility_score': 0.0,
            'recommendation': 'HOLD'
        }
        
        if token_info.is_valid and token_info.virtual_sol_reserves:
            # Calculate liquidity score
            analysis['liquidity_score'] = min(token_info.virtual_sol_reserves / 100.0, 1.0)
            
            # Simple recommendation logic
            if token_info.market_cap and token_info.market_cap < 50000:  # Under $50k market cap
                if token_info.virtual_sol_reserves > 10:  # Good liquidity
                    analysis['recommendation'] = 'BUY'
                else:
                    analysis['recommendation'] = 'RISKY'
            elif token_info.market_cap and token_info.market_cap > 500000:  # Over $500k market cap
                analysis['recommendation'] = 'SELL'
        
        return analysis

    async def get_portfolio_for_tokens(self, token_mints: List[str]) -> Dict[str, Any]:
        """
        Get portfolio summary for multiple tokens
        
        Args:
            token_mints: List of token mint addresses
            
        Returns:
            Portfolio summary with balances and values
        """
        portfolio = {
            'sol_balance': await self.get_sol_balance(),
            'tokens': {},
            'total_value_sol': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        for token_mint in token_mints:
            try:
                balance = await self.get_token_balance_by_mint(token_mint)
                token_info = await self.get_token_info(token_mint)
                
                token_data = {
                    'balance': balance,
                    'mint': token_mint,
                    'is_valid': token_info.is_valid,
                    'market_cap': token_info.market_cap,
                    'value_sol': 0.0
                }
                
                # Calculate approximate value in SOL
                if balance > 0 and token_info.virtual_sol_reserves and token_info.virtual_token_reserves:
                    token_price_sol = token_info.virtual_sol_reserves / token_info.virtual_token_reserves
                    token_data['value_sol'] = balance * token_price_sol
                    portfolio['total_value_sol'] += token_data['value_sol']
                
                portfolio['tokens'][token_mint] = token_data
                
            except Exception as e:
                logger.error(f"Error getting portfolio data for {token_mint}: {e}")
        
        return portfolio

# Example usage and testing functions
async def demo_generalized_bot():
    """Demonstrate the generalized trading bot"""
    
    print("🌟 GENERALIZED PUMP.FUN TRADING BOT DEMONSTRATION")
    print("="*80)
    
    # Initialize bot
    config = TradeConfig(sol_amount=0.001, max_retries=2)  # Smaller amount for testing
    bot = GeneralizedPumpTradingBot(config)
    
    try:
        # Test with the known working token first
        test_token = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
        
        print(f"\n🔍 Testing with token: {test_token}")
        
        # Get token info
        token_info = await bot.get_token_info(test_token)
        print(f"Token valid: {token_info.is_valid}")
        if token_info.market_cap:
            print(f"Market cap: ${token_info.market_cap:,.2f}")
        
        # Analyze profitability
        analysis = await bot.analyze_token_profitability(test_token)
        print(f"Recommendation: {analysis['recommendation']}")
        print(f"Liquidity score: {analysis['liquidity_score']:.2f}")
        
        # Show initial portfolio
        portfolio = await bot.get_portfolio_for_tokens([test_token])
        print(f"\n📊 Initial Portfolio:")
        print(f"💰 SOL Balance: {portfolio['sol_balance']:.6f}")
        print(f"🪙 Token Balance: {portfolio['tokens'][test_token]['balance']:,}")
        
        # Execute a small trade cycle if recommended
        if analysis['recommendation'] in ['BUY', 'HOLD']:
            print(f"\n🚀 Executing trade cycle...")
            results = await bot.complete_token_cycle(test_token, hold_duration=3.0)
            
            print(f"\n📋 Trading Results:")
            for action, result in results.items():
                print(f"{action.upper()}: {result.result.value}")
                if result.signature:
                    print(f"  TX: https://solscan.io/tx/{result.signature}")
        else:
            print(f"\n⏭️ Skipping trade - recommendation is {analysis['recommendation']}")
        
        # Show final portfolio
        final_portfolio = await bot.get_portfolio_for_tokens([test_token])
        print(f"\n📊 Final Portfolio:")
        print(f"💰 SOL Balance: {final_portfolio['sol_balance']:.6f}")
        print(f"🪙 Token Balance: {final_portfolio['tokens'][test_token]['balance']:,}")
        
        sol_change = final_portfolio['sol_balance'] - portfolio['sol_balance']
        token_change = final_portfolio['tokens'][test_token]['balance'] - portfolio['tokens'][test_token]['balance']
        print(f"\n📈 Net Changes:")
        print(f"💰 SOL: {sol_change:+.6f}")
        print(f"🪙 Tokens: {token_change:+,}")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(demo_generalized_bot())
