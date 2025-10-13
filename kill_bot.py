#!/usr/bin/env python3
"""
🚨 EMERGENCY KILL SCRIPT - STOP ALL TRADING BOT PROCESSES 🚨
This script forcefully terminates all Python processes related to the trading bot
"""

import os
import signal
import subprocess
import sys
import time
from typing import List, Tuple

def get_python_processes() -> List[Tuple[str, str, str]]:
    """Get all running Python processes"""
    try:
        # Get all Python processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        python_processes = []
        for line in lines:
            if 'python' in line.lower() and 'grep' not in line:
                parts = line.split()
                if len(parts) >= 11:
                    pid = parts[1]
                    command = ' '.join(parts[10:])
                    user = parts[0]
                    python_processes.append((pid, user, command))
        
        return python_processes
    except Exception as e:
        print(f"❌ Error getting processes: {e}")
        return []

def kill_process_by_pid(pid: str, force: bool = False) -> bool:
    """Kill a process by PID"""
    try:
        pid_int = int(pid)
        
        if force:
            # Force kill with SIGKILL
            os.kill(pid_int, signal.SIGKILL)
            print(f"🔥 FORCE KILLED process {pid}")
        else:
            # Graceful kill with SIGTERM
            os.kill(pid_int, signal.SIGTERM)
            print(f"⚡ Gracefully terminated process {pid}")
        
        return True
    except ProcessLookupError:
        print(f"⚠️ Process {pid} not found (already terminated)")
        return True
    except PermissionError:
        print(f"❌ Permission denied to kill process {pid}")
        return False
    except Exception as e:
        print(f"❌ Error killing process {pid}: {e}")
        return False

def kill_processes_by_name(process_names: List[str], force: bool = False) -> None:
    """Kill processes by name using pkill"""
    for name in process_names:
        try:
            if force:
                result = subprocess.run(['pkill', '-9', '-f', name], capture_output=True)
                print(f"🔥 FORCE KILLED all processes matching '{name}'")
            else:
                result = subprocess.run(['pkill', '-f', name], capture_output=True)
                print(f"⚡ Gracefully killed all processes matching '{name}'")
        except Exception as e:
            print(f"❌ Error killing processes with name '{name}': {e}")

def emergency_kill_all():
    """🚨 EMERGENCY: Kill all trading bot related processes"""
    print("🚨" * 20)
    print("🚨 EMERGENCY KILL SCRIPT ACTIVATED")
    print("🚨 Stopping ALL trading bot processes...")
    print("🚨" * 20)
    
    # Step 1: Get all Python processes
    print("\n🔍 Step 1: Scanning for Python processes...")
    python_processes = get_python_processes()
    
    if not python_processes:
        print("✅ No Python processes found")
    else:
        print(f"Found {len(python_processes)} Python processes:")
        for pid, user, command in python_processes:
            print(f"   PID {pid} ({user}): {command[:100]}...")
    
    # Step 2: Kill specific trading bot processes
    print("\n⚡ Step 2: Graceful termination of trading bot processes...")
    trading_bot_processes = []
    
    for pid, user, command in python_processes:
        # Check if it's our trading bot
        if any(keyword in command.lower() for keyword in ['main.py', 'copy', 'trading', 'bot']):
            trading_bot_processes.append((pid, user, command))
            kill_process_by_pid(pid, force=False)
    
    # Wait a moment for graceful shutdown
    if trading_bot_processes:
        print("⏳ Waiting 3 seconds for graceful shutdown...")
        time.sleep(3)
    
    # Step 3: Force kill if still running
    print("\n🔥 Step 3: Force killing any remaining processes...")
    python_processes_after = get_python_processes()
    
    for pid, user, command in python_processes_after:
        if any(keyword in command.lower() for keyword in ['main.py', 'copy', 'trading', 'bot']):
            print(f"🔥 Force killing stubborn process {pid}: {command[:50]}...")
            kill_process_by_pid(pid, force=True)
    
    # Step 4: Nuclear option - kill by process name
    print("\n💥 Step 4: Nuclear option - killing by process name...")
    process_names = [
        'main.py',
        'python main.py',
        'python3 main.py'
    ]
    
    kill_processes_by_name(process_names, force=True)
    
    # Step 5: Final verification
    print("\n✅ Step 5: Final verification...")
    time.sleep(1)
    final_processes = get_python_processes()
    
    remaining_bot_processes = []
    for pid, user, command in final_processes:
        if any(keyword in command.lower() for keyword in ['main.py', 'copy', 'trading', 'bot']):
            remaining_bot_processes.append((pid, user, command))
    
    if remaining_bot_processes:
        print("⚠️ WARNING: Some processes are still running:")
        for pid, user, command in remaining_bot_processes:
            print(f"   PID {pid}: {command[:100]}...")
        print("You may need to manually kill these with: sudo kill -9 <PID>")
    else:
        print("✅ SUCCESS: All trading bot processes have been terminated!")
    
    print("\n" + "🛑" * 20)
    print("🛑 EMERGENCY KILL COMPLETE")
    print("🛑" * 20)

def main():
    """Main function"""
    print("🚨 Emergency Kill Script for Trading Bot")
    print("This will forcefully stop ALL Python trading bot processes")
    
    # Check if running as script
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        emergency_kill_all()
    else:
        # Interactive mode
        response = input("\n⚠️ Are you sure you want to kill all trading bot processes? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            emergency_kill_all()
        else:
            print("❌ Operation cancelled")

if __name__ == "__main__":
    main()
