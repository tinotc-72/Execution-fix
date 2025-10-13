#!/usr/bin/env python3
"""
Test script for the Solana Trading Bot
Tests basic functionality and a complete trade cycle with minimal amounts
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from dataclasses import dataclass

from config import WALLET
from env_keys import EnvKeys
from production_pump_trading_bot import SolanaTradingBot, TradeConfig, ProgramConfig

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration with minimal amounts
@dataclass
class TestConfig:
    # Test token (should be a known working token)
    TEST_TOKEN_MINT = "766cu48DWcanNfre5p4Hs9e13UaBjSQxSFy8mzJcpump"
    
    # Program configuration
    PUMP_PROGRAM = Pubkey.from_string("PUMPmnZGqEQE4NqvY6bNKpTLHLAKm8vZ7pxcvwdgv8y")
    
    # Test trade parameters
    TEST_SOL_AMOUNT = 0.001  # Minimal SOL amount for testing
    HOLD_DURATION = 5.0  # 5 second hold
    
    # Buy/Sell discriminators (from production bot)
    BUY_DISCRIMINATOR = bytes([102, 83, 150, 5, 207, 106, 87, 216])  # real discriminator
    SELL_DISCRIMINATOR = bytes([31, 125, 193, 130, 176, 164, 37, 147])  # real discriminator

async def test_trading_bot():
    """Run a complete test of the trading bot"""
    
    logger.info("🧪 Starting trading bot test")
    
    # Create minimal trade config
    trade_config = TradeConfig(
        sol_amount=TestConfig.TEST_SOL_AMOUNT,
        slippage_tolerance=0.10,
        max_retries=1,
        retry_delay=0.0,
        confirmation_timeout=10.0,
        max_balance_checks=1,
        initial_wait_time=0.0
    )
    
    # Create program config
    program_config = ProgramConfig(
        program_id=TestConfig.PUMP_PROGRAM,
        buy_discriminator=TestConfig.BUY_DISCRIMINATOR,
        sell_discriminator=TestConfig.SELL_DISCRIMINATOR,
        required_accounts={}  # Will be populated by the bot
    )
    
    # Initialize bot
    bot = SolanaTradingBot(program_config, trade_config)
    
    try:
        # Test 1: Check connectivity
        logger.info("Test 1: Checking connectivity and balances")
        sol_balance = await bot.get_sol_balance()
        logger.info(f"✓ Connected successfully. SOL Balance: {sol_balance}")
        
        if sol_balance < TestConfig.TEST_SOL_AMOUNT:
            logger.error(f"❌ Insufficient SOL balance for testing. Need at least {TestConfig.TEST_SOL_AMOUNT} SOL")
            return
        
        # Test 2: Check token account
        logger.info("Test 2: Checking token account")
        token_mint = Pubkey.from_string(TestConfig.TEST_TOKEN_MINT)
        token_balance = await bot.get_token_balance(token_mint)
        logger.info(f"✓ Token balance check successful. Current balance: {token_balance}")
        
        # Test 3: Execute minimal trade cycle
        logger.info("Test 3: Executing minimal trade cycle")
        logger.info(f"Starting trade cycle with {TestConfig.TEST_SOL_AMOUNT} SOL")
        
        results = await bot.execute_complete_trade_cycle(
            token_mint=token_mint,
            hold_duration=TestConfig.HOLD_DURATION,
            buy_amount=TestConfig.TEST_SOL_AMOUNT
        )
        
        # Print results
        if 'buy' in results:
            buy_result = results['buy']
            logger.info(f"Buy Result: {buy_result.result.value}")
            if buy_result.signature:
                logger.info(f"Buy TX: {buy_result.signature}")
        
        if 'sell' in results:
            sell_result = results['sell']
            logger.info(f"Sell Result: {sell_result.result.value}")
            if sell_result.signature:
                logger.info(f"Sell TX: {sell_result.signature}")
        
        # Final balance check
        final_sol = await bot.get_sol_balance()
        final_tokens = await bot.get_token_balance(token_mint)
        
        logger.info("Final Balances:")
        logger.info(f"SOL: {final_sol}")
        logger.info(f"Tokens: {final_tokens}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_trading_bot())
