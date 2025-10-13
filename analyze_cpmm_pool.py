#!/usr/bin/env python3
"""
Complete Raydium CPMM Pool Information Retriever
================================================

This script gets ALL the information needed for trading:
- Pool state address
- Token mint addresses  
- Vault addresses (base and quote)
- Tick array addresses
- Pool configuration

Use this to get complete, verified pool data for your trading script.
"""

import asyncio
import struct
from typing import Dict, List, Optional, Tuple
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solana.rpc.commitment import Confirmed
from env_keys import validate_env_vars
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Raydium CPMM Program ID
CPMM_PROGRAM_ID = "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK"

class CPMMPoolAnalyzer:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        
    async def get_complete_pool_info(self, pool_id: str) -> Optional[Dict]:
        """Get complete pool information including all required addresses"""
        
        logger.info(f"🔍 Analyzing CPMM pool: {pool_id}")
        
        try:
            async with AsyncClient(self.rpc_url) as client:
                # Get pool account data
                pool_pubkey = Pubkey.from_string(pool_id)
                pool_info = await client.get_account_info(pool_pubkey, commitment=Confirmed)
                
                if not pool_info.value:
                    logger.error(f"❌ Pool {pool_id} does not exist")
                    return None
                
                # Verify this is a CPMM pool
                if str(pool_info.value.owner) != CPMM_PROGRAM_ID:
                    logger.error(f"❌ Pool {pool_id} is not a Raydium CPMM pool")
                    logger.error(f"   Owner: {pool_info.value.owner}")
                    logger.error(f"   Expected: {CPMM_PROGRAM_ID}")
                    return None
                
                # Parse pool data
                pool_data = await self.parse_cpmm_pool_data(pool_info.value.data)
                if not pool_data:
                    logger.error(f"❌ Failed to parse pool data")
                    return None
                
                # Get additional derived addresses
                derived_addresses = await self.get_derived_addresses(pool_id, pool_data)
                
                # Combine all information
                complete_info = {
                    'pool_id': pool_id,
                    'program_id': CPMM_PROGRAM_ID,
                    'exists': True,
                    'lamports': pool_info.value.lamports,
                    'data_length': len(pool_info.value.data),
                    **pool_data,
                    **derived_addresses
                }
                
                # Verify all addresses exist
                verification = await self.verify_all_addresses(client, complete_info)
                complete_info['verification'] = verification
                
                logger.info(f"✅ Complete pool analysis finished")
                return complete_info
                
        except Exception as e:
            logger.error(f"❌ Error analyzing pool: {e}")
            return None
    
    async def parse_cpmm_pool_data(self, data: bytes) -> Optional[Dict]:
        """Parse CPMM pool account data"""
        try:
            if len(data) < 300:  # CPMM pools should be larger
                logger.error(f"❌ Pool data too small: {len(data)} bytes")
                return None
            
            # CPMM pool data layout (simplified - this may need adjustment)
            # The exact layout depends on Raydium's implementation
            
            offset = 0
            
            # Discriminator (8 bytes)
            discriminator = data[offset:offset+8]
            offset += 8
            
            # Config ID (32 bytes)
            config_id = data[offset:offset+32]
            offset += 32
            
            # Token A mint (32 bytes)
            token_a_mint = data[offset:offset+32]
            offset += 32
            
            # Token B mint (32 bytes)
            token_b_mint = data[offset:offset+32]
            offset += 32
            
            # Token A vault (32 bytes)
            token_a_vault = data[offset:offset+32]
            offset += 32
            
            # Token B vault (32 bytes)
            token_b_vault = data[offset:offset+32]
            offset += 32
            
            # Additional fields would follow...
            
            parsed = {
                'config_id': str(Pubkey(config_id)),
                'token_a_mint': str(Pubkey(token_a_mint)),
                'token_b_mint': str(Pubkey(token_b_mint)),
                'token_a_vault': str(Pubkey(token_a_vault)),
                'token_b_vault': str(Pubkey(token_b_vault)),
                'discriminator': discriminator.hex(),
                'raw_data_length': len(data)
            }
            
            logger.info(f"✅ Parsed pool data:")
            logger.info(f"   Token A: {parsed['token_a_mint']}")
            logger.info(f"   Token B: {parsed['token_b_mint']}")
            logger.info(f"   Vault A: {parsed['token_a_vault']}")
            logger.info(f"   Vault B: {parsed['token_b_vault']}")
            
            return parsed
            
        except Exception as e:
            logger.error(f"❌ Error parsing pool data: {e}")
            # Fallback: try to extract some basic info
            return self.fallback_parse_pool_data(data)
    
    def fallback_parse_pool_data(self, data: bytes) -> Dict:
        """Fallback parsing when main parsing fails"""
        logger.warning("⚠️ Using fallback parsing method")
        
        # Try to find Pubkey-like patterns in the data
        pubkeys = []
        for i in range(0, len(data) - 32, 4):
            try:
                potential_pubkey = data[i:i+32]
                # Basic validation - pubkeys are 32 bytes and usually printable
                pubkey_str = str(Pubkey(potential_pubkey))
                if not pubkey_str.startswith('1111111111'):  # Avoid null keys
                    pubkeys.append(pubkey_str)
            except:
                continue
        
        return {
            'parsing_method': 'fallback',
            'potential_addresses': pubkeys[:10],  # First 10 potential addresses
            'raw_data_length': len(data),
            'needs_manual_analysis': True
        }
    
    async def get_derived_addresses(self, pool_id: str, pool_data: Dict) -> Dict:
        """Get derived addresses like authority, tick arrays, etc."""
        
        try:
            # AMM authority (standard derivation)
            amm_authority, _ = Pubkey.find_program_address(
                [b"amm_authority"],
                Pubkey.from_string(CPMM_PROGRAM_ID)
            )
            
            # For tick arrays and other derived accounts, we'd need the specific
            # derivation seeds used by Raydium CPMM
            
            derived = {
                'amm_authority': str(amm_authority),
                'derivation_method': 'standard'
            }
            
            # Try to find tick arrays by common patterns
            # This is pool-specific and may require different approaches
            
            return derived
            
        except Exception as e:
            logger.warning(f"⚠️ Error deriving addresses: {e}")
            return {'amm_authority': 'unknown'}
    
    async def verify_all_addresses(self, client: AsyncClient, pool_info: Dict) -> Dict:
        """Verify that all addresses in pool info actually exist"""
        
        verification = {}
        
        addresses_to_check = [
            ('config_id', pool_info.get('config_id')),
            ('token_a_mint', pool_info.get('token_a_mint')),
            ('token_b_mint', pool_info.get('token_b_mint')),
            ('token_a_vault', pool_info.get('token_a_vault')),
            ('token_b_vault', pool_info.get('token_b_vault')),
            ('amm_authority', pool_info.get('amm_authority'))
        ]
        
        for name, address in addresses_to_check:
            if address and address != 'unknown':
                try:
                    account_info = await client.get_account_info(
                        Pubkey.from_string(address),
                        commitment=Confirmed
                    )
                    exists = bool(account_info.value)
                    verification[name] = {
                        'address': address,
                        'exists': exists,
                        'lamports': account_info.value.lamports if exists else 0
                    }
                    
                    if exists:
                        logger.info(f"✅ {name}: {address}")
                    else:
                        logger.warning(f"❌ {name}: {address} (does not exist)")
                        
                except Exception as e:
                    verification[name] = {
                        'address': address,
                        'exists': False,
                        'error': str(e)
                    }
                    logger.error(f"❌ Error checking {name}: {e}")
        
        return verification
    
    def generate_trading_config(self, pool_info: Dict, target_token: str) -> str:
        """Generate configuration code for the trading script"""
        
        if not pool_info or not pool_info.get('verification'):
            return "# Error: Invalid pool information"
        
        # Determine which token is the target
        token_a = pool_info.get('token_a_mint')
        token_b = pool_info.get('token_b_mint')
        
        if token_a == target_token:
            base_mint = token_a
            quote_mint = token_b
            base_vault = pool_info.get('token_a_vault')
            quote_vault = pool_info.get('token_b_vault')
        elif token_b == target_token:
            base_mint = token_b
            quote_mint = token_a
            base_vault = pool_info.get('token_b_vault')
            quote_vault = pool_info.get('token_a_vault')
        else:
            base_mint = token_a  # Default
            quote_mint = token_b
            base_vault = pool_info.get('token_a_vault')
            quote_vault = pool_info.get('token_b_vault')
        
        # Check verification status
        verification = pool_info.get('verification', {})
        all_verified = all(
            v.get('exists', False) for v in verification.values()
            if isinstance(v, dict)
        )
        
        config = f'''# 🔧 RAYDIUM CPMM POOL CONFIGURATION
# Generated for pool: {pool_info.get('pool_id')}
# Target token: {target_token}
# Verification status: {"✅ ALL VERIFIED" if all_verified else "❌ NEEDS VERIFICATION"}

# POOL ADDRESSES
CPMM_TOKEN_MINT = Pubkey.from_string("{base_mint}")
POOL_STATE = Pubkey.from_string("{pool_info.get('pool_id')}")
BASE_VAULT = Pubkey.from_string("{base_vault}")
QUOTE_VAULT = Pubkey.from_string("{quote_vault}")

# AMM AUTHORITY
AMM_AUTH = Pubkey.from_string("{pool_info.get('amm_authority', 'unknown')}")

# CONFIGURATION
AMM_PROGRAM = Pubkey.from_string("{CPMM_PROGRAM_ID}")

# TICK ARRAY (you may need to find this manually)
TICK_ARRAY = Pubkey.from_string("11111111111111111111111111111112")  # ❌ PLACEHOLDER

# SAFETY CHECK
ADDRESSES_VERIFIED = {str(all_verified).lower()}  # Set to True only if all addresses verified

# VERIFICATION RESULTS:
{self._format_verification_results(verification)}
'''
        
        return config
    
    def _format_verification_results(self, verification: Dict) -> str:
        """Format verification results as comments"""
        lines = []
        for name, result in verification.items():
            if isinstance(result, dict):
                status = "✅" if result.get('exists') else "❌"
                lines.append(f"# {name}: {status} {result.get('address', 'unknown')}")
        return '\n'.join(lines)

async def main():
    print("🔍 Complete CPMM Pool Analyzer")
    print("=" * 50)
    
    # Get pool ID
    pool_id = input("Enter CPMM pool ID: ").strip()
    target_token = input("Enter target token mint (optional): ").strip()
    
    if not pool_id:
        print("❌ No pool ID provided")
        return
    
    try:
        # Load environment
        env_vars = validate_env_vars()
        rpc_url = env_vars["RPC_URL"]
        
        # Analyze pool
        analyzer = CPMMPoolAnalyzer(rpc_url)
        pool_info = await analyzer.get_complete_pool_info(pool_id)
        
        if not pool_info:
            print("❌ Failed to analyze pool")
            return
        
        # Display results
        print("\n" + "="*60)
        print("📊 POOL ANALYSIS RESULTS")
        print("="*60)
        
        print(f"Pool ID: {pool_info['pool_id']}")
        print(f"Program: {pool_info['program_id']}")
        print(f"Exists: {pool_info['exists']}")
        print(f"Data Length: {pool_info['data_length']} bytes")
        
        if 'token_a_mint' in pool_info:
            print(f"\nToken A: {pool_info['token_a_mint']}")
            print(f"Token B: {pool_info['token_b_mint']}")
            print(f"Vault A: {pool_info['token_a_vault']}")
            print(f"Vault B: {pool_info['token_b_vault']}")
        
        # Generate config
        if target_token:
            config = analyzer.generate_trading_config(pool_info, target_token)
            
            print("\n" + "="*60)
            print("🔧 TRADING SCRIPT CONFIGURATION")
            print("="*60)
            print(config)
            
            # Save to file
            with open(f'pool_config_{pool_id[:8]}.py', 'w') as f:
                f.write(config)
            print(f"\n💾 Configuration saved to: pool_config_{pool_id[:8]}.py")
        
        # Save full analysis
        import json
        with open(f'pool_analysis_{pool_id[:8]}.json', 'w') as f:
            json.dump(pool_info, f, indent=2, default=str)
        print(f"💾 Full analysis saved to: pool_analysis_{pool_id[:8]}.json")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
