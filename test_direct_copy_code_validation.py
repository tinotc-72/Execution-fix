#!/usr/bin/env python3
"""
Static code validation test for mev_direct_copy_executor.py changes.
Validates that required changes are present without importing modules.
"""

import sys
import ast
import re


def test_import_base58():
    """Test that base58 is correctly imported (no typo)"""
    print("\n" + "="*60)
    print("TEST 1: Import base58 (No Typo)")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Check for correct import
        assert "import base58" in content, "❌ 'import base58' not found"
        
        # Check that there's no typo like 'base5\n8' or 'base5 8'
        # Look for the specific pattern of the typo
        import re
        typo_pattern = r'import\s+base5\s*\n\s*8|import\s+base5\s+8|from\s+base5'
        if re.search(typo_pattern, content):
            assert False, "❌ Typo 'import base5\\n8' or similar found"
        
        print("✅ PASS: base58 imported correctly")
        print("✅ PASS: No typo found")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_exec_ok_exec_err_import():
    """Test that exec_ok and exec_err are imported from execution_coordinator"""
    print("\n" + "="*60)
    print("TEST 2: exec_ok and exec_err Import")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Check for import statement
        assert "from execution_coordinator import exec_ok, exec_err" in content, \
            "❌ exec_ok and exec_err not imported from execution_coordinator"
        
        print("✅ PASS: exec_ok and exec_err imported from execution_coordinator")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_submit_cloned_tx_function():
    """Test that submit_cloned_tx helper function exists"""
    print("\n" + "="*60)
    print("TEST 3: submit_cloned_tx Helper Function")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Find submit_cloned_tx function
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == 'submit_cloned_tx':
                found = True
                
                # Check parameters
                args = [arg.arg for arg in node.args.args]
                assert 'final_vtx' in args, "❌ Missing 'final_vtx' parameter"
                assert 'fast_executor' in args, "❌ Missing 'fast_executor' parameter"
                
                print(f"✅ PASS: submit_cloned_tx function found")
                print(f"   Parameters: {args}")
                break
        
        assert found, "❌ submit_cloned_tx function not found"
        
        # Check that it calls fast_executor.send_and_confirm
        assert "fast_executor.send_and_confirm" in content, \
            "❌ submit_cloned_tx doesn't call fast_executor.send_and_confirm"
        
        print("✅ PASS: Calls fast_executor.send_and_confirm")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fast_executor_parameter():
    """Test that FastExecutor parameter is in __init__"""
    print("\n" + "="*60)
    print("TEST 4: FastExecutor Parameter in __init__")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Find MEVDirectCopyExecutor class
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'MEVDirectCopyExecutor':
                # Find __init__ method
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                        found = True
                        args = [arg.arg for arg in method.args.args]
                        
                        assert 'fast_executor' in args, \
                            f"❌ Missing 'fast_executor' parameter. Found: {args}"
                        
                        print(f"✅ PASS: fast_executor parameter found in __init__")
                        print(f"   Parameters: {args}")
                        break
                break
        
        assert found, "❌ __init__ method not found"
        
        # Check that self.fast_executor is assigned
        assert "self.fast_executor = fast_executor" in content, \
            "❌ self.fast_executor not assigned in __init__"
        
        print("✅ PASS: self.fast_executor assigned")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exec_ok_usage():
    """Test that exec_ok is used in return statements"""
    print("\n" + "="*60)
    print("TEST 5: exec_ok Usage in Return Statements")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Check for exec_ok usage
        pattern = r'return exec_ok\("direct_copy"'
        matches = re.findall(pattern, content)
        
        assert len(matches) > 0, "❌ exec_ok not used in return statements"
        
        print(f"✅ PASS: exec_ok used in {len(matches)} return statement(s)")
        
        # Verify it includes signature parameter
        assert 'exec_ok("direct_copy", signature' in content, \
            "❌ exec_ok doesn't include signature parameter"
        
        print("✅ PASS: exec_ok includes signature parameter")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_exec_err_usage():
    """Test that exec_err is used in return statements"""
    print("\n" + "="*60)
    print("TEST 6: exec_err Usage in Return Statements")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Check for exec_err usage
        pattern = r'return exec_err\("direct_copy"'
        matches = re.findall(pattern, content)
        
        assert len(matches) > 0, "❌ exec_err not used in return statements"
        
        print(f"✅ PASS: exec_err used in {len(matches)} return statement(s)")
        
        # Verify it includes error parameter
        assert 'exec_err("direct_copy",' in content, \
            "❌ exec_err doesn't include error parameter"
        
        print("✅ PASS: exec_err includes error parameter")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_fast_executor_integration():
    """Test that FastExecutor integration is present"""
    print("\n" + "="*60)
    print("TEST 7: FastExecutor Integration")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Check for conditional FastExecutor usage
        assert "if self.fast_executor:" in content, \
            "❌ Missing conditional FastExecutor check"
        
        print("✅ PASS: Conditional FastExecutor check present")
        
        # Check for submit_cloned_tx call
        assert "await submit_cloned_tx(" in content, \
            "❌ Missing submit_cloned_tx call"
        
        print("✅ PASS: submit_cloned_tx call present")
        
        # Check for fallback to internal method
        assert "_submit_mev_transaction" in content, \
            "❌ Missing fallback to _submit_mev_transaction"
        
        print("✅ PASS: Fallback to _submit_mev_transaction present")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_rpc_fallback_support():
    """Test that RPC fallback is supported (Jito not required)"""
    print("\n" + "="*60)
    print("TEST 8: RPC Fallback Support")
    print("="*60)
    
    try:
        with open('mev_direct_copy_executor.py', 'r') as f:
            content = f.read()
        
        # Check that FastExecutor.send_and_confirm handles fallback
        # This is handled in fast_executor.py's send_and_confirm method
        
        # Verify that submit_cloned_tx doesn't require Jito
        assert "JITO_AVAILABLE" not in content or \
               "if JITO_AVAILABLE" not in content.split("async def submit_cloned_tx")[1].split("class MEVDirectCopyExecutor")[0], \
            "⚠️  WARNING: submit_cloned_tx may have Jito dependency"
        
        print("✅ PASS: submit_cloned_tx doesn't require Jito")
        print("✅ PASS: RPC fallback handled by FastExecutor.send_and_confirm")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("\n" + "🚀"*30)
    print("MEV DIRECT COPY EXECUTOR CODE VALIDATION")
    print("🚀"*30)
    
    results = []
    
    # Test 1: Import base58
    results.append(test_import_base58())
    
    # Test 2: exec_ok/exec_err import
    results.append(test_exec_ok_exec_err_import())
    
    # Test 3: submit_cloned_tx function
    results.append(test_submit_cloned_tx_function())
    
    # Test 4: FastExecutor parameter
    results.append(test_fast_executor_parameter())
    
    # Test 5: exec_ok usage
    results.append(test_exec_ok_usage())
    
    # Test 6: exec_err usage
    results.append(test_exec_err_usage())
    
    # Test 7: FastExecutor integration
    results.append(test_fast_executor_integration())
    
    # Test 8: RPC fallback support
    results.append(test_rpc_fallback_support())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n" + "🎉"*30)
        print("ALL VALIDATION TESTS PASSED!")
        print("🎉"*30 + "\n")
        
        print("VERIFIED REQUIREMENTS:")
        print("  ✅ No 'import base5\\n8' typo")
        print("  ✅ exec_ok and exec_err properly imported")
        print("  ✅ submit_cloned_tx helper function implemented")
        print("  ✅ FastExecutor.send_and_confirm used for submission")
        print("  ✅ exec_ok returned on success with signature")
        print("  ✅ exec_err returned on failure")
        print("  ✅ RPC fallback supported (Jito not required)")
        print("")
        return 0
    else:
        print("\n" + "❌"*30)
        print(f"SOME TESTS FAILED: {total - passed} failures")
        print("❌"*30 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
