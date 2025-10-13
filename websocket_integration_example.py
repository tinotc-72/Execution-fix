#!/usr/bin/env python3
"""
Example integration of WebSocket wallet monitoring with main.py copy trading bot
This shows how to use the wallet_tx_parser WebSocket functionality
"""

import asyncio
from typing import Dict, Any
from wallet_tx_parser import start_realtime_monitoring, example_trade_handler

# Example target wallets (replace with your actual target wallets)
TARGET_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Wallet 1
    "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Wallet 2
]

class CopyTradingIntegration:
    """Integration example showing how to connect WebSocket monitoring to copy trading"""
    
    def __init__(self):
        self.copy_trades_executed = 0
        
    async def handle_detected_trade(self, trade_info: Dict[str, Any]):
        """
        Handle detected trades from WebSocket monitoring
        This is where you would integrate with your main.py copy trading logic
        """
        print(f"\n🚨 TRADE DETECTED VIA WEBSOCKET!")
        print(f"   👤 Wallet: {trade_info['wallet_address'][:8]}...{trade_info['wallet_address'][-8:]}")
        print(f"   🎬 Action: {trade_info['action'].upper()}")
        print(f"   💎 Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
        print(f"   🏪 DEX: {trade_info.get('dex', 'Unknown')}")
        print(f"   📝 Signature: {trade_info['signature'][:12]}...")
        print(f"   ⏰ Time: {trade_info['timestamp']}")
        
        # Integration with your copy trading bot
        if trade_info['action'] == 'buy':
            await self._execute_copy_buy(trade_info)
        elif trade_info['action'] == 'sell':
            await self._execute_copy_sell(trade_info)
            
    async def _execute_copy_buy(self, trade_info: Dict[str, Any]):
        """Execute copy buy - integrate with your main.py logic"""
        token_mint = trade_info.get('token_mint')
        wallet_address = trade_info['wallet_address']
        dex = trade_info.get('dex', 'Unknown')
        
        print(f"🎯 COPY BUY SIGNAL!")
        print(f"   🎯 Token: {token_mint}")
        print(f"   🏪 DEX: {dex}")
        
        # Here you would call your existing copy trading functions from main.py
        # Example (you would replace this with your actual copy trading logic):
        
        try:
            # This is where you would integrate with your main.py CopyTradingBot
            # Example integration:
            # await self.copy_trading_bot._execute_copy_buy(token_mint, wallet_address, dex)
            
            print(f"✅ COPY BUY EXECUTED for {token_mint[:8]}...")
            self.copy_trades_executed += 1
            
        except Exception as e:
            print(f"❌ COPY BUY FAILED: {e}")
            
    async def _execute_copy_sell(self, trade_info: Dict[str, Any]):
        """Execute copy sell - integrate with your main.py logic"""
        token_mint = trade_info.get('token_mint')
        wallet_address = trade_info['wallet_address']
        dex = trade_info.get('dex', 'Unknown')
        
        print(f"🎯 COPY SELL SIGNAL!")
        print(f"   🎯 Token: {token_mint}")
        print(f"   🏪 DEX: {dex}")
        
        try:
            # This is where you would integrate with your main.py CopyTradingBot
            # Example integration:
            # await self.copy_trading_bot._execute_copy_sell(token_mint, wallet_address, dex)
            
            print(f"✅ COPY SELL EXECUTED for {token_mint[:8]}...")
            self.copy_trades_executed += 1
            
        except Exception as e:
            print(f"❌ COPY SELL FAILED: {e}")
            
    def get_stats(self):
        """Get trading statistics"""
        return {
            "copy_trades_executed": self.copy_trades_executed
        }

async def main():
    """Main function to run the WebSocket monitoring with copy trading integration"""
    print("🚀 Starting WebSocket Copy Trading Integration")
    print("=" * 60)
    print(f"📡 Monitoring {len(TARGET_WALLETS)} target wallets:")
    for i, wallet in enumerate(TARGET_WALLETS, 1):
        print(f"   {i}. {wallet[:8]}...{wallet[-8:]}")
    print()
    
    # Create the integration handler
    integration = CopyTradingIntegration()
    
    try:
        # Start WebSocket monitoring with our trade handler
        await start_realtime_monitoring(TARGET_WALLETS, integration.handle_detected_trade)
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
        
    except Exception as e:
        print(f"❌ Error in monitoring: {e}")
        
    finally:
        # Show final stats
        stats = integration.get_stats()
        print(f"\n📊 Final Statistics:")
        print(f"   🎯 Copy trades executed: {stats['copy_trades_executed']}")

if __name__ == "__main__":
    print("🔍 WebSocket Copy Trading Integration Example")
    print("This demonstrates how to integrate WebSocket monitoring with your copy trading bot")
    print("Press Ctrl+C to stop\n")
    
    asyncio.run(main())
