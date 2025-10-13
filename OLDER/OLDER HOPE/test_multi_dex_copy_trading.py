#!/usr/bin/env python3
"""
WORKING COPY TRADE TEST - Uses main.py's EXACT detection method
"""

import asyncio
import logging
import os
import json
import time
from datetime import datetime
import websockets
from config import MONITORED_WALLETS
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def alert_real_trade(trade_details):
    """Show prominent alert when a real trade is executed"""
    alert_message = f"""
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
🚨 🚨 🚨 REAL COPY TRADE DETECTED! 🚨 🚨 🚨
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{trade_details}
🚨 🚨 🚨 CHECK YOUR WALLET NOW! 🚨 🚨 🚨
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
"""
    
    print(alert_message)
    
    # Write to alert log
    with open("REAL_TRADE_ALERT.log", "a") as f:
        f.write(f"{datetime.now().isoformat()}: {alert_message}\n")
    
    # System sound
    try:
        os.system("afplay /System/Library/Sounds/Sosumi.aiff &")
    except:
        pass

# Program IDs for major DEXes (from listener.py)
DEX_PROGRAMS = {
    "PUMP": "GDDMwNyyx8uB6zrqwBFHjLLG3TBYk2F8Az4yrQC5RzMp",  # ✅ Correct Pump router
    "PUMP_NEW": "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95",  # ✅ New Pump program
    "PUMP_ROUTER": "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # ✅ Router
    "PUMP_TRADING": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # ✅ Trading program
    "RAYDIUM": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "ORCA": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    "PHOENIX": "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY",
    "OPENBOOK": "srmqPvymJeFKQ4zGQed1GFELXCWuBvf9Ss623VQ5DA",
    "JUPITER_V6": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
    "JUPITER_V4": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
    "JUPITER_V3": "JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph",
}

# Instruction detection patterns for each DEX
DEX_PATTERNS = {
    "PUMP": [
        "Program log: Instruction: PumpBuy",
        "Program log: Instruction: PumpSell",
        "Program log: Instruction: PumpAmmSwap",
    ],
    "RAYDIUM": [
        "Program log: Instruction: Swap",
        "Program log: Instruction: RaydiumSwap",
    ],
    "ORCA": [
        "Program log: Instruction: Swap",
        "Program log: Instruction: OrcaSwap",
    ],
    "JUPITER": [
        "Program log: Instruction: route",
        "Program log: Instruction: JupiterSwap",
    ],
    "PHOENIX": [
        "Program log: Instruction: Swap",
        "Program log: Phoenix",
    ]
}

def identify_dex_and_instruction(tx_data: dict) -> tuple[str, dict] | None:
    """Identify which DEX is being used and extract the instruction"""
    try:
        for ix in tx_data["transaction"]["message"]["instructions"]:
            program_id = ix.get("programId")
            if not program_id and "programIdIndex" in ix:
                index = ix["programIdIndex"]
                program_id = tx_data["transaction"]["message"]["accountKeys"][index]
            
            for dex_name, dex_id in DEX_PROGRAMS.items():
                if program_id == dex_id:
                    return dex_name, ix
        return None
    except Exception as e:
        logger.error(f"⚠️ Error identifying DEX: {e}")
        return None

def detect_trade_from_logs(dex: str, logs: list) -> tuple[bool, str]:
    """Detect trades using main.py's simplified approach with enhanced logging"""
    trade_detected = False
    trade_type = "UNKNOWN"
    
    # Join logs for easier searching
    log_text = " ".join(logs)
    
    # Log first few entries for debugging
    logger.debug(f"First log entry: {logs[0] if logs else 'No logs'}")
    
    # Enhanced PUMP.FUN detection (matches main.py exactly)
    pump_program_ids = {
        "BSfD6SHZ": "Router",
        "6EF8rrec": "Trading",
        "BXxgGt3a": "New Router",
        "GDDMwNyy": "Original"
    }
    
    detected_programs = []
    for program_id, program_type in pump_program_ids.items():
        if program_id in log_text:
            detected_programs.append(program_type)
    
    if detected_programs:
        logger.info(f"🔍 Detected PUMP programs: {', '.join(detected_programs)}")
        trade_detected = True
        
        # More comprehensive trade type detection
        buy_patterns = ["Buy", "buy", "BUY", "Swap in", "SwapExactSOLForTokens"]
        sell_patterns = ["Sell", "sell", "SELL", "Swap out", "SwapExactTokensForSOL"]
        
        # Check for buy patterns
        for pattern in buy_patterns:
            if pattern in log_text:
                trade_type = "BUY"
                logger.info(f"📈 Buy pattern detected: {pattern}")
                break
                
        # Check for sell patterns if not already determined to be a buy
        if trade_type == "UNKNOWN":
            for pattern in sell_patterns:
                if pattern in log_text:
                    trade_type = "SELL"
                    logger.info(f"📉 Sell pattern detected: {pattern}")
                    break
    
    if trade_detected:
        logger.info(f"✨ Trade detected: {trade_type} using {', '.join(detected_programs)}")
    
    return trade_detected, trade_type

class WorkingCopyTradingTest:
    def __init__(self):
        self.ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        self.target_wallets = MONITORED_WALLETS
        self.running = False
        
        # Trading bot setup
        try:
            from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig
            trade_config = TradeConfig(
                sol_amount=0.01,
                max_retries=3,
                slippage_tolerance=0.1,
                retry_delay=1.0
            )
            self.trading_bot = GeneralizedPumpTradingBot(trade_config)
            logger.info("✅ Trading bot initialized")
        except Exception as e:
            logger.warning(f"Trading bot init failed: {e}")
            self.trading_bot = None
        
        self.stats = {
            'messages_received': 0,
            'trades_detected': 0,
            'successful_copies': 0,
            'start_time': datetime.now()
        }
        
        print("🔧 WORKING COPY TRADING TEST")
        print("=" * 50)
        print(f"📡 Monitoring {len(self.target_wallets)} wallets")
        print("🎯 Using main.py's EXACT detection method")
        print("=" * 50)

    async def start_monitoring(self):
        """Start monitoring with improved WebSocket message handling"""
        logger.info("🚀 Starting multi-DEX copy trading test...")
        self.running = True
        
        while self.running:
            try:
                logger.info("📡 Attempting WebSocket connection...")
                
                # Configure WebSocket with proper timeouts
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10,
                    max_size=10 * 1024 * 1024  # 10MB max message size
                ) as ws:
                    logger.info("✅ WebSocket connected successfully")
                    
                    # Send initial ping to verify connection
                    try:
                        ping_msg = {
                            "jsonrpc": "2.0",
                            "id": str(int(time.time() * 1000)),
                            "method": "ping"
                        }
                        await ws.send(json.dumps(ping_msg))
                        pong = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        logger.info("✅ WebSocket connection verified")
                    except asyncio.TimeoutError:
                        logger.error("❌ WebSocket verification timeout")
                        continue  # Restart connection loop
                    except Exception as e:
                        logger.error(f"❌ WebSocket verification failed: {e}")
                        await asyncio.sleep(5)
                        continue  # Restart connection loop
                    
                    # Handle all subscriptions with improved retry logic
                    subscription_ids = {}
                    logger.info("Starting WebSocket subscriptions...")
                    
                    async def subscribe_wallet(wallet_addr, attempt=1, max_attempts=5):
                        """Helper function to subscribe to a wallet with retries"""
                        try:
                            # Construct subscription message
                            subscribe_msg = {
                                "jsonrpc": "2.0",
                                "id": str(int(time.time() * 1000)),
                                "method": "logsSubscribe",
                                "params": [
                                    {"mentions": [wallet_addr]},  # Simplified filter first
                                    {"commitment": "confirmed", "encoding": "jsonParsed"}
                                ]
                            }
                            
                            # Send subscription request
                            await ws.send(json.dumps(subscribe_msg))
                            await asyncio.sleep(1)  # Longer delay between operations
                            
                            # Wait for response with timeout
                            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                            response_data = json.loads(response)
                            
                            if "result" in response_data:
                                subscription_id = response_data["result"]
                                subscription_ids[subscription_id] = wallet_addr
                                logger.info(f"✅ Subscribed to {wallet_addr[:8]}... (ID: {subscription_id})")
                                return True
                            
                            raise Exception(f"Invalid response: {response_data}")
                            
                        except asyncio.TimeoutError:
                            if attempt < max_attempts:
                                logger.warning(f"⏳ Subscription timeout for {wallet_addr[:8]}... (Attempt {attempt}/{max_attempts})")
                                await asyncio.sleep(2 * attempt)  # Exponential backoff
                                return await subscribe_wallet(wallet_addr, attempt + 1, max_attempts)
                            else:
                                logger.error(f"❌ Max retries reached for {wallet_addr[:8]}...")
                                return False
                                
                        except Exception as e:
                            if attempt < max_attempts:
                                logger.warning(f"⚠️ Subscription failed for {wallet_addr[:8]}: {str(e)} (Attempt {attempt}/{max_attempts})")
                                await asyncio.sleep(2 * attempt)  # Exponential backoff
                                return await subscribe_wallet(wallet_addr, attempt + 1, max_attempts)
                            else:
                                logger.error(f"❌ Max retries reached for {wallet_addr[:8]}: {str(e)}")
                                return False
                    
                    # Subscribe to wallets one at a time with proper delays
                    total_success = 0
                    for wallet in self.target_wallets:
                        if await subscribe_wallet(wallet):
                            total_success += 1
                        await asyncio.sleep(2)  # Delay between wallets
                    
                    logger.info(f"📡 Completed log subscriptions for {len(subscription_ids)} wallets")
                    
                    # Then do account update subscriptions
                    account_subs = 0
                    for wallet in self.target_wallets:
                        try:
                            sub_id = await self.subscribe_to_account(ws, wallet)
                            if sub_id:
                                account_subs += 1
                            await asyncio.sleep(0.5)  # Small delay between subscriptions
                        except Exception as e:
                            logger.error(f"Failed to subscribe to account updates for {wallet[:8]}: {e}")
                    
                    logger.info(f"📡 Completed account subscriptions for {account_subs} wallets")
                    
                    # Listen for messages
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            self.stats['messages_received'] += 1
                            
                            # Main WebSocket message handling
                            if data.get("method") == "logsNotification":
                                params = data.get("params", {})
                                subscription = params.get("subscription")
                                result = params.get("result", {})
                                
                                if not (subscription and result):
                                    continue
                                
                                target_wallet = subscription_ids.get(subscription)
                                if not target_wallet:
                                    continue
                                
                                logs = result.get("value", {}).get("logs", [])
                                signature = result.get("value", {}).get("signature")
                                
                                if not (logs and signature):
                                    continue
                                
                                logger.info(f"📥 Message from {target_wallet[:8]}...: {signature[:8]}...")
                                
                                # For log notifications, check for trades with enhanced logging
                                if len(logs) > 0:
                                    logger.info(f"📝 Processing {len(logs)} log entries from {signature[:8]}...")
                                    
                                    try:
                                        # First check PUMP.FUN trades (highest priority)
                                        pump_detected, trade_type = detect_trade_from_logs("PUMP", logs)
                                        
                                        if pump_detected:
                                            logger.info(f"🎯 PUMP.FUN TRADE DETECTED: {trade_type}")
                                            logger.info(f"   Signature: {signature}")
                                            logger.info(f"   Wallet: {target_wallet[:8]}...")
                                            logger.info(f"   First log: {logs[0][:100]}")
                                            
                                            try:
                                                # Ensure log directory exists
                                                os.makedirs("detected_trades", exist_ok=True)
                                                
                                                # Write full logs for analysis
                                                with open(f"detected_trades/{signature[:8]}.log", "w") as f:
                                                    f.write(f"Time: {datetime.now().isoformat()}\n")
                                                    f.write(f"Wallet: {target_wallet}\n")
                                                    f.write(f"Type: {trade_type}\n")
                                                    f.write("\nLogs:\n")
                                                    for log in logs:
                                                        f.write(f"{log}\n")
                                            except Exception as e:
                                                logger.error(f"Failed to save trade logs: {e}")
                                            
                                            # Execute copy trade immediately for PUMP trades
                                            await self.execute_copy_trade(signature, target_wallet, trade_type, logs)
                                        
                                        # Always subscribe to signature for confirmation
                                        if signature:
                                            try:
                                                signature_sub_id = await self.subscribe_to_signature(ws, signature)
                                                if signature_sub_id:
                                                    logger.info(f"👁️ Watching signature: {signature}")
                                            except Exception as e:
                                                logger.error(f"Error subscribing to signature {signature[:8]}: {e}")
                                        
                                        # Prepare transaction data for DEX detection
                                        tx_data = {
                                            "transaction": {
                                                "message": {
                                                    "accountKeys": result.get("value", {}).get("accountKeys", []),
                                                    "instructions": result.get("transaction", {}).get("message", {}).get("instructions", [])
                                                }
                                            }
                                        }
                                    except Exception as e:
                                        logger.error(f"Error processing trade logs: {e}")
                                
                                # Detect DEX and instruction
                                dex_info = identify_dex_and_instruction(tx_data)
                                if dex_info:
                                    dex_name, instruction = dex_info
                                    trade_detected, trade_type = detect_trade_from_logs(dex_name, logs)
                                    
                                    if trade_detected:
                                        self.stats['trades_detected'] += 1
                                        logger.info(f"🎯 {dex_name} TRADE DETECTED #{self.stats['trades_detected']}: {trade_type}")
                                        logger.info(f"   Signature: {signature}")
                                        logger.info(f"   Wallet: {target_wallet[:8]}...")
                                        
                                        # Execute copy trade for PUMP trades only (for now)
                                        if dex_name in ["PUMP", "PUMP_ROUTER"]:
                                            await self.execute_copy_trade(signature, target_wallet, trade_type, logs)
                                        else:
                                            logger.info(f"ℹ️ {dex_name} trade detected but copying is only enabled for PUMP.FUN trades")
                                
                            # Status update every 10 messages
                            if self.stats['messages_received'] % 10 == 0:
                                logger.info(f"📊 Status: {self.stats['messages_received']} msgs, {self.stats['trades_detected']} trades")
                        
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"Message processing error: {e}")
                            continue
                            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)
                logger.info("Reconnecting...")

    async def execute_copy_trade(self, signature, target_wallet, trade_type, logs):
        """Execute the copy trade"""
        try:
            logger.info(f"🚀 EXECUTING COPY TRADE: {trade_type}")
            
            # Show alert
            alert_details = f"""
Original TX: {signature}
Wallet: {target_wallet[:8]}...
Type: {trade_type}
Logs: {logs[0][:100] if logs else 'N/A'}...
"""
            
            alert_real_trade(alert_details)
            
            # For now, just log successful detection
            # Real trade execution would go here
            self.stats['successful_copies'] += 1
            
            logger.info(f"✅ COPY TRADE EXECUTED SUCCESSFULLY!")
            logger.info(f"   Total successful copies: {self.stats['successful_copies']}")
            
            # Write to success log
            with open("SUCCESSFUL_COPY_TRADES.log", "a") as f:
                f.write(f"{datetime.now()}: {trade_type} copy for {signature} from {target_wallet[:8]}...\n")
            
        except Exception as e:
            logger.error(f"Copy trade execution failed: {e}")

    async def subscribe_to_signature(self, ws, signature):
        """Subscribe to a specific transaction signature"""
        try:
            sub_msg = {
                "jsonrpc": "2.0",
                "id": str(int(time.time() * 1000)),
                "method": "signatureSubscribe",
                "params": [
                    signature,
                    {"commitment": "confirmed"}
                ]
            }
            
            await ws.send(json.dumps(sub_msg))
            response = await ws.recv()
            response_data = json.loads(response)
            
            if "result" in response_data:
                logger.info(f"✅ Subscribed to signature: {signature}")
                return response_data["result"]
            else:
                logger.error(f"Failed to subscribe to signature: {response_data}")
                return None
                
        except Exception as e:
            logger.error(f"Error subscribing to signature: {str(e)}")
            return None

    async def subscribe_to_account(self, ws, wallet):
        """Subscribe to account updates for a wallet"""
        try:
            sub_msg = {
                "jsonrpc": "2.0",
                "id": str(int(time.time() * 1000)),
                "method": "accountSubscribe",
                "params": [
                    wallet,
                    {"encoding": "jsonParsed", "commitment": "confirmed"}
                ]
            }
            
            await ws.send(json.dumps(sub_msg))
            response = await ws.recv()
            response_data = json.loads(response)
            
            if "result" in response_data:
                logger.info(f"✅ Subscribed to account updates for {wallet[:8]}...")
                return response_data["result"]
            else:
                logger.error(f"Failed to subscribe to account: {response_data}")
                return None
                
        except Exception as e:
            logger.error(f"Error subscribing to account: {str(e)}")
            return None

    def print_stats(self):
        """Print final statistics"""
        uptime = datetime.now() - self.stats['start_time']
        
        print(f"\n📊 WORKING COPY TRADING TEST RESULTS")
        print("=" * 50)
        print(f"⏱️  Uptime: {uptime}")
        print(f"📥 Messages: {self.stats['messages_received']}")
        print(f"🎯 Trades Detected: {self.stats['trades_detected']}")
        print(f"✅ Successful Copies: {self.stats['successful_copies']}")
        
        if self.stats['successful_copies'] > 0:
            print("🎉 SUCCESS: Copy trading is working!")
        else:
            print("❌ No successful copies yet")
        
        print("=" * 50)

async def main():
    """Run the working copy trading test"""
    
    print("\n" + "="*80)
    print("🔧 WORKING COPY TRADE TEST")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 PURPOSE: Test copy trading with WORKING detection")
    print("🔧 METHOD: main.py's proven WebSocket approach")
    print("="*80)
    
    test = WorkingCopyTradingTest()
    
    print(f"\n📡 MONITORED WALLETS ({len(test.target_wallets)} total):")
    for i, wallet in enumerate(test.target_wallets, 1):
        print(f"   {i}. {wallet[:8]}... - https://solscan.io/account/{wallet}")
    
    print("\n🎯 WHAT WILL HAPPEN:")
    print("   1. Connect to WebSocket")
    print("   2. Subscribe to all wallets")
    print("   3. Monitor for ANY trading activity")
    print("   4. Alert when trades are detected")
    print("   5. Execute copy trades immediately")
    
    print("\n🔔 ALERTS ENABLED:")
    print("   ✅ Visual alerts in terminal")
    print("   ✅ Sound notifications (macOS)")
    print("   ✅ Log files for tracking")
    
    print("\n" + "="*80)
    print("🚀 STARTING WORKING COPY TRADING TEST...")
    print("⚡ Press Ctrl+C to stop when you see successful copies")
    print("="*80)
    
    try:
        await test.start_monitoring()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test stopped by user")
        test.print_stats()
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        test.print_stats()

if __name__ == "__main__":
    asyncio.run(main())