#!/usr/bin/env python3
"""
Deep analysis of why the IllegalOwner error occurred
"""

import requests
import json
from solders.pubkey import Pubkey

def deep_analyze_illegal_owner():
    """Analyze the exact cause of the IllegalOwner error"""
    
    print("🔬 DEEP ANALYSIS: Why IllegalOwner Error Occurred")
    print("=" * 80)
    
    # From the failed transaction
    wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    mint = "4pWnhgWh95J1sHeFjxV4JXp6ub2Fyp3uYr2kBF3eBAGS"
    failed_ata = "Cd2SUEabM1eg37J5yizdQfKLQrL7QGB6BUYyP444CDAP"
    
    print(f"📋 TRANSACTION DETAILS:")
    print(f"   Wallet: {wallet}")
    print(f"   Token Mint: {mint}")
    print(f"   ATA Address: {failed_ata}")
    print()
    
    # Calculate what the ATA SHOULD be
    try:
        from solders.pubkey import Pubkey
        
        wallet_pubkey = Pubkey.from_string(wallet)
        mint_pubkey = Pubkey.from_string(mint)
        
        # Calculate the correct ATA
        from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
        
        # Find the ATA address
        ata_address, bump = Pubkey.find_program_address(
            [
                bytes(wallet_pubkey),
                bytes(TOKEN_PROGRAM_ID),
                bytes(mint_pubkey)
            ],
            ASSOCIATED_TOKEN_PROGRAM_ID
        )
        
        calculated_ata = str(ata_address)
        
        print(f"🧮 CALCULATED ATA:")
        print(f"   Expected ATA: {calculated_ata}")
        print(f"   Actual ATA:   {failed_ata}")
        print(f"   Match: {'✅ YES' if calculated_ata == failed_ata else '❌ NO'}")
        print()
        
        if calculated_ata != failed_ata:
            print("❌ MISMATCH DETECTED!")
            print("   The ATA address in the transaction doesn't match the calculated one.")
            print("   This suggests the derivation logic is wrong.")
        else:
            print("✅ ATA ADDRESS IS CORRECT")
            print("   The address derivation is working properly.")
        
    except Exception as e:
        print(f"❌ Error calculating ATA: {e}")
    
    print()
    print("🔍 POSSIBLE REASONS FOR 'IllegalOwner':")
    
    # Check if ATA already exists
    try:
        rpc_url = "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
        
        # Check account info
        response = requests.post(rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                failed_ata,
                {"encoding": "jsonParsed"}
            ]
        })
        
        data = response.json()
        
        if data.get('result', {}).get('value'):
            account_info = data['result']['value']
            print("1. ❌ ATA ALREADY EXISTS")
            print(f"   Owner: {account_info.get('owner', 'Unknown')}")
            print(f"   Data: {account_info.get('data', {})}")
            print("   → This means the bot tried to create an ATA that already exists")
        else:
            print("1. ✅ ATA does not exist yet")
            print("   → The account creation should have worked")
        
    except Exception as e:
        print(f"1. ❌ Error checking ATA existence: {e}")
    
    print()
    print("2. 🔍 OTHER POSSIBLE CAUSES:")
    print("   • Wrong token program ID")
    print("   • Wrong associated token program ID") 
    print("   • Malformed instruction data")
    print("   • Invalid authority in the instruction")
    print("   • Race condition (multiple simultaneous creations)")
    
    print()
    print("🎯 MOST LIKELY CAUSE:")
    print("   Based on the timing and the error, this is probably a:")
    print("   **DUPLICATE ATA CREATION ATTEMPT**")
    print("   → Your bot tried to create the same ATA twice in rapid succession")
    print("   → First attempt succeeded, second attempt failed with IllegalOwner")

if __name__ == "__main__":
    deep_analyze_illegal_owner()
