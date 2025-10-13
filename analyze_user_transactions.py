#!/usr/bin/env python3
"""
Analyze User-Provided Buy/Sell Transactions
Compare patterns between confirmed buy and sell signatures to find reliable detection rules
"""

import asyncio
import json
import requests
from typing import Dict, Any, List, Tuple
from env_keys import EnvKeys

class UserTransactionAnalyzer:
    """Analyze user-provided transaction signatures to find buy/sell patterns"""
    
    def __init__(self):
        try:
            kz = EnvKeys()
            # Try different RPC URL attribute names
            if hasattr(kz, 'HELIUS_RPC_URL'):
                self.rpc_url = kz.HELIUS_RPC_URL
            elif hasattr(kz, 'HELIUS_Standard_RPC_URL'):
                self.rpc_url = kz.HELIUS_Standard_RPC_URL
            elif hasattr(kz, 'rpc_url'):
                self.rpc_url = kz.rpc_url
            else:
                # Fallback - construct from available attributes
                api_key = "7277139c-ff2c-4257-ad06-2db6aa16c315"  # From the logs
                self.rpc_url = f"https://mainnet.helius-rpc.com/v0?api-key={api_key}"
            
            print(f"🔗 Connected to RPC: {self.rpc_url[:50]}...")
        except Exception as e:
            print(f"❌ Error loading RPC configuration: {e}")
            raise
    
    async def fetch_transaction_details(self, signature: str) -> Dict[str, Any]:
        """Fetch complete transaction details including logs"""
        
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
                return data["result"]
            else:
                print(f"❌ No transaction data for {signature[:12]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching {signature[:12]}...: {e}")
            return None
    
    def analyze_transaction_patterns(self, tx_data: Dict[str, Any], signature: str, expected_type: str) -> Dict[str, Any]:
        """Deep analysis of transaction patterns"""
        
        print(f"\n{'='*80}")
        print(f"🔍 ANALYZING {expected_type.upper()} TRANSACTION: {signature}")
        print(f"{'='*80}")
        
        meta = tx_data.get("meta", {})
        logs = meta.get("logMessages", [])
        
        if not logs:
            print("❌ No logs found in transaction")
            return None
        
        print(f"📊 Transaction has {len(logs)} log lines")
        
        # INSTRUCTION ANALYSIS
        instructions = []
        instruction_positions = []
        
        for i, log in enumerate(logs):
            if 'Program log: Instruction:' in log:
                instruction = log.split('Instruction:')[1].strip()
                instructions.append(instruction)
                instruction_positions.append(i)
                print(f"   [{i:3d}] INSTRUCTION: {instruction}")
        
        # ACCOUNT OPERATION ANALYSIS
        account_operations = []
        operation_positions = []
        
        for i, log in enumerate(logs):
            if 'InitializeAccount' in log:
                account_operations.append(('INIT', i))
                operation_positions.append(i)
                print(f"   [{i:3d}] INIT_ACCOUNT")
            elif 'CloseAccount' in log:
                account_operations.append(('CLOSE', i))
                operation_positions.append(i)
                print(f"   [{i:3d}] CLOSE_ACCOUNT")
            elif 'CreateAccount' in log:
                account_operations.append(('CREATE', i))
                operation_positions.append(i)
                print(f"   [{i:3d}] CREATE_ACCOUNT")
        
        # TRANSFER ANALYSIS
        transfers = []
        transfer_positions = []
        
        for i, log in enumerate(logs):
            if 'TransferChecked' in log:
                transfers.append(('TRANSFER_CHECKED', i))
                transfer_positions.append(i)
                print(f"   [{i:3d}] TRANSFER_CHECKED")
            elif 'Transfer' in log and 'TransferChecked' not in log:
                transfers.append(('TRANSFER', i))
                transfer_positions.append(i)
                print(f"   [{i:3d}] TRANSFER")
        
        # PROGRAM INVOCATION ANALYSIS
        programs = []
        for log in logs:
            if ' invoke [' in log and 'Program ' in log:
                parts = log.split()
                if len(parts) >= 3 and parts[0] == 'Program':
                    program_id = parts[1]
                    if program_id not in [
                        '11111111111111111111111111111111',  # System
                        'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token
                        'ComputeBudget111111111111111111111111111111',  # Compute
                        'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token
                    ]:
                        programs.append(program_id)
        
        # POSITION ANALYSIS
        transfer_position_analysis = {}
        if transfer_positions:
            first_transfer = min(transfer_positions)
            last_transfer = max(transfer_positions)
            avg_transfer_position = sum(transfer_positions) / len(transfer_positions)
            
            transfer_position_analysis = {
                'first_transfer_position': first_transfer,
                'last_transfer_position': last_transfer,
                'avg_transfer_position': avg_transfer_position,
                'relative_first_position': first_transfer / len(logs),
                'relative_last_position': last_transfer / len(logs),
                'relative_avg_position': avg_transfer_position / len(logs),
                'transfer_spread': last_transfer - first_transfer,
                'transfers_in_first_half': sum(1 for pos in transfer_positions if pos < len(logs)/2),
                'transfers_in_last_half': sum(1 for pos in transfer_positions if pos >= len(logs)/2)
            }
        
        # SEQUENCE PATTERN ANALYSIS
        sequence_patterns = {
            'has_init_before_transfers': False,
            'has_close_after_transfers': False,
            'init_to_first_transfer_distance': None,
            'last_transfer_to_close_distance': None
        }
        
        if account_operations and transfer_positions:
            init_positions = [pos for op, pos in account_operations if op == 'INIT']
            close_positions = [pos for op, pos in account_operations if op == 'CLOSE']
            
            if init_positions and transfer_positions:
                min_init = min(init_positions)
                min_transfer = min(transfer_positions)
                if min_init < min_transfer:
                    sequence_patterns['has_init_before_transfers'] = True
                    sequence_patterns['init_to_first_transfer_distance'] = min_transfer - min_init
            
            if close_positions and transfer_positions:
                max_close = max(close_positions)
                max_transfer = max(transfer_positions)
                if max_close > max_transfer:
                    sequence_patterns['has_close_after_transfers'] = True
                    sequence_patterns['last_transfer_to_close_distance'] = max_close - max_transfer
        
        # COMPILE RESULTS
        analysis_result = {
            'signature': signature,
            'expected_type': expected_type,
            'total_logs': len(logs),
            'instructions': instructions,
            'instruction_count': len(instructions),
            'instruction_positions': instruction_positions,
            'account_operations': account_operations,
            'operation_count': len(account_operations),
            'transfers': transfers,
            'transfer_count': len(transfers),
            'transfer_positions': transfer_positions,
            'transfer_position_analysis': transfer_position_analysis,
            'sequence_patterns': sequence_patterns,
            'programs_invoked': programs,
            'program_count': len(set(programs))
        }
        
        # SUMMARY OUTPUT
        print(f"\n📋 TRANSACTION SUMMARY:")
        print(f"   Type: {expected_type.upper()}")
        print(f"   Total logs: {len(logs)}")
        print(f"   Instructions: {len(instructions)}")
        print(f"   Account operations: {len(account_operations)}")
        print(f"   Transfers: {len(transfers)}")
        print(f"   Unique programs: {len(set(programs))}")
        
        if transfer_position_analysis:
            print(f"   Transfer timing:")
            print(f"      First: {transfer_position_analysis['relative_first_position']:.2%}")
            print(f"      Average: {transfer_position_analysis['relative_avg_position']:.2%}")
            print(f"      Last: {transfer_position_analysis['relative_last_position']:.2%}")
        
        return analysis_result
    
    async def compare_buy_sell_patterns(self, buy_signatures: List[str], sell_signatures: List[str]):
        """Compare patterns between buy and sell transactions"""
        
        print(f"🧪 COMPARATIVE BUY/SELL PATTERN ANALYSIS")
        print(f"=" * 80)
        print(f"📈 Buy signatures to analyze: {len(buy_signatures)}")
        print(f"📉 Sell signatures to analyze: {len(sell_signatures)}")
        print(f"=" * 80)
        
        # Analyze all buy transactions
        buy_analyses = []
        for signature in buy_signatures:
            print(f"\n🔄 Fetching BUY transaction: {signature[:12]}...")
            tx_data = await self.fetch_transaction_details(signature)
            if tx_data:
                analysis = self.analyze_transaction_patterns(tx_data, signature, 'buy')
                if analysis:
                    buy_analyses.append(analysis)
        
        # Analyze all sell transactions
        sell_analyses = []
        for signature in sell_signatures:
            print(f"\n🔄 Fetching SELL transaction: {signature[:12]}...")
            tx_data = await self.fetch_transaction_details(signature)
            if tx_data:
                analysis = self.analyze_transaction_patterns(tx_data, signature, 'sell')
                if analysis:
                    sell_analyses.append(analysis)
        
        # COMPARATIVE ANALYSIS
        self.generate_comparative_report(buy_analyses, sell_analyses)
        
        return buy_analyses, sell_analyses
    
    def generate_comparative_report(self, buy_analyses: List[Dict], sell_analyses: List[Dict]):
        """Generate detailed comparative analysis report"""
        
        print(f"\n{'='*80}")
        print(f"📊 COMPARATIVE PATTERN ANALYSIS REPORT")
        print(f"{'='*80}")
        
        if not buy_analyses or not sell_analyses:
            print("❌ Insufficient data for comparison")
            return
        
        print(f"\n📈 BUY TRANSACTION PATTERNS ({len(buy_analyses)} transactions):")
        
        # Buy pattern analysis
        buy_avg_logs = sum(a['total_logs'] for a in buy_analyses) / len(buy_analyses)
        buy_avg_instructions = sum(a['instruction_count'] for a in buy_analyses) / len(buy_analyses)
        buy_avg_transfers = sum(a['transfer_count'] for a in buy_analyses) / len(buy_analyses)
        
        buy_transfer_positions = []
        for analysis in buy_analyses:
            if analysis['transfer_position_analysis']:
                buy_transfer_positions.append(analysis['transfer_position_analysis']['relative_avg_position'])
        
        buy_avg_transfer_pos = sum(buy_transfer_positions) / len(buy_transfer_positions) if buy_transfer_positions else 0
        
        print(f"   Average logs: {buy_avg_logs:.1f}")
        print(f"   Average instructions: {buy_avg_instructions:.1f}")
        print(f"   Average transfers: {buy_avg_transfers:.1f}")
        print(f"   Average transfer position: {buy_avg_transfer_pos:.2%}")
        
        # Common patterns in buys
        buy_has_init_before = sum(1 for a in buy_analyses if a['sequence_patterns']['has_init_before_transfers'])
        buy_has_close_after = sum(1 for a in buy_analyses if a['sequence_patterns']['has_close_after_transfers'])
        
        print(f"   Init before transfers: {buy_has_init_before}/{len(buy_analyses)} ({buy_has_init_before/len(buy_analyses):.1%})")
        print(f"   Close after transfers: {buy_has_close_after}/{len(buy_analyses)} ({buy_has_close_after/len(buy_analyses):.1%})")
        
        print(f"\n📉 SELL TRANSACTION PATTERNS ({len(sell_analyses)} transactions):")
        
        # Sell pattern analysis
        sell_avg_logs = sum(a['total_logs'] for a in sell_analyses) / len(sell_analyses)
        sell_avg_instructions = sum(a['instruction_count'] for a in sell_analyses) / len(sell_analyses)
        sell_avg_transfers = sum(a['transfer_count'] for a in sell_analyses) / len(sell_analyses)
        
        sell_transfer_positions = []
        for analysis in sell_analyses:
            if analysis['transfer_position_analysis']:
                sell_transfer_positions.append(analysis['transfer_position_analysis']['relative_avg_position'])
        
        sell_avg_transfer_pos = sum(sell_transfer_positions) / len(sell_transfer_positions) if sell_transfer_positions else 0
        
        print(f"   Average logs: {sell_avg_logs:.1f}")
        print(f"   Average instructions: {sell_avg_instructions:.1f}")
        print(f"   Average transfers: {sell_avg_transfers:.1f}")
        print(f"   Average transfer position: {sell_avg_transfer_pos:.2%}")
        
        # Common patterns in sells
        sell_has_init_before = sum(1 for a in sell_analyses if a['sequence_patterns']['has_init_before_transfers'])
        sell_has_close_after = sum(1 for a in sell_analyses if a['sequence_patterns']['has_close_after_transfers'])
        
        print(f"   Init before transfers: {sell_has_init_before}/{len(sell_analyses)} ({sell_has_init_before/len(sell_analyses):.1%})")
        print(f"   Close after transfers: {sell_has_close_after}/{len(sell_analyses)} ({sell_has_close_after/len(sell_analyses):.1%})")
        
        # DISCRIMINATING FACTORS
        print(f"\n🎯 DISCRIMINATING FACTORS:")
        
        transfer_pos_diff = buy_avg_transfer_pos - sell_avg_transfer_pos
        print(f"   Transfer position difference: {transfer_pos_diff:+.2%}")
        if abs(transfer_pos_diff) > 0.1:  # 10% difference
            print(f"   ✅ STRONG DISCRIMINATOR: Transfer timing significantly different!")
        else:
            print(f"   ⚠️ WEAK DISCRIMINATOR: Transfer timing similar")
        
        logs_diff = buy_avg_logs - sell_avg_logs
        print(f"   Transaction length difference: {logs_diff:+.1f} logs")
        
        transfers_diff = buy_avg_transfers - sell_avg_transfers
        print(f"   Transfer count difference: {transfers_diff:+.1f} transfers")
        
        # RECOMMENDED DETECTION LOGIC
        print(f"\n🚀 RECOMMENDED DETECTION LOGIC:")
        print(f"   1. Transfer Position Rule:")
        if buy_avg_transfer_pos > sell_avg_transfer_pos:
            threshold = (buy_avg_transfer_pos + sell_avg_transfer_pos) / 2
            print(f"      - If avg transfer position > {threshold:.2%} → BUY")
            print(f"      - If avg transfer position ≤ {threshold:.2%} → SELL")
        else:
            threshold = (buy_avg_transfer_pos + sell_avg_transfer_pos) / 2
            print(f"      - If avg transfer position < {threshold:.2%} → BUY")
            print(f"      - If avg transfer position ≥ {threshold:.2%} → SELL")
        
        print(f"   2. Sequence Pattern Rules:")
        if buy_has_close_after > sell_has_close_after:
            print(f"      - CloseAccount after transfers more common in BUYs")
        elif sell_has_close_after > buy_has_close_after:
            print(f"      - CloseAccount after transfers more common in SELLs")
        
        if buy_has_init_before > sell_has_init_before:
            print(f"      - InitializeAccount before transfers more common in BUYs")
        elif sell_has_init_before > buy_has_init_before:
            print(f"      - InitializeAccount before transfers more common in SELLs")
        
        print(f"\n💡 CONFIDENCE ASSESSMENT:")
        if abs(transfer_pos_diff) > 0.15:
            print(f"   🟢 HIGH CONFIDENCE: Transfer position is a strong discriminator")
        elif abs(transfer_pos_diff) > 0.05:
            print(f"   🟡 MEDIUM CONFIDENCE: Transfer position shows some difference")
        else:
            print(f"   🔴 LOW CONFIDENCE: Transfer position not discriminating")

async def main():
    """Main analysis function - waiting for user's transaction signatures"""
    
    print("🧪 USER TRANSACTION PATTERN ANALYZER")
    print("=" * 80)
    print("Please provide your confirmed BUY and SELL transaction signatures")
    print("for comprehensive pattern analysis")
    print("=" * 80)
    
    # USER PROVIDED SIGNATURES - CONFIRMED BUY/SELL TRANSACTIONS
    user_buy_signatures = [
        "4TMgVbpTY83dci52HkyShgHJDowYeyBrn7S1CdW1YR3Gh4mLHWiJjwBTcFpQVmRtqqYpMyi7BnDSZCqNPve3GaRW",
        "2CDKCDhzUjKKxNQkhbcNMh2zVeq14pwmSnyNdGCq8XvB7cqHyMaXHgtgLUMov9E8FUkAauoubJ2zC9JjURFewymr",
        "UDUp8Z5FA8HPij7uXXkwcmvVEL1bG89HFeKijVqS1Kq1pMHtXuKiC6cL7PZdFuvQSiMUqntq13P8EjijM49wXqf",
        "3zpcyXDudoShNYrgohoy5vYFLJaCf7tTAGVYgKiqf2STQkXHSfcfH1Bw51GDxg7LbEXrDGZGMAoRVa2PLs2canSE"
    ]
    
    user_sell_signatures = [
        # ORIGINAL SELL SIGNATURES (7 transactions - 100% validated)
        "2TiAZ3gDLosvWryz84oCZLKfeB8qEWwkZo4a2htKjRZdBpSjPnV8fwLMrgNvsQbZfsn4m8K5V2zkHLVJGQaEA8Xj",
        "4tijQwFC5hhngmQJHefeBjSpphd28ssfJZJaPpZ3Sh7Z89r8B12MuEQT7APqQ53MLtYtkaFYt6Ex4qva55jh9XNN",
        "4h3EtfEPH9nge9tW9wjK483hye9jsvyWP77jaxQHhzsD3S8ruHpLjxut7MnPG4yoybdiX9UEDMw3ysCAzyqAuG4A",
        "2jVHGoggb4FSPqkKQMREquyhceWA2nG3TDkbqk8WWV5D2NJLnPJBu85P4nwkcNSTpVrvNQ8z3mDcgQTYgKZhXbzd",
        "3WEhx6hMSp9ciGZ2LKgMmWmWf7fWu6giynZ2pL2pQsSrpJwxtUhVhdjqsufv2Z72wdpn3KgEtdBF6Jn8Cheo2NBk",
        "2pomJiWey1k8NXyYczCFEiXYGJxHupXVHwJoVQYhR9RdA3bJrTJbWXncVeLjdvYnKvbMpvcUHgdmxJBUmKBJTd1P",
        "3coQUsYoZpUbCtwBo5CAS9gvpsoyECHdWguj3353zDUxJWXpYqZFN8U63nayZQ77yxrbvE2AWNLwyvywKjNAaghW",
        
        # NEW ADDITIONAL SELL SIGNATURES (11 transactions - to be validated)
        "5aUojub2bBvY4vGpvmtYvVKnuYetEaWwGi3csU1hYcMo9FVGF1ofjpFmGHZHToYTDtn8oyhtYzRctP5uuv8QUahB",
        "4SyXk5tS7EpSVvRDFQ7DL4KP7z8HgeS52jFZ75m6ymowfDPsAJQEacLtQWjBKwaYANxBgyVyxSKHsqJYrLv7jpco",
        "267rkRQkV6QHsvRFEcyVKnTjoRBH9wdEX1wBNY1FLRnxim87pYF3SvYnUyweHqDm8EXfMNxxn2Yax2dangLhzXQJ",
        "5dtbtTcMJ3a63JKdzd5U5SdgBGVyFQyZfZaahn2KwJhaRgx5A6PqVqAC8FH5WW3HkWm5MPd4VGGsdhaJ7GZJGYoL",
        "4cL7ZzRjgx374y4ZCy2vWQdXhmG9tstW1JPi3DiLmWBZj3sNjdaYHNRxvReV1EcEpC6CEMf8XSsvEcrdRdK6rSwE",
        "32yrmAJRpH7EruUA3ZYXCm19v4P3jDVG8JNHzrUxgeZqYZMNoF5mQpEGRPLrTgB7cDCMhb1T6hLxAkAYzdHoF4Jr",
        "ktgC7ndhpLP6TsJjSCbJAgKsZSoiSD1CY3n4JLRe27n96MUHY8c7hTTdoGrq8Dqap5CMiGC1hr7eHJ3Q3C2iBKo",
        "4LhTxwUxM2uWz5oACJ49T6a3ZA2eugW5AB5Lsbz6GmDn7LJiQJYkbxxuhzhSwrYtzMUvXQZ4dM7aU2c88GbaVCVy",
        "3oPcnjo5L2PsbUWbKo7ten991yaz24U3QjmhcZso8vfUGYUfRm5NyQiGR4FcXBWSYPxmZLS6fsDxDzRGBvQcrCXr",
        "4N66GktemYm9ihtnVjqzz2CAGmt1buuZz4sn7x9MEpBALYSzpge3eLGhPs3TZVAHz1hDbhGXZNcADeFTBuhCiX8U",
        "5M9ZNBQjJbpGL3gpodmnBrSEiZkKMbgQBm2AudAdR2GjSH9ftHi7d9BFwyGehXUoBF8dMyXnPYZur4svumjVqYUE"
    ]
    
    analyzer = UserTransactionAnalyzer()
    
    try:
        await analyzer.compare_buy_sell_patterns(user_buy_signatures, user_sell_signatures)
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    print("🎯 Analyzing your confirmed buy/sell transaction signatures!")
    print("🚀 Starting comprehensive pattern analysis...")
    
    # Run the analysis with user's signatures
    asyncio.run(main())
