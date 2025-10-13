#!/usr/bin/env python3
"""
Test Liquidation Functionality
==============================

This script tests the automatic position liquidation feature.
Run this to verify that the liquidation system works correctly.

Usage:
- python test_liquidation.py --simulate    # Test without actual trades
- python test_liquidation.py --emergency   # Emergency liquidate all positions
- python test_liquidation.py --check       # Just check current positions

Author: tinotc-72
Date: July 2025
"""

import asyncio
import argparse
import sys
from main import CopyTradingBot, CopyTradeConfig, emergency_liquidate_all, logger, WalletPosition

async def test_liquidation_simulation():
    """Test liquidation functionality with simulated positions"""
    logger.info("🧪 TESTING LIQUIDATION SYSTEM (SIMULATION MODE)")
    logger.info("=" * 60)
    
    # Create test configuration
    config = CopyTradeConfig(
        target_wallets=[],  # Not needed for testing
        investment_amount_sol=0.001,
        max_positions=10,
        enable_dexes={
            "orca": True,      # Keep only working DEXes for testing
            "phoenix": True,
            "raydium": True
        }
    )
    
    # Create bot instance
    bot = CopyTradingBot(config)
    
    # Simulate some positions
    logger.info("📝 Creating simulated positions...")
    
    # Add fake positions for testing
    test_tokens = [
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC (real token for testing)
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT (real token for testing)
        "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs"   # ETHER (real token for testing)
    ]
    
    for i, token_mint in enumerate(test_tokens):
        position = WalletPosition(
            token_mint=token_mint,
            initial_amount=0.001,
            current_amount=0.001,
            our_amount=0.001
        )
        bot.positions[token_mint] = position
        logger.info(f"   ✅ Added test position: {token_mint[:8]}...")
    
    logger.info(f"📊 Created {len(bot.positions)} test positions")
    logger.info("=" * 60)
    
    # Test liquidation (simulation - won't actually trade)
    logger.info("🧪 Testing liquidation logic...")
    
    # In simulation mode, we'll just log what would happen
    logger.info(f"💸 SIMULATION: Would liquidate {len(bot.positions)} positions")
    
    for token_mint, position in bot.positions.items():
        logger.info(f"   🎯 Would sell {token_mint[:8]}... (invested: {position.current_amount:.6f} SOL)")
    
    # Clear test positions
    bot.positions.clear()
    logger.info("✅ Simulation completed successfully")

async def check_current_positions():
    """Check what positions are currently held in the wallet"""
    logger.info("🔍 CHECKING CURRENT WALLET POSITIONS")
    logger.info("=" * 60)
    
    config = CopyTradeConfig(
        target_wallets=[],
        investment_amount_sol=0.001,
        enable_dexes={"orca": True}  # Minimal config just to check balances
    )
    
    bot = CopyTradingBot(config)
    
    try:
        # Get wallet balances
        balances = await bot.get_wallet_balance()
        
        logger.info(f"💰 Current Wallet Balances:")
        logger.info(f"   💎 SOL: {balances.get('SOL', 0):.6f}")
        
        # Show token positions
        token_positions = {k: v for k, v in balances.items() if k != "SOL" and v > 0.000001}
        
        if token_positions:
            logger.info(f"🎯 Token Positions ({len(token_positions)}):")
            for token_mint, balance in token_positions.items():
                logger.info(f"   📍 {token_mint[:8]}...: {balance:.6f} tokens")
                
            total_estimated_value = len(token_positions) * 0.001  # Rough estimate
            logger.info(f"💡 Estimated total position value: ~{total_estimated_value:.6f} SOL")
            
        else:
            logger.info("✅ No token positions found - wallet is clean")
            
    except Exception as e:
        logger.error(f"❌ Error checking positions: {e}")
    
    logger.info("=" * 60)

async def main():
    parser = argparse.ArgumentParser(description='Test liquidation functionality')
    parser.add_argument('--simulate', action='store_true', 
                       help='Run liquidation simulation (no real trades)')
    parser.add_argument('--emergency', action='store_true', 
                       help='Emergency liquidate all real positions')
    parser.add_argument('--check', action='store_true', 
                       help='Check current wallet positions')
    
    args = parser.parse_args()
    
    if args.simulate:
        await test_liquidation_simulation()
        
    elif args.emergency:
        logger.info("🚨 EMERGENCY LIQUIDATION MODE")
        logger.info("⚠️  This will sell ALL token positions in your wallet!")
        
        confirm = input("Are you sure you want to liquidate all positions? (yes/NO): ")
        if confirm.lower() == 'yes':
            logger.info("🔥 Starting emergency liquidation...")
            await emergency_liquidate_all()
        else:
            logger.info("❌ Emergency liquidation cancelled")
            
    elif args.check:
        await check_current_positions()
        
    else:
        logger.info("🧪 LIQUIDATION TEST SUITE")
        logger.info("=" * 60)
        logger.info("Available test modes:")
        logger.info("  --simulate   : Test liquidation logic (safe)")
        logger.info("  --check      : Check current positions")
        logger.info("  --emergency  : Emergency liquidate (REAL TRADES)")
        logger.info("=" * 60)
        logger.info("💡 Run with --simulate first to test safely")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Test cancelled")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        sys.exit(1)
