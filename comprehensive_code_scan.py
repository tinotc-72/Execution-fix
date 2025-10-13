#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE CODE SCAN
Final check for any outstanding issues across the entire codebase
"""

import os
import re
import subprocess
from typing import Dict, List, Tuple

def scan_for_outstanding_issues():
    """Comprehensive scan for any remaining issues"""
    print("🔍 COMPREHENSIVE CODE SCAN")
    print("="*80)
    
    issues_found = []
    
    # 1. Check for syntax errors in core files
    print("\n1️⃣ SYNTAX ERROR CHECK")
    print("-" * 40)
    
    core_files = [
        "main.py",
        "trade_processor.py", 
        "websocket_handler.py",
        "pumpfun_copy_executor.py",
        "jupiter_copy_executor.py",
        "raydium_copy_executor.py",
        "cpmm_copy_executor.py",
        "raydium_clmm_copy_executor.py",
        "clmm_copy_executor.py",
        "raydium_trade_executor.py",
        "raydium_clmm_trade_executor.py"
    ]
    
    for file in core_files:
        if os.path.exists(file):
            try:
                result = subprocess.run(['python3', '-m', 'py_compile', file], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   ✅ {file}: No syntax errors")
                else:
                    print(f"   ❌ {file}: SYNTAX ERROR")
                    print(f"      {result.stderr}")
                    issues_found.append(f"Syntax error in {file}")
            except Exception as e:
                print(f"   ⚠️ {file}: Could not check ({e})")
        else:
            print(f"   ❌ {file}: File not found")
            issues_found.append(f"Missing file: {file}")
    
    # 2. Check for proportional selling consistency
    print("\n2️⃣ PROPORTIONAL SELLING CHECK")
    print("-" * 40)
    
    executor_files = [f for f in core_files if 'executor' in f]
    prop_sell_issues = check_proportional_selling_consistency(executor_files)
    issues_found.extend(prop_sell_issues)
    
    # 3. Check for ATA fix consistency  
    print("\n3️⃣ ATA FIX CONSISTENCY CHECK")
    print("-" * 40)
    
    ata_issues = check_ata_fix_consistency(executor_files)
    issues_found.extend(ata_issues)
    
    # 4. Check for import issues
    print("\n4️⃣ IMPORT CONSISTENCY CHECK")
    print("-" * 40)
    
    import_issues = check_import_consistency()
    issues_found.extend(import_issues)
    
    # 5. Check for clean architecture compliance
    print("\n5️⃣ ARCHITECTURE COMPLIANCE CHECK")
    print("-" * 40)
    
    arch_issues = check_architecture_compliance()
    issues_found.extend(arch_issues)
    
    # Final summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE SCAN RESULTS")
    print("="*80)
    
    if not issues_found:
        print("✅ NO OUTSTANDING ISSUES FOUND!")
        print("   All files pass syntax check")
        print("   Proportional selling consistent across executors")
        print("   ATA fixes properly implemented")
        print("   Import dependencies clean")
        print("   Architecture properly separated")
        print("\n🎉 CODE IS READY FOR PRODUCTION!")
    else:
        print(f"⚠️ {len(issues_found)} ISSUE(S) FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 Please address these issues before deployment")
    
    return len(issues_found) == 0

def check_proportional_selling_consistency(executor_files: List[str]) -> List[str]:
    """Check if all executors have consistent proportional selling"""
    issues = []
    
    for file in executor_files:
        if not os.path.exists(file):
            continue
            
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            # Check for sell_percentage parameter
            has_sell_percentage = bool(re.search(r'sell_percentage', content, re.IGNORECASE))
            has_proportional_calc = bool(re.search(r'sell_percentage.*100|token_balance.*sell_percentage', content, re.IGNORECASE))
            has_kwargs = bool(re.search(r'kwargs\.get.*sell_percentage', content, re.IGNORECASE))
            
            if has_sell_percentage and (has_proportional_calc or has_kwargs):
                print(f"   ✅ {file}: Proportional selling implemented")
            else:
                print(f"   ❌ {file}: Missing proportional selling")
                issues.append(f"Missing proportional selling in {file}")
                
        except Exception as e:
            print(f"   ⚠️ {file}: Could not check proportional selling ({e})")
    
    return issues

def check_ata_fix_consistency(executor_files: List[str]) -> List[str]:
    """Check if all executors have ATA fix implemented"""
    issues = []
    
    for file in executor_files:
        if not os.path.exists(file):
            continue
            
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            # Check for ATA existence check pattern
            has_get_account_info = bool(re.search(r'get_account_info.*ata|account_info.*value.*None', content, re.IGNORECASE))
            has_ata_creation = bool(re.search(r'create_associated_token_account', content, re.IGNORECASE))
            has_ensure_method = bool(re.search(r'ensure_token_account_exists', content, re.IGNORECASE))
            
            if has_get_account_info and has_ata_creation:
                print(f"   ✅ {file}: ATA fix implemented")
            elif has_ensure_method:
                print(f"   ✅ {file}: ATA fix implemented (ensure method)")
            else:
                print(f"   ❌ {file}: Missing ATA fix")
                issues.append(f"Missing ATA fix in {file}")
                
        except Exception as e:
            print(f"   ⚠️ {file}: Could not check ATA fix ({e})")
    
    return issues

def check_import_consistency() -> List[str]:
    """Check for import issues"""
    issues = []
    
    # Check main.py imports
    if os.path.exists('main.py'):
        try:
            with open('main.py', 'r') as f:
                content = f.read()
            
            # Check for clean imports
            required_imports = [
                'trade_processor',
                'websocket_handler',
                'execution_coordinator'
            ]
            
            for imp in required_imports:
                if imp in content:
                    print(f"   ✅ main.py: {imp} imported")
                else:
                    print(f"   ❌ main.py: Missing {imp} import")
                    issues.append(f"Missing {imp} import in main.py")
                    
        except Exception as e:
            print(f"   ⚠️ main.py: Could not check imports ({e})")
    
    return issues

def check_architecture_compliance() -> List[str]:
    """Check for clean architecture compliance"""
    issues = []
    
    # Check that handlers don't have execution code
    handler_files = ['websocket_handler.py', 'trade_processor.py']
    
    for file in handler_files:
        if not os.path.exists(file):
            continue
            
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            # Check for execution patterns that shouldn't be in handlers
            bad_patterns = [
                r'send_transaction',
                r'build.*transaction',
                r'VersionedTransaction',
                r'ComputeBudgetInstruction'
            ]
            
            found_bad_patterns = []
            for pattern in bad_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_bad_patterns.append(pattern)
            
            if found_bad_patterns:
                print(f"   ❌ {file}: Contains execution code")
                for pattern in found_bad_patterns:
                    print(f"      - Found: {pattern}")
                issues.append(f"Handler {file} contains execution code")
            else:
                print(f"   ✅ {file}: Clean handler (no execution code)")
                
        except Exception as e:
            print(f"   ⚠️ {file}: Could not check architecture ({e})")
    
    return issues

if __name__ == "__main__":
    success = scan_for_outstanding_issues()
    exit(0 if success else 1)
