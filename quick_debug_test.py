#!/usr/bin/env python3
"""
Quick Debug Script for Transaction Analysis
==========================================

This script will quickly run the bot and test our transaction analysis
with proper debugging based on official Solana documentation.
"""

import asyncio
import traceback
import logging
from main import CopyTradingBot, CopyTradeConfig

# Setup debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug_test")

TARGET_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
    "HKwCgqkgBjkpuv3b8ZcEJ3oNxsR7Sf4WtbDLoyjkT26J"
]

async def test_transaction_analysis():
    """Test our transaction analysis with actual recent transactions"""
    try:
        # Create bot configuration
        config = CopyTradeConfig(
            target_wallets=TARGET_WALLETS,
            investment_amount_sol=0.001,
            use_jito=True
        )
        
        # Initialize bot
        bot = CopyTradingBot(config)
        
        logger.info("🔧 Testing transaction analysis with recent transactions...")
        
        # Get the most recent transaction from first target wallet
        from solders.pubkey import Pubkey
        
        response = await bot.rpc_client.get_signatures_for_address(
            Pubkey.from_string(TARGET_WALLETS[0]),
            limit=3
        )
        
        if response.value:
            for i, tx_info in enumerate(response.value):
                signature = str(tx_info.signature)
                logger.info(f"\n📋 Testing transaction {i+1}: {signature}")
                
                # Analyze this transaction
                await bot.analyze_transaction(signature, TARGET_WALLETS[0])
                
                if i >= 2:  # Just test first 3
                    break
        else:
            logger.warning("No transactions found for target wallet")
            
        await bot.rpc_client.close()
        
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_transaction_analysis())
