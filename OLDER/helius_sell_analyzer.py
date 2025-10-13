#!/usr/bin/env python3
"""
Find real sell instructions using Helius API
This script analyzes recent pump.fun transactions to find sell instruction patterns
"""

import asyncio
import aiohttp
import json
import base64
import time
from typing import List, Dict, Optional
import logging

from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeliusPumpAnalyzer:
    def __init__(self):
        self.pump_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        self.buy_discriminator = "66063d1201daebea"
        self.helius_api_key = EnvKeys().HELIUS_API_KEY
        self.rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={self.helius_api_key}"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_signatures_for_address(self, limit: int = 50) -> List[str]:
        """Get recent transaction signatures for pump.fun program"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                self.pump_program,
                {
                    "limit": limit,
                    "commitment": "confirmed"
                }
            ]
        }
        
        try:
            async with self.session.post(self.rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data:
                        return [sig['signature'] for sig in data['result']]
                    else:
                        logger.error(f"No result in response: {data}")
                        return []
                else:
                    logger.warning(f"Failed to get signatures: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching signatures: {e}")
            return []
    
    async def get_transaction_details(self, signature: str) -> Optional[Dict]:
        """Get detailed transaction information"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0,
                    "commitment": "confirmed"
                }
            ]
        }
        
        try:
            async with self.session.post(self.rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('result')
                else:
                    logger.warning(f"Failed to get transaction {signature}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting transaction {signature}: {e}")
            return None
    
    def extract_pump_instructions(self, tx_data: Dict) -> List[Dict]:
        """Extract pump.fun instructions from transaction"""
        instructions = []
        
        if not tx_data or 'transaction' not in tx_data:
            return instructions
        
        # Get instructions from the transaction
        message = tx_data['transaction'].get('message', {})
        tx_instructions = message.get('instructions', [])
        account_keys = message.get('accountKeys', [])
        
        for ix in tx_instructions:
            program_id_index = ix.get('programIdIndex')
            if program_id_index is not None and program_id_index < len(account_keys):
                program_id = account_keys[program_id_index]
                if program_id == self.pump_program:
                    # Get account addresses for this instruction
                    accounts = []
                    for acc_index in ix.get('accounts', []):
                        if acc_index < len(account_keys):
                            accounts.append(account_keys[acc_index])
                    
                    instructions.append({
                        'programId': program_id,
                        'accounts': accounts,
                        'data': ix.get('data', ''),
                        'accountIndices': ix.get('accounts', [])
                    })
        
        return instructions
    
    def analyze_instruction_data(self, instruction_data: str) -> Dict:
        """Analyze instruction data to extract discriminator"""
        try:
            # Decode base58 instruction data
            import base58
            decoded = base58.b58decode(instruction_data)
            
            # Extract discriminator (first 8 bytes)
            discriminator = decoded[:8].hex()
            
            return {
                'discriminator': discriminator,
                'data_length': len(decoded),
                'full_data_hex': decoded.hex(),
                'raw_data': instruction_data
            }
        except Exception as e:
            try:
                # Try base64 decoding as fallback
                decoded = base64.b64decode(instruction_data)
                discriminator = decoded[:8].hex()
                
                return {
                    'discriminator': discriminator,
                    'data_length': len(decoded),
                    'full_data_hex': decoded.hex(),
                    'raw_data': instruction_data,
                    'encoding': 'base64'
                }
            except:
                logger.error(f"Error analyzing instruction data: {e}")
                return {}
    
    def is_potential_sell(self, instruction: Dict) -> bool:
        """Check if instruction could be a sell based on heuristics"""
        data_analysis = self.analyze_instruction_data(instruction.get('data', ''))
        if not data_analysis:
            return False
        
        discriminator = data_analysis['discriminator']
        
        # Not a buy instruction
        if discriminator == self.buy_discriminator:
            return False
        
        # Has reasonable number of accounts (similar to buy)
        account_count = len(instruction.get('accounts', []))
        if account_count < 8 or account_count > 15:
            return False
        
        # Has instruction data
        if data_analysis['data_length'] < 16:  # At least discriminator + some parameters
            return False
        
        return True
    
    async def analyze_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """Analyze recent transactions to find sell patterns"""
        logger.info(f"🔍 Analyzing last {limit} pump.fun transactions...")
        
        # Get recent signatures
        signatures = await self.get_signatures_for_address(limit)
        logger.info(f"📊 Found {len(signatures)} recent signatures")
        
        sell_candidates = []
        buy_count = 0
        
        for i, signature in enumerate(signatures):
            if i % 10 == 0:
                logger.info(f"🔎 Processed {i}/{len(signatures)} transactions...")
            
            # Add delay to avoid rate limiting
            await asyncio.sleep(0.1)
            
            # Get transaction details
            tx_data = await self.get_transaction_details(signature)
            if not tx_data:
                continue
            
            # Extract pump instructions
            pump_instructions = self.extract_pump_instructions(tx_data)
            
            for instruction in pump_instructions:
                data_analysis = self.analyze_instruction_data(instruction.get('data', ''))
                if not data_analysis:
                    continue
                
                discriminator = data_analysis['discriminator']
                
                if discriminator == self.buy_discriminator:
                    buy_count += 1
                elif self.is_potential_sell(instruction):
                    sell_candidates.append({
                        'signature': signature,
                        'instruction': instruction,
                        'analysis': data_analysis,
                        'account_count': len(instruction.get('accounts', []))
                    })
                    logger.info(f"✅ Found potential sell: {signature} (discriminator: {discriminator})")
        
        logger.info(f"📈 Summary: {buy_count} buys, {len(sell_candidates)} potential sells")
        return sell_candidates
    
    def analyze_sell_patterns(self, sell_candidates: List[Dict]) -> Dict:
        """Analyze patterns in sell candidates"""
        if not sell_candidates:
            return {}
        
        # Group by discriminator
        discriminator_groups = {}
        for candidate in sell_candidates:
            disc = candidate['analysis']['discriminator']
            if disc not in discriminator_groups:
                discriminator_groups[disc] = []
            discriminator_groups[disc].append(candidate)
        
        # Calculate statistics
        analysis = {
            'total_candidates': len(sell_candidates),
            'unique_discriminators': len(discriminator_groups),
            'discriminator_frequency': {disc: len(candidates) for disc, candidates in discriminator_groups.items()},
            'discriminator_details': {}
        }
        
        # Detailed analysis
        for disc, candidates in discriminator_groups.items():
            account_counts = [c['account_count'] for c in candidates]
            
            analysis['discriminator_details'][disc] = {
                'frequency': len(candidates),
                'account_counts': account_counts,
                'most_common_account_count': max(set(account_counts), key=account_counts.count) if account_counts else 0,
                'example_accounts': candidates[0]['instruction']['accounts'] if candidates else [],
                'example_signature': candidates[0]['signature'] if candidates else "",
                'data_lengths': [c['analysis']['data_length'] for c in candidates]
            }
        
        return analysis

async def main():
    """Main function"""
    async with HeliusPumpAnalyzer() as analyzer:
        # Analyze recent transactions
        sell_candidates = await analyzer.analyze_recent_transactions(200)
        
        if not sell_candidates:
            logger.warning("❌ No sell instruction candidates found")
            return
        
        # Analyze patterns
        analysis = analyzer.analyze_sell_patterns(sell_candidates)
        
        # Print results
        print("\n" + "="*80)
        print("🔍 PUMP.FUN SELL INSTRUCTION ANALYSIS")
        print("="*80)
        
        print(f"\n📊 Summary:")
        print(f"   Total sell candidates: {analysis['total_candidates']}")
        print(f"   Unique discriminators: {analysis['unique_discriminators']}")
        
        print(f"\n🎯 Discriminator Frequency (most common first):")
        for disc, freq in sorted(analysis['discriminator_frequency'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {disc}: {freq} occurrences")
        
        print(f"\n📋 Detailed Analysis:")
        for disc, details in sorted(analysis['discriminator_details'].items(), 
                                  key=lambda x: x[1]['frequency'], reverse=True):
            print(f"\n   🔹 Discriminator: {disc}")
            print(f"     Frequency: {details['frequency']}")
            print(f"     Account counts: {set(details['account_counts'])}")
            print(f"     Most common account count: {details['most_common_account_count']}")
            print(f"     Data lengths: {set(details['data_lengths'])}")
            print(f"     Example signature: {details['example_signature']}")
            print(f"     Example accounts ({len(details['example_accounts'])}):")
            for i, acc in enumerate(details['example_accounts'][:8]):
                print(f"       [{i}] {acc}")
        
        # Save results
        results = {
            'candidates': sell_candidates,
            'analysis': analysis,
            'timestamp': time.time()
        }
        
        with open('helius_sell_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("💾 Results saved to helius_sell_analysis.json")
        
        # Provide recommendation
        if analysis['discriminator_frequency']:
            most_common = max(analysis['discriminator_frequency'].items(), key=lambda x: x[1])
            print(f"\n🏆 RECOMMENDED SELL DISCRIMINATOR: {most_common[0]}")
            print(f"   Found in {most_common[1]} transactions")
            
            # Show the most common account structure
            details = analysis['discriminator_details'][most_common[0]]
            print(f"   Most common account count: {details['most_common_account_count']}")
            print(f"   Example transaction: {details['example_signature']}")

if __name__ == "__main__":
    asyncio.run(main())
