#!/usr/bin/env python3
"""
Analyze the last 6 transactions from your wallet address
"""

import json
import requests
from datetime import datetime
from typing import List, Dict, Any

class MyWalletAnalyzer:
    def __init__(self):
        # Load RPC URL from environment
        try:
            from env_keys import get_env_value
            self.rpc_url = get_env_value('HELIUS_RPC_URL')
        except:
            self.rpc_url = "https://api.mainnet-beta.solana.com"
        
        # Your wallet address
        self.wallet_address = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
        
        print(f"🔗 Using RPC: {self.rpc_url[:50]}...")
        print(f"👤 Your Wallet: {self.wallet_address}")
        print()
    
    def get_recent_transactions(self, limit: int = 6) -> List[str]:
        """Get the last N transaction signatures for the wallet"""
        print(f"📡 Fetching last {limit} transactions...")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                self.wallet_address,
                {
                    "limit": limit,
                    "commitment": "confirmed"
                }
            ]
        }
        
        try:
            response = requests.post(self.rpc_url, json=payload, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if "result" in data and data["result"]:
                transactions = data["result"]
                print(f"✅ Found {len(transactions)} transactions")
                
                # Print basic info
                for i, tx in enumerate(transactions, 1):
                    sig = tx["signature"]
                    slot = tx.get("slot", "Unknown")
                    block_time = tx.get("blockTime")
                    err = tx.get("err")
                    
                    timestamp = "Unknown"
                    if block_time:
                        timestamp = datetime.fromtimestamp(block_time).strftime("%Y-%m-%d %H:%M:%S")
                    
                    status = "✅ Success" if err is None else f"❌ Failed: {err}"
                    print(f"   {i}. {sig[:16]}... | {timestamp} | {status}")
                
                return [tx["signature"] for tx in transactions]
            else:
                print("❌ No transactions found")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching transactions: {str(e)}")
            return []
    
    def analyze_transaction_detailed(self, signature: str) -> Dict[str, Any]:
        """Get detailed analysis of a single transaction"""
        print(f"\n🔍 DETAILED ANALYSIS: {signature}")
        print("-" * 60)
        
        # Try multiple encodings for best data
        for encoding in ["jsonParsed", "json"]:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        signature,
                        {
                            "encoding": encoding,
                            "commitment": "confirmed",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                }
                
                response = requests.post(self.rpc_url, json=payload, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if "result" in data and data["result"]:
                    return self._analyze_transaction_data(signature, data["result"], encoding)
                    
            except Exception as e:
                print(f"❌ Error with {encoding}: {str(e)}")
                continue
        
        print("❌ Could not fetch transaction data")
        return {"signature": signature, "error": "Could not fetch"}
    
    def _analyze_transaction_data(self, signature: str, tx_data: Dict[str, Any], encoding: str) -> Dict[str, Any]:
        """Analyze the transaction data"""
        meta = tx_data.get("meta", {})
        message = tx_data.get("transaction", {}).get("message", {})
        
        print(f"📊 Basic Info:")
        print(f"   Encoding: {encoding}")
        print(f"   Slot: {tx_data.get('slot')}")
        print(f"   Block Time: {tx_data.get('blockTime')}")
        
        if tx_data.get('blockTime'):
            timestamp = datetime.fromtimestamp(tx_data.get('blockTime')).strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"   Timestamp: {timestamp}")
        
        print(f"   Fee: {meta.get('fee', 0)} lamports ({meta.get('fee', 0) / 1e9:.6f} SOL)")
        print(f"   Compute Units: {meta.get('computeUnitsConsumed', 0)}")
        
        # Status
        error = meta.get("err")
        if error:
            print(f"   Status: ❌ FAILED")
            print(f"   Error: {error}")
        else:
            print(f"   Status: ✅ SUCCESS")
        
        # Instructions
        instructions = message.get("instructions", [])
        print(f"   Instructions: {len(instructions)}")
        
        # Accounts
        account_keys = message.get("accountKeys", [])
        print(f"   Accounts: {len(account_keys)}")
        
        # Programs involved
        programs = set()
        for instruction in instructions:
            program_id_index = instruction.get("programIdIndex")
            if program_id_index is not None and program_id_index < len(account_keys):
                if isinstance(account_keys[program_id_index], dict):
                    program_id = account_keys[program_id_index].get("pubkey")
                else:
                    program_id = account_keys[program_id_index]
                if program_id:
                    programs.add(program_id)
        
        print(f"\n🏛️ Programs Involved:")
        for program_id in programs:
            program_name = self._identify_program(program_id)
            print(f"   • {program_name}")
            print(f"     {program_id}")
        
        # Balance changes
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        
        if len(pre_balances) > 0 and len(post_balances) > 0:
            wallet_change = post_balances[0] - pre_balances[0]
            print(f"\n💰 SOL Balance Change: {wallet_change:+,} lamports ({wallet_change / 1e9:+.6f} SOL)")
        
        # Token balance changes
        pre_token = meta.get("preTokenBalances", [])
        post_token = meta.get("postTokenBalances", [])
        
        if pre_token or post_token:
            print(f"\n🪙 Token Balance Changes:")
            
            # Track changes by mint
            token_changes = {}
            
            # Process pre-balances
            for token_balance in pre_token:
                if token_balance.get("owner") == self.wallet_address:
                    mint = token_balance.get("mint")
                    amount = float(token_balance.get("uiTokenAmount", {}).get("uiAmount", 0) or 0)
                    token_changes[mint] = {"pre": amount, "post": 0}
            
            # Process post-balances
            for token_balance in post_token:
                if token_balance.get("owner") == self.wallet_address:
                    mint = token_balance.get("mint")
                    amount = float(token_balance.get("uiTokenAmount", {}).get("uiAmount", 0) or 0)
                    if mint in token_changes:
                        token_changes[mint]["post"] = amount
                    else:
                        token_changes[mint] = {"pre": 0, "post": amount}
            
            # Display changes
            for mint, balances in token_changes.items():
                change = balances["post"] - balances["pre"]
                if abs(change) > 0.001:  # Only significant changes
                    action = "BOUGHT" if change > 0 else "SOLD"
                    print(f"   • {action}: {change:+,.6f} tokens")
                    print(f"     Mint: {mint}")
                    print(f"     Before: {balances['pre']:,.6f}")
                    print(f"     After: {balances['post']:,.6f}")
        
        # Log messages for detailed analysis
        logs = meta.get("logMessages", [])
        if logs:
            print(f"\n📝 Transaction Logs ({len(logs)} lines):")
            
            # Look for key patterns
            key_logs = []
            for i, log in enumerate(logs):
                if any(keyword in log for keyword in [
                    "Instruction:", "Transfer", "Swap", "Buy", "Sell", 
                    "Initialize", "Close", "Create", "Error", "failed"
                ]):
                    key_logs.append(f"   [{i:2d}] {log}")
            
            if key_logs:
                print("   Key events:")
                for log in key_logs[:10]:  # Show first 10 key events
                    print(log)
                if len(key_logs) > 10:
                    print(f"   ... and {len(key_logs) - 10} more events")
            else:
                print("   (System-level operations)")
        
        return {
            "signature": signature,
            "slot": tx_data.get("slot"),
            "timestamp": tx_data.get("blockTime"),
            "fee": meta.get("fee", 0),
            "compute_units": meta.get("computeUnitsConsumed", 0),
            "status": "success" if error is None else "failed",
            "error": error,
            "programs": list(programs),
            "sol_change": wallet_change / 1e9 if len(pre_balances) > 0 and len(post_balances) > 0 else 0,
            "token_changes": len(token_changes) if 'token_changes' in locals() else 0
        }
    
    def _identify_program(self, program_id: str) -> str:
        """Identify well-known program IDs"""
        known_programs = {
            "11111111111111111111111111111111": "System Program",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program",
            "ComputeBudget111111111111111111111111111111": "Compute Budget Program",
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Raydium CLMM",
            "cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG": "Raydium CPMM",
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump.fun",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
            "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin": "Serum DEX V3"
        }
        
        return known_programs.get(program_id, f"Unknown Program ({program_id[:8]}...)")
    
    def analyze_recent_activity(self, limit: int = 6):
        """Analyze recent wallet activity"""
        print("🔍 MY WALLET TRANSACTION ANALYSIS")
        print("=" * 80)
        
        # Get recent transactions
        signatures = self.get_recent_transactions(limit)
        
        if not signatures:
            print("❌ No recent transactions found")
            return
        
        print(f"\n📊 Analyzing {len(signatures)} transactions in detail...")
        
        # Analyze each transaction
        analyses = []
        for i, signature in enumerate(signatures, 1):
            print(f"\n{'='*80}")
            print(f"📋 TRANSACTION {i}/{len(signatures)}")
            print(f"{'='*80}")
            
            analysis = self.analyze_transaction_detailed(signature)
            analyses.append(analysis)
        
        # Summary
        print(f"\n{'='*80}")
        print(f"📈 WALLET ACTIVITY SUMMARY")
        print(f"{'='*80}")
        
        successful = sum(1 for a in analyses if a.get("status") == "success")
        failed = len(analyses) - successful
        total_fees = sum(a.get("fee", 0) for a in analyses)
        total_sol_change = sum(a.get("sol_change", 0) for a in analyses)
        
        print(f"📊 Overview:")
        print(f"   Total Transactions: {len(analyses)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        print(f"   Total Fees Paid: {total_fees:,} lamports ({total_fees / 1e9:.6f} SOL)")
        print(f"   Net SOL Change: {total_sol_change:+.6f} SOL")
        
        # Recent activity pattern
        if failed > successful:
            print(f"\n⚠️ WARNING: More failed transactions than successful ones!")
            print(f"   This suggests systematic issues with your trading setup.")
            
        if total_fees > 50000:  # More than 0.05 SOL in fees
            print(f"\n💸 HIGH FEE ALERT: You've paid {total_fees / 1e9:.6f} SOL in fees recently")
            
        # Save detailed analysis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"my_wallet_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analyses, f, indent=2, default=str)
        
        print(f"\n💾 Detailed analysis saved to: {filename}")

def main():
    analyzer = MyWalletAnalyzer()
    analyzer.analyze_recent_activity(6)

if __name__ == "__main__":
    main()
