#!/usr/bin/env python3
"""
Test script for executing a buy and sell trade on a Pump.fun meme token
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from production_pump_trading_bot import PumpFunTradingBot, TradeConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_meme_trade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    # Configure the trading bot
    config = TradeConfig(
        sol_amount=0.1,  # Amount of SOL to use for buying
        slippage_tolerance=0.05  # 5% slippage tolerance
    )
    
    bot = PumpFunTradingBot(config)
    await bot.initialize()
    
    try:
        # Replace these with the token you want to test
        token_mint = Pubkey.from_string("YOUR_TOKEN_MINT")
        bonding_curve = Pubkey.from_string("BONDING_CURVE_ADDRESS")
        bonding_curve_ata = Pubkey.from_string("BONDING_CURVE_ATA")
        
        # Execute buy trade
        logger.info("Executing buy trade...")
        buy_result = await bot.execute_buy_trade(
            token_mint=token_mint,
            bonding_curve=bonding_curve,
            bonding_curve_ata=bonding_curve_ata
        )
        
        if buy_result.result == "success":
            logger.info(f"Buy successful! Tokens received: {buy_result.tokens_amount:,}")
            
            # Wait a bit before selling (you can adjust this)
            await asyncio.sleep(5)
            
            # Execute sell trade for all tokens received
            logger.info("Executing sell trade...")
            sell_result = await bot.execute_sell_trade(
                token_mint=token_mint,
                bonding_curve=bonding_curve,
                bonding_curve_ata=bonding_curve_ata,
                token_amount=buy_result.tokens_amount
            )
            
            if sell_result.result == "success":
                logger.info(f"Sell successful! SOL received: {sell_result.sol_amount:.4f}")
            else:
                logger.error(f"Sell failed: {sell_result.error_message}")
        else:
            logger.error(f"Buy failed: {buy_result.error_message}")
            
    except Exception as e:
        logger.error(f"Error during trading: {str(e)}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
