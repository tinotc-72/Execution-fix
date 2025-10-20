#!/usr/bin/env python3
"""
Test Jito import pattern - Verifies that code handles missing Jito gracefully
without requiring actual dependencies to be installed.
"""

import sys
import re
import ast

def test_file_import_pattern(filename, module_name):
    """Test that a file has proper Jito conditional import pattern."""
    print(f"\n{'='*80}")
    print(f"Testing: {filename} ({module_name})")
    print('='*80)
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Check for try/except around jito_service import
        has_try_import = bool(re.search(r'try:\s+from jito_service import', content, re.MULTILINE))
        has_except_import_error = bool(re.search(r'except ImportError', content))
        has_jito_available_false = bool(re.search(r'JITO_AVAILABLE\s*=\s*False', content))
        has_jito_client_none = bool(re.search(r'JitoClient\s*=\s*None', content))
        
        # Check for logging of import status
        has_import_logging = bool(re.search(r'logger\.info.*JitoClient.*available', content, re.IGNORECASE))
        
        # Check for jito_is_configured function
        has_jito_is_configured = bool(re.search(r'def jito_is_configured', content))
        
        # Parse the file to ensure it's valid Python
        try:
            ast.parse(content)
            valid_syntax = True
        except SyntaxError:
            valid_syntax = False
        
        # Report results
        checks = [
            ("Try/except for jito_service import", has_try_import),
            ("Handles ImportError", has_except_import_error),
            ("Sets JITO_AVAILABLE = False on error", has_jito_available_false),
            ("Sets JitoClient = None on error", has_jito_client_none),
            ("Logs import status", has_import_logging),
            ("Valid Python syntax", valid_syntax),
        ]
        
        if has_jito_is_configured:
            checks.append(("Has jito_is_configured function", True))
        
        passed = all(result for _, result in checks)
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
        
        if passed:
            print(f"\n✅ {module_name} PASSED - Proper Jito import handling")
        else:
            print(f"\n❌ {module_name} FAILED - Issues with Jito import handling")
        
        return passed
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return False
    except Exception as e:
        print(f"❌ Error testing {filename}: {e}")
        return False

def test_no_direct_bundle_import():
    """Test that no files try to import Bundle from jito_service."""
    print(f"\n{'='*80}")
    print("Testing: No direct Bundle import from jito_service")
    print('='*80)
    
    files_to_check = [
        'fast_executor.py',
        'execution_coordinator.py',
        'mev_jupiter_executor.py',
        'mev_meteora_executor.py',
        'mev_direct_copy_executor.py',
        'mev_advanced_bot_executor.py',
        'mev_direct_sell_executor.py',
        'mev_raydium_executor.py',
    ]
    
    issues_found = []
    
    for filename in files_to_check:
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Check for problematic import
            if re.search(r'from jito_service import.*Bundle', content):
                issues_found.append(f"{filename}: Imports Bundle from jito_service")
        
        except FileNotFoundError:
            pass  # Skip missing files
    
    if issues_found:
        print("❌ Found problematic imports:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ No files import Bundle from jito_service")
        return True

def test_bundle_in_models():
    """Test that Bundle class exists in models.py."""
    print(f"\n{'='*80}")
    print("Testing: Bundle class in models.py")
    print('='*80)
    
    try:
        with open('models.py', 'r') as f:
            content = f.read()
        
        has_bundle_class = bool(re.search(r'class Bundle:', content))
        
        if has_bundle_class:
            print("✅ Bundle class found in models.py")
            return True
        else:
            print("❌ Bundle class not found in models.py")
            return False
    
    except FileNotFoundError:
        print("❌ models.py not found")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Jito Import Pattern Compliance")
    print("="*80)
    print("This test verifies code structure without requiring dependencies\n")
    
    results = []
    
    # Test each executor file
    files_to_test = [
        ('fast_executor.py', 'FastExecutor'),
        ('mev_jupiter_executor.py', 'MEV Jupiter Executor'),
        ('mev_meteora_executor.py', 'MEV Meteora Executor'),
        ('mev_direct_copy_executor.py', 'MEV Direct Copy Executor'),
        ('mev_advanced_bot_executor.py', 'MEV Advanced Bot Executor'),
    ]
    
    for filename, module_name in files_to_test:
        results.append((module_name, test_file_import_pattern(filename, module_name)))
    
    # Test Bundle handling
    results.append(("No Bundle from jito_service", test_no_direct_bundle_import()))
    results.append(("Bundle in models.py", test_bundle_in_models()))
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print('='*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print('='*80)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All import patterns are correct!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
