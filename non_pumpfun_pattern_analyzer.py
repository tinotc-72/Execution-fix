"""
Non-Pump.fun Trading Pattern Analyzer
Reverse engineers how target wallets trade on Jupiter, Meteora, Raydium, etc.
Focus on understanding their strategies to build better executors
"""

import sys
import base64
import struct
import asyncio
import httpx
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from env_keys import EnvKeys


class NonPumpFunAnalyzer:
    """Analyze target wallet transactions on non-Pump.fun platforms"""
    
    def __init__(self):
        env = EnvKeys()
        self.rpc_url = env.HELIUS_RPC_URL
        
        # Target wallets (from main.py)
        self.target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
        ]
        
        # Non-Pump.fun DEX programs to analyze
        self.dex_programs = {
            # Jupiter (Aggregator)
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            
            # Raydium variants
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4 AMM",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Raydium LaunchLab",
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Raydium CPMM v2",
            
            # Meteora
            "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "Meteora Dynamic Bonding Curve",
            "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora DLMM",
            
            # Orca
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool v2",
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca v1",
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca v2",
            
            # Other
            "EhYXq3ANp5nAerUpbSgd7VK2RRcxK1zNuSQ755G5Mtxx": "Serum/OpenBook",
            "srmqPiAMgUidFWrEEPVt7fvMJPJbcmuHggASNGdvYNV": "Serum v3",
        }
        
        # MEV and router programs
        self.mev_programs = {
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Professional MEV Bot",
            "F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq": "Advanced Router",
            "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ": "Fee Calculator",
            "jitodontfrontd1111111TradeWithAxiomDotTrade": "Jito MEV Protection"
        }
        
        # System programs (filter these out for cleaner analysis)
        self.system_programs = {
            "11111111111111111111111111111111": "System Program",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program",
            "ComputeBudget111111111111111111111111111111": "Compute Budget",
            "SysvarRent111111111111111111111111111111111": "Rent Sysvar",
            "SysvarC1ock11111111111111111111111111111111": "Clock Sysvar",
        }
        
        # Pump.fun (to filter out)
        self.pumpfun_programs = {
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun"
        }

    async def fetch_wallet_signatures(self, wallet_address: str, limit: int = 50) -> List[str]:
        """Fetch recent transaction signatures for a wallet"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet_address, {"limit": limit}]
            })
            
            data = response.json()
            if "error" in data:
                raise Exception(f"RPC error: {data['error']}")
            
            return [sig["signature"] for sig in data["result"]]

    async def fetch_transaction(self, signature: str) -> Dict[str, Any]:
        """Fetch detailed transaction data"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {"encoding": "json", "maxSupportedTransactionVersion": 0}
                ]
            })
            
            data = response.json()
            if "error" in data:
                return None
            
            return data["result"]

    def analyze_non_pumpfun_transaction(self, tx_data: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """Analyze a single non-Pump.fun transaction for patterns"""
        
        if not tx_data or not tx_data.get("transaction"):
            return None
            
        instructions = tx_data["transaction"]["message"]["instructions"]
        account_keys = tx_data["transaction"]["message"]["accountKeys"]
        
        # Get all program IDs used
        program_ids = [account_keys[inst["programIdIndex"]] for inst in instructions]
        
        # Check if this is a non-Pump.fun transaction
        has_pumpfun = any(pid in self.pumpfun_programs for pid in program_ids)
        has_non_pumpfun_dex = any(pid in self.dex_programs for pid in program_ids)
        
        if has_pumpfun or not has_non_pumpfun_dex:
            return None  # Skip Pump.fun or non-DEX transactions
        
        # Identify DEXes used
        dexes_used = []
        mev_tools = []
        
        for pid in program_ids:
            if pid in self.dex_programs:
                dexes_used.append(self.dex_programs[pid])
            elif pid in self.mev_programs:
                mev_tools.append(self.mev_programs[pid])
        
        # Analyze instruction structure
        instruction_analysis = []
        for i, instruction in enumerate(instructions):
            program_id = account_keys[instruction["programIdIndex"]]
            
            if program_id in self.dex_programs:
                instruction_analysis.append({
                    "index": i,
                    "program": self.dex_programs[program_id],
                    "program_id": program_id,
                    "accounts": len(instruction["accounts"]),
                    "data_length": len(instruction["data"]),
                    "data_hex": instruction["data"][:20] + "..." if len(instruction["data"]) > 20 else instruction["data"]
                })
        
        # Extract trading details
        meta = tx_data.get("meta", {})
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        
        # Calculate SOL change for the wallet
        sol_change = 0
        if len(pre_balances) > 0 and len(post_balances) > 0:
            sol_change = (post_balances[0] - pre_balances[0]) / 1_000_000_000
        
        return {
            "signature": signature,
            "slot": tx_data.get("slot"),
            "success": not bool(meta.get("err")),
            "timestamp": tx_data.get("blockTime"),
            "dexes_used": list(set(dexes_used)),
            "mev_tools": list(set(mev_tools)),
            "sol_change": sol_change,
            "fee_sol": meta.get("fee", 0) / 1_000_000_000,
            "instruction_count": len(instructions),
            "dex_instructions": instruction_analysis,
            "compute_units_consumed": meta.get("computeUnitsConsumed"),
            "total_accounts": len(account_keys)
        }

    async def analyze_wallet_non_pumpfun_patterns(self, wallet_address: str, limit: int = 100) -> Dict[str, Any]:
        """Analyze all non-Pump.fun transactions for a wallet"""
        
        print(f"🔍 Analyzing non-Pump.fun patterns for wallet: {wallet_address[:8]}...")
        
        # Fetch recent signatures
        signatures = await self.fetch_wallet_signatures(wallet_address, limit)
        print(f"📡 Found {len(signatures)} recent transactions")
        
        non_pumpfun_transactions = []
        processed = 0
        
        for signature in signatures:
            try:
                tx_data = await self.fetch_transaction(signature)
                if tx_data:
                    analysis = self.analyze_non_pumpfun_transaction(tx_data, signature)
                    if analysis:
                        non_pumpfun_transactions.append(analysis)
                        print(f"✅ Found non-Pump.fun trade: {analysis['dexes_used']}")
                
                processed += 1
                if processed % 10 == 0:
                    print(f"⏳ Processed {processed}/{len(signatures)} transactions...")
                    
            except Exception as e:
                print(f"❌ Error processing {signature[:8]}: {e}")
                continue
        
        # Aggregate patterns
        return self._aggregate_patterns(non_pumpfun_transactions, wallet_address)

    def _aggregate_patterns(self, transactions: List[Dict[str, Any]], wallet_address: str) -> Dict[str, Any]:
        """Aggregate patterns from multiple transactions"""
        
        if not transactions:
            return {
                "wallet": wallet_address,
                "total_non_pumpfun_trades": 0,
                "message": "No non-Pump.fun trades found"
            }
        
        # DEX usage statistics
        dex_usage = {}
        mev_tool_usage = {}
        success_rates = {}
        
        for tx in transactions:
            # Count DEX usage
            for dex in tx["dexes_used"]:
                dex_usage[dex] = dex_usage.get(dex, 0) + 1
                if dex not in success_rates:
                    success_rates[dex] = {"successful": 0, "total": 0}
                success_rates[dex]["total"] += 1
                if tx["success"]:
                    success_rates[dex]["successful"] += 1
            
            # Count MEV tool usage
            for tool in tx["mev_tools"]:
                mev_tool_usage[tool] = mev_tool_usage.get(tool, 0) + 1
        
        # Calculate success rates
        dex_success_rates = {}
        for dex, stats in success_rates.items():
            dex_success_rates[dex] = {
                "success_rate": (stats["successful"] / stats["total"] * 100) if stats["total"] > 0 else 0,
                "successful_trades": stats["successful"],
                "total_trades": stats["total"]
            }
        
        # Identify most common patterns
        instruction_patterns = {}
        for tx in transactions:
            for instruction in tx["dex_instructions"]:
                program = instruction["program"]
                pattern_key = f"{program}_{instruction['accounts']}accounts_{instruction['data_length']}bytes"
                instruction_patterns[pattern_key] = instruction_patterns.get(pattern_key, 0) + 1
        
        return {
            "wallet": wallet_address,
            "analysis_summary": {
                "total_non_pumpfun_trades": len(transactions),
                "successful_trades": sum(1 for tx in transactions if tx["success"]),
                "overall_success_rate": (sum(1 for tx in transactions if tx["success"]) / len(transactions) * 100) if transactions else 0
            },
            "dex_preferences": {
                "usage_count": dex_usage,
                "success_rates": dex_success_rates
            },
            "mev_tools_used": mev_tool_usage,
            "common_instruction_patterns": dict(sorted(instruction_patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
            "sample_transactions": transactions[:5],  # First 5 for detailed analysis
            "all_transactions": transactions
        }

    async def reverse_engineer_trading_strategies(self):
        """Analyze both target wallets and compare their non-Pump.fun strategies"""
        
        print("🚀 REVERSE ENGINEERING NON-PUMP.FUN TRADING STRATEGIES")
        print("=" * 60)
        
        results = {}
        
        for wallet in self.target_wallets:
            print(f"\n🎯 Analyzing wallet: {wallet}")
            try:
                analysis = await self.analyze_wallet_non_pumpfun_patterns(wallet, limit=200)
                results[wallet] = analysis
                
                # Print immediate insights
                if analysis["analysis_summary"]["total_non_pumpfun_trades"] > 0:
                    print(f"📊 Found {analysis['analysis_summary']['total_non_pumpfun_trades']} non-Pump.fun trades")
                    print(f"✅ Success rate: {analysis['analysis_summary']['overall_success_rate']:.1f}%")
                    print(f"🔥 Preferred DEXes: {list(analysis['dex_preferences']['usage_count'].keys())}")
                    if analysis["mev_tools_used"]:
                        print(f"🤖 MEV tools: {list(analysis['mev_tools_used'].keys())}")
                else:
                    print("📭 No non-Pump.fun trades found")
                    
            except Exception as e:
                print(f"❌ Error analyzing wallet {wallet}: {e}")
                results[wallet] = {"error": str(e)}
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"non_pumpfun_analysis_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed analysis saved to: {filename}")
        
        # Generate insights summary
        self._generate_insights_summary(results)
        
        return results

    def _generate_insights_summary(self, results: Dict[str, Any]):
        """Generate actionable insights from the analysis"""
        
        print("\n" + "=" * 60)
        print("🧠 REVERSE ENGINEERING INSIGHTS & RECOMMENDATIONS")
        print("=" * 60)
        
        all_dex_usage = {}
        all_mev_tools = {}
        total_non_pumpfun = 0
        
        for wallet, data in results.items():
            if "error" not in data and data.get("analysis_summary", {}).get("total_non_pumpfun_trades", 0) > 0:
                total_non_pumpfun += data["analysis_summary"]["total_non_pumpfun_trades"]
                
                # Aggregate DEX usage
                for dex, count in data["dex_preferences"]["usage_count"].items():
                    all_dex_usage[dex] = all_dex_usage.get(dex, 0) + count
                
                # Aggregate MEV tools
                for tool, count in data["mev_tools_used"].items():
                    all_mev_tools[tool] = all_mev_tools.get(tool, 0) + count
        
        if total_non_pumpfun == 0:
            print("📭 No non-Pump.fun trades found across target wallets")
            return
        
        print(f"📊 TOTAL NON-PUMP.FUN TRADES ANALYZED: {total_non_pumpfun}")
        print(f"\n🎯 TOP DEX PLATFORMS:")
        for dex, count in sorted(all_dex_usage.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_non_pumpfun) * 100
            print(f"   • {dex}: {count} trades ({percentage:.1f}%)")
        
        if all_mev_tools:
            print(f"\n🤖 MEV/OPTIMIZATION TOOLS:")
            for tool, count in sorted(all_mev_tools.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_non_pumpfun) * 100
                print(f"   • {tool}: {count} uses ({percentage:.1f}%)")
        
        print(f"\n💡 EXECUTOR DEVELOPMENT PRIORITIES:")
        sorted_dexes = sorted(all_dex_usage.items(), key=lambda x: x[1], reverse=True)
        
        for i, (dex, count) in enumerate(sorted_dexes[:5], 1):
            percentage = (count / total_non_pumpfun) * 100
            print(f"   {i}. Build advanced {dex} executor ({percentage:.1f}% of trades)")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Examine sample transactions from top DEXes")
        print(f"   2. Reverse engineer instruction patterns")
        print(f"   3. Build MEV-optimized executors")
        print(f"   4. Test with small amounts before production")


async def main():
    """Run the non-Pump.fun pattern analysis"""
    analyzer = NonPumpFunAnalyzer()
    results = await analyzer.reverse_engineer_trading_strategies()
    return results


if __name__ == "__main__":
    asyncio.run(main())
