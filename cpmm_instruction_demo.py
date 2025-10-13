#!/usr/bin/env python3
"""
CPMM Instruction Format Demonstration
This shows the exact instruction format you need for your copy bot
"""

import struct
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction

# CPMM Program ID (Real program on mainnet)
CPMM_PROGRAM_ID = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

def build_cpmm_instruction_for_copy_bot(
    pool_state: str,
    pool_authority: str,
    base_vault: str,
    quote_vault: str,
    token_mint: str,
    user_wallet: str,
    user_source_ata: str,
    user_dest_ata: str,
    amount_in: int,
    min_amount_out: int
) -> Instruction:
    """
    Build CPMM instruction for your copy bot
    
    This is the EXACT format you need for ANY CPMM pool!
    Just change the addresses for different tokens.
    """
    
    # Convert string addresses to Pubkey objects
    pool_state_pubkey = Pubkey.from_string(pool_state)
    pool_authority_pubkey = Pubkey.from_string(pool_authority)
    base_vault_pubkey = Pubkey.from_string(base_vault)
    quote_vault_pubkey = Pubkey.from_string(quote_vault)
    token_mint_pubkey = Pubkey.from_string(token_mint)
    user_wallet_pubkey = Pubkey.from_string(user_wallet)
    user_source_ata_pubkey = Pubkey.from_string(user_source_ata)
    user_dest_ata_pubkey = Pubkey.from_string(user_dest_ata)
    
    # ✅ CPMM Standard Account Structure
    accounts = [
        AccountMeta(pool_state_pubkey, False, True),        # 0. Pool state
        AccountMeta(pool_authority_pubkey, False, False),   # 1. Pool authority
        AccountMeta(SOL_MINT, False, False),                # 2. Base mint (SOL)
        AccountMeta(token_mint_pubkey, False, False),       # 3. Quote mint (Token)
        AccountMeta(base_vault_pubkey, False, True),        # 4. Base vault (SOL)
        AccountMeta(quote_vault_pubkey, False, True),       # 5. Quote vault (Token)
        AccountMeta(user_source_ata_pubkey, False, True),   # 6. User source ATA
        AccountMeta(user_dest_ata_pubkey, False, True),     # 7. User destination ATA
        AccountMeta(user_wallet_pubkey, True, False),       # 8. User wallet (signer)
        AccountMeta(TOKEN_PROGRAM_ID, False, False),        # 9. Token program
    ]
    
    # ✅ CPMM Standard Instruction Data
    discriminator = 0  # Swap instruction
    instruction_data = struct.pack("<BQQ", discriminator, amount_in, min_amount_out)
    
    # ✅ Build the instruction
    instruction = Instruction(
        program_id=CPMM_PROGRAM_ID,
        data=instruction_data,
        accounts=accounts
    )
    
    return instruction

def demonstrate_cpmm_for_copy_bot():
    """Demonstrate CPMM instruction building for copy bot"""
    
    print("🎯 CPMM Instruction Format for Copy Bot")
    print("=" * 50)
    
    # Example pool addresses (these would be real addresses for actual pools)
    example_pool_config = {
        "pool_state": "11111111111111111111111111111112",
        "pool_authority": "11111111111111111111111111111113", 
        "base_vault": "11111111111111111111111111111114",
        "quote_vault": "11111111111111111111111111111115",
        "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "user_wallet": "11111111111111111111111111111116",
        "user_source_ata": "11111111111111111111111111111117",
        "user_dest_ata": "11111111111111111111111111111118",
    }
    
    # Build instruction for buy trade
    buy_instruction = build_cpmm_instruction_for_copy_bot(
        pool_state=example_pool_config["pool_state"],
        pool_authority=example_pool_config["pool_authority"],
        base_vault=example_pool_config["base_vault"],
        quote_vault=example_pool_config["quote_vault"],
        token_mint=example_pool_config["token_mint"],
        user_wallet=example_pool_config["user_wallet"],
        user_source_ata=example_pool_config["user_source_ata"],
        user_dest_ata=example_pool_config["user_dest_ata"],
        amount_in=5_000_000,  # 0.005 SOL
        min_amount_out=800_000  # ~0.8 USDC (with slippage)
    )
    
    print(f"✅ CPMM Instruction Built Successfully!")
    print(f"   Program ID: {buy_instruction.program_id}")
    print(f"   Data length: {len(buy_instruction.data)} bytes")
    print(f"   Account count: {len(buy_instruction.accounts)}")
    
    # Show instruction data breakdown
    discriminator, amount_in, min_out = struct.unpack("<BQQ", buy_instruction.data)
    print(f"\n📦 Instruction Data:")
    print(f"   Discriminator: {discriminator}")
    print(f"   Amount In: {amount_in} ({amount_in/1e9:.6f} SOL)")
    print(f"   Min Amount Out: {min_out} ({min_out/1e6:.6f} USDC)")
    
    print(f"\n📋 Copy Bot Integration Guide:")
    print("=" * 50)
    print("1. Use this exact account structure for ANY CPMM pool")
    print("2. Only change these addresses for different tokens:")
    print("   - pool_state (find from pool discovery)")
    print("   - pool_authority (derive from pool_state)")
    print("   - base_vault (SOL vault for the pool)")
    print("   - quote_vault (Token vault for the pool)")
    print("   - token_mint (the token you want to trade)")
    print("3. Keep the same instruction data format")
    print("4. Same program ID: CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
    
    print(f"\n🔄 For Your Copy Bot:")
    print("=" * 50)
    print("def trade_new_token_cpmm(token_mint, pool_addresses):")
    print("    # 1. Get pool addresses from discovery")
    print("    # 2. Build instruction using this format")
    print("    # 3. Send transaction")
    print("    # 4. Same logic works for ANY token!")
    
    return buy_instruction

if __name__ == "__main__":
    demonstrate_cpmm_for_copy_bot()
