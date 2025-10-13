#!/usr/bin/env python3
"""
Analyze a specific successful sell transaction to extract the exact structure
"""

import asyncio
import aiohttp
import json
import base58
from typing import Dict, List, Optional

from env_keys import EnvKeys

class TransactionAnalyzer:
    def __init__(self):
        self.helius_api_key = EnvKeys().HELIUS_API_KEY
        self.rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={self.helius_api_key}"
        self.pump_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        
    async def analyze_transaction(self, signature: str) -> Dict:
        """Get detailed transaction analysis"""
        async with aiohttp.ClientSession() as session:
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
            
            async with session.post(self.rpc_url, json=payload) as response:
                data = await response.json()
                return data.get('result', {})
    
    def decode_instruction_data(self, data: str) -> Dict:
        """Decode instruction data"""
        try:
            decoded = base58.b58decode(data)
            discriminator = decoded[:8].hex()
            
            # Try to decode parameters
            params = {}
            if len(decoded) >= 24:  # discriminator (8) + token_amount (8) + min_sol_out (8)
                token_amount = int.from_bytes(decoded[8:16], 'little')
                min_sol_out = int.from_bytes(decoded[16:24], 'little')
                params = {
                    'token_amount': token_amount,
                    'min_sol_out': min_sol_out
                }
            
            return {
                'discriminator': discriminator,
                'full_hex': decoded.hex(),
                'length': len(decoded),
                'parameters': params
            }
        except Exception as e:
            print(f"Error decoding instruction data: {e}")
            return {}
    
    def analyze_pump_instructions(self, tx_data: Dict) -> List[Dict]:
        """Extract and analyze pump instructions"""
        instructions = []
        
        if 'transaction' not in tx_data:
            return instructions
        
        message = tx_data['transaction']['message']
        account_keys = message.get('accountKeys', [])
        
        for ix in message.get('instructions', []):
            program_id_index = ix.get('programIdIndex')
            if program_id_index < len(account_keys) and account_keys[program_id_index] == self.pump_program:
                
                # Get account addresses
                accounts = []
                for acc_index in ix.get('accounts', []):
                    if acc_index < len(account_keys):
                        accounts.append(account_keys[acc_index])
                
                # Decode instruction data
                data_analysis = self.decode_instruction_data(ix.get('data', ''))
                
                instructions.append({
                    'accounts': accounts,
                    'data_analysis': data_analysis,
                    'raw_data': ix.get('data', ''),
                    'account_count': len(accounts)
                })
        
        return instructions

async def main():
    """Analyze specific sell transactions"""
    analyzer = TransactionAnalyzer()
    
    # Analyze multiple successful sell transactions
    sell_signatures = [
        "3cVhmonakERwheg7Jidg9aTdTAPNqWG6T37Nfwrb8S5dABbEzvwd8wFqcXAmg4Z1rhuv3q3L3AQvF5TtuHMnHmTV",  # 12 accounts
        "4mewsLZNWxzHV9vRTN1ZLEhL4BiAaN4szrPgM3GvQzd3ebEUbyxfQAdjyash5ziv5yegNo72UtD5rhizVc1S5w7h",  # 12 accounts  
        "5H9GSaG1EiWRBy63LqQcrjGJ9mn3KqihNaKo7ickcSzk1dwAXUShgBGuQvDfcTogpr6RnLeLzYba4RhHzv7diihG"   # 14 accounts (different discriminator)
    ]
    
    for i, signature in enumerate(sell_signatures):
        print(f"\n{'='*80}")
        print(f"🔍 ANALYZING TRANSACTION {i+1}: {signature}")
        print(f"{'='*80}")
        
        tx_data = await analyzer.analyze_transaction(signature)
        if not tx_data:
            print("❌ Failed to get transaction data")
            continue
        
        pump_instructions = analyzer.analyze_pump_instructions(tx_data)
        
        for j, instruction in enumerate(pump_instructions):
            print(f"\n📋 Instruction {j+1}:")
            print(f"   Discriminator: {instruction['data_analysis'].get('discriminator', 'N/A')}")
            print(f"   Account count: {instruction['account_count']}")
            print(f"   Data length: {instruction['data_analysis'].get('length', 0)}")
            
            if 'parameters' in instruction['data_analysis']:
                params = instruction['data_analysis']['parameters']
                print(f"   Token amount: {params.get('token_amount', 'N/A')}")
                print(f"   Min SOL out: {params.get('min_sol_out', 'N/A')}")
            
            print(f"   Full data hex: {instruction['data_analysis'].get('full_hex', 'N/A')}")
            
            print(f"\n   📍 Accounts ({len(instruction['accounts'])}):")
            for k, account in enumerate(instruction['accounts']):
                print(f"     [{k:2}] {account}")
        
        # Save detailed analysis
        with open(f'transaction_analysis_{i+1}.json', 'w') as f:
            json.dump({
                'signature': signature,
                'transaction_data': tx_data,
                'pump_instructions': pump_instructions
            }, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to transaction_analysis_{i+1}.json")

if __name__ == "__main__":
    asyncio.run(main())
