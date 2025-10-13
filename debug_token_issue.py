#!/usr/bin/env python3

import os
import sys
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import json
from spl.token.constants import TOKEN_PROGRAM_ID

def debug_token_mint():
    """Debug the problematic token mint"""
    
    print("🔍 DEBUGGING TOKEN MINT ISSUE")
    print("="*50)
    
    # Use the RPC URL directly
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    rpc_client = Client(rpc_url)
    
    # The problematic token from logs
    token_mint = "EZLW2AoSU7FR6UbikjyxwsktMfCksxdcuZXst1byBAGS"
    wallet_pubkey = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    
    print(f"🪙 Token Mint: {token_mint}")
    print(f"👤 Wallet: {wallet_pubkey}")
    print()
    
    try:
        # 1. Check if token mint exists
        print("1️⃣ Checking token mint account...")
        token_pubkey = Pubkey.from_string(token_mint)
        account_info = rpc_client.get_account_info(token_pubkey)
        
        if account_info.value is None:
            print("❌ Token mint account does not exist!")
            return
        else:
            print("✅ Token mint account exists")
            print(f"   Owner: {account_info.value.owner}")
            print(f"   Data length: {len(account_info.value.data)}")
            
        # 2. Check if it's a valid SPL Token
        print("\n2️⃣ Validating SPL Token...")
        if account_info.value.owner == TOKEN_PROGRAM_ID:
            print("✅ Valid SPL Token (owned by Token Program)")
        else:
            print(f"⚠️ Not a standard SPL Token. Owner: {account_info.value.owner}")
            
        # 3. Try to get token supply
        print("\n3️⃣ Checking token supply...")
        try:
            supply_response = rpc_client.get_token_supply(token_pubkey)
            if supply_response.value:
                print(f"✅ Token supply: {supply_response.value.amount}")
                print(f"   Decimals: {supply_response.value.decimals}")
            else:
                print("❌ Could not get token supply")
        except Exception as e:
            print(f"❌ Token supply error: {e}")
            
        # 4. Calculate expected ATA
        print("\n4️⃣ Calculating Associated Token Account...")
        from spl.token.instructions import get_associated_token_address
        
        wallet_pubkey_obj = Pubkey.from_string(wallet_pubkey)
        expected_ata = get_associated_token_address(wallet_pubkey_obj, token_pubkey)
        print(f"📍 Expected ATA: {expected_ata}")
        
        # 5. Check if ATA exists
        print("\n5️⃣ Checking if ATA exists...")
        ata_info = rpc_client.get_account_info(expected_ata)
        if ata_info.value is None:
            print("❌ ATA does not exist (needs to be created)")
        else:
            print("✅ ATA already exists")
            print(f"   Owner: {ata_info.value.owner}")
            
        # 6. Check token metadata program
        print("\n6️⃣ Checking for token metadata...")
        try:
            # Metaplex metadata PDA
            METADATA_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
            
            # Calculate metadata PDA
            metadata_seeds = [
                b"metadata",
                bytes(METADATA_PROGRAM_ID),
                bytes(token_pubkey)
            ]
            metadata_pda, _ = Pubkey.find_program_address(metadata_seeds, METADATA_PROGRAM_ID)
            print(f"📋 Metadata PDA: {metadata_pda}")
            
            metadata_info = rpc_client.get_account_info(metadata_pda)
            if metadata_info.value:
                print("✅ Token has metadata")
            else:
                print("⚠️ No metadata found")
                
        except Exception as e:
            print(f"⚠️ Metadata check failed: {e}")
            
        # 7. Check if token is on Pump.fun
        print("\n7️⃣ Checking Pump.fun bonding curve...")
        try:
            PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
            
            # Calculate bonding curve PDA
            bonding_curve_seeds = [b"bonding-curve", bytes(token_pubkey)]
            bonding_curve_pda, _ = Pubkey.find_program_address(bonding_curve_seeds, PUMP_FUN_PROGRAM)
            print(f"📈 Bonding curve PDA: {bonding_curve_pda}")
            
            bonding_curve_info = rpc_client.get_account_info(bonding_curve_pda)
            if bonding_curve_info.value:
                print("✅ Pump.fun bonding curve exists")
                print(f"   Data length: {len(bonding_curve_info.value.data)}")
            else:
                print("❌ Pump.fun bonding curve does not exist")
                print("   This token is NOT on Pump.fun!")
                
        except Exception as e:
            print(f"❌ Pump.fun check failed: {e}")
            
        print("\n" + "="*50)
        print("🎯 DIAGNOSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_token_mint()
