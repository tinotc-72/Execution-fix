#!/usr/bin/env python3
"""
IMMEDIATE TRADE DETECTOR - Catches ALL trades from monitored wallets
Uses the simplest possible detection to ensure we catch everything
"""

import asyncio
import json
import logging
import time
from datetime import datetime
import websockets
from config import MONITORED_WALLETS
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImmediateTradeDetector:
    def __init__(self):
        self.ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        self.target_wallets = MONITORED_WALLETS
        self.running = False
        
        # Statistics
        self.messages_received = 0
        self.trades_detected = 0
        self.start_time = datetime.now()
        
        print("\n🚨 IMMEDIATE TRADE DETECTOR")
        print("=" * 50)
        print("🎯 GOAL: Detect ANY trade from monitored wallets")
        print("📡 METHOD: Catch ALL WebSocket notifications")
        print("🔍 PATTERN: ANY transaction with logs")
        print("=" * 50)
    
    async def start_detecting(self):
        """Start immediate detection"""
        logger.info("🚀 Starting immediate trade detector...")
        
        self.running = True
        self.start_time = datetime.now()
        
        try:
            async with websockets.connect(self.ws_url) as ws:
                logger.info("✅ WebSocket connected")
                
                # Subscribe to all wallets
                subscription_ids = {}
                
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
                        subscription_id = response_data["result"]
                        subscription_ids[subscription_id] = wallet
                        logger.info(f"✅ Subscribed to {wallet[:8]}... (ID: {subscription_id})")
                    else:
                        logger.error(f"❌ Failed to subscribe to {wallet[:8]}...")
                
                logger.info(f"📡 Monitoring {len(subscription_ids)} wallets for ANY transactions...")
                
                # Listen for ALL messages
                async for message in ws:
                    try:
                        data = json.loads(message)
                        self.messages_received += 1
                        
                        # Check for any subscription notifications
                        if "method" in data and data["method"] == "logsNotification":
                            await self.process_notification(data, subscription_ids)
                        elif "method" in data and data["method"] == "subscription":
                            # Also check main.py format
                            await self.process_subscription(data, subscription_ids)
                        
                        # Status every 25 messages
                        if self.messages_received % 25 == 0:
                            logger.info(f"📊 {self.messages_received} messages, {self.trades_detected} trades detected")
                    
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
    
    async def process_notification(self, data: dict, subscription_ids: dict):
        """Process logsNotification format"""
        try:
            params = data.get("params", {})
            result = params.get("result", {})
            
            if "value" in result:
                value = result["value"]
                signature = value.get("signature")
                logs = value.get("logs", [])
                subscription = params.get("subscription")
                
                if signature and logs and subscription:
                    # Find which wallet this is from
                    wallet = subscription_ids.get(subscription, "Unknown")
                    
                    self.trades_detected += 1
                    
                    # Show immediate alert
                    await self.show_trade_alert(signature, wallet, logs, "logsNotification")
                    
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
    
    async def process_subscription(self, data: dict, subscription_ids: dict):
        """Process main.py subscription format"""
        try:
            params = data.get("params", {})
            subscription = params.get("subscription")
            result = params.get("result", {})
            
            if subscription and result:
                signature = result.get("signature")
                logs = result.get("logs", [])
                
                if signature and logs:
                    # Find which wallet this is from
                    wallet = subscription_ids.get(subscription, "Unknown")
                    
                    self.trades_detected += 1
                    
                    # Show immediate alert
                    await self.show_trade_alert(signature, wallet, logs, "subscription")
                    
        except Exception as e:
            logger.error(f"Error processing subscription: {e}")
    
    async def show_trade_alert(self, signature: str, wallet: str, logs: list, format_type: str):
        """Show immediate trade alert"""
        print(f"\n🚨 TRADE DETECTED #{self.trades_detected} 🚨")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"📝 Signature: {signature}")
        print(f"👤 Wallet: {wallet[:8]}...")
        print(f"📋 Format: {format_type}")
        print(f"📊 Logs: {len(logs)} entries")
        
        # Show first few log entries
        print("🔍 Log samples:")
        for i, log in enumerate(logs[:3]):
            print(f"   {i+1}. {log[:80]}...")
        
        # Analyze what DEX this might be
        dex_analysis = self.analyze_dex(logs)
        if dex_analysis:
            print(f"🏦 Detected DEX: {dex_analysis}")
        
        print(f"🔗 Solscan: https://solscan.io/tx/{signature}")
        print("-" * 60)
        
        # Write to log file
        with open("IMMEDIATE_TRADE_DETECTIONS.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}: {signature} from {wallet[:8]}... via {format_type} ({len(logs)} logs)\n")
        
        # System sound
        try:
            import os
            os.system("afplay /System/Library/Sounds/Ping.aiff &")
        except:
            pass
    
    def analyze_dex(self, logs: list) -> str:
        """Quick DEX analysis"""
        log_text = " ".join(logs)
        
        if "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8" in log_text:
            return "RAYDIUM"
        elif "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc" in log_text:
            return "ORCA"
        elif "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4" in log_text:
            return "JUPITER"
        elif "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P" in log_text:
            return "PUMP.FUN"
        elif "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW" in log_text:
            return "PUMP.FUN (Router)"
        elif "phoenixV1FXSuGbBt5HaXHtq2Z5oaQP5bFVbUrJZzFBCdx" in log_text:
            return "PHOENIX"
        elif "srmqPiDuMkE9LjK1JJNSvSfX8T7Ym" in log_text:
            return "SERUM/OPENBOOK"
        else:
            return f"UNKNOWN (contains: {log_text[:50]}...)"
    
    def print_final_stats(self):
        """Print final statistics"""
        uptime = datetime.now() - self.start_time
        
        print(f"\n📊 IMMEDIATE DETECTION RESULTS")
        print("=" * 50)
        print(f"⏱️  Runtime: {uptime}")
        print(f"📥 Messages: {self.messages_received}")
        print(f"🎯 Trades Detected: {self.trades_detected}")
        
        if self.messages_received > 0:
            detection_rate = (self.trades_detected / self.messages_received) * 100
            print(f"📈 Detection Rate: {detection_rate:.2f}%")
        
        print("📝 Check IMMEDIATE_TRADE_DETECTIONS.log for full history")
        print("=" * 50)

async def main():
    """Run immediate detection"""
    detector = None
    try:
        detector = ImmediateTradeDetector()
        
        print("🚀 Starting immediate trade detection...")
        print("📋 This will catch ANY transaction from monitored wallets")
        print("⚡ Press Ctrl+C to stop and see results")
        print()
        
        await detector.start_detecting()
        
    except KeyboardInterrupt:
        print("\n👋 Detection stopped by user")
    except Exception as e:
        print(f"❌ Detection failed: {e}")
    finally:
        if detector:
            detector.print_final_stats()

if __name__ == "__main__":
    asyncio.run(main())
