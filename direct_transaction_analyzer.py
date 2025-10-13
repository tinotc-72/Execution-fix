#!/usr/bin/env python3
"""
Direct Transaction Analysis for Copy Trading Bot
Analyzes specific missed transactions to improve DEX classification
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
sys.path.append('.')
from env_keys import EnvKeys
import aiohttp

class DirectTransactionAnalyzer:
    def __init__(self):
        self.env = EnvKeys()
        self.rpc_url = self.env.HELIUS_RPC_URL
        
        # Current DEX program mappings from main.py
        self.current_dex_programs = {
            # Jupiter
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            
            # Raydium
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
            
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Pump.fun Trading",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
            
            # Orca
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca V1",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpools",
            
            # Phoenix
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
            
            # Other DEXes
            "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora",
            "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom",
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity",
            "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95": "Unknown DEX/Router",
            
            # Token Program
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token Program"
        }
        
        # Current DEX routing from main.py
        self.current_dex_routing = {
            "Jupiter V6": ["jupiter", "pumpfun"],
            "Jupiter V4": ["jupiter", "pumpfun"], 
            "Raydium V4": ["raydium", "cpmm"],
            "Raydium CPMM": ["cpmm", "raydium"],
            "Raydium CPMM V2": ["cpmm", "raydium"],
            "Orca Whirlpool": ["orca", "clmm"],
            "Orca": ["orca"],
            "Pump.fun": ["direct_pumpfun", "pumpfun"],
            "Pump.fun Trading": ["direct_pumpfun", "pumpfun"],
            "Pump.fun Core": ["direct_pumpfun", "pumpfun"],
            "Axiom": ["jupiter"],
            "Unknown DEX/Router": ["jupiter", "direct_pumpfun"],  # Fallback options
        }
    
    async def get_transaction_details(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get detailed transaction information using Helius RPC"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        signature,
                        {
                            "encoding": "jsonParsed",
                            "commitment": "finalized",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                }
                
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('result')
                    else:
                        print(f"❌ RPC error {response.status} for {signature}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error fetching transaction {signature}: {e}")
            return None
    
    def analyze_transaction_classification(self, tx_data: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """Analyze how a transaction would be classified by current system"""
        try:
            if not tx_data:
                return {
                    'signature': signature,
                    'error': 'No transaction data',
                    'current_classification': 'ERROR'
                }
            
            # Extract basic info
            meta = tx_data.get('meta', {})
            transaction = tx_data.get('transaction', {})
            
            if meta.get('err'):
                return {
                    'signature': signature,
                    'error': f"Transaction failed: {meta['err']}",
                    'current_classification': 'FAILED'
                }
            
            # Get all program IDs involved
            message = transaction.get('message', {})
            instructions = message.get('instructions', [])
            accounts = message.get('accountKeys', [])
            
            involved_programs = set()
            
            # Extract program IDs from instructions
            for instruction in instructions:
                program_id_index = instruction.get('programIdIndex')
                if program_id_index is not None and program_id_index < len(accounts):
                    program_account = accounts[program_id_index]
                    if isinstance(program_account, dict):
                        program_id = program_account.get('pubkey', '')
                    else:
                        program_id = str(program_account)
                    if program_id:
                        involved_programs.add(program_id)
            
            # Check inner instructions too
            inner_instructions = meta.get('innerInstructions', [])
            for inner_group in inner_instructions:
                for inner_inst in inner_group.get('instructions', []):
                    program_id_index = inner_inst.get('programIdIndex')
                    if program_id_index is not None and program_id_index < len(accounts):
                        program_account = accounts[program_id_index]
                        if isinstance(program_account, dict):
                            program_id = program_account.get('pubkey', '')
                        else:
                            program_id = str(program_account)
                        if program_id:
                            involved_programs.add(program_id)
            
            # Classify based on current DEX detection system
            detected_dexes = []
            for program_id in involved_programs:
                if program_id in self.current_dex_programs:
                    dex_name = self.current_dex_programs[program_id]
                    detected_dexes.append(dex_name)
            
            # Determine primary classification
            if detected_dexes:
                primary_dex = detected_dexes[0]  # Take first detected
                current_classification = primary_dex
            else:
                current_classification = "Unknown DEX/Router"
            
            # Get SOL balance changes to determine trade type
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            sol_changes = []
            
            for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                change = (post - pre) / 1e9  # Convert to SOL
                if abs(change) > 0.001:  # Significant change
                    sol_changes.append({
                        'account_index': i,
                        'change': change,
                        'pre_balance': pre / 1e9,
                        'post_balance': post / 1e9
                    })
            
            # Get token balance changes
            token_changes = []
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            # Create lookup for token changes
            token_accounts = {}
            for token_balance in pre_token_balances:
                account_index = token_balance.get('accountIndex')
                mint = token_balance.get('mint')
                amount = float(token_balance.get('uiTokenAmount', {}).get('uiAmount', 0))
                if account_index is not None and mint:
                    key = f"{account_index}_{mint}"
                    token_accounts[key] = {'pre': amount, 'post': 0}
            
            for token_balance in post_token_balances:
                account_index = token_balance.get('accountIndex')
                mint = token_balance.get('mint')
                amount = float(token_balance.get('uiTokenAmount', {}).get('uiAmount', 0))
                if account_index is not None and mint:
                    key = f"{account_index}_{mint}"
                    if key in token_accounts:
                        token_accounts[key]['post'] = amount
                    else:
                        token_accounts[key] = {'pre': 0, 'post': amount}
            
            for key, balances in token_accounts.items():
                change = balances['post'] - balances['pre']
                if abs(change) > 0.000001:  # Significant token change
                    account_index, mint = key.split('_', 1)
                    token_changes.append({
                        'account_index': int(account_index),
                        'mint': mint,
                        'change': change,
                        'pre_balance': balances['pre'],
                        'post_balance': balances['post']
                    })
            
            # Determine trade type based on balance changes
            trade_type = None
            if sol_changes and token_changes:
                # Look for typical buy pattern: SOL decreases, token increases
                sol_decrease = any(c['change'] < -0.01 for c in sol_changes)  # More than 0.01 SOL spent
                token_increase = any(c['change'] > 0 for c in token_changes)
                
                if sol_decrease and token_increase:
                    trade_type = 'buy'
                elif not sol_decrease and any(c['change'] < 0 for c in token_changes):
                    trade_type = 'sell'
            
            # Get routing suggestions
            routing_suggestions = []
            if current_classification in self.current_dex_routing:
                routing_suggestions = self.current_dex_routing[current_classification]
            
            return {
                'signature': signature,
                'current_classification': current_classification,
                'detected_dexes': detected_dexes,
                'involved_programs': list(involved_programs),
                'trade_type': trade_type,
                'sol_changes': sol_changes,
                'token_changes': token_changes,
                'routing_suggestions': routing_suggestions,
                'would_be_detected': len(detected_dexes) > 0,
                'raw_transaction': tx_data
            }
            
        except Exception as e:
            return {
                'signature': signature,
                'error': f"Classification error: {e}",
                'current_classification': 'ERROR'
            }
    
    async def analyze_missed_transactions(self, missed_signatures: List[str]) -> Dict[str, Any]:
        """Analyze specific transactions that were missed"""
        print("🔍 DIRECT TRANSACTION ANALYSIS")
        print("=" * 50)
        print(f"🎯 Analyzing {len(missed_signatures)} missed transactions:")
        for i, sig in enumerate(missed_signatures, 1):
            print(f"   {i}. {sig[:20]}...{sig[-20:]}")
        print()
        
        results = {}
        classification_gaps = set()
        new_programs_found = set()
        
        for signature in missed_signatures:
            print(f"🔍 Analyzing: {signature[:16]}...")
            
            # Get transaction details
            tx_data = await self.get_transaction_details(signature)
            
            # Analyze classification
            analysis = self.analyze_transaction_classification(tx_data, signature)
            results[signature] = analysis
            
            # Check for classification gaps
            if not analysis.get('would_be_detected', False):
                print(f"❌ Would NOT be detected by current system")
                print(f"   Classification: {analysis.get('current_classification', 'Unknown')}")
                print(f"   Programs: {analysis.get('involved_programs', [])[:3]}...")
                
                # Track new programs that need classification
                for program in analysis.get('involved_programs', []):
                    if program not in self.current_dex_programs:
                        new_programs_found.add(program)
                        
                classification_gaps.add(signature)
            else:
                print(f"✅ Would be detected as: {analysis.get('current_classification')}")
                if analysis.get('trade_type'):
                    print(f"   Trade type: {analysis.get('trade_type')}")
                if analysis.get('routing_suggestions'):
                    print(f"   Routing: {analysis.get('routing_suggestions')}")
            
            # Rate limiting
            await asyncio.sleep(0.5)
            print()
        
        # Summary
        total_analyzed = len(missed_signatures)
        would_be_detected = total_analyzed - len(classification_gaps)
        
        print("📊 ANALYSIS SUMMARY:")
        print("=" * 30)
        print(f"✅ Would be detected: {would_be_detected}/{total_analyzed}")
        print(f"❌ Would be missed: {len(classification_gaps)}/{total_analyzed}")
        
        if new_programs_found:
            print(f"🔍 New programs found: {len(new_programs_found)}")
            for program in list(new_programs_found)[:10]:
                print(f"   {program}")
        
        # Generate improvement suggestions
        improvements = self.generate_classification_improvements(results, new_programs_found)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'direct_missed_transactions',
            'total_analyzed': total_analyzed,
            'would_be_detected': would_be_detected,
            'classification_gaps': list(classification_gaps),
            'new_programs_found': list(new_programs_found),
            'detailed_results': results,
            'improvements': improvements
        }
    
    def generate_classification_improvements(self, results: Dict[str, Any], new_programs: set) -> Dict[str, Any]:
        """Generate code improvements for better classification"""
        improvements = {
            'new_program_mappings': {},
            'routing_additions': {},
            'code_updates': []
        }
        
        if not new_programs:
            improvements['message'] = "✅ All transactions use known program IDs - classification system is complete!"
            return improvements
        
        print(f"\n🔧 CLASSIFICATION IMPROVEMENTS:")
        print("=" * 40)
        
        # Suggest program classifications based on transaction patterns
        for signature, analysis in results.items():
            if not analysis.get('would_be_detected', False):
                involved_programs = analysis.get('involved_programs', [])
                trade_type = analysis.get('trade_type')
                
                for program in involved_programs:
                    if program in new_programs:
                        # Try to classify based on context
                        if trade_type in ['buy', 'sell']:
                            improvements['new_program_mappings'][program] = "Unknown Trading DEX"
                        else:
                            improvements['new_program_mappings'][program] = "Unknown DEX/Router"
        
        # Generate code updates
        if improvements['new_program_mappings']:
            print("📝 Suggested program mappings:")
            code_lines = []
            code_lines.append("# Add these to dex_programs in main.py:")
            for program, classification in improvements['new_program_mappings'].items():
                code_lines.append(f'    "{program}": "{classification}",')
                print(f"   {program}: {classification}")
            
            code_lines.append("")
            code_lines.append("# Add routing for new classifications:")
            for classification in set(improvements['new_program_mappings'].values()):
                if classification not in self.current_dex_routing:
                    code_lines.append(f'    "{classification}": ["jupiter", "direct_pumpfun"],  # Fallback routing')
                    improvements['routing_additions'][classification] = ["jupiter", "direct_pumpfun"]
            
            improvements['code_updates'] = code_lines
        
        return improvements

async def main():
    """Main function to analyze missed transactions"""
    
    # Known missed transactions from previous analysis
    missed_transactions = [
        "2wdEcuWDtGGoWaPSHoNQ7Re2XxbiPCfS9uWJqTdNUkjqi35rizsdpTHQRwqwjDtt99mbcctG7XSQPtZrLQfwaz3D",  # First missed
        "2i2Y5X4gwcFkLRoYxjbQEe3hdqQsGW3Q1tm76gTxm8jeK3pxKdzNDpiZy6UQc8SBGAyAgVLACrYq9LvL32Xea27M",  # Second missed
    ]
    
    print("🚀 Starting Direct Transaction Analysis...")
    print(f"Target: Analyze specific missed transactions to improve classification")
    print()
    
    analyzer = DirectTransactionAnalyzer()
    results = await analyzer.analyze_missed_transactions(missed_transactions)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"direct_transaction_analysis_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Analysis saved to: {filename}")
    
    # Show improvement code
    if results['improvements']['code_updates']:
        print(f"\n🔧 COPY THIS CODE TO IMPROVE CLASSIFICATION:")
        print("-" * 50)
        for line in results['improvements']['code_updates']:
            print(line)
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    print("\n✅ Direct transaction analysis complete!")
