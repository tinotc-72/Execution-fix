#!/usr/bin/env python3
"""
VERIFICATION SCRIPT - Double-checking all our fixes
"""

import os

def verify_all_fixes():
    print("🔍 COMPREHENSIVE VERIFICATION OF ALL FIXES")
    print("=" * 80)
    
    print("📋 CHECKING ALL PUMP.FUN EXECUTORS:")
    print("-" * 40)
    
    # Check which pump.fun executor files exist
    executor_files = []
    for file in os.listdir('.'):
        if 'pump' in file.lower() and file.endswith('.py'):
            executor_files.append(file)
    
    print(f"Found {len(executor_files)} pump.fun related files:")
    for file in executor_files:
        print(f"   • {file}")
    
    print("\n🔍 CHECKING PROGRAM ID IN EACH FILE:")
    print("-" * 40)
    
    correct_program_id = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
    wrong_program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    
    issues_found = []
    
    for file in executor_files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                
            correct_count = content.count(correct_program_id)
            wrong_count = content.count(wrong_program_id)
            
            print(f"\n📄 {file}:")
            print(f"   ✅ Correct program ID: {correct_count} instances")
            print(f"   ❌ Wrong program ID: {wrong_count} instances")
            
            if wrong_count > 0:
                issues_found.append(f"{file} still has {wrong_count} wrong program IDs")
            elif correct_count == 0:
                issues_found.append(f"{file} has no program ID references")
                
        except Exception as e:
            print(f"   ❌ Error reading {file}: {e}")
            issues_found.append(f"Could not read {file}")
    
    print("\n🔍 CHECKING WHICH EXECUTOR THE BOT USES:")
    print("-" * 40)
    
    # Check execution_coordinator.py
    try:
        with open('execution_coordinator.py', 'r') as f:
            coordinator_content = f.read()
        
        if "PumpFunCopyExecutor" in coordinator_content:
            print("   ✅ Bot uses PumpFunCopyExecutor")
        if "DirectPumpfunExecutor" in coordinator_content:
            print("   ✅ Bot uses DirectPumpfunExecutor")
        if "pumpfun_executor" in coordinator_content:
            print("   ✅ Bot imports pumpfun_executor")
            
    except Exception as e:
        print(f"   ❌ Error reading execution_coordinator.py: {e}")
    
    print("\n📊 VERIFICATION SUMMARY:")
    print("-" * 40)
    
    if not issues_found:
        print("✅ ALL CHECKS PASSED!")
        print("   • All pump.fun executors use correct program ID")
        print("   • No instances of wrong program ID found")
        print("   • Fixes appear to be complete")
        print()
        print("🎯 CONFIDENCE LEVEL: HIGH")
        print("   Next pump.fun transaction should work correctly")
    else:
        print("❌ ISSUES STILL FOUND:")
        for issue in issues_found:
            print(f"   • {issue}")
        print()
        print("🎯 CONFIDENCE LEVEL: LOW")
        print("   Additional fixes may be needed")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    verify_all_fixes()
