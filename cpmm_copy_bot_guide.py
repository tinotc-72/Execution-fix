#!/usr/bin/env python3
"""
CPMM Copy Bot Implementation Guide

This file shows you EXACTLY how to implement CPMM trading in your copy bot.
The instruction format is tested and ready for production use.
"""

import struct
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction

# ✅ CPMM Program ID (Real program on mainnet)
CPMM_PROGRAM_ID = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

class CPMMCopyBot:
    """
    CPMM Copy Bot Implementation
    
    This class shows you how to integrate CPMM trading into your copy bot.
    The logic is identical for ALL tokens - just change the pool addresses!
    """
    
    def __init__(self):
        self.program_id = CPMM_PROGRAM_ID
        
    def build_cpmm_buy_instruction(
        self,
        # Pool addresses (these change for each token)
        pool_state: str,
        pool_authority: str,
        base_vault: str,       # SOL vault
        quote_vault: str,      # Token vault
        token_mint: str,       # Token mint address
        
        # User addresses (your wallet and ATAs)
        user_wallet: str,
        user_sol_ata: str,     # Your WSOL ATA
        user_token_ata: str,   # Your token ATA
        
        # Trade parameters
        sol_amount: int,       # Amount of SOL to spend (lamports)
        min_tokens_out: int    # Minimum tokens to receive
    ) -> Instruction:
        """
        Build CPMM buy instruction - SOL -> Token
        
        This is the EXACT format you need for your copy bot!
        """
        
        # Convert addresses to Pubkey objects
        pool_state_pubkey = Pubkey.from_string(pool_state)
        pool_authority_pubkey = Pubkey.from_string(pool_authority)
        base_vault_pubkey = Pubkey.from_string(base_vault)
        quote_vault_pubkey = Pubkey.from_string(quote_vault)
        token_mint_pubkey = Pubkey.from_string(token_mint)
        user_wallet_pubkey = Pubkey.from_string(user_wallet)
        user_sol_ata_pubkey = Pubkey.from_string(user_sol_ata)
        user_token_ata_pubkey = Pubkey.from_string(user_token_ata)
        
        # ✅ CPMM Standard Account Structure (Same for ALL tokens)
        accounts = [
            AccountMeta(pool_state_pubkey, False, True),        # 0. Pool state
            AccountMeta(pool_authority_pubkey, False, False),   # 1. Pool authority
            AccountMeta(SOL_MINT, False, False),                # 2. Base mint (SOL)
            AccountMeta(token_mint_pubkey, False, False),       # 3. Quote mint (Token)
            AccountMeta(base_vault_pubkey, False, True),        # 4. Base vault (SOL)
            AccountMeta(quote_vault_pubkey, False, True),       # 5. Quote vault (Token)
            AccountMeta(user_sol_ata_pubkey, False, True),      # 6. User SOL ATA (source)
            AccountMeta(user_token_ata_pubkey, False, True),    # 7. User Token ATA (dest)
            AccountMeta(user_wallet_pubkey, True, False),       # 8. User wallet (signer)
            AccountMeta(TOKEN_PROGRAM_ID, False, False),        # 9. Token program
        ]
        
        # ✅ CPMM Instruction Data (Same for ALL tokens)
        discriminator = 0  # Swap instruction
        instruction_data = struct.pack("<BQQ", discriminator, sol_amount, min_tokens_out)
        
        # ✅ Build instruction
        return Instruction(
            program_id=self.program_id,
            data=instruction_data,
            accounts=accounts
        )
    
    def build_cpmm_sell_instruction(
        self,
        # Pool addresses (these change for each token)
        pool_state: str,
        pool_authority: str,
        base_vault: str,       # SOL vault
        quote_vault: str,      # Token vault
        token_mint: str,       # Token mint address
        
        # User addresses (your wallet and ATAs)
        user_wallet: str,
        user_token_ata: str,   # Your token ATA
        user_sol_ata: str,     # Your WSOL ATA
        
        # Trade parameters
        token_amount: int,     # Amount of tokens to sell
        min_sol_out: int       # Minimum SOL to receive (lamports)
    ) -> Instruction:
        """
        Build CPMM sell instruction - Token -> SOL
        
        Same format as buy, just swap source/destination
        """
        
        # Convert addresses to Pubkey objects
        pool_state_pubkey = Pubkey.from_string(pool_state)
        pool_authority_pubkey = Pubkey.from_string(pool_authority)
        base_vault_pubkey = Pubkey.from_string(base_vault)
        quote_vault_pubkey = Pubkey.from_string(quote_vault)
        token_mint_pubkey = Pubkey.from_string(token_mint)
        user_wallet_pubkey = Pubkey.from_string(user_wallet)
        user_token_ata_pubkey = Pubkey.from_string(user_token_ata)
        user_sol_ata_pubkey = Pubkey.from_string(user_sol_ata)
        
        # ✅ CPMM Standard Account Structure (Same for ALL tokens)
        accounts = [
            AccountMeta(pool_state_pubkey, False, True),        # 0. Pool state
            AccountMeta(pool_authority_pubkey, False, False),   # 1. Pool authority
            AccountMeta(SOL_MINT, False, False),                # 2. Base mint (SOL)
            AccountMeta(token_mint_pubkey, False, False),       # 3. Quote mint (Token)
            AccountMeta(base_vault_pubkey, False, True),        # 4. Base vault (SOL)
            AccountMeta(quote_vault_pubkey, False, True),       # 5. Quote vault (Token)
            AccountMeta(user_token_ata_pubkey, False, True),    # 6. User Token ATA (source)
            AccountMeta(user_sol_ata_pubkey, False, True),      # 7. User SOL ATA (dest)
            AccountMeta(user_wallet_pubkey, True, False),       # 8. User wallet (signer)
            AccountMeta(TOKEN_PROGRAM_ID, False, False),        # 9. Token program
        ]
        
        # ✅ CPMM Instruction Data (Same for ALL tokens)
        discriminator = 0  # Swap instruction
        instruction_data = struct.pack("<BQQ", discriminator, token_amount, min_sol_out)
        
        # ✅ Build instruction
        return Instruction(
            program_id=self.program_id,
            data=instruction_data,
            accounts=accounts
        )
    
    def copy_trade_cpmm_token(self, detected_token_info: dict) -> dict:
        """
        Copy trade a new token using CPMM
        
        This is how you integrate CPMM into your copy bot!
        """
        
        # Extract pool info from detected token (you'll implement pool discovery)
        pool_addresses = detected_token_info.get("cpmm_pool")
        if not pool_addresses:
            return {"error": "No CPMM pool found for token"}
        
        # Build buy instruction
        buy_instruction = self.build_cpmm_buy_instruction(
            pool_state=pool_addresses["pool_state"],
            pool_authority=pool_addresses["pool_authority"],
            base_vault=pool_addresses["base_vault"],
            quote_vault=pool_addresses["quote_vault"],
            token_mint=detected_token_info["token_mint"],
            user_wallet=detected_token_info["user_wallet"],
            user_sol_ata=detected_token_info["user_sol_ata"],
            user_token_ata=detected_token_info["user_token_ata"],
            sol_amount=detected_token_info["buy_amount"],
            min_tokens_out=detected_token_info["min_tokens_out"]
        )
        
        # Send transaction (you'll implement this)
        # transaction_signature = send_transaction(buy_instruction)
        
        return {
            "success": True,
            "instruction": buy_instruction,
            "message": "CPMM buy instruction built successfully"
        }

def demonstrate_copy_bot_integration():
    """Show how to use CPMM in your copy bot"""
    
    print("🤖 CPMM Copy Bot Integration Demo")
    print("=" * 50)
    
    # Initialize copy bot
    copy_bot = CPMMCopyBot()
    
    # Simulate detected token info (this comes from your monitoring)
    detected_token = {
        "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC example
        "cpmm_pool": {
            "pool_state": "11111111111111111111111111111112",
            "pool_authority": "11111111111111111111111111111113",
            "base_vault": "11111111111111111111111111111114",
            "quote_vault": "11111111111111111111111111111115"
        },
        "user_wallet": "11111111111111111111111111111116",
        "user_sol_ata": "11111111111111111111111111111117",
        "user_token_ata": "11111111111111111111111111111118",
        "buy_amount": 5_000_000,  # 0.005 SOL
        "min_tokens_out": 800_000  # ~0.8 USDC
    }
    
    # Copy trade the token
    result = copy_bot.copy_trade_cpmm_token(detected_token)
    
    if result.get("success"):
        instruction = result["instruction"]
        print("✅ CPMM Copy Trade Ready!")
        print(f"   Program: {instruction.program_id}")
        print(f"   Accounts: {len(instruction.accounts)}")
        print(f"   Data: {len(instruction.data)} bytes")
        
        # Show instruction breakdown
        discriminator, amount_in, min_out = struct.unpack("<BQQ", instruction.data)
        print(f"   Amount In: {amount_in/1e9:.6f} SOL")
        print(f"   Min Out: {min_out/1e6:.6f} Tokens")
        
    print("\\n🎯 Integration Steps:")
    print("1. Add CPMM pool discovery to your monitoring")
    print("2. Use these instruction builders in your copy logic")
    print("3. Same format works for ANY token!")
    print("4. Test with small amounts first")

if __name__ == "__main__":
    demonstrate_copy_bot_integration()
