#!/usr/bin/env python3
"""
Real-time WebSocket Message Analysis
Shows exactly what messages main.py receives vs test script
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

class WebSocketMessageAnalyzer:
    def __init__(self):
        self.ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        self.target_wallets = MONITORED_WALLETS[:3]  # Test with first 3 wallets
        
        # Message counters
        self.main_py_messages = 0
        self.test_bot_messages = 0
        self.main_py_format_count = 0
        self.test_bot_format_count = 0
        
        print("\n🔍 REAL-TIME WEBSOCKET MESSAGE ANALYSIS")
        print("=" * 60)
        print("🎯 Comparing message formats between:")
        print("   1. main.py approach")
        print("   2. test script approach")
        print("=" * 60)
    
    async def analyze_main_py_format(self):
        """Analyze messages using main.py format"""
        try:
            async with websockets.connect(self.ws_url) as ws:
                print("✅ main.py WebSocket connected")
                
                # Subscribe like main.py
                for i, wallet in enumerate(self.target_wallets):
                    subscription = {
                        "jsonrpc": "2.0",
                        "id": str(int(time.time() * 1000) + i),
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
                        print(f"✅ main.py subscribed to {wallet[:8]}... (ID: {response_data['result']})")
                
                print("📡 Listening with main.py format...")
                
                # Listen for 60 seconds
                start_time = time.time()
                while time.time() - start_time < 60:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        self.main_py_messages += 1
                        
                        # main.py processing
                        if "method" in data and data["method"] == "subscription":
                            params = data.get("params", {})
                            result = params.get("result", {})
                            logs = result.get("logs", [])
                            signature = result.get("signature")
                            
                            if logs and signature:
                                self.main_py_format_count += 1
                                print(f"📥 MAIN.PY #{self.main_py_format_count}: {signature[:8]}... ({len(logs)} logs)")
                                
                                # Check for pump patterns
                                pump_logs = [log for log in logs if any(id in log for id in 
                                           ["BSfD6SHZ", "6EF8rrec", "pAMMBay6"])]
                                if pump_logs:
                                    print(f"   🎯 MAIN.PY DETECTION: {pump_logs[0][:50]}...")
                        
                        # Show sample message structure every 20 messages
                        if self.main_py_messages % 20 == 1:
                            print(f"📋 main.py message structure sample:")
                            print(f"   Keys: {list(data.keys())}")
                            if "params" in data:
                                print(f"   Params keys: {list(data['params'].keys())}")
                                if "result" in data['params']:
                                    print(f"   Result keys: {list(data['params']['result'].keys())}")
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"main.py format error: {e}")
                        
        except Exception as e:
            logger.error(f"main.py approach failed: {e}")
    
    async def analyze_test_bot_format(self):
        """Analyze messages using test bot format"""
        try:
            async with websockets.connect(self.ws_url) as ws:
                print("✅ test bot WebSocket connected")
                
                # Subscribe like test bot
                for wallet in self.target_wallets:
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
                    print(f"✅ test bot subscribed to {wallet[:8]}...")
                
                print("📡 Listening with test bot format...")
                
                # Listen for 60 seconds
                start_time = time.time()
                while time.time() - start_time < 60:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(msg)
                        self.test_bot_messages += 1
                        
                        # test bot processing (advanced_copy_trading_bot style)
                        result = data.get("params", {}).get("result", {})
                        logs = result.get("value", {}).get("logs", [])
                        signature = result.get("value", {}).get("signature")
                        
                        if logs and signature:
                            self.test_bot_format_count += 1
                            print(f"📥 TEST BOT #{self.test_bot_format_count}: {signature[:8]}... ({len(logs)} logs)")
                            
                            # Check for patterns
                            for wallet in self.target_wallets:
                                wallet_in_logs = any(wallet in log for log in logs)
                                if wallet_in_logs:
                                    print(f"   🎯 TEST BOT DETECTION from {wallet[:8]}...")
                        
                        # Show sample message structure every 20 messages
                        if self.test_bot_messages % 20 == 1:
                            print(f"📋 test bot message structure sample:")
                            print(f"   Keys: {list(data.keys())}")
                            if "params" in data:
                                print(f"   Params keys: {list(data['params'].keys())}")
                                if "result" in data['params']:
                                    result_keys = list(data['params']['result'].keys())
                                    print(f"   Result keys: {result_keys}")
                                    if "value" in data['params']['result']:
                                        value_keys = list(data['params']['result']['value'].keys())
                                        print(f"   Value keys: {value_keys}")
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"test bot format error: {e}")
                        
        except Exception as e:
            logger.error(f"test bot approach failed: {e}")
    
    def print_analysis_results(self):
        """Print analysis results"""
        print(f"\n📊 WEBSOCKET MESSAGE ANALYSIS RESULTS")
        print("=" * 60)
        print(f"📥 main.py total messages: {self.main_py_messages}")
        print(f"📥 test bot total messages: {self.test_bot_messages}")
        print(f"🎯 main.py valid trade messages: {self.main_py_format_count}")
        print(f"🎯 test bot valid trade messages: {self.test_bot_format_count}")
        
        print(f"\n🔍 KEY FINDINGS:")
        print("-" * 30)
        
        if self.main_py_format_count > self.test_bot_format_count:
            print(f"✅ main.py format is MORE EFFECTIVE:")
            print(f"   - main.py processed {self.main_py_format_count} valid messages")
            print(f"   - test bot processed {self.test_bot_format_count} valid messages")
            print(f"   - Difference: {self.main_py_format_count - self.test_bot_format_count} messages")
            print(f"\n💡 RECOMMENDATION:")
            print(f"   Use main.py message processing approach:")
            print(f"   data['method'] == 'subscription' and data['params']['result']")
        elif self.test_bot_format_count > self.main_py_format_count:
            print(f"✅ test bot format is MORE EFFECTIVE:")
            print(f"   - test bot processed {self.test_bot_format_count} valid messages")
            print(f"   - main.py processed {self.main_py_format_count} valid messages")
            print(f"   - Difference: {self.test_bot_format_count - self.main_py_format_count} messages")
            print(f"\n💡 RECOMMENDATION:")
            print(f"   Use test bot message processing approach:")
            print(f"   data['params']['result']['value']")
        else:
            print(f"⚖️ Both formats performed equally")
            print(f"   Both processed {self.main_py_format_count} valid messages")
        
        if self.main_py_format_count == 0 and self.test_bot_format_count == 0:
            print(f"\n❌ NO VALID MESSAGES DETECTED BY EITHER APPROACH")
            print(f"💡 This suggests:")
            print(f"   1. No trading activity during test period")
            print(f"   2. WebSocket subscription issues")
            print(f"   3. Message format has changed")
            print(f"   4. Need to test with more active wallets")

async def main():
    """Run the message analysis"""
    print("🔬 STARTING REAL-TIME MESSAGE ANALYSIS")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⏱️ Test duration: 60 seconds per approach")
    
    analyzer = WebSocketMessageAnalyzer()
    
    print("\n🧪 PHASE 1: Testing main.py approach...")
    await analyzer.analyze_main_py_format()
    
    print("\n⏸️ Brief pause between tests...")
    await asyncio.sleep(3)
    
    print("\n🧪 PHASE 2: Testing advanced bot approach...")
    await analyzer.analyze_test_bot_format()
    
    analyzer.print_analysis_results()

if __name__ == "__main__":
    asyncio.run(main())
