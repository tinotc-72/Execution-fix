#!/usr/bin/env python3
"""
Example usage of the generic Solana trading bot
"""
import asyncio
import logging
from solders.pubkey import Pubkey

from solana_trading_bot import SolanaTradingBot, ProgramConfig, TradeConfig, TradeResult

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_example_trade():
    """Run an example trade cycle using a specific program"""
    
    # Program-specific configuration
    program_config = ProgramConfig(
        program_id=Pubkey.from_string("YOUR_PROGRAM_ID"),  # Replace with actual program ID
        buy_discriminator=bytes.fromhex("YOUR_BUY_DISCRIMINATOR"),  # Replace with actual buy instruction discriminator
        sell_discriminator=bytes.fromhex("YOUR_SELL_DISCRIMINATOR"),  # Replace with actual sell instruction discriminator
        required_accounts={
            # Add program-specific accounts that are required for trades
            "pool": Pubkey.from_string("POOL_ADDRESS"),  # Example
            "vault": Pubkey.from_string("VAULT_ADDRESS"),  # Example
        }
    )
    
    # Trading parameters
    trade_config = TradeConfig(
        sol_amount=0.005,  # Amount of SOL to trade
        slippage_tolerance=0.10,  # 10% slippage tolerance
        max_retries=1,  # Number of retry attempts
        confirmation_timeout=10.0  # Transaction confirmation timeout
    )
    
    # Initialize trading bot
    bot = SolanaTradingBot(program_config, trade_config)
    
    try:
        # Replace with your token mint
        token_mint = Pubkey.from_string("YOUR_TOKEN_MINT")
        
        # Execute buy trade
        logger.info("Executing buy trade...")
        buy_result = await bot.execute_buy_trade(token_mint)
        
        if buy_result.result == TradeResult.SUCCESS:
            # Hold for 5 seconds
            logger.info("Buy successful! Holding for 5 seconds...")
            await asyncio.sleep(5)
            
            # Execute sell trade
            logger.info("Executing sell trade...")
            sell_result = await bot.execute_sell_trade(
                token_mint=token_mint,
                token_amount=buy_result.tokens_amount
            )
            
            if sell_result.result == TradeResult.SUCCESS:
                net_sol = sell_result.sol_amount - buy_result.sol_amount
                logger.info(f"Trade cycle complete! Net SOL: {net_sol:+.6f}")
            else:
                logger.error(f"Sell failed: {sell_result.error_message}")
        else:
            logger.error(f"Buy failed: {buy_result.error_message}")
            
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(run_example_trade())
