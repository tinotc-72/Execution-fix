"""
🎯 SIMPLE MAIN.PY INTEGRATION - Copy this to your main.py

Add these 3 simple additions to your existing main.py:
"""

# 1. ADD THIS IMPORT (at the top with your other imports)
from modular_integration_connector import create_modular_trading_system, get_integration_status

# 2. ADD THIS METHOD to your CopyTradingBot class
async def start_modular_trading(self):
    """Start the modular trading system - handles socket detection + Jito execution"""
    try:
        logger.info("🔗 Starting modular trading system...")
        
        # Prepare configuration for modular system
        modular_config = {
            'target_wallets': self.target_wallets,
            'wallet_keypair': self.wallet,
            'rpc_client': self.rpc_client,
            'jito_service': self.jito_service,
            'trading_config': {
                'investment_amount_sol': self.config.investment_amount_sol,
                'slippage_tolerance': self.config.slippage_tolerance,
                'slippage_bps': self.config.slippage_bps,
                'enable_dexes': self.config.enable_dexes
            }
        }
        
        # Create and start modular trading system
        self.modular_system = await create_modular_trading_system(modular_config)
        
        if self.modular_system:
            return await self.modular_system.start_trading_system()
        else:
            return False
            
    except Exception as e:
        logger.error(f"❌ Error starting modular trading: {e}")
        return False

# 3. ADD THIS AT THE VERY END of your main.py file
if __name__ == "__main__":
    async def main():
        target_wallets = [
            "9BfvqJ5cuiWCwUGTrKzv8pRr5ZQ7pLFSDJdMakJYm7nQ",  # Replace with your actual target wallets
            # Add more wallets here
        ]
        
        config = CopyTradeConfig(
            target_wallets=target_wallets,
            investment_amount_sol=0.0005,
            use_jito=True
        )
        
        bot = CopyTradingBot(config)
        
        # Start modular trading system
        if await bot.start_modular_trading():
            logger.info("🚀 Bot running with socket detection + Jito execution!")
            try:
                while True:
                    await asyncio.sleep(30)
                    logger.info(f"🔗 System status: {bot.modular_system.get_system_status()}")
            except KeyboardInterrupt:
                logger.info("🛑 Stopping...")
                await bot.modular_system.stop_trading_system()
        else:
            logger.error("❌ Failed to start modular system")

    asyncio.run(main())
