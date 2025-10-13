"""
Enhanced Pump.fun Transaction Pattern Analyzer
Identifies how wallets are trading: Jupiter, Direct, Router, etc.
"""

import sys
import base64
import struct
import asyncio
import httpx
from typing import Dict, List, Any
from env_keys import EnvKeys


class TradingPatternAnalyzer:
    """Analyze transaction signatures to identify trading patterns"""
    
    def __init__(self):
        env = EnvKeys()
        self.rpc_url = env.HELIUS_RPC_URL
        
        # Known program IDs for pattern recognition
        self.programs = {
            # Jupiter
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4", 
            "JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph": "Jupiter V3",
            
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
            
            # Routers & MEV
            "F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq": "Pump.fun Router",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Advanced MEV Bot/Router",
            
            # Other DEXs
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium",
            "5quBtoiQqy5PyxPpSWuxmSv4ryQVgDJXR7U5q2C6Lq9M": "Raydium CPMM",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CLMM",
            "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Raydium LaunchLab",
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Raydium CPMM",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUQpMDdHFWmXqSiF7DT": "Raydium CLMM",
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium V4",
            "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "Meteora Dynamic Bonding Curve",
            "EhYXq3ANp5nAerUpbSgd7VK2RRcxK1zNuSQ755G5Mtxx": "Serum",
            
            # System programs
            "11111111111111111111111111111111": "System Program",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program",
            "ComputeBudget111111111111111111111111111111": "Compute Budget",
            "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ": "Fee Calculator",
        }
        
        # Discriminators for instruction identification
        self.discriminators = {
            "66063d1201daebea": "Pump.fun BUY",
            "33e685a4017f83ad": "Pump.fun SELL",
            "e445a52e51cb9a1d": "Jupiter SWAP",
            "229299aad5280fd2": "Jupiter ROUTE",
        }
    
    async def fetch_transaction(self, signature: str) -> Dict[str, Any]:
        """Fetch transaction data from RPC"""
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
                raise Exception(f"RPC error: {data['error']}")
            
            return data["result"]
    
    def identify_trading_pattern(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify how the wallet is trading"""
        
        if not tx_data:
            return {"error": "Transaction not found"}
        
        instructions = tx_data['transaction']['message']['instructions']
        account_keys = tx_data['transaction']['message']['accountKeys']
        
        # Get all program IDs used
        program_ids = [account_keys[inst['programIdIndex']] for inst in instructions]
        programs_used = []
        
        for program_id in program_ids:
            if program_id in self.programs:
                programs_used.append(self.programs[program_id])
            else:
                programs_used.append(f"Unknown ({program_id[:8]}...)")
        
        # Analyze trading pattern
        pattern = self._analyze_pattern(program_ids, instructions, account_keys)
        
        return {
            "signature": tx_data.get("transaction", {}).get("signatures", ["unknown"])[0] if "transaction" in tx_data else "unknown",
            "slot": tx_data.get("slot"),
            "success": not bool(tx_data.get("meta", {}).get("err")),
            "pattern": pattern,
            "programs_used": list(set(programs_used)),
            "instruction_count": len(instructions),
            "fee_sol": tx_data.get("meta", {}).get("fee", 0) / 1_000_000_000,
        }
    
    def _analyze_pattern(self, program_ids: List[str], instructions: List[Dict], account_keys: List[str]) -> Dict[str, Any]:
        """Analyze the trading pattern based on programs and instructions"""
        
        pattern = {
            "method": "Unknown",
            "category": "Unknown", 
            "confidence": "Low",
            "details": "",
            "instructions": []
        }
        
        # Check for specific patterns
        jupiter_programs = [
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
            "JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph"
        ]
        
        pump_direct = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
        pump_router = "F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq"
        mev_bot = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
        
        # Analyze each instruction
        for i, instruction in enumerate(instructions):
            program_id = account_keys[instruction['programIdIndex']]
            inst_analysis = self._analyze_instruction(instruction, program_id, account_keys)
            pattern["instructions"].append({
                "index": i,
                "program": self.programs.get(program_id, f"Unknown ({program_id[:8]}...)"),
                "program_id": program_id,
                **inst_analysis
            })
        
        # Determine overall pattern
        has_jupiter = any(jp in program_ids for jp in jupiter_programs)
        has_pump_direct = pump_direct in program_ids
        has_pump_router = pump_router in program_ids
        has_mev_bot = mev_bot in program_ids
        
        # Meteora Dynamic Bonding Curve detection
        meteora_dbc = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"
        has_meteora_dbc = meteora_dbc in program_ids
        
        # Enhanced pattern detection with Meteora support
        if has_meteora_dbc and has_jupiter:
            pattern.update({
                "method": "Jupiter + Meteora DBC",
                "category": "Hybrid Meteora",
                "confidence": "High",
                "details": "Uses Jupiter aggregator to route trades through Meteora Dynamic Bonding Curve for new token launches"
            })
        elif has_meteora_dbc:
            pattern.update({
                "method": "Direct Meteora DBC",
                "category": "Direct Meteora",
                "confidence": "High",
                "details": "Direct interaction with Meteora Dynamic Bonding Curve for new token trading (early launch strategy)"
            })
        elif has_mev_bot and has_pump_direct:
            pattern.update({
                "method": "Advanced MEV Bot",
                "category": "MEV/Bot",
                "confidence": "High",
                "details": "Uses sophisticated MEV bot with fee calculation and direct Pump.fun execution (professional/bot trading)"
            })
        elif has_mev_bot:
            pattern.update({
                "method": "Advanced MEV Bot",
                "category": "MEV/Bot", 
                "confidence": "High",
                "details": "Uses sophisticated MEV/bot program to execute Pump.fun trades with advanced features"
            })
        elif has_jupiter and has_pump_direct:
            pattern.update({
                "method": "Jupiter + Direct Hybrid",
                "category": "Hybrid",
                "confidence": "High",
                "details": "Uses Jupiter aggregator combined with direct Pump.fun calls for optimization"
            })
        elif has_jupiter:
            pattern.update({
                "method": "Jupiter Aggregator",
                "category": "Aggregator",
                "confidence": "High", 
                "details": "Routes trades through Jupiter for best prices across multiple DEXs"
            })
        elif has_pump_direct and has_pump_router:
            pattern.update({
                "method": "Router + Direct",
                "category": "Mixed Direct",
                "confidence": "High",
                "details": "Uses router program with direct Pump.fun calls (common MEV pattern)"
            })
        elif has_pump_router:
            pattern.update({
                "method": "Router Program",
                "category": "Router",
                "confidence": "High",
                "details": "Uses router program to handle Pump.fun trades (most common pattern)"
            })
        elif has_pump_direct:
            pattern.update({
                "method": "Direct Protocol",
                "category": "Direct",
                "confidence": "High",
                "details": "Direct calls to Pump.fun program (requires manual account setup)"
            })
        else:
            # Check for other DEX patterns
            other_dexes = [
                "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium
                "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Raydium CPMM
                "CAMMCzo5YL8w4VFF8KVHrK22GGUQpMDdHFWmXqSiF7DT",  # Raydium CLMM
            ]
            
            for dex in other_dexes:
                if dex in program_ids:
                    dex_name = self.programs.get(dex, "Unknown DEX")
                    pattern.update({
                        "method": f"{dex_name} Trading",
                        "category": "DEX",
                        "confidence": "Medium",
                        "details": f"Uses {dex_name} for trading (not Pump.fun specific)"
                    })
                    break
        
        return pattern
    
    def _analyze_instruction(self, instruction: Dict, program_id: str, account_keys: List[str]) -> Dict[str, Any]:
        """Analyze individual instruction"""
        
        analysis = {
            "type": "Unknown",
            "data_length": len(instruction.get("data", "")),
            "account_count": len(instruction.get("accounts", [])),
        }
        
        # Decode instruction data if possible
        data = instruction.get("data", "")
        if data:
            try:
                data_bytes = base64.b64decode(data)
                if len(data_bytes) >= 8:
                    discriminator = data_bytes[:8].hex()
                    analysis["discriminator"] = discriminator
                    
                    if discriminator in self.discriminators:
                        analysis["type"] = self.discriminators[discriminator]
                        
                        # Decode specific instruction types
                        if discriminator == "66063d1201daebea":  # Pump.fun BUY
                            analysis.update(self._decode_pump_buy(data_bytes))
                        elif discriminator == "33e685a4017f83ad":  # Pump.fun SELL
                            analysis.update(self._decode_pump_sell(data_bytes))
                            
            except Exception as e:
                analysis["decode_error"] = str(e)
        
        return analysis
    
    def _decode_pump_buy(self, data_bytes: bytes) -> Dict[str, Any]:
        """Decode Pump.fun buy instruction"""
        try:
            if len(data_bytes) >= 24:
                amount = struct.unpack("<Q", data_bytes[8:16])[0]
                max_sol_cost = struct.unpack("<Q", data_bytes[16:24])[0]
                
                return {
                    "action": "BUY",
                    "amount_lamports": amount,
                    "amount_sol": amount / 1_000_000_000,
                    "max_sol_cost_lamports": max_sol_cost,
                    "max_sol_cost_sol": max_sol_cost / 1_000_000_000,
                    "slippage_tolerance": ((max_sol_cost - amount) / amount * 100) if amount > 0 else 0
                }
        except Exception as e:
            return {"decode_error": f"Buy decode failed: {e}"}
        
        return {}
    
    def _decode_pump_sell(self, data_bytes: bytes) -> Dict[str, Any]:
        """Decode Pump.fun sell instruction"""
        try:
            if len(data_bytes) >= 24:
                token_amount = struct.unpack("<Q", data_bytes[8:16])[0]
                min_sol_out = struct.unpack("<Q", data_bytes[16:24])[0]
                
                return {
                    "action": "SELL",
                    "token_amount": token_amount,
                    "min_sol_out_lamports": min_sol_out,
                    "min_sol_out_sol": min_sol_out / 1_000_000_000
                }
        except Exception as e:
            return {"decode_error": f"Sell decode failed: {e}"}
        
        return {}
    
    async def analyze_signature(self, signature: str) -> Dict[str, Any]:
        """Analyze a single transaction signature"""
        try:
            tx_data = await self.fetch_transaction(signature)
            return self.identify_trading_pattern(tx_data)
        except Exception as e:
            return {
                "signature": signature,
                "error": str(e),
                "success": False
            }
    
    async def analyze_multiple(self, signatures: List[str]) -> Dict[str, Any]:
        """Analyze multiple transaction signatures and provide summary"""
        
        results = []
        patterns = {}
        
        print(f"🔍 Analyzing {len(signatures)} transactions...\n")
        
        for i, signature in enumerate(signatures, 1):
            print(f"[{i}/{len(signatures)}] Analyzing: {signature[:16]}...")
            
            result = await self.analyze_signature(signature)
            results.append(result)
            
            if "error" not in result:
                method = result["pattern"]["method"]
                if method not in patterns:
                    patterns[method] = []
                patterns[method].append(signature[:8])
                
                print(f"   ✅ {method} ({result['pattern']['category']})")
                if result["pattern"]["instructions"]:
                    for inst in result["pattern"]["instructions"]:
                        if inst["type"] != "Unknown":
                            print(f"      📋 {inst['type']}")
            else:
                print(f"   ❌ Error: {result['error']}")
            
            print()
        
        # Summary
        summary = {
            "total_analyzed": len(signatures),
            "successful_analysis": len([r for r in results if "error" not in r]),
            "trading_patterns": patterns,
            "pattern_distribution": {method: len(sigs) for method, sigs in patterns.items()},
            "detailed_results": results
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print analysis summary"""
        
        print("📊 TRADING PATTERN ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Total transactions analyzed: {summary['total_analyzed']}")
        print(f"Successful analyses: {summary['successful_analysis']}")
        print()
        
        if summary["trading_patterns"]:
            print("🎯 TRADING METHODS IDENTIFIED:")
            for method, signatures in summary["trading_patterns"].items():
                count = len(signatures)
                percentage = (count / summary["successful_analysis"]) * 100
                print(f"   {method}: {count} transactions ({percentage:.1f}%)")
                print(f"      Examples: {', '.join(signatures[:3])}{'...' if len(signatures) > 3 else ''}")
                print()
        
        print("🔍 DETAILED PATTERN INSIGHTS:")
        method_details = {}
        for result in summary["detailed_results"]:
            if "error" not in result:
                method = result["pattern"]["method"]
                if method not in method_details:
                    method_details[method] = {
                        "category": result["pattern"]["category"],
                        "confidence": result["pattern"]["confidence"], 
                        "details": result["pattern"]["details"],
                        "examples": []
                    }
                
                # Add instruction examples
                for inst in result["pattern"]["instructions"]:
                    if inst["type"] != "Unknown":
                        if inst["type"] not in method_details[method]["examples"]:
                            method_details[method]["examples"].append(inst["type"])
        
        for method, details in method_details.items():
            print(f"   {method} ({details['category']}):")
            print(f"      Confidence: {details['confidence']}")
            print(f"      Details: {details['details']}")
            if details["examples"]:
                print(f"      Common instructions: {', '.join(details['examples'])}")
            print()

    async def find_non_pumpfun_transactions(self, wallet_address: str, limit: int = 50) -> List[str]:
        """Find transaction signatures for non-Pump.fun trades"""
        
        print(f"🔍 Scanning {limit} recent transactions for non-Pump.fun trades...")
        
        # First get all recent signatures for the wallet
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet_address, {"limit": limit}]
            })
            
            data = response.json()
            if "error" in data:
                print(f"❌ Error fetching signatures: {data['error']}")
                return []
            
            all_signatures = [sig["signature"] for sig in data["result"]]
        
        # Filter for non-Pump.fun transactions
        non_pumpfun_signatures = []
        processed = 0
        
        for signature in all_signatures:
            try:
                tx_data = await self.fetch_transaction(signature)
                if not tx_data or not tx_data.get("transaction"):
                    continue
                
                instructions = tx_data["transaction"]["message"]["instructions"]
                account_keys = tx_data["transaction"]["message"]["accountKeys"]
                program_ids = [account_keys[inst["programIdIndex"]] for inst in instructions]
                
                # Check if transaction has Pump.fun program
                has_pumpfun = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P" in program_ids
                
                # Check if transaction has other DEX programs (Jupiter, Raydium, etc.)
                dex_programs = [
                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter V6
                    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",  # Jupiter V4
                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium V4
                    "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",  # Raydium CPMM
                    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaV7grrKgrWqK",  # Raydium CLMM
                    "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj",  # Raydium LaunchLab
                    "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN",  # Meteora
                    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",  # Orca Whirlpool
                    "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",  # Orca v1
                ]
                
                has_other_dex = any(dex_id in program_ids for dex_id in dex_programs)
                
                # Include if it has other DEX but not Pump.fun (pure non-Pump.fun trade)
                if has_other_dex and not has_pumpfun:
                    non_pumpfun_signatures.append(signature)
                    print(f"✅ Found non-Pump.fun trade: {signature[:8]}...")
                
                processed += 1
                if processed % 10 == 0:
                    print(f"⏳ Processed {processed}/{len(all_signatures)} transactions...")
                
            except Exception as e:
                print(f"❌ Error checking {signature[:8]}: {e}")
                continue
        
        print(f"📊 Analysis complete: {len(non_pumpfun_signatures)} non-Pump.fun trades found")
        return non_pumpfun_signatures


async def main():
    """Main function for interactive analysis"""
    
    analyzer = TradingPatternAnalyzer()
    if len(sys.argv) > 2 and sys.argv[1] == "--dump-mev":
        signature = sys.argv[2]
        tx = await analyzer.fetch_transaction(signature)
        instructions = tx['transaction']['message']['instructions']
        account_keys = tx['transaction']['message']['accountKeys']
        print(f"\n🔍 DUMPING ADVANCED MEV BOT/ROUTER INSTRUCTIONS FOR {signature}")
        print("=" * 60)
        for i, inst in enumerate(instructions):
            prog = account_keys[inst['programIdIndex']]
            if prog == 'BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW':
                print(f"\nInstruction {i} (Advanced MEV Bot/Router):")
                print(f"  Data (base64): {inst['data']}")
                print(f"  Accounts:")
                for idx in inst['accounts']:
                    if idx < len(account_keys):
                        print(f"    {account_keys[idx]}")
                    else:
                        print(f"    [index {idx}] (out of range in accountKeys)")
        print("\nDone.")
        return
    elif len(sys.argv) > 1:
        signature = sys.argv[1]
        print("\n🔍 DETAILED SINGLE TRANSACTION ANALYSIS")
        print("=" * 50)
        result = await analyzer.analyze_signature(signature)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        print(f"Signature: {result['signature']}")
        print(f"Slot: {result['slot']}")
        print(f"Success: {'✅' if result['success'] else '❌'}")
        print(f"Fee: {result['fee_sol']:.9f} SOL")
        print()
        print(f"🎯 TRADING PATTERN:")
        pattern = result['pattern']
        print(f"   Method: {pattern['method']}")
        print(f"   Category: {pattern['category']}")
        print(f"   Confidence: {pattern['confidence']}")
        print(f"   Details: {pattern['details']}")
        print()
        print(f"📋 INSTRUCTIONS BREAKDOWN:")
        for inst in pattern['instructions']:
            print(f"   [{inst['index']}] {inst['program']}")
            print(f"       Type: {inst['type']}")
            print(f"       Data length: {inst['data_length']} bytes")
            print(f"       Accounts: {inst['account_count']}")
            if 'action' in inst:
                if inst['action'] == 'BUY':
                    print(f"       💰 BUY: {inst['amount_sol']:.6f} SOL (max: {inst['max_sol_cost_sol']:.6f} SOL)")
                    print(f"       📊 Slippage tolerance: {inst['slippage_tolerance']:.2f}%")
                elif inst['action'] == 'SELL':
                    print(f"       💰 SELL: {inst['token_amount']} tokens (min: {inst['min_sol_out_sol']:.6f} SOL)")
            print()
        print(f"🔧 PROGRAMS USED:")
        for program in result['programs_used']:
            print(f"   • {program}")
    else:
        print("Usage: python3 trading_pattern_analyzer.py <TRANSACTION_SIGNATURE>")
        print("       python3 trading_pattern_analyzer.py --dump-mev <TRANSACTION_SIGNATURE>")
        print("Example: python3 trading_pattern_analyzer.py 4dZhH9bnq9yodsxXbG86pqZsKQCH2kNDU3P46d7egNHbCdq8MNmNx5sJowXQk8dQK1HAeu8PHNTb6bZVSDZZoZ4c")
        print("         python3 trading_pattern_analyzer.py --dump-mev 4dZhH9bnq9yodsxXbG86pqZsKQCH2kNDU3P46d7egNHbCdq8MNmNx5sJowXQk8dQK1HAeu8PHNTb6bZVSDZZoZ4c")


if __name__ == "__main__":
    asyncio.run(main())
