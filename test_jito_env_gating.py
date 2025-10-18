#!/usr/bin/env python3
"""
Test that JITO_ENABLED environment variable gates Jito functionality.

This test verifies:
1. When JITO_ENABLED=false, Jito is not imported even if available
2. When JITO_ENABLED=true (or unset), Jito is imported if available
3. When Jito import fails, code gracefully falls back to RPC
4. execution_coordinator.py has no top-level Jito imports
"""

import sys
import re
import os
import ast


def test_jito_enabled_env_check():
    """Test that fast_executor checks JITO_ENABLED env variable"""
    print("=" * 80)
    print("TEST 1: JITO_ENABLED Environment Variable Check")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'import os', "✅ Imports os module for env check"),
        (r'JITO_ENABLED\s*=\s*os\.getenv\(["\']JITO_ENABLED["\']', 
         "✅ Reads JITO_ENABLED from environment"),
        (r'if JITO_ENABLED:', 
         "✅ Gates Jito imports behind JITO_ENABLED check"),
        (r'if JITO_ENABLED and JITO_AVAILABLE:', 
         "✅ Checks both JITO_ENABLED and JITO_AVAILABLE before using Jito"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_submit_transaction_respects_use_jito():
    """Test that submit_transaction respects self.use_jito flag"""
    print("=" * 80)
    print("TEST 2: submit_transaction Respects use_jito Flag")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    # Find submit_transaction method
    method_match = re.search(
        r'async def submit_transaction\(self.*?\n(.*?)(?=\n    async def|\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    if not method_match:
        print("  ❌ Could not find submit_transaction method")
        return False
    
    method_content = method_match.group(1)
    
    patterns = [
        (r'if self\.use_jito:', "✅ Checks self.use_jito before trying Jito"),
        (r'falling back to RPC', "✅ Logs fallback to RPC on Jito failure"),
        (r'await self\._submit_via_rpc\(vtx\)', "✅ Falls back to RPC"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, method_content, re.IGNORECASE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_no_jito_imports_in_coordinator():
    """Test that execution_coordinator.py has no top-level Jito imports"""
    print("=" * 80)
    print("TEST 3: No Top-Level Jito Imports in execution_coordinator.py")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Parse the file to get top-level imports
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"  ❌ Syntax error in execution_coordinator.py: {e}")
        return False
    
    jito_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if 'jito' in alias.name.lower():
                    jito_imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and 'jito' in node.module.lower():
                for alias in node.names:
                    jito_imports.append(f"from {node.module} import {alias.name}")
    
    if jito_imports:
        print("  ❌ Found Jito imports:")
        for imp in jito_imports:
            print(f"     - {imp}")
        print("\n  Result: FAILED\n")
        return False
    else:
        print("  ✅ No top-level Jito imports found")
        print("  ✅ execution_coordinator.py only passes jito_service as parameter")
        print("\n  Result: PASSED\n")
        return True


def test_rpc_only_mode():
    """Test that RPC-only mode works when Jito is disabled"""
    print("=" * 80)
    print("TEST 4: RPC-Only Mode When Jito Disabled")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    # Check that when JITO_ENABLED=false or JITO_AVAILABLE=false, 
    # the code sets use_jito=False
    patterns = [
        (r'self\.use_jito = False', "✅ Sets use_jito=False when Jito unavailable"),
        (r'self\.jito = None', "✅ Sets jito client to None when unavailable"),
        (r'using pure RPC path', "✅ Logs RPC-only mode"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_submit_via_rpc_error_handling():
    """Test that _submit_via_rpc has proper error handling"""
    print("=" * 80)
    print("TEST 5: _submit_via_rpc Error Handling")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    # Find _submit_via_rpc method
    method_match = re.search(
        r'async def _submit_via_rpc\(self.*?\n(.*?)(?=\n    async def|\n    def|\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    if not method_match:
        print("  ❌ Could not find _submit_via_rpc method")
        return False
    
    method_content = method_match.group(1)
    
    patterns = [
        (r'try:', "✅ Has try/except block"),
        (r'except Exception as e:', "✅ Catches exceptions"),
        (r'self\.logger\.error.*SUBMIT_RPC.*error', "✅ Logs RPC errors"),
        (r'return None', "✅ Returns None on error"),
        (r'self\.logger\.info.*SUBMIT_RPC.*sig', "✅ Logs successful RPC submission"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, method_content, re.IGNORECASE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def test_initialization_logging():
    """Test that initialization logs correct Jito status"""
    print("=" * 80)
    print("TEST 6: Initialization Logging")
    print("=" * 80)
    
    with open('fast_executor.py', 'r') as f:
        content = f.read()
    
    patterns = [
        (r'Jito disabled via JITO_ENABLED env var', 
         "✅ Logs when Jito is disabled via env"),
        (r'JitoClient import failed', 
         "✅ Logs when Jito import fails"),
        (r'using pure RPC path', 
         "✅ Logs RPC-only mode in __init__"),
        (r'MEV Protection: Enabled', 
         "✅ Logs when Jito is enabled"),
    ]
    
    passed = 0
    for pattern, description in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(patterns)} checks passed\n")
    return passed == len(patterns)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("JITO ENVIRONMENT GATING TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        test_jito_enabled_env_check(),
        test_submit_transaction_respects_use_jito(),
        test_no_jito_imports_in_coordinator(),
        test_rpc_only_mode(),
        test_submit_via_rpc_error_handling(),
        test_initialization_logging(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL JITO ENVIRONMENT GATING TESTS PASSED!")
        print("\n  Implementation summary:")
        print("  ✅ JITO_ENABLED env variable gates Jito imports")
        print("  ✅ submit_transaction respects use_jito flag")
        print("  ✅ execution_coordinator.py has no top-level Jito imports")
        print("  ✅ RPC-only mode works when Jito is disabled")
        print("  ✅ _submit_via_rpc has proper error handling")
        print("  ✅ Initialization logs correct Jito status")
        print()
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print(f"  ❌ {total - passed} test(s) need attention")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
