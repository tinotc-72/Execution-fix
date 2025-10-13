#!/usr/bin/env python3
"""
Fix the account derivation issue that's causing our sell transactions to fail
"""

import asyncio
import aiohttp
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address
from env_keys import EnvKeys

def derive_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    """Derive the Associated Token Address for a given owner and mint"""
    return get_associated_token_address(owner, mint)

async def check_correct_accounts():
    """Check and derive the correct accounts for our transaction"""
    
    print("🔧 FIXING ACCOUNT DERIVATION ISSUES")
    print("="*80)
    
    # Known addresses
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    our_wallet = Pubkey.from_string("A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
    bonding_curve = Pubkey.from_string("EAgio9owovfTwneWhv3SZrbEaPCj23QJ5C8JDN5XdyyV")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    
    # Derive our correct associated token account
    our_correct_ata = derive_associated_token_address(our_wallet, token_mint)
    
    # Derive the bonding curve's associated token account
    bonding_curve_ata = derive_associated_token_address(bonding_curve, token_mint)
    
    print(f"Our wallet: {our_wallet}")
    print(f"Token mint: {token_mint}")
    print(f"Our CORRECT ATA: {our_correct_ata}")
    print(f"Bonding curve: {bonding_curve}")
    print(f"Bonding curve ATA: {bonding_curve_ata}")
    print()
    
    # Compare with what we were using
    wrong_ata = "9DGQqtdBJHU4fN66cRE1JLVVVJq3KK4mYZxLoSZHqWKf"
    current_ata = "21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG"
    
    print("COMPARISON:")
    print(f"❌ Wrong ATA (from successful tx): {wrong_ata}")
    print(f"🤔 Current ATA (our wallet): {current_ata}")
    print(f"✅ Correct ATA (calculated): {our_correct_ata}")
    print()
    
    # Check if our current ATA matches the calculated one
    if str(our_correct_ata) == current_ata:
        print("✅ Our current ATA is correctly derived!")
    else:
        print("❌ Our current ATA doesn't match the calculated one!")
    
    # Check accounts existence
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    accounts_to_check = {
        "Our correct ATA": str(our_correct_ata),
        "Bonding curve ATA": str(bonding_curve_ata),
        "Current ATA": current_ata,
    }
    
    print("\n🔍 ACCOUNT EXISTENCE CHECK:")
    print("="*50)
    
    async with aiohttp.ClientSession() as session:
        for name, address in accounts_to_check.items():
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [
                    address,
                    {"encoding": "base64"}
                ]
            }
            
            try:
                async with session.post(helius_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data:
                        result = data['result']
                        if result and result.get('value'):
                            account_info = result['value']
                            owner = account_info.get('owner')
                            lamports = account_info.get('lamports', 0)
                            print(f"✅ {name}: EXISTS")
                            print(f"   Address: {address}")
                            print(f"   Owner: {owner}")
                            print(f"   Lamports: {lamports:,}")
                            
                            # Get token balance
                            if "ATA" in name:
                                token_payload = {
                                    "jsonrpc": "2.0",
                                    "id": 1,
                                    "method": "getTokenAccountBalance",
                                    "params": [address]
                                }
                                
                                async with session.post(helius_url, json=token_payload) as token_response:
                                    token_data = await token_response.json()
                                    if 'result' in token_data:
                                        balance_info = token_data['result']['value']
                                        amount = balance_info.get('amount', '0')
                                        decimals = balance_info.get('decimals', 6)
                                        print(f"   Token balance: {amount} (raw)")
                                        print(f"   Token balance: {int(amount) / (10**decimals):,.6f} (adjusted)")
                            
                            print()
                        else:
                            print(f"❌ {name}: DOES NOT EXIST")
                            print(f"   Address: {address}")
                            print()
                            
            except Exception as e:
                print(f"❌ {name}: ERROR - {e}")
                print()
                
            await asyncio.sleep(0.1)

def generate_correct_account_order():
    """Generate the correct account order for our sell transaction"""
    
    print("📋 CORRECT ACCOUNT ORDER FOR SELL TRANSACTION:")
    print("="*80)
    
    # Our addresses
    token_mint = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
    our_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    our_ata = "21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG"
    
    # Pump.fun program addresses
    bonding_curve = "EAgio9owovfTwneWhv3SZrbEaPCj23QJ5C8JDN5XdyyV"
    bonding_curve_ata = "AQPLuT1nZPFXsJ47JSk7LFVLYopnmC1FPh5fgzKaXFUZ"
    pump_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    pump_fee_recipient = "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM"
    system_program = "11111111111111111111111111111111"
    token_program = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    
    # System accounts
    event_authority = "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"
    program_data = "8WHNZ5pwqy6ZgS8jJUjtT3MKoSNWoAp4LCpm8hNHaWfN"
    
    accounts = [
        ("Global", pump_fee_recipient),
        ("Fee recipient", pump_fee_recipient), 
        ("Token mint", token_mint),
        ("Bonding curve", bonding_curve),
        ("Bonding curve token account", bonding_curve_ata),
        ("User token account", our_ata),
        ("User wallet", our_wallet),
        ("System program", system_program),
        ("Token program", token_program),
        ("Event authority", event_authority),
        ("Pump program", pump_program),
        ("Program data", program_data),
    ]
    
    print("Account order for sell transaction:")
    for i, (name, address) in enumerate(accounts):
        print(f"{i:2}: {name:<25} {address}")
    
    return accounts

async def main():
    """Main function"""
    await check_correct_accounts()
    generate_correct_account_order()
    
    print("\n💡 FINDINGS:")
    print("="*50)
    print("1. The account that 'doesn't exist' is from a different user's transaction")
    print("2. We need to use OUR correctly derived associated token account")
    print("3. Our current ATA derivation appears to be correct")
    print("4. The issue might be elsewhere - let's test with the correct accounts")

if __name__ == "__main__":
    asyncio.run(main())
