"""
🚀 TRADE PROCESSOR - Enhanced trade validation and execution logic
Separated from main.py for cleaner architecture
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TradeProcessor:
    """Handles all trade processing, validation, and execution logic"""
    
    def __init__(self, execution_coordinator, target_wallets: List[str], rpc_client=None):
        self.execution_coordinator = execution_coordinator
        self.target_wallets = target_wallets
        self.rpc_client = rpc_client
        
        # 🧠 INTELLIGENT EXECUTOR MAPPING based on program IDs
        self.dex_executor_mapping = {
            'pumpfun': ['direct_pumpfun'],
            'raydium_cpmm': ['cpmm'],
            'raydium_clmm': ['clmm'], 
            'raydium_amm': ['raydium'],
            'jupiter': ['jupiter'],
            'orca': ['orca'],
            'phoenix': ['phoenix'],
            'unknown': ['jupiter', 'raydium']  # Safe defaults
        }
    
    async def validate_trade_info(self, trade_info: Dict[str, Any]) -> bool:
        """Validate trade info - clean delegate method"""
        if not trade_info:
            return False
        
        # Check for minimum required fields
        required_fields = ['signature', 'wallet_address']
        for field in required_fields:
            if field not in trade_info:
                return False
        
        return True
    
    async def execute_single_wallet_trade(self, trade_info: Dict[str, Any], source_wallet: str) -> Dict:
        """Execute trade for a specific wallet - clean delegate method"""
        try:
            # ✅ NEW: Extract action from either direct field or basic_analysis
            action = trade_info.get('action')
            if not action and 'basic_analysis' in trade_info:
                action = trade_info['basic_analysis'].get('likely_action', 'unknown')
            if not action:
                action = 'unknown'
            
            action = action.lower()
            token_mint = trade_info.get('token_mint', 'UNKNOWN')
            
            logger.info(f"🎯 ⚡ SPEED PROCESSING {action.upper()} from {source_wallet[:8]}...")
            
            # 🚀 ENHANCED: Extract token mint if not available
            if token_mint in ['UNKNOWN', 'PENDING_ANALYSIS', '', 'FALLBACK'] or len(token_mint) < 32:
                logger.info("🔍 Extracting token mint during processing...")
                
                signature = trade_info.get('signature')
                if signature:
                    try:
                        token_extraction = await asyncio.wait_for(
                            self.fast_token_extraction(signature, source_wallet),
                            timeout=3.0  # Extended timeout for better extraction
                        )
                        
                        if token_extraction and token_extraction.get('token_mint'):
                            token_mint = token_extraction['token_mint']
                            logger.info(f"✅ Extracted token: {token_mint[:8]}...")
                            
                            # Update trade info with extracted details
                            if 'amount_change' in token_extraction:
                                trade_info['amount_change'] = token_extraction['amount_change']
                        else:
                            logger.warning("⚠️ Could not extract token mint - trying simple analysis")
                            # Try simple analysis as backup
                            simple_analysis = await asyncio.wait_for(
                                self.simple_trade_analysis(signature, source_wallet),
                                timeout=2.0
                            )
                            if simple_analysis and simple_analysis.get('token_mint'):
                                token_mint = simple_analysis['token_mint']
                                logger.info(f"✅ Simple analysis found token: {token_mint[:8]}...")
                            
                    except asyncio.TimeoutError:
                        logger.warning("⏰ Token extraction timeout - checking if valid token anyway")
                    except Exception as e:
                        logger.warning(f"❌ Token extraction error: {e} - checking if valid token anyway")
            
            # ✅ NEW: Skip execution if still no valid token
            if not token_mint or token_mint in ['UNKNOWN', 'PENDING_ANALYSIS', '', 'FALLBACK'] or len(token_mint) < 32:
                logger.warning(f"⚠️ Invalid or missing token mint: {token_mint} - skipping execution")
                return {'success': False, 'error': f'Invalid token mint: {token_mint}'}
            
            # 🚀 EXECUTE REGARDLESS: Even if token extraction failed, try to execute
            # The executors might be able to extract token info themselves
            
            if action == 'buy':
                logger.info(f"💎 ⚡ Executing INTELLIGENT copy BUY")
                
                # 🧠 INTELLIGENT ROUTING: Use detection confidence for smart executor selection
                basic_analysis = trade_info.get('basic_analysis', {})
                detection_confidence = basic_analysis.get('detection_confidence', 'low')
                detected_dex = basic_analysis.get('detected_dex', 'unknown')
                
                if detection_confidence == 'high' and detected_dex != 'unknown':
                    # HIGH CONFIDENCE: Use intelligent routing
                    logger.info(f"🎯 HIGH CONFIDENCE detection ({detected_dex}) - using intelligent routing")
                    success = await self._execute_intelligent_buy(token_mint, source_wallet, trade_info)
                else:
                    # FALLBACK: Use original parallel execution
                    logger.info(f"🔄 FALLBACK to parallel execution (confidence: {detection_confidence})")
                    success = await self.execution_coordinator._execute_copy_buy(
                        token_mint=token_mint,
                        source_wallet=source_wallet,
                        detected_dex=trade_info.get('dex', 'Unknown'),
                        trade_info=trade_info
                    )
                
                return {'success': success, 'action': 'buy'}
                
            elif action == 'sell':
                if token_mint and len(token_mint) >= 32:
                    logger.info(f"💸 ⚡ Executing SPEED copy SELL for {token_mint[:8]}...")
                    await self.execution_coordinator._execute_copy_sell(
                        token_mint=token_mint,
                        trade_info=trade_info,
                        source_wallet=source_wallet
                    )
                    return {'success': True, 'action': 'sell'}
                else:
                    logger.warning(f"⚠️ Cannot sell without valid token mint: {token_mint}")
                    return {'success': False, 'error': 'Invalid token mint for sell'}
                    
            elif action in ['unknown', 'transfer', 'swap']:
                # For unknown actions, try as buy (most profitable strategy)
                logger.info(f"🎯 ⚡ Unknown/Transfer action - trying as BUY for aggressive copying")
                await self.execution_coordinator._execute_copy_buy(
                    token_mint=token_mint,
                    source_wallet=source_wallet,
                    detected_dex=trade_info.get('dex', 'Unknown'),
                    trade_info=trade_info
                )
                return {'success': True, 'action': 'buy_fallback'}
            else:
                logger.warning(f"⚠️ Unhandled action: {action}")
                return {'success': False, 'error': f'Unhandled action: {action}'}
                
        except Exception as e:
            logger.error(f"❌ Error executing single wallet trade: {e}")
            return {'success': False, 'error': str(e)}
    
    async def fast_token_extraction(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        ⚡ Ultra-fast token mint extraction for immediate copying
        ENHANCED: Robust None handling and multiple extraction fallbacks
        """
        try:
            from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
            analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
            result = await analyzer.analyze_wallet_action(signature, wallet_address)
            
            if result and 'token_mint' in result and result['token_mint'] not in ['UNKNOWN', '', None]:
                # ENHANCED: Defensive None handling for balance calculations
                pre = result.get('pre')
                post = result.get('post')
                amount_change = 0
                
                try:
                    # Handle various None scenarios gracefully
                    if pre is not None and post is not None:
                        # Both values available - safe calculation
                        amount_change = float(post) - float(pre)
                    elif pre is not None and post is None:
                        # Only pre available - assume full sale if negative
                        amount_change = -float(pre) if float(pre) > 0 else 0
                    elif pre is None and post is not None:
                        # Only post available - assume full buy
                        amount_change = float(post) if float(post) > 0 else 0
                    else:
                        # Both None - use fallback from result
                        amount_change = result.get('amount_change', 0)
                        if amount_change is None:
                            amount_change = 0
                        else:
                            amount_change = float(amount_change)
                            
                except (TypeError, ValueError, Exception) as calc_error:
                    logger.debug(f"⚠️ Balance calculation error: {calc_error}, using fallback")
                    # Ultimate fallback - extract from result or default to 0
                    amount_change = result.get('amount_change', 0)
                    if amount_change is None:
                        amount_change = 0
                    try:
                        amount_change = float(amount_change)
                    except:
                        amount_change = 0
                
                logger.debug(f"✅ Balance extraction: pre={pre}, post={post}, change={amount_change}")
                
                return {
                    'token_mint': result['token_mint'],
                    'action': result.get('action', 'buy'),
                    'amount_change': amount_change,
                    'pre_balance': pre if pre is not None else 0,
                    'post_balance': post if post is not None else 0
                }
                
        except Exception as e:
            logger.warning(f"Fast extraction failed: {e}")

        # Fallback 1: Parse raw logs for mint (enhanced with balance parsing)
        try:
            from utils import get_transaction_with_logs
            tx_data = await get_transaction_with_logs(signature)
            if tx_data and 'logMessages' in tx_data:
                extracted_mint = None
                balance_info = {'pre': None, 'post': None}
                
                for log in tx_data['logMessages']:
                    # Extract mint
                    if 'mint' in log.lower():
                        import re
                        match = re.search(r"mint[:=]\s*([A-Za-z0-9]{32,})", log)
                        if match:
                            extracted_mint = match.group(1)
                    
                    # Extract balance information
                    if 'balance' in log.lower():
                        balance_match = re.search(r"balance[:=]\s*(\d+)", log)
                        if balance_match:
                            balance_val = int(balance_match.group(1))
                            if balance_info['pre'] is None:
                                balance_info['pre'] = balance_val
                            else:
                                balance_info['post'] = balance_val
                
                if extracted_mint:
                    # Calculate change safely
                    amount_change = 0
                    if balance_info['pre'] is not None and balance_info['post'] is not None:
                        amount_change = balance_info['post'] - balance_info['pre']
                    
                    logger.info(f"✅ Fallback log parsing found: mint={extracted_mint}, change={amount_change}")
                    return {
                        'token_mint': extracted_mint, 
                        'action': 'unknown', 
                        'amount_change': amount_change,
                        'pre_balance': balance_info['pre'] or 0,
                        'post_balance': balance_info['post'] or 0
                    }
                    
        except Exception as e:
            logger.warning(f"Log parsing fallback failed: {e}")

        # Fallback 2: External API lookup with enhanced error handling
        try:
            # Placeholder for external API calls
            # Example: Helius Enhanced API, SolanaFM, etc.
            mint = None  # Replace with actual API call
            if mint:
                logger.info(f"✅ External API found mint: {mint}")
                return {
                    'token_mint': mint, 
                    'action': 'unknown', 
                    'amount_change': 0,
                    'pre_balance': 0,
                    'post_balance': 0
                }
        except Exception as e:
            logger.warning(f"External API fallback failed: {e}")

        # Fallback 3: Simple mint extraction from instruction data
        try:
            from utils import get_transaction_with_logs
            tx_data = await get_transaction_with_logs(signature)
            if tx_data and 'transaction' in tx_data:
                transaction = tx_data['transaction']
                if 'message' in transaction and 'instructions' in transaction['message']:
                    for instruction in transaction['message']['instructions']:
                        # Look for common DEX program IDs and extract mints
                        if 'accounts' in instruction and len(instruction['accounts']) > 2:
                            account_keys = transaction['message']['accountKeys']
                            for acc_idx in instruction['accounts'][:5]:  # Check first few accounts
                                if acc_idx < len(account_keys):
                                    potential_mint = account_keys[acc_idx]
                                    # Basic validation for mint-like addresses
                                    if len(potential_mint) >= 32 and not potential_mint.startswith('11111'):
                                        logger.info(f"✅ Instruction parsing found potential mint: {potential_mint}")
                                        return {
                                            'token_mint': potential_mint,
                                            'action': 'unknown',
                                            'amount_change': 0,
                                            'pre_balance': 0,
                                            'post_balance': 0
                                        }
        except Exception as e:
            logger.debug(f"Instruction parsing fallback failed: {e}")

        # Log every failed extraction for review
        logger.error(f"❌ All mint extraction methods failed for signature={signature[:8]}..., wallet={wallet_address[:8]}...")
        return None

    async def simple_trade_analysis(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Simple trade analysis using official analyzer
        ENHANCED: Robust None handling and comprehensive balance validation
        """
        try:
            from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
            
            analyzer = OfficialWalletPerspectiveAnalyzer(self.rpc_client)
            result = await analyzer.analyze_wallet_action(signature, wallet_address)
            
            if result and result.get('action') not in ['none', 'error']:
                # ENHANCED: Safe balance change calculation with None handling
                balance_change = 0
                try:
                    amount_change = result.get('amount_change')
                    if amount_change is not None:
                        balance_change = float(amount_change)
                    else:
                        # Calculate from pre/post if available
                        pre = result.get('pre')
                        post = result.get('post')
                        if pre is not None and post is not None:
                            balance_change = float(post) - float(pre)
                        else:
                            balance_change = 0
                except (TypeError, ValueError, Exception) as balance_error:
                    logger.debug(f"Balance calculation error in simple analysis: {balance_error}")
                    balance_change = 0
                
                return {
                    'signature': signature,
                    'wallet_address': wallet_address,
                    'action': result['action'],
                    'dex': 'Official_Analysis',
                    'token_mint': result.get('token_mint', 'UNKNOWN'),
                    'timestamp': datetime.now(timezone.utc),
                    'extraction_method': 'simple_analysis',
                    'balance_change': balance_change,
                    'confidence': result.get('confidence', 10),
                    'pre_balance': result.get('pre', 0) if result.get('pre') is not None else 0,
                    'post_balance': result.get('post', 0) if result.get('post') is not None else 0
                }
            return None
        except Exception as e:
            logger.debug(f"Simple analysis failed: {e}")
            return None
    
    async def process_detected_trade(self, trade_info: Dict[str, Any], fast_token_extraction_func, simple_trade_analysis_func) -> bool:
        """
        🚀 ENHANCED: Process validated trade with intelligent wallet detection
        Returns True if trade was processed successfully, False otherwise
        """
        try:
            # ✅ Extract action from either direct field or basic_analysis
            action = self._extract_action(trade_info)
            token_mint = trade_info.get('token_mint', 'UNKNOWN')
            source_wallet = trade_info.get('wallet_address')
            
            # 🔧 FIX: Enhanced wallet determination
            if not source_wallet or source_wallet == self.target_wallets[0]:
                # If wallet is unknown or defaulted, determine correct wallet from transaction
                return await self._determine_and_execute_trade(trade_info, fast_token_extraction_func, simple_trade_analysis_func)
            
            # Normal execution with known wallet
            return await self._execute_single_wallet_trade(trade_info, source_wallet, fast_token_extraction_func, simple_trade_analysis_func)
            
        except Exception as e:
            logger.error(f"❌ Error processing trade: {e}")
            logger.debug(f"Trade info: {trade_info}")
            
            # 🚀 AGGRESSIVE FALLBACK: Try to extract token mint from logs first
            try:
                signature = trade_info.get('signature')
                if signature:
                    logger.info("🔄 ⚡ Attempting fallback token extraction...")
                    
                    # Try with each target wallet to see which one has balance changes
                    for wallet in self.target_wallets:
                        try:
                            token_extraction = await asyncio.wait_for(
                                fast_token_extraction_func(signature, wallet),
                                timeout=3.0
                            )
                            if token_extraction and token_extraction.get('token_mint'):
                                logger.info(f"✅ Found token for wallet {wallet[:8]}...: {token_extraction['token_mint'][:8]}...")
                                await self.execution_coordinator._execute_copy_buy(
                                    token_mint=token_extraction['token_mint'],
                                    source_wallet=wallet,
                                    detected_dex='extracted',
                                    trade_info=trade_info
                                )
                                return True
                        except Exception as wallet_error:
                            logger.debug(f"No trade found for wallet {wallet[:8]}...: {wallet_error}")
                            continue
                            
            except Exception as extraction_error:
                logger.warning(f"⚠️ Fallback extraction failed: {extraction_error}")
            
            # Final fallback - skip invalid token
            logger.warning("⚠️ No valid token mint available - skipping execution")
            return False
    
    async def _determine_and_execute_trade(self, trade_info: Dict[str, Any], fast_token_extraction_func, simple_trade_analysis_func) -> bool:
        """🔍 ENHANCED: Determine correct wallet and execute trade"""
        try:
            signature = trade_info.get('signature')
            if not signature:
                logger.warning("❌ No signature for wallet determination")
                return False
            
            logger.info(f"🔍 Determining correct wallet for transaction: {signature[:8]}...")
            
            # Try each target wallet to see which one has balance changes
            for wallet in self.target_wallets:
                logger.info(f"🔍 Testing wallet: {wallet[:8]}...")
                
                try:
                    # Use the official analyzer to check for balance changes
                    analysis_result = await asyncio.wait_for(
                        simple_trade_analysis_func(signature, wallet),
                        timeout=5.0
                    )
                    
                    if analysis_result and analysis_result.get('action') not in ['none', 'error']:
                        # Found the correct wallet!
                        logger.info(f"✅ Found correct wallet: {wallet[:8]}... with action: {analysis_result.get('action')}")
                        
                        # Update trade info with correct wallet and analysis
                        corrected_trade_info = trade_info.copy()
                        corrected_trade_info.update(analysis_result)
                        corrected_trade_info['wallet_address'] = wallet
                        
                        # Execute with corrected info
                        return await self._execute_single_wallet_trade(
                            corrected_trade_info, wallet, fast_token_extraction_func, simple_trade_analysis_func
                        )
                        
                except asyncio.TimeoutError:
                    logger.debug(f"⏰ Analysis timeout for wallet {wallet[:8]}...")
                    continue
                except Exception as e:
                    logger.debug(f"❌ Analysis error for wallet {wallet[:8]}...: {e}")
                    continue
            
            logger.warning(f"⚠️ Could not determine correct wallet for transaction {signature[:8]}...")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in wallet determination: {e}")
            return False
    
    def _extract_action(self, trade_info: Dict[str, Any]) -> str:
        """Extract action from trade_info with fallbacks"""
        action = trade_info.get('action')
        if not action and 'basic_analysis' in trade_info:
            action = trade_info['basic_analysis'].get('likely_action', 'unknown')
        if not action:
            action = 'unknown'
        return action.lower()
    
    def _extract_action(self, trade_info: Dict[str, Any]) -> str:
        """Extract action from trade_info with fallbacks"""
        action = trade_info.get('action')
        if not action and 'basic_analysis' in trade_info:
            action = trade_info['basic_analysis'].get('likely_action', 'unknown')
        if not action:
            action = 'unknown'
        return action.lower()
    
    async def _execute_single_wallet_trade(self, trade_info: Dict[str, Any], source_wallet: str, fast_token_extraction_func, simple_trade_analysis_func) -> bool:
        """Execute trade for a specific wallet"""
        try:
            action = self._extract_action(trade_info)
            token_mint = trade_info.get('token_mint', 'UNKNOWN')
            
            logger.info(f"🎯 ⚡ SPEED PROCESSING {action.upper()} from {source_wallet[:8]}...")
            
            # 🚀 ENHANCED: Extract token mint if not available
            token_mint = await self._extract_token_mint(trade_info, token_mint, source_wallet, fast_token_extraction_func, simple_trade_analysis_func)
            
            # ✅ Skip execution if still no valid token
            if not self._is_valid_token_mint(token_mint):
                logger.warning(f"⚠️ Invalid or missing token mint: {token_mint} - skipping execution")
                return False
            
            # 🚀 EXECUTE with valid token
            return await self._execute_trade_action(action, token_mint, source_wallet, trade_info)
                
        except Exception as e:
            logger.error(f"❌ Error executing single wallet trade: {e}")
            return False
    
    async def _extract_token_mint(self, trade_info: Dict[str, Any], current_token_mint: str, source_wallet: str, fast_token_extraction_func, simple_trade_analysis_func) -> str:
        """Extract token mint with multiple fallback methods"""
        token_mint = current_token_mint
        
        if token_mint in ['UNKNOWN', 'PENDING_ANALYSIS', '', 'FALLBACK'] or len(token_mint) < 32:
            logger.info("🔍 Extracting token mint during processing...")
            
            signature = trade_info.get('signature')
            if signature:
                try:
                    # Try fast extraction first
                    token_extraction = await asyncio.wait_for(
                        fast_token_extraction_func(signature, source_wallet),
                        timeout=3.0
                    )
                    
                    if token_extraction and token_extraction.get('token_mint'):
                        token_mint = token_extraction['token_mint']
                        logger.info(f"✅ Extracted token: {token_mint[:8]}...")
                        
                        # Update trade info with extracted details
                        if 'amount_change' in token_extraction:
                            trade_info['amount_change'] = token_extraction['amount_change']
                    else:
                        logger.warning("⚠️ Could not extract token mint - trying simple analysis")
                        # Try simple analysis as backup
                        simple_analysis = await asyncio.wait_for(
                            simple_trade_analysis_func(signature, source_wallet),
                            timeout=2.0
                        )
                        if simple_analysis and simple_analysis.get('token_mint'):
                            token_mint = simple_analysis['token_mint']
                            logger.info(f"✅ Simple analysis found token: {token_mint[:8]}...")
                        
                except asyncio.TimeoutError:
                    logger.warning("⏰ Token extraction timeout - checking if valid token anyway")
                except Exception as e:
                    logger.warning(f"❌ Token extraction error: {e} - checking if valid token anyway")
        
        return token_mint
    
    def _is_valid_token_mint(self, token_mint: str) -> bool:
        """Check if token mint is valid for execution"""
        if not token_mint:
            return False
        if token_mint in ['UNKNOWN', 'PENDING_ANALYSIS', '', 'FALLBACK']:
            return False
        if len(token_mint) < 32:
            return False
        return True
    
    async def _execute_trade_action(self, action: str, token_mint: str, source_wallet: str, trade_info: Dict[str, Any]) -> bool:
        """Execute the actual trade based on action type"""
        try:
            if action == 'buy':
                logger.info(f"💎 ⚡ Executing SPEED copy BUY")
                await self.execution_coordinator._execute_copy_buy(
                    token_mint=token_mint,
                    source_wallet=source_wallet,
                    detected_dex=trade_info.get('dex', 'Unknown'),
                    trade_info=trade_info
                )
                return True
                
            elif action == 'sell':
                logger.info(f"💸 ⚡ Executing SPEED copy SELL for {token_mint[:8]}...")
                await self.execution_coordinator._execute_copy_sell(
                    token_mint=token_mint,
                    trade_info=trade_info,
                    source_wallet=source_wallet
                )
                return True
                    
            elif action in ['unknown', 'transfer', 'swap']:
                # For unknown actions, try as buy (most profitable strategy)
                logger.info(f"🎯 ⚡ Unknown/Transfer action - trying as BUY for aggressive copying")
                await self.execution_coordinator._execute_copy_buy(
                    token_mint=token_mint,
                    source_wallet=source_wallet,
                    detected_dex=trade_info.get('dex', 'Unknown'),
                    trade_info=trade_info
                )
                return True
            else:
                logger.warning(f"⚠️ Unhandled action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error executing trade action {action}: {e}")
            return False
    
    def validate_trade(self, trade_info: Dict[str, Any]) -> bool:
        """
        🎯 SPEED OPTIMIZATION: Minimal validation for maximum copying
        """
        try:
            # Handle cases where wallet needs to be determined from transaction analysis
            wallet_address = trade_info.get('wallet_address', '')
            if not wallet_address:
                # ✅ Allow transactions with unknown wallet - will be determined by analysis
                if trade_info.get('detection_method') == 'websocket_logs_unknown_wallet':
                    logger.debug("Unknown wallet - will be determined by transaction analysis")
                    return True  # Let analysis determine the correct wallet
                else:
                    logger.debug("Missing wallet address")
                    return False
            
            # Check if wallet is in target list
            if wallet_address not in self.target_wallets:
                logger.debug(f"Not a target wallet: {wallet_address[:8]}...")
                return False
            
            # Must have signature for transaction analysis
            if not trade_info.get('signature'):
                logger.debug("Missing transaction signature")
                return False
            
            # ✅ UNIVERSAL VALIDATION: Accept all transactions for aggressive copying
            # We want to copy EVERYTHING to maximize profit opportunities
            logger.debug("✅ Trade validation passed - ready for copying")
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return False
    
    async def _execute_intelligent_buy(self, token_mint: str, source_wallet: str, trade_info: Dict[str, Any]) -> bool:
        """
        🧠 INTELLIGENT ROUTING: Select specific executor based on detected program ID
        Replaces the shotgun approach with focused execution
        """
        try:
            # Extract detection information
            basic_analysis = trade_info.get('basic_analysis', {})
            detected_dex = basic_analysis.get('detected_dex', 'unknown')
            detection_confidence = basic_analysis.get('detection_confidence', 'low')
            detection_method = basic_analysis.get('detection_method', 'text_pattern')
            
            logger.info(f"🧠 INTELLIGENT ROUTING:")
            logger.info(f"   🏪 DEX: {detected_dex}")
            logger.info(f"   📊 Confidence: {detection_confidence}")
            logger.info(f"   🔍 Method: {detection_method}")
            
            # Get specific executors for this DEX
            executors = self.dex_executor_mapping.get(detected_dex, ['jupiter'])
            
            if detection_confidence == 'high' and detection_method == 'program_id':
                # HIGH CONFIDENCE: Use only the specific executor
                executor_name = executors[0]
                logger.info(f"🎯 HIGH CONFIDENCE: Using {executor_name} executor only")
                
                return await self._execute_single_executor(token_mint, executor_name)
            
            elif detection_confidence == 'medium':
                # MEDIUM CONFIDENCE: Use specific executor + 1 backup
                focused_executors = executors[:2] if len(executors) > 1 else executors + ['jupiter']
                logger.info(f"🎯 MEDIUM CONFIDENCE: Using {len(focused_executors)} focused executors: {focused_executors}")
                
                return await self._execute_focused_parallel(token_mint, focused_executors)
            
            else:
                # LOW CONFIDENCE: Use 2-3 safe executors
                safe_executors = ['jupiter', 'raydium']
                logger.info(f"🎯 LOW CONFIDENCE: Using {len(safe_executors)} safe executors: {safe_executors}")
                
                return await self._execute_focused_parallel(token_mint, safe_executors)
                
        except Exception as e:
            logger.error(f"❌ Intelligent routing error: {e}")
            # Fallback to original execution
            return await self._fallback_execution(token_mint, source_wallet, trade_info)
    
    async def _execute_single_executor(self, token_mint: str, executor_name: str) -> bool:
        """Execute with a single, specific executor"""
        try:
            executor_func = self._get_executor_function(executor_name)
            if not executor_func:
                logger.warning(f"⚠️ Executor {executor_name} not available")
                return False
            
            logger.info(f"⚡ Executing with {executor_name} executor")
            
            result = await asyncio.wait_for(
                executor_func(
                    self.execution_coordinator.wallet,
                    token_mint,
                    self.execution_coordinator.config.investment_amount_sol
                ),
                timeout=15.0
            )
            
            success = result and result.get('success', False)
            if success:
                logger.info(f"✅ {executor_name} executor SUCCESS")
            else:
                logger.warning(f"⚠️ {executor_name} executor failed")
            
            return success
            
        except asyncio.TimeoutError:
            logger.warning(f"⏰ {executor_name} executor timeout")
            return False
        except Exception as e:
            logger.error(f"❌ {executor_name} executor error: {e}")
            return False
    
    async def _execute_focused_parallel(self, token_mint: str, executor_names: List[str]) -> bool:
        """Execute with a focused set of executors in parallel"""
        try:
            # Create tasks for each executor
            tasks = []
            for executor_name in executor_names:
                executor_func = self._get_executor_function(executor_name)
                if executor_func:
                    task = asyncio.create_task(
                        self._try_executor_with_timeout(executor_name, executor_func, token_mint),
                        name=f"exec_{executor_name}"
                    )
                    tasks.append(task)
            
            if not tasks:
                logger.error("❌ No valid executors found")
                return False
            
            logger.info(f"⚡ Parallel execution with {len(tasks)} focused executors")
            
            # Wait for first success
            done, pending = await asyncio.wait(
                tasks, 
                return_when=asyncio.FIRST_COMPLETED,
                timeout=12.0
            )
            
            # Cancel pending tasks to save resources
            for task in pending:
                task.cancel()
            
            # Check for success
            for task in done:
                try:
                    if await task:
                        logger.info(f"✅ Focused parallel execution SUCCESS")
                        return True
                except Exception:
                    pass
            
            logger.warning(f"⚠️ All focused executors failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Focused parallel execution error: {e}")
            return False
    
    async def _try_executor_with_timeout(self, executor_name: str, executor_func, token_mint: str) -> bool:
        """Try a single executor with timeout"""
        try:
            result = await asyncio.wait_for(
                executor_func(
                    self.execution_coordinator.wallet,
                    token_mint,
                    self.execution_coordinator.config.investment_amount_sol
                ),
                timeout=10.0
            )
            
            success = result and result.get('success', False)
            if success:
                logger.info(f"✅ {executor_name} SUCCESS")
            
            return success
            
        except asyncio.TimeoutError:
            logger.debug(f"⏰ {executor_name} timeout")
            return False
        except Exception as e:
            logger.debug(f"❌ {executor_name} error: {e}")
            return False
    
    def _get_executor_function(self, executor_name: str):
        """Get the executor function for a given name"""
        try:
            if executor_name == 'direct_pumpfun':
                return self.execution_coordinator._try_direct_pumpfun_buy
            elif executor_name == 'pumpfun':
                from official_executor_wrappers import try_pumpfun_buy
                return try_pumpfun_buy
            elif executor_name == 'jupiter':
                from official_executor_wrappers import try_jupiter_buy
                return try_jupiter_buy
            elif executor_name == 'raydium':
                from official_executor_wrappers import try_raydium_buy
                return try_raydium_buy
            elif executor_name == 'cpmm':
                from official_executor_wrappers import try_cpmm_buy
                return try_cpmm_buy
            elif executor_name == 'clmm':
                from official_executor_wrappers import try_clmm_hybrid_buy
                return try_clmm_hybrid_buy
            elif executor_name == 'orca':
                from official_executor_wrappers import try_orca_buy
                return try_orca_buy
            elif executor_name == 'phoenix':
                from official_executor_wrappers import try_phoenix_buy
                return try_phoenix_buy
            else:
                return None
        except ImportError as e:
            logger.debug(f"Executor {executor_name} not available: {e}")
            return None
    
    async def _fallback_execution(self, token_mint: str, source_wallet: str, trade_info: Dict[str, Any]) -> bool:
        """Fallback to original execution method"""
        logger.info("🔄 Falling back to original execution method")
        try:
            await self.execution_coordinator._execute_copy_buy(
                token_mint=token_mint,
                source_wallet=source_wallet,
                detected_dex=trade_info.get('dex', 'Unknown'),
                trade_info=trade_info
            )
            return True
        except Exception as e:
            logger.error(f"❌ Fallback execution failed: {e}")
            return False

# PATCHED: Ultra-aggressive fallback mint extraction, minimal validation, automated wallet determination, robust error handling
