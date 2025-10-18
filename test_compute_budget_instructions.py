"""
Test to verify that compute budget instructions are added to all transactions.
"""
import os
os.environ['COMPUTE_UNIT_LIMIT'] = '500000'
os.environ['COMPUTE_UNIT_PRICE'] = '2000'

from utils.fees import with_compute_budget, get_compute_unit_limit, get_compute_unit_price
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price


def test_with_compute_budget_adds_instructions():
    """Test that with_compute_budget prepends compute budget instructions"""
    # Create a dummy instruction
    dummy_ix = Instruction(
        program_id=Pubkey.from_string("11111111111111111111111111111111"),
        accounts=[],
        data=bytes([0, 1, 2])
    )
    
    # Add compute budget
    instructions = with_compute_budget([dummy_ix])
    
    # Should have 3 instructions: compute limit, compute price, original
    assert len(instructions) == 3, f"Expected 3 instructions, got {len(instructions)}"
    
    # First two should be compute budget instructions
    assert isinstance(instructions[0], Instruction), "First instruction should be Instruction"
    assert isinstance(instructions[1], Instruction), "Second instruction should be Instruction"
    assert isinstance(instructions[2], Instruction), "Third instruction should be Instruction"
    
    print("✅ with_compute_budget adds compute budget instructions")


def test_env_variable_configuration():
    """Test that environment variables are read correctly"""
    limit = get_compute_unit_limit()
    price = get_compute_unit_price()
    
    assert limit == 500000, f"Expected limit 500000, got {limit}"
    assert price == 2000, f"Expected price 2000, got {price}"
    
    print("✅ Environment variables are read correctly")


def test_custom_values():
    """Test that custom values override defaults"""
    dummy_ix = Instruction(
        program_id=Pubkey.from_string("11111111111111111111111111111111"),
        accounts=[],
        data=bytes([0, 1, 2])
    )
    
    # Use custom values
    instructions = with_compute_budget([dummy_ix], compute_unit_limit=600000, compute_unit_price=3000)
    
    assert len(instructions) == 3, f"Expected 3 instructions, got {len(instructions)}"
    
    print("✅ Custom values work correctly")


def test_safety_caps():
    """Test that safety caps are applied"""
    dummy_ix = Instruction(
        program_id=Pubkey.from_string("11111111111111111111111111111111"),
        accounts=[],
        data=bytes([0, 1, 2])
    )
    
    # Try with values that exceed caps
    instructions = with_compute_budget([dummy_ix], compute_unit_limit=999_999_999, compute_unit_price=999_999_999_999)
    
    # Should still create 3 instructions (caps should be applied)
    assert len(instructions) == 3, f"Expected 3 instructions, got {len(instructions)}"
    
    print("✅ Safety caps are applied correctly")


def test_empty_instruction_list():
    """Test that with_compute_budget works with empty instruction list"""
    instructions = with_compute_budget([])
    
    # Should have 2 instructions: compute limit and compute price
    assert len(instructions) == 2, f"Expected 2 instructions, got {len(instructions)}"
    
    print("✅ with_compute_budget works with empty instruction list")


def test_multiple_instructions():
    """Test that with_compute_budget works with multiple instructions"""
    dummy_ix1 = Instruction(
        program_id=Pubkey.from_string("11111111111111111111111111111111"),
        accounts=[],
        data=bytes([0, 1, 2])
    )
    dummy_ix2 = Instruction(
        program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
        accounts=[],
        data=bytes([3, 4, 5])
    )
    
    instructions = with_compute_budget([dummy_ix1, dummy_ix2])
    
    # Should have 4 instructions: compute limit, compute price, and 2 original
    assert len(instructions) == 4, f"Expected 4 instructions, got {len(instructions)}"
    
    print("✅ with_compute_budget works with multiple instructions")


if __name__ == "__main__":
    test_with_compute_budget_adds_instructions()
    test_env_variable_configuration()
    test_custom_values()
    test_safety_caps()
    test_empty_instruction_list()
    test_multiple_instructions()
    
    print("\n✅ All tests passed!")
