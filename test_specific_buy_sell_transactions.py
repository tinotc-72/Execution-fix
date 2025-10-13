#!/usr/bin/env python3
"""
Test Buy/Sell Detection with Specific Transactions
Testing our corrected logic against known buy and sell transactions
"""

import asyncio
import json
import requests
from typing import Dict, Any, List
from env_keys import EnvKeys

class TransactionAnalyzer:
    """Analyze specific transactions to test buy/sell detection"""
    
    def __init__(self):
        self.kz = EnvKeys()
        self.rpc_url = self.kz.HELIUS_RPC_URL
        
    def analyze_transaction_logs(self, logs: List[str], signature: str, expected_action: str) -> Dict[str, Any]:
        """
        ENHANCED Buy/Sell Detection Logic (Same as WebSocket)
        Based on Solana transaction patterns and instruction analysis
        """
        
        print(f"\n🔍 ANALYZING TRANSACTION: {signature}")
        print(f"🎯 Expected Action: {expected_action.upper()}")
        print(f"📊 Total logs: {len(logs)}")
        
        # Show key log lines for pattern recognition
        print(f"\n📋 KEY LOG PATTERNS:")
        for i, log in enumerate(logs[:15]):  # Show first 15 logs
            print(f"   [{i+1:2d}] {log}")
        if len(logs) > 15:
            print(f"   ... and {len(logs)-15} more lines")
        
        # STEP 1: Look for specific Solana instructions that indicate buy/sell
        has_close_account = any('CloseAccount' in log for log in logs)
        has_init_account = any('InitializeAccount' in log for log in logs)
        has_swap = any('Swap' in log for log in logs)
        
        # Count transfers
        token_transfers = [log for log in logs if 'TransferChecked' in log or 'Transfer' in log]
        sol_transfers = [log for log in logs if 'So11111111111111111111111111111111111111112' in log]
        
        print(f"\n🔧 INSTRUCTION ANALYSIS:")
        print(f"   CloseAccount found: {has_close_account}")
        print(f"   InitializeAccount found: {has_init_account}")
        print(f"   Swap instruction found: {has_swap}")
        print(f"   Token transfers: {len(token_transfers)}")
        print(f"   SOL transfers: {len(sol_transfers)}")
        
        # ENHANCED DETECTION LOGIC
        detected_action = None
        confidence = 0
        reasoning = []
        
        # METHOD 1: CloseAccount Pattern (Strong Sell Indicator)
        if has_close_account:
            detected_action = 'sell'
            confidence = 90
            reasoning.append("CloseAccount instruction indicates token account closure (sell pattern)")
        
        # METHOD 2: InitializeAccount + Multiple Transfers (Strong Buy Indicator)
        elif has_init_account and len(token_transfers) >= 2:
            detected_action = 'buy'
            confidence = 85
            reasoning.append(f"InitializeAccount + {len(token_transfers)} transfers indicates new token acquisition (buy pattern)")
        
        # METHOD 3: Account Operation Sequence Analysis
        if not detected_action:
            # Analyze the sequence of account operations
            account_operations = []
            operation_positions = []
            
            for i, log in enumerate(logs):
                if 'InitializeAccount' in log:
                    account_operations.append('INIT')
                    operation_positions.append(i)
                elif 'CloseAccount' in log:
                    account_operations.append('CLOSE')
                    operation_positions.append(i)
                elif 'TransferChecked' in log:
                    account_operations.append('TRANSFER')
                    operation_positions.append(i)
            
            print(f"   📊 Operation sequence: {' -> '.join(account_operations[-8:])}")  # Last 8 operations
            
            # Pattern-based detection
            if 'CLOSE' in account_operations:
                detected_action = 'sell'
                confidence = 75
                reasoning.append("Account closure pattern detected in operation sequence")
            elif 'INIT' in account_operations and operation_positions:
                # Check if INIT operations are early in the transaction
                init_positions = [pos for i, pos in enumerate(operation_positions) if account_operations[i] == 'INIT']
                if init_positions:
                    avg_init_position = sum(init_positions) / len(init_positions)
                    relative_position = avg_init_position / len(logs)
                    
                    if relative_position < 0.5:  # INIT operations in first half
                        detected_action = 'buy'
                        confidence = 70
                        reasoning.append(f"InitializeAccount operations early in transaction (position: {relative_position:.2f})")
        
        # METHOD 4: Transfer Position Analysis (Fallback)
        if not detected_action and token_transfers:
            transfer_indices = [i for i, log in enumerate(logs) if 'TransferChecked' in log]
            if transfer_indices:
                avg_transfer_position = sum(transfer_indices) / len(transfer_indices)
                relative_position = avg_transfer_position / len(logs)
                
                if relative_position > 0.7:  # Transfers in last 30% of transaction
                    detected_action = 'sell'
                    confidence = 60
                    reasoning.append(f"Token transfers near end of transaction (position: {relative_position:.2f})")
                else:
                    detected_action = 'buy'
                    confidence = 60
                    reasoning.append(f"Token transfers earlier in transaction (position: {relative_position:.2f})")
        
        # METHOD 5: Generic swap detection (lowest confidence)
        if not detected_action and has_swap:
            detected_action = 'swap'
            confidence = 40
            reasoning.append("Generic swap instruction detected")
        
        # Final fallback
        if not detected_action:
            detected_action = 'unknown'
            confidence = 0
            reasoning.append("No clear buy/sell pattern detected")
        
        # RESULTS
        is_correct = detected_action.lower() == expected_action.lower()
        
        print(f"\n✅ DETECTION RESULTS:")
        print(f"   🎯 Detected Action: {detected_action.upper()}")
        print(f"   📊 Confidence: {confidence}%")
        print(f"   🎪 Expected: {expected_action.upper()}")
        print(f"   ✅ Correct: {'YES' if is_correct else 'NO'}")
        
        print(f"\n🧠 REASONING:")
        for i, reason in enumerate(reasoning, 1):
            print(f"   {i}. {reason}")
        
        return {
            'signature': signature,
            'detected_action': detected_action,
            'expected_action': expected_action,
            'confidence': confidence,
            'is_correct': is_correct,
            'reasoning': reasoning,
            'has_close_account': has_close_account,
            'has_init_account': has_init_account,
            'has_swap': has_swap,
            'token_transfers': len(token_transfers),
            'sol_transfers': len(sol_transfers),
            'total_logs': len(logs)
        }
    
    async def fetch_transaction_logs(self, signature: str) -> List[str]:
        """Fetch transaction logs from Helius RPC"""
        try:
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
            
            print(f"📡 Fetching transaction: {signature[:12]}...")
            
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            data = response.json()
            
            if "result" in data and data["result"]:
                meta = data["result"].get("meta", {})
                logs = meta.get("logMessages", [])
                print(f"✅ Retrieved {len(logs)} log lines")
                return logs
            else:
                print(f"❌ No transaction data found: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching transaction: {e}")
            return []
    
    async def test_buy_sell_detection(self):
        """Test our buy/sell detection with known transactions"""
        
        print("🧪 TESTING BUY/SELL DETECTION WITH SPECIFIC TRANSACTIONS")
        print("=" * 70)
        
        # Known transactions with expected actions
        test_transactions = [
            # BUYS
            {
                'signature': '5Rze8W5ywhEdVTRVeheDxG7XAeL5SijSQvgZS2dTg9WBjQqc5sYrYcXtG58CTjhdNM728cKnLUuYF3u8c9onc2nm',
                'expected': 'buy',
                'description': 'Known BUY transaction #1'
            },
            {
                'signature': 'Npud84MJwJqQZfLoG2cFuNTNhE7sbKv3jqsGoAyfyVHvdQcuUL4JcxYJn8xcvwxNp6Pts9zUhHpRTTk9pSBxhHr',
                'expected': 'buy',
                'description': 'Known BUY transaction #2'
            },
            # SELLS
            {
                'signature': 'BBKetUfJZyMn9XpBqggc3B5eNnTbARxLLHDqVxDR81QFhAzTFicpR9pgReJEqjuH4XW25ZbzeUQ655HUbBH2xNV',
                'expected': 'sell',
                'description': 'Known SELL transaction #1'
            },
            {
                'signature': '2UgB8Lzz8Z9Fm2CSATFt8X3qyxXUX1KAT5LrZ5NN1y1gHoq18phRSGiLbzpcphHo2Dq5m1bn79SCzuGkABuCTkMt',
                'expected': 'sell',
                'description': 'Known SELL transaction #2'
            }
        ]
        
        results = []
        correct_detections = 0
        
        for i, tx in enumerate(test_transactions, 1):
            print(f"\n🔬 TEST {i}/4: {tx['description']}")
            print("=" * 50)
            
            # Fetch transaction logs
            logs = await self.fetch_transaction_logs(tx['signature'])
            
            if logs:
                # Analyze with our detection logic
                result = self.analyze_transaction_logs(logs, tx['signature'], tx['expected'])
                results.append(result)
                
                if result['is_correct']:
                    correct_detections += 1
                    print(f"✅ CORRECT DETECTION!")
                else:
                    print(f"❌ INCORRECT DETECTION!")
            else:
                print(f"⚠️ Could not fetch transaction data")
                results.append({
                    'signature': tx['signature'],
                    'detected_action': 'error',
                    'expected_action': tx['expected'],
                    'is_correct': False,
                    'error': 'Could not fetch transaction'
                })
            
            print("\n" + "─" * 50)
        
        # SUMMARY
        print(f"\n🎯 FINAL RESULTS SUMMARY")
        print("=" * 50)
        print(f"📊 Total Tests: {len(test_transactions)}")
        print(f"✅ Correct Detections: {correct_detections}")
        print(f"❌ Incorrect Detections: {len(test_transactions) - correct_detections}")
        print(f"📈 Accuracy: {(correct_detections/len(test_transactions)*100):.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in results:
            if 'error' not in result:
                status = "✅" if result['is_correct'] else "❌"
                conf = result.get('confidence', 0)
                print(f"   {status} {result['signature'][:12]}... | Expected: {result['expected_action'].upper()} | Detected: {result['detected_action'].upper()} | Confidence: {conf}%")
            else:
                print(f"   ⚠️ {result['signature'][:12]}... | ERROR: {result['error']}")
        
        # PATTERN ANALYSIS
        if results:
            print(f"\n🔍 PATTERN ANALYSIS:")
            close_account_results = [r for r in results if r.get('has_close_account')]
            init_account_results = [r for r in results if r.get('has_init_account')]
            
            print(f"   🔒 Transactions with CloseAccount: {len(close_account_results)}")
            for r in close_account_results:
                print(f"      - {r['signature'][:12]}... (Expected: {r['expected_action']}, Detected: {r['detected_action']})")
            
            print(f"   🏗️ Transactions with InitializeAccount: {len(init_account_results)}")
            for r in init_account_results:
                print(f"      - {r['signature'][:12]}... (Expected: {r['expected_action']}, Detected: {r['detected_action']})")
        
        if correct_detections == len(test_transactions):
            print(f"\n🎉 PERFECT SCORE! All transactions correctly detected!")
            print(f"✅ Our buy/sell detection logic is working correctly!")
        elif correct_detections >= len(test_transactions) * 0.75:
            print(f"\n👍 GOOD PERFORMANCE! Most transactions correctly detected.")
            print(f"🔧 Minor adjustments may be needed for edge cases.")
        else:
            print(f"\n⚠️ NEEDS IMPROVEMENT! Detection logic requires refinement.")
            print(f"🛠️ Review patterns and adjust detection criteria.")
        
        return results

async def main():
    """Main test function"""
    analyzer = TransactionAnalyzer()
    await analyzer.test_buy_sell_detection()

if __name__ == "__main__":
    print("🧪 BUY/SELL DETECTION TEST")
    print("Testing with specific known transactions")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
