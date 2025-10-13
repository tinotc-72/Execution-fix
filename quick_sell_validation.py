#!/usr/bin/env python3
"""
Quick Validation: Test New Sell Signatures Against Current Detection Logic
Validate that new sell signatures match our 65.63% threshold pattern
"""

import asyncio
import json
import requests
from typing import Dict, Any, List
from env_keys import EnvKeys

class QuickSellValidator:
    """Quick validator for new sell signatures"""
    
    def __init__(self):
        try:
            kz = EnvKeys()
            if hasattr(kz, 'HELIUS_RPC_URL'):
                self.rpc_url = kz.HELIUS_RPC_URL
            else:
                api_key = "7277139c-ff2c-4257-ad06-2db6aa16c315"
                self.rpc_url = f"https://mainnet.helius-rpc.com/v0?api-key={api_key}"
            
            print(f"🔗 Connected to RPC: {self.rpc_url[:50]}...")
        except Exception as e:
            print(f"❌ Error loading RPC configuration: {e}")
            raise
    
    async def fetch_and_test_signature(self, signature: str) -> Dict[str, Any]:
        """Fetch transaction and test with current detection logic"""
        
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
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            data = response.json()
            
            if "result" in data and data["result"]:
                meta = data["result"].get("meta", {})
                logs = meta.get("logMessages", [])
                
                if logs:
                    return self.test_current_logic(logs, signature)
                else:
                    print(f"❌ No logs for {signature[:12]}...")
                    return {"signature": signature, "status": "no_logs"}
            else:
                print(f"❌ No data for {signature[:12]}...")
                return {"signature": signature, "status": "no_data"}
                
        except Exception as e:
            print(f"❌ Error fetching {signature[:12]}...: {e}")
            return {"signature": signature, "status": "error", "error": str(e)}
    
    def test_current_logic(self, logs: List[str], signature: str) -> Dict[str, Any]:
        """Test the current 65.63% threshold detection logic"""
        
        print(f"\n🧪 TESTING: {signature[:12]}...")
        
        # Find transfer positions (EXACT same logic as WebSocket)
        transfer_indices = [i for i, log in enumerate(logs) if 'TransferChecked' in log or 'Transfer' in log]
        
        if transfer_indices:
            avg_transfer_position = sum(transfer_indices) / len(transfer_indices)
            relative_position = avg_transfer_position / len(logs)
            
            # Apply current threshold: 65.63%
            if relative_position > 0.6563:
                predicted = 'buy'
                correct = False  # We expect sells
                print(f"   🎯 DETECTED: BUY (position: {relative_position:.2%}) ❌ WRONG - Expected SELL")
            else:
                predicted = 'sell'
                correct = True   # We expect sells
                print(f"   ✅ DETECTED: SELL (position: {relative_position:.2%}) ✅ CORRECT")
            
            return {
                "signature": signature,
                "expected": "sell",
                "predicted": predicted,
                "correct": correct,
                "transfer_position": relative_position,
                "transaction_length": len(logs),
                "transfer_count": len(transfer_indices),
                "status": "analyzed"
            }
        else:
            print(f"   ❌ No transfers found")
            return {"signature": signature, "status": "no_transfers"}
    
    async def validate_new_sells(self):
        """Validate all new sell signatures"""
        
        print("🧪 QUICK VALIDATION: New Sell Signatures")
        print("=" * 60)
        print("Testing new sell signatures against current 65.63% threshold")
        print("=" * 60)
        
        # New sell signatures from user
        new_sell_signatures = [
            "5aUojub2bBvY4vGpvmtYvVKnuYetEaWwGi3csU1hYcMo9FVGF1ofjpFmGHZHToYTDtn8oyhtYzRctP5uuv8QUahB",
            "4SyXk5tS7EpSVvRDFQ7DL4KP7z8HgeS52jFZ75m6ymowfDPsAJQEacLtQWjBKwaYANxBgyVyxSKHsqJYrLv7jpco",
            "267rkRQkV6QHsvRFEcyVKnTjoRBH9wdEX1wBNY1FLRnxim87pYF3SvYnUyweHqDm8EXfMNxxn2Yax2dangLhzXQJ",
            "5dtbtTcMJ3a63JKdzd5U5SdgBGVyFQyZfZaahn2KwJhaRgx5A6PqVqAC8FH5WW3HkWm5MPd4VGGsdhaJ7GZJGYoL",
            "4cL7ZzRjgx374y4ZCy2vWQdXhmG9tstW1JPi3DiLmWBZj3sNjdaYHNRxvReV1EcEpC6CEMf8XSsvEcrdRdK6rSwE",
            "32yrmAJRpH7EruUA3ZYXCm19v4P3jDVG8JNHzrUxgeZqYZMNoF5mQpEGRPLrTgB7cDCMhb1T6hLxAkAYzdHoF4Jr",
            "ktgC7ndhpLP6TsJjSCbJAgKsZSoiSD1CY3n4JLRe27n96MUHY8c7hTTdoGrq8Dqap5CMiGC1hr7eHJ3Q3C2iBKo",
            "4LhTxwUxM2uWz5oACJ49T6a3ZA2eugW5AB5Lsbz6GmDn7LJiQJYkbxxuhzhSwrYtzMUvXQZ4dM7aU2c88GbaVCVy",
            "3oPcnjo5L2PsbUWbKo7ten991yaz24U3QjmhcZso8vfUGYUfRm5NyQiGR4FcXBWSYPxmZLS6fsDxDzRGBvQcrCXr",
            "4N66GktemYm9ihtnVjqzz2CAGmt1buuZz2CAGmt1buuZz4sn7x9MEpBALYSzpge3eLGhPs3TZVAHz1hDbhGXZNcADeFTBuhCiX8U",
            "5M9ZNBQjJbpGL3gpodmnBrSEiZkKMbgQBm2AudAdR2GjSH9ftHi7d9BFwyGehXUoBF8dMyXnPYZur4svumjVqYUE"
        ]
        
        print(f"🔍 Testing {len(new_sell_signatures)} new sell signatures...")
        
        results = []
        
        # Test each signature
        for i, signature in enumerate(new_sell_signatures, 1):
            print(f"\n📋 [{i}/{len(new_sell_signatures)}] Processing: {signature[:12]}...")
            result = await self.fetch_and_test_signature(signature)
            results.append(result)
        
        # Calculate results
        analyzed_results = [r for r in results if r.get("status") == "analyzed"]
        correct_predictions = sum(1 for r in analyzed_results if r.get("correct", False))
        total_analyzed = len(analyzed_results)
        
        print(f"\n{'='*60}")
        print(f"📊 VALIDATION RESULTS")
        print(f"{'='*60}")
        print(f"Total new signatures: {len(new_sell_signatures)}")
        print(f"Successfully analyzed: {total_analyzed}")
        print(f"Correct predictions: {correct_predictions}")
        
        if total_analyzed > 0:
            accuracy = (correct_predictions / total_analyzed) * 100
            print(f"Current threshold accuracy: {accuracy:.1f}%")
            
            # Show detailed results
            print(f"\n📋 DETAILED RESULTS:")
            for i, result in enumerate(analyzed_results, 1):
                status = "✅" if result.get('correct', False) else "❌"
                pos = result.get('transfer_position', 0)
                print(f"   [{i:2d}] {status} {result['signature'][:12]}... | "
                      f"Position: {pos:.2%} | "
                      f"Predicted: {result.get('predicted', 'N/A').upper()}")
            
            # Analysis of wrong predictions
            wrong_predictions = [r for r in analyzed_results if not r.get('correct', False)]
            if wrong_predictions:
                print(f"\n❌ INCORRECT PREDICTIONS ({len(wrong_predictions)} signatures):")
                
                # Calculate average position of wrong predictions
                wrong_positions = [r['transfer_position'] for r in wrong_predictions]
                avg_wrong_position = sum(wrong_positions) / len(wrong_positions)
                
                print(f"   Average transfer position of wrong predictions: {avg_wrong_position:.2%}")
                print(f"   Current threshold: 65.63%")
                
                for result in wrong_predictions:
                    print(f"      {result['signature'][:12]}... | "
                          f"Position: {result['transfer_position']:.2%} | "
                          f"Length: {result['transaction_length']} logs")
                
                # Suggest threshold adjustment
                all_positions = [r['transfer_position'] for r in analyzed_results]
                max_sell_position = max(all_positions)
                
                print(f"\n💡 THRESHOLD ANALYSIS:")
                print(f"   Highest sell position: {max_sell_position:.2%}")
                print(f"   Current threshold: 65.63%")
                
                if max_sell_position > 0.6563:
                    new_threshold = max_sell_position + 0.01  # 1% buffer
                    print(f"   🔧 SUGGESTED NEW THRESHOLD: {new_threshold:.2%}")
                    print(f"      This would catch all current sells")
                else:
                    print(f"   ✅ Current threshold is appropriate")
            
            # Recommendations
            if accuracy >= 95:
                print(f"\n🟢 EXCELLENT: {accuracy:.1f}% accuracy - Current threshold works great!")
            elif accuracy >= 85:
                print(f"\n🟡 GOOD: {accuracy:.1f}% accuracy - Consider minor threshold adjustment")
            else:
                print(f"\n🔴 NEEDS IMPROVEMENT: {accuracy:.1f}% accuracy - Threshold needs adjustment")
        
        return results

async def main():
    """Run quick validation"""
    validator = QuickSellValidator()
    await validator.validate_new_sells()

if __name__ == "__main__":
    asyncio.run(main())
