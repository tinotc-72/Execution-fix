#!/usr/bin/env python3

import os
import sys
from solana.rpc.api import Client
from solders.pubkey import Pubkey
import json

def check_dex_pools():
    """Check which DEX this token is traded on"""
    
    print("🔍 CHECKING DEX POOLS FOR TOKEN")
    print("="*50)
    
    # Use the RPC URL directly
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    rpc_client = Client(rpc_url)
    
    # The token from logs
    token_mint = "EZLW2AoSU7FR6UbikjyxwsktMfCksxdcuZXst1byBAGS"
    
    print(f"🪙 Token Mint: {token_mint}")
    print()
    
    try:
        token_pubkey = Pubkey.from_string(token_mint)
        
        # 1. Check Raydium V4 pools
        print("1️⃣ Checking Raydium V4 pools...")
        try:
            # Get all accounts owned by Raydium V4 program
            RAYDIUM_V4_PROGRAM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
            
            # Check for pools involving this token
            # This is a simplified check - in practice you'd need to parse all pool accounts
            print(f"   Raydium V4 Program: {RAYDIUM_V4_PROGRAM}")
            print("   (Full pool discovery requires complex parsing)")
            
        except Exception as e:
            print(f"   ⚠️ Raydium check failed: {e}")
            
        # 2. Check if there are any known Raydium CPMM pools
        print("\n2️⃣ Checking Raydium CPMM pools...")
        try:
            # CPMM program
            CPMM_PROGRAM = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
            print(f"   CPMM Program: {CPMM_PROGRAM}")
            print("   (Pool discovery requires specialized indexing)")
            
        except Exception as e:
            print(f"   ⚠️ CPMM check failed: {e}")
            
        # 3. Check Jupiter for routing
        print("\n3️⃣ Checking Jupiter quote...")
        try:
            import requests
            
            # Try to get a Jupiter quote for this token
            jupiter_api = "https://quote-api.jup.ag/v6/quote"
            params = {
                "inputMint": "So11111111111111111111111111111111111111112",  # SOL
                "outputMint": token_mint,
                "amount": "1000000",  # 0.001 SOL
                "slippageBps": "50"
            }
            
            response = requests.get(jupiter_api, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'routePlan' in data:
                    print("✅ Jupiter routing available!")
                    route_plan = data.get('routePlan', [])
                    for i, step in enumerate(route_plan):
                        swap_info = step.get('swapInfo', {})
                        amm_key = swap_info.get('ammKey', 'Unknown')
                        label = swap_info.get('label', 'Unknown DEX')
                        print(f"   Step {i+1}: {label} (Pool: {amm_key[:8]}...)")
                else:
                    print("❌ No Jupiter routes found")
            else:
                print(f"⚠️ Jupiter API error: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Jupiter check failed: {e}")
            
        # 4. Look for recent transactions to see DEX activity
        print("\n4️⃣ Checking recent transaction activity...")
        try:
            # Get signatures for this token mint (recent activity)
            signatures = rpc_client.get_signatures_for_address(token_pubkey, limit=5)
            
            if signatures.value:
                print(f"✅ Found {len(signatures.value)} recent transactions")
                for i, sig_info in enumerate(signatures.value[:3]):  # Check first 3
                    signature = sig_info.signature
                    print(f"   Transaction {i+1}: {signature}")
                    
                    # Get transaction details
                    tx_response = rpc_client.get_transaction(
                        signature, 
                        encoding="jsonParsed",
                        max_supported_transaction_version=0
                    )
                    
                    if tx_response.value and tx_response.value.transaction:
                        message = tx_response.value.transaction.transaction.message
                        account_keys = message.account_keys
                        
                        # Look for known DEX programs
                        dex_programs = {
                            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
                            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM", 
                            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
                            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca V1",
                            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca V2"
                        }
                        
                        found_dexs = []
                        for account in account_keys:
                            if hasattr(account, 'pubkey'):
                                pubkey_str = str(account.pubkey)
                            else:
                                pubkey_str = str(account)
                                
                            if pubkey_str in dex_programs:
                                found_dexs.append(dex_programs[pubkey_str])
                        
                        if found_dexs:
                            print(f"     DEXs involved: {', '.join(set(found_dexs))}")
                        else:
                            print("     No known DEX programs detected")
            else:
                print("❌ No recent transactions found")
                
        except Exception as e:
            print(f"⚠️ Transaction analysis failed: {e}")
            
        print("\n" + "="*50)
        print("🎯 DEX ANALYSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_dex_pools()
