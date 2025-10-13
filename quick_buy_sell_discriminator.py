#!/usr/bin/env python3
"""
CRITICAL PATTERN DISCOVERY: Find Real Buy/Sell Discriminators
Based on analysis of confirmed buy transactions - the transfer position approach failed!
Need to find the REAL distinguishing factors between buys and sells.
"""

import asyncio
import json
import aiohttp
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from env_keys import EnvKeys

@dataclass
class QuickPatternAnalysis:
    signature: str
    transaction_type: str
    total_logs: int
    has_buy_exact_in: bool
    has_close_account: bool
    transfer_position_percent: float
    programs_count: int

class QuickDiscriminatorFinder:
    """Quick analysis to find real buy/sell patterns"""
    
    def __init__(self):
        self.kz = EnvKeys()
        self.rpc_url = self.kz.HELIUS_RPC_URL
    
    async def find_patterns(self):
        """Find the real patterns that distinguish buys from sells"""
        
        print("🔍 QUICK PATTERN DISCOVERY: Buy vs Sell Analysis")
        print("=" * 70)
        print("❌ Transfer position failed (buys overlap with sells)")
        print("🎯 Finding alternative discriminating factors")
        print("=" * 70)
        
        # Confirmed sell signatures
        sell_signatures = [
            "WARi9zjewz6eQxPajSpr8kGEDLw52foAweghWZ8yx5KgJmuUAUY3Mc7NLnFyGiVTHXc22qKimxUWXZ4BAuB27Rs",
            "CvUZ4fUvC3mDtxv3bAXK1sdq8CYMGAHcykN16rtbg41CeNBy8ULpDDTN1CmLUe4EuMJnCmEUWzbLh5eg1vgDyn5",
            "6VqmoBzPG5zTxibiNwUkHqVhmb4g67yYp67MMdEQNn6VYqh1EnwCbb1V8tNwD3Be2vicKrBbfXAcVBZRdGQCdib"
        ]
        
        # Confirmed buy signatures
        buy_signatures = [
            "5szMCyNB1JUhQuApXYWhBQNUedstoH1vp3u5fRBGJt12Mk4GPro8M5VnqwixaX6yhxSo9E5wcwRrdn5fM32TfQzs",
            "2Zn9QbiXrMmnoRTSA4qB1okwHniFfaufncqhf7HGRtzyDYPxTkieaorVnWuTSy7cbT5tac5xjBzRaPiJxYuusDRP",
            "3mQR5kKSzEZXJaSW8AmFgfcbtxY2om59KixYyRAAAnjSaE2LTbEzq3aF9dHdPpACT92fjdmL4y2o49n2xRGju3mm"
        ]
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            print(f"📉 Analyzing {len(sell_signatures)} confirmed SELL transactions:")
            for i, sig in enumerate(sell_signatures, 1):
                print(f"   Sell #{i}: {sig[:12]}...")
                analysis = await self._quick_analyze(session, sig, 'sell')
                if analysis:
                    results.append(analysis)
            
            print(f"\n📈 Analyzing {len(buy_signatures)} confirmed BUY transactions:")
            for i, sig in enumerate(buy_signatures, 1):
                print(f"   Buy #{i}: {sig[:12]}...")
                analysis = await self._quick_analyze(session, sig, 'buy')
                if analysis:
                    results.append(analysis)
        
        # Analyze patterns
        await self._analyze_discriminating_patterns(results)
    
    async def _quick_analyze(self, session: aiohttp.ClientSession, signature: str, tx_type: str) -> Optional[QuickPatternAnalysis]:
        """Quick analysis of transaction patterns"""
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {"encoding": "json", "commitment": "confirmed", "maxSupportedTransactionVersion": 0}
            ]
        }
        
        try:
            async with session.post(self.rpc_url, json=payload) as response:
                data = await response.json()
                
                if 'error' in data:
                    print(f"❌ Error for {signature[:12]}: {data['error']}")
                    return None
                
                result = data.get('result')
                if not result:
                    return None
                
                logs = result.get('meta', {}).get('logMessages', [])
                if not logs:
                    return None
                
                # Quick pattern analysis
                total_logs = len(logs)
                has_buy_exact_in = any('BuyExactIn' in log for log in logs)
                has_close_account = any('CloseAccount' in log for log in logs)
                
                # Transfer position
                transfer_indices = [i for i, log in enumerate(logs) if 'TransferChecked' in log or 'Transfer' in log]
                if transfer_indices:
                    avg_pos = sum(transfer_indices) / len(transfer_indices)
                    transfer_position_percent = (avg_pos / total_logs) * 100
                else:
                    transfer_position_percent = 0.0
                
                # Program count
                programs = set()
                for log in logs:
                    if ' invoke [' in log and 'Program ' in log:
                        parts = log.split()
                        if len(parts) >= 3 and parts[0] == 'Program':
                            programs.add(parts[1])
                
                return QuickPatternAnalysis(
                    signature=signature,
                    transaction_type=tx_type,
                    total_logs=total_logs,
                    has_buy_exact_in=has_buy_exact_in,
                    has_close_account=has_close_account,
                    transfer_position_percent=transfer_position_percent,
                    programs_count=len(programs)
                )
                
        except Exception as e:
            print(f"❌ Error analyzing {signature[:12]}: {e}")
            return None
    
    async def _analyze_discriminating_patterns(self, results: List[QuickPatternAnalysis]):
        """Find discriminating patterns between buys and sells"""
        
        buys = [r for r in results if r.transaction_type == 'buy']
        sells = [r for r in results if r.transaction_type == 'sell']
        
        print(f"\n🎯 PATTERN ANALYSIS RESULTS")
        print("=" * 60)
        print(f"📊 Dataset: {len(buys)} buys, {len(sells)} sells")
        
        if not buys or not sells:
            print("❌ Insufficient data for pattern analysis")
            return
        
        # 1. BuyExactIn Analysis
        buys_with_buyexactin = sum(1 for b in buys if b.has_buy_exact_in)
        sells_with_buyexactin = sum(1 for s in sells if s.has_buy_exact_in)
        
        print(f"\n🔧 BUYEXACTIN INSTRUCTION ANALYSIS:")
        print(f"   Buys with BuyExactIn: {buys_with_buyexactin}/{len(buys)} ({buys_with_buyexactin/len(buys)*100:.0f}%)")
        print(f"   Sells with BuyExactIn: {sells_with_buyexactin}/{len(sells)} ({sells_with_buyexactin/len(sells)*100:.0f}%)")
        
        # 2. CloseAccount Analysis
        buys_with_close = sum(1 for b in buys if b.has_close_account)
        sells_with_close = sum(1 for s in sells if s.has_close_account)
        
        print(f"\n🔒 CLOSEACCOUNT INSTRUCTION ANALYSIS:")
        print(f"   Buys with CloseAccount: {buys_with_close}/{len(buys)} ({buys_with_close/len(buys)*100:.0f}%)")
        print(f"   Sells with CloseAccount: {sells_with_close}/{len(sells)} ({sells_with_close/len(sells)*100:.0f}%)")
        
        # 3. Combined Analysis - THE KEY INSIGHT
        print(f"\n💡 COMBINED PATTERN ANALYSIS:")
        
        # Check for exclusive patterns
        buys_buyexactin_only = [b for b in buys if b.has_buy_exact_in and not b.has_close_account]
        buys_closeaccount_only = [b for b in buys if not b.has_buy_exact_in and b.has_close_account]
        buys_both = [b for b in buys if b.has_buy_exact_in and b.has_close_account]
        buys_neither = [b for b in buys if not b.has_buy_exact_in and not b.has_close_account]
        
        sells_buyexactin_only = [s for s in sells if s.has_buy_exact_in and not s.has_close_account]
        sells_closeaccount_only = [s for s in sells if not s.has_buy_exact_in and s.has_close_account]
        sells_both = [s for s in sells if s.has_buy_exact_in and s.has_close_account]
        sells_neither = [s for s in sells if not s.has_buy_exact_in and not s.has_close_account]
        
        print(f"   BUY PATTERNS:")
        print(f"     BuyExactIn only: {len(buys_buyexactin_only)}")
        print(f"     CloseAccount only: {len(buys_closeaccount_only)}")
        print(f"     Both instructions: {len(buys_both)}")
        print(f"     Neither instruction: {len(buys_neither)}")
        
        print(f"   SELL PATTERNS:")
        print(f"     BuyExactIn only: {len(sells_buyexactin_only)}")
        print(f"     CloseAccount only: {len(sells_closeaccount_only)}")
        print(f"     Both instructions: {len(sells_both)}")
        print(f"     Neither instruction: {len(sells_neither)}")
        
        # 4. Detailed breakdown
        print(f"\n📊 DETAILED TRANSACTION BREAKDOWN:")
        print(f"{'Type':<4} {'Signature':<12} {'Logs':<5} {'BuyExactIn':<10} {'CloseAcc':<9} {'Position':<8}")
        print("-" * 65)
        
        for result in results:
            print(f"{result.transaction_type.upper():<4} {result.signature[:12]:<12} {result.total_logs:<5} {str(result.has_buy_exact_in):<10} {str(result.has_close_account):<9} {result.transfer_position_percent:<7.1f}%")
        
        # 5. Proposed NEW detection logic
        print(f"\n🎯 PROPOSED NEW DETECTION LOGIC:")
        print("=" * 50)
        
        # Test different rules
        if buys_with_buyexactin > 0 and sells_with_buyexactin == 0:
            print("✅ RULE 1: BuyExactIn instruction → BUY")
            print("✅ RULE 2: No BuyExactIn → Analyze further")
            
            # For transactions without BuyExactIn, what distinguishes them?
            buys_no_buyexactin = [b for b in buys if not b.has_buy_exact_in]
            sells_no_buyexactin = [s for s in sells if not s.has_buy_exact_in]
            
            if buys_no_buyexactin and sells_no_buyexactin:
                # CloseAccount analysis for non-BuyExactIn transactions
                buys_no_buyexactin_with_close = sum(1 for b in buys_no_buyexactin if b.has_close_account)
                sells_no_buyexactin_with_close = sum(1 for s in sells_no_buyexactin if s.has_close_account)
                
                print(f"   For non-BuyExactIn transactions:")
                print(f"     Buys with CloseAccount: {buys_no_buyexactin_with_close}/{len(buys_no_buyexactin)}")
                print(f"     Sells with CloseAccount: {sells_no_buyexactin_with_close}/{len(sells_no_buyexactin)}")
                
                if sells_no_buyexactin_with_close > buys_no_buyexactin_with_close:
                    print("✅ RULE 3: No BuyExactIn + CloseAccount → SELL")
                    print("✅ RULE 4: No BuyExactIn + No CloseAccount → BUY")
        
        # Test the proposed logic
        correct_predictions = 0
        total_predictions = len(results)
        
        print(f"\n🧪 TESTING PROPOSED LOGIC:")
        for result in results:
            predicted_type = None
            
            if result.has_buy_exact_in:
                predicted_type = 'buy'
                rule_used = "BuyExactIn → BUY"
            elif result.has_close_account:
                predicted_type = 'sell'
                rule_used = "CloseAccount → SELL"
            else:
                predicted_type = 'buy'
                rule_used = "Neither → BUY"
            
            is_correct = predicted_type == result.transaction_type
            if is_correct:
                correct_predictions += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"   {status} {result.signature[:12]} → {predicted_type.upper()} ({rule_used}) | Actual: {result.transaction_type.upper()}")
        
        accuracy = (correct_predictions / total_predictions) * 100
        print(f"\n🎯 ACCURACY: {correct_predictions}/{total_predictions} ({accuracy:.1f}%)")
        
        if accuracy == 100:
            print("🚀 PERFECT DETECTION RULES FOUND!")
            print("💡 New WebSocket detection logic:")
            print("   1. Has 'BuyExactIn' instruction → BUY")
            print("   2. Has 'CloseAccount' (no BuyExactIn) → SELL")
            print("   3. Neither instruction → BUY (default)")
        elif accuracy >= 80:
            print("✅ Good detection rules - minor refinement needed")
        else:
            print("❌ Detection rules need more work")

async def main():
    finder = QuickDiscriminatorFinder()
    await finder.find_patterns()

if __name__ == "__main__":
    asyncio.run(main())
