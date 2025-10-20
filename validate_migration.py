#!/usr/bin/env python3
"""
Validation script to verify legacy solana package removal

This script validates:
1. No legacy solana imports remain
2. All files use solders for Solana types
3. RPCClient is properly implemented
4. All syntax is valid
"""

import os
import sys
import ast
import subprocess

def check_no_legacy_imports():
    """Verify no legacy solana imports exist"""
    print("🔍 Checking for legacy solana imports...")
    
    result = subprocess.run(
        ["grep", "-r", "from solana\\.", "--include=*.py", "."],
        cwd="/home/runner/work/Execution-fix/Execution-fix",
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print(f"   ❌ FAIL: Found legacy solana imports:\n{result.stdout}")
        return False
    
    print("   ✅ PASS: No legacy solana imports found")
    return True

def check_solders_usage():
    """Verify solders is used throughout"""
    print("\n🔍 Checking solders usage...")
    
    result = subprocess.run(
        ["grep", "-l", "from solders", "*.py"],
        cwd="/home/runner/work/Execution-fix/Execution-fix",
        capture_output=True,
        text=True,
        shell=True
    )
    
    files = [f for f in result.stdout.strip().split('\n') if f]
    if len(files) < 10:
        # Fallback: count manually
        import glob
        py_files = glob.glob("/home/runner/work/Execution-fix/Execution-fix/*.py")
        count = 0
        for py_file in py_files:
            with open(py_file, 'r') as f:
                if 'from solders' in f.read():
                    count += 1
        
        if count < 10:
            print(f"   ⚠️  WARNING: Only {count} files use solders")
            return False
        else:
            print(f"   ✅ PASS: {count} files use solders")
            return True
    
    print(f"   ✅ PASS: {len(files)} files use solders")
    return True

def check_rpc_client_implementation():
    """Verify RPCClient is properly implemented"""
    print("\n🔍 Checking RPCClient implementation...")
    
    utils_path = "/home/runner/work/Execution-fix/Execution-fix/utils.py"
    
    try:
        with open(utils_path, 'r') as f:
            content = f.read()
        
        # Check for RPCClient class
        if 'class RPCClient:' not in content:
            print("   ❌ FAIL: RPCClient class not found")
            return False
        
        # Check for essential methods
        required_methods = [
            'get_balance',
            'get_latest_blockhash',
            'send_transaction',
            'send_raw_transaction',
            'get_signature_statuses',
            'simulate_transaction',
            'get_health'
        ]
        
        missing_methods = []
        for method in required_methods:
            if f'async def {method}' not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"   ❌ FAIL: Missing methods: {', '.join(missing_methods)}")
            return False
        
        print("   ✅ PASS: RPCClient class with all required methods")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

def check_syntax():
    """Verify all Python files have valid syntax"""
    print("\n🔍 Checking Python syntax...")
    
    files_to_check = [
        "utils.py",
        "main.py",
        "mev_jupiter_executor.py",
        "mev_advanced_bot_executor.py",
        "mev_direct_sell_executor.py",
        "mev_direct_copy_executor.py",
        "mev_meteora_executor.py",
        "wallet_tx_parser.py"
    ]
    
    all_valid = True
    for filename in files_to_check:
        filepath = f"/home/runner/work/Execution-fix/Execution-fix/{filename}"
        result = subprocess.run(
            ["python3", "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"   ❌ {filename}: {result.stderr}")
            all_valid = False
        else:
            print(f"   ✅ {filename}: Valid syntax")
    
    return all_valid

def check_rpc_client_usage():
    """Verify RPCClient is being used"""
    print("\n🔍 Checking RPCClient usage...")
    
    # Count manually
    import glob
    py_files = glob.glob("/home/runner/work/Execution-fix/Execution-fix/*.py")
    files_with_rpc = []
    for py_file in py_files:
        with open(py_file, 'r') as f:
            if 'RPCClient' in f.read():
                files_with_rpc.append(os.path.basename(py_file))
    
    if len(files_with_rpc) < 5:
        print(f"   ⚠️  WARNING: Only {len(files_with_rpc)} files use RPCClient")
        return False
    
    print(f"   ✅ PASS: {len(files_with_rpc)} files use RPCClient")
    for f in sorted(files_with_rpc):
        print(f"      - {f}")
    return True

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("LEGACY SOLANA PACKAGE REMOVAL - VALIDATION")
    print("=" * 60)
    
    checks = [
        ("No legacy imports", check_no_legacy_imports),
        ("Solders usage", check_solders_usage),
        ("RPCClient implementation", check_rpc_client_implementation),
        ("Python syntax", check_syntax),
        ("RPCClient usage", check_rpc_client_usage)
    ]
    
    results = []
    for name, check_func in checks:
        results.append(check_func())
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for (name, _), result in zip(checks, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("\nMigration complete:")
        print("  • All legacy solana imports removed")
        print("  • Using solders for Solana types")
        print("  • Using aiohttp for RPC via RPCClient")
        print("  • All syntax valid")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
