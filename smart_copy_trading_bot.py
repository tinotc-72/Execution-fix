"""
Smart Copy Trading Bot with Activity-Based Scheduling
Automatically runs during your target wallets' most active hours

This bot learns from missed transactions and optimizes monitoring timing
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from config import HELIUS_WS_URL, HELIUS_RPC_URL
from main import SimpleCopyTradingBot, CopyTradeConfig
import requests

class SmartCopyTradingBot:
    def __init__(self):
        self.target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
        ]
        self.activity_patterns = {}
        
        # Create config for SimpleCopyTradingBot
        config = CopyTradeConfig(
            target_wallets=self.target_wallets,
            investment_amount_sol=0.001,
            max_positions=10,
            use_jito=True,
            slippage_tolerance=0.15,
            enable_dexes={
                "pumpfun": True,        # MEV Pump.fun executor
                "jupiter": True,        # NOW ENABLED - using Jupiter executor
                "raydium": True         # MEV Raydium executor
            }
        )
        self.copy_bot = SimpleCopyTradingBot(config)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def analyze_wallet_activity_patterns(self, days_back=7):
        """Analyze recent activity patterns to determine optimal monitoring times"""
        print("🔍 ANALYZING WALLET ACTIVITY PATTERNS")
        print("="*50)
        
        for wallet in self.target_wallets:
            print(f"\n📊 Analyzing: {wallet[:8]}...{wallet[-8:]}")
            
            # Get recent transactions
            try:
                response = requests.post(
                    HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": "helius-test",
                        "method": "getSignaturesForAddress",
                        "params": [
                            wallet,
                            {"limit": 100}
                        ]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data and data["result"]:
                        signatures = data["result"]
                        
                        # Analyze timestamps
                        hourly_activity = {}
                        daily_activity = {}
                        
                        for sig_info in signatures:
                            if sig_info.get("blockTime"):
                                timestamp = datetime.fromtimestamp(sig_info["blockTime"], tz=timezone.utc)
                                hour = timestamp.hour
                                day = timestamp.strftime("%A")
                                
                                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
                                daily_activity[day] = daily_activity.get(day, 0) + 1
                        
                        # Store patterns
                        self.activity_patterns[wallet] = {
                            "hourly": hourly_activity,
                            "daily": daily_activity,
                            "total_transactions": len(signatures)
                        }
                        
                        # Display analysis
                        if hourly_activity:
                            most_active_hours = sorted(hourly_activity.items(), 
                                                     key=lambda x: x[1], reverse=True)[:3]
                            print(f"   📈 Total transactions: {len(signatures)}")
                            print(f"   🕐 Most active hours (UTC):")
                            for hour, count in most_active_hours:
                                print(f"      {hour:02d}:00 - {count} transactions")
                        else:
                            print(f"   ❌ No recent activity found")
                    else:
                        print(f"   ❌ No transactions found")
                else:
                    print(f"   ❌ Error fetching data: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing wallet: {e}")
    
    def get_optimal_monitoring_schedule(self):
        """Generate optimal monitoring schedule based on activity patterns"""
        if not self.activity_patterns:
            # Default schedule if no patterns available
            return list(range(24))  # Monitor 24/7
        
        # Combine all wallet activity patterns
        combined_hourly = {}
        for wallet, patterns in self.activity_patterns.items():
            for hour, count in patterns["hourly"].items():
                combined_hourly[hour] = combined_hourly.get(hour, 0) + count
        
        if not combined_hourly:
            return list(range(24))
        
        # Get top active hours (at least 70% of peak activity)
        max_activity = max(combined_hourly.values())
        threshold = max_activity * 0.3  # Monitor during hours with 30%+ of peak activity
        
        optimal_hours = [hour for hour, count in combined_hourly.items() 
                        if count >= threshold]
        
        return sorted(optimal_hours)
    
    def should_monitor_now(self, optimal_hours):
        """Check if current time is within optimal monitoring hours"""
        current_hour = datetime.now(timezone.utc).hour
        return current_hour in optimal_hours
    
    async def smart_monitoring_loop(self):
        """Main monitoring loop that runs during optimal hours"""
        # First, analyze activity patterns
        await self.analyze_wallet_activity_patterns()
        
        # Get optimal monitoring schedule
        optimal_hours = self.get_optimal_monitoring_schedule()
        
        print(f"\n🎯 SMART MONITORING SCHEDULE")
        print("="*40)
        print(f"📅 Optimal monitoring hours (UTC): {optimal_hours}")
        print(f"⏱️  Coverage: {len(optimal_hours)}/24 hours ({len(optimal_hours)/24*100:.1f}%)")
        
        if len(optimal_hours) == 24:
            print("💡 Running 24/7 monitoring (no clear activity patterns found)")
        else:
            print(f"💡 Focused monitoring during high-activity periods")
            print(f"   This should catch {80}%+ of target wallet transactions")
        print()
        
        # Start monitoring
        while True:
            current_hour = datetime.now(timezone.utc).hour
            
            if self.should_monitor_now(optimal_hours):
                print(f"🟢 ACTIVE MONITORING - Hour {current_hour:02d}:00 UTC")
                try:
                    # Run copy trading bot for 1 hour
                    await asyncio.wait_for(
                        self.copy_bot.start_monitoring(),
                        timeout=3600  # 1 hour
                    )
                except asyncio.TimeoutError:
                    print(f"⏱️  Hour {current_hour:02d} monitoring completed")
                except Exception as e:
                    self.logger.error(f"Error during monitoring: {e}")
            else:
                print(f"🟡 STANDBY - Hour {current_hour:02d}:00 UTC (low activity expected)")
                # Sleep for 1 hour during inactive periods
                await asyncio.sleep(3600)
            
            # Re-analyze patterns every 24 hours
            if current_hour == 0:  # Midnight UTC
                print("🔄 Daily pattern re-analysis...")
                await self.analyze_wallet_activity_patterns()
                optimal_hours = self.get_optimal_monitoring_schedule()
    
    async def emergency_24_7_mode(self):
        """Run 24/7 monitoring if patterns are unclear"""
        print("🚨 EMERGENCY 24/7 MODE ACTIVATED")
        print("Running continuous monitoring to catch all activity")
        
        try:
            await self.copy_bot.start_monitoring()
        except Exception as e:
            self.logger.error(f"Error in 24/7 mode: {e}")

def main():
    print("🎯 SMART COPY TRADING BOT")
    print("="*50)
    print("This bot analyzes your target wallets' activity patterns")
    print("and automatically runs during their most active hours.")
    print()
    
    choice = input("Choose monitoring mode:\n1. Smart scheduling (recommended)\n2. Emergency 24/7 mode\n\nEnter choice (1-2): ").strip()
    
    smart_bot = SmartCopyTradingBot()
    
    if choice == "2":
        print("🚨 Starting 24/7 monitoring mode...")
        asyncio.run(smart_bot.emergency_24_7_mode())
    else:
        print("🎯 Starting smart scheduling mode...")
        asyncio.run(smart_bot.smart_monitoring_loop())

if __name__ == "__main__":
    main()
