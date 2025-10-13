#!/usr/bin/env python3

import os
import sys
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address

def test_ata_creation():
    """Test ATA creation logic to debug the IncorrectProgramId error"""
    
    print("🔍 TESTING ATA CREATION LOGIC")
    print("="*50)
    
    # Use the RPC URL directly
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    rpc_client = Client(rpc_url)
    
    # Test data from logs
    token_mint = "EZLW2AoSU7FR6UbikjyxwsktMfCksxdcuZXst1byBAGS"
    wallet_pubkey = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    
    print(f"🪙 Token Mint: {token_mint}")
    print(f"👤 Wallet: {wallet_pubkey}")
    print()
    
    try:
        # Convert to Pubkey objects
        token_mint_pubkey = Pubkey.from_string(token_mint)
        wallet_pubkey_obj = Pubkey.from_string(wallet_pubkey)
        
        # Calculate expected ATA
        expected_ata = get_associated_token_address(wallet_pubkey_obj, token_mint_pubkey)
        print(f"📍 Expected ATA: {expected_ata}")
        
        # Check if ATA exists
        ata_info = rpc_client.get_account_info(expected_ata)
        if ata_info.value is None:
            print("❌ ATA does not exist (creation needed)")
            
            # Test the create_associated_token_account function
            from spl.token.instructions import create_associated_token_account
            
            print("\n🧪 Testing create_associated_token_account instruction...")
            try:
                create_ata_ix = create_associated_token_account(
                    payer=wallet_pubkey_obj,
                    owner=wallet_pubkey_obj,
                    mint=token_mint_pubkey
                )
                
                print("✅ ATA instruction created successfully")
                print(f"   Program ID: {create_ata_ix.program_id}")
                print(f"   Accounts: {len(create_ata_ix.accounts)}")
                
                # Examine the accounts
                for i, account in enumerate(create_ata_ix.accounts):
                    print(f"   Account {i}: {account.pubkey} (writable: {account.is_writable}, signer: {account.is_signer})")
                    
            except Exception as create_error:
                print(f"❌ ATA instruction creation failed: {create_error}")
                import traceback
                traceback.print_exc()
        else:
            print("✅ ATA already exists")
            print(f"   Owner: {ata_info.value.owner}")
            print(f"   Data length: {len(ata_info.value.data)}")
            
            # Parse ATA data to check if it's valid
            try:
                from spl.token.client import Token
                from spl.token.constants import TOKEN_PROGRAM_ID
                
                # Create a token client to check ATA data
                token_client = Token(rpc_client, token_mint_pubkey, TOKEN_PROGRAM_ID, wallet_pubkey_obj)
                
                # Get token account info
                account_info = token_client.get_account_info(expected_ata)
                print(f"   Token account state: Valid")
                print(f"   Balance: {account_info.amount}")
                print(f"   Mint: {account_info.mint}")
                print(f"   Owner: {account_info.owner}")
                
            except Exception as parse_error:
                print(f"⚠️ ATA data parsing failed: {parse_error}")
                
        # Test different ATA creation methods
        print("\n🧪 Testing alternative ATA creation methods...")
        
        # Method 1: Using spl-token-2022 (if needed)
        try:
            from spl.token.constants import TOKEN_2022_PROGRAM_ID
            from spl.token.instructions import get_associated_token_address as get_ata_2022
            
            ata_2022 = get_ata_2022(wallet_pubkey_obj, token_mint_pubkey, TOKEN_2022_PROGRAM_ID)
            print(f"📍 Token-2022 ATA: {ata_2022}")
            
            ata_2022_info = rpc_client.get_account_info(ata_2022)
            if ata_2022_info.value:
                print("✅ Token-2022 ATA exists")
            else:
                print("❌ Token-2022 ATA does not exist")
                
        except Exception as token_2022_error:
            print(f"⚠️ Token-2022 check failed: {token_2022_error}")
            
        # Method 2: Check if the token uses a different standard
        print("\n🔍 Checking token program compatibility...")
        token_info = rpc_client.get_account_info(token_mint_pubkey)
        if token_info.value:
            print(f"Token owner program: {token_info.value.owner}")
            from spl.token.constants import TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID
            
            if str(token_info.value.owner) == str(TOKEN_PROGRAM_ID):
                print("✅ Standard SPL Token")
            elif str(token_info.value.owner) == str(TOKEN_2022_PROGRAM_ID):
                print("⚠️ Token-2022 (might need different handling)")
            else:
                print(f"⚠️ Unknown token program: {token_info.value.owner}")
        
        print("\n" + "="*50)
        print("🎯 ATA TESTING COMPLETE")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ata_creation()
