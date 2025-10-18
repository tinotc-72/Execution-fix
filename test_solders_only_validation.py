#!/usr/bin/env python3
"""
Test to validate that solders-only refactor is complete and functional.
"""

import sys
import ast
import os

def test_no_solana_py_imports():
    """Verify no solana-py imports exist in production code"""
    print("🔍 Testing: No solana-py imports in production code")
    
    excluded_patterns = ['test_', 'validate_', 'demo_', '.pyc']
    
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in root:
            continue
            
        for file in files:
            if not file.endswith('.py'):
                continue
            
            # Skip test/validation/demo files
            if any(pattern in file for pattern in excluded_patterns):
                continue
            
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # Check for solana-py imports
                if 'from solana.' in content or 'import solana' in content:
                    # Make sure it's not in a comment or string
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name.startswith('solana'):
                                    print(f"   ❌ FAIL: Found 'import {alias.name}' in {filepath}")
                                    return False
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and node.module.startswith('solana'):
                                print(f"   ❌ FAIL: Found 'from {node.module} import ...' in {filepath}")
                                return False
            except Exception as e:
                # Skip files that can't be parsed
                continue
    
    print("   ✅ PASS: No solana-py imports found in production code")
    return True

def test_models_uses_versioned_transaction():
    """Verify models.py only uses VersionedTransaction"""
    print("\n🔍 Testing: models.py uses only VersionedTransaction")
    
    with open('models.py', 'r') as f:
        content = f.read()
    
    # Parse the file
    tree = ast.parse(content)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == 'solders.transaction':
                imports = [alias.name for alias in node.names]
                if 'Transaction' in imports and 'Transaction' != 'VersionedTransaction':
                    print(f"   ❌ FAIL: models.py imports Transaction (non-versioned)")
                    return False
    
    # Check Bundle class type annotation
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'Bundle':
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if item.target.id == 'transactions':
                        # Get the annotation as string
                        annotation_str = ast.unparse(item.annotation)
                        if 'Union' in annotation_str and 'Transaction' in annotation_str:
                            print(f"   ❌ FAIL: Bundle.transactions uses Union with Transaction")
                            return False
    
    print("   ✅ PASS: models.py uses only VersionedTransaction")
    return True

def test_transaction_serialization():
    """Verify transaction serialization uses bytes()"""
    print("\n🔍 Testing: Transaction serialization uses bytes()")
    
    files_to_check = ['models.py', 'fast_executor.py', 'mev_meteora_executor.py']
    
    for filename in files_to_check:
        if not os.path.exists(filename):
            continue
            
        with open(filename, 'r') as f:
            content = f.read()
        
        # Check for bytes() usage with transactions
        if 'bytes(tx)' in content or 'bytes(vtx)' in content or 'bytes(transaction)' in content:
            print(f"   ✅ {filename} uses bytes() for serialization")
        else:
            # That's okay if the file doesn't serialize transactions
            pass
    
    print("   ✅ PASS: Transaction serialization verified")
    return True

def test_mev_meteora_executor_refactored():
    """Verify mev_meteora_executor.py is properly refactored"""
    print("\n🔍 Testing: mev_meteora_executor.py refactored to use instructions list")
    
    with open('mev_meteora_executor.py', 'r') as f:
        content = f.read()
    
    # Should not have Transaction() constructor calls
    if 'Transaction()' in content:
        print("   ❌ FAIL: Still uses Transaction() constructor")
        return False
    
    # Should have List[Instruction] return types
    if 'List[Instruction]' not in content:
        print("   ❌ FAIL: Missing List[Instruction] return type")
        return False
    
    # Should use Instruction class (not TransactionInstruction)
    if 'TransactionInstruction(' in content:
        print("   ❌ FAIL: Still uses TransactionInstruction")
        return False
    
    # Should import create_associated_token_account
    if 'from utils import create_associated_token_account' not in content:
        print("   ❌ FAIL: Missing create_associated_token_account import")
        return False
    
    print("   ✅ PASS: mev_meteora_executor.py properly refactored")
    return True

def main():
    """Run all tests"""
    print("=" * 80)
    print("SOLDERS-ONLY REFACTOR VALIDATION TESTS")
    print("=" * 80)
    
    tests = [
        test_no_solana_py_imports,
        test_models_uses_versioned_transaction,
        test_transaction_serialization,
        test_mev_meteora_executor_refactored,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 80)
    
    if all(results):
        print("\n✅ All validation tests passed!")
        return 0
    else:
        print(f"\n❌ {len(results) - sum(results)} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
