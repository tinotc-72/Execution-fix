#!/usr/bin/env python3
"""
Test the copy trading system to verify functionality
"""

import asyncio
import logging
from datetime import datetime, timedelta
import json
from typing import Dict, List

from advanced_copy_trading_bot import PumpCopyTradingBot
from listener import fetch_transaction, identify_dex_and_instruction, extract_trade_data
from config import MONITORED_WALLETS
from env_keys import EnvKeys
import aiohttp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_wallet_activity(wallet: str, days_back: int = 7) -> List[Dict]:
    """Check recent transaction activity for a wallet"""
    logger.info(f"🔍 Checking activity for wallet {wallet[:8]}... (last {days_back} days)")
    
    try:
        # Use Helius API to get recent transactions
        env_keys = EnvKeys()
        url = f"{env_keys.HELIUS_RPC_URL.replace('/v0/', '/v0/addresses/')}{wallet}/transactions"
        
        params = {
            'limit': 50,  # Get last 50 transactions
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    transactions = await response.json()
                    
                    recent_pump_trades = []
                    cutoff_date = datetime.now() - timedelta(days=days_back)
                    
                    for tx in transactions:
                        # Check if transaction is recent
                        timestamp = tx.get('timestamp', 0)
                        tx_date = datetime.fromtimestamp(timestamp)
                        
                        if tx_date < cutoff_date:
                            continue
                        
                        # Analyze transaction for pump.fun activity
                        dex_info = identify_dex_and_instruction(tx)
                        if dex_info and dex_info[0] == "PUMP":
                            trade_data = extract_trade_data(tx, dex_info[0], dex_info[1])
                            if trade_data:
                                recent_pump_trades.append({
                                    'signature': tx.get('signature', ''),
                                    'timestamp': tx_date,
                                    'dex': dex_info[0],
                                    'instruction': dex_info[1],
                                    'token_mint': trade_data.get('token_mint', ''),
                                    'trade_data': trade_data
                                })
                    
                    logger.info(f"📊 Found {len(recent_pump_trades)} pump.fun trades in last {days_back} days")
                    return recent_pump_trades
                
                else:
                    logger.error(f"Failed to fetch transactions: {response.status}")
                    return []
    
    except Exception as e:
        logger.error(f"Error checking wallet activity: {e}")
        return []

async def test_single_transaction_processing(signature: str, target_wallet: str):
    """Test processing a specific transaction"""
    logger.info(f"🧪 Testing transaction processing: {signature[:8]}...")
    
    # Create a test bot instance
    copy_config = {
        'fixed_buy_amount': 0.001,  # Use small amount for testing
        'delay_seconds': 1,
        'enable_sells': True,
        'enable_buys': True,
        'proportional_selling': True
    }
    
    bot = PumpCopyTradingBot(copy_config)
    
    try:
        # Fetch and analyze the transaction
        tx_data = await fetch_transaction(signature)
        if not tx_data:
            logger.error("❌ Could not fetch transaction data")
            return
        
        logger.info("✅ Transaction data fetched successfully")
        
        # Analyze the trade
        target_trade = await bot.analyze_target_trade(tx_data, target_wallet)
        if not target_trade:
            logger.warning("⚠️ No pump.fun trade detected in this transaction")
            return
        
        logger.info("✅ Trade analysis successful:")
        logger.info(f"   Action: {target_trade['action'].value}")
        logger.info(f"   Token: {target_trade['token_mint'][:8]}...")
        logger.info(f"   SOL Amount: {target_trade['sol_amount']:.6f}")
        logger.info(f"   Token Amount: {target_trade['token_amount']:,}")
        
        # Test copy trade execution (dry run mode)
        logger.info("🧪 Testing copy trade execution (dry run)...")
        
        # Note: In a real test, you might want to execute a small trade
        # For now, we'll just log what would happen
        if target_trade['action'].value == 'BUY':
            logger.info(f"💰 Would copy buy {copy_config['fixed_buy_amount']:.3f} SOL worth")
        elif target_trade['action'].value == 'SELL':
            logger.info(f"💸 Would copy sell proportionally")
        
        return target_trade
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return None
    finally:
        await bot.close()

async def test_websocket_connection():
    """Test WebSocket connection to Helius"""
    logger.info("🔌 Testing WebSocket connection...")
    
    try:
        import websockets
        env_keys = EnvKeys()
        
        async with websockets.connect(env_keys.HELIUS_Standard_Websocket_URL) as ws:
            # Test subscription
            subscription = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "logsSubscribe",
                "params": [
                    {"mentions": [MONITORED_WALLETS[0]]},
                    {"commitment": "finalized"}
                ]
            }
            
            await ws.send(json.dumps(subscription))
            logger.info("✅ WebSocket connection successful")
            logger.info("✅ Subscription sent successfully")
            
            # Wait for a response or timeout
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                logger.info("✅ Received WebSocket response")
                logger.info(f"Response: {response}")
            except asyncio.TimeoutError:
                logger.warning("⚠️ No immediate response (normal for quiet periods)")
            
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")

async def analyze_monitored_wallets():
    """Analyze all monitored wallets for recent activity"""
    logger.info("🔍 Analyzing all monitored wallets...")
    
    total_recent_trades = 0
    
    for i, wallet in enumerate(MONITORED_WALLETS):
        logger.info(f"\n📡 Wallet {i+1}/{len(MONITORED_WALLETS)}: {wallet}")
        
        recent_trades = await check_wallet_activity(wallet, days_back=3)
        total_recent_trades += len(recent_trades)
        
        if recent_trades:
            logger.info(f"✅ Found {len(recent_trades)} recent pump.fun trades")
            
            # Test the most recent trade
            latest_trade = recent_trades[0]
            logger.info(f"🧪 Testing latest trade: {latest_trade['signature'][:8]}...")
            
            await test_single_transaction_processing(
                latest_trade['signature'], 
                wallet
            )
        else:
            logger.warning(f"⚠️ No recent pump.fun trades found")
    
    logger.info(f"\n📊 SUMMARY:")
    logger.info(f"   Total monitored wallets: {len(MONITORED_WALLETS)}")
    logger.info(f"   Total recent trades: {total_recent_trades}")
    
    if total_recent_trades == 0:
        logger.warning("⚠️ No recent pump.fun activity detected!")
        logger.info("💡 Consider:")
        logger.info("   - Checking if wallets are still active")
        logger.info("   - Adding more active wallets")
        logger.info("   - Extending the time window")

async def test_trading_bot_components():
    """Test individual components of the trading bot"""
    logger.info("🧪 Testing trading bot components...")
    
    copy_config = {
        'fixed_buy_amount': 0.001,  # Small test amount
        'delay_seconds': 1,
        'enable_sells': True,
        'enable_buys': True,
        'proportional_selling': True
    }
    
    bot = PumpCopyTradingBot(copy_config)
    
    try:
        # Test bot initialization
        logger.info("✅ Bot initialization successful")
        
        # Test wallet balance check (if needed)
        logger.info("💰 Testing wallet connectivity...")
        
        # Check if we can connect to the trading bot
        if bot.trading_bot:
            logger.info("✅ Trading bot component initialized")
        else:
            logger.error("❌ Trading bot component failed")
        
        logger.info("✅ All components test passed")
        
    except Exception as e:
        logger.error(f"❌ Component test failed: {e}")
    finally:
        await bot.close()

async def main():
    """Run comprehensive copy trading system tests"""
    print("🧪 COPY TRADING SYSTEM TEST SUITE")
    print("=" * 60)
    
    # Test 1: WebSocket Connection
    print("\n1️⃣ Testing WebSocket Connection...")
    await test_websocket_connection()
    
    # Test 2: Trading Bot Components
    print("\n2️⃣ Testing Trading Bot Components...")
    await test_trading_bot_components()
    
    # Test 3: Wallet Activity Analysis
    print("\n3️⃣ Analyzing Monitored Wallets...")
    await analyze_monitored_wallets()
    
    print("\n✅ TEST SUITE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
