#!/usr/bin/env python3
"""
Validate test scripts structure without requiring .env file

This script validates that all test scripts:
1. Have correct imports
2. Have proper argument parsing
3. Have --simulate and --submit flags
4. Follow the expected structure
"""

import ast
import sys
from pathlib import Path

def validate_test_script(script_path):
    """Validate a single test script."""
    print(f"\nValidating: {script_path.name}")
    print("-" * 60)
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"  ❌ Syntax error: {e}")
        return False
    
    # Check for required imports
    required_imports = ['argparse', 'asyncio', 'logging']
    found_imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                found_imports.append(node.module)
    
    missing_imports = [imp for imp in required_imports if imp not in found_imports]
    if missing_imports:
        print(f"  ❌ Missing imports: {missing_imports}")
        return False
    else:
        print(f"  ✅ All required imports present")
    
    # Check for argparse usage
    if 'ArgumentParser' in content:
        print(f"  ✅ Uses ArgumentParser")
    else:
        print(f"  ❌ Missing ArgumentParser")
        return False
    
    # Check for --simulate and --submit flags
    if '--simulate' in content and '--submit' in content:
        print(f"  ✅ Has --simulate and --submit flags")
    else:
        print(f"  ❌ Missing required flags")
        return False
    
    # Check for async main function
    has_async_main = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == 'main':
            has_async_main = True
            break
    
    if has_async_main:
        print(f"  ✅ Has async main function")
    else:
        print(f"  ❌ Missing async main function")
        return False
    
    # Check for proper logging setup
    if 'logging.basicConfig' in content:
        print(f"  ✅ Logging configured")
    else:
        print(f"  ⚠️  Logging may not be configured")
    
    # Check for TEST_AMOUNT_SOL and TEST_AMOUNT_LAMPORTS constants
    if 'TEST_AMOUNT_SOL' in content and 'TEST_AMOUNT_LAMPORTS' in content:
        print(f"  ✅ Test amount constants defined (TEST_AMOUNT_SOL, TEST_AMOUNT_LAMPORTS)")
    else:
        print(f"  ⚠️  Test amount constants may be missing")
    
    print(f"  ✅ {script_path.name} structure is valid")
    return True


def main():
    """Validate all test scripts."""
    print("=" * 60)
    print("Validating Test Scripts Structure")
    print("=" * 60)
    
    tests_dir = Path(__file__).parent
    test_scripts = [
        tests_dir / "test_jupiter.py",
        tests_dir / "test_pumpfun.py",
        tests_dir / "test_raydium_cpmm.py",
        tests_dir / "test_meteora.py",
    ]
    
    results = []
    for script_path in test_scripts:
        if not script_path.exists():
            print(f"\n❌ Script not found: {script_path}")
            results.append(False)
            continue
        
        valid = validate_test_script(script_path)
        results.append(valid)
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("✅ All test scripts are properly structured")
        return 0
    else:
        print("❌ Some test scripts have issues")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
