#!/usr/bin/env python3
"""
Token Scanner for Active Pump.Fun Tokens
Finds recently created and active pump.fun tokens to test trading with
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from solders.pubkey import Pubkey

from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PumpTokenScanner:
    """Scanner for active pump.fun tokens"""
    
    def __init__(self):
        self.helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
        self.pump_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        
    async def get_recent_pump_transactions(self, limit: int = 50) -> List[Dict]:
        """Get recent transactions from pump.fun program"""
        
        logger.info(f"🔍 Scanning for recent pump.fun transactions (limit: {limit})")
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    self.pump_program,
                    {
                        "limit": limit,
                        "before": None,
                        "until": None,
                        "commitment": "confirmed"
                    }
                ]
            }
            
            try:
                async with session.post(self.helius_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data and data['result']:
                        signatures = [tx['signature'] for tx in data['result'] if not tx.get('err')]
                        logger.info(f"✅ Found {len(signatures)} successful transactions")
                        return signatures
                    else:
                        logger.error(f"Failed to get signatures: {data}")
                        return []
                        
            except Exception as e:
                logger.error(f"Error getting signatures: {e}")
                return []

    async def analyze_transaction(self, signature: str) -> Optional[Dict]:
        """Analyze a transaction to extract token information"""
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "jsonParsed",
                        "maxSupportedTransactionVersion": 0,
                        "commitment": "confirmed"
                    }
                ]
            }
            
            try:
                async with session.post(self.helius_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data and data['result']:
                        tx = data['result']
                        
                        # Extract token mint from account keys
                        account_keys = []
                        if 'transaction' in tx and 'message' in tx['transaction']:
                            if 'accountKeys' in tx['transaction']['message']:
                                account_keys = [acc['pubkey'] for acc in tx['transaction']['message']['accountKeys']]
                            elif 'accounts' in tx['transaction']['message']:
                                account_keys = tx['transaction']['message']['accounts']
                        
                        # Look for token mints (typically have specific characteristics)
                        token_candidates = []
                        for account in account_keys:
                            if account != self.pump_program and len(account) == 44:  # Pubkey length
                                token_candidates.append(account)
                        
                        # Get slot timestamp
                        block_time = tx.get('blockTime', 0)
                        
                        return {
                            'signature': signature,
                            'token_candidates': token_candidates,
                            'block_time': block_time,
                            'slot': tx.get('slot', 0),
                            'accounts': account_keys
                        }
                        
            except Exception as e:
                logger.error(f"Error analyzing transaction {signature}: {e}")
                return None

    async def validate_token_mint(self, token_mint: str) -> Dict:
        """Validate if an address is a valid pump.fun token mint"""
        
        try:
            # Check if it's a valid pubkey
            mint_pubkey = Pubkey.from_string(token_mint)
            
            async with aiohttp.ClientSession() as session:
                # Get account info
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [
                        token_mint,
                        {"encoding": "jsonParsed"}
                    ]
                }
                
                async with session.post(self.helius_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data and data['result'] and data['result']['value']:
                        account_info = data['result']['value']
                        
                        # Check if it's a token mint
                        if (account_info['owner'] == 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA' and
                            'parsed' in account_info['data'] and
                            account_info['data']['parsed']['type'] == 'mint'):
                            
                            mint_info = account_info['data']['parsed']['info']
                            
                            # Check if it has the pump.fun characteristics
                            supply = int(mint_info['supply'])
                            decimals = mint_info['decimals']
                            
                            # Try to derive bonding curve
                            seeds = [b"bonding-curve", bytes(mint_pubkey)]
                            pump_program_pubkey = Pubkey.from_string(self.pump_program)
                            
                            try:
                                bonding_curve, bump = Pubkey.find_program_address(seeds, pump_program_pubkey)
                                
                                # Check if bonding curve exists
                                bc_payload = {
                                    "jsonrpc": "2.0",
                                    "id": 1,
                                    "method": "getAccountInfo",
                                    "params": [str(bonding_curve), {"encoding": "base64"}]
                                }
                                
                                async with session.post(self.helius_url, json=bc_payload) as bc_response:
                                    bc_data = await bc_response.json()
                                    
                                    bonding_curve_exists = (
                                        'result' in bc_data and 
                                        bc_data['result'] and 
                                        bc_data['result']['value']
                                    )
                                    
                                    return {
                                        'mint': token_mint,
                                        'is_valid_mint': True,
                                        'is_pump_token': bonding_curve_exists,
                                        'supply': supply,
                                        'decimals': decimals,
                                        'bonding_curve': str(bonding_curve),
                                        'freeze_authority': mint_info.get('freezeAuthority'),
                                        'mint_authority': mint_info.get('mintAuthority')
                                    }
                                    
                            except Exception as e:
                                logger.error(f"Error deriving bonding curve for {token_mint}: {e}")
                                
                        return {
                            'mint': token_mint,
                            'is_valid_mint': False,
                            'is_pump_token': False,
                            'error': 'Not a valid token mint'
                        }
                    else:
                        return {
                            'mint': token_mint,
                            'is_valid_mint': False,
                            'is_pump_token': False,
                            'error': 'Account does not exist'
                        }
                        
        except Exception as e:
            return {
                'mint': token_mint,
                'is_valid_mint': False,
                'is_pump_token': False,
                'error': str(e)
            }

    async def find_active_pump_tokens(self, max_transactions: int = 100) -> List[Dict]:
        """Find active pump.fun tokens from recent transactions"""
        
        logger.info(f"🔍 Searching for active pump.fun tokens...")
        
        # Get recent transactions
        signatures = await self.get_recent_pump_transactions(max_transactions)
        
        if not signatures:
            logger.error("No transactions found")
            return []
        
        # Analyze transactions to find token candidates
        token_candidates = set()
        
        for i, signature in enumerate(signatures[:20]):  # Limit analysis to first 20 for speed
            logger.info(f"Analyzing transaction {i+1}/{min(20, len(signatures))}: {signature[:8]}...")
            
            tx_info = await self.analyze_transaction(signature)
            if tx_info:
                for candidate in tx_info['token_candidates']:
                    token_candidates.add(candidate)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.1)
        
        logger.info(f"Found {len(token_candidates)} token candidates")
        
        # Validate each candidate
        valid_tokens = []
        
        for i, candidate in enumerate(list(token_candidates)[:10]):  # Limit validation to 10
            logger.info(f"Validating token {i+1}/{min(10, len(token_candidates))}: {candidate[:8]}...")
            
            validation = await self.validate_token_mint(candidate)
            
            if validation.get('is_pump_token'):
                valid_tokens.append(validation)
                logger.info(f"✅ Found valid pump token: {candidate}")
            
            await asyncio.sleep(0.1)
        
        # Sort by supply (newer tokens often have lower supply)
        valid_tokens.sort(key=lambda x: x.get('supply', 0))
        
        return valid_tokens

    async def get_token_market_info(self, token_mint: str) -> Dict:
        """Get market information for a token"""
        
        try:
            mint_pubkey = Pubkey.from_string(token_mint)
            pump_program_pubkey = Pubkey.from_string(self.pump_program)
            
            # Derive bonding curve
            seeds = [b"bonding-curve", bytes(mint_pubkey)]
            bonding_curve, bump = Pubkey.find_program_address(seeds, pump_program_pubkey)
            
            async with aiohttp.ClientSession() as session:
                # Get bonding curve data
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [str(bonding_curve), {"encoding": "base64"}]
                }
                
                async with session.post(self.helius_url, json=payload) as response:
                    data = await response.json()
                    
                    if 'result' in data and data['result'] and data['result']['value']:
                        account_data = data['result']['value']['data'][0]
                        
                        # Decode base64 data
                        import base64
                        raw_data = base64.b64decode(account_data)
                        
                        if len(raw_data) >= 64:
                            # Parse bonding curve data (pump.fun specific format)
                            import struct
                            
                            virtual_token_reserves = struct.unpack('<Q', raw_data[8:16])[0]
                            virtual_sol_reserves = struct.unpack('<Q', raw_data[16:24])[0]
                            real_token_reserves = struct.unpack('<Q', raw_data[24:32])[0]
                            real_sol_reserves = struct.unpack('<Q', raw_data[32:40])[0]
                            
                            return {
                                'mint': token_mint,
                                'bonding_curve': str(bonding_curve),
                                'virtual_token_reserves': virtual_token_reserves,
                                'virtual_sol_reserves': virtual_sol_reserves / 1_000_000_000,
                                'real_token_reserves': real_token_reserves,
                                'real_sol_reserves': real_sol_reserves / 1_000_000_000,
                                'has_liquidity': virtual_sol_reserves > 0
                            }
                            
        except Exception as e:
            logger.error(f"Error getting market info for {token_mint}: {e}")
            
        return {'mint': token_mint, 'error': 'Could not get market info'}

async def main():
    """Main scanner function"""
    
    print("🔍 PUMP.FUN TOKEN SCANNER")
    print("="*60)
    
    scanner = PumpTokenScanner()
    
    try:
        # Find active tokens
        tokens = await scanner.find_active_pump_tokens(50)
        
        print(f"\n✅ Found {len(tokens)} valid pump.fun tokens:")
        print("-" * 60)
        
        for i, token in enumerate(tokens[:5]):  # Show top 5
            print(f"\n{i+1}. Token: {token['mint']}")
            print(f"   Supply: {token['supply']:,}")
            print(f"   Decimals: {token['decimals']}")
            print(f"   Bonding Curve: {token['bonding_curve']}")
            
            # Get market info
            market_info = await scanner.get_token_market_info(token['mint'])
            
            if 'virtual_sol_reserves' in market_info:
                print(f"   SOL Reserves: {market_info['virtual_sol_reserves']:.4f}")
                print(f"   Has Liquidity: {market_info['has_liquidity']}")
            
            await asyncio.sleep(0.1)
        
        if tokens:
            print(f"\n🎯 Recommended token for testing:")
            best_token = tokens[0]
            print(f"Token Mint: {best_token['mint']}")
            print(f"Use this with the generalized trading bot!")
            
            # Test market info
            market_info = await scanner.get_token_market_info(best_token['mint'])
            if 'virtual_sol_reserves' in market_info and market_info['virtual_sol_reserves'] > 1:
                print(f"✅ Good liquidity: {market_info['virtual_sol_reserves']:.4f} SOL")
            else:
                print("⚠️ Low liquidity - be careful with trade sizes")
        else:
            print("❌ No valid pump.fun tokens found")
            
    except Exception as e:
        logger.error(f"Scanner error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
