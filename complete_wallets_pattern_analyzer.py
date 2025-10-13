#!/usr/bin/env python3
"""
Complete Target Wallets Pattern Analysis
Analyze the previous 50 executions for BOTH correct target wallets to identify transaction verification patterns
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteWalletsPatternAnalyzer:
    def __init__(self, rpc_url: str, target_wallets: List[str]):
        """Initialize the complete wallets pattern analyzer"""
        self.rpc_url = rpc_url
        self.target_wallets = target_wallets
        self.session = None
        
        # Current WebSocket monitored program IDs (UPDATED with recent additions)
        self.monitored_programs = {
            # Jupiter
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            
            # Raydium
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
            "CamM7Te6wPCRqieiLvNHtmNnTsUhVLfafSJNMzUthhUU": "Raydium V5",
            "CLMM9tUoggJu2wagPkkqs9eFG4BWhVBZWkP1qv3Sp7tR": "Raydium CLMM",
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM Alt",
            
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
            "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Trading",
            "39azUYFWPz3VHgKCf3VchUwbpURdCHRxjWVowf5jUJjg": "Pump.fun Router",
            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Pump.fun Trading V2",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router V2",
            
            # Orca
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca V1",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpools",
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca V2",
            
            # Phoenix
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix V1",
            
            # Others
            "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora",
            "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "Meteora DLMM",
            "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora V2",
            "2wT8Yq49kHgDzXuPxZSaeLaH1qbmGXtEyPy64bL7aD3c": "Lifinity V2",
            "EewxydAPCCVuNEP3LBaHp4qCWwSswUJcygtaEaYHatAx": "Lifinity V1",
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity V3",
            "AMM55ShdkoGRB5jVYPjWziwk8m5MpwyDgsMWHaMSQWH6": "GooseFX",
            "SSwpkEEcbUqx4vtoEByFjSkhKdCT862DNVb52nXHeH1": "Saros AMM",
            "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX",
            
            # 🚨 CRITICAL PROGRAMS ADDED from first wallet analysis
            "WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh": "Target Wallet DEX Router",
            "2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr": "Target Wallet DEX Program",
            "6s1xP3hpbAfFoNtUNF8mfHsjr2Bd97JxFJRWLbL6aHuX": "Target Wallet Token Swap",
            "FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1": "Target Wallet Liquidity",
            "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv": "Target Wallet DEX #2",
            "Z9z6LsWmKURFCYKptcQLjmXUB4HbhcTwXCcHYTme8K6": "Target Wallet DEX #3",
            "9djsqy8mnbmPZJoYp1SqDyqQsz22YNRsrPtbXPcWQqHc": "Target Wallet DEX #4",
            "9smUrM3MpvJAbCLbuzkxSKSuBRR8mKeKSjjde8ao3j4t": "Target Wallet DEX #5",
            "GpH7NwogU6QGG4aQQXicTitwV8Yx5KL9pVcZZo3sK6jz": "Target Wallet DEX #6",
            "2SDG5aK3r55KZ97VqrnGU9AntFadmDr7S2Kenbuabonk": "Target Wallet DEX #7",
            "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95": "Target Wallet Router #1",
            "GwQ9bcrcZAEK3W1S9HyiSsJAVVXSz8Zr8ExbppdJ4zQU": "Target Wallet Router #2",
            "BmCNT7mkSuzBi7x51PQEZGM9wPa3CBGgMHZtvinp2r5U": "Target Wallet Router #3",
            "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY": "Target Wallet Router #4",
            "jitodontfrontd1111111TradeWithAxiomDotTrade": "Axiom Trade Router",
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def get_wallet_transactions(self, wallet_address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history for a wallet using Helius RPC"""
        try:
            logger.info(f"📡 Fetching {limit} transactions for wallet {wallet_address[:8]}...")
            
            # Use Helius RPC to get transaction signatures
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    wallet_address,
                    {
                        "limit": limit,
                        "commitment": "finalized"
                    }
                ]
            }
            
            async with self.session.post(self.rpc_url, json=payload) as response:
                if response.status != 200:
                    logger.error(f"❌ RPC request failed with status {response.status}")
                    return []
                    
                data = await response.json()
                
                if 'error' in data:
                    logger.error(f"❌ RPC error: {data['error']}")
                    return []
                    
                signatures = data.get('result', [])
                logger.info(f"✅ Retrieved {len(signatures)} transaction signatures")
                
                # Get detailed transaction data for each signature
                transactions = []
                for i, sig_info in enumerate(signatures):
                    signature = sig_info['signature']
                    
                    # Get detailed transaction
                    tx_detail = await self.get_transaction_detail(signature)
                    if tx_detail:
                        transactions.append(tx_detail)
                        
                    # Progress update every 10 transactions
                    if (i + 1) % 10 == 0:
                        logger.info(f"⏳ Processed {i + 1}/{len(signatures)} transactions...")
                        
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                
                logger.info(f"✅ Successfully processed {len(transactions)} detailed transactions")
                return transactions
                
        except Exception as e:
            logger.error(f"❌ Error fetching transactions for {wallet_address}: {e}")
            return []

    async def get_transaction_detail(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get detailed transaction information"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "jsonParsed",
                        "maxSupportedTransactionVersion": 0,
                        "commitment": "finalized"
                    }
                ]
            }
            
            async with self.session.post(self.rpc_url, json=payload) as response:
                if response.status != 200:
                    return None
                    
                data = await response.json()
                
                if 'error' in data or not data.get('result'):
                    return None
                    
                return data['result']
                
        except Exception as e:
            logger.debug(f"Error getting transaction detail for {signature}: {e}")
            return None

    def analyze_transaction_programs(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a transaction to extract program IDs and patterns"""
        try:
            analysis = {
                'signature': transaction.get('transaction', {}).get('signatures', [''])[0],
                'slot': transaction.get('slot'),
                'timestamp': None,
                'program_ids': [],
                'monitored_programs': [],
                'unmonitored_programs': [],
                'instruction_count': 0,
                'inner_instruction_count': 0,
                'account_keys': [],
                'balance_changes': {},
                'is_trade': False,
                'trade_type': None,
                'token_involved': None,
                'dex_detected': None
            }
            
            # Extract timestamp
            if transaction.get('blockTime'):
                analysis['timestamp'] = datetime.fromtimestamp(transaction['blockTime'])
            
            # Extract program IDs from instructions
            message = transaction.get('transaction', {}).get('message', {})
            
            # Get account keys
            account_keys = message.get('accountKeys', [])
            if isinstance(account_keys, list):
                analysis['account_keys'] = [
                    key.get('pubkey', key) if isinstance(key, dict) else str(key) 
                    for key in account_keys
                ]
            
            # Extract program IDs from instructions
            instructions = message.get('instructions', [])
            analysis['instruction_count'] = len(instructions)
            
            program_ids = set()
            
            # Main instructions
            for instruction in instructions:
                if isinstance(instruction, dict):
                    program_id_index = instruction.get('programIdIndex')
                    if program_id_index is not None and program_id_index < len(analysis['account_keys']):
                        program_id = analysis['account_keys'][program_id_index]
                        program_ids.add(program_id)
            
            # Inner instructions
            meta = transaction.get('meta', {})
            inner_instructions = meta.get('innerInstructions', [])
            
            inner_count = 0
            for inner_group in inner_instructions:
                inner_instrs = inner_group.get('instructions', [])
                inner_count += len(inner_instrs)
                
                for inner_instr in inner_instrs:
                    if isinstance(inner_instr, dict):
                        program_id_index = inner_instr.get('programIdIndex')
                        if program_id_index is not None and program_id_index < len(analysis['account_keys']):
                            program_id = analysis['account_keys'][program_id_index]
                            program_ids.add(program_id)
            
            analysis['inner_instruction_count'] = inner_count
            analysis['program_ids'] = list(program_ids)
            
            # Categorize programs
            for program_id in program_ids:
                if program_id in self.monitored_programs:
                    analysis['monitored_programs'].append({
                        'program_id': program_id,
                        'name': self.monitored_programs[program_id]
                    })
                else:
                    analysis['unmonitored_programs'].append(program_id)
            
            # Analyze balance changes for trade detection
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            
            if len(pre_balances) == len(post_balances):
                for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                    if i < len(analysis['account_keys']):
                        account = analysis['account_keys'][i]
                        change = (post - pre) / 1e9  # Convert lamports to SOL
                        if abs(change) > 0.001:  # Only significant changes
                            analysis['balance_changes'][account] = change
            
            # Detect if this looks like a trade
            analysis['is_trade'] = self.detect_trade_pattern(analysis)
            
            # Detect DEX if monitored programs present
            if analysis['monitored_programs']:
                analysis['dex_detected'] = analysis['monitored_programs'][0]['name']
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing transaction programs: {e}")
            return {
                'signature': 'ERROR',
                'error': str(e),
                'program_ids': [],
                'monitored_programs': [],
                'unmonitored_programs': []
            }

    def detect_trade_pattern(self, analysis: Dict[str, Any]) -> bool:
        """Detect if transaction appears to be a trade based on patterns"""
        try:
            # Check for known DEX programs
            if analysis['monitored_programs']:
                return True
            
            # Check for balance changes that look like trades
            balance_changes = analysis['balance_changes']
            if len(balance_changes) >= 2:
                # Look for SOL decrease (buy) or increase (sell) patterns
                sol_changes = [change for account, change in balance_changes.items() if abs(change) > 0.01]
                if len(sol_changes) >= 1:
                    return True
            
            # Check for token program involvement
            token_program = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            if token_program in analysis['program_ids']:
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Trade detection error: {e}")
            return False

    async def analyze_wallet_patterns(self, wallet_address: str, limit: int = 50) -> Dict[str, Any]:
        """Analyze transaction patterns for a specific wallet"""
        try:
            logger.info(f"🔍 ANALYZING PATTERNS for wallet {wallet_address[:8]}...")
            
            # Get transaction history
            transactions = await self.get_wallet_transactions(wallet_address, limit)
            
            if not transactions:
                return {
                    'wallet': wallet_address,
                    'error': 'No transactions retrieved',
                    'transactions_analyzed': 0
                }
            
            # Analyze each transaction
            pattern_analysis = {
                'wallet': wallet_address,
                'transactions_analyzed': len(transactions),
                'trades_detected': 0,
                'monitored_trades': 0,
                'unmonitored_trades': 0,
                'program_usage': {},
                'dex_usage': {},
                'unmonitored_programs': Counter(),
                'time_range': {
                    'earliest': None,
                    'latest': None
                },
                'detailed_transactions': [],
                'coverage_analysis': {
                    'would_detect': 0,
                    'would_miss': 0,
                    'detection_rate': 0.0
                }
            }
            
            earliest_time = None
            latest_time = None
            
            for transaction in transactions:
                analysis = self.analyze_transaction_programs(transaction)
                pattern_analysis['detailed_transactions'].append(analysis)
                
                # Track time range
                if analysis['timestamp']:
                    if earliest_time is None or analysis['timestamp'] < earliest_time:
                        earliest_time = analysis['timestamp']
                    if latest_time is None or analysis['timestamp'] > latest_time:
                        latest_time = analysis['timestamp']
                
                # Count program usage
                for program_id in analysis['program_ids']:
                    pattern_analysis['program_usage'][program_id] = pattern_analysis['program_usage'].get(program_id, 0) + 1
                
                # Count DEX usage
                if analysis['dex_detected']:
                    pattern_analysis['dex_usage'][analysis['dex_detected']] = pattern_analysis['dex_usage'].get(analysis['dex_detected'], 0) + 1
                
                # Count unmonitored programs
                for program_id in analysis['unmonitored_programs']:
                    pattern_analysis['unmonitored_programs'][program_id] += 1
                
                # Count trades
                if analysis['is_trade']:
                    pattern_analysis['trades_detected'] += 1
                    
                    if analysis['monitored_programs']:
                        pattern_analysis['monitored_trades'] += 1
                        pattern_analysis['coverage_analysis']['would_detect'] += 1
                    else:
                        pattern_analysis['unmonitored_trades'] += 1
                        pattern_analysis['coverage_analysis']['would_miss'] += 1
            
            # Set time range
            pattern_analysis['time_range']['earliest'] = earliest_time
            pattern_analysis['time_range']['latest'] = latest_time
            
            # Calculate detection rate
            total_trades = pattern_analysis['trades_detected']
            if total_trades > 0:
                pattern_analysis['coverage_analysis']['detection_rate'] = (
                    pattern_analysis['coverage_analysis']['would_detect'] / total_trades
                )
            
            logger.info(f"✅ Pattern analysis complete for {wallet_address[:8]}...")
            logger.info(f"   📊 {pattern_analysis['transactions_analyzed']} transactions analyzed")
            logger.info(f"   💹 {pattern_analysis['trades_detected']} trades detected")
            logger.info(f"   ✅ {pattern_analysis['monitored_trades']} would be detected by WebSocket")
            logger.info(f"   ❌ {pattern_analysis['unmonitored_trades']} would be missed")
            logger.info(f"   📈 Detection rate: {pattern_analysis['coverage_analysis']['detection_rate']:.1%}")
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing patterns for {wallet_address}: {e}")
            return {
                'wallet': wallet_address,
                'error': str(e),
                'transactions_analyzed': 0
            }

    async def generate_comprehensive_report(self, all_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive report comparing both wallets"""
        try:
            logger.info(f"📊 GENERATING COMPREHENSIVE COMPARISON REPORT...")
            
            report = {
                'analysis_timestamp': datetime.now().isoformat(),
                'wallets_analyzed': len(all_patterns),
                'total_transactions': 0,
                'total_trades': 0,
                'total_detectable': 0,
                'total_missable': 0,
                'overall_detection_rate': 0.0,
                'wallet_comparison': [],
                'combined_missing_programs': Counter(),
                'combined_dex_usage': Counter(),
                'recommendations': [],
                'new_programs_discovered': []
            }
            
            # Analyze each wallet
            for pattern in all_patterns:
                if 'error' in pattern:
                    continue
                    
                wallet_summary = {
                    'wallet': pattern['wallet'][:8] + '...',
                    'full_address': pattern['wallet'],
                    'transactions': pattern['transactions_analyzed'],
                    'trades': pattern['trades_detected'],
                    'detection_rate': pattern['coverage_analysis']['detection_rate'],
                    'would_detect': pattern['coverage_analysis']['would_detect'],
                    'would_miss': pattern['coverage_analysis']['would_miss'],
                    'unique_missing_programs': len(pattern['unmonitored_programs']),
                    'top_missing_programs': dict(pattern['unmonitored_programs'].most_common(5))
                }
                
                report['wallet_comparison'].append(wallet_summary)
                
                # Aggregate data
                report['total_transactions'] += pattern['transactions_analyzed']
                report['total_trades'] += pattern['trades_detected']
                report['total_detectable'] += pattern['coverage_analysis']['would_detect']
                report['total_missable'] += pattern['coverage_analysis']['would_miss']
                
                # Combine missing programs
                for program_id, count in pattern['unmonitored_programs'].items():
                    report['combined_missing_programs'][program_id] += count
                
                # Combine DEX usage
                for dex, count in pattern['dex_usage'].items():
                    report['combined_dex_usage'][dex] += count
            
            # Calculate overall detection rate
            if report['total_trades'] > 0:
                report['overall_detection_rate'] = report['total_detectable'] / report['total_trades']
            
            # Find new programs not yet in monitoring
            current_monitored = set(self.monitored_programs.keys())
            all_discovered_programs = set(report['combined_missing_programs'].keys())
            truly_new_programs = all_discovered_programs - current_monitored
            
            report['new_programs_discovered'] = [
                {
                    'program_id': program_id,
                    'usage_count': report['combined_missing_programs'][program_id],
                    'is_critical': report['combined_missing_programs'][program_id] >= 3
                }
                for program_id in sorted(truly_new_programs, 
                                       key=lambda x: report['combined_missing_programs'][x], 
                                       reverse=True)
            ]
            
            # Generate recommendations
            recommendations = []
            
            if report['overall_detection_rate'] < 0.95:
                recommendations.append(f"🚨 CRITICAL: Overall detection rate is {report['overall_detection_rate']:.1%}. Target should be >95%")
            
            if len(report['new_programs_discovered']) > 0:
                critical_new = [p for p in report['new_programs_discovered'] if p['is_critical']]
                recommendations.append(f"➕ ADD MONITORING: {len(critical_new)} new critical programs discovered")
                
            # Compare wallets
            if len(report['wallet_comparison']) >= 2:
                wallet1 = report['wallet_comparison'][0]
                wallet2 = report['wallet_comparison'][1]
                
                if abs(wallet1['detection_rate'] - wallet2['detection_rate']) > 0.1:
                    better_wallet = wallet1 if wallet1['detection_rate'] > wallet2['detection_rate'] else wallet2
                    worse_wallet = wallet2 if wallet1['detection_rate'] > wallet2['detection_rate'] else wallet1
                    recommendations.append(f"⚠️  Detection rate varies: {better_wallet['wallet']} ({better_wallet['detection_rate']:.1%}) vs {worse_wallet['wallet']} ({worse_wallet['detection_rate']:.1%})")
            
            if not recommendations:
                recommendations.append("✅ Both wallets have good coverage with current monitoring!")
            
            report['recommendations'] = recommendations
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating comprehensive report: {e}")
            return {'error': str(e)}

    async def save_complete_analysis_results(self, all_patterns: List[Dict[str, Any]], comprehensive_report: Dict[str, Any]) -> str:
        """Save complete analysis results to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"complete_wallets_pattern_analysis_{timestamp}.json"
            
            results = {
                'metadata': {
                    'analysis_type': 'complete_wallets_pattern_analysis',
                    'timestamp': timestamp,
                    'target_wallets': self.target_wallets,
                    'transactions_per_wallet': 50,
                    'note': 'Analysis of BOTH correct target wallets'
                },
                'comprehensive_report': comprehensive_report,
                'individual_wallet_patterns': all_patterns,
                'current_monitoring': {
                    'total_programs_monitored': len(self.monitored_programs),
                    'monitored_programs': self.monitored_programs
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"💾 Complete analysis results saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving complete analysis results: {e}")
            return ""

async def main():
    """Main execution function"""
    try:
        # Import configuration
        from env_keys import EnvKeys
        
        env = EnvKeys()
        
        # CORRECT target wallets (both of them)
        target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Wallet 1 (analyzed before)
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Wallet 2 (NEW analysis)
        ]
        
        logger.info("🚀 COMPLETE TARGET WALLETS PATTERN ANALYSIS STARTING")
        logger.info("=" * 70)
        logger.info(f"🎯 Target wallets: {len(target_wallets)}")
        for i, wallet in enumerate(target_wallets, 1):
            logger.info(f"   {i}. {wallet[:8]}...{wallet[-8:]} ({'ANALYZED BEFORE' if i == 1 else 'NEW ANALYSIS'})")
        logger.info(f"📊 Transactions per wallet: 50")
        logger.info(f"🔍 Analysis goal: Complete pattern comparison between both wallets")
        logger.info("=" * 70)
        
        async with CompleteWalletsPatternAnalyzer(env.HELIUS_RPC_URL, target_wallets) as analyzer:
            
            # Analyze patterns for each wallet
            all_patterns = []
            
            for i, wallet in enumerate(target_wallets, 1):
                logger.info(f"")
                logger.info(f"📡 WALLET {i}/{len(target_wallets)}: {wallet[:8]}...{wallet[-8:]}")
                if i == 2:
                    logger.info(f"🔍 NEW ANALYSIS: This is the wallet we haven't analyzed yet!")
                
                pattern_analysis = await analyzer.analyze_wallet_patterns(wallet, 50)
                all_patterns.append(pattern_analysis)
                
                # Small delay between wallets
                if i < len(target_wallets):
                    logger.info(f"⏳ Waiting 2 seconds before next wallet...")
                    await asyncio.sleep(2)
            
            logger.info(f"")
            logger.info("📊 GENERATING COMPREHENSIVE COMPARISON REPORT...")
            
            # Generate comprehensive report
            comprehensive_report = await analyzer.generate_comprehensive_report(all_patterns)
            
            # Save results
            saved_file = await analyzer.save_complete_analysis_results(all_patterns, comprehensive_report)
            
            # Display summary
            logger.info(f"")
            logger.info("=" * 70)
            logger.info("📈 COMPLETE WALLETS PATTERN ANALYSIS RESULTS")
            logger.info("=" * 70)
            
            if 'error' not in comprehensive_report:
                logger.info(f"📊 OVERALL SUMMARY:")
                logger.info(f"   🎯 Wallets analyzed: {comprehensive_report['wallets_analyzed']}")
                logger.info(f"   📈 Total transactions: {comprehensive_report['total_transactions']}")
                logger.info(f"   💹 Total trades detected: {comprehensive_report['total_trades']}")
                logger.info(f"   ✅ Would detect: {comprehensive_report['total_detectable']}")
                logger.info(f"   ❌ Would miss: {comprehensive_report['total_missable']}")
                logger.info(f"   📈 Overall detection rate: {comprehensive_report['overall_detection_rate']:.1%}")
                
                logger.info(f"")
                logger.info(f"📊 WALLET COMPARISON:")
                for wallet_data in comprehensive_report['wallet_comparison']:
                    logger.info(f"   🔸 {wallet_data['wallet']} ({wallet_data['full_address'][:8]}...{wallet_data['full_address'][-8:]}):")
                    logger.info(f"      📈 {wallet_data['transactions']} transactions, {wallet_data['trades']} trades")
                    logger.info(f"      📊 Detection rate: {wallet_data['detection_rate']:.1%}")
                    logger.info(f"      ✅ Would detect: {wallet_data['would_detect']}")
                    logger.info(f"      ❌ Would miss: {wallet_data['would_miss']}")
                    logger.info(f"      🔍 Unique missing programs: {wallet_data['unique_missing_programs']}")
                
                logger.info(f"")
                logger.info(f"🎯 KEY FINDINGS:")
                for recommendation in comprehensive_report['recommendations']:
                    logger.info(f"   {recommendation}")
                
                if comprehensive_report['new_programs_discovered']:
                    logger.info(f"")
                    logger.info(f"🆕 NEW PROGRAMS DISCOVERED:")
                    for i, program_info in enumerate(comprehensive_report['new_programs_discovered'][:10], 1):
                        status = "🚨 CRITICAL" if program_info['is_critical'] else "📝 Monitor"
                        logger.info(f"   {i:2d}. {program_info['program_id']} (used {program_info['usage_count']} times) - {status}")
                
                logger.info(f"")
                logger.info(f"💾 Complete analysis results saved to: {saved_file}")
            else:
                logger.error(f"❌ Comprehensive report generation failed: {comprehensive_report['error']}")
            
            logger.info("=" * 70)
            
    except Exception as e:
        logger.error(f"❌ Complete analysis failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
