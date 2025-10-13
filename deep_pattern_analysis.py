#!/usr/bin/env python3
"""
Deep Pattern Analysis for Buy vs Sell Detection
Analyze the specific differences between confirmed buy and sell transactions
"""

import asyncio
import json
import requests
from typing import Dict, Any, List
from env_keys import EnvKeys

class DetailedPatternAnalyzer:
    """Deep analysis of transaction patterns to identify buy vs sell indicators"""
    
    def __init__(self):
        self.kz = EnvKeys()
        self.rpc_url = self.kz.HELIUS_RPC_URL
    
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
            
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            data = response.json()
            
            if "result" in data and data["result"]:
                meta = data["result"].get("meta", {})
                logs = meta.get("logMessages", [])
                return logs
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error fetching transaction: {e}")
            return []
    
    def analyze_detailed_patterns(self, logs: List[str], signature: str, action_type: str):
        """Detailed pattern analysis to find buy vs sell indicators"""
        
        print(f"\n{'='*80}")
        print(f"🔍 DEEP ANALYSIS: {action_type.upper()} Transaction")
        print(f"📝 Signature: {signature}")
        print(f"📊 Total logs: {len(logs)}")
        print(f"{'='*80}")
        
        # Show ALL logs with line numbers for pattern analysis
        print(f"\n📋 COMPLETE LOG ANALYSIS:")
        for i, log in enumerate(logs, 1):
            print(f"   [{i:2d}] {log}")
        
        # DETAILED INSTRUCTION BREAKDOWN
        print(f"\n🔧 INSTRUCTION BREAKDOWN:")
        instructions = []
        instruction_positions = []
        
        for i, log in enumerate(logs):
            if 'Program log: Instruction:' in log:
                instruction = log.split('Instruction:')[1].strip()
                instructions.append(instruction)
                instruction_positions.append(i)
                print(f"   [{i:2d}] {instruction}")
        
        print(f"\n📊 INSTRUCTION SEQUENCE: {' -> '.join(instructions)}")
        
        # ACCOUNT OPERATIONS ANALYSIS
        print(f"\n🏗️ ACCOUNT OPERATIONS:")
        account_ops = []
        account_positions = []
        
        for i, log in enumerate(logs):
            if 'InitializeAccount' in log:
                account_ops.append(f"INIT[{i}]")
                account_positions.append(('INIT', i))
                print(f"   [{i:2d}] InitializeAccount")
            elif 'CloseAccount' in log:
                account_ops.append(f"CLOSE[{i}]")
                account_positions.append(('CLOSE', i))
                print(f"   [{i:2d}] CloseAccount")
            elif 'CreateAccount' in log:
                account_ops.append(f"CREATE[{i}]")
                account_positions.append(('CREATE', i))
                print(f"   [{i:2d}] CreateAccount")
        
        print(f"   Sequence: {' -> '.join(account_ops)}")
        
        # TRANSFER ANALYSIS
        print(f"\n💰 TRANSFER ANALYSIS:")
        transfers = []
        transfer_positions = []
        
        for i, log in enumerate(logs):
            if 'TransferChecked' in log:
                transfers.append(f"TRANSFER[{i}]")
                transfer_positions.append(i)
                print(f"   [{i:2d}] TransferChecked")
            elif 'Transfer' in log and 'TransferChecked' not in log:
                transfers.append(f"TRANSFER[{i}]")
                transfer_positions.append(i)
                print(f"   [{i:2d}] Transfer")
        
        print(f"   Transfer count: {len(transfers)}")
        print(f"   Transfer sequence: {' -> '.join(transfers)}")
        
        if transfer_positions:
            avg_transfer_pos = sum(transfer_positions) / len(transfer_positions)
            relative_transfer_pos = avg_transfer_pos / len(logs)
            print(f"   Average transfer position: {avg_transfer_pos:.1f} ({relative_transfer_pos:.2%} through transaction)")
        
        # PROGRAM INVOCATION ANALYSIS
        print(f"\n🔧 PROGRAM INVOCATIONS:")
        programs = []
        for i, log in enumerate(logs):
            if ' invoke [' in log and 'Program ' in log:
                parts = log.split()
                if len(parts) >= 3 and parts[0] == 'Program':
                    program_id = parts[1]
                    depth = parts[3].strip('[]')
                    if program_id not in [
                        '11111111111111111111111111111111',
                        'ComputeBudget111111111111111111111111111111',
                        'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',
                        'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'
                    ]:
                        programs.append(f"{program_id}[depth:{depth}]")
                        print(f"   [{i:2d}] {program_id} (depth: {depth})")
        
        # TOKEN ACCOUNT OPERATIONS TIMELINE
        print(f"\n⏰ ACCOUNT OPERATIONS TIMELINE:")
        timeline = []
        for i, log in enumerate(logs):
            if any(op in log for op in ['InitializeAccount', 'CloseAccount', 'CreateAccount', 'TransferChecked', 'Transfer']):
                if 'InitializeAccount' in log:
                    timeline.append(f"[{i:2d}] INIT")
                elif 'CloseAccount' in log:
                    timeline.append(f"[{i:2d}] CLOSE")
                elif 'CreateAccount' in log:
                    timeline.append(f"[{i:2d}] CREATE")
                elif 'TransferChecked' in log:
                    timeline.append(f"[{i:2d}] XFER")
                elif 'Transfer' in log:
                    timeline.append(f"[{i:2d}] XFER")
        
        for item in timeline:
            print(f"   {item}")
        
        # POSITION-BASED ANALYSIS
        print(f"\n📍 POSITION ANALYSIS:")
        if transfer_positions:
            first_transfer = min(transfer_positions)
            last_transfer = max(transfer_positions)
            print(f"   First transfer at position: {first_transfer} ({first_transfer/len(logs):.2%})")
            print(f"   Last transfer at position: {last_transfer} ({last_transfer/len(logs):.2%})")
        
        init_positions = [pos for op, pos in account_positions if op == 'INIT']
        close_positions = [pos for op, pos in account_positions if op == 'CLOSE']
        
        if init_positions:
            avg_init = sum(init_positions) / len(init_positions)
            print(f"   Average INIT position: {avg_init:.1f} ({avg_init/len(logs):.2%})")
        
        if close_positions:
            avg_close = sum(close_positions) / len(close_positions)
            print(f"   Average CLOSE position: {avg_close:.1f} ({avg_close/len(logs):.2%})")
        
        # SEQUENCE PATTERN ANALYSIS
        print(f"\n🔍 SEQUENCE PATTERNS:")
        
        # Look for specific patterns
        has_init_before_transfers = False
        has_close_after_transfers = False
        
        if init_positions and transfer_positions:
            min_init = min(init_positions)
            min_transfer = min(transfer_positions)
            if min_init < min_transfer:
                has_init_before_transfers = True
                print(f"   ✅ InitializeAccount BEFORE first transfer")
            else:
                print(f"   ❌ InitializeAccount AFTER first transfer")
        
        if close_positions and transfer_positions:
            max_close = max(close_positions)
            max_transfer = max(transfer_positions)
            if max_close > max_transfer:
                has_close_after_transfers = True
                print(f"   ✅ CloseAccount AFTER last transfer")
            else:
                print(f"   ❌ CloseAccount BEFORE last transfer")
        
        # UNIQUE PATTERN IDENTIFICATION
        print(f"\n🎯 PATTERN SUMMARY FOR {action_type.upper()}:")
        print(f"   Instructions: {len(instructions)} total")
        print(f"   Account operations: {len(account_positions)} total")
        print(f"   Transfers: {len(transfer_positions)} total")
        print(f"   Init before transfers: {has_init_before_transfers}")
        print(f"   Close after transfers: {has_close_after_transfers}")
        
        if init_positions and close_positions:
            init_to_close_distance = min(close_positions) - max(init_positions)
            print(f"   Init-to-Close distance: {init_to_close_distance} positions")
        
        return {
            'action_type': action_type,
            'signature': signature,
            'total_logs': len(logs),
            'instructions': instructions,
            'instruction_count': len(instructions),
            'account_operations': len(account_positions),
            'transfer_count': len(transfer_positions),
            'init_positions': init_positions,
            'close_positions': close_positions,
            'transfer_positions': transfer_positions,
            'has_init_before_transfers': has_init_before_transfers,
            'has_close_after_transfers': has_close_after_transfers,
            'avg_transfer_position_ratio': sum(transfer_positions) / len(transfer_positions) / len(logs) if transfer_positions else 0,
            'programs': programs
        }
    
    async def analyze_all_transactions(self):
        """Analyze all transactions to find patterns"""
        
        print("🧪 DEEP PATTERN ANALYSIS FOR BUY VS SELL DETECTION")
        print("=" * 80)
        
        transactions = [
            # BUYS
            ('5Rze8W5ywhEdVTRVeheDxG7XAeL5SijSQvgZS2dTg9WBjQqc5sYrYcXtG58CTjhdNM728cKnLUuYF3u8c9onc2nm', 'buy'),
            ('Npud84MJwJqQZfLoG2cFuNTNhE7sbKv3jqsGoAyfyVHvdQcuUL4JcxYJn8xcvwxNp6Pts9zUhHpRTTk9pSBxhHr', 'buy'),
            # SELLS
            ('BBKetUfJZyMn9XpBqggc3B5eNnTbARxLLHDqVxDR81QFhAzTFicpR9pgReJEqjuH4XW25ZbzeUQ655HUbBH2xNV', 'sell'),
            ('2UgB8Lzz8Z9Fm2CSATFt8X3qyxXUX1KAT5LrZ5NN1y1gHoq18phRSGiLbzpcphHo2Dq5m1bn79SCzuGkABuCTkMt', 'sell'),
        ]
        
        results = []
        
        for signature, action_type in transactions:
            print(f"\n⏳ Fetching {action_type.upper()} transaction: {signature[:12]}...")
            logs = await self.fetch_transaction_logs(signature)
            
            if logs:
                result = self.analyze_detailed_patterns(logs, signature, action_type)
                results.append(result)
            else:
                print(f"❌ Could not fetch transaction: {signature[:12]}...")
        
        # COMPARATIVE ANALYSIS
        print(f"\n{'='*80}")
        print(f"🔍 COMPARATIVE PATTERN ANALYSIS")
        print(f"{'='*80}")
        
        buy_results = [r for r in results if r['action_type'] == 'buy']
        sell_results = [r for r in results if r['action_type'] == 'sell']
        
        print(f"\n📊 BUY PATTERNS:")
        for result in buy_results:
            print(f"   {result['signature'][:12]}:")
            print(f"      Instructions: {result['instruction_count']}")
            print(f"      Transfers: {result['transfer_count']}")
            print(f"      Init before transfers: {result['has_init_before_transfers']}")
            print(f"      Close after transfers: {result['has_close_after_transfers']}")
            print(f"      Avg transfer position: {result['avg_transfer_position_ratio']:.2%}")
        
        print(f"\n📊 SELL PATTERNS:")
        for result in sell_results:
            print(f"   {result['signature'][:12]}:")
            print(f"      Instructions: {result['instruction_count']}")
            print(f"      Transfers: {result['transfer_count']}")
            print(f"      Init before transfers: {result['has_init_before_transfers']}")
            print(f"      Close after transfers: {result['has_close_after_transfers']}")
            print(f"      Avg transfer position: {result['avg_transfer_position_ratio']:.2%}")
        
        # FIND DISCRIMINATING PATTERNS
        print(f"\n🎯 DISCRIMINATING PATTERNS:")
        
        if buy_results and sell_results:
            # Compare average transfer positions
            buy_avg_transfer_pos = sum(r['avg_transfer_position_ratio'] for r in buy_results) / len(buy_results)
            sell_avg_transfer_pos = sum(r['avg_transfer_position_ratio'] for r in sell_results) / len(sell_results)
            
            print(f"   Average transfer position:")
            print(f"      BUYs: {buy_avg_transfer_pos:.2%}")
            print(f"      SELLs: {sell_avg_transfer_pos:.2%}")
            
            # Check init before transfers pattern
            buy_init_before = sum(1 for r in buy_results if r['has_init_before_transfers'])
            sell_init_before = sum(1 for r in sell_results if r['has_init_before_transfers'])
            
            print(f"   Init before transfers:")
            print(f"      BUYs: {buy_init_before}/{len(buy_results)} ({buy_init_before/len(buy_results):.1%})")
            print(f"      SELLs: {sell_init_before}/{len(sell_results)} ({sell_init_before/len(sell_results):.1%})")
            
            # Check close after transfers pattern
            buy_close_after = sum(1 for r in buy_results if r['has_close_after_transfers'])
            sell_close_after = sum(1 for r in sell_results if r['has_close_after_transfers'])
            
            print(f"   Close after transfers:")
            print(f"      BUYs: {buy_close_after}/{len(buy_results)} ({buy_close_after/len(buy_results):.1%})")
            print(f"      SELLs: {sell_close_after}/{len(sell_results)} ({sell_close_after/len(sell_results):.1%})")
        
        print(f"\n🔧 RECOMMENDED DETECTION LOGIC:")
        if buy_results and sell_results:
            # Based on the analysis, suggest new detection criteria
            print(f"   Instead of using CloseAccount alone, consider:")
            print(f"   1. Transfer position: SELLs tend to have transfers later in transaction")
            print(f"   2. Operation sequence: Pattern of INIT -> TRANSFER -> CLOSE")
            print(f"   3. Multiple criteria combination rather than single indicator")
        
        return results

async def main():
    """Main analysis function"""
    analyzer = DetailedPatternAnalyzer()
    await analyzer.analyze_all_transactions()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Analysis stopped by user")
    except Exception as e:
        print(f"\n❌ Analysis error: {e}")
