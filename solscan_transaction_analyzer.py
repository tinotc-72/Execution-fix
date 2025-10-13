#!/usr/bin/env python3
"""
Solscan Transaction Analyzer for Copy Trading Bot
Analyzes target wallet transaction history using Solscan API to ensure accurate DEX classification
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

class SolscanTransactionAnalyzer:
    def __init__(self):
        self.base_url = "https://public-api.solscan.io"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session = None
        
        # DEX program mappings for accurate classification
        self.dex_programs = {
            # Jupiter
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            
            # Raydium
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",  
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
            
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Pump.fun Trading",
            "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Router",
            
            # Orca
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca V1",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpools",
            
            # Phoenix
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
            
            # Other DEXes
            "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora",
            "AAmkoDEUz7VmZEPMrZjjm4gEwvELdGrwYsqNEgZqhk6y": "Axiom",
            "2wT8Yq49kHgDzXuPxZSaeLaH1qbmGXtEyPy64bL7aD3c": "Lifinity",
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_wallet_transactions(self, wallet_address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history for a wallet from Solscan API"""
        try:
            url = f"{self.base_url}/account/transactions"
            params = {
                'account': wallet_address,
                'limit': min(limit, 50)  # Solscan API limit
            }
            
            print(f"🔍 Fetching transactions for {wallet_address[:8]}...")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    transactions = data.get('data', [])
                    print(f"✅ Found {len(transactions)} transactions")
                    return transactions
                else:
                    print(f"❌ Solscan API error: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error fetching transactions: {e}")
            return []
    
    async def get_transaction_details(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get detailed transaction information from Solscan"""
        try:
            url = f"{self.base_url}/transaction"
            params = {'tx': signature}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"⚠️ Could not fetch details for {signature[:16]}...")
                    return None
                    
        except Exception as e:
            print(f"⚠️ Error fetching transaction details: {e}")
            return None
    
    def classify_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify transaction based on program interactions and token changes"""
        try:
            # Get basic transaction info
            signature = tx_data.get('txHash', '')
            block_time = tx_data.get('blockTime', 0)
            timestamp = datetime.fromtimestamp(block_time) if block_time else datetime.now()
            
            # Look for program interactions
            instructions = tx_data.get('parsedInstruction', [])
            involved_programs = set()
            
            # Collect all programs involved
            for instruction in instructions:
                program_id = instruction.get('programId', '')
                if program_id:
                    involved_programs.add(program_id)
            
            # Determine DEX from program IDs
            detected_dex = "Unknown"
            for program_id in involved_programs:
                if program_id in self.dex_programs:
                    detected_dex = self.dex_programs[program_id]
                    break
            
            # Look for token balance changes to determine trade type
            sol_change = tx_data.get('solChange', {}).get('changeAmount', 0)
            token_changes = tx_data.get('tokenBalanceChanges', [])
            
            # Determine trade type based on SOL and token changes
            trade_type = None
            token_mint = None
            amount = 0
            
            if sol_change < 0 and token_changes:
                # Negative SOL change + token increase = BUY
                for token_change in token_changes:
                    if token_change.get('changeAmount', 0) > 0:
                        trade_type = 'buy'
                        token_mint = token_change.get('tokenAddress', 'UNKNOWN')
                        amount = abs(sol_change) / 1e9  # Convert lamports to SOL
                        break
                        
            elif sol_change > 0 and token_changes:
                # Positive SOL change + token decrease = SELL
                for token_change in token_changes:
                    if token_change.get('changeAmount', 0) < 0:
                        trade_type = 'sell'
                        token_mint = token_change.get('tokenAddress', 'UNKNOWN')
                        amount = sol_change / 1e9  # Convert lamports to SOL
                        break
            
            return {
                'signature': signature,
                'timestamp': timestamp.isoformat(),
                'dex': detected_dex,
                'trade_type': trade_type,
                'token_mint': token_mint,
                'amount': amount,
                'sol_change': sol_change / 1e9,
                'programs': list(involved_programs),
                'raw_data': tx_data
            }
            
        except Exception as e:
            print(f"⚠️ Error classifying transaction: {e}")
            return {
                'signature': tx_data.get('txHash', ''),
                'error': str(e),
                'raw_data': tx_data
            }
    
    async def analyze_wallet_trading_patterns(self, wallet_address: str, limit: int = 50) -> Dict[str, Any]:
        """Analyze trading patterns for a specific wallet"""
        print(f"\n🎯 ANALYZING WALLET: {wallet_address[:8]}...{wallet_address[-8:]}")
        print("=" * 60)
        
        # Get transaction history
        transactions = await self.get_wallet_transactions(wallet_address, limit)
        
        if not transactions:
            return {
                'wallet': wallet_address,
                'error': 'No transactions found',
                'trades': []
            }
        
        # Analyze each transaction
        trades = []
        dex_usage = {}
        trade_types = {'buy': 0, 'sell': 0, 'other': 0}
        
        print(f"📊 Analyzing {len(transactions)} transactions...")
        
        for i, tx in enumerate(transactions):
            # Rate limiting - small delay between requests
            if i > 0 and i % 10 == 0:
                print(f"🔄 Processed {i} transactions...")
                await asyncio.sleep(1)  # 1 second delay every 10 transactions
            
            classified = self.classify_transaction(tx)
            
            if 'error' not in classified:
                # Count DEX usage
                dex = classified.get('dex', 'Unknown')
                dex_usage[dex] = dex_usage.get(dex, 0) + 1
                
                # Count trade types
                trade_type = classified.get('trade_type')
                if trade_type in ['buy', 'sell']:
                    trade_types[trade_type] += 1
                    trades.append(classified)
                else:
                    trade_types['other'] += 1
        
        # Summary statistics
        total_trades = trade_types['buy'] + trade_types['sell']
        
        print(f"\n📈 TRADING ANALYSIS RESULTS:")
        print(f"   🟢 Buy trades: {trade_types['buy']}")
        print(f"   🔴 Sell trades: {trade_types['sell']}")
        print(f"   💹 Total trades: {total_trades}")
        print(f"   ⚪ Other transactions: {trade_types['other']}")
        
        if dex_usage:
            print(f"\n🏢 DEX USAGE BREAKDOWN:")
            for dex, count in sorted(dex_usage.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(transactions)) * 100
                print(f"   {dex}: {count} transactions ({percentage:.1f}%)")
        
        # Show recent trade examples
        recent_buys = [t for t in trades if t.get('trade_type') == 'buy'][-5:]
        recent_sells = [t for t in trades if t.get('trade_type') == 'sell'][-5:]
        
        if recent_buys:
            print(f"\n🟢 RECENT BUY TRADES:")
            for i, buy in enumerate(recent_buys, 1):
                token_short = buy['token_mint'][:8] + '...' if buy['token_mint'] != 'UNKNOWN' else 'UNKNOWN'
                print(f"   {i}. {buy['dex']} | {buy['amount']:.6f} SOL | {token_short}")
                print(f"      📅 {buy['timestamp'][:19]} | 🔗 {buy['signature'][:20]}...")
        
        if recent_sells:
            print(f"\n🔴 RECENT SELL TRADES:")
            for i, sell in enumerate(recent_sells, 1):
                token_short = sell['token_mint'][:8] + '...' if sell['token_mint'] != 'UNKNOWN' else 'UNKNOWN'
                print(f"   {i}. {sell['dex']} | {sell['amount']:.6f} SOL | {token_short}")
                print(f"      📅 {sell['timestamp'][:19]} | 🔗 {sell['signature'][:20]}...")
        
        return {
            'wallet': wallet_address,
            'total_transactions': len(transactions),
            'total_trades': total_trades,
            'buy_trades': trade_types['buy'],
            'sell_trades': trade_types['sell'],
            'other_transactions': trade_types['other'],
            'dex_usage': dex_usage,
            'trades': trades,
            'recent_buys': recent_buys,
            'recent_sells': recent_sells
        }
    
    async def analyze_all_target_wallets(self, target_wallets: List[str], limit: int = 50) -> Dict[str, Any]:
        """Analyze trading patterns for all target wallets"""
        print("🔍 SOLSCAN TRANSACTION CLASSIFICATION ANALYSIS")
        print("=" * 70)
        print("🎯 Target Wallets:")
        for i, wallet in enumerate(target_wallets, 1):
            print(f"   {i}. {wallet[:8]}...{wallet[-8:]}")
        print()
        
        results = {}
        overall_stats = {
            'total_wallets': len(target_wallets),
            'successful_analyses': 0,
            'total_trades': 0,
            'total_buys': 0,
            'total_sells': 0,
            'dex_distribution': {},
            'program_coverage': set()
        }
        
        # Analyze each wallet
        for wallet in target_wallets:
            try:
                analysis = await self.analyze_wallet_trading_patterns(wallet, limit)
                results[wallet] = analysis
                
                if 'error' not in analysis:
                    overall_stats['successful_analyses'] += 1
                    overall_stats['total_trades'] += analysis['total_trades']
                    overall_stats['total_buys'] += analysis['buy_trades']
                    overall_stats['total_sells'] += analysis['sell_trades']
                    
                    # Aggregate DEX usage
                    for dex, count in analysis['dex_usage'].items():
                        overall_stats['dex_distribution'][dex] = overall_stats['dex_distribution'].get(dex, 0) + count
                    
                    # Collect program IDs for coverage analysis
                    for trade in analysis['trades']:
                        overall_stats['program_coverage'].update(trade.get('programs', []))
                
                # Rate limiting between wallets
                await asyncio.sleep(2)  # 2 second delay between wallets
                
            except Exception as e:
                print(f"❌ Error analyzing wallet {wallet}: {e}")
                results[wallet] = {'error': str(e)}
        
        # Overall summary
        print(f"\n📊 OVERALL CLASSIFICATION ANALYSIS:")
        print("=" * 50)
        print(f"✅ Successfully analyzed: {overall_stats['successful_analyses']}/{overall_stats['total_wallets']} wallets")
        print(f"🟢 Total buy trades: {overall_stats['total_buys']}")
        print(f"🔴 Total sell trades: {overall_stats['total_sells']}")
        print(f"💹 Grand total trades: {overall_stats['total_trades']}")
        
        if overall_stats['total_trades'] > 0:
            buy_pct = (overall_stats['total_buys'] / overall_stats['total_trades']) * 100
            sell_pct = (overall_stats['total_sells'] / overall_stats['total_trades']) * 100
            print(f"📈 Trade distribution: {buy_pct:.1f}% buys, {sell_pct:.1f}% sells")
        
        print(f"\n🏢 OVERALL DEX USAGE:")
        print("-" * 30)
        for dex, count in sorted(overall_stats['dex_distribution'].items(), key=lambda x: x[1], reverse=True):
            if overall_stats['total_trades'] > 0:
                percentage = (count / sum(overall_stats['dex_distribution'].values())) * 100
                print(f"   {dex}: {count} trades ({percentage:.1f}%)")
        
        print(f"\n🔍 PROGRAM COVERAGE ANALYSIS:")
        print("-" * 35)
        covered_programs = overall_stats['program_coverage']
        known_programs = set(self.dex_programs.keys())
        
        # Check coverage
        covered_known = covered_programs.intersection(known_programs)
        uncovered_programs = covered_programs - known_programs
        
        print(f"✅ Known DEX programs detected: {len(covered_known)}")
        for program in covered_known:
            print(f"   {program}: {self.dex_programs[program]}")
        
        if uncovered_programs:
            print(f"❓ Unknown programs (need classification): {len(uncovered_programs)}")
            for program in list(uncovered_programs)[:10]:  # Show first 10
                print(f"   {program}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"solscan_classification_analysis_{timestamp}.json"
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'solscan_classification',
            'target_wallets': target_wallets,
            'overall_stats': {
                **overall_stats,
                'program_coverage': list(overall_stats['program_coverage'])  # Convert set to list
            },
            'wallet_analyses': results
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n💾 Analysis saved to: {filename}")
        return output_data
    
    def generate_program_mapping_update(self, analysis_results: Dict[str, Any]) -> str:
        """Generate updated program mapping code for main.py"""
        overall_stats = analysis_results['overall_stats']
        covered_programs = set(overall_stats['program_coverage'])
        known_programs = set(self.dex_programs.keys())
        uncovered_programs = covered_programs - known_programs
        
        if not uncovered_programs:
            return "✅ All programs are already mapped in the DEX detection system!"
        
        print(f"\n🔧 GENERATING PROGRAM MAPPING UPDATES:")
        print("=" * 45)
        print(f"Found {len(uncovered_programs)} unmapped programs that need classification")
        
        mapping_code = "# Add these program mappings to main.py DEX detection:\n\n"
        mapping_code += "# In the dex_programs dictionary, add:\n"
        
        for program in list(uncovered_programs)[:20]:  # Limit to first 20
            mapping_code += f'    "{program}": "Unknown DEX",  # TODO: Classify this program\n'
        
        mapping_code += "\n# And in the dex_routing dictionary, add corresponding routes\n"
        
        print("Generated mapping code (check the return value)")
        return mapping_code

async def main():
    """Main function to run the Solscan analysis"""
    
    # Target wallets to analyze
    target_wallets = [
        'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK',
        'DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj'
    ]
    
    async with SolscanTransactionAnalyzer() as analyzer:
        # Analyze all target wallets
        results = await analyzer.analyze_all_target_wallets(target_wallets, limit=50)
        
        # Generate program mapping updates
        mapping_update = analyzer.generate_program_mapping_update(results)
        print(f"\n{mapping_update}")
        
        return results

if __name__ == "__main__":
    print("🚀 Starting Solscan Transaction Classification Analysis...")
    results = asyncio.run(main())
    print("\n✅ Analysis complete!")
