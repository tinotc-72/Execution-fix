#!/usr/bin/env python3
"""
Test for clone/direct_copy path reliability improvements.

This test validates that the transaction_cloner.py has all the required
components for reliable v0 transaction cloning with ALTs, ATAs, compute budget,
and BuildResult returns.

Tests:
1. All required imports are present
2. get_recent_blockhash helper function exists
3. clone_tx_from_signature returns BuildResult
4. ALT fetching uses build_alts_from_tables (sync version)
5. ATA checking logic is present
6. Compute budget is applied
7. Unified submit helper is used
8. Post-submit logging is used
9. No "return None" in clone_tx_from_signature
"""

import sys
import ast
import re
from pathlib import Path


def read_file(filepath: str) -> str:
    """Read file contents"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def test_required_imports():
    """Test that all required imports are present"""
    print("\n📋 Test 1: Required Imports")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    
    required_imports = {
        "build_alts_from_tables": r"from\s+utils\.alt_fetch\s+import.*build_alts_from_tables",
        "ensure_ata_ixs": r"from\s+utils\.ata_enforce\s+import.*ensure_ata_ixs",
        "create_associated_token_account": r"from\s+utils\.ata\s+import.*create_associated_token_account",
        "BuildResult": r"from\s+models\.build_result\s+import.*BuildResult",
        "send_and_confirm_v0_tx": r"from\s+executors\.submit\s+import.*send_and_confirm_v0_tx",
        "log_submit_result": r"from\s+utils\.logs\s+import.*log_submit_result",
        "with_compute_budget": r"from\s+utils\.fees\s+import.*with_compute_budget",
    }
    
    passed = 0
    failed = 0
    
    for name, pattern in required_imports.items():
        if re.search(pattern, content):
            print(f"  ✅ {name}")
            passed += 1
        else:
            print(f"  ❌ {name} - MISSING")
            failed += 1
    
    print(f"\nResult: {passed}/{len(required_imports)} imports found")
    return failed == 0


def test_get_recent_blockhash_function():
    """Test that get_recent_blockhash helper function exists"""
    print("\n🔧 Test 2: get_recent_blockhash Helper Function")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    tree = ast.parse(content)
    
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_recent_blockhash":
            found = True
            # Check it has the right signature
            args = [arg.arg for arg in node.args.args]
            if "rpc_url" in args:
                print(f"  ✅ Function found with correct signature")
                print(f"     Parameters: {args}")
            else:
                print(f"  ⚠️  Function found but missing 'rpc_url' parameter")
            break
    
    if not found:
        print(f"  ❌ get_recent_blockhash function not found")
        return False
    
    return found


def test_clone_tx_from_signature_returns_buildresult():
    """Test that clone_tx_from_signature returns BuildResult"""
    print("\n🏗️  Test 3: clone_tx_from_signature Returns BuildResult")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    tree = ast.parse(content)
    
    found = False
    correct_return_type = False
    no_return_none = True
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "clone_tx_from_signature":
            found = True
            
            # Check return type annotation
            if node.returns:
                return_annotation = ast.unparse(node.returns)
                if "BuildResult" in return_annotation:
                    correct_return_type = True
                    print(f"  ✅ Return type is BuildResult")
                else:
                    print(f"  ❌ Return type is {return_annotation}, expected BuildResult")
            else:
                print(f"  ❌ No return type annotation")
            
            # Check for "return None" statements
            for child in ast.walk(node):
                if isinstance(child, ast.Return):
                    if child.value is None or (isinstance(child.value, ast.Constant) and child.value.value is None):
                        no_return_none = False
                        print(f"  ❌ Found 'return None' statement")
            
            if no_return_none:
                print(f"  ✅ No 'return None' statements found")
            
            break
    
    if not found:
        print(f"  ❌ clone_tx_from_signature function not found")
        return False
    
    return found and correct_return_type and no_return_none


def test_alt_fetching_uses_sync():
    """Test that ALT fetching uses build_alts_from_tables (sync version)"""
    print("\n🔄 Test 4: ALT Fetching Uses Sync Version")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    
    # Check for build_alts_from_tables usage
    if "build_alts_from_tables" in content:
        print(f"  ✅ build_alts_from_tables is used")
    else:
        print(f"  ❌ build_alts_from_tables not found")
        return False
    
    # Check that async alts_from_lookups is NOT used in clone_transaction
    # (it's okay to have it elsewhere, but not in the main path)
    if "await alts_from_lookups" in content:
        print(f"  ⚠️  'await alts_from_lookups' found - should use sync version")
        # Check if it's commented out
        if "# await alts_from_lookups" in content or "# from utils.alts import alts_from_lookups" in content:
            print(f"     (Commented out - OK)")
            return True
        return False
    else:
        print(f"  ✅ Async alts_from_lookups not used")
    
    return True


def test_ata_checking_logic():
    """Test that ATA checking logic is present"""
    print("\n💳 Test 5: ATA Checking Logic")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    
    checks = {
        "ensure_ata_ixs call": r"ensure_ata_ixs\s*\(",
        "token_mints tracking": r"token_mints\s*=",
        "ATA instructions": r"ata_instructions\s*=",
    }
    
    passed = 0
    for name, pattern in checks.items():
        if re.search(pattern, content):
            print(f"  ✅ {name}")
            passed += 1
        else:
            print(f"  ❌ {name} - MISSING")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_compute_budget():
    """Test that compute budget is applied"""
    print("\n⚙️  Test 6: Compute Budget")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    
    if "with_compute_budget" in content:
        print(f"  ✅ with_compute_budget is used")
        # Check it's called with instructions
        if re.search(r"with_compute_budget\s*\(\s*\w+", content):
            print(f"  ✅ Called with instructions")
            return True
    else:
        print(f"  ❌ with_compute_budget not found")
    
    return False


def test_unified_submit():
    """Test that unified submit helper is used"""
    print("\n🚀 Test 7: Unified Submit Helper")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    
    if "send_and_confirm_v0_tx" in content:
        print(f"  ✅ send_and_confirm_v0_tx is used")
        return True
    else:
        print(f"  ❌ send_and_confirm_v0_tx not found")
        return False


def test_post_submit_logging():
    """Test that post-submit logging is used"""
    print("\n📝 Test 8: Post-Submit Logging")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    
    if "log_submit_result" in content:
        print(f"  ✅ log_submit_result is used")
        # Check it's called with proper parameters
        if re.search(r'log_submit_result\s*\(\s*["\']', content):
            print(f"  ✅ Called with parameters")
            return True
    else:
        print(f"  ❌ log_submit_result not found")
    
    return False


def test_no_return_none_in_builder():
    """Test that there are no 'return None' in clone builders"""
    print("\n🔍 Test 9: No 'return None' in Builders")
    print("-" * 60)
    
    content = read_file("transaction_cloner.py")
    tree = ast.parse(content)
    
    # Find clone_tx_from_signature and check for return None
    found_function = False
    has_return_none = False
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "clone_tx_from_signature":
            found_function = True
            for child in ast.walk(node):
                if isinstance(child, ast.Return):
                    if child.value is None or (isinstance(child.value, ast.Constant) and child.value.value is None):
                        has_return_none = True
                        print(f"  ❌ Found 'return None' in clone_tx_from_signature")
            break
    
    if not found_function:
        print(f"  ❌ clone_tx_from_signature not found")
        return False
    
    if not has_return_none:
        print(f"  ✅ No 'return None' found in clone_tx_from_signature")
    
    return not has_return_none


def main():
    """Run all tests"""
    print("=" * 70)
    print("Clone/Direct-Copy Path Reliability Test Suite")
    print("=" * 70)
    
    # Change to repository root if needed
    if not Path("transaction_cloner.py").exists():
        print("❌ ERROR: transaction_cloner.py not found")
        print(f"   Current directory: {Path.cwd()}")
        return 1
    
    tests = [
        ("Required Imports", test_required_imports),
        ("get_recent_blockhash", test_get_recent_blockhash_function),
        ("BuildResult Returns", test_clone_tx_from_signature_returns_buildresult),
        ("ALT Sync Fetching", test_alt_fetching_uses_sync),
        ("ATA Checking", test_ata_checking_logic),
        ("Compute Budget", test_compute_budget),
        ("Unified Submit", test_unified_submit),
        ("Post-Submit Logging", test_post_submit_logging),
        ("No return None", test_no_return_none_in_builder),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
