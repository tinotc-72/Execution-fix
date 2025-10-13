#!/usr/bin/env python3
"""
Find real sell instructions by analyzing recent pump.fun transactions
This script uses Solscan API to find actual sell transactions and extract their structure
"""

import asyncio
import aiohttp
import json
import base64
import time
from typing import List, Dict, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PumpSellAnalyzer:
    def __init__(self):
        self.pump_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_recent_pump_transactions(self, limit: int = 50) -> List[Dict]:
        """Get recent transactions for the pump.fun program"""
        url = "https://public-api.solscan.io/account/transactions"
        params = {
            "account": self.pump_program,
            "limit": limit,
            "before": "",
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    logger.warning(f"Failed to get transactions: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching transactions: {e}")
            return []
    
    async def analyze_transaction(self, tx_signature: str) -> Optional[Dict]:
        """Analyze a specific transaction to extract instruction details"""
        url = f"https://public-api.solscan.io/transaction/{tx_signature}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"Failed to get transaction {tx_signature}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error analyzing transaction {tx_signature}: {e}")
            return None
    
    def extract_pump_instructions(self, tx_data: Dict) -> List[Dict]:
        """Extract pump.fun instructions from transaction data"""
        instructions = []
        
        if not tx_data or 'instruction' not in tx_data:
            return instructions
            
        for ix in tx_data['instruction']:
            program_id = ix.get('programId', '')
            if program_id == self.pump_program:
                instructions.append(ix)
                
        return instructions
    
    def analyze_instruction_data(self, instruction_data: str) -> Dict:
        """Analyze instruction data to extract discriminator and parameters"""
        try:
            # Decode base64 instruction data
            decoded = base64.b64decode(instruction_data)
            
            # Extract discriminator (first 8 bytes)
            discriminator = decoded[:8].hex()
            
            # Extract remaining data
            remaining_data = decoded[8:]
            
            return {
                'discriminator': discriminator,
                'data_length': len(decoded),
                'remaining_data_length': len(remaining_data),
                'full_data_hex': decoded.hex(),
                'raw_data': instruction_data
            }
        except Exception as e:
            logger.error(f"Error analyzing instruction data: {e}")
            return {}
    
    def identify_sell_transactions(self, instructions: List[Dict]) -> List[Dict]:
        """Identify potential sell transactions based on patterns"""
        sell_candidates = []
        
        for ix in instructions:
            # Look for instructions that might be sells
            accounts = ix.get('accounts', [])
            data = ix.get('data', '')
            
            if not data:
                continue
                
            analysis = self.analyze_instruction_data(data)
            if not analysis:
                continue
                
            # Heuristics for identifying sell transactions:
            # 1. Different discriminator than buy (66063d1201daebea)
            # 2. Similar account structure but possibly different order
            # 3. Instruction data suggests token -> SOL swap
            
            discriminator = analysis['discriminator']
            if discriminator != '66063d1201daebea':  # Not a buy
                sell_candidates.append({
                    'instruction': ix,
                    'analysis': analysis,
                    'account_count': len(accounts),
                    'accounts': accounts
                })
        
        return sell_candidates
    
    async def find_sell_instructions(self) -> List[Dict]:
        """Main method to find sell instructions"""
        logger.info("🔍 Searching for pump.fun sell instructions...")
        
        # Get recent transactions
        transactions = await self.get_recent_pump_transactions(100)
        logger.info(f"📊 Found {len(transactions)} recent transactions")
        
        all_sell_candidates = []
        
        for i, tx in enumerate(transactions):
            tx_signature = tx.get('txHash', '')
            if not tx_signature:
                continue
                
            logger.info(f"🔎 Analyzing transaction {i+1}/{len(transactions)}: {tx_signature}")
            
            # Add delay to avoid rate limiting
            await asyncio.sleep(0.5)
            
            # Analyze the transaction
            tx_data = await self.analyze_transaction(tx_signature)
            if not tx_data:
                continue
                
            # Extract pump instructions
            pump_instructions = self.extract_pump_instructions(tx_data)
            if not pump_instructions:
                continue
                
            # Identify sell candidates
            sell_candidates = self.identify_sell_transactions(pump_instructions)
            if sell_candidates:
                logger.info(f"✅ Found {len(sell_candidates)} sell candidates in {tx_signature}")
                for candidate in sell_candidates:
                    candidate['tx_signature'] = tx_signature
                    all_sell_candidates.append(candidate)
        
        return all_sell_candidates
    
    def analyze_sell_patterns(self, sell_candidates: List[Dict]) -> Dict:
        """Analyze patterns in sell instructions to find the most likely correct one"""
        if not sell_candidates:
            return {}
            
        # Group by discriminator
        discriminator_groups = {}
        for candidate in sell_candidates:
            disc = candidate['analysis']['discriminator']
            if disc not in discriminator_groups:
                discriminator_groups[disc] = []
            discriminator_groups[disc].append(candidate)
        
        # Analyze patterns
        analysis = {
            'total_candidates': len(sell_candidates),
            'unique_discriminators': len(discriminator_groups),
            'discriminator_frequency': {disc: len(candidates) for disc, candidates in discriminator_groups.items()},
            'discriminator_details': {}
        }
        
        # Detailed analysis for each discriminator
        for disc, candidates in discriminator_groups.items():
            account_counts = [c['account_count'] for c in candidates]
            
            analysis['discriminator_details'][disc] = {
                'frequency': len(candidates),
                'account_counts': account_counts,
                'most_common_account_count': max(set(account_counts), key=account_counts.count),
                'example_accounts': candidates[0]['accounts'] if candidates else [],
                'example_tx': candidates[0]['tx_signature'] if candidates else ""
            }
        
        return analysis

async def main():
    """Main function to find and analyze sell instructions"""
    async with PumpSellAnalyzer() as analyzer:
        # Find sell instructions
        sell_candidates = await analyzer.find_sell_instructions()
        
        if not sell_candidates:
            logger.warning("❌ No sell instruction candidates found")
            return
        
        logger.info(f"🎯 Found {len(sell_candidates)} sell instruction candidates")
        
        # Analyze patterns
        analysis = analyzer.analyze_sell_patterns(sell_candidates)
        
        # Print results
        print("\n" + "="*80)
        print("🔍 SELL INSTRUCTION ANALYSIS RESULTS")
        print("="*80)
        
        print(f"\n📊 Summary:")
        print(f"   Total candidates: {analysis['total_candidates']}")
        print(f"   Unique discriminators: {analysis['unique_discriminators']}")
        
        print(f"\n🎯 Discriminator Frequency:")
        for disc, freq in sorted(analysis['discriminator_frequency'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {disc}: {freq} occurrences")
        
        print(f"\n📋 Detailed Analysis:")
        for disc, details in analysis['discriminator_details'].items():
            print(f"\n   Discriminator: {disc}")
            print(f"   Frequency: {details['frequency']}")
            print(f"   Account counts: {details['account_counts']}")
            print(f"   Most common account count: {details['most_common_account_count']}")
            print(f"   Example transaction: {details['example_tx']}")
            print(f"   Example accounts: {len(details['example_accounts'])} accounts")
            for i, acc in enumerate(details['example_accounts'][:5]):  # Show first 5 accounts
                print(f"     [{i}] {acc}")
        
        # Save detailed results to file
        with open('sell_instruction_analysis.json', 'w') as f:
            json.dump({
                'candidates': sell_candidates,
                'analysis': analysis,
                'timestamp': time.time()
            }, f, indent=2)
        
        logger.info("💾 Detailed results saved to sell_instruction_analysis.json")
        
        # Recommend the most promising discriminator
        if analysis['discriminator_frequency']:
            most_common = max(analysis['discriminator_frequency'].items(), key=lambda x: x[1])
            print(f"\n🏆 RECOMMENDED SELL DISCRIMINATOR: {most_common[0]}")
            print(f"   (Found in {most_common[1]} transactions)")

if __name__ == "__main__":
    asyncio.run(main())
