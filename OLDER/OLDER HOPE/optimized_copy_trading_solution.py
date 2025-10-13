#!/usr/bin/env python3
"""
SOLUTION: Why main.py detects trades instantly while test script doesn't

🔍 ANALYSIS FINDINGS:
====================

After comparing main.py and the test script (advanced_copy_trading_bot.py), I identified 
the key differences that cause the detection issues:

1. WEBSOCKET MESSAGE FORMAT DIFFERENCES:
   - main.py: Uses data['params']['result'] directly
   - test script: Uses data['params']['result']['value'] (expects nested structure)

2. SUBSCRIPTION HANDLING:
   - main.py: Individual subscription IDs and proper response validation
   - test script: Generic ID (always 1) and less robust validation

3. MESSAGE PROCESSING:
   - main.py: Checks data['method'] == 'subscription' first
   - test script: Assumes specific nested structure without validation

4. LOG PATTERN MATCHING:
   - main.py: Simple, proven substring checks
   - test script: Complex pattern matching that may miss simple cases

RECOMMENDED SOLUTION:
====================
Use the main.py approach for detection and combine it with the test script's 
execution capabilities.
"""

import asyncio
import json
import logging
import time
import traceback
from datetime import datetime
import websockets
import os

from config import MONITORED_WALLETS
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedCopyTradingBot:
    """
    Optimized copy trading bot using main.py detection approach
    Combined with advanced trading execution
    """
    
    def __init__(self):
        # Use exact same WebSocket configuration as main.py
        self.ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        self.target_wallets = MONITORED_WALLETS
        self.running = False
        
        # Initialize advanced trading bot for execution
        try:
            from advanced_copy_trading_bot import PumpCopyTradingBot
            copy_config = {
                'fixed_buy_amount': 0.01,     # Small amount for testing
                'delay_seconds': 0,           # No delay - execute immediately
                'enable_sells': True,         # Copy sell trades
                'enable_buys': True,          # Copy buy trades
                'proportional_selling': True
            }
            self.copy_bot = PumpCopyTradingBot(copy_config)
            logger.info("✅ Advanced copy trading bot initialized")
        except Exception as e:
            logger.error(f"Failed to initialize copy bot: {e}")
            self.copy_bot = None
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'trades_detected': 0,
            'trades_executed': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'start_time': datetime.now()
        }
        
        # Alert system
        self.alert_log = "OPTIMIZED_COPY_TRADE_ALERT.log"
        
        print("\n🚀 OPTIMIZED COPY TRADING BOT")
        print("=" * 50)
        print("🎯 Using main.py detection + advanced execution")
        print(f"📡 Monitoring {len(self.target_wallets)} wallets")
        print("=" * 50)
    
    async def start_monitoring(self):
        """Start monitoring using optimized main.py approach"""
        logger.info("🚀 Starting optimized copy trading bot...")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while self.running:
            try:
                logger.info("Connecting to WebSocket...")
                
                # Use EXACT WebSocket connection method from main.py
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=None,
                    ping_timeout=None
                ) as ws:
                    logger.info("✅ WebSocket connected successfully")
                    
                    # Subscribe using main.py's proven method
                    subscription_ids = {}
                    
                    for i, wallet in enumerate(self.target_wallets):
                        # Use unique subscription ID for each wallet (main.py approach)
                        sub_id = str(int(time.time() * 1000) + i)
                        subscription = {
                            "jsonrpc": "2.0",
                            "id": sub_id,
                            "method": "logsSubscribe",
                            "params": [
                                {"mentions": [wallet]},
                                {"commitment": "confirmed"}  # Fast confirmation
                            ]
                        }
                        
                        await ws.send(json.dumps(subscription))
                        response = await ws.recv()
                        response_data = json.loads(response)
                        
                        if "result" in response_data:
                            subscription_id = response_data["result"]
                            subscription_ids[subscription_id] = wallet
                            logger.info(f"✅ Subscribed to {wallet[:8]}... (ID: {subscription_id})")
                        else:
                            logger.error(f"❌ Failed to subscribe to {wallet[:8]}...: {response}")
                    
                    if not subscription_ids:
                        raise Exception("Failed to establish any subscriptions")
                    
                    logger.info(f"📡 All {len(subscription_ids)} subscriptions active")
                    logger.info("⚡ Monitoring for trades using OPTIMIZED detection...")
                    
                    # Reset reconnect attempts on successful connection
                    reconnect_attempts = 0
                    
                    # Listen for messages using main.py's EXACT approach
                    async for message in ws:
                        try:
                            if not message:
                                continue
                            
                            data = json.loads(message)
                            self.stats['messages_received'] += 1
                            
                            # Use EXACT main.py message processing
                            if "method" in data and data["method"] == "subscription":
                                params = data.get("params", {})
                                subscription = params.get("subscription")
                                result = params.get("result")
                                
                                if not (subscription and result):
                                    continue
                                
                                # Find which wallet this message is from
                                target_wallet = subscription_ids.get(subscription)
                                if not target_wallet:
                                    continue
                                
                                # Extract logs and signature using main.py's approach
                                logs = result.get("logs", [])
                                signature = result.get("signature")
                                
                                if not (logs and signature):
                                    continue
                                
                                # Use main.py's PROVEN detection logic
                                pump_logs = [log for log in logs if any(pattern in log for pattern in 
                                           ["BSfD6SHZ", "6EF8rrec", "pAMMBay6", "Program log: Instruction"])]
                                
                                if pump_logs:
                                    self.stats['trades_detected'] += 1
                                    await self.handle_detected_trade(result, target_wallet, signature, pump_logs)
                                
                                # Print status every 100 messages
                                if self.stats['messages_received'] % 100 == 0:
                                    self.print_status()
                        
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON message: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error processing message: {str(e)}")
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                logger.error(traceback.format_exc())
                reconnect_attempts += 1
                
                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error("Max reconnection attempts reached. Stopping bot.")
                    self.running = False
                    break
                
                # Exponential backoff for reconnection
                delay = min(5 * (2 ** (reconnect_attempts - 1)), 60)
                logger.info(f"Reconnecting in {delay} seconds... (attempt {reconnect_attempts})")
                await asyncio.sleep(delay)
    
    async def handle_detected_trade(self, tx_result: dict, target_wallet: str, signature: str, matching_logs: list):
        """Handle a detected trade with instant execution"""
        try:
            logger.info(f"🎯 TRADE DETECTED #{self.stats['trades_detected']}")
            logger.info(f"   Signature: {signature[:12]}...")
            logger.info(f"   Wallet: {target_wallet[:8]}...")
            logger.info(f"   Matching logs: {len(matching_logs)}")
            
            # Show prominent alert
            await self.show_trade_alert(signature, target_wallet, matching_logs)
            
            # Execute copy trade if copy bot is available
            if self.copy_bot:
                logger.info("🚀 Executing copy trade...")
                self.stats['trades_executed'] += 1
                
                try:
                    # Analyze the trade using the advanced bot
                    trade_info = await self.copy_bot.analyze_target_trade(tx_result, target_wallet)
                    
                    if trade_info:
                        logger.info(f"✅ Trade analysis successful:")
                        logger.info(f"   Action: {trade_info['action'].value}")
                        logger.info(f"   Token: {trade_info['token_mint'][:8]}...")
                        logger.info(f"   Amount: {trade_info.get('sol_amount', 'N/A')} SOL")
                        
                        # Execute based on trade type
                        if trade_info['action'].value == 'BUY' and self.copy_bot.copy_config['enable_buys']:
                            result = await self.copy_bot._execute_copy_buy(trade_info)
                            if result and result.success:
                                self.stats['successful_executions'] += 1
                                logger.info(f"✅ BUY COPY SUCCESSFUL: {result.signature}")
                                await self.log_successful_trade("BUY", trade_info, result.signature)
                            else:
                                self.stats['failed_executions'] += 1
                                logger.error(f"❌ BUY copy failed: {result.error if result else 'Unknown error'}")
                        
                        elif trade_info['action'].value == 'SELL' and self.copy_bot.copy_config['enable_sells']:
                            result = await self.copy_bot._execute_copy_sell(trade_info)
                            if result and result.success:
                                self.stats['successful_executions'] += 1
                                logger.info(f"✅ SELL COPY SUCCESSFUL: {result.signature}")
                                await self.log_successful_trade("SELL", trade_info, result.signature)
                            else:
                                self.stats['failed_executions'] += 1
                                logger.error(f"❌ SELL copy failed: {result.error if result else 'Unknown error'}")
                        else:
                            logger.info(f"⏸️ {trade_info['action'].value} execution disabled in config")
                    else:
                        self.stats['failed_executions'] += 1
                        logger.warning(f"⚠️ Could not analyze trade details")
                        
                except Exception as e:
                    self.stats['failed_executions'] += 1
                    logger.error(f"Copy trade execution error: {str(e)}")
                    logger.error(traceback.format_exc())
            else:
                logger.warning("⚠️ Copy bot not available - only detecting trades")
                
        except Exception as e:
            logger.error(f"Error handling detected trade: {str(e)}")
            logger.error(traceback.format_exc())
    
    async def show_trade_alert(self, signature: str, target_wallet: str, matching_logs: list):
        """Show prominent trade alert"""
        alert_message = f"""
🚨 🚨 🚨 OPTIMIZED COPY TRADE DETECTED! 🚨 🚨 🚨
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Signature: {signature}
Wallet: {target_wallet[:8]}...
Detection: main.py approach (PROVEN)
Logs: {matching_logs[0][:50]}... (+{len(matching_logs)-1} more)
🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨
"""
        
        # Print to console
        print(alert_message)
        
        # Write to alert log
        with open(self.alert_log, "a") as f:
            f.write(f"{datetime.now().isoformat()}: {alert_message}\n")
        
        # Try to make system sound (macOS)
        try:
            os.system("afplay /System/Library/Sounds/Sosumi.aiff &")
        except:
            pass
        
        # Terminal bell
        try:
            print("\a" * 3)
        except:
            pass
    
    async def log_successful_trade(self, action: str, trade_info: dict, execution_signature: str):
        """Log successful copy trade execution"""
        success_message = f"""
✅ COPY TRADE EXECUTION SUCCESS!
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Action: {action}
Original TX: {trade_info['signature']}
Copy TX: {execution_signature}
Token: {trade_info['token_mint']}
Amount: {trade_info.get('sol_amount', 'N/A')} SOL
Target Wallet: {trade_info['target_wallet'][:8]}...
"""
        
        print(success_message)
        
        with open("SUCCESSFUL_COPY_TRADES.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}: {success_message}\n")
    
    def print_status(self):
        """Print current status"""
        uptime = datetime.now() - self.stats['start_time']
        
        logger.info(f"📊 STATUS: Messages: {self.stats['messages_received']}, "
                   f"Detected: {self.stats['trades_detected']}, "
                   f"Executed: {self.stats['trades_executed']}, "
                   f"Success: {self.stats['successful_executions']}, "
                   f"Uptime: {uptime}")
    
    def print_final_stats(self):
        """Print final statistics"""
        uptime = datetime.now() - self.stats['start_time']
        
        print(f"\n📊 OPTIMIZED COPY TRADING BOT FINAL RESULTS")
        print("=" * 60)
        print(f"⏱️  Uptime: {uptime}")
        print(f"📥 Messages Received: {self.stats['messages_received']}")
        print(f"🎯 Trades Detected: {self.stats['trades_detected']}")
        print(f"🚀 Trades Executed: {self.stats['trades_executed']}")
        print(f"✅ Successful Executions: {self.stats['successful_executions']}")
        print(f"❌ Failed Executions: {self.stats['failed_executions']}")
        
        if self.stats['messages_received'] > 0:
            detection_rate = (self.stats['trades_detected'] / self.stats['messages_received']) * 100
            print(f"📈 Detection Rate: {detection_rate:.4f}%")
        
        if self.stats['trades_executed'] > 0:
            success_rate = (self.stats['successful_executions'] / self.stats['trades_executed']) * 100
            print(f"⚡ Execution Success Rate: {success_rate:.1f}%")
        
        print("=" * 60)
        
        if self.stats['successful_executions'] > 0:
            print("🎉 SUCCESS: Copy trading is working with optimized detection!")
            print("📋 Check SUCCESSFUL_COPY_TRADES.log for execution details")
        else:
            print("❌ No successful copy trades executed")
            if self.stats['trades_detected'] > 0:
                print("💡 Trades were detected but execution failed")
            else:
                print("💡 No trades detected - may need more active monitoring time")
    
    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping optimized copy trading bot...")
        self.running = False
        if self.copy_bot:
            await self.copy_bot.close()

async def main():
    """Run the optimized copy trading bot"""
    bot = None
    try:
        bot = OptimizedCopyTradingBot()
        
        print("🚀 Starting OPTIMIZED copy trading bot...")
        print("\n📋 KEY IMPROVEMENTS:")
        print("   ✅ Uses main.py's proven WebSocket detection")
        print("   ✅ Individual subscription IDs for each wallet")
        print("   ✅ Proper message format handling")
        print("   ✅ Simple, reliable log pattern matching")
        print("   ✅ Advanced trade execution capabilities")
        print("   ✅ Comprehensive error handling and reconnection")
        print("\n📍 MONITORING:")
        print(f"   🎯 Wallets: {len(MONITORED_WALLETS)} active traders")
        print("   📊 Real-time statistics and alerts")
        print("   📝 Detailed logging of all activities")
        print("\n⚡ Press Ctrl+C to stop")
        print("=" * 60)
        
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot failed: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        if bot:
            bot.print_final_stats()
            await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
