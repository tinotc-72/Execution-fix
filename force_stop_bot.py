#!/usr/bin/env python3
"""
🚨 FORCE STOP BOT - Comprehensive bot stopping script
This script will forcefully stop all trading bot processes
"""

import os
import signal
import subprocess
import time
import sys

def force_stop_all_bots():
    """🚨 FORCE STOP: Kill all trading bot processes using multiple methods"""
    print("🚨 FORCE STOP: Killing all trading bot processes...")
    
    stopped_processes = 0
    
    # Method 1: Kill by process name patterns
    process_patterns = [
        'main.py',
        'copy_trading',
        'trading_bot',
        'python.*main.py',
        'python3.*main.py'
    ]
    
    for pattern in process_patterns:
        try:
            print(f"🔍 Searching for processes matching: {pattern}")
            result = subprocess.run(['pgrep', '-f', pattern], capture_output=True, text=True)
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip():
                        try:
                            pid_num = int(pid.strip())
                            print(f"🔥 Killing PID {pid_num} (pattern: {pattern})")
                            os.kill(pid_num, signal.SIGKILL)
                            stopped_processes += 1
                        except (ValueError, ProcessLookupError, PermissionError) as e:
                            print(f"⚠️ Could not kill PID {pid}: {e}")
                            
        except FileNotFoundError:
            # pgrep not available, try pkill
            try:
                subprocess.run(['pkill', '-9', '-f', pattern], capture_output=True)
                print(f"🔥 pkill executed for pattern: {pattern}")
                stopped_processes += 1
            except Exception as e:
                print(f"⚠️ pkill failed for {pattern}: {e}")
    
    # Method 2: Find and kill Python processes running main.py
    try:
        print("🔍 Searching for Python processes...")
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'python' in line and 'main.py' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1])
                        print(f"🔥 Killing Python main.py process PID {pid}")
                        os.kill(pid, signal.SIGKILL)
                        stopped_processes += 1
                    except (ValueError, ProcessLookupError, PermissionError) as e:
                        print(f"⚠️ Could not kill Python process {parts[1]}: {e}")
                        
    except Exception as e:
        print(f"⚠️ Error in Python process search: {e}")
    
    # Method 3: Kill processes by port (if WebSocket is running on specific port)
    websocket_ports = [8080, 8765, 9001, 8001]  # Common WebSocket ports
    for port in websocket_ports:
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid.strip():
                        try:
                            pid_num = int(pid.strip())
                            print(f"🔥 Killing process using port {port}: PID {pid_num}")
                            os.kill(pid_num, signal.SIGKILL)
                            stopped_processes += 1
                        except (ValueError, ProcessLookupError, PermissionError) as e:
                            print(f"⚠️ Could not kill port process {pid}: {e}")
        except FileNotFoundError:
            pass  # lsof not available
        except Exception as e:
            print(f"⚠️ Error checking port {port}: {e}")
    
    # Method 4: Nuclear option - kill all Python processes with trading keywords
    try:
        print("🔍 Nuclear scan for trading-related Python processes...")
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        trading_keywords = ['copy_trading', 'trading_bot', 'jito', 'solana', 'pump.fun', 'jupiter']
        
        for line in lines:
            if 'python' in line.lower():
                line_lower = line.lower()
                for keyword in trading_keywords:
                    if keyword in line_lower and 'grep' not in line_lower:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                pid = int(parts[1])
                                print(f"🔥 Nuclear kill - trading Python process PID {pid} ({keyword})")
                                os.kill(pid, signal.SIGKILL)
                                stopped_processes += 1
                                break
                            except (ValueError, ProcessLookupError, PermissionError) as e:
                                print(f"⚠️ Nuclear kill failed for {parts[1]}: {e}")
                                
    except Exception as e:
        print(f"⚠️ Error in nuclear scan: {e}")
    
    print(f"✅ FORCE STOP COMPLETED: {stopped_processes} processes terminated")
    
    # Verify no trading processes are left
    time.sleep(1)
    try:
        result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️ WARNING: Some main.py processes may still be running:")
            print(result.stdout.strip())
        else:
            print("✅ VERIFIED: No main.py processes detected")
    except:
        print("ℹ️ Could not verify process termination (pgrep not available)")

def main():
    """Main execution"""
    print("🚨" * 20)
    print("🚨 FORCE STOP BOT SCRIPT")
    print("🚨 This will terminate ALL trading bot processes")
    print("🚨" * 20)
    
    # Check if running with sudo (might be needed for some processes)
    if os.geteuid() != 0:
        print("ℹ️ Running without sudo - some processes may not be killable")
    
    force_stop_all_bots()
    
    print("\n🎯 If processes are still running, try:")
    print("   sudo python3 force_stop_bot.py")
    print("   or manually kill with: sudo pkill -9 -f main.py")

if __name__ == "__main__":
    main()
