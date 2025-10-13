#!/usr/bin/env python3
"""
WebSocket Diagnostic Tool - Check why transactions are being missed
"""

import asyncio
import json
import time
import websockets
from datetime import datetime
import env_keys

class WebSocketDiagnostic:
    def __init__(self):
        self.env = env_keys.EnvKeys()
        self.target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
        ]
        self.subscription_id = 1
        self.message_count = 0
        self.notifications_received = {
            'logs': 0,
            'account': 0,
            'program': 0,
            'other': 0,
            'errors': 0
        }
        
    async def run_diagnostic(self):
        """Run comprehensive WebSocket diagnostic"""
        print("🔍 WEBSOCKET DIAGNOSTIC TOOL")
        print("=" * 60)
        print(f"📡 WebSocket URL: {self.env.HELIUS_Standard_Websocket_URL}")
        print(f"👥 Target Wallets: {len(self.target_wallets)}")
        for i, wallet in enumerate(self.target_wallets, 1):
            print(f"   {i}. {wallet}")
        print("")
        
        try:
            print("🔌 Connecting to WebSocket...")
            async with websockets.connect(
                self.env.HELIUS_Standard_Websocket_URL,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            ) as websocket:
                print("✅ WebSocket connected successfully")
                
                # Setup subscriptions
                await self.setup_diagnostic_subscriptions(websocket)
                
                # Monitor for 60 seconds
                print("")
                print("📊 MONITORING FOR 60 SECONDS...")
                print("(This will show real-time activity from your target wallets)")
                print("")
                
                start_time = time.time()
                last_status = time.time()
                
                while time.time() - start_time < 60:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        self.message_count += 1
                        await self.process_diagnostic_message(message)
                        
                    except asyncio.TimeoutError:
                        # Show periodic status
                        if time.time() - last_status >= 10:
                            remaining = int(60 - (time.time() - start_time))
                            print(f"⏰ Still monitoring... {remaining}s remaining")
                            last_status = time.time()
                        continue
                
                # Final report
                await self.show_diagnostic_results()
                
        except Exception as e:
            print(f"❌ WebSocket diagnostic error: {e}")
    
    async def setup_diagnostic_subscriptions(self, websocket):
        """Setup subscriptions for diagnostic monitoring"""
        print("📡 Setting up subscriptions...")
        
        for wallet in self.target_wallets:
            # Logs subscription - this is your primary method
            logs_params = {
                "jsonrpc": "2.0",
                "id": self.subscription_id,
                "method": "logsSubscribe",
                "params": [
                    {"mentions": [wallet]},
                    {"commitment": "processed"}
                ]
            }
            await websocket.send(json.dumps(logs_params))
            print(f"   📋 Logs subscription for {wallet[:8]}...")
            self.subscription_id += 1
            
            # Account subscription for balance changes
            account_params = {
                "jsonrpc": "2.0", 
                "id": self.subscription_id,
                "method": "accountSubscribe",
                "params": [
                    wallet,
                    {"encoding": "jsonParsed", "commitment": "processed"}
                ]
            }
            await websocket.send(json.dumps(account_params))
            print(f"   💰 Account subscription for {wallet[:8]}...")
            self.subscription_id += 1
        
        print(f"✅ {self.subscription_id - 1} subscriptions sent")
        print("")
    
    async def process_diagnostic_message(self, message):
        """Process WebSocket messages for diagnostic purposes"""
        try:
            data = json.loads(message)
            
            # Skip subscription confirmations
            if "result" in data and isinstance(data["result"], int):
                print(f"✅ Subscription confirmed: ID {data['result']}")
                return
            
            # Process notifications
            if "params" in data and "result" in data["params"]:
                method = data.get("method", "")
                result = data["params"]["result"]
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if method == "logsNotification":
                    self.notifications_received['logs'] += 1
                    await self.analyze_logs_notification(result, timestamp)
                    
                elif method == "accountNotification":
                    self.notifications_received['account'] += 1
                    print(f"[{timestamp}] 💰 ACCOUNT CHANGE detected")
                    
                elif method == "programNotification":
                    self.notifications_received['program'] += 1
                    print(f"[{timestamp}] 🏢 PROGRAM NOTIFICATION detected")
                    
                else:
                    self.notifications_received['other'] += 1
                    print(f"[{timestamp}] ❓ Unknown method: {method}")
                    
        except Exception as e:
            self.notifications_received['errors'] += 1
            print(f"❌ Error processing message: {e}")
    
    async def analyze_logs_notification(self, result, timestamp):
        """Analyze logs notification in detail"""
        try:
            value = result.get("value", {})
            signature = value.get("signature", "")
            logs = value.get("logs", [])
            error = value.get("err")
            
            if error:
                print(f"[{timestamp}] ❌ FAILED TRANSACTION: {signature[:8]}...")
                return
            
            print(f"[{timestamp}] 📋 LOGS NOTIFICATION: {signature[:8]}...")
            
            if not logs:
                print(f"           ⚠️  No logs in notification")
                return
            
            log_text = ' '.join(logs).lower()
            
            # Check for target wallet involvement
            target_found = None
            for wallet in self.target_wallets:
                if wallet in log_text:
                    target_found = wallet
                    break
            
            if target_found:
                print(f"           🎯 Target wallet: {target_found[:8]}...")
                
                # Quick DEX detection
                dex_detected = []
                if 'jupiter' in log_text:
                    dex_detected.append("Jupiter")
                if 'raydium' in log_text:
                    dex_detected.append("Raydium")
                if 'pump' in log_text:
                    dex_detected.append("Pump.fun")
                if 'orca' in log_text:
                    dex_detected.append("Orca")
                if 'phoenix' in log_text:
                    dex_detected.append("Phoenix")
                
                if dex_detected:
                    print(f"           🏢 DEX detected: {', '.join(dex_detected)}")
                    
                    # Check for trade indicators
                    trade_indicators = []
                    if any(pattern in log_text for pattern in ['buy', 'swap', 'purchase']):
                        trade_indicators.append("BUY")
                    if any(pattern in log_text for pattern in ['sell', 'redeem']):
                        trade_indicators.append("SELL")
                    
                    if trade_indicators:
                        print(f"           💹 Trade type: {', '.join(trade_indicators)}")
                        print(f"           🚨 THIS SHOULD TRIGGER COPY TRADE!")
                    else:
                        print(f"           ❓ No clear trade type detected")
                else:
                    print(f"           ❓ No DEX detected")
                
                # Show sample logs for debugging
                if len(logs) > 0:
                    print(f"           📝 Sample log: {logs[0][:100]}...")
            else:
                print(f"           ❓ Target wallet not found in logs")
                
        except Exception as e:
            print(f"           ❌ Error analyzing logs: {e}")
    
    async def show_diagnostic_results(self):
        """Show final diagnostic results"""
        print("")
        print("📊 DIAGNOSTIC RESULTS")
        print("=" * 60)
        print(f"📨 Total messages received: {self.message_count}")
        print(f"📋 Logs notifications: {self.notifications_received['logs']}")
        print(f"💰 Account notifications: {self.notifications_received['account']}")
        print(f"🏢 Program notifications: {self.notifications_received['program']}")
        print(f"❓ Other notifications: {self.notifications_received['other']}")
        print(f"❌ Errors: {self.notifications_received['errors']}")
        print("")
        
        total_notifications = sum([
            self.notifications_received['logs'],
            self.notifications_received['account'], 
            self.notifications_received['program']
        ])
        
        if total_notifications == 0:
            print("🚨 CRITICAL ISSUE FOUND:")
            print("   NO NOTIFICATIONS RECEIVED FROM TARGET WALLETS")
            print("   This suggests:")
            print("   1. Target wallets are not making trades during monitoring period")
            print("   2. WebSocket subscription is not working properly")
            print("   3. RPC endpoint may have issues")
            print("")
            print("💡 RECOMMENDATIONS:")
            print("   1. Check if target wallets are active by checking recent transactions")
            print("   2. Test WebSocket connection with a known active wallet")
            print("   3. Verify RPC endpoint is working correctly")
            
        elif self.notifications_received['logs'] > 0:
            print("✅ WebSocket is receiving notifications")
            print("   If copy trades are still being missed, the issue is in:")
            print("   1. Message processing logic")
            print("   2. Trade detection algorithms")
            print("   3. Execution timing")
            
        else:
            print("⚠️  Receiving non-logs notifications")
            print("   This suggests WebSocket is working but logs subscription may have issues")

async def main():
    diagnostic = WebSocketDiagnostic()
    await diagnostic.run_diagnostic()

if __name__ == "__main__":
    asyncio.run(main())
