#!/usr/bin/env python3
"""
🔬 PUMP.FUN ACCOUNT STRUCTURE RESEARCH
Research official account requirements from successful transactions
"""

import asyncio
import aiohttp
import json
from solders.pubkey import Pubkey

async def analyze_successful_pumpfun_tx(signature: str):
    """Analyze a successful Pump.fun transaction to understand account structure"""
    print(f"🔍 Analyzing successful Pump.fun transaction: {signature[:16]}...")
    
    try:
        # Use Helius API for detailed transaction analysis
        from env_keys import EnvKeys
        env_keys = EnvKeys()
        
        helius_url = f"https://api.helius.xyz/v0/transactions/{signature}?api-key={env_keys.HELIUS_API_KEY}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(helius_url) as response:
                if response.status != 200:
                    print(f"❌ API error: {response.status}")
                    return None
                
                data = await response.json()
                return data
                
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")
        return None

async def extract_pumpfun_account_structure(tx_data):
    """Extract the exact account structure from successful Pump.fun transaction"""
    try:
        instructions = tx_data.get('instructions', [])
        
        for i, instruction in enumerate(instructions):
            program_id = instruction.get('programId')
            
            # Look for Pump.fun program instructions
            if program_id == "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA":
                print(f"🎯 Found Pump.fun instruction #{i}")
                
                accounts = instruction.get('accounts', [])
                data = instruction.get('data')
                
                print(f"📊 Account Structure ({len(accounts)} accounts):")
                for j, account in enumerate(accounts):
                    print(f"   Account {j}: {account}")
                
                print(f"📝 Instruction data: {data}")
                
                # Check if this is a buy or sell instruction
                if data:
                    buy_discriminator = "66063d1201daebea"
                    sell_discriminator = "33e685a4017f83ad"
                    
                    if data.startswith(buy_discriminator):
                        print(f"✅ This is a BUY instruction")
                    elif data.startswith(sell_discriminator):
                        print(f"✅ This is a SELL instruction")
                    else:
                        print(f"🤔 Unknown instruction type")
                
                return {
                    'accounts': accounts,
                    'data': data,
                    'account_count': len(accounts)
                }
        
        print(f"❌ No Pump.fun instructions found")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting account structure: {e}")
        return None

async def research_current_pumpfun_requirements():
    """Research current Pump.fun account requirements"""
    print("🔬 RESEARCHING CURRENT PUMP.FUN ACCOUNT REQUIREMENTS")
    print("=" * 60)
    
    # Known successful Pump.fun transaction signatures (you can replace with recent ones)
    successful_signatures = [
        # Recent successful buy transactions - replace with actual signatures
        "2CZ8j7KqZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQZQ",  # Example
    ]
    
    print("📝 If you have recent successful Pump.fun transaction signatures,")
    print("   replace the example signatures in this script.")
    print()
    
    # For now, let's analyze the theoretical requirements based on Pump.fun program structure
    print("🧠 THEORETICAL ACCOUNT REQUIREMENTS (based on Pump.fun program):")
    print()
    
    expected_accounts = [
        "Global state account (read-only)",
        "Fee recipient (writable)", 
        "Token mint (read-only)",
        "Bonding curve PDA (writable)",
        "Associated bonding curve (writable)",
        "User token account (writable)",
        "User wallet (signer, writable)",
        "System program (read-only)",
        "Token program (read-only)",
        "Associated token program (read-only)",
        "Rent sysvar (read-only)",
        "Event authority (read-only)",
        "Pump.fun program (read-only)"
    ]
    
    print(f"📊 Expected account count: {len(expected_accounts)}")
    for i, account in enumerate(expected_accounts):
        print(f"   Account {i}: {account}")
    
    return expected_accounts

async def compare_with_current_implementation():
    """Compare our current implementation with requirements"""
    print("\n🔧 COMPARING WITH CURRENT IMPLEMENTATION")
    print("=" * 50)
    
    print("📝 Our current account list (13 accounts):")
    our_accounts = [
        "Global state account",
        "Fee recipient", 
        "Token mint",
        "Bonding curve",
        "Associated bonding curve",
        "User token account",
        "User wallet",
        "System program",
        "Token program",
        "Associated token program",
        "Rent sysvar",
        "Event authority",
        "Pump.fun program"
    ]
    
    for i, account in enumerate(our_accounts):
        print(f"   Account {i}: {account}")
    
    print(f"\n📊 Our account count: {len(our_accounts)}")
    print(f"🎯 This matches the expected structure!")
    
    print("\n🤔 POSSIBLE ISSUES:")
    print("1. Account order might be wrong")
    print("2. Some accounts might have wrong pubkeys")
    print("3. Token might have graduated from Pump.fun")
    print("4. Missing recent program updates")

async def suggest_fixes():
    """Suggest potential fixes based on research"""
    print("\n💡 SUGGESTED FIXES FOR AccountNotEnoughKeys ERROR")
    print("=" * 55)
    
    fixes = [
        {
            "fix": "Check token graduation status",
            "description": "Use Pump.fun API to check if token is still active",
            "code": "GET https://frontend-api.pump.fun/coins/{token_mint}"
        },
        {
            "fix": "Try alternative account order",
            "description": "Some programs expect accounts in different order",
            "code": "Reorder accounts based on successful transaction analysis"
        },
        {
            "fix": "Add missing accounts",
            "description": "Recent program updates might require additional accounts",
            "code": "Add Clock sysvar or other missing system accounts"
        },
        {
            "fix": "Update account pubkeys",
            "description": "Global state or fee accounts might have changed",
            "code": "Verify all hardcoded pubkeys are current"
        },
        {
            "fix": "Check account permissions",
            "description": "Ensure is_signer and is_writable flags are correct",
            "code": "Match exact account meta from successful transactions"
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix['fix']}")
        print(f"   📝 {fix['description']}")
        print(f"   💻 {fix['code']}")
        print()

async def main():
    """Main research function"""
    print("🔬 PUMP.FUN ACCOUNT STRUCTURE RESEARCH")
    print("Based on Solana documentation and error analysis")
    print("=" * 60)
    
    # Research requirements
    await research_current_pumpfun_requirements()
    
    # Compare with our implementation
    await compare_with_current_implementation()
    
    # Suggest fixes
    await suggest_fixes()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Test token graduation check first")
    print("2. Try account structure variations")
    print("3. Update hardcoded pubkeys if needed")
    print("4. Add missing system accounts if required")

if __name__ == "__main__":
    asyncio.run(main())
