#!/usr/bin/env python3

from solders.pubkey import Pubkey
import asyncio

def test_creator_vault_derivation():
    """Test different PDA derivation patterns for creator_vault"""
    mint = Pubkey.from_string("8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    
    print(f"🔍 Testing creator_vault derivation for mint: {mint}")
    print(f"🎯 Target creator_vault: J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ")
    
    # Test common PDA patterns
    patterns = [
        [b"creator", bytes(mint)],
        [b"creator_vault", bytes(mint)],
        [b"creator-vault", bytes(mint)],
        [b"vault", bytes(mint)],
        [b"mint", bytes(mint)],
        [bytes(mint)],
        [b"bonding-curve", bytes(mint)],
    ]
    
    for i, seeds in enumerate(patterns):
        try:
            pda, bump = Pubkey.find_program_address(seeds, pump_program)
            print(f"Pattern {i+1}: {seeds} -> {pda}")
            if str(pda) == "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ":
                print(f"✅ MATCH FOUND! Pattern {i+1}: {seeds}")
                return
        except Exception as e:
            print(f"Pattern {i+1} failed: {e}")
    
    print("❌ No matching pattern found")

if __name__ == "__main__":
    test_creator_vault_derivation()