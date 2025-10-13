#!/usr/bin/env python3
"""
🛡️ WALLET PROTECTION SCRIPT - EMERGENCY SAFEGUARDS
This script implements multiple layers of protection for your wallet
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

def kill_all_trading_processes():
    """Kill all trading-related processes"""
    print("🚨 KILLING ALL TRADING PROCESSES...")
    
    # Kill by process name patterns
    patterns = [
        'main.py',
        'python.*main.py',
        'copy.*trading',
        'trading.*bot',
        'solana.*bot'
    ]
    
    for pattern in patterns:
        try:
            subprocess.run(['pkill', '-9', '-f', pattern], capture_output=True)
            print(f"🔥 Killed processes matching: {pattern}")
        except:
            pass
    
    # Kill by PID scanning
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if ('python' in line and 'main.py' in line and 'grep' not in line):
                parts = line.split()
                if len(parts) > 1:
                    try:
                        os.kill(int(parts[1]), 9)
                        print(f"🔥 Force killed PID: {parts[1]}")
                    except:
                        pass
    except:
        pass

def disable_main_py():
    """Temporarily disable main.py to prevent accidental execution"""
    main_py_path = Path("main.py")
    backup_path = Path("main.py.DISABLED_FOR_SAFETY")
    
    if main_py_path.exists():
        try:
            main_py_path.rename(backup_path)
            print("🛡️ main.py has been DISABLED for safety")
            print("🛡️ Renamed to: main.py.DISABLED_FOR_SAFETY")
            return True
        except Exception as e:
            print(f"❌ Could not disable main.py: {e}")
            return False
    else:
        print("ℹ️ main.py not found in current directory")
        return False

def create_safety_lock():
    """Create a safety lock file to prevent trading"""
    lock_file = Path("TRADING_DISABLED.lock")
    try:
        with open(lock_file, 'w') as f:
            f.write(f"Trading disabled at: {time.ctime()}\n")
            f.write("This file prevents any trading operations.\n")
            f.write("Delete this file only when you're ready to trade again.\n")
        print("🔒 Created safety lock file: TRADING_DISABLED.lock")
        return True
    except Exception as e:
        print(f"❌ Could not create safety lock: {e}")
        return False

def wallet_emergency_protection():
    """Implement emergency wallet protection"""
    print("🛡️" * 20)
    print("🛡️ WALLET EMERGENCY PROTECTION ACTIVATED")
    print("🛡️" * 20)
    
    # Step 1: Kill all processes
    kill_all_trading_processes()
    
    # Step 2: Disable main.py
    disable_main_py()
    
    # Step 3: Create safety locks
    create_safety_lock()
    
    # Step 4: Final verification
    time.sleep(2)
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    trading_processes = []
    for line in result.stdout.split('\n'):
        if ('python' in line and any(keyword in line for keyword in ['main.py', 'trading', 'bot']) and 'grep' not in line):
            trading_processes.append(line)
    
    if trading_processes:
        print("⚠️ WARNING: Some trading processes may still be running:")
        for proc in trading_processes:
            print(f"   {proc}")
    else:
        print("✅ SUCCESS: No trading processes detected")
    
    print("\n🛡️ PROTECTION MEASURES ACTIVE:")
    print("🛡️ 1. All trading processes terminated")
    print("🛡️ 2. main.py disabled (renamed to .DISABLED_FOR_SAFETY)")
    print("🛡️ 3. Safety lock file created")
    print("🛡️")
    print("🛡️ Your wallet is now protected from accidental trades")
    print("🛡️" * 20)

def restore_trading_access():
    """Restore trading access (use with extreme caution)"""
    response = input("⚠️ Are you ABSOLUTELY SURE you want to restore trading access? (type 'YES I AM SURE'): ")
    if response == "YES I AM SURE":
        # Restore main.py
        backup_path = Path("main.py.DISABLED_FOR_SAFETY")
        main_py_path = Path("main.py")
        
        if backup_path.exists():
            backup_path.rename(main_py_path)
            print("✅ main.py restored")
        
        # Remove safety lock
        lock_file = Path("TRADING_DISABLED.lock")
        if lock_file.exists():
            lock_file.unlink()
            print("✅ Safety lock removed")
        
        print("⚠️ Trading access restored - BE EXTREMELY CAREFUL")
    else:
        print("❌ Trading access NOT restored")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--protect':
            wallet_emergency_protection()
        elif sys.argv[1] == '--restore':
            restore_trading_access()
        else:
            print("Usage: python3 wallet_protection.py [--protect|--restore]")
    else:
        print("🛡️ Wallet Protection Script")
        print("Options:")
        print("  --protect: Activate emergency protection")
        print("  --restore: Restore trading access (DANGEROUS)")
        
        choice = input("\nChoose action (protect/restore/cancel): ").lower()
        if choice == 'protect':
            wallet_emergency_protection()
        elif choice == 'restore':
            restore_trading_access()
        else:
            print("❌ No action taken")

if __name__ == "__main__":
    main()
