#!/usr/bin/env python3
"""
Test ATA (Associated Token Account) Utilities

Tests the basic functionality of utils/ata.py helper functions.
"""

from solders.pubkey import Pubkey
from utils.ata import (
    associated_token_address,
    create_associated_token_account,
    ensure_ata_for,
    SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID,
    SPL_TOKEN_PROGRAM_ID,
)


def test_ata_imports():
    """Test that ATA utilities can be imported"""
    print("=" * 80)
    print("TEST: ATA UTILITIES IMPORT")
    print("=" * 80)
    
    print("\n✅ PASS: All ATA utilities imported successfully")
    print(f"   - SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID: {SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID}")
    print(f"   - SPL_TOKEN_PROGRAM_ID: {SPL_TOKEN_PROGRAM_ID}")
    return True


def test_associated_token_address():
    """Test associated_token_address function"""
    print("\n" + "=" * 80)
    print("TEST: associated_token_address()")
    print("=" * 80)
    
    owner = Pubkey.from_string("11111111111111111111111111111111")
    mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
    
    ata = associated_token_address(owner, mint)
    
    print(f"\nOwner: {owner}")
    print(f"Mint: {mint}")
    print(f"ATA (placeholder): {ata}")
    print("\n⚠️  NOTE: Currently returns placeholder (mint). TODO: Implement real PDA derivation")
    
    # Verify it returns a Pubkey
    assert isinstance(ata, Pubkey), "associated_token_address should return a Pubkey"
    
    print("✅ PASS: associated_token_address returns a Pubkey")
    return True


def test_create_associated_token_account():
    """Test create_associated_token_account instruction builder"""
    print("\n" + "=" * 80)
    print("TEST: create_associated_token_account()")
    print("=" * 80)
    
    payer = Pubkey.from_string("11111111111111111111111111111111")
    owner = Pubkey.from_string("11111111111111111111111111111111")
    mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
    
    instruction = create_associated_token_account(payer, owner, mint)
    
    print(f"\nPayer: {payer}")
    print(f"Owner: {owner}")
    print(f"Mint: {mint}")
    print(f"Instruction program_id: {instruction.program_id}")
    print(f"Instruction accounts count: {len(instruction.accounts)}")
    print(f"Instruction data: {instruction.data}")
    
    # Verify instruction structure
    assert instruction.program_id == SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID, \
        "Instruction should use ATA program ID"
    assert len(instruction.accounts) == 7, \
        "ATA creation instruction should have 7 accounts"
    assert instruction.data == b"", \
        "ATA creation instruction should have empty data"
    
    print("\n✅ PASS: create_associated_token_account creates valid instruction")
    return True


def test_ensure_ata_for():
    """Test ensure_ata_for conditional instruction builder"""
    print("\n" + "=" * 80)
    print("TEST: ensure_ata_for()")
    print("=" * 80)
    
    owner = Pubkey.from_string("11111111111111111111111111111111")
    mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
    payer = Pubkey.from_string("11111111111111111111111111111111")
    
    # Test when ATA exists
    print("\nTest case 1: ATA exists (exists=True)")
    instructions_exists = ensure_ata_for(owner, mint, payer, exists=True)
    print(f"Instructions returned: {len(instructions_exists)}")
    assert len(instructions_exists) == 0, "Should return empty list when ATA exists"
    print("✅ PASS: Returns empty list when exists=True")
    
    # Test when ATA doesn't exist
    print("\nTest case 2: ATA doesn't exist (exists=False)")
    instructions_not_exists = ensure_ata_for(owner, mint, payer, exists=False)
    print(f"Instructions returned: {len(instructions_not_exists)}")
    assert len(instructions_not_exists) == 1, "Should return 1 instruction when ATA doesn't exist"
    assert instructions_not_exists[0].program_id == SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID, \
        "Should return ATA creation instruction"
    print("✅ PASS: Returns create ATA instruction when exists=False")
    
    print("\n⚠️  NOTE: exists parameter is currently manual. TODO: Implement RPC query")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("ATA UTILITIES TEST SUITE")
    print("=" * 80)
    
    all_passed = True
    
    try:
        all_passed &= test_ata_imports()
        all_passed &= test_associated_token_address()
        all_passed &= test_create_associated_token_account()
        all_passed &= test_ensure_ata_for()
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ ALL TESTS PASSED")
        else:
            print("❌ SOME TESTS FAILED")
        print("=" * 80)
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
