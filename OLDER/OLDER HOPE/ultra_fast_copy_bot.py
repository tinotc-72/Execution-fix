#!/usr/bin/env python3
"""
ULTRA FAST Copy Trading Bot
Based on proven detection patterns from OLDER scripts for maximum speed
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

from config import MONITORED_WALLETS
from env_keys import EnvKeys
from production_pump_trading_bot import TradeConfig
from generalized_pump_trading_bot import GeneralizedPumpTradingBot
import logging

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL"

class UltraFastCopyBot:
    """
    Ultra-fast copy trading bot focused on instant log-based detection
    """
    
    def __init__(self):
        self.copy_config = {
            'fixed_buy_amount': 0.01,
            'enable_sells': True,
            'enable_buys': True,
        }
        
        # Initialize trading bot
        trade_config = TradeConfig(sol_amount=0.01, max_retries=3)
        self.trading_bot = GeneralizedPumpTradingBot(trade_config)
        
        # WebSocket configuration
        self.helius_ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        
        # Track recent trades to avoid duplicates (small set for speed)
        self.processed_signatures = set()
        self.target_wallets = MONITORED_WALLETS
        
        # Performance tracking
        self.stats = {
            'trades_detected': 0,
            'trades_copied': 0,
            'successful_copies': 0,
            'failed_copies': 0,
            'total_volume_sol': 0.0,
            'start_time': datetime.now()
        }
        
        logger.info("⚡ ULTRA-FAST Copy Trading Bot initialized")
        logger.info(f"📡 Monitoring wallets: {self.target_wallets}")
    
    def ultra_fast_log_detection(self, logs: List[str], target_wallet: str, signature: str) -> Optional[Dict]:
        """
        ULTRA FAST: Detect trades directly from WebSocket logs - NO RPC CALLS!
        Based on proven patterns from OLDER scripts
        """
        try:
            # FASTEST PATH: Look for proven pump.fun instruction patterns
            pump_instruction = None
            token_mint = None
            
            for log in logs:
                # INSTANT detection from logs (proven patterns)
                if "Program log: Instruction: PumpBuy" in log:
                    pump_instruction = "BUY"
                    logger.info(f"🚀 INSTANT BUY detection from log!")
                elif "Program log: Instruction: PumpSell" in log:
                    pump_instruction = "SELL"
                    logger.info(f"🚀 INSTANT SELL detection from log!")
                elif "Program log: Token:" in log:
                    # Extract token mint: "Program log: Token: ERGKydJayFVtBogci46Ht4U3otjJgchiYWo83mT1Kgw5"
                    try:
                        token_mint = log.split("Program log: Token: ")[1].strip()
                        logger.info(f"🎯 Token extracted: {token_mint[:8]}...")
                    except:
                        continue
            
            # If we found both instruction and token from logs - INSTANT EXECUTION!
            if pump_instruction and token_mint:
                logger.info(f"⚡ INSTANT DETECTION: {pump_instruction} {token_mint[:8]}... (NO RPC CALL!)")
                
                return {
                    'action': TradeAction.BUY if pump_instruction == "BUY" else TradeAction.SELL,
                    'token_mint': token_mint,
                    'sol_amount': 0.01,
                    'target_wallet': target_wallet,
                    'signature': signature,
                    'timestamp': datetime.now(),
                    'dex': 'PUMP',
                    'detection_method': 'ultra_fast_log_instant'
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Ultra-fast log detection failed: {e}")
            return None
    
    async def execute_instant_trade(self, trade_info: Dict) -> Dict:
        """
        ULTRA FAST: Execute trade immediately with fire-and-forget pattern
        """
        result = {
            'success': False,
            'signature': None,
            'error': None,
            'execution_time_ms': 0
        }
        
        start_time = datetime.now()
        
        try:
            action = trade_info['action']
            token_mint = trade_info['token_mint']
            
            logger.info(f"🚀 INSTANT EXECUTE: {action.value} {token_mint[:8]}...")
            
            if action == TradeAction.BUY:
                logger.info(f"💰 INSTANT BUY: {trade_info['sol_amount']} SOL")
                
                # Execute buy immediately
                trade_result = await self.trading_bot.buy_token(
                    token_mint=token_mint,
                    sol_amount=trade_info['sol_amount']
                )
                
                if trade_result and hasattr(trade_result, 'result') and trade_result.result.value == 'success':
                    result['success'] = True
                    result['signature'] = trade_result.signature
                    self.stats['successful_copies'] += 1
                    logger.info(f"✅ INSTANT BUY SUCCESS: {trade_result.signature[:8]}...")
                else:
                    result['error'] = getattr(trade_result, 'error_message', 'Unknown error')
                    self.stats['failed_copies'] += 1
                    logger.error(f"❌ INSTANT BUY FAILED: {result['error']}")
            
            elif action == TradeAction.SELL:
                logger.info(f"💸 INSTANT SELL: {token_mint[:8]}...")
                
                # For sells, we try to sell if we have the token, otherwise opportunistic buy
                try:
                    # Try to sell first (fast path)
                    trade_result = await self.trading_bot.sell_token(
                        token_mint=token_mint,
                        percentage=100  # Sell all for speed
                    )
                    
                    if trade_result and hasattr(trade_result, 'result') and trade_result.result.value == 'success':
                        result['success'] = True
                        result['signature'] = trade_result.signature
                        self.stats['successful_copies'] += 1
                        logger.info(f"✅ INSTANT SELL SUCCESS: {trade_result.signature[:8]}...")
                    else:
                        # If sell fails, try opportunistic buy
                        logger.info(f"💡 Sell failed - trying opportunistic buy...")
                        
                        trade_result = await self.trading_bot.buy_token(
                            token_mint=token_mint,
                            sol_amount=0.01
                        )
                        
                        if trade_result and hasattr(trade_result, 'result') and trade_result.result.value == 'success':
                            result['success'] = True
                            result['signature'] = trade_result.signature
                            self.stats['successful_copies'] += 1
                            logger.info(f"✅ OPPORTUNISTIC BUY SUCCESS: {trade_result.signature[:8]}...")
                        else:
                            result['error'] = getattr(trade_result, 'error_message', 'Both sell and buy failed')
                            self.stats['failed_copies'] += 1
                            logger.error(f"❌ BOTH SELL AND BUY FAILED: {result['error']}")
                            
                except Exception as sell_error:
                    result['error'] = str(sell_error)
                    self.stats['failed_copies'] += 1
                    logger.error(f"❌ SELL EXECUTION ERROR: {sell_error}")
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result['execution_time_ms'] = execution_time
            
            self.stats['trades_detected'] += 1
            self.stats['trades_copied'] += 1
            self.stats['total_volume_sol'] += trade_info['sol_amount']
            
            logger.info(f"⚡ INSTANT EXECUTION COMPLETE: {execution_time:.1f}ms")
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result['execution_time_ms'] = execution_time
            result['error'] = str(e)
            self.stats['failed_copies'] += 1
            logger.error(f"❌ INSTANT EXECUTION ERROR: {e}")
        
        return result
    
    async def start_monitoring(self):
        """Start monitoring with ultra-fast detection"""
        logger.info("🚀 Starting ULTRA-FAST copy trading bot...")
        logger.info(f"📡 Monitoring {len(self.target_wallets)} wallets")
        
        while True:
            try:
                async with websockets.connect(self.helius_ws_url) as ws:
                    # Subscribe to all target wallets
                    for wallet in self.target_wallets:
                        subscription = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "logsSubscribe",
                            "params": [
                                {"mentions": [wallet]},
                                {"commitment": "finalized"}
                            ]
                        }
                        await ws.send(json.dumps(subscription))
                        logger.info(f"✅ Subscribed to wallet: {wallet[:8]}...")
                    
                    logger.info("⚡ ULTRA-FAST bot active - waiting for trades...")
                    
                    # Listen for messages with maximum speed priority
                    while True:
                        try:
                            msg = await ws.recv()
                            data = json.loads(msg)
                            
                            result = data.get("params", {}).get("result", {})
                            logs = result.get("value", {}).get("logs", [])
                            signature = result.get("value", {}).get("signature")
                            
                            if not logs or not signature:
                                continue
                            
                            # Skip duplicates (ultra-fast check)
                            if signature in self.processed_signatures:
                                continue
                            
                            self.processed_signatures.add(signature)
                            
                            # Keep set small for speed (only last 100 signatures)
                            if len(self.processed_signatures) > 100:
                                self.processed_signatures = set(list(self.processed_signatures)[-50:])
                            
                            # ULTRA FAST: Check if any target wallet is in logs
                            for wallet in self.target_wallets:
                                wallet_in_logs = any(wallet in log for log in logs)
                                if not wallet_in_logs:
                                    continue
                                
                                logger.info(f"⚡ INSTANT detection: {signature[:8]}... from {wallet[:8]}...")
                                
                                # Try ultra-fast log detection immediately
                                fast_result = self.ultra_fast_log_detection(logs, wallet, signature)
                                if fast_result:
                                    logger.info(f"🚀 INSTANT LOG TRADE: {fast_result['action'].value} {fast_result['token_mint'][:8]}...")
                                    
                                    # Execute immediately in background for maximum speed
                                    asyncio.create_task(self.execute_instant_trade(fast_result))
                                    break  # Found trade, move to next message
                            
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("WebSocket connection closed, reconnecting...")
                            break
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            continue
            
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                logger.info("Reconnecting in 2 seconds...")
                await asyncio.sleep(2)
    
    def print_stats(self):
        """Print current performance statistics"""
        uptime = datetime.now() - self.stats['start_time']
        
        print(f"\n📊 ULTRA-FAST COPY BOT STATISTICS")
        print("=" * 50)
        print(f"⏱️  Uptime: {uptime}")
        print(f"🎯 Trades Detected: {self.stats['trades_detected']}")
        print(f"📋 Trades Copied: {self.stats['trades_copied']}")
        print(f"✅ Successful Copies: {self.stats['successful_copies']}")
        print(f"❌ Failed Copies: {self.stats['failed_copies']}")
        print(f"💰 Total Volume: {self.stats['total_volume_sol']:.6f} SOL")
        
        if self.stats['trades_copied'] > 0:
            success_rate = (self.stats['successful_copies'] / self.stats['trades_copied']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("=" * 50)
    
    async def close(self):
        """Clean shutdown"""
        logger.info("🛑 Shutting down ultra-fast copy trading bot...")
        if self.trading_bot:
            await self.trading_bot.close()
        self.print_stats()

async def main():
    """Run the ultra-fast copy trading bot"""
    bot = UltraFastCopyBot()
    
    try:
        await bot.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
