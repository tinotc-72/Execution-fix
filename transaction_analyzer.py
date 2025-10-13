"""
🔍 TRANSACTION ANALYSIS MODULE - CLEAN VERSION WITH ROUTER EXTRACTION
Fixed version that properly extracts and returns router program information
"""

import asyncio
import logging
import traceback
import time
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature

logger = logging.getLogger(__name__)

class TransactionAnalyzer:
    """
    🔍 TRANSACTION ANALYZER - CLEAN VERSION WITH ROUTER EXTRACTION
    
    Handles all transaction analysis logic:
    - Balance-based trade detection
    - Router program extraction
    - Token extraction
    - Platform detection
    """
    
    def __init__(self, rpc_client: AsyncClient, env_keys=None):
        """Initialize transaction analyzer"""
        self.rpc_client = rpc_client
        self.env_keys = env_keys
        
        # Cache for performance
        self._token_cache = {}
        self._analysis_cache = {}
        
        logger.info("✅ Transaction Analyzer initialized")
    
    async def analyze_transaction_with_data(self, signature: str, wallet_address: str, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        🎯 NEW: ANALYZE TRANSACTION WITH EXISTING DATA (NO RPC REFETCH)
        Uses transaction data already obtained from WebSocket to avoid RPC refetch issues
        """
        
        # Check cache first
        cache_key = f"{signature}_{wallet_address}"
        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]

        # Robust input validation
        if transaction_data is None or not isinstance(transaction_data, dict):
            logger.error(f"❌ Invalid transaction_data provided to analyze_transaction_with_data (None or not dict)")
            return {
                'error': 'Invalid transaction_data: None or not a dict',
                'success': False,
                'token_mint': None,
                'action': 'error',
                'dex': 'unknown',
                'router_program_id': None
            }

        try:
            logger.info(f"🔍 Analyzing transaction {signature[:8]}... with existing data for wallet {wallet_address[:8]}...")

            # Use provided transaction data instead of fetching
            transaction = transaction_data.get('transaction', {})
            meta = transaction_data.get('meta', {})
            if transaction is None or not isinstance(transaction, dict):
                logger.error(f"❌ Invalid transaction in transaction_data (None or not dict)")
                return {
                    'error': 'Invalid transaction in transaction_data',
                    'success': False,
                    'token_mint': None,
                    'action': 'error',
                    'dex': 'unknown',
                    'router_program_id': None
                }
            if meta is None or not isinstance(meta, dict):
                logger.error(f"❌ Invalid meta in transaction_data (None or not dict)")
                return {
                    'error': 'Invalid meta in transaction_data',
                    'success': False,
                    'token_mint': None,
                    'action': 'error',
                    'dex': 'unknown',
                    'router_program_id': None
                }
            message = transaction.get('message', {})
            if message is None or not isinstance(message, dict):
                logger.error(f"❌ Invalid message in transaction (None or not dict)")
                return {
                    'error': 'Invalid message in transaction',
                    'success': False,
                    'token_mint': None,
                    'action': 'error',
                    'dex': 'unknown',
                    'router_program_id': None
                }

            if not meta or not message:
                logger.warning(f"   ❌ Missing metadata or message in provided data")
                return {
                    'error': 'Missing metadata or message in provided data',
                    'success': False,
                    'token_mint': None,
                    'action': 'error',
                    'dex': 'unknown',
                    'router_program_id': None
                }
            
            # Extract router program information first
            router_info = self._extract_router_program_info_from_data(message, meta, signature)
            logger.info(f"   🔧 Router program: {router_info['router_program_id']}")
            logger.info(f"   🔧 Account metas count: {len(router_info['account_metas'])}")
            logger.info(f"   🔧 Instruction data: {'Present' if router_info['instruction_data'] else 'None'}")
            
            # Get account keys
            account_keys = message.get('accountKeys', [])
            
            # Find wallet index in account keys
            wallet_index = None
            for i, account in enumerate(account_keys):
                if account == wallet_address:
                    wallet_index = i
                    break
            
            if wallet_index is None:
                logger.warning(f"   ❌ Target wallet not found in transaction")
                # Still try to extract token and return basic info
                token_mint = self._extract_token_from_provided_data(transaction_data)
                if token_mint:
                    logger.info(f"   ✅ Extracted token {token_mint[:8]}... without balance analysis")
                    result = {
                        'token_mint': token_mint,
                        'action': 'buy',  # Default assumption
                        'confidence': 'MEDIUM',
                        'dex': 'unknown',
                        'analysis_method': 'token_extraction_without_balance',
                        'router_program_id': router_info['router_program_id'],
                        'account_metas': router_info['account_metas'],
                        'instruction_data': router_info['instruction_data']
                    }
                    self._analysis_cache[cache_key] = result
                    return result
                return None
            
            # Continue with balance analysis using provided data
            return await self._perform_balance_analysis_with_data(signature, wallet_address, transaction_data, router_info)
            
        except Exception as e:
            logger.error(f"❌ Error analyzing transaction with data: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    async def analyze_transaction_with_balance_detection(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        🎯 PRODUCTION-READY BALANCE-BASED TRADE DETECTION WITH ROUTER EXTRACTION
        Uses actual balance changes to determine buy/sell/swap actions and extracts router information
        """
        
        # Check cache first
        cache_key = f"{signature}_{wallet_address}"
        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]
        
        try:
            logger.info(f"🔍 Analyzing transaction {signature[:8]}... for wallet {wallet_address[:8]}...")
            
            # Convert string signature to Signature object
            sig_obj = Signature.from_string(signature)
            
            # Get transaction data
            result = await self.rpc_client.get_transaction(sig_obj, max_supported_transaction_version=0)
            if not result or not result.value:
                logger.warning(f"   ❌ No transaction data found")
                return None
            
            transaction = result.value
            meta = transaction.meta
            message = transaction.transaction.message
            
            if not meta or not message:
                logger.warning(f"   ❌ Missing metadata or message")
                return None
            
            # Extract router program information first
            router_info = self._extract_router_program_info(message, meta, signature)
            logger.info(f"   🔧 Router program: {router_info['router_program_id']}")
            logger.info(f"   🔧 Account metas count: {len(router_info['account_metas'])}")
            logger.info(f"   🔧 Instruction data: {'Present' if router_info['instruction_data'] else 'None'}")
            
            # Get account keys
            account_keys = [str(key) for key in message.account_keys]
            
            # Find wallet index in account keys
            wallet_index = None
            for i, account in enumerate(account_keys):
                if account == wallet_address:
                    wallet_index = i
                    break
            
            if wallet_index is None:
                logger.warning(f"   ❌ Target wallet not found in transaction")
                # Still try to extract token and return basic info
                token_mint = await self._extract_token_from_transaction(transaction)
                if token_mint:
                    logger.info(f"   ✅ Extracted token {token_mint[:8]}... without balance analysis")
                    result = {
                        'token_mint': token_mint,
                        'action': 'buy',  # Default assumption
                        'confidence': 'MEDIUM',
                        'dex': 'unknown',
                        'analysis_method': 'token_extraction_without_balance'
                    }
                    # Add router information
                    result.update(router_info)
                    return result
                return None
            
            # Analyze SOL balance changes
            pre_balances = meta.pre_balances
            post_balances = meta.post_balances
            
            if wallet_index >= len(pre_balances) or wallet_index >= len(post_balances):
                logger.warning(f"   ❌ Balance data incomplete")
                return None
            
            sol_delta = (post_balances[wallet_index] - pre_balances[wallet_index]) / 1e9  # Convert to SOL
            
            # Analyze token balance changes
            token_changes = self._analyze_token_changes(meta, wallet_address)
            
            # Determine action
            action_result = self._determine_trade_action(sol_delta, token_changes, signature, wallet_address)
            
            if action_result:
                # Add router information to result
                action_result.update(router_info)
                
                # Detect platform
                platform = await self._detect_trading_platform(meta, account_keys)
                action_result['dex'] = platform
                
                logger.info(f"   ✅ {action_result['action'].upper()} detected with {action_result['confidence']} confidence")
                logger.info(f"   🎯 Platform: {platform}")
                
                # Cache result
                self._analysis_cache[cache_key] = action_result
            
            return action_result
            
        except Exception as e:
            logger.error(f"   ❌ Error analyzing transaction: {e}")
            logger.error(f"   ❌ Traceback: {traceback.format_exc()}")
            return None
    
    def _extract_router_program_info_from_data(self, message, meta, signature: str) -> Dict[str, Any]:
        """
        Extract router program information from provided transaction data (WebSocket format)
        """
        router_program_id = None
        account_metas = []
        instruction_data = None
        
        system_programs = {
            "11111111111111111111111111111111",
            "ComputeBudget111111111111111111111111111111",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
        }
        
        try:
            # Get account keys from WebSocket data format
            all_account_keys = message.get('accountKeys', [])
            
            # Handle address table lookups for WebSocket format
            address_table_lookups = message.get('addressTableLookups', [])
            if address_table_lookups and meta.get('loadedAddresses'):
                loaded_addresses = meta.get('loadedAddresses', {})
                if loaded_addresses.get('readonly'):
                    all_account_keys.extend(loaded_addresses['readonly'])
                if loaded_addresses.get('writable'):
                    all_account_keys.extend(loaded_addresses['writable'])
            
            logger.info(f"   🔧 Total account keys from data: {len(all_account_keys)}")
            
            # Extract router program from instructions
            instructions = message.get('instructions', [])
            if instructions:
                router_candidates = []
                
                for ix in instructions:
                    try:
                        # Find router program using programIdIndex
                        program_id_index = ix.get('programIdIndex')
                        if program_id_index is not None and program_id_index < len(all_account_keys):
                            candidate_router = all_account_keys[program_id_index]
                            if candidate_router not in system_programs:
                                router_candidates.append({
                                    'program_id': candidate_router,
                                    'instruction': ix
                                })
                                logger.info(f"   🎯 Router candidate found: {candidate_router}")
                            
                    except Exception as ix_error:
                        logger.debug(f"   ⚠️ Error processing instruction: {ix_error}")
                        continue
                
                # Prioritize known DEX routers
                known_dex_programs = {
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun
                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter
                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium CPMM
                    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # Pump.fun AMM
                }
                
                # Use the first known DEX router, or first candidate if none are known DEXs
                selected_router = None
                for candidate in router_candidates:
                    if candidate['program_id'] in known_dex_programs:
                        selected_router = candidate
                        break
                
                # If no known DEX found, use first non-system program
                if not selected_router and router_candidates:
                    selected_router = router_candidates[0]
                
                if selected_router:
                    router_program_id = selected_router['program_id']
                    ix = selected_router['instruction']
                    logger.info(f"   🎯 Selected router program: {router_program_id}")
                    
                    # Extract account metas from the selected instruction
                    if ix.get('accounts'):
                        account_metas = []
                        for account_index in ix['accounts']:
                            if account_index < len(all_account_keys):
                                account_metas.append({
                                    'pubkey': all_account_keys[account_index],
                                    'is_signer': account_index == 0,  # First account usually signer
                                    'is_writable': True  # Assume writable for simplicity
                                })
                    
                    # Extract instruction data
                    if ix.get('data'):
                        instruction_data = ix['data']
            
            return {
                'router_program_id': router_program_id,
                'account_metas': account_metas,
                'instruction_data': instruction_data
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting router info from data: {e}")
            return {
                'router_program_id': None,
                'account_metas': [],
                'instruction_data': None
            }

    def _extract_router_program_info(self, message, meta, signature: str) -> Dict[str, Any]:
        """
        Extract router program, account metas, and instruction data from transaction
        Returns dict with router_program_id, account_metas, instruction_data
        """
        router_program_id = None
        account_metas = []
        instruction_data = None
        
        system_programs = {
            "11111111111111111111111111111111",
            "ComputeBudget111111111111111111111111111111",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
            "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
        }
        
        try:
            # Build complete account keys list including address table lookups
            all_account_keys = [str(key) for key in message.account_keys]
            
            # Handle addressTableLookups for versioned transactions
            if hasattr(message, 'address_table_lookups') and message.address_table_lookups:
                for lookup in message.address_table_lookups:
                    # Add readonly accounts from lookup tables
                    if hasattr(lookup, 'readonly_indexes') and meta and hasattr(meta, 'loaded_addresses'):
                        if meta.loaded_addresses and hasattr(meta.loaded_addresses, 'readonly'):
                            all_account_keys.extend([str(addr) for addr in meta.loaded_addresses.readonly])
                    # Add writable accounts from lookup tables
                    if hasattr(lookup, 'writable_indexes') and meta and hasattr(meta, 'loaded_addresses'):
                        if meta.loaded_addresses and hasattr(meta.loaded_addresses, 'writable'):
                            all_account_keys.extend([str(addr) for addr in meta.loaded_addresses.writable])
            
            logger.info(f"   🔧 Total account keys (including lookups): {len(all_account_keys)}")
            
            # Extract router program from instructions
            if hasattr(message, 'instructions') and message.instructions:
                router_candidates = []
                
                for ix in message.instructions:
                    try:
                        # Find router program using program_id_index
                        if hasattr(ix, 'program_id_index') and ix.program_id_index < len(all_account_keys):
                            candidate_router = all_account_keys[ix.program_id_index]
                            if candidate_router not in system_programs:
                                router_candidates.append({
                                    'program_id': candidate_router,
                                    'instruction': ix
                                })
                                logger.info(f"   🎯 Router candidate found: {candidate_router}")
                            
                    except Exception as e:
                        logger.warning(f"   ⚠️ Error processing instruction: {e}")
                        continue
                
                # Prioritize known DEX routers
                known_dex_programs = {
                    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun
                    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter
                    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # Raydium CPMM
                    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # Pump.fun AMM
                }
                
                # Use the first known DEX router, or first candidate if none are known DEXs
                selected_router = None
                for candidate in router_candidates:
                    if candidate['program_id'] in known_dex_programs:
                        selected_router = candidate
                        break
                
                # If no known DEX found, use first non-system program
                if not selected_router and router_candidates:
                    selected_router = router_candidates[0]
                
                if selected_router:
                    router_program_id = selected_router['program_id']
                    ix = selected_router['instruction']
                    logger.info(f"   🎯 Selected router program: {router_program_id}")
                    
                    # Extract account metas from the selected instruction
                    if hasattr(ix, 'accounts'):
                        account_metas = []
                        for account_index in ix.accounts:
                            if account_index < len(all_account_keys):
                                account_metas.append(all_account_keys[account_index])
                    
                    # Extract instruction data
                    if hasattr(ix, 'data'):
                        instruction_data = bytes(ix.data)
            
            # Fallback: If router_program_id is still None, pick first non-system accountKey
            if not router_program_id and all_account_keys:
                for key in all_account_keys:
                    if key not in system_programs:
                        router_program_id = key
                        logger.warning(f"   ⚠️ Fallback router program used: {router_program_id}")
                        break
            
            # Final fallback
            if not router_program_id:
                router_program_id = "unknown_router"
                logger.error(f"   ❌ Router program could not be determined for transaction {signature}")
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting router info: {e}")
            router_program_id = "unknown_router"
        
        return {
            'router_program_id': router_program_id,
            'account_metas': account_metas,
            'instruction_data': instruction_data
        }
    
    def _analyze_token_changes(self, meta, wallet_address: str) -> Dict[str, Dict[str, Any]]:
        """Analyze token balance changes for the wallet"""
        token_changes = {}
        
        # Get pre and post token balances
        pre_token_balances = getattr(meta, 'pre_token_balances', [])
        post_token_balances = getattr(meta, 'post_token_balances', [])
        
        # Process pre-transaction token balances
        for balance in pre_token_balances:
            if balance.owner == wallet_address:
                mint = str(balance.mint)
                ui_amount = balance.ui_token_amount
                amount = float(ui_amount.ui_amount or 0)
                token_changes[mint] = {
                    'pre': amount,
                    'post': 0,
                    'delta': 0,
                    'symbol': 'TOKEN'
                }
        
        # Process post-transaction token balances
        for balance in post_token_balances:
            if balance.owner == wallet_address:
                mint = str(balance.mint)
                ui_amount = balance.ui_token_amount
                amount = float(ui_amount.ui_amount or 0)
                
                if mint in token_changes:
                    token_changes[mint]['post'] = amount
                else:
                    token_changes[mint] = {
                        'pre': 0,
                        'post': amount,
                        'delta': 0,
                        'symbol': 'TOKEN'
                    }
        
        # Calculate deltas
        for mint in token_changes:
            change = token_changes[mint]
            change['delta'] = change['post'] - change['pre']
        
        return token_changes
    
    def _determine_trade_action(self, sol_delta: float, token_changes: Dict[str, Dict[str, Any]], 
                              signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Determine the trade action based on balance changes"""
        
        # Separate gained and lost tokens
        gained_tokens = []
        lost_tokens = []
        
        for mint, change in token_changes.items():
            if change['delta'] > 0:
                gained_tokens.append((mint, change))
            elif change['delta'] < 0:
                lost_tokens.append((mint, change))
        
        logger.info(f"   💰 SOL delta: {sol_delta:+.6f}")
        logger.info(f"   📈 Gained tokens: {len(gained_tokens)}")
        logger.info(f"   📉 Lost tokens: {len(lost_tokens)}")
        
        for mint, change in gained_tokens:
            logger.info(f"      ✅ Gained {change['delta']:,.6f} {change['symbol']}")
        for mint, change in lost_tokens:
            logger.info(f"      ❌ Lost {abs(change['delta']):,.6f} {change['symbol']}")
        
        # Decision logic
        if sol_delta < -0.001 and len(gained_tokens) > 0 and len(lost_tokens) == 0:
            # Spent SOL and gained tokens = BUY
            primary_token = gained_tokens[0][0]
            return {
                'action': 'buy',
                'confidence': 'HIGH',
                'reasoning': f"Spent {abs(sol_delta):.6f} SOL, gained {gained_tokens[0][1]['delta']:,.6f} {gained_tokens[0][1]['symbol']}",
                'signature': signature,
                'wallet': wallet_address,
                'sol_delta': sol_delta,
                'token_mint': primary_token,
                'gained_tokens': gained_tokens,
                'lost_tokens': lost_tokens,
                'timestamp': time.time(),
                'method': 'balance_based_detection'
            }
            
        elif sol_delta > 0.001 and len(lost_tokens) > 0 and len(gained_tokens) == 0:
            # Gained SOL and lost tokens = SELL
            primary_token = lost_tokens[0][0]
            return {
                'action': 'sell',
                'confidence': 'HIGH',
                'reasoning': f"Gained {sol_delta:+.6f} SOL, sold {abs(lost_tokens[0][1]['delta']):,.6f} {lost_tokens[0][1]['symbol']}",
                'signature': signature,
                'wallet': wallet_address,
                'sol_delta': sol_delta,
                'token_mint': primary_token,
                'gained_tokens': gained_tokens,
                'lost_tokens': lost_tokens,
                'timestamp': time.time(),
                'method': 'balance_based_detection'
            }
            
        elif len(gained_tokens) > 0 and len(lost_tokens) > 0:
            # Token-to-token swap
            primary_token = gained_tokens[0][0] if len(gained_tokens) > 0 else lost_tokens[0][0]
            return {
                'action': 'swap',
                'confidence': 'MEDIUM',
                'reasoning': f"Swapped {abs(lost_tokens[0][1]['delta']):,.6f} {lost_tokens[0][1]['symbol']} for {gained_tokens[0][1]['delta']:,.6f} {gained_tokens[0][1]['symbol']}",
                'signature': signature,
                'wallet': wallet_address,
                'sol_delta': sol_delta,
                'token_mint': primary_token,
                'gained_tokens': gained_tokens,
                'lost_tokens': lost_tokens,
                'timestamp': time.time(),
                'method': 'balance_based_detection'
            }
        
        # No clear action detected
        logger.info(f"   ❓ No clear trade action detected")
        return None
    
    async def _detect_trading_platform(self, meta, account_keys: List[str]) -> str:
        """Detect the trading platform based on account keys"""
        
        # Check for known DEX program IDs
        platform_programs = {
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "jupiter",
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "pumpfun",
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "raydium_amm",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "raydium_cpmm",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "orca_whirlpool",
            "9W959DqEETiGZocYWCQPaJ6sBmUzgZsGEGPWGveEwyxD": "orca_aquafarm"
        }
        
        for account in account_keys:
            if account in platform_programs:
                return platform_programs[account]
        
        return "unknown"
    
    def _extract_token_from_provided_data(self, transaction_data: Dict[str, Any]) -> Optional[str]:
        """Extract token mint from provided transaction data (WebSocket format)"""
        try:
            meta = transaction_data.get('meta', {})
            
            # Look in post token balances first
            post_token_balances = meta.get('postTokenBalances', [])
            if post_token_balances:
                for balance in post_token_balances:
                    mint = balance.get('mint', '')
                    if mint and len(mint) == 44 and not mint.startswith('So1111'):
                        return mint
            
            # Look in pre token balances
            pre_token_balances = meta.get('preTokenBalances', [])
            if pre_token_balances:
                for balance in pre_token_balances:
                    mint = balance.get('mint', '')
                    if mint and len(mint) == 44 and not mint.startswith('So1111'):
                        return mint
            
            return None
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting token from data: {e}")
            return None

    async def _perform_balance_analysis_with_data(self, signature: str, wallet_address: str, transaction_data: Dict[str, Any], router_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Perform balance analysis using provided transaction data"""
        try:
            meta = transaction_data.get('meta', {})
            transaction = transaction_data.get('transaction', {})
            message = transaction.get('message', {})
            
            # Get account keys
            account_keys = message.get('accountKeys', [])
            
            # Handle address table lookups
            address_table_lookups = message.get('addressTableLookups', [])
            if address_table_lookups and meta.get('loadedAddresses'):
                loaded_addresses = meta.get('loadedAddresses', {})
                if loaded_addresses.get('readonly'):
                    account_keys.extend(loaded_addresses['readonly'])
                if loaded_addresses.get('writable'):
                    account_keys.extend(loaded_addresses['writable'])
            
            # Find wallet index
            wallet_index = None
            for i, account in enumerate(account_keys):
                if account == wallet_address:
                    wallet_index = i
                    break
            
            if wallet_index is None:
                return None
            
            # Analyze balance changes
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            if wallet_index >= len(pre_balances) or wallet_index >= len(post_balances):
                logger.warning(f"   ❌ Wallet index {wallet_index} out of range for balances")
                return None
            
            # Calculate SOL balance change
            sol_change = post_balances[wallet_index] - pre_balances[wallet_index]
            
            # Find token balance changes for the wallet
            token_changes = {}
            
            # Check pre token balances
            for balance in pre_token_balances:
                if balance.get('accountIndex') == wallet_index:
                    mint = balance.get('mint')
                    amount = float(balance.get('uiTokenAmount', {}).get('uiAmount', 0))
                    token_changes[mint] = -amount  # Negative for pre (what we had before)
            
            # Check post token balances
            for balance in post_token_balances:
                if balance.get('accountIndex') == wallet_index:
                    mint = balance.get('mint')
                    amount = float(balance.get('uiTokenAmount', {}).get('uiAmount', 0))
                    if mint in token_changes:
                        token_changes[mint] += amount  # Add post amount
                    else:
                        token_changes[mint] = amount  # New token
            
            # Determine action based on changes
            action = 'unknown'
            confidence = 'LOW'
            token_mint = None
            
            # Find the primary token involved (largest change)
            primary_token = None
            max_change = 0
            
            for mint, change in token_changes.items():
                if abs(change) > max_change and not mint.startswith('So1111'):
                    max_change = abs(change)
                    primary_token = mint
                    token_mint = mint
            
            if primary_token and max_change > 0:
                change = token_changes[primary_token]
                if change > 0:
                    action = 'buy'
                    confidence = 'HIGH'
                elif change < 0:
                    action = 'sell'
                    confidence = 'HIGH'
            
            # Detect DEX
            dex = self._detect_dex_from_data(transaction_data)
            
            result = {
                'token_mint': token_mint,
                'action': action,
                'confidence': confidence,
                'dex': dex,
                'sol_change': sol_change,
                'token_changes': token_changes,
                'analysis_method': 'balance_analysis_with_data',
                'router_program_id': router_info['router_program_id'],
                'account_metas': router_info['account_metas'],
                'instruction_data': router_info['instruction_data']
            }
            
            # Cache result
            cache_key = f"{signature}_{wallet_address}"
            self._analysis_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in balance analysis with data: {e}")
            return None

    def _detect_dex_from_data(self, transaction_data: Dict[str, Any]) -> str:
        """Detect DEX from provided transaction data"""
        try:
            logs = transaction_data.get('meta', {}).get('logMessages', [])
            
            # Check for known DEX signatures in logs
            for log in logs:
                if 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4' in log:
                    return 'Jupiter'
                elif 'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA' in log:
                    return 'Pump.fun'
                elif 'RouteProcessor' in log:
                    return 'Jupiter'
                elif 'Raydium' in log:
                    return 'Raydium'
            
            # Check account keys for known DEX programs
            account_keys = transaction_data.get('transaction', {}).get('message', {}).get('accountKeys', [])
            
            for account in account_keys:
                if account == 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4':
                    return 'Jupiter'
                elif account == 'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA':
                    return 'Pump.fun'
                elif 'Raydium' in account or 'raydium' in account.lower():
                    return 'Raydium'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error detecting DEX from data: {e}")
            return 'unknown'

    async def _extract_token_from_transaction(self, transaction) -> Optional[str]:
        """Extract token mint from transaction"""
        try:
            meta = transaction.meta
            
            # Look in post token balances first
            if hasattr(meta, 'post_token_balances') and meta.post_token_balances:
                for balance in meta.post_token_balances:
                    mint = str(balance.mint)
                    if mint and len(mint) == 44 and not mint.startswith('So1111'):
                        return mint
            
            # Look in pre token balances
            if hasattr(meta, 'pre_token_balances') and meta.pre_token_balances:
                for balance in meta.pre_token_balances:
                    mint = str(balance.mint)
                    if mint and len(mint) == 44 and not mint.startswith('So1111'):
                        return mint
            
            return None
            
        except Exception as e:
            logger.error(f"   ❌ Error extracting token: {e}")
            return None


# Factory function for easy creation
def create_transaction_analyzer(rpc_client: AsyncClient, env_keys=None) -> TransactionAnalyzer:
    """Create a transaction analyzer instance"""
    return TransactionAnalyzer(rpc_client=rpc_client, env_keys=env_keys)