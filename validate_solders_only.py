#!/usr/bin/env python3
"""
Validation script to ensure all code uses only solders library
and no legacy solana-py or spl.token imports remain.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and return output"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def check_legacy_imports():
    """Check for any legacy imports from solana-py or spl.token"""
    print("\n🔍 Checking for legacy imports...")
    
    # Check for solana-py imports
    ret_solana, out_solana, _ = run_command(
        'grep -r "from solana\\." --include="*.py" . | grep -v "validate" | grep -v "^#" | grep -v ".pyc"',
        "Searching for solana-py imports"
    )
    
    # Check for spl.token imports  
    ret_spl, out_spl, _ = run_command(
        'grep -r "from spl" --include="*.py" . | grep -v "validate" | grep -v "^#" | grep -v ".pyc"',
        "Searching for spl.token imports"
    )
    
    if ret_solana == 0 and out_solana.strip():
        print(f"❌ FAIL: Found legacy solana-py imports:")
        print(out_solana)
        return False
    
    if ret_spl == 0 and out_spl.strip():
        print(f"❌ FAIL: Found legacy spl.token imports:")
        print(out_spl)
        return False
        
    print("✅ PASS: No legacy imports found")
    return True

def check_solders_usage():
    """Verify solders is being used"""
    print("\n🔍 Checking for solders usage...")
    
    ret, out, _ = run_command(
        'grep -r "from solders" --include="*.py" . | wc -l',
        "Counting solders imports"
    )
    
    count = int(out.strip())
    if count > 0:
        print(f"✅ PASS: Found {count} solders imports")
        return True
    else:
        print("❌ FAIL: No solders imports found")
        return False

def check_ata_helpers():
    """Verify ATA helper functions exist in utils.py"""
    print("\n🔍 Checking ATA helper functions in utils.py...")
    
    required_functions = [
        'find_associated_token_address',
        'get_associated_token_address', 
        'create_associated_token_account',
        'TOKEN_PROGRAM_ID',
        'ASSOCIATED_TOKEN_PROGRAM_ID'
    ]
    
    with open('utils.py', 'r') as f:
        content = f.read()
    
    missing = []
    for func in required_functions:
        if func not in content:
            missing.append(func)
    
    if missing:
        print(f"❌ FAIL: Missing functions in utils.py: {', '.join(missing)}")
        return False
    
    print(f"✅ PASS: All required ATA helper functions present")
    return True

def check_python_syntax():
    """Verify all Python files have valid syntax"""
    print("\n🔍 Checking Python syntax for all files...")
    
    py_files = [
        'utils.py',
        'mev_jupiter_executor.py',
        'mev_direct_sell_executor.py',
        'mev_direct_copy_executor.py',
        'execution_coordinator.py',
        'mev_raydium_executor.py',
        'mev_meteora_executor.py',
        'mev_advanced_bot_executor.py',
        'main.py'
    ]
    
    all_valid = True
    for py_file in py_files:
        if not os.path.exists(py_file):
            print(f"⚠️  WARNING: {py_file} not found, skipping")
            continue
            
        ret, _, err = run_command(
            f'python3 -m py_compile {py_file}',
            f"Compiling {py_file}"
        )
        
        if ret == 0:
            print(f"   ✅ {py_file}: Valid syntax")
        else:
            print(f"   ❌ {py_file}: Syntax error")
            print(f"      {err}")
            all_valid = False
    
    return all_valid

def check_utils_imports():
    """Verify files import ATA helpers from utils"""
    print("\n🔍 Checking that files import ATA helpers from utils...")
    
    files_to_check = [
        'mev_jupiter_executor.py',
        'mev_direct_sell_executor.py', 
        'mev_direct_copy_executor.py',
        'execution_coordinator.py'
    ]
    
    all_good = True
    for file in files_to_check:
        if not os.path.exists(file):
            continue
            
        with open(file, 'r') as f:
            content = f.read()
        
        # Check if file uses ATA functions
        uses_get_ata = 'get_associated_token_address(' in content
        uses_create_ata = 'create_associated_token_account(' in content
        
        if uses_get_ata or uses_create_ata:
            # Check for imports from utils - both module-level and local imports
            has_utils_import = 'from utils import' in content and (
                'get_associated_token_address' in content or
                'create_associated_token_account' in content
            )
            
            if not has_utils_import:
                print(f"   ⚠️  {file}: Uses ATA functions but may not import from utils")
                all_good = False
            else:
                print(f"   ✅ {file}: Correctly imports from utils")
        else:
            print(f"   ℹ️  {file}: Does not use ATA functions")
    
    return all_good

def main():
    """Run all validation checks"""
    print("="*60)
    print("SOLDERS-ONLY REFACTOR VALIDATION")
    print("="*60)
    
    checks = [
        ("Legacy Imports", check_legacy_imports),
        ("Solders Usage", check_solders_usage),
        ("ATA Helpers in utils.py", check_ata_helpers),
        ("Python Syntax", check_python_syntax),
        ("Utils Imports", check_utils_imports),
    ]
    
    results = []
    for name, check_func in checks:
        results.append((name, check_func()))
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\nMigration to solders-only is complete:")
        print("  • All legacy solana-py imports removed")
        print("  • All legacy spl.token imports removed")
        print("  • Using solders for all Solana operations")
        print("  • SPL token helpers in utils.py using solders")
        print("  • All syntax valid")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("\nPlease review the failures above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
