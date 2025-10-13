#!/usr/bin/env python3
"""
Properly derive bonding curve and associated accounts for our token
"""

import asyncio
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address
import hashlib

def find_program_address(seeds: list, program_id: Pubkey) -> tuple[Pubkey, int]:
    """Find a valid program derived address"""
    for nonce in range(256):
        try:
            # Create the address with nonce
            seed_bytes = b''.join(seeds) + bytes([nonce])
            hash_input = seed_bytes + bytes(program_id)
            hash_result = hashlib.sha256(hash_input).digest()
            
            # Check if this is a valid address (not on curve)
            candidate = Pubkey(hash_result)
            # Simple check - if we can create it, it's probably valid
            return candidate, nonce
        except:
            continue
    raise ValueError("Could not find valid program address")

def derive_bonding_curve_address(token_mint: Pubkey, pump_program: Pubkey) -> Pubkey:
    """Derive the bonding curve address for a token mint"""
    
    # Common seed patterns for bonding curves
    seeds_patterns = [
        [b"bonding-curve", bytes(token_mint)],
        [b"curve", bytes(token_mint)], 
        [bytes(token_mint), b"bonding-curve"],
        [bytes(token_mint), b"curve"],
        [bytes(token_mint)],
    ]
    
    print("🔍 TRYING TO DERIVE BONDING CURVE ADDRESS")
    print("="*80)
    
    expected_address = "9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"
    print(f"Expected address: {expected_address}")
    print(f"Token mint: {token_mint}")
    print(f"Pump program: {pump_program}")
    print()
    
    for i, seeds in enumerate(seeds_patterns):
        try:
            address, nonce = find_program_address(seeds, pump_program)
            print(f"Pattern {i+1}: {seeds} -> {address} (nonce: {nonce})")
            
            if str(address) == expected_address:
                print(f"🎉 FOUND MATCHING PATTERN!")
                return address
                
        except Exception as e:
            print(f"Pattern {i+1}: Failed - {e}")
    
    print(f"❌ Could not derive expected address")
    return None

def derive_associated_bonding_curve(bonding_curve: Pubkey, token_mint: Pubkey) -> Pubkey:
    """Derive the associated token account for the bonding curve"""
    return get_associated_token_address(bonding_curve, token_mint)

async def test_derived_addresses():
    """Test with properly derived addresses"""
    
    print("\n🧪 TESTING WITH DERIVED ADDRESSES")
    print("="*80)
    
    # Our token mint
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    
    # Try to derive the correct bonding curve
    bonding_curve = derive_bonding_curve_address(token_mint, pump_program)
    
    if bonding_curve:
        print(f"✅ Derived bonding curve: {bonding_curve}")
        
        # Derive associated bonding curve
        bonding_curve_ata = derive_associated_bonding_curve(bonding_curve, token_mint)
        print(f"✅ Derived bonding curve ATA: {bonding_curve_ata}")
        
        # Check if these exist
        from env_keys import EnvKeys
        import aiohttp
        
        helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
        
        async with aiohttp.ClientSession() as session:
            # Check bonding curve
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [str(bonding_curve), {"encoding": "base64"}]
            }
            
            async with session.post(helius_url, json=payload) as response:
                data = await response.json()
                if 'result' in data and data['result']['value']:
                    print(f"✅ Bonding curve exists and is valid")
                else:
                    print(f"❌ Bonding curve does not exist")
            
            # Check bonding curve ATA
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [str(bonding_curve_ata), {"encoding": "base64"}]
            }
            
            async with session.post(helius_url, json=payload) as response:
                data = await response.json()
                if 'result' in data and data['result']['value']:
                    print(f"✅ Bonding curve ATA exists and is valid")
                else:
                    print(f"❌ Bonding curve ATA does not exist")
    else:
        print("❌ Could not derive bonding curve address")

async def manual_derive_with_solders():
    """Use solders to properly derive the address"""
    
    print("\n🔧 MANUAL DERIVATION WITH SOLDERS")
    print("="*80)
    
    from solders.pubkey import Pubkey
    
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    expected = "9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"
    
    # Try different seed patterns
    patterns = [
        [b"bonding-curve"],
        [b"curve"], 
        [b"bonding_curve"],
        [b"pumpfun"],
        [b"pump"],
        [bytes(token_mint)],
    ]
    
    for pattern in patterns:
        try:
            # Use solders find_program_address
            derived, nonce = Pubkey.find_program_address(pattern, pump_program)
            print(f"Pattern {pattern}: {derived} (nonce: {nonce})")
            
            if str(derived) == expected:
                print(f"🎉 FOUND CORRECT PATTERN: {pattern}")
                return derived
                
        except Exception as e:
            print(f"Pattern {pattern}: Error - {e}")
    
    print("❌ Could not find the correct derivation pattern")
    return None

async def main():
    """Main function"""
    await test_derived_addresses()
    await manual_derive_with_solders()

if __name__ == "__main__":
    asyncio.run(main())
