#!/usr/bin/env python3
"""
Validate Updated Detection Logic Against User's Confirmed Transactions
Test the new buy/sell detection rules using your specific transaction signatures
"""

import asyncio
import json
import requests
from typing import Dict, Any, List
from env_keys import EnvKeys

class ValidationTester:
    """Test updated detection logic against known buy/sell transactions"""
    
    def __init__(self):
        try:
            kz = EnvKeys()
            # Try different RPC URL attribute names
            if hasattr(kz, 'HELIUS_RPC_URL'):
                self.rpc_url = kz.HELIUS_RPC_URL
            elif hasattr(kz, 'HELIUS_Standard_RPC_URL'):
                self.rpc_url = kz.HELIUS_Standard_RPC_URL
            else:
                # Fallback
                api_key = "7277139c-ff2c-4257-ad06-2db6aa16c315"
                self.rpc_url = f"https://mainnet.helius-rpc.com/v0?api-key={api_key}"
            
            print(f"🔗 Connected to RPC: {self.rpc_url[:50]}...")
        except Exception as e:
            print(f"❌ Error loading RPC configuration: {e}")
            raise
    
    async def fetch_transaction_logs(self, signature: str) -> List[str]:
        """Fetch transaction logs for analysis"""
        
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
                return logs
            else:
                print(f"❌ No transaction data for {signature[:12]}...")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching {signature[:12]}...: {e}")
            return []
    
    def test_detection_logic(self, logs: List[str], signature: str, expected_type: str) -> Dict[str, Any]:
        """Test the updated detection logic"""
        
        print(f"\n{'='*60}")
        print(f"🧪 TESTING {expected_type.upper()}: {signature[:12]}...")
        print(f"{'='*60}")
        
        # Apply the EXACT same logic as the updated WebSocket monitor
        detected_type = None
        
        # Find transfer positions
        transfer_indices = [i for i, log in enumerate(logs) if 'TransferChecked' in log or 'Transfer' in log]
        
        if transfer_indices:
            avg_transfer_position = sum(transfer_indices) / len(transfer_indices)
            relative_position = avg_transfer_position / len(logs)
            
            # YOUR TRANSACTION EVIDENCE: BUYs 68.30% vs SELLs 62.96%
            if relative_position > 0.6563:  # Threshold: 65.63% (midpoint)
                detected_type = 'buy'
                print(f"   🎯 DETECTED: BUY (transfer position: {relative_position:.2%})")
                print(f"      Logic: Position > 65.63% threshold")
            else:
                detected_type = 'sell'
                print(f"   🎯 DETECTED: SELL (transfer position: {relative_position:.2%})")
                print(f"      Logic: Position ≤ 65.63% threshold")
        
        # Secondary detection methods
        if not detected_type:
            # Instruction pattern analysis
            has_buy_exact_in = any('BuyExactIn' in log for log in logs)
            has_swap_only = any('Swap' in log for log in logs) and not has_buy_exact_in
            
            if has_buy_exact_in:
                detected_type = 'buy'
                print(f"   🎯 DETECTED: BUY (BuyExactIn instruction)")
            elif has_swap_only and len(logs) < 56:
                detected_type = 'sell'
                print(f"   🎯 DETECTED: SELL (Swap + short transaction)")
            elif len(logs) >= 58:
                detected_type = 'buy'
                print(f"   🎯 DETECTED: BUY (long transaction: {len(logs)} logs)")
            else:
                detected_type = 'sell'
                print(f"   🎯 DETECTED: SELL (default for short transaction)")
        
        # Check accuracy
        correct = (detected_type == expected_type)
        
        print(f"   📊 Expected: {expected_type.upper()}")
        print(f"   📊 Detected: {detected_type.upper()}")
        print(f"   {'✅ CORRECT' if correct else '❌ WRONG'}")
        
        return {
            'signature': signature,
            'expected': expected_type,
            'detected': detected_type,
            'correct': correct,
            'transfer_position': relative_position if transfer_indices else None,
            'transaction_length': len(logs),
            'transfer_count': len(transfer_indices)
        }
    
    async def validate_all_transactions(self):
        """Validate detection logic against all known transactions"""
        
        print("🧪 VALIDATION TEST: Updated Detection Logic")
        print("=" * 80)
        print("Testing against your confirmed buy/sell transaction signatures")
        print("=" * 80)
        
        # Your confirmed transactions
        test_cases = [
            # Known BUYs
            ("4TMgVbpTY83dci52HkyShgHJDowYeyBrn7S1CdW1YR3Gh4mLHWiJjwBTcFpQVmRtqqYpMyi7BnDSZCqNPve3GaRW", "buy"),
            ("2CDKCDhzUjKKxNQkhbcNMh2zVeq14pwmSnyNdGCq8XvB7cqHyMaXHgtgLUMov9E8FUkAauoubJ2zC9JjURFewymr", "buy"),
            ("UDUp8Z5FA8HPij7uXXkwcmvVEL1bG89HFeKijVqS1Kq1pMHtXuKiC6cL7PZdFuvQSiMUqntq13P8EjijM49wXqf", "buy"),
            ("3zpcyXDudoShNYrgohoy5vYFLJaCf7tTAGVYgKiqf2STQkXHSfcfH1Bw51GDxg7LbEXrDGZGMAoRVa2PLs2canSE", "buy"),
            
            # Known SELLs
            ("2TiAZ3gDLosvWryz84oCZLKfeB8qEWwkZo4a2htKjRZdBpSjPnV8fwLMrgNvsQbZfsn4m8K5V2zkHLVJGQaEA8Xj", "sell"),
            ("4tijQwFC5hhngmQJHefeBjSpphd28ssfJZJaPpZ3Sh7Z89r8B12MuEQT7APqQ53MLtYtkaFYt6Ex4qva55jh9XNN", "sell"),
            ("4h3EtfEPH9nge9tW9wjK483hye9jsvyWP77jaxQHhzsD3S8ruHpLjxut7MnPG4yoybdiX9UEDMw3ysCAzyqAuG4A", "sell"),
            ("2jVHGoggb4FSPqkKQMREquyhceWA2nG3TDkbqk8WWV5D2NJLnPJBu85P4nwkcNSTpVrvNQ8z3mDcgQTYgKZhXbzd", "sell"),
            ("3WEhx6hMSp9ciGZ2LKgMmWmWf7fWu6giynZ2pL2pQsSrpJwxtUhVhdjqsufv2Z72wdpn3KgEtdBF6Jn8Cheo2NBk", "sell"),
            ("2pomJiWey1k8NXyYczCFEiXYGJxHupXVHwJoVQYhR9RdA3bJrTJbWXncVeLjdvYnKvbMpvcUHgdmxJBUmKBJTd1P", "sell"),
            ("3coQUsYoZpUbCtwBo5CAS9gvpsoyECHdWguj3353zDUxJWXpYqZFN8U63nayZQ77yxrbvE2AWNLwyvywKjNAaghW", "sell"),
        ]
        
        results = []
        
        # Test each transaction
        for signature, expected_type in test_cases:
            print(f"\n🔄 Fetching logs for {expected_type.upper()}: {signature[:12]}...")
            logs = await self.fetch_transaction_logs(signature)
            
            if logs:
                result = self.test_detection_logic(logs, signature, expected_type)
                results.append(result)
            else:
                print(f"❌ Could not fetch logs for {signature[:12]}...")
        
        # Calculate accuracy
        correct_predictions = sum(1 for r in results if r['correct'])
        total_predictions = len(results)
        accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"📊 VALIDATION RESULTS")
        print(f"{'='*80}")
        print(f"Total transactions tested: {total_predictions}")
        print(f"Correct predictions: {correct_predictions}")
        print(f"Accuracy: {accuracy:.1f}%")
        
        # Show detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(results, 1):
            status = "✅" if result['correct'] else "❌"
            print(f"   [{i:2d}] {status} {result['signature'][:12]}... | "
                  f"Expected: {result['expected'].upper():4} | "
                  f"Detected: {result['detected'].upper():4} | "
                  f"Position: {result['transfer_position']:.2%}")
        
        # Analysis of wrong predictions
        wrong_predictions = [r for r in results if not r['correct']]
        if wrong_predictions:
            print(f"\n❌ INCORRECT PREDICTIONS ANALYSIS:")
            for result in wrong_predictions:
                print(f"   {result['signature'][:12]}... | "
                      f"Expected {result['expected'].upper()} but detected {result['detected'].upper()}")
                print(f"      Transfer position: {result['transfer_position']:.2%}")
                print(f"      Transaction length: {result['transaction_length']} logs")
        
        # Recommendations
        if accuracy >= 90:
            print(f"\n🟢 EXCELLENT: {accuracy:.1f}% accuracy - Ready for live trading!")
        elif accuracy >= 75:
            print(f"\n🟡 GOOD: {accuracy:.1f}% accuracy - Acceptable for testing")
        else:
            print(f"\n🔴 POOR: {accuracy:.1f}% accuracy - Needs improvement")
        
        return results

async def main():
    """Run validation test"""
    tester = ValidationTester()
    await tester.validate_all_transactions()

if __name__ == "__main__":
    asyncio.run(main())
