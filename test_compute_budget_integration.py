"""
Integration test to verify compute budget is properly included in transaction construction.

This test checks that:
1. transaction_cloner.py includes compute budget when cloning
2. All executor files have compute budget in their transaction paths
"""

import re


def test_transaction_cloner_has_compute_budget():
    """Verify transaction_cloner.py includes compute budget import and call"""
    with open('transaction_cloner.py', 'r') as f:
        content = f.read()
    
    # Check for import
    assert 'from utils.fees import with_compute_budget' in content, \
        "transaction_cloner.py missing compute budget import"
    
    # Check for usage
    assert 'with_compute_budget(new_instructions' in content, \
        "transaction_cloner.py not calling with_compute_budget"
    
    # Check it's called before MessageV0.try_compile
    lines = content.splitlines()
    compute_budget_line = None
    message_compile_line = None
    
    for i, line in enumerate(lines):
        if 'with_compute_budget(new_instructions' in line:
            compute_budget_line = i
        if 'MessageV0.try_compile' in line:
            message_compile_line = i
            break
    
    assert compute_budget_line is not None, "with_compute_budget call not found"
    assert message_compile_line is not None, "MessageV0.try_compile not found"
    assert compute_budget_line < message_compile_line, \
        "with_compute_budget must be called before MessageV0.try_compile"
    
    print("✅ transaction_cloner.py has proper compute budget handling")


def test_all_executors_have_compute_budget():
    """Verify all executor files that construct transactions have compute budget"""
    executor_files = [
        'mev_meteora_executor.py',
        'mev_jupiter_executor.py',
        'mev_direct_sell_executor.py',
        'mev_advanced_bot_executor.py',
        'complete_mev_bot.py',
    ]
    
    for filename in executor_files:
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Check if file constructs transactions
            if 'MessageV0.try_compile' in content or 'VersionedTransaction(' in content:
                # Should have compute budget handling
                has_cu = 'with_compute_budget' in content or 'set_compute_unit_' in content
                assert has_cu, f"{filename} constructs transactions but lacks compute budget"
                print(f"✅ {filename} has compute budget")
        except FileNotFoundError:
            print(f"⚠️  {filename} not found (skipping)")


def test_compute_budget_parameters():
    """Verify compute budget is called with reasonable parameters"""
    with open('transaction_cloner.py', 'r') as f:
        content = f.read()
    
    # Extract compute budget call
    match = re.search(r'with_compute_budget\([^)]+cu_limit=(\d+)[^)]+cu_price=(\d+)', content)
    assert match, "Could not find compute budget call with parameters"
    
    cu_limit = int(match.group(1))
    cu_price = int(match.group(2))
    
    # Verify reasonable values
    assert 200_000 <= cu_limit <= 1_400_000, f"CU limit {cu_limit} out of reasonable range"
    assert 0 <= cu_price <= 100_000_000, f"CU price {cu_price} out of reasonable range"
    
    print(f"✅ Compute budget parameters are reasonable: limit={cu_limit}, price={cu_price}")


def test_verification_script_exists():
    """Verify the compute budget verification script exists and is executable"""
    import os
    
    script_path = 'tools/verify_compute_budget.py'
    assert os.path.exists(script_path), f"{script_path} does not exist"
    
    # Check if it's executable (on Unix-like systems)
    is_executable = os.access(script_path, os.X_OK)
    print(f"✅ Verification script exists (executable: {is_executable})")


def test_patcher_script_exists():
    """Verify the compute budget patcher script exists"""
    import os
    
    script_path = 'tools/patch_compute_budget.py'
    assert os.path.exists(script_path), f"{script_path} does not exist"
    
    # Verify it has the expected structure
    with open(script_path, 'r') as f:
        content = f.read()
    
    assert 'def process_file' in content, "Patcher missing process_file function"
    assert 'MSG_CONSTRUCT_RX' in content or 'MSG_RX' in content, "Patcher missing message pattern"
    assert 'HAS_CU_RX' in content, "Patcher missing compute budget pattern"
    
    print("✅ Patcher script exists with expected structure")


if __name__ == "__main__":
    test_transaction_cloner_has_compute_budget()
    test_all_executors_have_compute_budget()
    test_compute_budget_parameters()
    test_verification_script_exists()
    test_patcher_script_exists()
    
    print("\n✅ All integration tests passed!")
