#!/usr/bin/env python3
"""
USAGE EXAMPLE - RPC Execution Methods
Quick start guide for using the new RPC execution options
"""

import asyncio
from main import CopyTradingBot, CopyTradeConfig

# YOUR TARGET WALLETS - Replace with actual wallet addresses you want to copy
TARGET_WALLETS = [
    "YOUR_TARGET_WALLET_ADDRESS_1",
    "YOUR_TARGET_WALLET_ADDRESS_2"
]

async def start_bot_with_rpc_options():
    """Start the bot with your preferred execution method"""
    
    # OPTION 1: Force Direct RPC (Hope Latest style) - FASTEST
    print("🚀 OPTION 1: Hope Latest Style (Force Direct RPC)")
    print("=" * 50)
    
    config_rpc_only = CopyTradeConfig(
        target_wallets=TARGET_WALLETS,
        investment_amount_sol=0.001,        # Adjust your investment amount
        use_jito=True,                      # Jito available but bypassed  
        force_rpc_only=True,                # 🚀 FORCE DIRECT RPC (like Hope Latest)
        rpc_priority_fee=1,                 # Minimal fees (1 lamport)
        slippage_tolerance=0.15             # 15% slippage
    )
    
    # OPTION 2: Jito-first with RPC fallback - BALANCED
    print("\n🛡️ OPTION 2: Jito-first with RPC fallback (Recommended)")
    print("=" * 50)
    
    config_hybrid = CopyTradeConfig(
        target_wallets=TARGET_WALLETS,
        investment_amount_sol=0.001,        # Adjust your investment amount
        use_jito=True,                      # Try Jito first for MEV protection
        use_direct_rpc_fallback=True,       # Fall back to RPC if Jito fails
        force_rpc_only=False,               # Don't force RPC-only
        rpc_priority_fee=1,                 # Minimal fees for RPC fallback
        slippage_tolerance=0.15             # 15% slippage
    )
    
    # Choose your preferred config
    print("\n🔧 Choose your execution method:")
    print("1. For MAXIMUM SPEED (like Hope Latest): use config_rpc_only")
    print("2. For MEV PROTECTION + SPEED FALLBACK: use config_hybrid")
    
    # Start with Option 1 (Hope Latest style) for maximum speed
    selected_config = config_rpc_only
    print(f"\n✅ Using: Force Direct RPC (Hope Latest style)")
    
    # Create and start the bot
    bot = CopyTradingBot(selected_config)
    
    print("\n🚀 Bot Configuration:")
    print(f"   Force RPC only: {selected_config.force_rpc_only}")
    print(f"   Use Jito: {selected_config.use_jito}")
    print(f"   RPC fallback: {selected_config.use_direct_rpc_fallback}")
    print(f"   Priority fee: {selected_config.rpc_priority_fee} lamports")
    print(f"   Investment: {selected_config.investment_amount_sol} SOL per trade")
    
    print("\n📡 Starting monitoring...")
    
    try:
        # Start the bot monitoring
        await bot.start_monitoring()
    except KeyboardInterrupt:
        print("\n⏹️ Stopping bot...")
        await bot.stop()
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        await bot.stop()

if __name__ == "__main__":
    print("🎯 Copy Trading Bot - RPC Execution Methods")
    print("=" * 60)
    print("This bot now supports both:")
    print("✅ Jito-first execution with MEV protection")
    print("⚡ Direct RPC execution (Hope Latest style)")
    print("\nMake sure to:")
    print("1. Replace TARGET_WALLETS with real wallet addresses")
    print("2. Adjust investment_amount_sol to your desired amount")
    print("3. Choose force_rpc_only=True for Hope Latest speed")
    print("\n" + "=" * 60)
    
    # Uncomment the line below to start the bot
    # asyncio.run(start_bot_with_rpc_options())
    
    print("\n⚠️ Uncomment the last line and add your target wallets to start!")
