#!/usr/bin/env python3
"""
Real-time monitoring dashboard for copy trading bot activity
"""

import time
import os
from datetime import datetime

def monitor_activity():
    """Monitor the bot activity and highlight important events"""
    
    print("🔍 LIVE COPY TRADING MONITOR")
    print("=" * 60)
    print("📊 Watching for pump.fun trades from monitored wallets...")
    print("⚡ Will highlight any detection and copy execution")
    print()
    
    # Key phrases to highlight
    highlight_phrases = [
        "⚡ INSTANT detection:",
        "🚀 INSTANT LOG TRADE:",
        "💰 INSTANT BUY:",
        "💸 INSTANT SELL:",
        "✅ INSTANT BUY SUCCESS:",
        "✅ INSTANT SELL SUCCESS:",
        "🎉 ULTRA-FAST copy completed!",
        "❌ INSTANT EXECUTION ERROR:",
        "Program log: Instruction: PumpBuy",
        "Program log: Instruction: PumpSell"
    ]
    
    log_file = "LIVE_COPY_TEST.log"
    
    if not os.path.exists(log_file):
        print(f"⚠️ Log file {log_file} not found. Waiting for activity...")
        time.sleep(2)
    
    # Monitor the log file
    try:
        with open(log_file, 'r') as f:
            # Go to end of file
            f.seek(0, 2)
            
            print(f"🎯 Monitoring started at {datetime.now().strftime('%H:%M:%S')}")
            print("💡 Waiting for wallet activity...")
            print()
            
            while True:
                line = f.readline()
                if line:
                    # Check if this line contains important activity
                    is_important = any(phrase in line for phrase in highlight_phrases)
                    
                    if is_important:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"🚨 [{timestamp}] ACTIVITY DETECTED:")
                        print(f"    {line.strip()}")
                        print()
                    
                    # Also show general wallet activity (less prominent)
                    elif any(wallet in line for wallet in ["suqh5sHt", "DfMxre4c", "9WzDXwBb", "5Q544fKr", "7UX2i7Su", "3D49QorJ", "CuieVDED"]):
                        if "analyzing" in line or "detection" in line:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            print(f"📊 [{timestamp}] {line.strip()}")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    except Exception as e:
        print(f"❌ Error monitoring: {e}")

if __name__ == "__main__":
    monitor_activity()
