#!/usr/bin/env python3
"""
Enhanced Program ID Detection Tool
Identifies the exact DEX programs being used by target wallets
"""

import time
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProgramIDDetector:
    """Detects and analyzes program IDs from target wallet transactions"""
    
    def __init__(self):
        self.rpc_url = "https://api.mainnet-beta.solana.com"
        self.min_interval = 1.0  # 1 second between requests
        self.last_request_time = 0
        
        # Our currently supported program IDs
        self.supported_programs = {
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",  # Jupiter v4
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter v6
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium CPMM
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",  # Raydium CPMM v2
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",  # Raydium CLMM
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",  # Orca v1
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",  # Orca Whirlpool
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY"   # Phoenix
        }
        
        # Track all discovered program IDs
        self.discovered_programs = {}
        self.transaction_count = 0
        
    async def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def get_signatures_for_address(self, address: str, limit: int = 10) -> List[Dict]:
        """Get transaction signatures for an address"""
        await self._wait_for_rate_limit()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [address, {"limit": limit}]
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 429:
                        logger.warning("Rate limited! Waiting 60 seconds...")
                        await asyncio.sleep(60)
                        return await self.get_signatures_for_address(address, limit)
                    
                    data = await response.json()
                    return data.get('result', [])
        except Exception as e:
            logger.error(f"Error fetching signatures: {e}")
            return []
    
    async def get_transaction(self, signature: str) -> Optional[Dict]:
        """Get transaction details"""
        await self._wait_for_rate_limit()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {"encoding": "json", "maxSupportedTransactionVersion": 0}
            ]
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 429:
                        logger.warning("Rate limited! Waiting 60 seconds...")
                        await asyncio.sleep(60)
                        return await self.get_transaction(signature)
                    
                    data = await response.json()
                    return data.get('result')
        except Exception as e:
            logger.error(f"Error fetching transaction {signature}: {e}")
            return None
    
    def analyze_transaction_programs(self, transaction: Dict) -> Set[str]:
        """Extract all program IDs from a transaction"""
        program_ids = set()
        
        try:
            # Get instructions from transaction
            instructions = transaction.get('transaction', {}).get('message', {}).get('instructions', [])
            
            for instruction in instructions:
                program_id = instruction.get('programId', '')
                if program_id:
                    program_ids.add(program_id)
                    
                    # Track program usage
                    if program_id not in self.discovered_programs:
                        self.discovered_programs[program_id] = {
                            'count': 0,
                            'supported': program_id in self.supported_programs,
                            'first_seen': datetime.now().isoformat()
                        }
                    self.discovered_programs[program_id]['count'] += 1
            
            # Also check inner instructions if present
            meta = transaction.get('meta', {})
            inner_instructions = meta.get('innerInstructions', [])
            
            for inner_group in inner_instructions:
                for inner_instruction in inner_group.get('instructions', []):
                    program_id = inner_instruction.get('programId', '')
                    if program_id:
                        program_ids.add(program_id)
                        
                        if program_id not in self.discovered_programs:
                            self.discovered_programs[program_id] = {
                                'count': 0,
                                'supported': program_id in self.supported_programs,
                                'first_seen': datetime.now().isoformat()
                            }
                        self.discovered_programs[program_id]['count'] += 1
            
        except Exception as e:
            logger.error(f"Error analyzing transaction programs: {e}")
        
        return program_ids
    
    async def analyze_wallet(self, wallet_address: str) -> Dict:
        """Analyze a single wallet's recent transactions"""
        logger.info(f"🔍 Analyzing wallet: {wallet_address}")
        
        # Get recent signatures (limited to avoid rate limits)
        signatures = await self.get_signatures_for_address(wallet_address, limit=5)
        
        if not signatures:
            logger.warning(f"No signatures found for {wallet_address}")
            return {}
        
        logger.info(f"📊 Found {len(signatures)} recent transactions")
        
        # Analyze each transaction
        for i, sig_info in enumerate(signatures):
            signature = sig_info['signature']
            logger.info(f"🔍 Analyzing transaction {i+1}/{len(signatures)}: {signature[:16]}...")
            
            transaction = await self.get_transaction(signature)
            if transaction:
                self.transaction_count += 1
                programs = self.analyze_transaction_programs(transaction)
                logger.info(f"   Found {len(programs)} unique program IDs")
        
        return self.discovered_programs
    
    def generate_program_report(self) -> str:
        """Generate a detailed program ID compatibility report"""
        
        if not self.discovered_programs:
            return "❌ No program IDs discovered. Check wallet activity and RPC connectivity."
        
        # Sort programs by usage count
        sorted_programs = sorted(
            self.discovered_programs.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        supported_count = sum(1 for _, info in self.discovered_programs.items() if info['supported'])
        unsupported_count = len(self.discovered_programs) - supported_count
        
        report = f"""
🎯 PROGRAM ID COMPATIBILITY ANALYSIS
{'=' * 70}

📊 DISCOVERY SUMMARY:
   Total Transactions Analyzed: {self.transaction_count}
   Unique Program IDs Found: {len(self.discovered_programs)}
   Supported Programs: {supported_count}
   Unsupported Programs: {unsupported_count}
   
   Compatibility Rate: {supported_count/len(self.discovered_programs)*100:.1f}%

🔍 DETAILED PROGRAM ANALYSIS:
"""
        
        for program_id, info in sorted_programs:
            status = "✅ SUPPORTED" if info['supported'] else "❌ UNSUPPORTED"
            usage_percentage = (info['count'] / self.transaction_count) * 100
            
            report += f"""
   Program ID: {program_id}
   Status: {status}
   Usage Count: {info['count']} ({usage_percentage:.1f}% of transactions)
   First Seen: {info['first_seen']}
"""
        
        # Identify critical missing programs
        unsupported_programs = [
            (pid, info) for pid, info in sorted_programs 
            if not info['supported']
        ]
        
        if unsupported_programs:
            report += f"""
🚨 CRITICAL MISSING PROGRAMS:
   The following programs are heavily used but NOT supported by your bot:
"""
            for program_id, info in unsupported_programs[:5]:  # Top 5 unsupported
                report += f"""
   🔴 {program_id}
      Usage: {info['count']} times ({info['count']/self.transaction_count*100:.1f}% of transactions)
      Impact: HIGH - Add support to significantly improve compatibility
"""
        
        # Recommendations
        compatibility_rate = supported_count / len(self.discovered_programs)
        
        if compatibility_rate >= 0.8:
            assessment = "🎉 EXCELLENT! Most programs are supported"
            recommendation = "Add support for the few remaining unsupported programs"
        elif compatibility_rate >= 0.6:
            assessment = "📈 GOOD! Majority of programs supported"
            recommendation = "Focus on adding the top 2-3 unsupported programs"
        else:
            assessment = "⚠️ NEEDS WORK! Many unsupported programs detected"
            recommendation = "Significant executor development needed for full compatibility"
        
        report += f"""
🎯 COMPATIBILITY ASSESSMENT:
   {assessment}
   
🚀 RECOMMENDED ACTIONS:
   1. {recommendation}
   2. Implement executors for the top unsupported program IDs
   3. Add fallback strategies for unrecognized programs
   4. Test with enhanced transaction builder for complex scenarios

💡 IMPLEMENTATION PRIORITY:
   Focus on the unsupported programs with highest usage counts first
   This will provide the maximum improvement in compatibility rates
"""
        
        return report

async def main():
    """Main analysis function"""
    # Target wallets
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCXQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    ]
    
    detector = ProgramIDDetector()
    
    print("🚀 Starting Program ID Detection Analysis")
    print("=" * 70)
    print("🔍 This will identify the exact DEX programs your target wallets use")
    print("⚠️  Using conservative rate limiting to avoid RPC errors")
    print()
    
    # Analyze each wallet
    for i, wallet in enumerate(target_wallets, 1):
        print(f"🎯 Analyzing Wallet {i}/{len(target_wallets)}")
        print(f"   Address: {wallet}")
        
        try:
            await detector.analyze_wallet(wallet)
            print(f"✅ Completed analysis for wallet {i}")
        except Exception as e:
            print(f"❌ Error analyzing wallet {i}: {e}")
        
        print()
    
    # Generate and display report
    print("\n" + "=" * 70)
    print(detector.generate_program_report())
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"program_id_analysis_{timestamp}.json"
    
    analysis_data = {
        'timestamp': timestamp,
        'transaction_count': detector.transaction_count,
        'discovered_programs': detector.discovered_programs,
        'supported_programs': list(detector.supported_programs)
    }
    
    with open(filename, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
