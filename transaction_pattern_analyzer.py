#!/usr/bin/env python3
"""
Transaction Pattern Analyzer
Analyzes the previous 50 executions for target wallets to identify transaction verification patterns
and compares them with current WebSocket monitoring system to ensure no future trades are missed.
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

class TransactionPatternAnalyzer:
    def __init__(self, rpc_url: str, target_wallets: List[str]):
        """Initialize the transaction pattern analyzer"""
        self.rpc_url = rpc_url
        self.target_wallets = target_wallets
        self.session = None
        
        # Current WebSocket monitored program IDs (from main.py)
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
            
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
            "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Trading",
            "39azUYFWPz3VHgKCf3VChUwbpURdCHRxjWVowf5jUJjg": "Pump.fun Router",
            
            # Orca
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca V1",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpools",
            
            # Phoenix
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix V1",
            
            # Others
            "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora",
            "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "Meteora DLMM",
            "2wT8Yq49kHgDzXuPxZSaeLaH1qbmGXtEyPy64bL7aD3c": "Lifinity V2",
            "EewxydAPCCVuNEP3LBaHp4qCWwSswUJcygtaEaYHatAx": "Lifinity V1",
            "AMM55ShdkoGRB5jVYPjWziwk8m5MpwyDgsMWHaMSQWH6": "GooseFX",
            "SSwpkEEcbUqx4vtoEByFjSkhKdCT862DNVb52nXHeH1": "Saros AMM",
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca V2",
            "Dooar9JkhdZ7J3LHN3A7YCuoGRUggXhQaG4kijfLGU2j": "Stepn",
            "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin": "Serum V3",
            "srmqPiDkYq2T6Nj6WtfU7Qh4Cd5ASBG7k5KwZoGvnH": "Serum V2",
            "EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o": "Saber",
            "SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8": "Saber Swap",
            "CTMAxxk34HjKWxQ3QLZL1MNAdXDcisG3CVnPrF9VbRkB": "Cropper",
            "MERLuDFBMmsHnsBPZw2sDQZHvXFMwp8EdjudcU2HKky": "Mercurial",
            "BSwp6bEBihVLdqJRKS58NwCjNYDAWcrjBQrD2HTRHVEr": "Step Finance",
            "AURY2249KY9qb78TXXaTdFpU33tDW3BKjSp5h7Jw7XjP": "Aurory",
            "61F3mYYaNu9EPevN6dRNUspjqoQtdUKGZp8KQHHy6Jfz": "Invariant"
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

    async def generate_coverage_report(self, all_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive coverage report"""
        try:
            logger.info(f"📊 GENERATING COMPREHENSIVE COVERAGE REPORT...")
            
            report = {
                'analysis_timestamp': datetime.now().isoformat(),
                'wallets_analyzed': len(all_patterns),
                'total_transactions': 0,
                'total_trades': 0,
                'total_detectable': 0,
                'total_missable': 0,
                'overall_detection_rate': 0.0,
                'program_gaps': {},
                'dex_coverage': {},
                'recommendations': [],
                'critical_missing_programs': [],
                'wallet_summaries': []
            }
            
            all_unmonitored_programs = Counter()
            all_dex_usage = Counter()
            
            # Aggregate data from all wallets
            for pattern in all_patterns:
                if 'error' in pattern:
                    continue
                    
                report['total_transactions'] += pattern['transactions_analyzed']
                report['total_trades'] += pattern['trades_detected']
                report['total_detectable'] += pattern['coverage_analysis']['would_detect']
                report['total_missable'] += pattern['coverage_analysis']['would_miss']
                
                # Aggregate unmonitored programs
                for program_id, count in pattern['unmonitored_programs'].items():
                    all_unmonitored_programs[program_id] += count
                
                # Aggregate DEX usage
                for dex, count in pattern['dex_usage'].items():
                    all_dex_usage[dex] += count
                
                # Wallet summary
                report['wallet_summaries'].append({
                    'wallet': pattern['wallet'][:8] + '...',
                    'transactions': pattern['transactions_analyzed'],
                    'trades': pattern['trades_detected'],
                    'detection_rate': pattern['coverage_analysis']['detection_rate'],
                    'time_range': {
                        'earliest': pattern['time_range']['earliest'].isoformat() if pattern['time_range']['earliest'] else None,
                        'latest': pattern['time_range']['latest'].isoformat() if pattern['time_range']['latest'] else None
                    }
                })
            
            # Calculate overall detection rate
            if report['total_trades'] > 0:
                report['overall_detection_rate'] = report['total_detectable'] / report['total_trades']
            
            # Identify critical missing programs
            report['critical_missing_programs'] = [
                {'program_id': program_id, 'usage_count': count}
                for program_id, count in all_unmonitored_programs.most_common(10)
                if count >= 2  # Programs used in 2+ transactions
            ]
            
            # DEX coverage analysis
            report['dex_coverage'] = dict(all_dex_usage.most_common())
            
            # Generate recommendations
            recommendations = []
            
            if report['overall_detection_rate'] < 0.95:
                recommendations.append(f"🚨 CRITICAL: Detection rate is {report['overall_detection_rate']:.1%}. Target should be >95%")
            
            if report['critical_missing_programs']:
                recommendations.append(f"➕ ADD MONITORING: {len(report['critical_missing_programs'])} critical programs not monitored")
                for program_info in report['critical_missing_programs'][:3]:
                    recommendations.append(f"   • {program_info['program_id']} (used {program_info['usage_count']} times)")
            
            if report['total_missable'] > 0:
                recommendations.append(f"⚠️  {report['total_missable']} trades would be missed with current monitoring")
            
            if not recommendations:
                recommendations.append("✅ Current monitoring appears comprehensive!")
            
            report['recommendations'] = recommendations
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating coverage report: {e}")
            return {'error': str(e)}

    async def save_analysis_results(self, all_patterns: List[Dict[str, Any]], coverage_report: Dict[str, Any]) -> str:
        """Save analysis results to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transaction_pattern_analysis_{timestamp}.json"
            
            results = {
                'metadata': {
                    'analysis_type': 'transaction_pattern_analysis',
                    'timestamp': timestamp,
                    'target_wallets': self.target_wallets,
                    'transactions_per_wallet': 50
                },
                'coverage_report': coverage_report,
                'wallet_patterns': all_patterns,
                'current_monitoring': {
                    'total_programs_monitored': len(self.monitored_programs),
                    'monitored_programs': self.monitored_programs
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"💾 Analysis results saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis results: {e}")
            return ""

async def main():
    """Main execution function"""
    try:
        # Import configuration
        from env_keys import EnvKeys
        from main import CopyTradeConfig
        
        env = EnvKeys()
        
        # Create config with target wallets
        target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Wallet 1
            "6KFXf7A97nKhKWYJr9rH6zzuY4kKoKYXKZadhq1yZVg4"   # Wallet 2
        ]
        
        config = CopyTradeConfig(target_wallets=target_wallets)
        
        logger.info("🚀 TRANSACTION PATTERN ANALYSIS STARTING")
        logger.info("=" * 60)
        logger.info(f"🎯 Target wallets: {len(config.target_wallets)}")
        logger.info(f"📊 Transactions per wallet: 50")
        logger.info(f"🔍 Analysis goal: Identify verification patterns & ensure WebSocket coverage")
        logger.info("=" * 60)
        
        async with TransactionPatternAnalyzer(env.HELIUS_RPC_URL, config.target_wallets) as analyzer:
            
            # Analyze patterns for each wallet
            all_patterns = []
            
            for i, wallet in enumerate(config.target_wallets, 1):
                logger.info(f"")
                logger.info(f"📡 WALLET {i}/{len(config.target_wallets)}: {wallet[:8]}...")
                
                pattern_analysis = await analyzer.analyze_wallet_patterns(wallet, 50)
                all_patterns.append(pattern_analysis)
                
                # Small delay between wallets
                if i < len(config.target_wallets):
                    logger.info(f"⏳ Waiting 2 seconds before next wallet...")
                    await asyncio.sleep(2)
            
            logger.info(f"")
            logger.info("📊 GENERATING COMPREHENSIVE COVERAGE REPORT...")
            
            # Generate coverage report
            coverage_report = await analyzer.generate_coverage_report(all_patterns)
            
            # Save results
            saved_file = await analyzer.save_analysis_results(all_patterns, coverage_report)
            
            # Display summary
            logger.info(f"")
            logger.info("=" * 60)
            logger.info("📈 TRANSACTION PATTERN ANALYSIS COMPLETE")
            logger.info("=" * 60)
            
            if 'error' not in coverage_report:
                logger.info(f"📊 COVERAGE SUMMARY:")
                logger.info(f"   🎯 Wallets analyzed: {coverage_report['wallets_analyzed']}")
                logger.info(f"   📈 Total transactions: {coverage_report['total_transactions']}")
                logger.info(f"   💹 Total trades detected: {coverage_report['total_trades']}")
                logger.info(f"   ✅ Would detect: {coverage_report['total_detectable']}")
                logger.info(f"   ❌ Would miss: {coverage_report['total_missable']}")
                logger.info(f"   📈 Detection rate: {coverage_report['overall_detection_rate']:.1%}")
                
                logger.info(f"")
                logger.info(f"🎯 KEY FINDINGS:")
                for recommendation in coverage_report['recommendations']:
                    logger.info(f"   {recommendation}")
                
                if coverage_report['critical_missing_programs']:
                    logger.info(f"")
                    logger.info(f"🚨 CRITICAL MISSING PROGRAMS:")
                    for program_info in coverage_report['critical_missing_programs'][:5]:
                        logger.info(f"   • {program_info['program_id']} (used {program_info['usage_count']} times)")
                
                logger.info(f"")
                logger.info(f"💾 Detailed results saved to: {saved_file}")
            else:
                logger.error(f"❌ Coverage report generation failed: {coverage_report['error']}")
            
            logger.info("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
