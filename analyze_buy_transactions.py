#!/usr/bin/env python3
"""
BUY TRANSACTION PATTERN ANALYZER
Comprehensive analysis of confirmed buy transactions to validate detection logic
"""

import asyncio
import json
import aiohttp
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from env_keys import EnvKeys

@dataclass
class BuyTransactionAnalysis:
    signature: str
    total_logs: int
    transfer_count: int
    transfer_indices: List[int]
    transfer_position_percent: float
    has_buy_exact_in: bool
    has_swap_instruction: bool
    programs_invoked: List[str]
    analysis_notes: str

class BuyTransactionAnalyzer:
    """Analyze confirmed buy transactions to understand patterns"""
    
    def __init__(self):
        self.kz = EnvKeys()
        self.rpc_url = self.kz.HELIUS_RPC_URL
        self.buy_analyses: List[BuyTransactionAnalysis] = []
    
    async def analyze_buy_signatures(self, buy_signatures: List[str]):
        """Analyze multiple buy transaction signatures"""
        print(f"🔍 ANALYZING {len(buy_signatures)} CONFIRMED BUY TRANSACTIONS")
        print("=" * 80)
        
        async with aiohttp.ClientSession() as session:
            for i, signature in enumerate(buy_signatures, 1):
                print(f"\n📊 ANALYZING BUY #{i}: {signature}")
                print("-" * 50)
                
                try:
                    analysis = await self._analyze_single_buy(session, signature)
                    if analysis:
                        self.buy_analyses.append(analysis)
                        print(f"✅ Analysis complete for buy #{i}")
                    else:
                        print(f"❌ Failed to analyze buy #{i}")
                        
                except Exception as e:
                    print(f"❌ Error analyzing buy #{i}: {e}")
        
        # Generate comprehensive pattern analysis
        await self._generate_buy_pattern_report()
        await self._compare_with_sell_patterns()
        await self._validate_threshold_against_buys()
    
    async def _analyze_single_buy(self, session: aiohttp.ClientSession, signature: str) -> Optional[BuyTransactionAnalysis]:
        """Analyze a single buy transaction"""
        
        # Fetch transaction data
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
        
        try:
            async with session.post(self.rpc_url, json=payload) as response:
                data = await response.json()
                
                if 'error' in data:
                    print(f"❌ RPC Error: {data['error']}")
                    return None
                
                result = data.get('result')
                if not result:
                    print(f"❌ No transaction data found")
                    return None
                
                # Extract transaction metadata
                meta = result.get('meta', {})
                transaction = result.get('transaction', {})
                
                # Get logs
                logs = meta.get('logMessages', [])
                if not logs:
                    print(f"❌ No logs found in transaction")
                    return None
                
                print(f"📋 Transaction Details:")
                print(f"   Total logs: {len(logs)}")
                print(f"   Status: {'SUCCESS' if meta.get('err') is None else 'FAILED'}")
                
                # Analyze transfer patterns
                transfer_indices = []
                for i, log in enumerate(logs):
                    if 'TransferChecked' in log or 'Transfer' in log:
                        transfer_indices.append(i)
                
                print(f"   Transfers: {len(transfer_indices)} found at positions {transfer_indices}")
                
                # Calculate transfer position percentage
                if transfer_indices:
                    avg_transfer_position = sum(transfer_indices) / len(transfer_indices)
                    transfer_position_percent = (avg_transfer_position / len(logs)) * 100
                else:
                    transfer_position_percent = 0.0
                
                print(f"   Transfer Position: {transfer_position_percent:.2f}%")
                
                # Analyze instruction patterns
                has_buy_exact_in = any('BuyExactIn' in log for log in logs)
                has_swap_instruction = any('Swap' in log for log in logs)
                
                print(f"   Instructions: BuyExactIn={has_buy_exact_in}, Swap={has_swap_instruction}")
                
                # Extract program invocations
                programs_invoked = []
                for log in logs:
                    if ' invoke [' in log and 'Program ' in log:
                        parts = log.split()
                        if len(parts) >= 3 and parts[0] == 'Program':
                            program_id = parts[1]
                            if program_id not in programs_invoked:
                                programs_invoked.append(program_id)
                
                print(f"   Programs: {len(programs_invoked)} unique programs invoked")
                
                # Generate analysis notes
                notes = []
                if transfer_position_percent > 71:
                    notes.append(f"ABOVE 71% threshold ({transfer_position_percent:.2f}%)")
                else:
                    notes.append(f"BELOW 71% threshold ({transfer_position_percent:.2f}%) - THRESHOLD ISSUE!")
                
                if has_buy_exact_in:
                    notes.append("Has BuyExactIn instruction")
                if has_swap_instruction:
                    notes.append("Has Swap instruction")
                if len(logs) > 55:
                    notes.append("Long transaction (>55 logs)")
                
                analysis_notes = "; ".join(notes)
                
                # Create analysis object
                analysis = BuyTransactionAnalysis(
                    signature=signature,
                    total_logs=len(logs),
                    transfer_count=len(transfer_indices),
                    transfer_indices=transfer_indices,
                    transfer_position_percent=transfer_position_percent,
                    has_buy_exact_in=has_buy_exact_in,
                    has_swap_instruction=has_swap_instruction,
                    programs_invoked=programs_invoked,
                    analysis_notes=analysis_notes
                )
                
                print(f"   Analysis: {analysis_notes}")
                
                return analysis
                
        except Exception as e:
            print(f"❌ Error fetching transaction {signature}: {e}")
            return None
    
    async def _generate_buy_pattern_report(self):
        """Generate comprehensive buy pattern analysis"""
        if not self.buy_analyses:
            print("\n❌ No buy analyses available for pattern report")
            return
        
        print(f"\n🎯 BUY TRANSACTION PATTERN ANALYSIS")
        print("=" * 80)
        print(f"📊 SAMPLE SIZE: {len(self.buy_analyses)} confirmed buy transactions")
        
        # Transfer position analysis
        transfer_positions = [analysis.transfer_position_percent for analysis in self.buy_analyses]
        min_position = min(transfer_positions)
        max_position = max(transfer_positions)
        avg_position = sum(transfer_positions) / len(transfer_positions)
        
        print(f"\n🎯 TRANSFER POSITION ANALYSIS:")
        print(f"   Range: {min_position:.2f}% - {max_position:.2f}%")
        print(f"   Average: {avg_position:.2f}%")
        print(f"   Above 71% threshold: {sum(1 for pos in transfer_positions if pos > 71)}/{len(transfer_positions)}")
        print(f"   Below 71% threshold: {sum(1 for pos in transfer_positions if pos <= 71)}/{len(transfer_positions)}")
        
        # Transaction length analysis
        log_counts = [analysis.total_logs for analysis in self.buy_analyses]
        min_logs = min(log_counts)
        max_logs = max(log_counts)
        avg_logs = sum(log_counts) / len(log_counts)
        
        print(f"\n📋 TRANSACTION LENGTH ANALYSIS:")
        print(f"   Range: {min_logs} - {max_logs} logs")
        print(f"   Average: {avg_logs:.1f} logs")
        print(f"   Above 55 logs: {sum(1 for count in log_counts if count > 55)}/{len(log_counts)}")
        print(f"   Below 55 logs: {sum(1 for count in log_counts if count <= 55)}/{len(log_counts)}")
        
        # Instruction pattern analysis
        buy_exact_in_count = sum(1 for analysis in self.buy_analyses if analysis.has_buy_exact_in)
        swap_only_count = sum(1 for analysis in self.buy_analyses if analysis.has_swap_instruction and not analysis.has_buy_exact_in)
        
        print(f"\n🔧 INSTRUCTION PATTERN ANALYSIS:")
        print(f"   BuyExactIn instruction: {buy_exact_in_count}/{len(self.buy_analyses)} ({buy_exact_in_count/len(self.buy_analyses)*100:.1f}%)")
        print(f"   Swap only (no BuyExactIn): {swap_only_count}/{len(self.buy_analyses)} ({swap_only_count/len(self.buy_analyses)*100:.1f}%)")
        
        # Individual transaction details
        print(f"\n📊 INDIVIDUAL BUY TRANSACTION BREAKDOWN:")
        print(f"{'#':<3} {'Signature':<12} {'Logs':<5} {'Transfers':<9} {'Position':<9} {'Instructions':<20} {'Notes'}")
        print("-" * 100)
        
        for i, analysis in enumerate(self.buy_analyses, 1):
            instructions = []
            if analysis.has_buy_exact_in:
                instructions.append("BuyExactIn")
            if analysis.has_swap_instruction:
                instructions.append("Swap")
            instruction_str = "+".join(instructions) if instructions else "None"
            
            print(f"{i:<3} {analysis.signature[:12]:<12} {analysis.total_logs:<5} {analysis.transfer_count:<9} {analysis.transfer_position_percent:<8.2f}% {instruction_str:<20} {analysis.analysis_notes}")
    
    async def _compare_with_sell_patterns(self):
        """Compare buy patterns with known sell patterns"""
        print(f"\n🔄 COMPARISON WITH SELL PATTERNS")
        print("=" * 80)
        
        # Known sell patterns from our previous analysis
        print(f"📉 KNOWN SELL PATTERNS (from 21 confirmed sells):")
        print(f"   Pattern A: 62.96% transfer position (13 sells)")
        print(f"   Pattern B: 70.00% transfer position (8 sells)")
        print(f"   Range: 62.96% - 70.00%")
        print(f"   Transaction length: 48-54 logs typically")
        
        if not self.buy_analyses:
            print(f"❌ No buy data to compare")
            return
        
        # Buy patterns
        buy_positions = [analysis.transfer_position_percent for analysis in self.buy_analyses]
        min_buy_pos = min(buy_positions)
        max_buy_pos = max(buy_positions)
        avg_buy_pos = sum(buy_positions) / len(buy_positions)
        
        print(f"\n📈 BUY PATTERNS (from {len(self.buy_analyses)} confirmed buys):")
        print(f"   Range: {min_buy_pos:.2f}% - {max_buy_pos:.2f}%")
        print(f"   Average: {avg_buy_pos:.2f}%")
        
        # Gap analysis
        if min_buy_pos > 70.00:
            gap_size = min_buy_pos - 70.00
            print(f"\n✅ CLEAR SEPARATION FOUND:")
            print(f"   Sell range: 62.96% - 70.00%")
            print(f"   Buy range: {min_buy_pos:.2f}% - {max_buy_pos:.2f}%")
            print(f"   Gap: {gap_size:.2f}% between highest sell and lowest buy")
            print(f"   Current 71% threshold: {'PERFECT' if min_buy_pos > 71 else 'NEEDS ADJUSTMENT'}")
        else:
            overlap = 70.00 - min_buy_pos
            print(f"\n⚠️ OVERLAP DETECTED:")
            print(f"   Some buys ({min_buy_pos:.2f}%) overlap with sell range (up to 70.00%)")
            print(f"   Overlap: {overlap:.2f}%")
            print(f"   71% threshold may need adjustment")
    
    async def _validate_threshold_against_buys(self):
        """Test current 71% threshold against buy transactions"""
        if not self.buy_analyses:
            print(f"\n❌ No buy data for threshold validation")
            return
        
        print(f"\n🎯 THRESHOLD VALIDATION AGAINST BUY TRANSACTIONS")
        print("=" * 80)
        
        # Test 71% threshold
        correct_buy_predictions = 0
        incorrect_buy_predictions = 0
        
        for analysis in self.buy_analyses:
            if analysis.transfer_position_percent > 71:
                # Correctly identified as buy
                correct_buy_predictions += 1
                prediction_status = "✅ CORRECT"
            else:
                # Incorrectly would be classified as sell
                incorrect_buy_predictions += 1
                prediction_status = "❌ INCORRECT (would classify as SELL)"
            
            print(f"Buy {analysis.signature[:12]}: {analysis.transfer_position_percent:.2f}% -> {prediction_status}")
        
        # Calculate accuracy
        total_buys = len(self.buy_analyses)
        buy_accuracy = (correct_buy_predictions / total_buys) * 100
        
        print(f"\n📊 BUY DETECTION ACCURACY WITH 71% THRESHOLD:")
        print(f"   Correct: {correct_buy_predictions}/{total_buys} ({buy_accuracy:.1f}%)")
        print(f"   Incorrect: {incorrect_buy_predictions}/{total_buys} ({100-buy_accuracy:.1f}%)")
        
        if buy_accuracy == 100:
            print(f"✅ PERFECT BUY DETECTION: 71% threshold works perfectly for buys!")
        elif buy_accuracy >= 90:
            print(f"✅ EXCELLENT BUY DETECTION: 71% threshold works well for buys")
        else:
            print(f"⚠️ THRESHOLD ADJUSTMENT NEEDED: Consider optimizing threshold")
            
            # Suggest better threshold
            if incorrect_buy_predictions > 0:
                buy_positions = [a.transfer_position_percent for a in self.buy_analyses]
                min_buy_position = min(buy_positions)
                suggested_threshold = min_buy_position - 0.01  # Just below lowest buy
                print(f"💡 SUGGESTED THRESHOLD: {suggested_threshold:.2f}% (just below lowest buy at {min_buy_position:.2f}%)")
        
        # Overall system accuracy (combining with known sell accuracy)
        print(f"\n🎯 OVERALL SYSTEM PERFORMANCE:")
        print(f"   Sell accuracy (21 confirmed): 100% (with 71% threshold)")
        print(f"   Buy accuracy ({total_buys} confirmed): {buy_accuracy:.1f}% (with 71% threshold)")
        
        if buy_accuracy == 100:
            print(f"✅ PERFECT TRADING SYSTEM: 100% accuracy for both buys and sells!")
            print(f"🚀 Ready for production deployment!")
        else:
            print(f"⚠️ System needs threshold optimization for perfect accuracy")

async def main():
    """Main analysis function - ready for buy transaction signatures"""
    print("🎯 BUY TRANSACTION PATTERN ANALYZER")
    print("=" * 80)
    print("Ready to analyze confirmed buy transaction signatures")
    print("This will help validate and optimize the buy/sell detection system")
    print("=" * 80)
    
    # Real buy transaction signatures provided by user
    confirmed_buy_signatures = [
        "5szMCyNB1JUhQuApXYWhBQNUedstoH1vp3u5fRBGJt12Mk4GPro8M5VnqwixaX6yhxSo9E5wcwRrdn5fM32TfQzs",
        "2Zn9QbiXrMmnoRTSA4qB1okwHniFfaufncqhf7HGRtzyDYPxTkieaorVnWuTSy7cbT5tac5xjBzRaPiJxYuusDRP",
        "3mQR5kKSzEZXJaSW8AmFgfcbtxY2om59KixYyRAAAnjSaE2LTbEzq3aF9dHdPpACT92fjdmL4y2o49n2xRGju3mm",
        "4DvgM9MxpmtehVzJevHVQJWyujyHGXBvXBFQuLZZDeE6aHqkqNs5g5SfdSkA1xYjek7uYnmE7NZjUZErEbkWQgQK",
        "3s5dU94ZD93EitPKc12Yf6nLVu97B9JVmL3UDNwZpoeFgnkuFXzPZ8ZZ8warHgL9pSK59NX2jy2fxZGHyWTze7wY",
        "5odppdYh2iuCQipUfFbH98bbMHQi1LDCwGCydiA1oDztN5hiAwxzSbW4PZT25L8cS8CfVqYc7nvXwrUmccnhcfQW",
        "5V5jGYcTK1BXr1wGxUwjehhD62dL9rRnztwwxCJ75t1VvEKCRtQGRcVJqPAoxE5kEKAm4781GGwo4zYKeThbR72F",
        "5HZeUYpBb2212kmWuSmzRtkABpBXa5Ytmx8Wigb4AmQc214ygSvN7W1f34zGFHjuCp3pSrgK95L7yoGyDkSFcGPu"
    ]
    
    analyzer = BuyTransactionAnalyzer()
    await analyzer.analyze_buy_signatures(confirmed_buy_signatures)

if __name__ == "__main__":
    asyncio.run(main())
