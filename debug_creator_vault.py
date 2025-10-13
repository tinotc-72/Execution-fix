#!/usr/bin/env python3
"""
Debug script to test different creator_vault PDA derivations
"""

from solders.pubkey import Pubkey

# Define the program IDs
PUMP_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
MEV_ROUTER_PROGRAM_ID = Pubkey.from_string("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW")

# The token mint from the test
token_mint = Pubkey.from_string("8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump")

# Expected value from error log (what the program wants)
expected = "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ"

print("🔍 Testing different creator_vault PDA derivations:")
print(f"Token mint: {token_mint}")
print(f"Expected: {expected}")
print()

# Test different patterns and program IDs
patterns = [
    ([b"creator", bytes(token_mint)], PUMP_PROGRAM_ID, "creator + mint with PUMP_PROGRAM"),
    ([b"creator", bytes(token_mint)], MEV_ROUTER_PROGRAM_ID, "creator + mint with MEV_ROUTER"),
    ([b"creator_vault", bytes(token_mint)], PUMP_PROGRAM_ID, "creator_vault + mint with PUMP_PROGRAM"),
    ([b"creator_vault", bytes(token_mint)], MEV_ROUTER_PROGRAM_ID, "creator_vault + mint with MEV_ROUTER"),
    ([bytes(token_mint), b"creator"], PUMP_PROGRAM_ID, "mint + creator with PUMP_PROGRAM"),
    ([bytes(token_mint), b"creator"], MEV_ROUTER_PROGRAM_ID, "mint + creator with MEV_ROUTER"),
    ([b"vault", bytes(token_mint)], PUMP_PROGRAM_ID, "vault + mint with PUMP_PROGRAM"),
    ([b"vault", bytes(token_mint)], MEV_ROUTER_PROGRAM_ID, "vault + mint with MEV_ROUTER"),
]

for i, (seeds, program_id, description) in enumerate(patterns):
    try:
        creator_vault, bump = Pubkey.find_program_address(seeds, program_id)
        match = "✅ MATCH!" if str(creator_vault) == expected else "❌ No match"
        print(f"{i+1:2d}. {description}")
        print(f"    Result: {creator_vault} (bump: {bump}) {match}")
        print()
    except Exception as e:
        print(f"{i+1:2d}. {description}")
        print(f"    Error: {e}")
        print()

# Also test the current implementation (what generates the "Left" value)
try:
    current_wrong, bump = Pubkey.find_program_address([b"creator", bytes(token_mint)], MEV_ROUTER_PROGRAM_ID)
    print(f"Current implementation result: {current_wrong} (bump: {bump})")
    if str(current_wrong) == "G592hY74eYuFFqWiwHWfvvUx6JjMnj87MsuAGeqqgGou":
        print("✅ This matches the 'Left' value from the error log!")
    else:
        print("❌ This doesn't match the 'Left' value from the error log")
except Exception as e:
    print(f"Current implementation error: {e}")