#!/usr/bin/env python3
"""
Comparison Script: main.py vs test_multi_dex_copy_trading.py
Analysis of why main.py detects trades instantly while test script doesn't
"""

import asyncio
import json
import logging
import time
from datetime import datetime
import websockets
from env_keys import EnvKeys
from config import MONITORED_WALLETS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DetectionComparison:
    def __init__(self):
        self.helius_ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        self.target_wallets = MONITORED_WALLETS
        self.message_count = 0
        self.trade_detections = []
        
        print("\n🔍 DETECTION METHOD COMPARISON")
        print("=" * 60)
        print("🎯 Testing both detection approaches:")
        print("   1. main.py approach: Direct WebSocket + immediate processing")
        print("   2. test script approach: abstracted PumpCopyTradingBot")
        print("=" * 60)
    
    async def test_main_py_approach(self):
        """Test the detection method used in main.py"""
        print("\n🧪 TESTING MAIN.PY APPROACH")
        print("-" * 40)
        
        try:
            # Use main.py's direct WebSocket approach
            async with websockets.connect(self.helius_ws_url) as ws:
                print("✅ Direct WebSocket connection established")
                
                # Subscribe like main.py does - to each wallet individually
                for wallet in self.target_wallets[:3]:  # Test first 3 wallets
                    subscription = {
                        "jsonrpc": "2.0",
                        "id": int(time.time() * 1000),
                        "method": "logsSubscribe",
                        "params": [
                            {"mentions": [wallet]},
                            {"commitment": "confirmed"}
                        ]
                    }
                    
                    await ws.send(json.dumps(subscription))
                    response = await ws.recv()
                    response_data = json.loads(response)
                    
                    if "result" in response_data:
                        print(f"✅ Subscribed to {wallet[:8]}... (ID: {response_data['result']})")
                    else:
                        print(f"❌ Failed to subscribe to {wallet[:8]}...")
                
                print("📡 Listening with main.py approach...")
                
                # Listen for 30 seconds
                start_time = time.time()
                while time.time() - start_time < 30:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        
                        self.message_count += 1
                        
                        # Process like main.py does
                        if "method" in data and data["method"] == "subscription":
                            params = data.get("params", {})
                            result = params.get("result", {})
                            logs = result.get("logs", [])
                            signature = result.get("signature")
                            
                            if logs and signature:
                                print(f"📥 Message {self.message_count}: {signature[:8]}... ({len(logs)} logs)")
                                
                                # Check for pump.fun patterns like main.py does
                                pump_logs = [log for log in logs if any(id in log for id in 
                                           ["BSfD6SHZ", "6EF8rrec", "pAMMBay6", "Program log: Instruction"])]
                                
                                if pump_logs:
                                    detection = {
                                        'method': 'main.py_approach',
                                        'signature': signature,
                                        'timestamp': datetime.now(),
                                        'logs_matched': pump_logs[:2],  # First 2 matching logs
                                        'total_logs': len(logs)
                                    }
                                    self.trade_detections.append(detection)
                                    print(f"🎯 MAIN.PY DETECTION: {signature[:8]}...")
                                    print(f"   Matching logs: {pump_logs[:1]}")
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error in main.py approach: {e}")
                        
        except Exception as e:
            logger.error(f"Main.py approach failed: {e}")
    
    async def test_advanced_bot_approach(self):
        """Test the detection method used in advanced_copy_trading_bot.py"""
        print("\n🧪 TESTING ADVANCED BOT APPROACH")
        print("-" * 40)
        
        try:
            # Import the bot like the test script does
            from advanced_copy_trading_bot import PumpCopyTradingBot
            
            # Create bot with minimal config
            copy_config = {
                'fixed_buy_amount': 0.001,  # Minimal for testing
                'delay_seconds': 0,
                'enable_sells': False,
                'enable_buys': False  # Disable actual trading
            }
            
            bot = PumpCopyTradingBot(copy_config)
            print("✅ PumpCopyTradingBot initialized")
            
            # Test the WebSocket approach used by the bot
            async with websockets.connect(bot.helius_ws_url) as ws:
                print("✅ Bot-style WebSocket connection established")
                
                # Subscribe like the bot does - all wallets at once
                for wallet in self.target_wallets[:3]:
                    subscription = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "logsSubscribe",
                        "params": [
                            {"mentions": [wallet]},
                            {"commitment": "confirmed"}
                        ]
                    }
                    await ws.send(json.dumps(subscription))
                    print(f"✅ Bot-style subscription sent for {wallet[:8]}...")
                
                print("📡 Listening with advanced bot approach...")
                
                # Listen for 30 seconds
                start_time = time.time()
                advanced_messages = 0
                
                while time.time() - start_time < 30:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        
                        advanced_messages += 1
                        
                        # Process like the advanced bot does
                        result = data.get("params", {}).get("result", {})
                        logs = result.get("value", {}).get("logs", [])
                        signature = result.get("value", {}).get("signature")
                        
                        if logs and signature:
                            print(f"📥 Advanced Message {advanced_messages}: {signature[:8]}... ({len(logs)} logs)")
                            
                            # Test ultra-fast detection like the bot does
                            for wallet in self.target_wallets:
                                wallet_in_logs = any(wallet in log for log in logs)
                                if wallet_in_logs:
                                    # Test the _ultra_fast_log_detection patterns
                                    fast_result = self._test_ultra_fast_detection(logs, wallet, signature)
                                    if fast_result:
                                        detection = {
                                            'method': 'advanced_bot_approach',
                                            'signature': signature,
                                            'timestamp': datetime.now(),
                                            'detection_result': fast_result,
                                            'total_logs': len(logs)
                                        }
                                        self.trade_detections.append(detection)
                                        print(f"🚀 ADVANCED BOT DETECTION: {signature[:8]}...")
                                        print(f"   Result: {fast_result}")
                                        break
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error in advanced bot approach: {e}")
        
        except Exception as e:
            logger.error(f"Advanced bot approach failed: {e}")
    
    def _test_ultra_fast_detection(self, logs, wallet, signature):
        """Test the ultra-fast detection logic"""
        try:
            # Test the patterns used in _ultra_fast_log_detection
            pump_instruction = None
            token_mint = None
            
            for log in logs:
                # Test for pump trade instructions
                if any(pattern in log for pattern in [
                    "Program log: Instruction: PumpBuy",
                    "Program log: Instruction: Buy",
                    "Program log: Instruction: PumpAmmSwap"
                ]):
                    pump_instruction = "BUY"
                elif any(pattern in log for pattern in [
                    "Program log: Instruction: PumpSell", 
                    "Program log: Instruction: Sell",
                    "Program log: Instruction: PumpAmmSell"
                ]):
                    pump_instruction = "SELL"
                elif "Program log: Token:" in log:
                    try:
                        token_mint = log.split("Program log: Token: ")[1].strip()
                    except:
                        continue
            
            if pump_instruction:
                return {
                    'instruction': pump_instruction,
                    'token_mint': token_mint[:8] + "..." if token_mint else None,
                    'wallet': wallet[:8] + "..."
                }
            
            # Test for program patterns
            pump_programs = [
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
                "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",
                "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
            ]
            
            for log in logs:
                for prog in pump_programs:
                    if f"Program {prog} invoke" in log:
                        return {
                            'instruction': 'PROGRAM_INVOKE',
                            'program': prog[:8] + "...",
                            'wallet': wallet[:8] + "..."
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in ultra-fast detection test: {e}")
            return None
    
    def print_comparison_results(self):
        """Print comparison results"""
        print("\n📊 DETECTION COMPARISON RESULTS")
        print("=" * 60)
        print(f"📥 Total messages received: {self.message_count}")
        print(f"🎯 Total detections: {len(self.trade_detections)}")
        
        if self.trade_detections:
            print("\n🔍 DETECTION BREAKDOWN:")
            print("-" * 30)
            
            main_py_detections = [d for d in self.trade_detections if d['method'] == 'main.py_approach']
            bot_detections = [d for d in self.trade_detections if d['method'] == 'advanced_bot_approach']
            
            print(f"   main.py approach: {len(main_py_detections)} detections")
            print(f"   advanced bot approach: {len(bot_detections)} detections")
            
            # Show recent detections
            if self.trade_detections:
                print("\n📋 RECENT DETECTIONS:")
                for i, detection in enumerate(self.trade_detections[-5:], 1):
                    print(f"   {i}. {detection['method']}: {detection['signature'][:8]}... at {detection['timestamp'].strftime('%H:%M:%S')}")
        else:
            print("❌ No detections found with either approach")
            print("💡 This suggests the issue might be:")
            print("   1. Low trading activity during test period")
            print("   2. Different WebSocket message formats")
            print("   3. Subscription setup differences")
        
        print("\n🔍 KEY DIFFERENCES IDENTIFIED:")
        print("-" * 40)
        print("1. WEBSOCKET SUBSCRIPTION FORMAT:")
        print("   main.py: Uses individual subscription IDs and full result parsing")
        print("   test bot: Uses simplified subscription and result.value parsing")
        print()
        print("2. MESSAGE PROCESSING:")
        print("   main.py: Checks data.method == 'subscription' first")
        print("   test bot: Directly accesses data.params.result.value")
        print()
        print("3. LOG PATTERN MATCHING:")
        print("   main.py: Simple substring check (BSfD6SHZ, 6EF8rrec)")
        print("   test bot: Complex pattern matching with multiple approaches")

async def main():
    """Run the comparison test"""
    print("🔬 STARTING DETECTION METHOD COMPARISON")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    comparison = DetectionComparison()
    
    # Test main.py approach first
    await comparison.test_main_py_approach()
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Test advanced bot approach
    await comparison.test_advanced_bot_approach()
    
    # Print results
    comparison.print_comparison_results()

if __name__ == "__main__":
    asyncio.run(main())
