#!/usr/bin/env python3
"""
Analyze Additional Sell Signatures from BullX Neo + Solscan
Test against current 71% threshold and identify any new patterns
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from env_keys import EnvKeys

@dataclass
class SellTransactionAnalysis:
    """Analysis results for a sell transaction"""
    signature: str
    total_logs: int
    transfer_count: int
    transfer_position_avg: float
    transfer_positions: List[float]
    transaction_length_category: str
    dex_programs: List[str]
    instruction_patterns: List[str]
    sol_transfers: int
    token_transfers: int
    analysis_status: str
    threshold_result: str  # PASS/FAIL against 71% threshold

class AdditionalSellAnalyzer:
    """Analyze additional sell signatures from BullX Neo + Solscan"""
    
    def __init__(self):
        try:
            kz = EnvKeys()
            self.rpc_url = kz.HELIUS_RPC_URL
            print(f"🔗 RPC URL loaded: {kz.HELIUS_RPC_URL[:50]}...")
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            raise
    
    async def analyze_new_sell_signatures(self):
        """Analyze the 3 new sell signatures from BullX Neo + Solscan"""
        
        print("🔍 ANALYZING ADDITIONAL SELL SIGNATURES")
        print("=" * 60)
        print("📊 BullX Neo events + Solscan transaction signatures")
        print("🎯 Testing against current 71% threshold")
        print("=" * 60)
        
        # New sell signatures from user (BullX Neo + Solscan)
        new_sell_signatures = [
            "CvUZ4fUvC3mDtxv3bAXK1sdq8CYMGAHcykN16rtbg41CeNBy8ULpDDTN1CmLUe4EuMJnCmEUWzbLh5eg1vgDyn5",
            "6VqmoBzPG5zTxibiNwUkHqVhmb4g67yYp67MMdEQNn6VYqh1EnwCbb1V8tNwD3Be2vicKrBbfXAcVBZRdGQCdib", 
            "4cw4EBtn2nosbg5FrU6B1Uo9nESCdqTcDET9tnBQ5TDiYDYVhaHGES6DxTUdXpwtLfqcAjjMRjY92sSjS1czu1Xi"
        ]
        
        print(f"📊 NEW SELL SIGNATURES: {len(new_sell_signatures)}")
        print(f"🎯 Will test against current 71% threshold")
        print(f"📈 Current knowledge: 18 confirmed sells, 100% accuracy")
        
        # Analyze each new signature
        analyses = []
        for i, signature in enumerate(new_sell_signatures):
            print(f"\n📊 [{i+1}/{len(new_sell_signatures)}] Analyzing: {signature[:12]}...")
            try:
                analysis = await self._analyze_single_sell_transaction(signature)
                if analysis:
                    analyses.append(analysis)
                    print(f"   ✅ Analysis complete")
                else:
                    print(f"   ❌ Analysis failed")
            except Exception as e:
                print(f"   ❌ Error analyzing {signature[:12]}: {e}")
        
        print(f"\n📈 SUCCESSFULLY ANALYZED: {len(analyses)} sell transactions")
        
        # Compare against current patterns and threshold
        await self._validate_against_current_threshold(analyses)
        
        # Update pattern knowledge
        await self._update_pattern_knowledge(analyses)
    
    async def _analyze_single_sell_transaction(self, signature: str) -> SellTransactionAnalysis:
        """Analyze a single sell transaction comprehensively"""
        
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
                
                # Extract comprehensive analysis
                analysis = self._extract_sell_analysis(signature, logs, tx_data)
                return analysis
    
    def _extract_sell_analysis(self, signature: str, logs: List[str], tx_data: Dict) -> SellTransactionAnalysis:
        """Extract comprehensive analysis from sell transaction"""
        
        total_logs = len(logs)
        
        # Transfer analysis
        transfer_indices = []
        sol_transfers = 0
        token_transfers = 0
        
        for i, log in enumerate(logs):
            if 'TransferChecked' in log or 'Transfer' in log:
                transfer_indices.append(i)
                
                if 'So11111111111111111111111111111111111111112' in log:
                    sol_transfers += 1
                else:
                    token_transfers += 1
        
        # Transfer position analysis
        if transfer_indices:
            transfer_positions = [idx / total_logs for idx in transfer_indices]
            transfer_position_avg = sum(transfer_positions) / len(transfer_positions)
        else:
            transfer_positions = []
            transfer_position_avg = 0.0
        
        # DEX program analysis
        dex_program_ids = {
            'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB': 'Jupiter V4',
            'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4': 'Jupiter V6',
            '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium AMM V4',
            '27haf8L6oxUeXrHrgEgsexjSY5hbVUWEmvv9Nyxg8vQv': 'Raydium CPMM',
            '9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM': 'Raydium CLMM',
            '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun',
            'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc': 'Orca Whirlpool',
        }
        
        detected_dex_programs = []
        for log in logs:
            if ' invoke [' in log and 'Program ' in log:
                parts = log.split()
                if len(parts) >= 3 and parts[0] == 'Program':
                    program_id = parts[1]
                    if program_id in dex_program_ids:
                        dex_name = dex_program_ids[program_id]
                        if dex_name not in detected_dex_programs:
                            detected_dex_programs.append(dex_name)
        
        # Instruction pattern analysis
        instruction_patterns = []
        for log in logs:
            if 'CloseAccount' in log:
                instruction_patterns.append('CloseAccount')
            if 'BuyExactIn' in log:
                instruction_patterns.append('BuyExactIn')
            if 'Swap' in log and 'BuyExactIn' not in log:
                instruction_patterns.append('Swap')
            if 'Program log: Instruction:' in log:
                instruction = log.split('Instruction:')[1].strip()
                instruction_patterns.append(f"Instruction:{instruction}")
        
        instruction_patterns = list(set(instruction_patterns))  # Remove duplicates
        
        # Transaction length categorization
        if total_logs < 50:
            length_category = 'short'
        elif total_logs < 60:
            length_category = 'medium'
        else:
            length_category = 'long'
        
        # Test against 71% threshold
        current_threshold = 0.71
        if transfer_position_avg <= current_threshold:
            threshold_result = "PASS"  # Correctly identified as SELL
        else:
            threshold_result = "FAIL"  # Would be misclassified as BUY
        
        return SellTransactionAnalysis(
            signature=signature,
            total_logs=total_logs,
            transfer_count=len(transfer_indices),
            transfer_position_avg=transfer_position_avg,
            transfer_positions=transfer_positions,
            transaction_length_category=length_category,
            dex_programs=detected_dex_programs,
            instruction_patterns=instruction_patterns,
            sol_transfers=sol_transfers,
            token_transfers=token_transfers,
            analysis_status="SUCCESS",
            threshold_result=threshold_result
        )
    
    async def _validate_against_current_threshold(self, analyses: List[SellTransactionAnalysis]):
        """Validate new sells against current 71% threshold"""
        
        print(f"\n🎯 THRESHOLD VALIDATION (71.00%)")
        print("=" * 40)
        
        passes = 0
        fails = 0
        threshold_issues = []
        
        for analysis in analyses:
            position_pct = analysis.transfer_position_avg * 100
            
            print(f"\n📊 {analysis.signature[:12]}:")
            print(f"   📍 Transfer position: {position_pct:.2f}%")
            print(f"   📏 Transaction length: {analysis.total_logs} logs ({analysis.transaction_length_category})")
            print(f"   🔄 Transfer count: {analysis.transfer_count}")
            print(f"   🏪 DEX: {', '.join(analysis.dex_programs) if analysis.dex_programs else 'Unknown'}")
            print(f"   🔧 Instructions: {', '.join(analysis.instruction_patterns[:3])}...")
            
            if analysis.threshold_result == "PASS":
                print(f"   ✅ THRESHOLD TEST: PASS (≤ 71.00%)")
                passes += 1
            else:
                print(f"   ❌ THRESHOLD TEST: FAIL (> 71.00%) - Would be classified as BUY!")
                fails += 1
                threshold_issues.append({
                    'signature': analysis.signature[:12],
                    'position': position_pct,
                    'logs': analysis.total_logs
                })
        
        # Summary
        total = len(analyses)
        accuracy = (passes / total) * 100 if total > 0 else 0
        
        print(f"\n📈 VALIDATION SUMMARY:")
        print(f"   🔴 Total new sells: {total}")
        print(f"   ✅ Correctly detected: {passes}/{total}")
        print(f"   ❌ Misclassified: {fails}/{total}")
        print(f"   📊 Accuracy: {accuracy:.1f}%")
        
        if fails > 0:
            print(f"\n⚠️ THRESHOLD ISSUES DETECTED:")
            max_position = max(issue['position'] for issue in threshold_issues)
            print(f"   📍 Highest sell position: {max_position:.2f}%")
            print(f"   💡 Suggested new threshold: {max_position + 1:.0f}%")
            
            print(f"\n🔧 PROBLEMATIC TRANSACTIONS:")
            for issue in threshold_issues:
                print(f"      {issue['signature']}: {issue['position']:.2f}% position, {issue['logs']} logs")
        else:
            print(f"\n🎉 PERFECT! All new sells correctly detected by 71% threshold")
    
    async def _update_pattern_knowledge(self, analyses: List[SellTransactionAnalysis]):
        """Update our pattern knowledge with new data"""
        
        print(f"\n📊 PATTERN KNOWLEDGE UPDATE")
        print("=" * 40)
        
        if not analyses:
            print("❌ No analyses to process")
            return
        
        # Current pattern knowledge
        previous_sells = 18
        new_sells = len(analyses)
        total_sells = previous_sells + new_sells
        
        print(f"📈 SELL TRANSACTION DATABASE:")
        print(f"   🔴 Previous confirmed sells: {previous_sells}")
        print(f"   🔴 New confirmed sells: {new_sells}")
        print(f"   🔴 Total confirmed sells: {total_sells}")
        
        # Analyze new patterns
        positions = [a.transfer_position_avg * 100 for a in analyses]
        lengths = [a.total_logs for a in analyses]
        
        if positions:
            print(f"\n📍 NEW SELL PATTERNS:")
            print(f"   Transfer positions: {min(positions):.2f}% - {max(positions):.2f}%")
            print(f"   Average position: {sum(positions)/len(positions):.2f}%")
            print(f"   Transaction lengths: {min(lengths)} - {max(lengths)} logs")
            print(f"   Average length: {sum(lengths)/len(lengths):.1f} logs")
        
        # Check if new patterns fit existing categories
        pattern_a_range = (62.0, 66.0)  # Early transfer pattern
        pattern_b_range = (68.0, 72.0)  # Late transfer pattern
        
        pattern_a_count = sum(1 for pos in positions if pattern_a_range[0] <= pos <= pattern_a_range[1])
        pattern_b_count = sum(1 for pos in positions if pattern_b_range[0] <= pos <= pattern_b_range[1])
        pattern_c_count = new_sells - pattern_a_count - pattern_b_count
        
        print(f"\n🔍 PATTERN CLASSIFICATION:")
        print(f"   📊 Pattern A (Early, 62-66%): {pattern_a_count} new sells")
        print(f"   📊 Pattern B (Late, 68-72%): {pattern_b_count} new sells")
        print(f"   📊 Pattern C (New range): {pattern_c_count} new sells")
        
        if pattern_c_count > 0:
            outlier_positions = [pos for pos in positions if not (pattern_a_range[0] <= pos <= pattern_a_range[1] or pattern_b_range[0] <= pos <= pattern_b_range[1])]
            print(f"   ⚠️ New pattern positions: {outlier_positions}")
        
        # Generate recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if all(a.threshold_result == "PASS" for a in analyses):
            print(f"   ✅ 71% threshold works perfectly for all new sells")
            print(f"   🎯 No threshold adjustment needed")
            print(f"   🚀 WebSocket detection ready for production")
        else:
            failed_positions = [a.transfer_position_avg * 100 for a in analyses if a.threshold_result == "FAIL"]
            max_failed_position = max(failed_positions)
            suggested_threshold = max_failed_position + 1
            print(f"   🔄 Threshold adjustment needed: {suggested_threshold:.0f}%")
            print(f"   📊 Update WebSocket detection logic")
            print(f"   🧪 Test against all {total_sells} confirmed sells")

async def main():
    """Run additional sell signature analysis"""
    analyzer = AdditionalSellAnalyzer()
    await analyzer.analyze_new_sell_signatures()

if __name__ == "__main__":
    asyncio.run(main())
