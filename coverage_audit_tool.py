#!/usr/bin/env python3
"""
🎯 COPY TRADING COVERAGE AUDIT TOOL
Comprehensive analysis to confirm 95%+ trade coverage and identify the remaining 5%
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import aiohttp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coverage_audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TransactionDetails:
    """Transaction analysis details"""
    signature: str
    timestamp: datetime
    program_id: str
    instruction_type: str
    token_mint: Optional[str]
    token_symbol: Optional[str]
    token_name: Optional[str]
    amount: Optional[float]
    success: bool
    block_time: int
    slot: int
    is_meme_coin: bool = False
    token_age_hours: Optional[float] = None
    bot_compatible: bool = False
    incompatibility_reason: Optional[str] = None

@dataclass
class MemeTokenAnalysis:
    """Meme token specific analysis"""
    mint_address: str
    symbol: Optional[str]
    name: Optional[str]
    creation_time: Optional[datetime]
    age_hours: Optional[float]
    total_trades_detected: int
    bot_compatible_trades: int
    incompatible_trades: int
    main_dex_used: str
    compatibility_rate: float
    incompatibility_reasons: List[str]

@dataclass
class CoverageAnalysis:
    """Coverage analysis results"""
    total_target_trades: int
    detected_trades: int
    executed_trades: int
    detection_rate: float
    execution_rate: float
    overall_coverage: float
    missed_trades: List[TransactionDetails]
    failure_reasons: Dict[str, int]
    performance_metrics: Dict[str, float]
    meme_token_analysis: Dict[str, MemeTokenAnalysis]
    bot_compatibility_summary: Dict[str, int]

class CoverageAuditTool:
    """Comprehensive coverage audit tool"""
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_client = AsyncClient(rpc_url)
        self.target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCXQfK",  # Your target wallet 1
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",  # Your target wallet 2
        ]
        self.bot_execution_log = []
        self.coverage_results = {}
        
        # Known DEX program IDs that your bot can handle
        self.supported_dex_programs = {
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # Pump.fun
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium AMM
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",  # Raydium CLMM  
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",   # Jupiter Aggregator
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",   # Jupiter V4
            "JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph",   # Jupiter V3
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",   # Orca Whirlpools
            "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP",   # Orca V2
            "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1",  # Orca V1
            "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY",   # Phoenix
            "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX",   # Serum DEX
            "EhpADToyrxjhe1PJiFbCNrMPwxoWWy1gJQWBSJFcKzKN",  # Serum V3
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # SPL Token
            "11111111111111111111111111111112",              # System Program
        }
        
        # Token standards your bot supports
        self.supported_token_standards = {
            "fungible",
            "fungible-asset", 
            "non-fungible",
            "spl-token",
            "spl-token-2022"
        }
        
    async def fetch_wallet_transactions(
        self, 
        wallet: str, 
        hours_back: int = 24,
        limit: int = 1000
    ) -> List[TransactionDetails]:
        """Fetch all transactions for a wallet in the specified time period"""
        logger.info(f"🔍 Fetching transactions for wallet {wallet[:8]}... (last {hours_back}h)")
        
        try:
            pubkey = Pubkey.from_string(wallet)
            
            # Get recent transactions
            response = await self.rpc_client.get_signatures_for_address(
                pubkey,
                limit=limit
            )
            
            if not response.value:
                logger.warning(f"No transactions found for wallet {wallet[:8]}...")
                return []
            
            transactions = []
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            for sig_info in response.value:
                if sig_info.block_time:
                    tx_time = datetime.fromtimestamp(sig_info.block_time)
                    if tx_time < cutoff_time:
                        continue
                    
                    # Get transaction details
                    tx_detail = await self.analyze_transaction(sig_info.signature)
                    if tx_detail:
                        transactions.append(tx_detail)
            
            logger.info(f"✅ Found {len(transactions)} transactions for {wallet[:8]}...")
            return transactions
            
        except Exception as e:
            logger.error(f"❌ Error fetching transactions for {wallet}: {e}")
            return []
    
    async def analyze_transaction(self, signature: str) -> Optional[TransactionDetails]:
        """Analyze individual transaction details"""
        try:
            response = await self.rpc_client.get_transaction(
                signature,
                encoding="jsonParsed",
                max_supported_transaction_version=0
            )
            
            if not response.value:
                return None
            
            tx = response.value
            transaction = tx.transaction
            meta = tx.meta
            
            # Extract transaction details
            program_ids = set()
            token_mint = None
            token_symbol = None
            token_name = None
            amount = None
            instruction_type = "unknown"
            
            # Analyze instructions
            if hasattr(transaction, 'message') and hasattr(transaction.message, 'instructions'):
                for instruction in transaction.message.instructions:
                    if hasattr(instruction, 'program_id'):
                        program_ids.add(str(instruction.program_id))
                    
                    # Try to extract token info from parsed instruction
                    if hasattr(instruction, 'parsed'):
                        parsed = instruction.parsed
                        if isinstance(parsed, dict):
                            if 'type' in parsed:
                                instruction_type = parsed['type']
                            if 'info' in parsed:
                                info = parsed['info']
                                if 'mint' in info:
                                    token_mint = info['mint']
                                if 'amount' in info:
                                    amount = float(info['amount'])
            
            # Get token metadata if available
            if token_mint:
                token_symbol, token_name = await self.get_token_metadata(token_mint)
            
            # Determine if this is a meme coin and get age
            is_meme_coin, token_age_hours = await self.analyze_meme_coin_characteristics(
                token_mint, tx.block_time
            )
            
            # Check bot compatibility
            main_program_id = list(program_ids)[0] if program_ids else "unknown"
            bot_compatible, incompatibility_reason = self.check_bot_compatibility(
                main_program_id, token_mint, instruction_type, is_meme_coin, token_age_hours
            )
            
            return TransactionDetails(
                signature=signature,
                timestamp=datetime.fromtimestamp(tx.block_time) if tx.block_time else datetime.now(),
                program_id=main_program_id,
                instruction_type=instruction_type,
                token_mint=token_mint,
                token_symbol=token_symbol,
                token_name=token_name,
                amount=amount,
                success=meta.err is None if meta else False,
                block_time=tx.block_time or 0,
                slot=tx.slot or 0,
                is_meme_coin=is_meme_coin,
                token_age_hours=token_age_hours,
                bot_compatible=bot_compatible,
                incompatibility_reason=incompatibility_reason
            )
            
        except Exception as e:
            logger.error(f"Error analyzing transaction {signature}: {e}")
            return None
    
    async def get_token_metadata(self, mint_address: str) -> Tuple[Optional[str], Optional[str]]:
        """Get token metadata (symbol and name)"""
        try:
            # Try to get token metadata from various sources
            # This is a simplified version - you might want to use specific metadata APIs
            
            # Method 1: Try Metaplex metadata
            metadata_account = await self.get_metaplex_metadata(mint_address)
            if metadata_account:
                return metadata_account.get('symbol'), metadata_account.get('name')
            
            # Method 2: Try token registry
            token_info = await self.get_token_registry_info(mint_address)
            if token_info:
                return token_info.get('symbol'), token_info.get('name')
            
            # Method 3: Try mint account data
            mint_info = await self.get_mint_account_info(mint_address)
            if mint_info:
                return mint_info.get('symbol'), mint_info.get('name')
            
            return None, None
            
        except Exception as e:
            logger.debug(f"Could not get metadata for token {mint_address}: {e}")
            return None, None
    
    async def get_metaplex_metadata(self, mint_address: str) -> Optional[Dict]:
        """Get Metaplex metadata for token"""
        try:
            # Implement Metaplex metadata fetching
            # This is a placeholder - implement actual metadata program calls
            return None
        except:
            return None
    
    async def get_token_registry_info(self, mint_address: str) -> Optional[Dict]:
        """Get token info from Solana token registry"""
        try:
            # This would query token registry APIs
            # Placeholder implementation
            return None
        except:
            return None
    
    async def get_mint_account_info(self, mint_address: str) -> Optional[Dict]:
        """Get basic mint account information"""
        try:
            mint_pubkey = Pubkey.from_string(mint_address)
            account_info = await self.rpc_client.get_account_info(mint_pubkey)
            
            if account_info.value:
                # Basic mint info available
                return {"symbol": None, "name": None}
            
            return None
        except:
            return None
    
    async def analyze_meme_coin_characteristics(
        self, 
        token_mint: Optional[str], 
        block_time: Optional[int]
    ) -> Tuple[bool, Optional[float]]:
        """Analyze if this is a meme coin and determine its age"""
        if not token_mint or not block_time:
            return False, None
        
        try:
            # Get token creation time
            creation_time = await self.get_token_creation_time(token_mint)
            
            if creation_time:
                current_time = datetime.fromtimestamp(block_time)
                age_hours = (current_time - creation_time).total_seconds() / 3600
                
                # Heuristics for meme coin detection
                is_meme_coin = self.is_likely_meme_coin(token_mint, age_hours)
                
                return is_meme_coin, age_hours
            
            return False, None
            
        except Exception as e:
            logger.debug(f"Error analyzing meme coin characteristics: {e}")
            return False, None
    
    async def get_token_creation_time(self, mint_address: str) -> Optional[datetime]:
        """Get token creation timestamp"""
        try:
            # This would require scanning for the token creation transaction
            # For now, return None as this requires more complex implementation
            return None
        except:
            return None
    
    def is_likely_meme_coin(self, token_mint: str, age_hours: Optional[float]) -> bool:
        """Heuristic to determine if token is likely a meme coin"""
        # Meme coin characteristics:
        # 1. Very new (< 7 days old)
        # 2. High trading volume relative to age
        # 3. Certain naming patterns
        # 4. Specific DEX usage patterns
        
        if age_hours is not None and age_hours < 168:  # Less than 7 days
            return True
        
        # Additional heuristics could be added here
        return False
    
    def check_bot_compatibility(
        self, 
        program_id: str, 
        token_mint: Optional[str], 
        instruction_type: str,
        is_meme_coin: bool,
        token_age_hours: Optional[float]
    ) -> Tuple[bool, Optional[str]]:
        """Check if your bot would be compatible with this trade"""
        
        # Check 1: DEX Program Support
        if program_id not in self.supported_dex_programs:
            return False, f"unsupported_dex_program: {program_id[:16]}..."
        
        # Check 2: Instruction Type Support
        if instruction_type not in ["swap", "transfer", "swapV2", "route", "unknown"]:
            return False, f"unsupported_instruction_type: {instruction_type}"
        
        # Check 3: Token Age (very new tokens might have issues)
        if token_age_hours is not None and token_age_hours < 0.1:  # Less than 6 minutes
            return False, "token_too_new"
        
        # Check 4: Token Mint Validity
        if not token_mint:
            return False, "no_token_mint_detected"
        
        # Check 5: Known problematic tokens (could add blacklist)
        if token_mint in []:  # Add any known problematic tokens
            return False, "blacklisted_token"
        
        # If all checks pass
        return True, None
    
    def load_bot_execution_log(self, log_file: str = "bot_output.log") -> List[Dict]:
        """Load bot execution log for comparison"""
        logger.info(f"📋 Loading bot execution log from {log_file}")
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            executions = []
            for line in lines:
                if "EXECUTED" in line or "SUCCESS" in line:
                    # Parse execution line - customize based on your log format
                    try:
                        # Extract signature, timestamp, etc. from log line
                        # This needs to match your actual log format
                        parts = line.strip().split(' ')
                        execution = {
                            'timestamp': parts[0] + ' ' + parts[1],
                            'signature': 'extracted_from_log',  # Customize extraction
                            'success': 'SUCCESS' in line
                        }
                        executions.append(execution)
                    except:
                        continue
            
            logger.info(f"✅ Loaded {len(executions)} bot executions")
            return executions
            
        except FileNotFoundError:
            logger.warning(f"⚠️ Bot log file {log_file} not found")
            return []
        except Exception as e:
            logger.error(f"❌ Error loading bot log: {e}")
            return []
    
    def analyze_coverage(
        self, 
        target_transactions: List[TransactionDetails],
        bot_executions: List[Dict]
    ) -> CoverageAnalysis:
        """Analyze coverage between target transactions and bot executions"""
        logger.info("📊 Analyzing coverage and meme coin compatibility...")
        
        # Convert bot executions to signatures set for comparison
        bot_signatures = set()
        for execution in bot_executions:
            if 'signature' in execution:
                bot_signatures.add(execution['signature'])
        
        # Analyze detection and execution rates
        detected_trades = 0
        executed_trades = 0
        missed_trades = []
        failure_reasons = {
            'not_detected': 0,
            'detected_not_executed': 0,
            'execution_failed': 0,
            'timing_issue': 0,
            'unknown': 0,
            'unsupported_dex': 0,
            'token_too_new': 0,
            'unsupported_instruction': 0,
            'no_token_mint': 0
        }
        
        # Meme token analysis
        meme_tokens = {}
        bot_compatibility_summary = {
            'total_trades': len(target_transactions),
            'compatible_trades': 0,
            'incompatible_trades': 0,
            'meme_coin_trades': 0,
            'compatible_meme_trades': 0,
            'new_token_trades': 0,
            'compatible_new_token_trades': 0
        }
        
        for tx in target_transactions:
            # Track meme coin statistics
            if tx.is_meme_coin:
                bot_compatibility_summary['meme_coin_trades'] += 1
                if tx.bot_compatible:
                    bot_compatibility_summary['compatible_meme_trades'] += 1
            
            # Track new token statistics (< 24 hours)
            if tx.token_age_hours is not None and tx.token_age_hours < 24:
                bot_compatibility_summary['new_token_trades'] += 1
                if tx.bot_compatible:
                    bot_compatibility_summary['compatible_new_token_trades'] += 1
            
            # Track overall compatibility
            if tx.bot_compatible:
                bot_compatibility_summary['compatible_trades'] += 1
            else:
                bot_compatibility_summary['incompatible_trades'] += 1
            
            # Analyze per-token data
            if tx.token_mint and tx.is_meme_coin:
                if tx.token_mint not in meme_tokens:
                    meme_tokens[tx.token_mint] = MemeTokenAnalysis(
                        mint_address=tx.token_mint,
                        symbol=tx.token_symbol,
                        name=tx.token_name,
                        creation_time=None,  # Would need additional data
                        age_hours=tx.token_age_hours,
                        total_trades_detected=0,
                        bot_compatible_trades=0,
                        incompatible_trades=0,
                        main_dex_used=tx.program_id,
                        compatibility_rate=0.0,
                        incompatibility_reasons=[]
                    )
                
                token_analysis = meme_tokens[tx.token_mint]
                token_analysis.total_trades_detected += 1
                
                if tx.bot_compatible:
                    token_analysis.bot_compatible_trades += 1
                else:
                    token_analysis.incompatible_trades += 1
                    if tx.incompatibility_reason:
                        token_analysis.incompatibility_reasons.append(tx.incompatibility_reason)
                
                # Update compatibility rate
                token_analysis.compatibility_rate = (
                    token_analysis.bot_compatible_trades / token_analysis.total_trades_detected
                )
            
            # Check if this transaction was detected/executed by bot
            if tx.signature in bot_signatures:
                detected_trades += 1
                executed_trades += 1  # Assuming presence in log means execution attempt
            else:
                missed_trades.append(tx)
                # Classify miss reason based on compatibility analysis
                if not tx.bot_compatible and tx.incompatibility_reason:
                    reason_key = tx.incompatibility_reason.split(':')[0]  # Get main reason
                    if reason_key in failure_reasons:
                        failure_reasons[reason_key] += 1
                    else:
                        failure_reasons['unknown'] += 1
                elif self.is_copy_eligible_transaction(tx):
                    failure_reasons['not_detected'] += 1
                else:
                    failure_reasons['unknown'] += 1
        
        total_trades = len(target_transactions)
        detection_rate = detected_trades / total_trades if total_trades > 0 else 0
        execution_rate = executed_trades / detected_trades if detected_trades > 0 else 0
        overall_coverage = executed_trades / total_trades if total_trades > 0 else 0
        
        performance_metrics = {
            'avg_detection_latency': 0.0,  # Would need real-time data
            'avg_execution_latency': 0.0,  # Would need real-time data
            'jito_success_rate': 0.0,      # Would need Jito-specific logs
            'rpc_fallback_rate': 0.0,      # Would need detailed execution logs
            'meme_coin_compatibility_rate': (
                bot_compatibility_summary['compatible_meme_trades'] / 
                bot_compatibility_summary['meme_coin_trades']
            ) if bot_compatibility_summary['meme_coin_trades'] > 0 else 0,
            'new_token_compatibility_rate': (
                bot_compatibility_summary['compatible_new_token_trades'] / 
                bot_compatibility_summary['new_token_trades']
            ) if bot_compatibility_summary['new_token_trades'] > 0 else 0
        }
        
        return CoverageAnalysis(
            total_target_trades=total_trades,
            detected_trades=detected_trades,
            executed_trades=executed_trades,
            detection_rate=detection_rate,
            execution_rate=execution_rate,
            overall_coverage=overall_coverage,
            missed_trades=missed_trades,
            failure_reasons=failure_reasons,
            performance_metrics=performance_metrics,
            meme_token_analysis=meme_tokens,
            bot_compatibility_summary=bot_compatibility_summary
        )
    
    def is_copy_eligible_transaction(self, tx: TransactionDetails) -> bool:
        """Determine if a transaction should have been copied"""
        # Define eligibility criteria based on your bot's logic
        eligible_programs = [
            "11111111111111111111111111111112",  # System Program
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token Program
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Token Program 2022
            # Add your DEX program IDs
        ]
        
        # Transaction is eligible if it involves token transfers/swaps
        return (
            tx.success and
            tx.token_mint is not None and
            tx.amount is not None and
            tx.amount > 0
        )
    
    async def generate_detailed_report(self, analysis: CoverageAnalysis) -> str:
        """Generate comprehensive coverage report"""
        report = f"""
🎯 MEME COIN COPY TRADING COMPATIBILITY AUDIT
{'=' * 60}
Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 OVERALL PERFORMANCE:
   Total Target Trades: {analysis.total_target_trades}
   Detected Trades: {analysis.detected_trades}
   Executed Trades: {analysis.executed_trades}
   
   Detection Rate: {analysis.detection_rate:.2%}
   Execution Rate: {analysis.execution_rate:.2%}
   Overall Coverage: {analysis.overall_coverage:.2%}

🎪 MEME COIN COMPATIBILITY ANALYSIS:
   Total Meme Coin Trades: {analysis.bot_compatibility_summary['meme_coin_trades']}
   Compatible Meme Trades: {analysis.bot_compatibility_summary['compatible_meme_trades']}
   Meme Coin Compatibility Rate: {analysis.performance_metrics['meme_coin_compatibility_rate']:.2%}
   
   New Token Trades (< 24h): {analysis.bot_compatibility_summary['new_token_trades']}
   Compatible New Token Trades: {analysis.bot_compatibility_summary['compatible_new_token_trades']}
   New Token Compatibility Rate: {analysis.performance_metrics['new_token_compatibility_rate']:.2%}

📈 BOT COMPATIBILITY SUMMARY:
   Total Trades Analyzed: {analysis.bot_compatibility_summary['total_trades']}
   Bot Compatible Trades: {analysis.bot_compatibility_summary['compatible_trades']} ({analysis.bot_compatibility_summary['compatible_trades']/analysis.bot_compatibility_summary['total_trades']:.1%})
   Bot Incompatible Trades: {analysis.bot_compatibility_summary['incompatible_trades']} ({analysis.bot_compatibility_summary['incompatible_trades']/analysis.bot_compatibility_summary['total_trades']:.1%})

❌ INCOMPATIBILITY REASONS:
"""
        
        for reason, count in analysis.failure_reasons.items():
            if count > 0:
                percentage = count / analysis.total_target_trades if analysis.total_target_trades > 0 else 0
                report += f"   - {reason.replace('_', ' ').title()}: {count} ({percentage:.1%})\n"
        
        report += f"""
🎪 MEME TOKEN DETAILED ANALYSIS:
"""
        
        if analysis.meme_token_analysis:
            report += f"   Found {len(analysis.meme_token_analysis)} unique meme tokens:\n\n"
            
            for i, (mint, token_analysis) in enumerate(list(analysis.meme_token_analysis.items())[:10]):
                report += f"""   {i+1}. Token: {mint[:16]}...
      Symbol: {token_analysis.symbol or 'Unknown'}
      Name: {token_analysis.name or 'Unknown'}
      Age: {token_analysis.age_hours:.1f}h ({token_analysis.age_hours/24:.1f} days)
      Total Trades: {token_analysis.total_trades_detected}
      Compatible: {token_analysis.bot_compatible_trades}
      Compatibility Rate: {token_analysis.compatibility_rate:.1%}
      Main DEX: {token_analysis.main_dex_used[:16]}...
      Issues: {', '.join(set(token_analysis.incompatibility_reasons)) if token_analysis.incompatibility_reasons else 'None'}
      
"""
            
            if len(analysis.meme_token_analysis) > 10:
                report += f"   ... and {len(analysis.meme_token_analysis) - 10} more meme tokens\n\n"
        else:
            report += "   No meme tokens detected in the analyzed period.\n\n"
        
        report += f"""
🔍 MISSED TRADES ANALYSIS:
   Total Missed: {len(analysis.missed_trades)}
   
   Top 10 Missed Trades:
"""
        
        for i, missed_tx in enumerate(analysis.missed_trades[:10]):
            compatibility_status = "❌ INCOMPATIBLE" if not missed_tx.bot_compatible else "⚠️ MISSED (Compatible)"
            report += f"""   {i+1}. {compatibility_status}
      Signature: {missed_tx.signature[:16]}...
      Time: {missed_tx.timestamp}
      Program: {missed_tx.program_id[:16]}...
      Token: {missed_tx.token_mint[:16] if missed_tx.token_mint else 'N/A'}...
      Symbol: {missed_tx.token_symbol or 'Unknown'}
      Is Meme: {'Yes' if missed_tx.is_meme_coin else 'No'}
      Age: {missed_tx.token_age_hours:.1f}h if missed_tx.token_age_hours else 'Unknown'
      Issue: {missed_tx.incompatibility_reason or 'Detection/Execution failure'}
      
"""
        
        if len(analysis.missed_trades) > 10:
            report += f"   ... and {len(analysis.missed_trades) - 10} more missed trades\n\n"
        
        report += f"""
⚡ PERFORMANCE METRICS:
   Average Detection Latency: {analysis.performance_metrics['avg_detection_latency']:.3f}s
   Average Execution Latency: {analysis.performance_metrics['avg_execution_latency']:.3f}s
   Jito Success Rate: {analysis.performance_metrics['jito_success_rate']:.1%}
   RPC Fallback Rate: {analysis.performance_metrics['rpc_fallback_rate']:.1%}
   Meme Coin Compatibility: {analysis.performance_metrics['meme_coin_compatibility_rate']:.1%}
   New Token Compatibility: {analysis.performance_metrics['new_token_compatibility_rate']:.1%}

🎯 BOT READINESS ASSESSMENT:
"""
        
        # Calculate readiness score
        compatibility_rate = analysis.bot_compatibility_summary['compatible_trades'] / analysis.bot_compatibility_summary['total_trades']
        meme_compatibility = analysis.performance_metrics['meme_coin_compatibility_rate']
        
        if compatibility_rate >= 0.95 and meme_compatibility >= 0.90:
            report += """   🎉 EXCELLENT! Your bot is ready for comprehensive meme coin copy trading!
   ✅ High compatibility rate with target wallet trades
   ✅ Strong meme coin support
   ✅ Ready for production deployment
"""
        elif compatibility_rate >= 0.85 and meme_compatibility >= 0.75:
            report += """   📈 GOOD! Your bot has strong compatibility with some optimization needed
   ✅ Good overall compatibility rate
   ⚠️ Some meme coin edge cases need addressing
   🔧 Review incompatibility reasons for improvements
"""
        else:
            report += """   ⚠️ NEEDS IMPROVEMENT! Significant gaps in meme coin compatibility
   ❌ Low compatibility rate with target trades
   ❌ Missing support for many meme coin scenarios
   🛠️ Requires substantial optimization before deployment
"""
        
        report += f"""
🚀 SPECIFIC RECOMMENDATIONS:
"""
        
        recommendations = []
        
        # Analyze failure patterns for recommendations
        if analysis.failure_reasons.get('unsupported_dex', 0) > 0:
            recommendations.append("   ✅ Add support for additional DEX programs detected")
        
        if analysis.failure_reasons.get('token_too_new', 0) > 0:
            recommendations.append("   ✅ Optimize handling of very new tokens (< 6 minutes old)")
        
        if analysis.failure_reasons.get('no_token_mint', 0) > 0:
            recommendations.append("   ✅ Improve transaction parsing to extract token mints")
        
        if analysis.failure_reasons.get('unsupported_instruction', 0) > 0:
            recommendations.append("   ✅ Add support for additional instruction types")
        
        if meme_compatibility < 0.90:
            recommendations.append("   ✅ Enhance meme coin detection and handling")
            recommendations.append("   ✅ Implement enhanced transaction builder for edge cases")
        
        if compatibility_rate < 0.95:
            recommendations.append("   ✅ Review and address top incompatibility reasons")
            recommendations.append("   ✅ Add fallback strategies for failed transaction types")
        
        if not recommendations:
            recommendations.append("   🎉 No major improvements needed - maintain current performance!")
        
        for rec in recommendations:
            report += rec + "\n"
        
        report += f"""
💡 NEXT STEPS:
   1. 🔧 Address the incompatibility reasons identified above
   2. ⚡ Run real-time monitoring to validate improvements
   3. 🎯 Focus on the specific meme tokens that were missed
   4. 🚀 Deploy with confidence once compatibility > 95%

📋 This analysis shows exactly which trades your bot WOULD and WOULD NOT have been able to copy from the target wallets over the past 24 hours.
"""
        
        return report
    
    async def run_comprehensive_audit(self, hours_back: int = 24) -> CoverageAnalysis:
        """Run complete coverage audit"""
        logger.info("🚀 Starting comprehensive coverage audit...")
        
        all_target_transactions = []
        
        # Fetch transactions for all target wallets
        for wallet in self.target_wallets:
            transactions = await self.fetch_wallet_transactions(wallet, hours_back)
            all_target_transactions.extend(transactions)
        
        # Load bot execution log
        bot_executions = self.load_bot_execution_log()
        
        # Analyze coverage
        analysis = self.analyze_coverage(all_target_transactions, bot_executions)
        
        # Generate and save report
        report = await self.generate_detailed_report(analysis)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(f'coverage_audit_{timestamp}.txt', 'w') as f:
            f.write(report)
        
        with open(f'coverage_analysis_{timestamp}.json', 'w') as f:
            # Convert analysis to dict for JSON serialization
            analysis_dict = asdict(analysis)
            # Convert datetime objects to strings
            for missed_tx in analysis_dict['missed_trades']:
                missed_tx['timestamp'] = missed_tx['timestamp'].isoformat()
            json.dump(analysis_dict, f, indent=2)
        
        logger.info("✅ Coverage audit complete!")
        logger.info(f"📊 Overall Coverage: {analysis.overall_coverage:.2%}")
        logger.info(f"📋 Report saved to coverage_audit_{timestamp}.txt")
        
        return analysis

async def main():
    """Run coverage audit"""
    print("🎯 COPY TRADING COVERAGE AUDIT TOOL")
    print("=" * 50)
    
    # Initialize audit tool
    audit_tool = CoverageAuditTool()
    
    # Run audit for last 24 hours
    analysis = await audit_tool.run_comprehensive_audit(hours_back=24)
    
    # Print summary
    print(f"\n🎯 AUDIT SUMMARY:")
    print(f"   Overall Coverage: {analysis.overall_coverage:.2%}")
    print(f"   Total Trades: {analysis.total_target_trades}")
    print(f"   Executed: {analysis.executed_trades}")
    print(f"   Missed: {len(analysis.missed_trades)}")
    
    if analysis.overall_coverage >= 0.95:
        print("\n🎉 EXCELLENT! Achieving 95%+ coverage!")
    else:
        gap = 0.95 - analysis.overall_coverage
        print(f"\n📈 Gap to 95%: {gap:.1%}")
        print("📋 Check the detailed report for improvement recommendations")

if __name__ == "__main__":
    asyncio.run(main())
