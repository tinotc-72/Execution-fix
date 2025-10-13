"""
Enhanced Wallet Activity Monitor
Tracks when your target wallets are most active for optimal copy trading timing

Features:
- 24/7 activity tracking
- Activity pattern analysis
- Optimal monitoring time recommendations
- Historical activity logging
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime, timezone
from collections import defaultdict
from config import HELIUS_WS_URL

# Target wallets to monitor
TARGET_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
    "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
]

class WalletActivityMonitor:
    def __init__(self):
        self.activity_log = defaultdict(list)  # wallet -> [timestamps]
        self.hourly_stats = defaultdict(lambda: defaultdict(int))  # wallet -> {hour: count}
        self.start_time = datetime.now(timezone.utc)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('wallet_activity.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def monitor_wallets(self, duration_hours=24):
        """Monitor wallet activity for specified duration"""
        print(f"🎯 WALLET ACTIVITY MONITOR")
        print(f"{'='*60}")
        print(f"📊 Monitoring {len(TARGET_WALLETS)} wallets for {duration_hours} hours")
        print(f"🕐 Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"📝 Activity will be logged to: wallet_activity.log")
        print()
        
        try:
            async with websockets.connect(HELIUS_WS_URL) as websocket:
                print("✅ Connected to WebSocket")
                
                # Subscribe to all target wallets
                subscription_id = 1
                for wallet in TARGET_WALLETS:
                    subscribe_message = {
                        "jsonrpc": "2.0",
                        "id": subscription_id,
                        "method": "logsSubscribe",
                        "params": [
                            {"mentions": [wallet]},
                            {"commitment": "processed"}
                        ]
                    }
                    await websocket.send(json.dumps(subscribe_message))
                    print(f"📡 Subscribed to wallet: {wallet[:8]}...{wallet[-8:]}")
                    subscription_id += 1
                
                print(f"\n🔍 Monitoring for {duration_hours} hours...")
                print("(Press Ctrl+C to stop early and see results)")
                
                end_time = datetime.now(timezone.utc).timestamp() + (duration_hours * 3600)
                
                while datetime.now(timezone.utc).timestamp() < end_time:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        await self.process_message(json.loads(message))
                    except asyncio.TimeoutError:
                        # Print periodic updates
                        elapsed_hours = (datetime.now(timezone.utc) - self.start_time).seconds / 3600
                        if int(elapsed_hours * 4) % 4 == 0:  # Every 15 minutes
                            self.print_status_update()
                        continue
                    except KeyboardInterrupt:
                        print("\n⏹️ Monitoring stopped by user")
                        break
                        
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
            
        finally:
            await self.generate_report()
    
    async def process_message(self, message):
        """Process incoming WebSocket messages"""
        if "params" in message and "result" in message["params"]:
            result = message["params"]["result"]
            if "value" in result and "logs" in result["value"]:
                # Extract transaction signature for logging
                signature = result["value"].get("signature", "unknown")
                timestamp = datetime.now(timezone.utc)
                
                # Determine which wallet this activity belongs to
                logs = result["value"]["logs"]
                for i, wallet in enumerate(TARGET_WALLETS):
                    if any(wallet in log for log in logs if log):
                        self.activity_log[wallet].append(timestamp)
                        self.hourly_stats[wallet][timestamp.hour] += 1
                        
                        self.logger.info(f"💰 Activity detected: {wallet[:8]}...{wallet[-8:]} | {signature[:12]}... | {timestamp.strftime('%H:%M:%S')}")
                        print(f"[{timestamp.strftime('%H:%M:%S')}] 💰 Wallet {i+1} activity: {signature[:12]}...")
                        break
    
    def print_status_update(self):
        """Print periodic status updates"""
        elapsed = datetime.now(timezone.utc) - self.start_time
        total_activity = sum(len(activities) for activities in self.activity_log.values())
        
        print(f"\n📊 STATUS UPDATE - Elapsed: {elapsed.seconds//3600}h {(elapsed.seconds%3600)//60}m")
        print(f"   Total activities detected: {total_activity}")
        for i, wallet in enumerate(TARGET_WALLETS):
            count = len(self.activity_log[wallet])
            print(f"   Wallet {i+1}: {count} activities")
        print()
    
    async def generate_report(self):
        """Generate comprehensive activity report"""
        print(f"\n📈 WALLET ACTIVITY REPORT")
        print(f"{'='*60}")
        
        total_duration = datetime.now(timezone.utc) - self.start_time
        print(f"⏱️  Monitoring Duration: {total_duration}")
        print(f"📊 Total Activities Detected: {sum(len(activities) for activities in self.activity_log.values())}")
        print()
        
        # Per-wallet analysis
        for i, wallet in enumerate(TARGET_WALLETS):
            activities = self.activity_log[wallet]
            hourly = self.hourly_stats[wallet]
            
            print(f"🎯 WALLET {i+1}: {wallet[:8]}...{wallet[-8:]}")
            print(f"   📈 Total Activities: {len(activities)}")
            
            if activities:
                # Find most active hours
                if hourly:
                    most_active_hour = max(hourly.keys(), key=lambda x: hourly[x])
                    print(f"   🕐 Most Active Hour: {most_active_hour:02d}:00 UTC ({hourly[most_active_hour]} activities)")
                
                # Activity distribution
                print(f"   📊 Hourly Distribution:")
                for hour in sorted(hourly.keys()):
                    bar = "█" * min(hourly[hour], 20)
                    print(f"      {hour:02d}:00: {bar} ({hourly[hour]})")
                
                # Recommendations
                active_hours = [h for h, count in hourly.items() if count > 0]
                if active_hours:
                    print(f"   💡 Recommended monitoring hours: {sorted(active_hours)}")
            else:
                print(f"   ❌ No activity detected during monitoring period")
            print()
        
        # Overall recommendations
        print(f"🎯 COPY TRADING RECOMMENDATIONS:")
        all_active_hours = set()
        for hourly in self.hourly_stats.values():
            all_active_hours.update(hourly.keys())
        
        if all_active_hours:
            print(f"   ⏰ Best monitoring hours: {sorted(all_active_hours)}")
            print(f"   📱 Run your copy trading bot during these hours for maximum effectiveness")
        else:
            print(f"   ❌ No activity detected - try monitoring during different time periods")
            print(f"   📱 Consider running 24/7 monitoring to catch sporadic activity")
        
        print(f"\n📝 Detailed logs saved to: wallet_activity.log")

async def main():
    monitor = WalletActivityMonitor()
    
    # Ask user for monitoring duration
    print("🕐 How long should we monitor wallet activity?")
    print("1. Quick test (1 hour)")
    print("2. Half day (12 hours)")  
    print("3. Full day (24 hours)")
    print("4. Custom duration")
    
    choice = input("Enter choice (1-4): ").strip()
    
    duration_map = {"1": 1, "2": 12, "3": 24}
    
    if choice in duration_map:
        duration = duration_map[choice]
    elif choice == "4":
        try:
            duration = float(input("Enter duration in hours: "))
        except ValueError:
            duration = 24
            print("Invalid input, defaulting to 24 hours")
    else:
        duration = 24
        print("Invalid choice, defaulting to 24 hours")
    
    await monitor.monitor_wallets(duration)

if __name__ == "__main__":
    asyncio.run(main())
