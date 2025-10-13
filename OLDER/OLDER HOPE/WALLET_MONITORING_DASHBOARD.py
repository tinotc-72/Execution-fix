#!/usr/bin/env python3
"""
WALLET MONITORING DASHBOARD
Displays all monitored wallets with Solscan links and real-time activity monitoring
"""

import os
import time
from datetime import datetime
import subprocess
import threading
from config import MONITORED_WALLETS

def print_header():
    """Print a beautiful header"""
    print("\n" + "="*80)
    print("🚀 AXIOM SNIPER - COPY TRADING BOT DASHBOARD")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def display_monitored_wallets():
    """Display all monitored wallets with Solscan links"""
    print("\n📊 MONITORED WALLETS (7 TOTAL)")
    print("-" * 80)
    
    wallet_descriptions = [
        "Your Original Wallet #1",
        "Your Original Wallet #2", 
        "🔥 ACTIVE TRADER - High Volume",
        "⚡ SPEED TRADER - High Frequency",
        "💎 VOLUME TRADER - Large Positions",
        "🎯 PUMP SPECIALIST - Active Trader",
        "🚀 FREQUENT TRADER - Regular Activity"
    ]
    
    for i, (wallet, description) in enumerate(zip(MONITORED_WALLETS, wallet_descriptions), 1):
        print(f"{i}. {description}")
        print(f"   📍 Address: {wallet}")
        print(f"   🔗 Solscan: https://solscan.io/account/{wallet}")
        print(f"   📈 Portfolio: https://solscan.io/account/{wallet}#portfolio")
        print()

def get_log_files():
    """Get all relevant log files"""
    log_files = []
    for file in ['LIVE_COPY_TEST.log', 'copy_trading.log', 'debug.log', 'trades.log']:
        if os.path.exists(file):
            log_files.append(file)
    return log_files

def tail_logs_combined():
    """Tail all log files and highlight important events"""
    log_files = get_log_files()
    if not log_files:
        print("❌ No log files found!")
        return
    
    print(f"\n📋 MONITORING LOG FILES: {', '.join(log_files)}")
    print("-" * 80)
    
    # Create tail command for all log files
    cmd = ['tail', '-f'] + log_files
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                 universal_newlines=True, bufsize=1)
        
        for line in iter(process.stdout.readline, ""):
            if line.strip():
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Highlight important events
                if any(keyword in line.lower() for keyword in ['trade', 'buy', 'sell', 'copy', 'detected']):
                    print(f"🔥 [{timestamp}] {line.strip()}")
                elif any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                    print(f"❌ [{timestamp}] {line.strip()}")
                elif any(keyword in line.lower() for keyword in ['success', 'completed', 'executed']):
                    print(f"✅ [{timestamp}] {line.strip()}")
                elif 'websocket' in line.lower() or 'connected' in line.lower():
                    print(f"🔗 [{timestamp}] {line.strip()}")
                else:
                    print(f"📝 [{timestamp}] {line.strip()}")
                    
    except KeyboardInterrupt:
        print("\n⏹️  Log monitoring stopped")
        process.terminate()
    except Exception as e:
        print(f"❌ Error monitoring logs: {e}")

def check_bot_status():
    """Check if the bot is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        bot_processes = []
        
        for line in result.stdout.split('\n'):
            if 'LIVE_COPY_TEST' in line or 'advanced_copy' in line:
                if 'grep' not in line:
                    bot_processes.append(line.strip())
        
        if bot_processes:
            print(f"\n✅ BOT STATUS: RUNNING ({len(bot_processes)} processes)")
            for i, process in enumerate(bot_processes, 1):
                parts = process.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    print(f"   Process {i}: PID {pid}")
        else:
            print("\n❌ BOT STATUS: NOT RUNNING")
            
    except Exception as e:
        print(f"❌ Error checking bot status: {e}")

def monitor_activity():
    """Main monitoring function"""
    print_header()
    display_monitored_wallets()
    check_bot_status()
    
    print("\n🎯 STARTING REAL-TIME LOG MONITORING...")
    print("💡 Press Ctrl+C to stop monitoring")
    print("="*80)
    
    tail_logs_combined()

if __name__ == "__main__":
    try:
        monitor_activity()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")
