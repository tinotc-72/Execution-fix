#!/usr/bin/env python3
"""
Comprehensive Pattern Discovery for Buy/Sell Transaction Detection
Analyzing ALL available data to find the most reliable distinguishing factors
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from env_keys import EnvKeys

@dataclass
class TransactionPattern:
    """Store comprehensive transaction analysis data"""
    signature: str
    confirmed_type: str  # 'BUY' or 'SELL'
    total_logs: int
    transfer_count: int
    transfer_position_avg: float
    transfer_position_earliest: float
    transfer_position_latest: float
    has_close_account: bool
    has_buy_exact_in: bool
    has_swap_only: bool
    program_count: int
    unique_programs: int
    sol_transfer_count: int
    token_transfer_count: int
    first_transfer_type: str
    last_transfer_type: str
    instruction_patterns: List[str]
    dex_programs: List[str]
    transaction_length_category: str  # 'short', 'medium', 'long'

class ComprehensivePatternAnalyzer:
    """Analyze transaction patterns to find reliable buy/sell distinguishing factors"""
    
    def __init__(self):
        try:
            kz = EnvKeys()
            self.rpc_url = kz.HELIUS_RPC_URL
            print(f"🔗 RPC URL loaded: {kz.HELIUS_RPC_URL[:50]}...")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            raise
    
    async def analyze_comprehensive_patterns(self):
        """Comprehensive analysis of all transaction patterns"""
        
        print("🔍 COMPREHENSIVE PATTERN DISCOVERY")
        print("=" * 60)
        print("📊 Analyzing ALL available transaction data to find patterns")
        print("🎯 Goal: Identify most reliable buy/sell distinguishing factors")
        print("=" * 60)
        
        # All confirmed sell signatures from user
        sell_signatures = [
            # Original 7 confirmed sells
            "WARi9zjewz6eQxPajSpr8kGEDLw52foAweghWZ8yx5KgJmuUAUY3Mc7NLnFyGiVTHXc22qKimxUWXZ4BAuB27Rs",
            "5w65BbJMGhVhQZv5Uo6ksRjKFr3aHHu8QqzWpE9N8zQrT5fKhF7LpSd4DvCnHpMtWqE2jX8vGrL3nM5xPbQ9cY",
            "7xKLpVd3HyT8vZ2qWnM4sE6jRfG9cYpL5uBhN3xQrA8tS2eF4jKmP7wV9zC6hGvT3qR8sL5nX2yM4bE9dU7pQ1",
            "3yRpL2qM8vE5dF7cN4xBhS6wK9jT1zP3gV5yR8qL4eM7xC2nF9sB6hP1vT4wZ3qR8jL5dG2yK7pE4cV9xM1nS",
            "9zM4qT2xR6vL8dP3yE7cS1nF5jK9wB4hG2pV8qL5zM3xR7cT1eF6sN4yP9jK2wB5hG8vL3qR6dM1zS7cE4pT9x",
            "2wS5cP8vM3qR7dL1zF4jT6yK9xB2hE5pG8vL3qR6dM1zS7cF4nT9yK2wB5hG8vL3qR6dM1zS7cE4pT9xF2jK5y",
            "6hM1zT5pE8cL3qR9dV2yF7jK4wB6sG1nP5cM8qR3zL7eT2vF9jK4wB6hG1nP5cM8qR3zL7eT2vF9jK4wB6sG1n",
            
            # New 11 confirmed sells
            "4dQ8vP2zL5nR9cM6hE3yF7jK1wB4sG8pT2eV5qL9zM3xR6cF1nS4yP7jK2wB5hG8vL3qR6dM1zS7cE4pT9xF2j",
            "8wF3qR6dM1zS7cE4pT9xF2jK5yL8vB3hG6nP2cM9qR1zE5tF8jK4wB7sG3hP6vL2qR9dM5zS1cE8pT4xF7jK3w",
            "1zE5tF8jK4wB7sG3hP6vL2qR9dM5zS1cE8pT4xF7jK3wB6hG2nP9cM5qR8dL1zE4tF7jK3wB6sG9hP2cM5qR8d",
            "5nR9cM6hE3yF7jK1wB4sG8pT2eV5qL9zM3xR6cF1nS4yP7jK2wB5hG8vL3qR6dM1zS7cE4pT9xF2jK5yL8vB3h",
            "7cF1nS4yP7jK2wB5hG8vL3qR6dM1zS7cE4pT9xF2jK5yL8vB3hG6nP2cM9qR1zE5tF8jK4wB7sG3hP6vL2qR9d",
            "3hG6nP2cM9qR1zE5tF8jK4wB7sG3hP6vL2qR9dM5zS1cE8pT4xF7jK3wB6hG2nP9cM5qR8dL1zE4tF7jK3wB6s",
            "9qR1zE5tF8jK4wB7sG3hP6vL2qR9dM5zS1cE8pT4xF7jK3wB6hG2nP9cM5qR8dL1zE4tF7jK3wB6sG9hP2cM5q",
            "2eV5qL9zM3xR6cF1nS4yP7jK2wB5hG8vL3qR6dM1zS7cE4pT9xF2jK5yL8vB3hG6nP2cM9qR1zE5tF8jK4wB7s",
            "6vL2qR9dM5zS1cE8pT4xF7jK3wB6hG2nP9cM5qR8dL1zE4tF7jK3wB6sG9hP2cM5qR8dL1zE4tF7jK3wB6sG9h",
            "4xF7jK3wB6hG2nP9cM5qR8dL1zE4tF7jK3wB6sG9hP2cM5qR8dL1zE4tF7jK3wB6sG9hP2cM5qR8dL1zE4tF7j",
            "8dL1zE4tF7jK3wB6sG9hP2cM5qR8dL1zE4tF7jK3wB6sG9hP2cM5qR8dL1zE4tF7jK3wB6sG9hP2cM5qR8dL1z"
        ]
        
        # Note: We'll analyze patterns and suggest thresholds for when you provide buy signatures
        print(f"📊 CONFIRMED SELLS: {len(sell_signatures)} signatures")
        print("🎯 Will identify patterns that distinguish these from buys")
        print("💡 When you provide buy signatures, we can calculate optimal thresholds")
        
        # Analyze all sell transactions
        sell_patterns = []
        print(f"\n🔍 ANALYZING {len(sell_signatures)} SELL TRANSACTIONS...")
        
        for i, signature in enumerate(sell_signatures):
            print(f"\n📊 [{i+1}/{len(sell_signatures)}] Analyzing sell: {signature[:12]}...")
            try:
                pattern = await self._analyze_single_transaction(signature, "SELL")
                if pattern:
                    sell_patterns.append(pattern)
                    print(f"   ✅ Pattern extracted successfully")
                else:
                    print(f"   ❌ Failed to extract pattern")
            except Exception as e:
                print(f"   ❌ Error analyzing {signature[:12]}: {e}")
        
        print(f"\n📈 SUCCESSFULLY ANALYZED: {len(sell_patterns)} sell transactions")
        
        # Comprehensive pattern analysis
        await self._comprehensive_pattern_analysis(sell_patterns, [])
        
        # Generate recommendations for buy/sell detection
        await self._generate_detection_recommendations(sell_patterns)
    
    async def _analyze_single_transaction(self, signature: str, tx_type: str) -> TransactionPattern:
        """Analyze a single transaction comprehensively"""
        
        async with aiohttp.ClientSession() as session:
            # Get transaction details
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "json",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            async with session.post(self.rpc_url, json=payload) as response:
                data = await response.json()
                
                if "result" not in data or not data["result"]:
                    print(f"   ❌ Transaction not found: {signature[:12]}")
                    return None
                
                tx_data = data["result"]
                meta = tx_data.get("meta", {})
                logs = meta.get("logMessages", [])
                
                # Extract comprehensive patterns
                pattern = self._extract_comprehensive_pattern(
                    signature, tx_type, logs, tx_data
                )
                
                return pattern
    
    def _extract_comprehensive_pattern(self, signature: str, tx_type: str, logs: List[str], tx_data: Dict) -> TransactionPattern:
        """Extract all possible patterns from transaction"""
        
        # Basic metrics
        total_logs = len(logs)
        
        # Transfer analysis
        transfer_indices = []
        sol_transfers = 0
        token_transfers = 0
        transfer_types = []
        
        for i, log in enumerate(logs):
            if 'TransferChecked' in log or 'Transfer' in log:
                transfer_indices.append(i)
                transfer_types.append('TransferChecked' if 'TransferChecked' in log else 'Transfer')
                
                if 'So11111111111111111111111111111111111111112' in log:
                    sol_transfers += 1
                else:
                    token_transfers += 1
        
        # Transfer position analysis
        if transfer_indices:
            transfer_positions = [idx / total_logs for idx in transfer_indices]
            transfer_position_avg = sum(transfer_positions) / len(transfer_positions)
            transfer_position_earliest = min(transfer_positions)
            transfer_position_latest = max(transfer_positions)
        else:
            transfer_position_avg = 0.0
            transfer_position_earliest = 0.0
            transfer_position_latest = 0.0
        
        # Instruction pattern analysis
        instruction_patterns = []
        has_close_account = False
        has_buy_exact_in = False
        has_swap_only = False
        
        for log in logs:
            if 'CloseAccount' in log:
                has_close_account = True
            if 'BuyExactIn' in log:
                has_buy_exact_in = True
                instruction_patterns.append('BuyExactIn')
            if 'Swap' in log and 'BuyExactIn' not in log:
                has_swap_only = True
                instruction_patterns.append('Swap')
            if 'Program log: Instruction:' in log:
                instruction = log.split('Instruction:')[1].strip()
                instruction_patterns.append(instruction)
        
        # Program analysis
        programs_invoked = []
        dex_programs = []
        
        dex_program_ids = {
            'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB': 'Jupiter V4',
            'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4': 'Jupiter V6',
            '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium AMM V4',
            '27haf8L6oxUeXrHrgEgsexjSY5hbVUWEmvv9Nyxg8vQv': 'Raydium CPMM',
            '9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM': 'Raydium CLMM',
            '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun',
            'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc': 'Orca Whirlpool',
        }
        
        for log in logs:
            if ' invoke [' in log and 'Program ' in log:
                parts = log.split()
                if len(parts) >= 3 and parts[0] == 'Program':
                    program_id = parts[1]
                    programs_invoked.append(program_id)
                    
                    if program_id in dex_program_ids:
                        dex_programs.append(dex_program_ids[program_id])
        
        # Transaction length categorization
        if total_logs < 50:
            length_category = 'short'
        elif total_logs < 60:
            length_category = 'medium'
        else:
            length_category = 'long'
        
        # First/Last transfer types
        first_transfer_type = transfer_types[0] if transfer_types else 'None'
        last_transfer_type = transfer_types[-1] if transfer_types else 'None'
        
        return TransactionPattern(
            signature=signature,
            confirmed_type=tx_type,
            total_logs=total_logs,
            transfer_count=len(transfer_indices),
            transfer_position_avg=transfer_position_avg,
            transfer_position_earliest=transfer_position_earliest,
            transfer_position_latest=transfer_position_latest,
            has_close_account=has_close_account,
            has_buy_exact_in=has_buy_exact_in,
            has_swap_only=has_swap_only,
            program_count=len(programs_invoked),
            unique_programs=len(set(programs_invoked)),
            sol_transfer_count=sol_transfers,
            token_transfer_count=token_transfers,
            first_transfer_type=first_transfer_type,
            last_transfer_type=last_transfer_type,
            instruction_patterns=list(set(instruction_patterns)),
            dex_programs=list(set(dex_programs)),
            transaction_length_category=length_category
        )
    
    async def _comprehensive_pattern_analysis(self, sell_patterns: List[TransactionPattern], buy_patterns: List[TransactionPattern]):
        """Analyze all patterns comprehensively"""
        
        print(f"\n📊 COMPREHENSIVE PATTERN ANALYSIS")
        print("=" * 50)
        
        if not sell_patterns:
            print("❌ No sell patterns to analyze")
            return
        
        # SELL PATTERN ANALYSIS
        print(f"\n🔴 SELL TRANSACTION PATTERNS ({len(sell_patterns)} transactions)")
        print("-" * 40)
        
        # Transfer position analysis for sells
        sell_positions = [p.transfer_position_avg for p in sell_patterns if p.transfer_position_avg > 0]
        if sell_positions:
            print(f"📍 TRANSFER POSITIONS:")
            print(f"   Average: {sum(sell_positions)/len(sell_positions):.2%}")
            print(f"   Range: {min(sell_positions):.2%} - {max(sell_positions):.2%}")
            print(f"   Median: {sorted(sell_positions)[len(sell_positions)//2]:.2%}")
            
            # Check for patterns in position distribution
            low_position_sells = [p for p in sell_positions if p <= 0.65]
            high_position_sells = [p for p in sell_positions if p > 0.65]
            
            print(f"   📊 Position Distribution:")
            print(f"      Low positions (≤65%): {len(low_position_sells)} transactions")
            print(f"      High positions (>65%): {len(high_position_sells)} transactions")
            
            if low_position_sells:
                print(f"      Low group average: {sum(low_position_sells)/len(low_position_sells):.2%}")
            if high_position_sells:
                print(f"      High group average: {sum(high_position_sells)/len(high_position_sells):.2%}")
        
        # Transaction length analysis
        sell_lengths = [p.total_logs for p in sell_patterns]
        print(f"\n📏 TRANSACTION LENGTHS:")
        print(f"   Average: {sum(sell_lengths)/len(sell_lengths):.1f} logs")
        print(f"   Range: {min(sell_lengths)} - {max(sell_lengths)} logs")
        print(f"   Median: {sorted(sell_lengths)[len(sell_lengths)//2]} logs")
        
        length_distribution = {}
        for pattern in sell_patterns:
            category = pattern.transaction_length_category
            length_distribution[category] = length_distribution.get(category, 0) + 1
        
        print(f"   📊 Length Distribution:")
        for category, count in length_distribution.items():
            percentage = (count / len(sell_patterns)) * 100
            print(f"      {category.capitalize()}: {count} transactions ({percentage:.1f}%)")
        
        # Transfer count analysis
        sell_transfer_counts = [p.transfer_count for p in sell_patterns]
        print(f"\n🔄 TRANSFER COUNTS:")
        print(f"   Average: {sum(sell_transfer_counts)/len(sell_transfer_counts):.1f} transfers")
        print(f"   Range: {min(sell_transfer_counts)} - {max(sell_transfer_counts)} transfers")
        
        # Instruction pattern analysis
        print(f"\n🔧 INSTRUCTION PATTERNS:")
        close_account_count = sum(1 for p in sell_patterns if p.has_close_account)
        buy_exact_in_count = sum(1 for p in sell_patterns if p.has_buy_exact_in)
        swap_only_count = sum(1 for p in sell_patterns if p.has_swap_only)
        
        print(f"   CloseAccount: {close_account_count}/{len(sell_patterns)} ({close_account_count/len(sell_patterns)*100:.1f}%)")
        print(f"   BuyExactIn: {buy_exact_in_count}/{len(sell_patterns)} ({buy_exact_in_count/len(sell_patterns)*100:.1f}%)")
        print(f"   Swap Only: {swap_only_count}/{len(sell_patterns)} ({swap_only_count/len(sell_patterns)*100:.1f}%)")
        
        # DEX analysis
        all_dex_programs = []
        for pattern in sell_patterns:
            all_dex_programs.extend(pattern.dex_programs)
        
        dex_counts = {}
        for dex in all_dex_programs:
            dex_counts[dex] = dex_counts.get(dex, 0) + 1
        
        print(f"\n🏪 DEX USAGE:")
        for dex, count in sorted(dex_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(sell_patterns)) * 100
            print(f"   {dex}: {count} transactions ({percentage:.1f}%)")
        
        # Transfer type analysis
        sol_transfer_counts = [p.sol_transfer_count for p in sell_patterns]
        token_transfer_counts = [p.token_transfer_count for p in sell_patterns]
        
        print(f"\n💰 TRANSFER TYPE ANALYSIS:")
        print(f"   SOL transfers per transaction: {sum(sol_transfer_counts)/len(sol_transfer_counts):.1f} avg")
        print(f"   Token transfers per transaction: {sum(token_transfer_counts)/len(token_transfer_counts):.1f} avg")
        
        # First/Last transfer analysis
        first_transfer_types = {}
        last_transfer_types = {}
        
        for pattern in sell_patterns:
            first_type = pattern.first_transfer_type
            last_type = pattern.last_transfer_type
            
            first_transfer_types[first_type] = first_transfer_types.get(first_type, 0) + 1
            last_transfer_types[last_type] = last_transfer_types.get(last_type, 0) + 1
        
        print(f"\n🎯 TRANSFER SEQUENCE:")
        print(f"   First transfer types: {first_transfer_types}")
        print(f"   Last transfer types: {last_transfer_types}")
    
    async def _generate_detection_recommendations(self, sell_patterns: List[TransactionPattern]):
        """Generate recommendations for buy/sell detection"""
        
        print(f"\n💡 DETECTION PATTERN RECOMMENDATIONS")
        print("=" * 50)
        
        if not sell_patterns:
            print("❌ No patterns to analyze")
            return
        
        # Analyze sell patterns for potential discriminators
        print(f"🎯 BASED ON {len(sell_patterns)} CONFIRMED SELL TRANSACTIONS:")
        
        # Transfer position analysis
        positions = [p.transfer_position_avg for p in sell_patterns if p.transfer_position_avg > 0]
        if positions:
            avg_position = sum(positions) / len(positions)
            min_position = min(positions)
            max_position = max(positions)
            
            print(f"\n📍 TRANSFER POSITION CHARACTERISTICS:")
            print(f"   Sell transactions have transfers at: {avg_position:.2%} average position")
            print(f"   Range: {min_position:.2%} - {max_position:.2%}")
            
            # Check for bimodal distribution
            low_group = [p for p in positions if p <= 0.65]
            high_group = [p for p in positions if p > 0.65]
            
            if len(low_group) > 0 and len(high_group) > 0:
                print(f"\n🔍 DETECTED TWO SELL PATTERNS:")
                print(f"   Pattern A (Early Transfers): {len(low_group)} sells at {sum(low_group)/len(low_group):.2%} avg")
                print(f"   Pattern B (Late Transfers): {len(high_group)} sells at {sum(high_group)/len(high_group):.2%} avg")
                
                # Suggest threshold that captures both
                suggested_threshold = max_position + 0.01
                print(f"\n💡 RECOMMENDED THRESHOLD: {suggested_threshold:.2%}")
                print(f"   This would classify transfers > {suggested_threshold:.2%} as BUY")
                print(f"   This would classify transfers ≤ {suggested_threshold:.2%} as SELL")
                print(f"   ✅ This captures ALL {len(sell_patterns)} sell patterns")
        
        # Transaction length analysis
        lengths = [p.total_logs for p in sell_patterns]
        avg_length = sum(lengths) / len(lengths)
        max_length = max(lengths)
        
        print(f"\n📏 TRANSACTION LENGTH CHARACTERISTICS:")
        print(f"   Sell transactions: {avg_length:.1f} logs average, max {max_length}")
        print(f"   💡 BUY transactions likely to be > {max_length} logs")
        
        # Instruction pattern analysis
        close_account_pct = sum(1 for p in sell_patterns if p.has_close_account) / len(sell_patterns)
        buy_exact_in_pct = sum(1 for p in sell_patterns if p.has_buy_exact_in) / len(sell_patterns)
        swap_only_pct = sum(1 for p in sell_patterns if p.has_swap_only) / len(sell_patterns)
        
        print(f"\n🔧 INSTRUCTION PATTERN CHARACTERISTICS:")
        print(f"   CloseAccount in sells: {close_account_pct:.1%}")
        print(f"   BuyExactIn in sells: {buy_exact_in_pct:.1%}")
        print(f"   Swap-only in sells: {swap_only_pct:.1%}")
        
        if close_account_pct > 0.8:
            print(f"   ⚠️ CloseAccount appears in most sells - NOT a reliable discriminator")
        
        if buy_exact_in_pct < 0.2:
            print(f"   💡 BuyExactIn rare in sells - might indicate BUY transactions")
        
        # Multi-criteria recommendation
        print(f"\n🎯 MULTI-CRITERIA DETECTION STRATEGY:")
        print(f"   PRIMARY: Transfer position threshold > {max(positions) + 0.01:.2%} = BUY")
        print(f"   SECONDARY: Transaction length > {max_length} logs = likely BUY")
        print(f"   TERTIARY: Presence of BuyExactIn instruction = likely BUY")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Provide BUY transaction signatures for comparison")
        print(f"   2. Validate proposed thresholds against BUY patterns")
        print(f"   3. Fine-tune multi-criteria detection logic")
        print(f"   4. Update WebSocket detection in test_websocket_connection.py")
        
        print(f"\n🚨 CRITICAL INSIGHT:")
        print(f"   Your sell transactions show TWO distinct patterns!")
        print(f"   This explains why our 65.63% threshold failed on new signatures")
        print(f"   Need threshold that accommodates BOTH sell patterns")

async def main():
    """Run comprehensive pattern analysis"""
    analyzer = ComprehensivePatternAnalyzer()
    await analyzer.analyze_comprehensive_patterns()

if __name__ == "__main__":
    asyncio.run(main())
