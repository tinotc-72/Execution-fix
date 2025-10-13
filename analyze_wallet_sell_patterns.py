#!/usr/bin/env python3
"""
Analyze Wallet Sell Patterns - Deep Transaction Analysis
Examines how a specific wallet executes SELL transactions to understand their trading strategy
"""

import asyncio
import json
import requests
from typing import Dict, Any, List, Tuple
from collections import defaultdict, Counter
import logging
from datetime import datetime, timezone
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WalletSellPatternAnalyzer:
    """Deep analysis of a wallet's selling patterns and DEX preferences"""
    
    def __init__(self):
        try:
            kz = EnvKeys()
            # Use the same RPC configuration as main bot
            if hasattr(kz, 'HELIUS_RPC_URL'):
                self.rpc_url = kz.HELIUS_RPC_URL
            else:
                api_key = "7277139c-ff2c-4257-ad06-2db6aa16c315"
                self.rpc_url = f"https://mainnet.helius-rpc.com/v0?api-key={api_key}"
            
            logger.info(f"🔗 Connected to RPC: {self.rpc_url[:50]}...")
        except Exception as e:
            logger.error(f"❌ Error loading RPC configuration: {e}")
            raise
    
    async def get_wallet_transactions(self, wallet_address: str, limit: int = 100) -> List[str]:
        """Get recent transaction signatures for the wallet"""
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                wallet_address,
                {
                    "limit": limit,
                    "commitment": "confirmed"
                }
            ]
        }
        
        try:
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result and result["result"]:
                signatures = [tx["signature"] for tx in result["result"]]
                logger.info(f"📋 Found {len(signatures)} transactions for wallet")
                return signatures
            else:
                logger.warning("⚠️ No transactions found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching wallet transactions: {e}")
            return []
    
    async def analyze_transaction(self, signature: str) -> Dict[str, Any]:
        """Analyze a single transaction to extract sell patterns"""
        
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
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "result" not in result or not result["result"]:
                return {"error": "Transaction not found"}
            
            tx_data = result["result"]
            meta = tx_data.get("meta", {})
            transaction = tx_data.get("transaction", {})
            
            # Extract key information
            analysis = {
                "signature": signature,
                "success": meta.get("err") is None,
                "fee": meta.get("fee", 0),
                "compute_units_consumed": meta.get("computeUnitsConsumed", 0),
                "programs_used": [],
                "router_programs": [],
                "sell_indicators": [],
                "token_changes": [],
                "sol_changes": {},
                "instruction_count": 0,
                "priority_fee_info": {},
                "timestamp": None
            }
            
            # Extract timestamp
            if "blockTime" in tx_data:
                analysis["timestamp"] = datetime.fromtimestamp(tx_data["blockTime"], timezone.utc)
            
            # Analyze instructions
            message = transaction.get("message", {})
            instructions = message.get("instructions", [])
            analysis["instruction_count"] = len(instructions)
            
            # Get account keys
            account_keys = message.get("accountKeys", [])
            
            # Analyze each instruction
            for idx, instruction in enumerate(instructions):
                program_idx = instruction.get("programIdIndex", 0)
                if program_idx < len(account_keys):
                    program_id = account_keys[program_idx]
                    analysis["programs_used"].append(program_id)
                    
                    # Check for known DEX programs
                    if program_id in [
                        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter
                        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # Pump.fun
                        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium CPMM
                        "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",   # pAMM Bay
                        "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",   # Raydium CPMM v2
                        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc"    # Orca Whirlpools
                    ]:
                        analysis["router_programs"].append({
                            "program_id": program_id,
                            "instruction_index": idx,
                            "data": instruction.get("data", "")
                        })
            
            # Analyze logs for sell indicators
            logs = meta.get("logMessages", [])
            for log in logs:
                if any(indicator in log.lower() for indicator in 
                      ["sell", "swap", "exchange", "trade", "instruction: sell"]):
                    analysis["sell_indicators"].append(log)
            
            # Analyze token balance changes
            pre_token_balances = meta.get("preTokenBalances", [])
            post_token_balances = meta.get("postTokenBalances", [])
            
            # Create balance change map
            balance_changes = {}
            
            # Process pre-balances
            for balance in pre_token_balances:
                account_idx = balance.get("accountIndex")
                mint = balance.get("mint")
                amount = float(balance.get("uiTokenAmount", {}).get("uiAmount", 0))
                balance_changes[f"{account_idx}_{mint}"] = {"pre": amount, "post": 0}
            
            # Process post-balances
            for balance in post_token_balances:
                account_idx = balance.get("accountIndex")
                mint = balance.get("mint")
                amount = float(balance.get("uiTokenAmount", {}).get("uiAmount", 0))
                key = f"{account_idx}_{mint}"
                if key in balance_changes:
                    balance_changes[key]["post"] = amount
                else:
                    balance_changes[key] = {"pre": 0, "post": amount}
            
            # Identify sells (token amount decreased)
            for key, change in balance_changes.items():
                diff = change["post"] - change["pre"]
                if diff < -0.001:  # Significant decrease (sell)
                    analysis["token_changes"].append({
                        "mint": key.split("_")[1],
                        "change": diff,
                        "type": "SELL",
                        "pre_amount": change["pre"],
                        "post_amount": change["post"]
                    })
                elif diff > 0.001:  # Increase (buy)
                    analysis["token_changes"].append({
                        "mint": key.split("_")[1],
                        "change": diff,
                        "type": "BUY",
                        "pre_amount": change["pre"],
                        "post_amount": change["post"]
                    })
            
            # Analyze SOL balance changes
            pre_sol = meta.get("preBalances", [])
            post_sol = meta.get("postBalances", [])
            
            for i, (pre, post) in enumerate(zip(pre_sol, post_sol)):
                diff = post - pre
                if abs(diff) > 1000:  # Significant SOL change (in lamports)
                    analysis["sol_changes"][i] = {
                        "change_lamports": diff,
                        "change_sol": diff / 1_000_000_000
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing transaction {signature[:8]}: {e}")
            return {"error": str(e)}
    
    async def analyze_wallet_sell_strategy(self, wallet_address: str) -> Dict[str, Any]:
        """Comprehensive analysis of wallet's selling strategy"""
        
        logger.info(f"🔍 Analyzing sell patterns for wallet: {wallet_address}")
        
        # Get transaction history
        signatures = await self.get_wallet_transactions(wallet_address, limit=50)
        if not signatures:
            return {"error": "No transactions found"}
        
        # Analyze each transaction
        transaction_analyses = []
        sell_transactions = []
        
        for i, signature in enumerate(signatures[:30]):  # Analyze last 30 transactions
            logger.info(f"📊 Analyzing transaction {i+1}/30: {signature[:8]}...")
            analysis = await self.analyze_transaction(signature)
            
            if "error" not in analysis:
                transaction_analyses.append(analysis)
                
                # Check if this is a sell transaction
                has_sell_indicators = len(analysis["sell_indicators"]) > 0
                has_token_decreases = any(change["type"] == "SELL" for change in analysis["token_changes"])
                has_router_programs = len(analysis["router_programs"]) > 0
                
                if has_sell_indicators or has_token_decreases or has_router_programs:
                    sell_transactions.append(analysis)
        
        # Generate comprehensive report
        report = {
            "wallet_address": wallet_address,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_transactions_analyzed": len(transaction_analyses),
            "sell_transactions_found": len(sell_transactions),
            "sell_strategy_summary": self._generate_sell_strategy_summary(sell_transactions),
            "dex_preferences": self._analyze_dex_preferences(sell_transactions),
            "timing_patterns": self._analyze_timing_patterns(sell_transactions),
            "transaction_structure": self._analyze_transaction_structure(sell_transactions),
            "detailed_sell_transactions": sell_transactions[:10]  # Show top 10 detailed
        }
        
        return report
    
    def _generate_sell_strategy_summary(self, sell_transactions: List[Dict]) -> Dict[str, Any]:
        """Generate summary of selling strategy"""
        
        if not sell_transactions:
            return {"strategy": "No sell transactions found"}
        
        # Analyze router program usage
        router_usage = Counter()
        for tx in sell_transactions:
            for router in tx["router_programs"]:
                program_id = router["program_id"]
                router_usage[program_id] += 1
        
        # Map program IDs to names
        program_names = {
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium CPMM",
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "pAMM Bay",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM v2",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpools"
        }
        
        router_usage_named = {
            program_names.get(pid, pid[:8]): count 
            for pid, count in router_usage.items()
        }
        
        # Calculate average metrics
        avg_fee = sum(tx["fee"] for tx in sell_transactions) / len(sell_transactions)
        avg_compute = sum(tx["compute_units_consumed"] for tx in sell_transactions) / len(sell_transactions)
        success_rate = sum(1 for tx in sell_transactions if tx["success"]) / len(sell_transactions) * 100
        
        return {
            "primary_strategy": "Multi-DEX" if len(router_usage) > 1 else "Single-DEX",
            "preferred_dex": max(router_usage_named, key=router_usage_named.get) if router_usage_named else "Unknown",
            "dex_usage_distribution": dict(router_usage_named),
            "average_transaction_fee": avg_fee / 1_000_000_000,  # Convert to SOL
            "average_compute_units": int(avg_compute),
            "success_rate_percent": round(success_rate, 1),
            "total_sell_transactions": len(sell_transactions)
        }
    
    def _analyze_dex_preferences(self, sell_transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze DEX preferences and routing patterns"""
        
        dex_analysis = {
            "routing_complexity": [],
            "multi_hop_usage": 0,
            "single_hop_usage": 0,
            "cross_dex_arbitrage": 0
        }
        
        for tx in sell_transactions:
            router_count = len(tx["router_programs"])
            instruction_count = tx["instruction_count"]
            
            if router_count > 1:
                dex_analysis["multi_hop_usage"] += 1
            else:
                dex_analysis["single_hop_usage"] += 1
            
            dex_analysis["routing_complexity"].append({
                "signature": tx["signature"][:8],
                "router_programs": len(tx["router_programs"]),
                "total_instructions": instruction_count,
                "complexity_score": router_count * instruction_count
            })
        
        return dex_analysis
    
    def _analyze_timing_patterns(self, sell_transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze timing patterns in selling behavior"""
        
        timestamps = [tx["timestamp"] for tx in sell_transactions if tx["timestamp"]]
        
        if not timestamps:
            return {"pattern": "No timestamp data available"}
        
        # Sort by timestamp
        timestamps.sort()
        
        # Calculate intervals between sells
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        timing_analysis = {
            "total_sell_period_days": (max(timestamps) - min(timestamps)).days if len(timestamps) > 1 else 0,
            "average_interval_hours": sum(intervals) / len(intervals) / 3600 if intervals else 0,
            "sell_frequency": "High" if len(sell_transactions) > 10 else "Medium" if len(sell_transactions) > 5 else "Low",
            "latest_sell": max(timestamps).isoformat() if timestamps else None,
            "earliest_sell": min(timestamps).isoformat() if timestamps else None
        }
        
        return timing_analysis
    
    def _analyze_transaction_structure(self, sell_transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze common transaction structures"""
        
        structure_patterns = {
            "compute_budget_usage": 0,
            "priority_fee_usage": 0,
            "average_instructions": 0,
            "complex_transactions": 0
        }
        
        total_instructions = 0
        for tx in sell_transactions:
            total_instructions += tx["instruction_count"]
            
            # Check for compute budget instructions
            if "ComputeBudget" in str(tx["programs_used"]):
                structure_patterns["compute_budget_usage"] += 1
            
            # Complex transaction (>10 instructions)
            if tx["instruction_count"] > 10:
                structure_patterns["complex_transactions"] += 1
        
        structure_patterns["average_instructions"] = (
            total_instructions / len(sell_transactions) if sell_transactions else 0
        )
        
        structure_patterns["compute_budget_usage_percent"] = (
            structure_patterns["compute_budget_usage"] / len(sell_transactions) * 100 if sell_transactions else 0
        )
        
        return structure_patterns

async def main():
    """Main execution function"""
    
    # Target wallet to analyze
    WALLET_ADDRESS = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    
    analyzer = WalletSellPatternAnalyzer()
    
    logger.info(f"🚀 Starting comprehensive sell pattern analysis for wallet: {WALLET_ADDRESS}")
    
    # Perform analysis
    report = await analyzer.analyze_wallet_sell_strategy(WALLET_ADDRESS)
    
    # Display results
    print("\n" + "="*80)
    print("🎯 WALLET SELL STRATEGY ANALYSIS REPORT")
    print("="*80)
    
    if "error" in report:
        print(f"❌ Analysis failed: {report['error']}")
        return
    
    # Summary
    print(f"\n📊 ANALYSIS SUMMARY")
    print(f"   Wallet: {report['wallet_address']}")
    print(f"   Transactions Analyzed: {report['total_transactions_analyzed']}")
    print(f"   Sell Transactions Found: {report['sell_transactions_found']}")
    
    # Strategy Summary
    strategy = report['sell_strategy_summary']
    print(f"\n🎯 SELL STRATEGY")
    print(f"   Strategy Type: {strategy['primary_strategy']}")
    print(f"   Preferred DEX: {strategy['preferred_dex']}")
    print(f"   Success Rate: {strategy['success_rate_percent']}%")
    print(f"   Avg Transaction Fee: {strategy['average_transaction_fee']:.6f} SOL")
    print(f"   Avg Compute Units: {strategy['average_compute_units']:,}")
    
    # DEX Distribution
    print(f"\n🏪 DEX USAGE DISTRIBUTION")
    for dex, count in strategy['dex_usage_distribution'].items():
        percentage = (count / strategy['total_sell_transactions'] * 100) if strategy['total_sell_transactions'] > 0 else 0
        print(f"   {dex}: {count} transactions ({percentage:.1f}%)")
    
    # DEX Preferences
    dex_prefs = report['dex_preferences']
    print(f"\n🔄 ROUTING COMPLEXITY")
    print(f"   Single-hop sells: {dex_prefs['single_hop_usage']}")
    print(f"   Multi-hop sells: {dex_prefs['multi_hop_usage']}")
    
    # Timing Patterns
    timing = report['timing_patterns']
    print(f"\n⏰ TIMING PATTERNS")
    print(f"   Sell Frequency: {timing['sell_frequency']}")
    print(f"   Trading Period: {timing['total_sell_period_days']} days")
    if timing['average_interval_hours'] > 0:
        print(f"   Avg Time Between Sells: {timing['average_interval_hours']:.1f} hours")
    
    # Transaction Structure
    structure = report['transaction_structure']
    print(f"\n🏗️ TRANSACTION STRUCTURE")
    print(f"   Avg Instructions per TX: {structure['average_instructions']:.1f}")
    print(f"   Compute Budget Usage: {structure['compute_budget_usage_percent']:.1f}%")
    print(f"   Complex Transactions: {structure['complex_transactions']}")
    
    # Detailed Examples
    print(f"\n📋 RECENT SELL TRANSACTION EXAMPLES")
    for i, tx in enumerate(report['detailed_sell_transactions'][:5]):
        print(f"\n   Example {i+1}: {tx['signature'][:16]}...")
        print(f"      Success: {'✅' if tx['success'] else '❌'}")
        print(f"      Fee: {tx['fee']/1_000_000_000:.6f} SOL")
        print(f"      Compute: {tx['compute_units_consumed']:,} units")
        print(f"      Instructions: {tx['instruction_count']}")
        
        if tx['router_programs']:
            print(f"      Router Programs:")
            for router in tx['router_programs'][:3]:  # Show first 3
                program_name = {
                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium CPMM",
                    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "pAMM Bay"
                }.get(router['program_id'], router['program_id'][:8])
                print(f"         - {program_name}")
        
        if tx['token_changes']:
            for change in tx['token_changes'][:2]:  # Show first 2 token changes
                if change['type'] == 'SELL':
                    print(f"      Token Sold: {abs(change['change']):.6f} tokens")
    
    print(f"\n" + "="*80)
    print("🎯 CONCLUSION: This wallet's selling strategy has been analyzed!")
    print("Use this information to replicate their DEX preferences and transaction structure.")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())