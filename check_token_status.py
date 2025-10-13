"""
Token Validator - Check if a token is still on pump.fun
"""

import asyncio
import httpx
from solders.pubkey import Pubkey
from env_keys import EnvKeys

async def check_token_status(token_address: str):
    """Check if token is still on pump.fun or has graduated"""
    print(f"🔍 Checking token: {token_address}")
    
    env = EnvKeys()
    
    try:
        # Check account owner
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                env.HELIUS_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [
                        token_address,
                        {"encoding": "base64"}
                    ]
                }
            )
            
            data = response.json()
            if 'result' in data and data['result']:
                account_info = data['result']['value']
                owner = account_info['owner']
                
                print(f"📋 Account owner: {owner}")
                
                # Check if owned by pump.fun program
                PUMP_FUN_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
                TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                
                if owner == PUMP_FUN_PROGRAM:
                    print("✅ Token is STILL ON PUMP.FUN - Your executor will work!")
                    return True
                elif owner == TOKEN_PROGRAM:
                    print("❌ Token has GRADUATED to SPL Token - Use Raydium executor instead")
                    return False
                else:
                    print(f"⚠️ Unknown owner: {owner}")
                    return False
            else:
                print("❌ Token not found or invalid")
                return False
                
    except Exception as e:
        print(f"❌ Error checking token: {e}")
        return False

async def main():
    print("🎯 TOKEN VALIDATOR - Check if token is on Pump.fun")
    print("=" * 50)
    
    # Test the token you provided
    test_token = "CzR5f68ySPMtvLEkAM6mP85VPBhvkRybTCV2CHzpump"
    await check_token_status(test_token)
    
    print("\n" + "=" * 50)
    print("💡 To test your executor with a fresh pump.fun token:")
    print("   1. Find a newly created token on pump.fun website")
    print("   2. Use this validator to confirm it's still on pump.fun")
    print("   3. Run your executor - it WILL work!")

if __name__ == "__main__":
    asyncio.run(main())
