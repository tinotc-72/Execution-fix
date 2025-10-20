#!/usr/bin/env python3
"""
Test Suite: ATA Enforcement Utilities
======================================

Tests for the new RPC-based ATA enforcement helpers that check ATA existence
and append creation instructions when necessary.
"""

import sys
from unittest.mock import Mock, patch
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction

# Import the new ATA enforcement utilities
from utils.ata_enforce import rpc_call, ata_exists, ensure_ata_ixs
from utils.ata import create_associated_token_account


def test_rpc_call():
    """Test the RPC call helper function."""
    print("=" * 80)
    print("TEST: rpc_call()")
    print("=" * 80)
    
    # Mock the requests.post response
    with patch('requests.post') as mock_post:
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"test": "data"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # Make RPC call
        result = rpc_call(
            "https://api.mainnet-beta.solana.com",
            "getBalance",
            ["11111111111111111111111111111111"]
        )
        
        # Verify
        assert "result" in result
        assert result["result"]["test"] == "data"
        print(f"✅ PASS: rpc_call returns expected response")
        print(f"   Response: {result}")
    
    print()


def test_ata_exists():
    """Test the ATA existence check function."""
    print("=" * 80)
    print("TEST: ata_exists()")
    print("=" * 80)
    
    owner = "11111111111111111111111111111111"
    mint = "So11111111111111111111111111111111111111112"
    
    # Test case 1: ATA exists (RPC returns accounts)
    print("\nTest case 1: ATA exists")
    with patch('utils.ata_enforce.rpc_call') as mock_rpc:
        mock_rpc.return_value = {
            "result": {
                "value": [
                    {"pubkey": "some_ata_address", "account": {}}
                ]
            }
        }
        
        exists = ata_exists("https://api.mainnet-beta.solana.com", owner, mint)
        assert exists is True
        print(f"✅ PASS: Returns True when RPC returns token accounts")
        print(f"   Owner: {owner}")
        print(f"   Mint: {mint}")
        print(f"   Exists: {exists}")
    
    # Test case 2: ATA doesn't exist (RPC returns empty array)
    print("\nTest case 2: ATA doesn't exist")
    with patch('utils.ata_enforce.rpc_call') as mock_rpc:
        mock_rpc.return_value = {
            "result": {
                "value": []
            }
        }
        
        exists = ata_exists("https://api.mainnet-beta.solana.com", owner, mint)
        assert exists is False
        print(f"✅ PASS: Returns False when RPC returns empty array")
        print(f"   Exists: {exists}")
    
    # Test case 3: RPC error (should return False to be safe)
    print("\nTest case 3: RPC error handling")
    with patch('utils.ata_enforce.rpc_call') as mock_rpc:
        mock_rpc.side_effect = Exception("RPC error")
        
        exists = ata_exists("https://api.mainnet-beta.solana.com", owner, mint)
        assert exists is False
        print(f"✅ PASS: Returns False on RPC error (safe default)")
        print(f"   Exists: {exists}")
    
    print()


def test_ensure_ata_ixs():
    """Test the ensure_ata_ixs wrapper function."""
    print("=" * 80)
    print("TEST: ensure_ata_ixs()")
    print("=" * 80)
    
    wallet = Keypair()
    payer = wallet.pubkey()
    owner = wallet.pubkey()
    mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
    
    # Test case 1: ATA exists (should return empty list)
    print("\nTest case 1: ATA exists - no instructions needed")
    with patch('utils.ata_enforce.ata_exists') as mock_exists:
        mock_exists.return_value = True
        
        instructions = ensure_ata_ixs(
            "https://api.mainnet-beta.solana.com",
            payer,
            owner,
            mint,
            create_associated_token_account
        )
        
        assert len(instructions) == 0
        print(f"✅ PASS: Returns empty list when ATA exists")
        print(f"   Payer: {payer}")
        print(f"   Owner: {owner}")
        print(f"   Mint: {mint}")
        print(f"   Instructions returned: {len(instructions)}")
    
    # Test case 2: ATA doesn't exist (should return creation instruction)
    print("\nTest case 2: ATA doesn't exist - creation instruction needed")
    with patch('utils.ata_enforce.ata_exists') as mock_exists:
        mock_exists.return_value = False
        
        instructions = ensure_ata_ixs(
            "https://api.mainnet-beta.solana.com",
            payer,
            owner,
            mint,
            create_associated_token_account
        )
        
        assert len(instructions) == 1
        assert isinstance(instructions[0], Instruction)
        print(f"✅ PASS: Returns ATA creation instruction when ATA doesn't exist")
        print(f"   Instructions returned: {len(instructions)}")
        print(f"   Instruction type: {type(instructions[0]).__name__}")
        print(f"   Instruction program_id: {instructions[0].program_id}")
    
    print()


def test_integration_concept():
    """
    Demonstrate the complete integration concept with a DEX executor.
    """
    print("=" * 80)
    print("INTEGRATION CONCEPT: Using ensure_ata_ixs in a DEX Executor")
    print("=" * 80)
    
    wallet = Keypair()
    token_mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
    rpc_url = "https://api.mainnet-beta.solana.com"
    
    print(f"\nWallet: {wallet.pubkey()}")
    print(f"Token Mint: {token_mint}")
    print(f"RPC URL: {rpc_url}")
    
    # Mock scenario: Building a buy transaction
    print("\n" + "-" * 80)
    print("SCENARIO: Building a buy transaction (SOL -> Token)")
    print("-" * 80)
    
    with patch('utils.ata_enforce.ata_exists') as mock_exists:
        # Simulate ATA doesn't exist yet
        mock_exists.return_value = False
        
        # Get ATA creation instructions
        ata_instructions = ensure_ata_ixs(
            rpc_url,
            wallet.pubkey(),
            wallet.pubkey(),
            token_mint,
            create_associated_token_account
        )
        
        print(f"\nStep 1: Check if output token ATA exists")
        print(f"   ATA exists: {mock_exists.return_value}")
        
        print(f"\nStep 2: Get ATA creation instructions if needed")
        print(f"   Instructions to prepend: {len(ata_instructions)}")
        
        if ata_instructions:
            print(f"   Instruction[0] program_id: {ata_instructions[0].program_id}")
            print(f"   Instruction[0] accounts: {len(ata_instructions[0].accounts)}")
        
        print(f"\nStep 3: Build final transaction")
        print(f"   Transaction would contain:")
        print(f"   - Compute budget instructions")
        print(f"   - ATA creation instruction (if needed): {len(ata_instructions)}")
        print(f"   - Swap instruction")
        
        print(f"\n✅ Integration concept validated")
        print(f"   Before swap: ATA creation is ensured")
        print(f"   Transaction will not fail due to missing ATA")
    
    print()


def run_all_tests():
    """Run all test functions."""
    print("\n" + "=" * 80)
    print("ATA ENFORCEMENT UTILITIES TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        test_rpc_call()
        test_ata_exists()
        test_ensure_ata_ixs()
        test_integration_concept()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
