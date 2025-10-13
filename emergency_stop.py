#!/usr/bin/env python3
"""
🚨 EMERGENCY STOP SCRIPT 🚨
Use this script to forcefully kill all trading bot processes when normal stop methods fail
Run: python3 emergency_stop.py
"""

import os
import signal
import subprocess
import time

def emergency_kill_all():
    """Kill all trading bot processes using multiple methods"""
    print("🚨 EMERGENCY KILL ALL TRADING BOTS 🚨")
    print("=" * 50)
    
    methods_tried = 0
    methods_successful = 0
    
    # Method 1: Kill by process name (main.py)
    print("🔥 Method 1: Killing all main.py processes...")
    try:
        result = subprocess.run(['pkill', '-9', '-f', 'main.py'], capture_output=True, text=True)
        methods_tried += 1
        if result.returncode == 0:
            methods_successful += 1
            print("✅ Successfully killed main.py processes")
        else:
            print("⚠️ No main.py processes found or already terminated")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Kill by keyword "copy" or "trading"
    print("🔥 Method 2: Killing all processes with 'copy' or 'trading'...")
    try:
        subprocess.run(['pkill', '-9', '-f', 'copy'], capture_output=True)
        subprocess.run(['pkill', '-9', '-f', 'trading'], capture_output=True)
        methods_tried += 1
        methods_successful += 1
        print("✅ Killed processes with copy/trading keywords")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Kill by directory
    print("🔥 Method 3: Killing all python processes in current directory...")
    try:
        current_dir = os.getcwd()
        subprocess.run(['pkill', '-9', '-f', f'python.*{current_dir}'], capture_output=True)
        methods_tried += 1
        methods_successful += 1
        print(f"✅ Killed python processes in {current_dir}")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    # Method 4: Search and kill by PID
    print("🔥 Method 4: Finding and killing by PID...")
    try:
        # Get all python processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        killed_pids = []
        for line in lines:
            if 'python' in line.lower() and ('main.py' in line or 'copy' in line or 'trading' in line):
                parts = line.split()
                if len(parts) > 1:
                    try:
                        pid = int(parts[1])
                        os.kill(pid, signal.SIGKILL)
                        killed_pids.append(pid)
                        print(f"🔥 Killed PID {pid}: {line[:80]}...")
                    except (ValueError, ProcessLookupError):
                        pass
        
        methods_tried += 1
        if killed_pids:
            methods_successful += 1
            print(f"✅ Killed {len(killed_pids)} processes by PID")
        else:
            print("⚠️ No matching processes found by PID method")
            
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
    
    # Method 5: Kill processes using specific ports (if known)
    print("🔥 Method 5: Killing processes using WebSocket ports...")
    try:
        # Common WebSocket ports
        ports = ['8080', '8765', '9000']
        for port in ports:
            result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"🔥 Killed process {pid} using port {port}")
                    except (ValueError, ProcessLookupError):
                        pass
        methods_tried += 1
        methods_successful += 1
        print("✅ Checked and cleaned up port-based processes")
    except Exception as e:
        print(f"❌ Method 5 failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 EMERGENCY KILL COMPLETED")
    print(f"📊 Methods tried: {methods_tried}")
    print(f"✅ Methods successful: {methods_successful}")
    print(f"💀 All trading bot processes should now be terminated")
    
    # Verify no processes remain
    print("\n🔍 Verifying no trading processes remain...")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        remaining = []
        for line in result.stdout.split('\n'):
            if 'python' in line.lower() and ('main.py' in line or 'copy' in line or 'trading' in line):
                remaining.append(line[:100])
        
        if remaining:
            print(f"⚠️ WARNING: {len(remaining)} processes may still be running:")
            for proc in remaining:
                print(f"   {proc}")
        else:
            print("✅ No remaining trading processes detected")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    print("\n🚨 EMERGENCY TRADING BOT KILLER 🚨")
    print("This will forcefully terminate ALL trading bot processes")
    
    # Add a confirmation to prevent accidental execution
    response = input("\nDo you want to proceed? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        emergency_kill_all()
        print("\n🎯 If the bot is still running after this, try:")
        print("   sudo pkill -9 -f 'python.*main.py'")
        print("   or restart your terminal/computer")
    else:
        print("❌ Emergency kill cancelled")
