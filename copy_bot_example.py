#!/usr/bin/env python3
"""
Copy Bot Example using Hybrid Trader
====================================

This example shows how to integrate the HybridTrader into a copy bot.
The bot monitors transactions and copies trades using the hybrid approach.

Features:
- CLMM first execution (fastest)
- Jupiter fallback (most reliable)  
- Proper error handling
- Transaction logging
- Balance tracking
"""

import asyncio
import logging
from datetime import datetime
from hybrid_trader import HybridTrader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CopyBot:
    """
    Example copy bot using the HybridTrader
    """
    
    def __init__(self, follow_wallet: str = None):
        """
        Initialize copy bot
        
        Args:
            follow_wallet: Wallet address to follow (for demo purposes)
        """
        self.trader = HybridTrader(enable_clmm=True, slippage_bps=300)
        self.follow_wallet = follow_wallet
        self.is_running = False
        self.trade_history = []
        
        logger.info(f"🤖 Copy Bot initialized")
        logger.info(f"   Following: {follow_wallet or 'Manual trades only'}")
    
    async def log_balances(self, prefix: str = ""):
        """Log current balances"""
        try:
            sol_balance = await self.trader.get_token_balance(self.trader.sol_mint)
            usdc_balance = await self.trader.get_token_balance(self.trader.usdc_mint)
            
            logger.info(f"{prefix}💰 Balances:")
            logger.info(f"   SOL: {sol_balance:.6f}")
            logger.info(f"   USDC: {usdc_balance:.6f}")
            
        except Exception as e:
            logger.error(f"❌ Error logging balances: {e}")
    
    async def execute_copy_trade(self, token_mint: str, action: str, amount: float):
        """
        Execute a copy trade
        
        Args:
            token_mint: Token to trade
            action: "buy" or "sell"
            amount: Amount to trade
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"\n🔄 [{timestamp}] Executing copy trade:")
            logger.info(f"   Token: {token_mint}")
            logger.info(f"   Action: {action.upper()}")
            logger.info(f"   Amount: {amount}")
            
            # Log balances before trade
            await self.log_balances("📊 Before trade - ")
            
            # Execute trade using hybrid approach
            signature = await self.trader.copy_trade(token_mint, action, amount)
            
            if signature:
                logger.info(f"✅ Trade successful!")
                logger.info(f"   Signature: {signature}")
                logger.info(f"   Explorer: https://explorer.solana.com/tx/{signature}?cluster=mainnet-beta")
                
                # Wait for balance to update
                await asyncio.sleep(3)
                
                # Log balances after trade
                await self.log_balances("📊 After trade - ")
                
                # Record trade
                trade_record = {
                    "timestamp": timestamp,
                    "token": token_mint,
                    "action": action,
                    "amount": amount,
                    "signature": signature,
                    "status": "success"
                }
                self.trade_history.append(trade_record)
                
                return signature
            else:
                logger.error(f"❌ Trade failed")
                
                # Record failed trade
                trade_record = {
                    "timestamp": timestamp,
                    "token": token_mint,
                    "action": action,
                    "amount": amount,
                    "signature": None,
                    "status": "failed"
                }
                self.trade_history.append(trade_record)
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Copy trade error: {e}")
            return None
    
    async def demo_trading_cycle(self):
        """
        Demo trading cycle for testing
        """
        try:
            logger.info(f"\n🚀 Starting demo trading cycle...")
            
            # Demo: Buy USDC with SOL
            logger.info(f"\n📈 DEMO BUY: 0.005 SOL worth of USDC")
            buy_signature = await self.execute_copy_trade(
                token_mint=self.trader.usdc_mint,
                action="buy",
                amount=0.005
            )
            
            if buy_signature:
                # Hold for a moment
                logger.info(f"\n⏰ Holding for 5 seconds...")
                await asyncio.sleep(5)
                
                # Demo: Sell USDC back to SOL
                logger.info(f"\n📉 DEMO SELL: All USDC back to SOL")
                sell_signature = await self.execute_copy_trade(
                    token_mint=self.trader.usdc_mint,
                    action="sell",
                    amount=None  # Auto-detect amount
                )
                
                if sell_signature:
                    logger.info(f"\n✅ Demo cycle completed successfully!")
                else:
                    logger.error(f"❌ Demo sell failed")
            else:
                logger.error(f"❌ Demo buy failed")
                
        except Exception as e:
            logger.error(f"❌ Demo cycle error: {e}")
    
    def print_trade_history(self):
        """Print trade history"""
        logger.info(f"\n📋 Trade History ({len(self.trade_history)} trades):")
        logger.info(f"{'='*80}")
        
        for i, trade in enumerate(self.trade_history, 1):
            status_icon = "✅" if trade["status"] == "success" else "❌"
            logger.info(f"{i}. {status_icon} [{trade['timestamp']}] {trade['action'].upper()}")
            logger.info(f"   Token: {trade['token']}")
            logger.info(f"   Amount: {trade['amount']}")
            if trade['signature']:
                logger.info(f"   Signature: {trade['signature']}")
            logger.info(f"   Status: {trade['status']}")
            logger.info("")
    
    async def start_monitoring(self):
        """
        Start monitoring for trades to copy
        (This is a placeholder - in a real bot, you'd monitor blockchain events)
        """
        self.is_running = True
        logger.info(f"🔍 Starting trade monitoring...")
        
        try:
            while self.is_running:
                # In a real copy bot, you would:
                # 1. Monitor blockchain for transactions from the followed wallet
                # 2. Parse transaction data to extract trade information
                # 3. Execute copy trades based on the detected trades
                
                # For demo, just run the demo cycle once
                await self.demo_trading_cycle()
                break
                
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Stop the copy bot"""
        self.is_running = False
        await self.trader.close()
        logger.info(f"🛑 Copy bot stopped")

async def main():
    """
    Main function to run the copy bot example
    """
    # Initialize copy bot
    copy_bot = CopyBot(follow_wallet="A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
    
    try:
        # Log initial balances
        await copy_bot.log_balances("📊 Initial ")
        
        # Start monitoring (runs demo cycle)
        await copy_bot.start_monitoring()
        
        # Print trade history
        copy_bot.print_trade_history()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Main error: {e}")
    finally:
        # Clean shutdown
        await copy_bot.stop()

if __name__ == "__main__":
    # Run the copy bot
    asyncio.run(main())
