#!/usr/bin/env python3
"""
Rate-Limited Meme Coin Compatibility Audit Tool
Analyzes target wallet trades with built-in rate limiting to avoid RPC errors
"""

import time
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RateLimitedSolanaClient:
    """Solana RPC client with built-in rate limiting"""
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com", requests_per_second: float = 2.0):
        self.rpc_url = rpc_url
        self.min_interval = 1.0 / requests_per_second  # Minimum time between requests
        self.last_request_time = 0
        
    async def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def get_signatures_for_address(self, address: str, limit: int = 50) -> List[Dict]:
        """Get transaction signatures for an address with rate limiting"""
        await self._wait_for_rate_limit()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                address,
                {"limit": limit}
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 429:
                        logger.warning("Rate limited! Waiting 30 seconds...")
                        await asyncio.sleep(30)
                        return await self.get_signatures_for_address(address, limit)
                    
                    data = await response.json()
                    return data.get('result', [])
        except Exception as e:
            logger.error(f"Error fetching signatures: {e}")
            return []
    
    async def get_transaction(self, signature: str) -> Optional[Dict]:
        """Get transaction details with rate limiting"""
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
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 429:
                        logger.warning("Rate limited! Waiting 30 seconds...")
                        await asyncio.sleep(30)
                        return await self.get_transaction(signature)
                    
                    data = await response.json()
                    return data.get('result')
        except Exception as e:
            logger.error(f"Error fetching transaction {signature}: {e}")
            return None

class MemeCompatibilityAnalyzer:
    """Analyzes meme coin trading compatibility with enhanced bot detection"""
    
    def __init__(self):
        self.client = RateLimitedSolanaClient(requests_per_second=1.5)  # Very conservative rate
        
        # Known DEX program IDs that our bot supports
        self.supported_programs = {
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
            
            # Jupiter
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
            
            # Raydium CPMM
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",
            
            # Raydium CLMM
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",
            
            # Orca
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
            
            # Phoenix
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY"
        }
        
        # Track analysis results
        self.analysis_results = {
            'total_trades': 0,
            'compatible_trades': 0,
            'incompatible_trades': 0,
            'meme_coin_trades': 0,
            'new_token_trades': 0,
            'incompatibility_reasons': {},
            'sample_tokens': []
        }
    
    def is_meme_token(self, transaction: Dict) -> bool:
        """Detect if transaction involves a meme token"""
        try:
            # Look for token transfers and new token creation patterns
            instructions = transaction.get('transaction', {}).get('message', {}).get('instructions', [])
            
            for instruction in instructions:
                program_id = instruction.get('programId', '')
                
                # Pump.fun transactions are typically meme tokens
                if program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    return True
                
                # Look for SPL token creation patterns
                if program_id == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                    # Check if this looks like a new token mint
                    return True
            
            return False
        except Exception:
            return False
    
    def analyze_transaction_compatibility(self, transaction: Dict) -> Tuple[bool, List[str]]:
        """Analyze if our bot can handle this transaction"""
        compatibility_issues = []
        
        try:
            instructions = transaction.get('transaction', {}).get('message', {}).get('instructions', [])
            
            if not instructions:
                compatibility_issues.append("no_instructions")
                return False, compatibility_issues
            
            supported_instruction_found = False
            
            for instruction in instructions:
                program_id = instruction.get('programId', '')
                
                if program_id in self.supported_programs:
                    supported_instruction_found = True
                    break
                else:
                    if program_id not in ['11111111111111111111111111111111', 'ComputeBudget111111111111111111111111111111']:
                        compatibility_issues.append(f"unsupported_program_{program_id}")
            
            if not supported_instruction_found:
                compatibility_issues.append("no_supported_programs")
                return False, compatibility_issues
            
            # Check for token mint extraction capability
            token_mints = self.extract_token_mints(transaction)
            if not token_mints:
                compatibility_issues.append("no_token_mints_found")
            
            return len(compatibility_issues) == 0, compatibility_issues
            
        except Exception as e:
            compatibility_issues.append(f"analysis_error_{str(e)}")
            return False, compatibility_issues
    
    def extract_token_mints(self, transaction: Dict) -> List[str]:
        """Extract token mints from transaction"""
        mints = set()
        
        try:
            # Look in pre/post token balances
            meta = transaction.get('meta', {})
            
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            
            for balance in pre_balances + post_balances:
                mint = balance.get('mint')
                if mint:
                    mints.add(mint)
            
            return list(mints)
        except Exception:
            return []
    
    async def analyze_wallet_trades(self, wallet_address: str, hours_back: int = 24) -> Dict:
        """Analyze recent trades from a target wallet"""
        logger.info(f"🎯 Analyzing trades from wallet: {wallet_address}")
        logger.info(f"⏰ Looking back {hours_back} hours")
        
        # Get signatures (limited to avoid rate limits)
        signatures = await self.client.get_signatures_for_address(wallet_address, limit=20)
        
        if not signatures:
            logger.warning(f"No signatures found for wallet {wallet_address}")
            return {}
        
        logger.info(f"📊 Found {len(signatures)} recent transactions")
        
        # Filter to last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_signatures = []
        
        for sig in signatures:
            if sig.get('blockTime'):
                tx_time = datetime.fromtimestamp(sig['blockTime'])
                if tx_time >= cutoff_time:
                    recent_signatures.append(sig)
        
        logger.info(f"⏰ {len(recent_signatures)} transactions in last {hours_back}h")
        
        # Analyze transactions (limit to prevent rate limiting)
        analyzed_count = 0
        max_analyze = min(10, len(recent_signatures))  # Limit analysis
        
        for sig_info in recent_signatures[:max_analyze]:
            signature = sig_info['signature']
            
            logger.info(f"🔍 Analyzing transaction {analyzed_count + 1}/{max_analyze}: {signature[:8]}...")
            
            transaction = await self.client.get_transaction(signature)
            if not transaction:
                continue
            
            analyzed_count += 1
            self.analysis_results['total_trades'] += 1
            
            # Check if it's a meme token trade
            is_meme = self.is_meme_token(transaction)
            if is_meme:
                self.analysis_results['meme_coin_trades'] += 1
            
            # Analyze compatibility
            is_compatible, issues = self.analyze_transaction_compatibility(transaction)
            
            if is_compatible:
                self.analysis_results['compatible_trades'] += 1
            else:
                self.analysis_results['incompatible_trades'] += 1
                
                # Track reasons for incompatibility
                for issue in issues:
                    if issue not in self.analysis_results['incompatibility_reasons']:
                        self.analysis_results['incompatibility_reasons'][issue] = 0
                    self.analysis_results['incompatibility_reasons'][issue] += 1
            
            # Extract token information for sample
            token_mints = self.extract_token_mints(transaction)
            if token_mints and len(self.analysis_results['sample_tokens']) < 5:
                self.analysis_results['sample_tokens'].append({
                    'signature': signature,
                    'is_meme': is_meme,
                    'is_compatible': is_compatible,
                    'token_mints': token_mints,
                    'issues': issues
                })
        
        return self.analysis_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive compatibility report"""
        results = self.analysis_results
        
        if results['total_trades'] == 0:
            return "❌ No trades analyzed. Check wallet addresses and RPC connectivity."
        
        compatibility_rate = results['compatible_trades'] / results['total_trades']
        
        report = f"""
🎯 MEME COIN COMPATIBILITY ANALYSIS REPORT
{'=' * 70}

📊 OVERALL PERFORMANCE:
   Total Trades Analyzed: {results['total_trades']}
   Compatible Trades: {results['compatible_trades']} ({compatibility_rate:.1%})
   Incompatible Trades: {results['incompatible_trades']} ({1-compatibility_rate:.1%})

🎪 MEME COIN ANALYSIS:
   Meme Coin Trades Detected: {results['meme_coin_trades']}
   Meme Compatibility Rate: {results['meme_coin_trades']/results['total_trades']:.1%} of all trades

❌ INCOMPATIBILITY BREAKDOWN:
"""
        
        for reason, count in results['incompatibility_reasons'].items():
            percentage = (count / results['total_trades']) * 100
            report += f"   - {reason}: {count} ({percentage:.1f}%)\n"
        
        report += f"""
🔍 SAMPLE TRANSACTIONS:
"""
        
        for i, sample in enumerate(results['sample_tokens'][:3], 1):
            status = "✅ Compatible" if sample['is_compatible'] else "❌ Incompatible"
            meme_status = "🎪 Meme Token" if sample['is_meme'] else "📊 Regular Token"
            
            report += f"""   {i}. Transaction: {sample['signature'][:16]}...
      Status: {status}
      Type: {meme_status}
      Token Mints: {len(sample['token_mints'])} found
      Issues: {', '.join(sample['issues']) if sample['issues'] else 'None'}

"""
        
        # Assessment
        if compatibility_rate >= 0.9:
            assessment = "🎉 EXCELLENT! Your bot is ready for meme coin copy trading!"
        elif compatibility_rate >= 0.8:
            assessment = "📈 GOOD! Strong compatibility with minor optimizations needed"
        else:
            assessment = "⚠️ NEEDS IMPROVEMENT! Significant compatibility gaps detected"
        
        report += f"""
🎯 BOT READINESS ASSESSMENT:
   Compatibility Score: {compatibility_rate:.1%}
   {assessment}

🚀 RECOMMENDATIONS:
   1. Address top incompatibility reasons listed above
   2. Enhance support for detected unsupported programs
   3. Improve token mint extraction for edge cases
   4. Test with enhanced transaction builder for complex scenarios
   
💡 BOTTOM LINE:
   Your bot would successfully copy {compatibility_rate:.0%} of analyzed target trades
   Focus on addressing the top 2-3 incompatibility reasons for maximum improvement
"""
        
        return report

async def main():
    """Main analysis function"""
    # Target wallets from config
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCXQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    ]
    
    analyzer = MemeCompatibilityAnalyzer()
    
    print("🚀 Starting Rate-Limited Meme Coin Compatibility Analysis")
    print("=" * 70)
    print("⚠️  Using conservative rate limiting to avoid RPC errors")
    print("📊 This will take a few minutes to complete safely")
    print()
    
    # Analyze each wallet
    for i, wallet in enumerate(target_wallets, 1):
        print(f"🎯 Analyzing Wallet {i}/{len(target_wallets)}")
        print(f"   Address: {wallet}")
        print()
        
        try:
            await analyzer.analyze_wallet_trades(wallet, hours_back=24)
            print(f"✅ Completed analysis for wallet {i}")
        except Exception as e:
            print(f"❌ Error analyzing wallet {i}: {e}")
        
        print()
    
    # Generate and display report
    print("\n" + "=" * 70)
    print(analyzer.generate_report())
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meme_compatibility_analysis_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(analyzer.analysis_results, f, indent=2)
    
    print(f"\n📁 Results saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
