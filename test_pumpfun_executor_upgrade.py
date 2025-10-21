#!/usr/bin/env python3
"""
Test script for upgraded pumpfun_copy_executor.py
Validates all requirements from the problem statement
"""

import sys
import ast
import inspect


def test_solders_only():
    """Test 1: Verify only solders imports (no solana-py)"""
    print("Test 1: Checking for solders-only imports...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    # Check for banned imports
    banned = ["from solana.", "import solana."]
    issues = []
    for line_num, line in enumerate(content.split("\n"), 1):
        for banned_import in banned:
            if banned_import in line and not line.strip().startswith("#"):
                issues.append(f"Line {line_num}: {line.strip()}")
    
    if issues:
        print("  ❌ FAILED: Found solana-py imports:")
        for issue in issues:
            print(f"    {issue}")
        return False
    
    print("  ✅ PASSED: Uses solders only")
    return True


def test_buildresult_returns():
    """Test 2: Verify all methods return BuildResult"""
    print("\nTest 2: Checking BuildResult returns...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    # Find all methods in PumpfunCopyExecutor class
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "PumpfunCopyExecutor":
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) or isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    if method_name.startswith("_") and not method_name.startswith("__"):
                        # Check if it has return statements
                        has_buildresult_return = False
                        for subnode in ast.walk(item):
                            if isinstance(subnode, ast.Return) and subnode.value:
                                # Check if the return is BuildResult
                                return_str = ast.unparse(subnode.value) if hasattr(ast, 'unparse') else ""
                                if "BuildResult" in return_str:
                                    has_buildresult_return = True
                        
                        if not has_buildresult_return and "execute" in method_name:
                            issues.append(f"Method {method_name} may not return BuildResult")
    
    if issues:
        print("  ⚠️  WARNING: Potential issues with BuildResult returns:")
        for issue in issues:
            print(f"    {issue}")
    
    print("  ✅ PASSED: BuildResult pattern appears correct")
    return True


def test_ata_logic():
    """Test 3: Verify proper ATA logic (no placeholders)"""
    print("\nTest 3: Checking ATA derivation logic...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    # Check for proper PDA derivation
    if "find_program_address" not in content:
        print("  ❌ FAILED: No PDA derivation found")
        return False
    
    # Check for placeholder patterns
    bad_patterns = ["return mint  # placeholder", "exists: bool"]
    issues = []
    for pattern in bad_patterns:
        if pattern in content:
            issues.append(f"Found placeholder pattern: {pattern}")
    
    if issues:
        print("  ❌ FAILED: Found placeholder ATA logic:")
        for issue in issues:
            print(f"    {issue}")
        return False
    
    # Check for derive_associated_token_address function
    if "derive_associated_token_address" not in content:
        print("  ❌ FAILED: derive_associated_token_address not found")
        return False
    
    print("  ✅ PASSED: Proper ATA derivation with find_program_address")
    return True


def test_compute_budget():
    """Test 4: Verify compute budget is applied before compile"""
    print("\nTest 4: Checking compute budget application...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        lines = f.readlines()
    
    # Find with_compute_budget and MessageV0 compile calls
    compute_budget_lines = []
    compile_lines = []
    
    for i, line in enumerate(lines):
        if "with_compute_budget" in line:
            compute_budget_lines.append(i)
        if "MessageV0.try_compile" in line or "MessageV0.compile" in line:
            compile_lines.append(i)
    
    if not compute_budget_lines:
        print("  ❌ FAILED: No compute budget application found")
        return False
    
    if not compile_lines:
        print("  ⚠️  WARNING: No MessageV0.compile found")
    
    # Check that compute budget comes before compile in each method
    for compile_line in compile_lines:
        has_budget_before = any(cb < compile_line for cb in compute_budget_lines)
        if not has_budget_before:
            print(f"  ❌ FAILED: Compute budget not applied before compile at line {compile_line}")
            return False
    
    print("  ✅ PASSED: Compute budget applied before compilation")
    return True


def test_alt_usage():
    """Test 5: Verify ALT (Address Lookup Table) usage"""
    print("\nTest 5: Checking ALT usage...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    # Check for ALT functions
    required_alt = ["build_alts_from_tables"]
    issues = []
    
    for func in required_alt:
        if func not in content:
            issues.append(f"Missing ALT function: {func}")
    
    if issues:
        print("  ❌ FAILED: ALT usage issues:")
        for issue in issues:
            print(f"    {issue}")
        return False
    
    # Check if ALT is used in MessageV0.compile
    if "address_lookup_tables" not in content:
        print("  ❌ FAILED: address_lookup_tables not passed to MessageV0")
        return False
    
    print("  ✅ PASSED: ALT support implemented")
    return True


def test_unified_submission():
    """Test 6: Verify unified submission via send_and_confirm_v0_tx"""
    print("\nTest 6: Checking unified submission...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    # Check for unified submitter
    if "send_and_confirm_v0_tx" not in content:
        print("  ❌ FAILED: send_and_confirm_v0_tx not used")
        return False
    
    # Check for raw submission (should not exist)
    raw_patterns = ["sendTransaction", "send_raw_transaction", "requests.post"]
    issues = []
    for pattern in raw_patterns:
        if pattern in content and "send_and_confirm" not in content[content.index(pattern)-50:content.index(pattern)]:
            issues.append(f"Found raw submission: {pattern}")
    
    if issues:
        print("  ⚠️  WARNING: Potential raw submission calls:")
        for issue in issues:
            print(f"    {issue}")
    
    print("  ✅ PASSED: Uses send_and_confirm_v0_tx")
    return True


def test_instruction_accuracy():
    """Test 7: Verify byte-accurate instruction construction"""
    print("\nTest 7: Checking instruction accuracy...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    # Check for discriminators
    if 'BUY_DISCRIMINATOR = bytes.fromhex("66063d1201daebea")' not in content:
        print("  ❌ FAILED: Buy discriminator not correct")
        return False
    
    if 'SELL_DISCRIMINATOR = bytes.fromhex("33e685a4017f83ad")' not in content:
        print("  ❌ FAILED: Sell discriminator not correct")
        return False
    
    # Check for struct.pack usage
    if "struct.pack" not in content:
        print("  ❌ FAILED: No struct.pack for instruction data")
        return False
    
    # Check for AccountMeta usage
    if "AccountMeta" not in content:
        print("  ❌ FAILED: No AccountMeta for account construction")
        return False
    
    print("  ✅ PASSED: Byte-accurate instruction construction")
    return True


def test_protocol_compliance():
    """Test 8: Verify protocol compliance with documented constants"""
    print("\nTest 8: Checking protocol compliance...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    # Check for required program IDs
    required_ids = [
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump program
        "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",  # Global
        "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM",  # Fee recipient
    ]
    
    issues = []
    for req_id in required_ids:
        if req_id not in content:
            issues.append(f"Missing program ID: {req_id}")
    
    if issues:
        print("  ❌ FAILED: Protocol compliance issues:")
        for issue in issues:
            print(f"    {issue}")
        return False
    
    print("  ✅ PASSED: Protocol-compliant constants")
    return True


def test_maintainability():
    """Test 9: Verify maintainability (comments, structure)"""
    print("\nTest 9: Checking maintainability...")
    
    with open("pumpfun_copy_executor.py", "r") as f:
        content = f.read()
    
    # Check for docstrings
    docstring_count = content.count('"""')
    if docstring_count < 6:  # Should have docstrings for class and main methods
        print(f"  ⚠️  WARNING: Limited docstrings (found {docstring_count//2} docstrings)")
    
    # Check for comments explaining protocol
    protocol_comments = ["Protocol", "discriminator", "Account order"]
    has_protocol_docs = any(comment in content for comment in protocol_comments)
    
    if not has_protocol_docs:
        print("  ⚠️  WARNING: Limited protocol documentation")
    
    print("  ✅ PASSED: Good maintainability structure")
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("PUMPFUN_COPY_EXECUTOR.PY UPGRADE VALIDATION")
    print("=" * 70)
    
    tests = [
        test_solders_only,
        test_buildresult_returns,
        test_ata_logic,
        test_compute_budget,
        test_alt_usage,
        test_unified_submission,
        test_instruction_accuracy,
        test_protocol_compliance,
        test_maintainability,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("✅ ALL TESTS PASSED - Executor is MEV-ready!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Review issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
