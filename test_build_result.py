#!/usr/bin/env python3
"""
Test BuildResult implementation to ensure no None returns from builders.
"""
import sys
from models.build_result import BuildResult

def test_build_result_creation():
    """Test that BuildResult can be created with all required fields"""
    print("Test 1: Creating BuildResult instances...")
    
    # Test failure case
    result_fail = BuildResult(
        ok=False, 
        tx=None, 
        reason="No route returned from Jupiter API",
        dex="jupiter",
        action="buy"
    )
    assert result_fail.ok == False, "Failed result should have ok=False"
    assert result_fail.tx is None, "Failed result should have tx=None"
    assert result_fail.reason == "No route returned from Jupiter API", "Reason should match"
    assert result_fail.dex == "jupiter", "DEX should match"
    assert result_fail.action == "buy", "Action should match"
    print("  ✅ Failure result created correctly")
    
    # Test success case
    result_success = BuildResult(
        ok=True,
        tx=None,  # Would be VersionedTransaction in real use
        dex="meteora",
        action="sell"
    )
    assert result_success.ok == True, "Success result should have ok=True"
    assert result_success.dex == "meteora", "DEX should match"
    assert result_success.action == "sell", "Action should match"
    print("  ✅ Success result created correctly")

def test_build_result_type_checking():
    """Test that BuildResult instances can be identified correctly"""
    print("\nTest 2: Type checking...")
    
    result = BuildResult(ok=False, tx=None, reason="Test", dex="jupiter", action="buy")
    assert isinstance(result, BuildResult), "Should be BuildResult instance"
    print("  ✅ Type checking works correctly")

def test_build_result_fields():
    """Test that BuildResult has all expected fields"""
    print("\nTest 3: Field validation...")
    
    result = BuildResult(
        ok=True, 
        tx=None, 
        reason="Success", 
        dex="meteora", 
        action="buy"
    )
    
    # Check all fields exist
    assert hasattr(result, 'ok'), "Should have 'ok' field"
    assert hasattr(result, 'tx'), "Should have 'tx' field"
    assert hasattr(result, 'reason'), "Should have 'reason' field"
    assert hasattr(result, 'dex'), "Should have 'dex' field"
    assert hasattr(result, 'action'), "Should have 'action' field"
    print("  ✅ All required fields present")

def test_build_result_optional_fields():
    """Test that BuildResult can be created with minimal fields"""
    print("\nTest 4: Optional fields...")
    
    # Create with just required fields
    result = BuildResult(ok=True, tx=None)
    assert result.ok == True, "ok field should be set"
    assert result.tx is None, "tx field should be None"
    assert result.reason is None, "reason should default to None"
    assert result.dex is None, "dex should default to None"
    assert result.action is None, "action should default to None"
    print("  ✅ Optional fields work correctly")

if __name__ == "__main__":
    try:
        test_build_result_creation()
        test_build_result_type_checking()
        test_build_result_fields()
        test_build_result_optional_fields()
        print("\n✅ All BuildResult tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
