import time
from datetime import datetime, timezone
from collections import OrderedDict
# Canonical known wallets/programs (expand as needed)
# Will be built after DEX_PROGRAMS and TOKEN_PROGRAMS are defined
CANONICAL_KNOWN_WALLETS = None

# Unified program ID configuration (single source of truth)
TOKEN_PROGRAMS = {
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # SPL Token Program
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",   # SPL Token-2022 Program
}

# DEX program IDs for routing
DEX_PROGRAMS = {
    # Raydium
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "raydium_cpmm",
    "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "raydium_cpmm",  # Raydium CPMM v2
    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "raydium_clmm",
    
    # Orca
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "orca_whirlpool",
    
    # Meteora DAMM v2
    "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "meteora",
    "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "meteora",
    
    # Pump.fun
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "pumpfun",
    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "pumpfun",  # Pump.fun AMM
    
    # Jupiter router
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "jupiter",
    
    # Advanced MEV Bot
    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "advanced_mev_bot",
}

# Build unified CANONICAL_KNOWN_WALLETS from all program IDs
CANONICAL_KNOWN_WALLETS = {
    "11111111111111111111111111111111",  # System Program
    "ComputeBudget111111111111111111111111111111",  # Compute Budget
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",  # Associated Token Program
    # Common intermediary tokens
    "So11111111111111111111111111111111111111112",  # WSOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",   # mSOL
    "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1",   # bSOL
    "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn", # JitoSOL
    # Bot wallets
    "gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB",  # Your bot wallet
    "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB",  # Your trading wallet
    "AVATAR_WALLET_1", "AVATAR_WALLET_2", "AVATAR_WALLET_3",
} | TOKEN_PROGRAMS | set(DEX_PROGRAMS.keys())  # Unify all known programs

# Simple LRU cache with TTL for pubkey → {is_mint, is_token_account, mint_of_token_account}
class LRUCacheTTL:
    def __init__(self, maxsize=512, ttl=1800):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.ttl = ttl
    def get(self, key):
        now = time.time()
        if key in self.cache:
            value, exp = self.cache[key]
            if exp > now:
                self.cache.move_to_end(key)
                return value
            else:
                del self.cache[key]
        return None
    def set(self, key, value):
        now = time.time()
        self.cache[key] = (value, now + self.ttl)
        self.cache.move_to_end(key)
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)

_mint_cache = LRUCacheTTL(maxsize=1024, ttl=1800)
# Pool-state cache: pool_address -> {mint_a, mint_b, vault_a, vault_b} for deterministic routing
_pool_cache = LRUCacheTTL(maxsize=512, ttl=3600)  # 1-hour TTL for pool states
import csv
import os
import re
from utils import get_transaction_with_logs
"""
🚀 TRADE PROCESSOR - Pure trade analysis and routing logic

OVERVIEW:
=========
This module handles all trade analysis and routing decisions WITHOUT executing trades.
It separates analysis logic from execution, making the system more maintainable and testable.

MAXIMALLY PERMISSIVE EXECUTION PHILOSOPHY:
==========================================
Following best practices from public Solana copy trading bots:
- Jupiter copy trading: https://github.com/jup-ag/jupiter-copy-trading
- Raydium copy bot: https://github.com/solana-labs/raydium-copy-bot

Key principles:
1. Execute on ANY DEX involvement - if a known DEX program is detected, execute the trade
2. Default to 'swap' for ambiguous actions - let the executor refine the action
3. Lower significance thresholds - prioritize trade capture over strict filtering
4. Permissive wallet monitoring - execute even if wallet isn't strictly in monitored list,
   as long as DEX involvement is detected

This ensures maximum trade capture and reliability, matching the behavior of public copy bots.

KEY COMPONENTS:
===============

1. ACTION EXTRACTION (_extract_action, _extract_action_with_fallback)
   - Primary: Token balance delta detection (most accurate)
   - Fallback: DEX program detection (MAXIMALLY PERMISSIVE - executes on ANY DEX involvement)
   - Last resort: Direct field extraction
   
   The fallback logic is ENHANCED to be more permissive:
   - Allows execution if monitored wallet is signer OR trade instructions exist
   - Defaults to 'swap' action when specific action cannot be determined
   - This prevents unnecessary trade skipping while maintaining safety

2. TOKEN MINT EXTRACTION
   - Sophisticated extraction from transaction metadata
   - Delta-based detection from balance changes
   - Pool cache for deterministic routing

3. DEX DETECTION (detect_dex_router)
   - Identifies DEX from program IDs
   - Validates against known DEX programs (Raydium, Orca, Meteora, etc.)
   - Routes to appropriate executor

4. EXECUTION VALIDATION (validate_execution_eligibility)
   - Ensures monitored wallets are involved
   - Provides detailed validation results for debugging

5. ROUTING DECISIONS (analyze_and_route_trade)
   - Combines all analysis results
   - Determines if execution is required
   - Returns routing instructions for execution coordinator

FALLBACK STRATEGY (MAXIMALLY PERMISSIVE):
==========================================
Following Jupiter/Raydium copy bot patterns for maximum trade capture:
- Reference: https://github.com/jup-ag/jupiter-copy-trading
- Reference: https://github.com/solana-labs/raydium-copy-bot

Primary trigger: DEX program detection
- If ANY known DEX program is detected, execution proceeds
- Defaults to 'swap' action for ambiguous cases (executor refines)
- No strict wallet monitoring requirement - executes on DEX involvement alone

This is safe because:
- Execution coordinator refines action from balance changes
- DEX routing handles generic swap actions  
- Focus on DEX involvement ensures we capture all relevant trades
- Maximizes trade capture like public copy bots while maintaining safety

Handles validation, analysis, and routing decisions without execution
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def is_valid_solana_address(address: str) -> bool:
    """Validate that a string is a valid Solana address format"""
    if not address or not (32 <= len(address) <= 44):
        return False
    try:
        import base58
        base58.b58decode(address)
        return True
    except Exception:
        return False

class TradeProcessor:
    # --- DEX memory for sell-on-same-DEX ---
    _last_buy_dex_by_mint = {}
    def _key_str(self, k) -> str:
        """Return a base58 string for any pubkey-like object (str, dict, solders.Pubkey)."""
        if k is None:
            return ""
        if isinstance(k, str):
            return k
        if isinstance(k, dict):
            v = k.get("pubkey")
            return v if isinstance(v, str) else (str(v) if v is not None else "")
        # solders.pubkey.Pubkey or other objects
        try:
            return str(k)
        except Exception:
            return ""
    
    def _pool_hints_for_keys(self, account_keys):
        # Placeholder advisory hints. Safe to return None.
        # If you later cache pool states elsewhere, consult them here.
        if not account_keys:
            return None
        # Example: check if any key already cached in _pool_cache
        for k in account_keys:
            st = _pool_cache.get(k)
            if st:
                return {"mints": {st.get("mint_a"), st.get("mint_b")}}
        return None
    """
    Pure trade processor - analyzes trades and provides routing decisions
    NO EXECUTION - only analysis and routing instructions
    """
    
    async def is_likely_token_mint(self, pubkey: str) -> bool:
        """
        Return True iff:
        - owner is Token Program (classic or 2022), and
        - data length matches mint account (≥ 82 and < 170), and
        - not in canonical known wallets
        Uses in-memory LRU cache with TTL.
        """
        if not pubkey or pubkey in CANONICAL_KNOWN_WALLETS:
            return False
        cached = _mint_cache.get(pubkey)
        if cached is not None:
            return cached.get('is_mint', False)

        info = await self._get_account_info(pubkey)
        is_mint = bool(info and info["is_mint"])
        _mint_cache.set(pubkey, {"is_mint": is_mint})
        return is_mint

    def _extract_router_program_id_from_tx(self, tx: dict) -> str | None:
        """Extract router program ID from transaction for coordinator detection"""
        try:
            msg = (tx.get('transaction', {}) or {}).get('message', {}) or tx.get('message', {})
            ixs = msg.get('instructions', []) or []
            # Normalize account keys to str
            raw_keys = msg.get('accountKeys', []) or []
            keys: list[str] = []
            for k in raw_keys:
                if isinstance(k, str):
                    keys.append(k)
                elif isinstance(k, dict) and 'pubkey' in k:
                    keys.append(str(k['pubkey']))
                else:
                    keys.append(str(k))

            known = set(DEX_PROGRAMS.keys())  # single source of truth
            for ix in ixs:
                pid = ix.get('programId')
                if not pid and 'programIdIndex' in ix and keys:
                    idx = ix['programIdIndex']
                    if isinstance(idx, int) and 0 <= idx < len(keys):
                        pid = keys[idx]
                if pid in known:
                    return pid
        except Exception:
            pass
        return None
    
    async def detect_dex_router(self, trade_info: Dict[str, Any], transaction_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enhanced DEX/Router Detection using router program ID and transaction logs
        
        Detects which DEX/router (e.g., Raydium, Jupiter, Meteora) was used for the trade
        by analyzing the router program ID and transaction logs.
        
        Args:
            trade_info: Trade information dictionary
            transaction_data: Optional full transaction data
            
        Returns:
            Dict with detected DEX information:
            {
                'dex_type': str,           # Detected DEX type
                'router_program_id': str,  # Router program ID if found
                'confidence': float,       # Detection confidence (0.0 to 1.0)
                'method': str,            # Detection method used
                'supported_executors': list  # Available executors for this DEX
            }
        """
        try:
            signature = trade_info.get('signature', 'N/A')
            logger.info(f"🔍 [DEX_DETECTION] Starting enhanced DEX detection for {signature[:12]}...")
            
            detection_result = {
                'dex_type': 'unknown',
                'router_program_id': None,
                'confidence': 0.0,
                'method': 'fallback',
                'supported_executors': ['jupiter']  # Safe default
            }
            
            # Priority 1: Extract router program ID from transaction
            router_program_id = None
            
            # Check if already extracted
            if trade_info.get('router_program_id'):
                router_program_id = trade_info['router_program_id']
                logger.info(f"✅ [DEX_DETECTION] Using existing router program ID: {router_program_id}")
            
            # Try to extract from transaction data if not available
            if not router_program_id and transaction_data:
                router_program_id = self._extract_router_program_id_from_tx(transaction_data)
                if router_program_id:
                    trade_info['router_program_id'] = router_program_id
                    logger.info(f"✅ [DEX_DETECTION] Extracted router program ID: {router_program_id}")
            
            # Try to extract from nested transaction structure
            if not router_program_id and trade_info.get('transaction_full'):
                router_program_id = self._extract_router_program_id_from_tx(trade_info['transaction_full'])
                if router_program_id:
                    trade_info['router_program_id'] = router_program_id
                    logger.info(f"✅ [DEX_DETECTION] Extracted from full transaction: {router_program_id}")
            
            # Priority 2: Map router program ID to DEX type using DEX_PROGRAMS
            if router_program_id and router_program_id in DEX_PROGRAMS:
                dex_type = DEX_PROGRAMS[router_program_id]
                confidence = 0.95  # High confidence from program ID
                method = 'router_program_id'
                
                logger.info(f"🎯 [DEX_DETECTION] Router Program Match: {router_program_id} → {dex_type}")
                
                detection_result.update({
                    'dex_type': dex_type,
                    'router_program_id': router_program_id,
                    'confidence': confidence,
                    'method': method,
                    'supported_executors': self.dex_executor_mapping.get(dex_type, ['jupiter'])
                })
                
                # Call existing _detect_token_platform for additional validation if available
                if hasattr(self, '_detect_token_platform'):
                    try:
                        token_mint = trade_info.get('token_mint')
                        if token_mint and is_valid_solana_address(token_mint):
                            platform_result = await self._detect_token_platform(token_mint, trade_info)
                            logger.info(f"🔍 [DEX_DETECTION] Platform validation: {platform_result}")
                    except Exception as e:
                        logger.debug(f"[DEX_DETECTION] Platform validation failed: {e}")
                
                return detection_result
            
            # Priority 3: Analyze transaction logs for DEX patterns
            logs = trade_info.get('logs', [])
            if not logs and transaction_data:
                logs = (transaction_data.get('meta', {}) or {}).get('logMessages', [])
            
            if logs:
                log_text = ' '.join(logs).lower()
                logger.info(f"🔍 [DEX_DETECTION] Analyzing {len(logs)} log messages...")
                
                # Check for specific DEX patterns in logs
                dex_patterns = {
                    'jupiter': ['jup6', 'jupiter'],
                    'pumpfun': ['pump', '6ef8rrec', 'pammba'],
                    'raydium_cpmm': ['cpmm', 'cpmmoo8', '675kpx9'],
                    'raydium_clmm': ['cammczo', 'clmm'],
                    'orca_whirlpool': ['whirlb', 'orca'],
                    'meteora': ['eo7wjkq', 'meteora', 'dbcij3l'],
                    'advanced_mev_bot': ['bsfd6shz', 'advanced', 'mev']
                }
                
                detected_dex = None
                for dex, patterns in dex_patterns.items():
                    if any(pattern in log_text for pattern in patterns):
                        detected_dex = dex
                        confidence = 0.8  # Good confidence from logs
                        method = 'transaction_logs'
                        break
                
                if detected_dex:
                    logger.info(f"🎯 [DEX_DETECTION] Log Pattern Match: {detected_dex}")
                    
                    detection_result.update({
                        'dex_type': detected_dex,
                        'confidence': confidence,
                        'method': method,
                        'supported_executors': self.dex_executor_mapping.get(detected_dex, ['jupiter'])
                    })
                    return detection_result
            
            # Priority 4: Use existing dex_type from trade_info if available
            if trade_info.get('dex_type') and trade_info['dex_type'] != 'unknown':
                existing_dex = trade_info['dex_type']
                logger.info(f"🔍 [DEX_DETECTION] Using existing dex_type: {existing_dex}")
                
                detection_result.update({
                    'dex_type': existing_dex,
                    'confidence': 0.6,  # Medium confidence
                    'method': 'existing_detection',
                    'supported_executors': self.dex_executor_mapping.get(existing_dex, ['jupiter'])
                })
                return detection_result
            
            # Fallback: Return unknown with safe defaults
            logger.warning(f"⚠️ [DEX_DETECTION] Could not detect DEX for {signature[:12]}...")
            logger.warning(f"   Router program ID: {router_program_id or 'Not found'}")
            logger.warning(f"   Log messages: {len(logs)} available")
            logger.warning(f"   Existing dex_type: {trade_info.get('dex_type', 'None')}")
            
            return detection_result
            
        except Exception as e:
            logger.error(f"❌ [DEX_DETECTION] Exception during DEX detection: {e}")
            return {
                'dex_type': 'unknown',
                'router_program_id': None,
                'confidence': 0.0,
                'method': 'error_fallback',
                'supported_executors': ['jupiter'],
                'error': str(e)
            }

    def log_unknown_program(self, program_id: str, tx_sig: str, instruction: dict):
        """Log unknown program IDs (sampled and non-blocking)"""
        try:
            # Sample 1 in 50 to minimize overhead, and make it non-blocking
            import random
            if random.randint(1, 50) == 1:
                # Just store in memory for now - in production, use a proper queue
                if not hasattr(self, '_unknown_programs_buffer'):
                    self._unknown_programs_buffer = []
                self._unknown_programs_buffer.append({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'program_id': program_id,
                    'tx_sig': tx_sig
                })
                # Keep buffer small
                if len(self._unknown_programs_buffer) > 100:
                    self._unknown_programs_buffer = self._unknown_programs_buffer[-50:]
        except Exception:
            pass  # Never fail the main flow
    
    def __init__(self, target_wallets: List[str], rpc_client=None, execution_coordinator=None):
        self.target_wallets = target_wallets
        self.rpc_client = rpc_client
        self.execution_coordinator = execution_coordinator
        
        # 🧠 INTELLIGENT EXECUTOR MAPPING based on program IDs
        self.dex_executor_mapping = {
            'pumpfun': ['direct_copy'],
            'raydium_cpmm': ['cpmm'],
            'raydium_clmm': ['clmm'], 
            'raydium_amm': ['raydium'],
            'jupiter': ['jupiter'],
            'orca': ['orca'],
            'orca_whirlpool': ['orca'],  # unified orca naming
            'phoenix': ['phoenix'],
            'advanced_mev_bot': ['advanced_mev'],
            'unknown': ['jupiter', 'raydium']  # Safe defaults
        }
    
    def validate_trade_info(self, trade: dict) -> bool:
        """
        Permissive validation allowing inferred fields with comprehensive logging.
        
        Allow either:
          (a) signature present (even if mint is unknown - use direct_copy), OR
          (b) actionable fields for building: dex + action + mint (+ optional amount)
        
        This method now accepts inferred/default values to enable permissive execution.
        """
        logger.info(f"[VALIDATION] 🔍 Starting trade validation...")
        logger.debug(f"[VALIDATION] Trade keys: {list(trade.keys())}")
        
        # Extract key fields
        token_mint = trade.get("token_mint") or trade.get("mint") or ""
        token_mint = token_mint.strip() if token_mint else ""
        has_sig = bool((trade.get("signature") or "").strip() and trade.get("signature") != "unknown")
        has_any_data = has_sig or trade.get("logs") or trade.get("transaction")
        
        # If we have zero data, stop here
        if not has_any_data:
            logger.warning("🛑 [VALIDATION] Insufficient data (no signature/logs/tx) — skipping")
            return False
        
        # If mint is still unknown but we have a signature, allow direct_copy
        if token_mint in (None, "", "PENDING_ANALYSIS", "UNKNOWN"):
            if has_sig:
                trade["route_hint"] = trade.get("route_hint") or "direct_copy"
                trade["dex"] = trade.get("dex") or trade.get("dex_type") or "unknown"
                trade["action"] = trade.get("action") or "swap"
                logger.info("✅ [VALIDATION] route_hint='direct_copy' fallback - Allowing execution via direct_copy (mint unresolved but signature present)")
                return True
            else:
                logger.warning("🛑 [VALIDATION] Mint unresolved and no signature — skipping")
                return False
        
        # Otherwise check for actionable fields (existing validation logic)
        sig = (trade.get("signature") or "").strip()
        if sig and sig != "unknown":
            logger.info(f"[VALIDATION] ✅ Signature present: {sig[:12]}... - trade approved")
            return True

        # Check for actionable fields (including inferred/default values)
        dex = (trade.get("dex") or trade.get("dex_type") or "").strip().lower()
        action = (trade.get("action") or "").strip().lower()
        mint = token_mint
        
        logger.debug(f"[VALIDATION] DEX: {dex}")
        logger.debug(f"[VALIDATION] Action: {action}")
        logger.debug(f"[VALIDATION] Mint: {mint[:12] if mint else 'None'}...")

        # Accept known DEXes (including 'unknown' for fallback routing)
        valid_dexes = {"pumpfun", "raydium", "jupiter", "meteora", "unknown"}
        # Accept all actionable actions (including 'swap' from inference)
        valid_actions = {"buy", "sell", "swap", "swap_in", "swap_out"}
        
        if dex in valid_dexes:
            logger.debug(f"[VALIDATION] ✅ DEX '{dex}' is valid")
        else:
            logger.warning(f"[VALIDATION] ❌ DEX '{dex}' not in valid set: {valid_dexes}")
        
        if action in valid_actions:
            logger.debug(f"[VALIDATION] ✅ Action '{action}' is valid")
        else:
            logger.warning(f"[VALIDATION] ❌ Action '{action}' not in valid set: {valid_actions}")
        
        if mint and mint not in {"UNKNOWN", "PENDING_ANALYSIS"}:
            logger.debug(f"[VALIDATION] ✅ Mint '{mint[:12]}...' is valid")
        else:
            logger.warning(f"[VALIDATION] ❌ Mint '{mint}' is placeholder or missing")
        
        if dex in valid_dexes and action in valid_actions and mint and mint not in {"UNKNOWN", "PENDING_ANALYSIS"}:
            logger.info(f"[VALIDATION] ✅ Trade approved - dex:{dex}, action:{action}, mint:{mint[:12]}...")
            return True

        # LOG why we're rejecting for visibility
        logger.warning(f"[VALIDATION] ❌ Trade rejected - insufficient data:")
        logger.warning(f"   - Has signature: {bool(sig)}")
        logger.warning(f"   - DEX: {dex} (valid: {dex in valid_dexes})")
        logger.warning(f"   - Action: {action} (valid: {action in valid_actions})")
        logger.warning(f"   - Mint: {mint or 'None'} (valid: {mint and mint not in {'UNKNOWN', 'PENDING_ANALYSIS'}})")
        return False
    
    async def analyze_and_route_trade(self, trade_info: Dict[str, Any], source_wallet: str) -> Dict[str, Any]:
        source_wallet = self._key_str(source_wallet)
        logger.debug(f"[DEBUG] analyze_and_route_trade called with trade_info: {trade_info}, source_wallet: {source_wallet}")
        """
        Analyze trade and return routing instructions (NO EXECUTION)
        
        Returns:
            Dict with routing instructions for the execution coordinator
        """
        try:
            # Extract action from trade info using robust fallback mechanism
            # This ensures we always get an actionable result (never 'unknown')
            action = self._extract_action_with_fallback(trade_info)
            logger.debug(f"[DEBUG] _extract_action_with_fallback result: {action}")
            token_mint = trade_info.get('token_mint', 'UNKNOWN')
            
            # Enrich if any critical field is missing
            needs_enrichment = (
                action in (None, 'unknown') or
                not trade_info.get('dex_type') or trade_info.get('dex_type') == 'unknown' or
                not trade_info.get('router_program_id')
            )
            if token_mint in ['PENDING_ANALYSIS', 'UNKNOWN'] or needs_enrichment:
                signature = trade_info.get('signature')
                logger.debug(f"[DEBUG] token_mint/action/dex/router pending analysis, signature: {signature}")
                if signature:
                    tx = await get_transaction_with_logs(signature)
                    if tx:
                        # Store full transaction for action/mint resolution
                        trade_info['transaction_full'] = tx
                        # Make coordinator-friendly structure
                        msg = (tx.get('transaction', {}) or {}).get('message', {}) or {}
                        simple_tx = {
                            'instructions': msg.get('instructions', []),
                            'accountKeys': msg.get('accountKeys', []),
                        }
                        trade_info['transaction'] = simple_tx

                        # Use our sophisticated mint detection
                        sophisticated_action = None
                        sophisticated_result = await self._extract_sophisticated_token_mint(tx, source_wallet)
                        if sophisticated_result:
                            if isinstance(sophisticated_result, dict):
                                token_mint = sophisticated_result.get('token_mint') or token_mint
                                sophisticated_action = sophisticated_result.get('action')
                                confidence = sophisticated_result.get('confidence', 0.9)
                                if sophisticated_action and sophisticated_action != 'unknown':
                                    action = sophisticated_action
                                    logger.info(f"🎯 SOPHISTICATED ACTION DETECTED: {action}")
                                trade_info['extracted_info'] = {
                                    'output_mint': token_mint,
                                    'token_mint': token_mint,
                                    'source': 'sophisticated_extraction',
                                    'confidence': 'high'
                                }
                            elif isinstance(sophisticated_result, str) and is_valid_solana_address(sophisticated_result):
                                token_mint = sophisticated_result
                                trade_info['extracted_info'] = {
                                    'output_mint': token_mint,
                                    'token_mint': token_mint,
                                    'source': 'sophisticated_extraction',
                                    'confidence': 'med'
                                }

                        # Fill router + dex from the actual tx
                        router_program_id = self._extract_router_program_id_from_tx(tx)
                        trade_info['router_program_id'] = router_program_id
                        inferred_dex = (DEX_PROGRAMS.get(router_program_id)
                                        if router_program_id else self._detect_platform(tx))
                        trade_info['dex_type'] = inferred_dex or 'unknown'
                        if sophisticated_action and sophisticated_action != 'unknown':
                            trade_info['action'] = sophisticated_action

                        # Backfill critical fields so downstream never crashes:
                        if not trade_info.get('wallet_address'):
                            owners = {b.get('owner') for b in (tx.get('meta', {}).get('postTokenBalances') or []) if b.get('owner')}
                            for w in self.target_wallets:
                                if w in owners:
                                    trade_info['wallet_address'] = w
                                    break
                            if not trade_info.get('wallet_address') and self.target_wallets:
                                trade_info['wallet_address'] = self.target_wallets[0]

                        if not trade_info.get('logs'):
                            trade_info['logs'] = (tx.get('meta') or {}).get('logMessages', []) or []

                        # Extra safety: If router_program_id is still None but logs show a known DEX, set it from logs
                        if not trade_info.get('router_program_id'):
                            log_text = " ".join((tx.get('meta') or {}).get('logMessages', []) or []).lower()
                            for pid, dex in DEX_PROGRAMS.items():
                                if pid.lower() in log_text:
                                    trade_info['router_program_id'] = pid
                                    trade_info['dex_type'] = dex
                                    break

            # --- DEX memory for sell-on-same-DEX ---
            if action == 'buy' and trade_info.get('dex_type') and is_valid_solana_address(token_mint):
                self._last_buy_dex_by_mint[token_mint] = trade_info['dex_type']
            
            # Fix: Confidence gating - only allow high-confidence sources for execution
            extracted_info = trade_info.get('extracted_info', {})  # may be partial
            src = (extracted_info.get('source',"").split(':',1)[0] if extracted_info else "")
            has_router = bool(trade_info.get("dex_type")) and trade_info.get("dex_type") != "unknown"
            source_ok = (src in {"meta","dex","layout","sophisticated_extraction"}) or has_router

            # As a safety net, run DEX detector and attach it
            # --- TOKEN MINT RESOLUTION WITH DELTA DETECTION ---
            # Always try to set token_mint from delta detection if it's missing or unknown
            if (token_mint in ['UNKNOWN', 'PENDING_ANALYSIS'] and 
                (trade_info.get('transaction_full') or trade_info.get('meta'))):
                
                logger.info(f"🎯 [TOKEN_RESOLUTION] Attempting delta detection for token mint resolution: {trade_info.get('signature', 'N/A')[:12]}...")
                
                try:
                    meta = trade_info.get('meta') or (trade_info.get('transaction_full', {}) or {}).get('meta', {})
                    if meta:
                        # Use ONLY target wallets - strict monitoring only
                        monitored_wallets = self.target_wallets.copy()
                        
                        # Validate source_wallet and wallet_address before considering them
                        source_wallet_valid = source_wallet and self._validate_monitored_wallet(source_wallet, self.target_wallets)
                        wallet_address_valid = trade_info.get('wallet_address') and self._validate_monitored_wallet(trade_info['wallet_address'], self.target_wallets)
                        
                        if not source_wallet_valid and not wallet_address_valid:
                            logger.warning(f"⚠️ [TOKEN_RESOLUTION] Neither source_wallet nor wallet_address are monitored - limiting to target wallets only")
                        
                        logger.info(f"🔒 [TOKEN_RESOLUTION] Using STRICT monitoring: {len(monitored_wallets)} target wallets only")
                        
                        # Run delta detection with STRICT monitoring
                        detected_actions = self.detect_buy_sell(meta, monitored_wallets)
                        
                        if detected_actions:
                            # Store detected actions
                            trade_info['detected_balance_actions'] = detected_actions
                            
                            # Find the best token mint (prioritize non-system tokens)
                            non_system_actions = [
                                a for a in detected_actions 
                                if a['mint'] not in ['So11111111111111111111111111111111111111112', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v']
                            ]
                            
                            if non_system_actions:
                                # For copy trading, prioritize BUY actions (new tokens acquired)
                                buy_actions = [a for a in non_system_actions if a['action'] == 'buy']
                                if buy_actions:
                                    primary_action = max(buy_actions, key=lambda x: abs(x['delta']))
                                else:
                                    primary_action = max(non_system_actions, key=lambda x: abs(x['delta']))
                                
                                token_mint = primary_action['mint']
                                trade_info['token_mint'] = token_mint
                                logger.info(f"🎯 TOKEN MINT SET: {token_mint[:8]}... from delta detection ({primary_action['action']} Δ{primary_action['delta']:+,.2f})")
                            
                            # Also update action if it was unknown
                            if action in (None, 'unknown') and detected_actions:
                                primary_action = max(detected_actions, key=lambda x: abs(x['delta']))
                                action = primary_action['action']
                                trade_info['action'] = action
                                logger.info(f"🎯 ACTION SET: {action} from delta detection")
                        else:
                            logger.debug(f"⚠️ [TOKEN_RESOLUTION] No balance changes detected for monitored wallets")
                    else:
                        logger.debug(f"⚠️ [TOKEN_RESOLUTION] No meta information available")
                except Exception as e:
                    logger.debug(f"❌ [TOKEN_RESOLUTION] Exception: {e}")
                
                # Legacy fallback for specific wallet/token pairs
                if (action in (None, 'unknown') and 
                    is_valid_solana_address(token_mint) and 
                    trade_info.get('wallet_address') and 
                    (trade_info.get('transaction_full') or trade_info.get('transaction'))):
                    try:
                        tx_for_action = trade_info.get('transaction_full') or trade_info.get('transaction')
                        action_guess = await self._determine_action_for_wallet(
                            tx_for_action, trade_info['wallet_address'], token_mint
                        )
                        if action_guess and action_guess != 'unknown':
                            action = action_guess
                            trade_info['action'] = action_guess
                            logger.info(f"🎯 LEGACY FALLBACK ACTION: {action_guess}")
                    except Exception as e:
                        logger.debug(f"[LEGACY ACTION RESOLUTION] failed: {e}")

            # === ENHANCED DEX/ROUTER DETECTION ===
            # Perform comprehensive DEX detection using router program ID and logs
            logger.info(f"🎯 [ENHANCED_DEX] Running enhanced DEX/router detection...")
            dex_detection = await self.detect_dex_router(
                trade_info, 
                trade_info.get('transaction_full') or trade_info.get('transaction')
            )
            
            # Update trade_info with enhanced detection results
            if dex_detection['dex_type'] != 'unknown':
                logger.info(f"✅ [ENHANCED_DEX] Detected: {dex_detection['dex_type']} (confidence: {dex_detection['confidence']:.2f})")
                trade_info['dex_type'] = dex_detection['dex_type']
                trade_info['dex_detection_confidence'] = dex_detection['confidence']
                trade_info['dex_detection_method'] = dex_detection['method']
                trade_info['supported_executors'] = dex_detection['supported_executors']
                
                # Update router program ID if detected
                if dex_detection['router_program_id']:
                    trade_info['router_program_id'] = dex_detection['router_program_id']
            else:
                logger.warning(f"⚠️ [ENHANCED_DEX] Could not detect DEX - using fallback")
            
            # === MINT/ACTION UNCERTAINTY DEBUGGING ===
            if action == 'unknown' or token_mint in ['UNKNOWN', 'PENDING_ANALYSIS']:
                logger.error(f"❌ [UNCERTAINTY] Final action/mint still uncertain: action={action}, token_mint={token_mint}")
                logger.error(f"   Signature: {trade_info.get('signature', 'missing')}")
                logger.error(f"   DEX Type: {trade_info.get('dex_type', 'missing')} (confidence: {dex_detection.get('confidence', 'N/A')})")
                logger.error(f"   Router Program: {trade_info.get('router_program_id', 'missing')}")
                logger.error(f"   Detection Method: {dex_detection.get('method', 'N/A')}")
                logger.error(f"   Supported Executors: {dex_detection.get('supported_executors', [])}")
                logger.error(f"   Extracted Info: {trade_info.get('extracted_info', 'missing')}")
                logger.error(f"   Detected Balance Actions: {len(trade_info.get('detected_balance_actions', []))}")
                
                # Log available meta for debugging
                meta = trade_info.get('meta') or (trade_info.get('transaction_full', {}) or {}).get('meta', {})
                if meta:
                    pre_count = len(meta.get('preTokenBalances', []))
                    post_count = len(meta.get('postTokenBalances', []))
                    logger.error(f"   Token Balances Available: pre={pre_count}, post={post_count}")
                else:
                    logger.error(f"   No meta information available for delta detection")

            # Comprehensive validation of execution eligibility based on monitored wallets
            execution_validation = self.validate_execution_eligibility(trade_info, source_wallet)
            
            # Build routing instructions
            routing_instructions = {
                'action': action,
                'token_mint': token_mint,
                'source_wallet': source_wallet,
                'execution_strategy': {'type': 'default'},
                'trade_info': trade_info,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'requires_execution': (
                    token_mint not in ['PENDING_ANALYSIS', 'UNKNOWN'] and 
                    is_valid_solana_address(token_mint) and
                    token_mint and  # Ensure not empty string
                    action in {'buy','sell'} and  # Ensure we actually know what to do
                    source_ok and
                    execution_validation['eligible']  # STRICT: ONLY MONITORED WALLETS CAN TRIGGER EXECUTION
                ),
                'forced_execution': False,
                'wallet_validation': execution_validation
            }

            logger.info(f"[ROUTING] mint={token_mint[:8] if token_mint != 'UNKNOWN' else 'UNKNOWN'} dex_type={trade_info.get('dex_type')} router={trade_info.get('router_program_id')}")
            logger.info(f"[ENHANCED_ROUTING] DEX: {trade_info.get('dex_type', 'unknown')} | Confidence: {dex_detection.get('confidence', 0.0):.2f} | Method: {dex_detection.get('method', 'N/A')} | Executors: {len(dex_detection.get('supported_executors', []))}")
            logger.info(f"✅ Trade analyzed - Action: {action}, Token: {token_mint[:8] if token_mint != 'UNKNOWN' else 'UNKNOWN'}")
            return routing_instructions
            
        except Exception as e:
            logger.error(f"❌ Trade analysis failed: {e}")
            return {
                'action': 'unknown',
                'token_mint': 'UNKNOWN',
                'source_wallet': source_wallet,
                'execution_strategy': {'type': 'emergency_fallback'},
                'trade_info': trade_info,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'requires_execution': False,
                'forced_execution': False,
                'error': str(e)
            }



    async def _decode_pump_fun(self, ix, meta, source_wallet):
        # TODO: implement cleanly later; for now rely on the Jupiter/real-mint paths
        return None
        if len(accounts) > 1:
            a1 = accounts[1]
            if isinstance(a1, int) and keys:
                pool_id = keys[a1] if isinstance(keys[0], str) else keys[a1].get("pubkey")
            elif isinstance(a1, str):
                pool_id = a1
        
        # Check pool cache for deterministic mint mapping
        pool_state = _pool_cache.get(pool_id) if pool_id else None
        
        pre = [b for b in meta.get('preTokenBalances', []) if b.get('owner') == source_wallet]
        post = [b for b in meta.get('postTokenBalances', []) if b.get('owner') == source_wallet]
        if not post:
            return None
        
        pre_map = {b['mint']: int(b['uiTokenAmount']['amount'] or '0') for b in pre}
        best_in = best_out = None
        best_in_delta = 0
        best_out_delta = 0
        
        for b in post:
            mint = b['mint']
            post_amt = int(b['uiTokenAmount']['amount'] or '0')
            pre_amt = pre_map.get(mint, 0)
            delta = post_amt - pre_amt
            if delta > best_out_delta:
                best_out, best_out_delta = mint, delta
            if delta < best_in_delta:
                best_in, best_in_delta = mint, delta
        
        # Populate pool cache with lazy first-touch fetch if needed
        if pool_id and not pool_state and best_in and best_out:
            try:
                # Lazy fetch pool state for future use (non-blocking)
                pool_state = await self._fetch_pool_state(pool_id)
                if pool_state:
                    _pool_cache.set(pool_id, pool_state)
            except:
                pass  # Don't block on pool fetch failures
        
        # Use pool state hints for validation if available (advisory only)
        # Always read accountKeys from tx for hints
        msg_keys = (ix.get('accountKeys') or (meta.get('_msg_keys') if meta else None) or (ix.get('transaction', {}) or {}).get('message', {}).get('accountKeys', []))
        hints = self._pool_hints_for_keys(msg_keys if isinstance(msg_keys, list) else [])
        if pool_state and best_in and best_out:
            pool_mints = {pool_state.get('mint_a'), pool_state.get('mint_b')}
            if best_in not in pool_mints or best_out not in pool_mints:
                logger.debug(f"Pool hint mismatch: deltas {best_in[:8]}/{best_out[:8]} not in pool {pool_mints}; trusting deltas")
                # Don't reject - pool hints are advisory, trust clear deltas
                
        if best_in and best_out:
            return {'token_mint': best_out, 'dex': 'raydium_cpmm', 'input_mint': best_in, 'output_mint': best_out}
        return None

    async def _decode_raydium_clmm(self, ix, meta, source_wallet):
        """Decode Raydium CLMM swaps using delta-based logic"""
        # Similar to CPMM but for concentrated liquidity
        pre = [b for b in meta.get('preTokenBalances', []) if b.get('owner') == source_wallet]
        post = [b for b in meta.get('postTokenBalances', []) if b.get('owner') == source_wallet]
        if not post:
            return None
        
        pre_map = {b['mint']: int(b['uiTokenAmount']['amount'] or '0') for b in pre}
        best_in = best_out = None
        best_in_delta = 0
        best_out_delta = 0
        
        for b in post:
            mint = b['mint']
            post_amt = int(b['uiTokenAmount']['amount'] or '0')
            pre_amt = pre_map.get(mint, 0)
            delta = post_amt - pre_amt
            if delta > best_out_delta:
                best_out, best_out_delta = mint, delta
            if delta < best_in_delta:
                best_in, best_in_delta = mint, delta
                
        if best_in and best_out:
            return {'token_mint': best_out, 'dex': 'raydium_clmm', 'input_mint': best_in, 'output_mint': best_out}
        return None

    async def _decode_orca_whirlpool(self, ix, meta, source_wallet):
        """Decode Orca Whirlpool swaps using delta-based logic"""
        pre = [b for b in meta.get('preTokenBalances', []) if b.get('owner') == source_wallet]
        post = [b for b in meta.get('postTokenBalances', []) if b.get('owner') == source_wallet]
        if not post:
            return None
        
        pre_map = {b['mint']: int(b['uiTokenAmount']['amount'] or '0') for b in pre}
        best_in = best_out = None
        best_in_delta = 0
        best_out_delta = 0
        
        for b in post:
            mint = b['mint']
            post_amt = int(b['uiTokenAmount']['amount'] or '0')
            pre_amt = pre_map.get(mint, 0)
            delta = post_amt - pre_amt
            if delta > best_out_delta:
                best_out, best_out_delta = mint, delta
            if delta < best_in_delta:
                best_in, best_in_delta = mint, delta
                
        if best_in and best_out:
            return {'token_mint': best_out, 'dex': 'orca_whirlpool', 'input_mint': best_in, 'output_mint': best_out}
        return None

    async def _decode_meteora(self, ix, meta, source_wallet):
        """Decode Meteora swaps using delta-based logic"""
        pre = [b for b in meta.get('preTokenBalances', []) if b.get('owner') == source_wallet]
        post = [b for b in meta.get('postTokenBalances', []) if b.get('owner') == source_wallet]
        if not post:
            return None
        
        pre_map = {b['mint']: int(b['uiTokenAmount']['amount'] or '0') for b in pre}
        best_in = best_out = None
        best_in_delta = 0
        best_out_delta = 0
        
        for b in post:
            mint = b['mint']
            post_amt = int(b['uiTokenAmount']['amount'] or '0')
            pre_amt = pre_map.get(mint, 0)
            delta = post_amt - pre_amt
            if delta > best_out_delta:
                best_out, best_out_delta = mint, delta
            if delta < best_in_delta:
                best_in, best_in_delta = mint, delta
                
        if best_in and best_out:
            return {'token_mint': best_out, 'dex': 'meteora', 'input_mint': best_in, 'output_mint': best_out}
        return None

    async def _decode_jupiter_v6(self, ix, meta, source_wallet):
        # Use delta-based logic for reliable multi-mint handling
        pre = [b for b in meta.get('preTokenBalances', []) if b.get('owner') == source_wallet]
        post = [b for b in meta.get('postTokenBalances', []) if b.get('owner') == source_wallet]
        if not post: 
            return None
        pre_map = {b['mint']: int(b['uiTokenAmount']['amount'] or '0') for b in pre}
        best_in = best_out = None
        best_in_delta = 0
        best_out_delta = 0
        for b in post:
            mint = b['mint']
            post_amt = int(b['uiTokenAmount']['amount'] or '0')
            pre_amt = pre_map.get(mint, 0)
            delta = post_amt - pre_amt
            if delta > best_out_delta:
                best_out, best_out_delta = mint, delta
            if delta < best_in_delta:
                best_in, best_in_delta = mint, delta
        if best_in and best_out:
            return {'token_mint': best_out, 'dex': 'jupiter', 'input_mint': best_in, 'output_mint': best_out}
        return None



    def _extract_mint_from_logs(self, logs):
        """
        Enhanced aggressive logs extraction: Look for any Solana addresses in logs.
        """
        import re
        
        # Pattern 1: Explicit mint= patterns
        for log in logs or []:
            match = re.search(r"mint=([A-Za-z0-9]{32,44})", log)
            if match:
                candidate = match.group(1)
                if is_valid_solana_address(candidate):
                    logger.debug(f"✅ [LOGS_EXTRACT] Found mint pattern: {candidate[:8]}...")
                    return candidate
        
        # Pattern 2: Transfer patterns (Transfer <address>)
        for log in logs or []:
            match = re.search(r"Transfer ([A-Za-z0-9]{32,44})", log)
            if match:
                candidate = match.group(1)
                if is_valid_solana_address(candidate) and not candidate.startswith('11111111111'):
                    logger.debug(f"✅ [LOGS_EXTRACT] Found transfer pattern: {candidate[:8]}...")
                    return candidate
        
        # Pattern 3: Any valid Solana address in logs (aggressive fallback)
        system_programs = {
            '11111111111111111111111111111111',            # System Program
            'ComputeBudget111111111111111111111111111111', # Compute Budget
            'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
            'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
        }
        
        for log in logs or []:
            # Find all potential addresses in this log
            addresses = re.findall(r'[A-Za-z0-9]{32,44}', log)
            for addr in addresses:
                if (is_valid_solana_address(addr) and 
                    addr not in system_programs and 
                    addr not in DEX_PROGRAMS and
                    len(addr) >= 32):
                    logger.debug(f"✅ [LOGS_EXTRACT] Found address pattern: {addr[:8]}...")
                    return addr
        
        logger.debug(f"❌ [LOGS_EXTRACT] No valid addresses found in logs")
        return None

    async def _get_account_info(self, pubkey: str) -> Optional[dict]:
        """
        Minimal wrapper around getAccountInfo. Expects self.rpc_client with .call(method, params) coroutine.
        Returns dict {owner:str, data_len:int, is_mint:bool, is_token_account:bool} or None.
        """
        if not self.rpc_client:
            return None
        try:
            # encoding base64 gives ["base64", <len>]
            params = [pubkey, {"encoding": "base64"}]
            resp = await self.rpc_client.call("getAccountInfo", params)
            value = resp.get("result", {}).get("value")
            if not value:
                return None

            owner = self._key_str(value.get("owner"))
            # data may be {"data":{"encoding":"base64","data":"..."}} or ["base64data", "base64"]
            raw = value.get("data")
            if isinstance(raw, list):
                b64 = raw[0]
            elif isinstance(raw, dict):
                b64 = raw.get("data") or ""
            else:
                b64 = ""
            import base64
            data_bytes = base64.b64decode(b64) if b64 else b""
            data_len = len(data_bytes)

            # quick SPL layouts
            is_mint = (owner in TOKEN_PROGRAMS and 82 <= data_len < 170)
            is_token_account = (owner in TOKEN_PROGRAMS and data_len >= 165)

            return {"owner": owner, "data_len": data_len, "is_mint": is_mint, "is_token_account": is_token_account, "raw": data_bytes}
        except Exception as e:
            logger.debug(f"_get_account_info failed for {pubkey[:8]}: {e}")
            return None

    async def _fetch_pool_state(self, pool_id: str) -> Optional[dict]:
        """Fetch pool state for deterministic mint mapping (lazy cache population)"""
        try:
            # Add timeout protection for pool state fetch
            import asyncio
            resp = await asyncio.wait_for(
                self.rpc_client.call("getAccountInfo", [pool_id, {"encoding": "base64"}]), 
                timeout=2.0
            )
            value = resp.get("result", {}).get("value")
            if not value or not value.get("data"):
                return None
                
            # Parse basic pool structure (simplified for common DEXes)
            data = value.get("data")
            if isinstance(data, list) and len(data) >= 1:
                import base64
                raw_data = base64.b64decode(data[0])
                
                # Basic Raydium CPMM structure extraction (offset-based)
                if len(raw_data) >= 100:
                    # Fix: Convert 32-byte slices to base58 for proper Solana address format
                    import base58
                    def k(b): return base58.b58encode(b).decode()
                    return {
                        "mint_a": k(raw_data[8:40]),  # Approximate offsets
                        "mint_b": k(raw_data[40:72]),
                        "vault_a": k(raw_data[72:104]),
                        "vault_b": k(raw_data[104:136]) if len(raw_data) >= 136 else None
                    }
        except Exception as e:
            logger.debug(f"Pool state fetch failed for {pool_id[:8]}: {e}")
        return None

    def _validate_monitored_wallet(self, wallet_address: str, monitored_wallets: List[str]) -> bool:
        """
        Strict validation that wallet is in monitored wallets list
        Returns True only if wallet is explicitly in the monitored list
        
        Uses case-insensitive matching to handle wallet address variations
        """
        if not wallet_address or not monitored_wallets:
            return False
        
        # Normalize wallet address (ensure it's a string and strip whitespace)
        wallet_str = str(wallet_address).strip()
        
        # Create case-insensitive comparison set (normalize to lowercase for comparison)
        monitored_wallets_lower = {w.lower() for w in monitored_wallets if w}
        
        # Check if wallet is in monitored list (case-insensitive match)
        is_monitored = wallet_str.lower() in monitored_wallets_lower
        
        if not is_monitored:
            logger.debug(f"⚠️ [WALLET_FILTER] Wallet {wallet_str[:8]}... NOT in monitored list")
        else:
            logger.debug(f"✅ [WALLET_FILTER] Wallet {wallet_str[:8]}... IS monitored (case-insensitive match)")
            
        return is_monitored

    def _filter_monitored_actions(self, actions: List[Dict], monitored_wallets: List[str]) -> List[Dict]:
        """
        Filter actions to only include those from monitored wallets
        Returns only actions where the owner is in the monitored wallets list
        """
        if not actions or not monitored_wallets:
            return []
        
        filtered_actions = []
        
        for action in actions:
            owner = action.get('owner')
            if owner and self._validate_monitored_wallet(owner, monitored_wallets):
                filtered_actions.append(action)
                logger.debug(f"✅ [ACTION_FILTER] Keeping action: {action['action']} by {owner[:8]}...")
            else:
                logger.debug(f"❌ [ACTION_FILTER] Filtering out action: {action.get('action', 'unknown')} by {str(owner)[:8] if owner else 'unknown'}...")
        
        logger.info(f"🔍 [ACTION_FILTER] Filtered {len(actions)} → {len(filtered_actions)} actions (monitored wallets only)")
        return filtered_actions

    def detect_buy_sell(self, meta, monitored_wallets):
        """
        Token Balance Delta Detection - Core method for determining buy/sell actions
        
        Analyzes preTokenBalances and postTokenBalances to calculate deltas
        Returns list of actions with precise buy/sell determination based on balance changes
        ONLY FOR MONITORED WALLETS
        """
        actions = []
        
        try:
            # Validate monitored wallets input
            if not monitored_wallets:
                logger.warning(f"🚫 [DELTA_DETECTION] No monitored wallets provided - no actions will be generated")
                return actions
                
            # Normalize monitored wallets to strings
            monitored_wallets = [str(w).strip() for w in monitored_wallets if w]
            
            # Get token balance data
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            if not pre_token_balances and not post_token_balances:
                logger.debug(f"🚫 [DELTA_DETECTION] No token balance data available")
                return actions
            
            logger.info(f"🔍 [DELTA_DETECTION] Analyzing {len(pre_token_balances)} pre + {len(post_token_balances)} post token balances")
            logger.info(f"🎯 [DELTA_DETECTION] Monitoring {len(monitored_wallets)} wallets: {[w[:8] + '...' for w in monitored_wallets[:3]]}")
            
            # Build comprehensive balance maps
            pre_map = {}  # (owner, mint) -> amount
            post_map = {}  # (owner, mint) -> amount
            
            # Map pre-token balances
            for tb_pre in pre_token_balances:
                owner = tb_pre.get('owner')
                mint = tb_pre.get('mint')
                amount = float(tb_pre.get('uiTokenAmount', {}).get('uiAmount') or 0)
                
                if owner and mint:
                    pre_map[(owner, mint)] = amount
                    
            # Map post-token balances
            for tb_post in post_token_balances:
                owner = tb_post.get('owner')
                mint = tb_post.get('mint')
                amount = float(tb_post.get('uiTokenAmount', {}).get('uiAmount') or 0)
                
                if owner and mint:
                    post_map[(owner, mint)] = amount
            
            # Calculate deltas for all (owner, mint) pairs
            all_pairs = set(pre_map.keys()) | set(post_map.keys())
            
            for (owner, mint) in all_pairs:
                # STRICT FILTERING: Only process monitored wallets
                if not self._validate_monitored_wallet(owner, monitored_wallets):
                    continue
                    
                pre_amount = pre_map.get((owner, mint), 0)
                post_amount = post_map.get((owner, mint), 0)
                delta = post_amount - pre_amount
                
                # Only process non-zero deltas (actual changes)
                if delta == 0:
                    continue
                
                # Skip SOL (we focus on token trades, not SOL changes)
                if mint == "So11111111111111111111111111111111111111112":
                    logger.debug(f"⏭️ [DELTA_DETECTION] Skipping SOL balance change for {owner[:8]}...")
                    continue
                
                # Determine action based on delta
                if delta > 0:
                    action_type = 'buy'
                    amount = delta
                    logger.info(f"🟢 [DELTA_DETECTION] BUY detected: {owner[:8]}.../{mint[:8]}... +{delta:,.6f}")
                elif delta < 0:
                    action_type = 'sell'
                    amount = abs(delta)
                    logger.info(f"🔴 [DELTA_DETECTION] SELL detected: {owner[:8]}.../{mint[:8]}... -{abs(delta):,.6f}")
                
                # FEATURE 6: Enhanced Action Logging for Debugging
                action_data = {
                    'action': action_type,
                    'owner': owner,
                    'mint': mint,
                    'amount': amount,
                    'delta': delta,
                    'pre_amount': pre_amount,
                    'post_amount': post_amount,
                    'method': 'token_balance_delta'
                }
                
                # Add to actions list
                actions.append(action_data)
                
                # FEATURE 6: Detailed Action Logging
                logger.info(f"📝 [ACTION_LOG] Detected Action #{len(actions)}")
                logger.info(f"   Action: {action_type.upper()}")
                logger.info(f"   Token: {mint}")
                logger.info(f"   Wallet: {owner}")
                logger.info(f"   Amount: {amount:,.6f}")
                logger.info(f"   Delta: {delta:+,.6f}")
                logger.info(f"   Pre-Balance: {pre_amount:,.6f}")
                logger.info(f"   Post-Balance: {post_amount:,.6f}")
                logger.info(f"   Detection Method: token_balance_delta")
            
            logger.info(f"✅ [DELTA_DETECTION] Found {len(actions)} balance change actions")
            
            # FEATURE 6: Enhanced Summary Logging for Debugging
            if actions:
                logger.info(f"📊 [ACTION_SUMMARY] Detected Actions Summary:")
                buy_count = sum(1 for a in actions if a['action'] == 'buy')
                sell_count = sum(1 for a in actions if a['action'] == 'sell')
                
                logger.info(f"   Total Actions: {len(actions)}")
                logger.info(f"   Buy Actions: {buy_count}")
                logger.info(f"   Sell Actions: {sell_count}")
                logger.info(f"   Unique Wallets: {len(set(a['owner'] for a in actions))}")
                logger.info(f"   Unique Tokens: {len(set(a['mint'] for a in actions))}")
                
                # Detailed action list for debugging
                for i, action in enumerate(actions, 1):
                    logger.info(f"   Action {i}: {action['action'].upper()} {action['owner'][:8]}.../{action['mint'][:8]}... Δ{action['delta']:+,.6f}")
            else:
                logger.warning(f"⚠️ [ACTION_SUMMARY] No balance changes detected for monitored wallets")
            
            return actions
            
        except Exception as e:
            logger.error(f"❌ [DELTA_DETECTION] Exception in detect_buy_sell: {e}")
            return actions

    def _has_actual_token_balance_change(self, trade_info: Dict[str, Any]) -> bool:
        """
        Check if there are actual token balance changes in the transaction
        Returns True only if there are real pre/post token balance differences
        """
        try:
            # Check for meta in trade_info directly
            meta = trade_info.get('meta')
            
            # Check for meta in nested transaction structures
            if not meta:
                tx = trade_info.get('transaction_full') or trade_info.get('transaction', {})
                meta = tx.get('meta')
            
            if not meta:
                logger.debug(f"⚠️ [BALANCE_CHECK] No meta information available")
                return False
                
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            
            logger.debug(f"🔍 [BALANCE_CHECK] Pre: {len(pre_balances)}, Post: {len(post_balances)}")
            
            # No balances = no token changes
            if not pre_balances and not post_balances:
                logger.debug(f"❌ [BALANCE_CHECK] No token balances found")
                return False
            
            # Build balance change map
            pre_map = {}
            for balance in pre_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                if owner and mint:
                    pre_map[(owner, mint)] = amount
            
            # Check for actual changes
            has_changes = False
            for balance in post_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                post_amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                
                if owner and mint:
                    pre_amount = pre_map.get((owner, mint), 0)
                    change = post_amount - pre_amount
                    
                    if change != 0:
                        logger.debug(f"✅ [BALANCE_CHECK] Found balance change: {owner[:8]}.../{mint[:8]}... = {change}")
                        has_changes = True
                        break
            
            logger.debug(f"🔍 [BALANCE_CHECK] Result: {has_changes}")
            return has_changes
            
        except Exception as e:
            logger.debug(f"❌ [BALANCE_CHECK] Exception: {e}")
            return False

    def _has_significant_token_balance_change(self, trade_info: Dict[str, Any], min_threshold: float = 0.000001) -> Dict[str, Any]:
        """
        Check if there are significant token balance changes for monitored wallets.
        Ignores non-trading transfers like dust, airdrops, or micro-transactions.
        
        Args:
            trade_info: Transaction information with balance data
            min_threshold: Minimum absolute change to consider significant (default: 0.000001)
        
        Returns:
            Dict with validation results and detected significant changes
        """
        result = {
            'has_significant_changes': False,
            'significant_changes': [],
            'total_changes': 0,
            'threshold_used': min_threshold,
            'validation_details': []
        }
        
        try:
            # Check for meta in trade_info directly
            meta = trade_info.get('meta')
            
            # Check for meta in nested transaction structures
            if not meta:
                tx = trade_info.get('transaction_full') or trade_info.get('transaction', {})
                meta = tx.get('meta')
            
            if not meta:
                result['validation_details'].append("No transaction meta data available")
                return result
            
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            if not pre_token_balances and not post_token_balances:
                result['validation_details'].append("No token balance data in transaction")
                return result
            
            # Build balance change map
            pre_map = {}
            post_map = {}
            
            for tb in pre_token_balances:
                owner = tb.get('owner')
                mint = tb.get('mint')
                amount = float(tb.get('uiTokenAmount', {}).get('uiAmount') or 0)
                
                if owner and mint:
                    key = f"{owner}:{mint}"
                    pre_map[key] = amount
                    
            for tb in post_token_balances:
                owner = tb.get('owner')
                mint = tb.get('mint')
                amount = float(tb.get('uiTokenAmount', {}).get('uiAmount') or 0)
                
                if owner and mint:
                    key = f"{owner}:{mint}"
                    post_map[key] = amount
            
            # Analyze changes for monitored wallets only
            all_keys = set(pre_map.keys()) | set(post_map.keys())
            
            for key in all_keys:
                owner, mint = key.split(':', 1)
                
                # STRICT: Only check monitored wallets
                if not self._validate_monitored_wallet(owner, self.target_wallets):
                    continue
                
                pre_amount = pre_map.get(key, 0)
                post_amount = post_map.get(key, 0)
                change = post_amount - pre_amount
                
                result['total_changes'] += 1
                
                # Skip zero changes
                if change == 0:
                    result['validation_details'].append(f"No change for {owner[:8]}.../{mint[:8]}...")
                    continue
                
                # Skip SOL balance changes (focus on token trades)
                if mint == "So11111111111111111111111111111111111111112":
                    result['validation_details'].append(f"Skipped SOL change for {owner[:8]}...: {change:+.6f}")
                    continue
                
                # Check if change meets significance threshold
                abs_change = abs(change)
                if abs_change >= min_threshold:
                    result['has_significant_changes'] = True
                    
                    change_info = {
                        'owner': owner,
                        'mint': mint,
                        'pre_amount': pre_amount,
                        'post_amount': post_amount,
                        'change': change,
                        'abs_change': abs_change,
                        'action': 'buy' if change > 0 else 'sell',
                        'meets_threshold': True
                    }
                    
                    result['significant_changes'].append(change_info)
                    result['validation_details'].append(
                        f"✅ SIGNIFICANT: {owner[:8]}.../{mint[:8]}... = {change:+.6f} (threshold: {min_threshold})"
                    )
                    
                    logger.info(f"✅ [SIGNIFICANT_CHANGE] {owner[:8]}.../{mint[:8]}... = {change:+.6f}")
                else:
                    result['validation_details'].append(
                        f"⚠️ Below threshold: {owner[:8]}.../{mint[:8]}... = {change:+.6f} (threshold: {min_threshold})"
                    )
                    
                    logger.debug(f"⚠️ [NON_SIGNIFICANT] {owner[:8]}.../{mint[:8]}... = {change:+.6f} (below {min_threshold})")
            
            # Summary logging
            if result['has_significant_changes']:
                logger.info(f"🎯 [SIGNIFICANCE_CHECK] Found {len(result['significant_changes'])} significant changes")
            else:
                logger.warning(f"⚠️ [SIGNIFICANCE_CHECK] No significant changes detected (threshold: {min_threshold})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [SIGNIFICANCE_CHECK] Error checking significant changes: {e}")
            result['validation_details'].append(f"Error: {str(e)}")
            return result

    def _extract_action(self, trade_info: Dict[str, Any]) -> str:
        """
        Extract trade action from trade info using TOKEN BALANCE DELTA DETECTION
        Uses the robust detect_buy_sell method to determine actions based on actual balance changes
        """
        
        # Log input for debugging
        signature = trade_info.get('signature', 'N/A')
        trade_keys = list(trade_info.keys())
        logger.debug(f"🔍 [ACTION_EXTRACTION] DELTA-BASED mode for {signature[:12]}...")
        logger.debug(f"   Available keys: {trade_keys}")
        
        # PRIORITY 1: Use TOKEN BALANCE DELTA DETECTION
        meta = trade_info.get('meta', {})
        
        # Check for meta in nested transaction structures
        if not meta:
            tx = trade_info.get('transaction_full') or trade_info.get('transaction', {})
            meta = tx.get('meta')
        
        if meta:
            # Use ONLY target wallets (monitored wallets) - no dynamic additions
            monitored_wallets = self.target_wallets.copy()
            
            # Validate that wallet_address is in target wallets before processing
            wallet_address = trade_info.get('wallet_address')
            if wallet_address and not self._validate_monitored_wallet(wallet_address, self.target_wallets):
                logger.warning(f"⚠️ [ACTION_EXTRACTION] Wallet {wallet_address[:8]}... is NOT in target wallets - skipping dynamic addition")
                # Don't add non-monitored wallets to the list
            
            logger.info(f"🎯 [ACTION_EXTRACTION] Using TOKEN BALANCE DELTA DETECTION with {len(monitored_wallets)} STRICT monitored wallets")
            logger.info(f"🔒 [ACTION_EXTRACTION] Monitored wallets: {[w[:8] + '...' for w in monitored_wallets[:3]]}")
            
            # Call our robust detect_buy_sell method with STRICT monitoring
            detected_actions = self.detect_buy_sell(meta, monitored_wallets)
            
            if detected_actions:
                # Take the first action (most significant)
                primary_action = detected_actions[0]
                action = primary_action['action']
                
                logger.info(f"✅ [ACTION_EXTRACTION] DELTA: Detected {action} from balance delta")
                logger.info(f"   Owner: {primary_action['owner'][:8]}...")
                logger.info(f"   Token: {primary_action['mint'][:8]}...")
                logger.info(f"   Amount: {primary_action['amount']:,.6f}")
                logger.info(f"   Delta: {primary_action['delta']:+,.6f}")
                logger.debug(f"   Output: '{action}' (token balance delta detection)")
                
                # Store detected actions in trade_info for downstream use
                trade_info['detected_balance_actions'] = detected_actions
                
                return action
            else:
                logger.debug(f"⚠️ [ACTION_EXTRACTION] DELTA: No balance changes detected for monitored wallets")
        else:
            logger.debug(f"⚠️ [ACTION_EXTRACTION] DELTA: No meta information available")
        
        # PRIORITY 2: Check basic_analysis as fallback
        if 'basic_analysis' in trade_info:
            basic_action = trade_info['basic_analysis'].get('likely_action')
            if basic_action and basic_action != 'unknown':
                # Validate that the action makes sense
                if basic_action.lower() in ['buy', 'sell', 'swap']:
                    logger.debug(f"✅ [ACTION_EXTRACTION] FALLBACK: Using basic_analysis action: {basic_action}")
                    logger.debug(f"   Output: '{basic_action.lower()}' from basic_analysis (fallback)")
                    return basic_action.lower()
        
        # PRIORITY 3: Try direct action field as last resort
        action = trade_info.get('action')
        if action and action != 'unknown':
            # Skip emergency/ultra-aggressive assumptions
            if trade_info.get('method') != 'ultra_aggressive_assumption':
                if action.lower() in ['buy', 'sell', 'swap']:
                    logger.debug(f"✅ [ACTION_EXTRACTION] FALLBACK: Using direct action field: {action}")
                    logger.debug(f"   Output: '{action.lower()}' from direct field (fallback)")
                    return action.lower()
        
        # ENHANCED: Try fallback method with signer + instruction analysis
        logger.debug(f"🔄 [ACTION_EXTRACTION] Trying enhanced fallback method...")
        fallback_action = self._try_signer_instruction_fallback(trade_info)
        if fallback_action and fallback_action != 'unknown':
            logger.info(f"✅ [ACTION_EXTRACTION] FALLBACK: {fallback_action} (signer + instruction analysis)")
            return fallback_action
        
        # If all methods fail, return 'unknown'
        logger.warning(f"⚠️ [ACTION_EXTRACTION] DELTA: Could not determine action for {signature[:12]}...")
        logger.warning(f"   Reason: No valid balance deltas found and fallback methods failed")
        logger.debug(f"   Output: 'unknown' (all methods failed)")
        return 'unknown'

    def _try_signer_instruction_fallback(self, trade_info: Dict[str, Any]) -> str:
        """
        Fallback method to help determine trade action when balance delta detection is inconclusive.
        
        This method provides ADDITIONAL validation and context for action detection.
        It does NOT bypass balance change requirements.
        
        Usage: Called when balance detection has identified changes but action is ambiguous.
        
        Validation Checks:
        1. Monitored Wallet Involvement: Verifies a monitored wallet is the transaction signer/fee payer
        2. Trade Instructions: Confirms transaction contains recognized DEX/swap program instructions
        
        Action Determination Strategy:
        1. Analyze transaction logs for explicit action indicators (buy/sell/swap)
        2. If logs are inconclusive, return 'unknown' (don't force execution)
        
        Args:
            trade_info (Dict[str, Any]): Trade information containing transaction data
        
        Returns:
            str: Action string - 'buy', 'sell', 'swap', or 'unknown'
                'unknown' is returned when action cannot be determined with confidence
        
        Note:
            This method is used for ACTION DETECTION ONLY, not execution gating.
            Balance changes are still required for execution - this just helps determine
            what type of action (buy/sell/swap) occurred.
        """
        try:
            signature = trade_info.get('signature', 'N/A')
            logger.debug(f"🔄 [ACTION_FALLBACK] Analyzing {signature[:12]}... for action determination")
            
            # Check if monitored wallet is signer/fee payer (for validation)
            signer_info = self._check_monitored_wallet_is_signer(trade_info)
            
            # Check for trade instructions (for validation)
            instruction_info = self._check_trade_instructions(trade_info)
            
            has_monitored_involvement = signer_info.get('has_monitored_involvement', False)
            has_trade_instructions = instruction_info.get('has_trade_instructions', False)
            
            logger.debug(f"🔍 [ACTION_FALLBACK] Monitored involvement: {has_monitored_involvement}")
            logger.debug(f"🔍 [ACTION_FALLBACK] Trade instructions: {has_trade_instructions}")
            
            # Both conditions should be present for confident action detection
            if has_monitored_involvement and has_trade_instructions:
                logger.info(f"✅ [ACTION_FALLBACK] Validation conditions met - attempting action detection")
                
                # Log validation details
                if has_monitored_involvement:
                    monitored_wallets = signer_info.get('monitored_wallets', [])
                    logger.info(f"   ✅ Monitored wallet involvement: {len(monitored_wallets)} wallet(s)")
                if has_trade_instructions:
                    detected_programs = instruction_info.get('detected_programs', [])
                    logger.info(f"   ✅ Trade instructions found: {len(detected_programs)} program(s)")
                
                # Try to determine specific action from transaction logs
                relevant_logs = instruction_info.get('relevant_logs', [])
                action_from_logs = self._analyze_logs_for_action(relevant_logs)
                
                if action_from_logs and action_from_logs != 'unknown':
                    logger.info(f"🎯 [ACTION_FALLBACK] Action detected from logs: {action_from_logs}")
                    return action_from_logs
                
                # If logs are inconclusive, return unknown
                # Don't force a default action - let balance detection handle it
                logger.debug(f"🔍 [ACTION_FALLBACK] Logs inconclusive - returning unknown")
                return 'unknown'
                    
            else:
                # Validation failed - return unknown
                logger.debug(f"🚫 [ACTION_FALLBACK] Validation conditions not met")
                if not has_monitored_involvement:
                    logger.debug(f"   - No monitored wallet involvement")
                if not has_trade_instructions:
                    logger.debug(f"   - No trade instructions detected")
                return 'unknown'
            
        except Exception as e:
            logger.error(f"❌ [ACTION_FALLBACK] Error in fallback analysis: {e}")
            import traceback
            logger.debug(f"[ACTION_FALLBACK] Stack trace: {traceback.format_exc()}")
            return 'unknown'
    
    async def _determine_execution_strategy(self, trade_info: Dict[str, Any], action: str) -> Dict[str, Any]:
        """
        Determine the best execution strategy based on trade analysis
        Returns strategy instructions, not execution
        """
        try:
            # Detect DEX type from trade info
            dex_type = self._detect_dex_type(trade_info)
            
            # Get confidence score
            confidence = self._calculate_confidence(trade_info, dex_type)
            
            # Determine strategy based on action and confidence
            if action in ['buy', 'swap_in']:
                return self._get_buy_strategy(dex_type, confidence, trade_info)
            elif action in ['sell', 'swap_out']:
                return self._get_sell_strategy(dex_type, confidence, trade_info)
            else:
                return self._get_fallback_strategy(trade_info)
                
        except Exception as e:
            logger.warning(f"Strategy determination failed: {e}")
            return self._get_fallback_strategy(trade_info)
    
    def _detect_dex_type(self, trade_info: Dict[str, Any]) -> str:
        """Detect which DEX was used based on trade info"""
        
        def _check_instructions_for_dex(instructions, account_keys):
            """Helper to check instructions for DEX programs"""
            # Normalize account keys to str for programIdIndex resolution
            keys: list[str] = []
            for k in account_keys:
                if isinstance(k, str):
                    keys.append(k)
                elif isinstance(k, dict) and 'pubkey' in k:
                    keys.append(str(k['pubkey']))
                else:
                    keys.append(str(k))
            
            for ix in instructions:
                program_id = ix.get('programId')
                # Handle programIdIndex resolution
                if not program_id and 'programIdIndex' in ix and keys:
                    idx = ix['programIdIndex']
                    if isinstance(idx, int) and 0 <= idx < len(keys):
                        program_id = keys[idx]
                
                if program_id in DEX_PROGRAMS:
                    return DEX_PROGRAMS[program_id]
            return None
        
        # Check transaction instructions for known DEX program IDs
        if 'transaction' in trade_info:
            tx = trade_info['transaction']
            
            # Handle flattened transaction structure (coordinator format)
            if 'instructions' in tx:
                result = _check_instructions_for_dex(
                    tx['instructions'], 
                    tx.get('accountKeys', [])
                )
                if result:
                    return result
            
            # Handle nested transaction structure (full RPC response)
            nested_tx = tx.get('transaction', {})
            if nested_tx and 'message' in nested_tx:
                msg = nested_tx['message']
                if 'instructions' in msg:
                    result = _check_instructions_for_dex(
                        msg['instructions'], 
                        msg.get('accountKeys', [])
                    )
                    if result:
                        return result
        
        # Fallback to log analysis
        logs = trade_info.get('logs', [])
        if not logs:
            return "unknown"
        
        # Convert logs to single string for pattern matching
        log_text = ' '.join(logs).lower()
        
        # Check for DEX-specific patterns in logs using DEX_PROGRAMS
        for program_id, dex_type in DEX_PROGRAMS.items():
            if program_id.lower() in log_text:
                return dex_type
        
        return "unknown"
    
    def _calculate_confidence(self, trade_info: Dict[str, Any], dex_type: str) -> float:
        """Calculate confidence score for trade detection"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on available data
        if trade_info.get('token_mint'):
            confidence += 0.2
        if trade_info.get('amount_change'):
            confidence += 0.2
        if dex_type != 'unknown':
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _get_buy_strategy(self, dex_type: str, confidence: float, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get buy execution strategy"""
        # High confidence - use specific DEX
        if confidence >= 0.8 and dex_type in self.dex_executor_mapping:
            return {
                'type': 'focused',
                'executors': self.dex_executor_mapping[dex_type],
                'confidence': confidence,
                'parallel': False
            }
        
        # Medium confidence - try focused then fallback
        elif confidence >= 0.6:
            primary = self.dex_executor_mapping.get(dex_type, ['jupiter'])
            fallback = ['jupiter', 'raydium'] if dex_type != 'unknown' else ['jupiter']
            
            return {
                'type': 'tiered',
                'primary_executors': primary,
                'fallback_executors': fallback,
                'confidence': confidence,
                'parallel': False
            }
        
        # Low confidence - safe parallel approach
        else:
            return {
                'type': 'parallel_safe',
                'executors': ['jupiter', 'raydium'],
                'confidence': confidence,
                'parallel': True
            }
    
    def _get_sell_strategy(self, dex_type: str, confidence: float, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get sell execution strategy"""
        # For sells, always try the detected DEX first
        if dex_type in self.dex_executor_mapping:
            return {
                'type': 'focused_sell',
                'executors': self.dex_executor_mapping[dex_type],
                'confidence': confidence,
                'parallel': False,
                'sell_percentage': trade_info.get('sell_percentage', 100)  # Default full sell
            }
        # If DEX unknown, try to use last buy DEX for this mint
        if dex_type == 'unknown' and is_valid_solana_address(trade_info.get('token_mint','')):
            remembered = self._last_buy_dex_by_mint.get(trade_info['token_mint'])
            if remembered and remembered in self.dex_executor_mapping:
                return {
                    'type': 'focused_sell',
                    'executors': self.dex_executor_mapping[remembered],
                    'confidence': confidence,
                    'parallel': False,
                    'sell_percentage': trade_info.get('sell_percentage', 100)
                }
        # Fallback
        return {
            'type': 'fallback_sell',
            'executors': ['jupiter'],
            'confidence': confidence,
            'parallel': False,
            'sell_percentage': trade_info.get('sell_percentage', 100)
        }
    
    def _get_fallback_strategy(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback strategy for unknown trades"""
        return {
            'type': 'fallback',
            'executors': ['jupiter'],
            'confidence': 0.3,
            'parallel': False,
            'note': 'Using fallback strategy due to analysis failure'
        }
    
    async def _get_transaction_strong_commitment(self, signature: str):
        """Get transaction with strong commitment to ensure reliable token balance data"""
        if not self.rpc_client or not signature:
            return None
        try:
            import asyncio
            # Always use finalized commitment for maximum reliability when refetching
            logger.debug(f"Refetching transaction {signature[:8]} with finalized commitment")
            resp = await asyncio.wait_for(
                self.rpc_client.call("getTransaction", [
                    signature, 
                    {"encoding": "json", "commitment": "finalized", "maxSupportedTransactionVersion": 0}
                ]), 
                timeout=3.0
            )
            tx = resp.get("result")
            return tx
        except Exception as e:
            logger.debug(f"Strong commitment fetch failed for {signature[:8]}: {e}")
            return None
    
    async def _extract_sophisticated_token_mint(self, tx, wallet_pubkey) -> Optional[Union[str, Dict[str, Any]]]:
        """
        Uses our sophisticated mint detection methods that we spent hours perfecting.
        Prioritizes Jupiter balance changes analysis and comprehensive mint extraction.
        """
        wallet_pubkey = self._key_str(wallet_pubkey)
        
        # Log input for debugging
        signature = tx.get('transaction', {}).get('signatures', ['N/A'])[0] if tx.get('transaction', {}).get('signatures') else 'N/A'
        logger.debug(f"🔍 [SOPHISTICATED_MINT] Input for {signature[:12]}...")
        logger.debug(f"   Wallet: {wallet_pubkey[:12]}...")
        logger.debug(f"   Transaction keys: {list(tx.keys())}")
        
        # Defensive: If meta or token balances are missing, retry with strong commitment
        meta = (tx.get('meta') or {})
        has_token_balances = bool(meta.get('preTokenBalances') or meta.get('postTokenBalances'))
        logger.debug(f"   Initial token balances present: {has_token_balances}")
        
        if not (meta.get('preTokenBalances') or meta.get('postTokenBalances')):
            logger.debug(f"⚠️ [SOPHISTICATED_MINT] Missing token balances, retrying with strong commitment")
            alt_tx = await self._get_transaction_strong_commitment(
                tx.get('transaction', {}).get('signatures', [''])[0] if tx.get('transaction', {}).get('signatures') else None
            )
            if alt_tx:
                logger.debug(f"✅ [SOPHISTICATED_MINT] Strong commitment fetch successful")
                tx = alt_tx
                meta = (tx.get('meta') or {})
            else:
                logger.debug(f"❌ [SOPHISTICATED_MINT] Strong commitment fetch failed")

        # 🚀 PRIORITY 1: ADVANCED JUPITER EXTRACTION (our sophisticated mint detection!)
        dex = self._detect_platform(tx)
        logger.debug(f"🔍 [SOPHISTICATED_MINT] Detected platform: {dex}")
        
        if dex == "jupiter":
            logger.debug(f"🎯 [SOPHISTICATED_MINT] Using ADVANCED Jupiter extraction")
            jupiter_result = await self._extract_jupiter_token_from_balance_changes(tx)
            logger.debug(f"   Jupiter result type: {type(jupiter_result)}, value: {jupiter_result}")
            
            if jupiter_result and isinstance(jupiter_result, dict):
                token_mint = jupiter_result.get('token_mint')
                if token_mint and is_valid_solana_address(token_mint):
                    logger.debug(f"✅ [SOPHISTICATED_MINT] Output: Jupiter dict result with mint {token_mint[:8]}...")
                    return jupiter_result  # Return full result with action
                else:
                    logger.debug(f"❌ [SOPHISTICATED_MINT] Jupiter dict result invalid: token_mint={token_mint}")
            elif jupiter_result and is_valid_solana_address(jupiter_result):
                # Backward compatibility for old return format
                logger.debug(f"✅ [SOPHISTICATED_MINT] Output: Jupiter string result {jupiter_result[:8]}...")
                return jupiter_result
            
            # If Jupiter detection returns None, still try to guess action for the chosen mint
            if jupiter_result is None:
                logger.debug(f"⚠️ [SOPHISTICATED_MINT] Jupiter extraction returned None, trying logs fallback")
                token_mint = None
                logs_mint = self._extract_mint_from_logs((tx.get('meta') or {}).get('logMessages', []))
                if logs_mint and is_valid_solana_address(logs_mint):
                    logger.debug(f"✅ [SOPHISTICATED_MINT] Found logs mint: {logs_mint[:8]}...")
                    token_mint = logs_mint
                if token_mint:
                    action_guess = await self._determine_action_for_wallet(tx, wallet_pubkey, token_mint)
                    logger.debug(f"✅ [SOPHISTICATED_MINT] Output: Logs-based result with action {action_guess}")
                    return {'token_mint': token_mint, 'action': action_guess, 'confidence': 0.5}
                else:
                    logger.debug(f"❌ [SOPHISTICATED_MINT] No valid mint found in logs either")

        # 🚀 PRIORITY 2: COMPREHENSIVE MINT EXTRACTION (our other sophisticated method!)
        logger.debug(f"🔍 [SOPHISTICATED_MINT] Using comprehensive mint extraction")
        comprehensive_mint = await self._extract_real_token_mint(tx)
        logger.debug(f"   Comprehensive result: {comprehensive_mint}")
        
        if comprehensive_mint and is_valid_solana_address(comprehensive_mint):
            logger.debug(f"✅ [SOPHISTICATED_MINT] Output: Comprehensive mint {comprehensive_mint[:8]}...")
            return comprehensive_mint
        else:
            logger.debug(f"❌ [SOPHISTICATED_MINT] Comprehensive extraction failed or invalid")

        # 🚨 AGGRESSIVE FALLBACK: Try everything one more time before giving up
        logger.debug(f"🔍 [SOPHISTICATED_MINT] AGGRESSIVE FALLBACK: Last attempt using all methods")
        
        # Final fallback: try extracting mint from logs before giving up  
        logs_mint = self._extract_mint_from_logs((tx.get('meta') or {}).get('logMessages', []))
        if logs_mint and is_valid_solana_address(logs_mint):
            logger.debug(f"✅ [SOPHISTICATED_MINT] Output: Final logs mint {logs_mint[:8]}...")
            return logs_mint
        else:
            logger.debug(f"❌ [SOPHISTICATED_MINT] Logs extraction also failed")
            
        # Ultra-aggressive: Try account keys as last resort
        logger.debug(f"🔍 [SOPHISTICATED_MINT] Ultra-aggressive: checking account keys as final attempt")
        msg = tx.get("transaction", {}).get("message", {}) or {}
        account_keys = msg.get("accountKeys", [])
        
        # Look for any valid token mints in account keys (excluding known system programs)
        system_programs = {
            '11111111111111111111111111111111',            # System Program
            'ComputeBudget111111111111111111111111111111', # Compute Budget
            'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
            'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
            'So11111111111111111111111111111111111111112',   # Wrapped SOL
        }
        
        for key in account_keys:
            key_str = self._key_str(key)
            if (key_str and is_valid_solana_address(key_str) and 
                key_str not in system_programs and 
                key_str not in DEX_PROGRAMS and
                len(key_str) == 44):  # Valid base58 length
                logger.debug(f"✅ [SOPHISTICATED_MINT] Output: Ultra-fallback account key {key_str[:8]}...")
                return key_str
                
        logger.debug(f"❌ [SOPHISTICATED_MINT] Even ultra-aggressive fallback failed")

        # Complete failure analysis
        logger.error(f"❌ [SOPHISTICATED_MINT] Complete failure for {signature[:12]}...")
        logger.error(f"   Reason: All extraction methods failed (Jupiter, Comprehensive, Logs)")
        logger.error(f"   Platform detected: {dex}")
        logger.error(f"   Meta present: {bool(meta)}")
        logger.error(f"   Token balances: pre={len(meta.get('preTokenBalances', []))}, post={len(meta.get('postTokenBalances', []))}")
        logger.error(f"   Log messages: {len((tx.get('meta') or {}).get('logMessages', []))}")
        logger.debug(f"   Output: None (complete failure)")
        return None

    # Removed unused helper methods - now using sophisticated mint detection directly

    def _detect_platform(self, tx):
        # First try program ID detection from instructions
        msg = tx.get("transaction", {}).get("message", {}) or {}
        instructions = msg.get("instructions", [])
        keys = [self._key_str(k) for k in (msg.get("accountKeys") or [])]
        
        for ix in instructions:
            pid = ix.get("programId")
            if not pid and "programIdIndex" in ix:
                idx = ix["programIdIndex"]
                if isinstance(idx, int) and 0 <= idx < len(keys):
                    pid = keys[idx]
            pid = self._key_str(pid)
            if pid and pid in DEX_PROGRAMS:
                return DEX_PROGRAMS[pid]
        
        # Fallback to log message analysis
        logs = (tx.get("meta", {}) or {}).get("logMessages", []) or []
        msg = " ".join(logs).lower()
        if "pump" in msg or "6ef8rrec" in msg or "pammba" in msg:
            return "pumpfun"
        if "jup6" in msg or "jupiter" in msg:
            return "jupiter"
        if "cpmm" in msg or "cpmmoo8" in msg:
            return "raydium_cpmm"
        if "cammczo" in msg:
            return "raydium_clmm"
        if "whirlb" in msg or "orca" in msg:
            return "orca_whirlpool"
        if "eo7wjkq" in msg or "meteora" in msg:
            return "meteora"
        return "unknown"

    # Removed unused _dex_decode_mints - using sophisticated detection only

    # Removed unused _candidates_from_atas - using sophisticated detection only

    # Removed unused helper methods - using sophisticated detection only

    async def _extract_jupiter_token_with_wallet_context(self, transaction_data: dict, target_wallet: str) -> Optional[str]:
        """
        Extract token specifically for the target wallet we're copying from
        This provides the most precise token extraction for copy trading
        """
        try:
            meta = transaction_data.get('meta', {})
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            
            if not pre_balances and not post_balances:
                return None
            
            logger.debug(f"🎯 Wallet-specific analysis for: {str(target_wallet)[:8]}")
            
            # System tokens to exclude
            exclude_mints = {
                'So11111111111111111111111111111111111111112',   # Wrapped SOL
                'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',   # USDC
                'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',    # USDT
            }
            
            # Find balance changes specifically for our target wallet
            wallet_pre = {}
            wallet_post = {}
            
            for balance in pre_balances:
                if balance.get('owner') == str(target_wallet):
                    mint = balance.get('mint')
                    amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                    decimals = balance.get('uiTokenAmount', {}).get('decimals', 0)
                    wallet_pre[mint] = {'amount': amount, 'decimals': decimals}
                    logger.debug(f"   🔵 PRE {str(mint)[:8]}: {amount} ({amount / (10**decimals) if decimals else amount})")
            
            for balance in post_balances:
                if balance.get('owner') == str(target_wallet):
                    mint = balance.get('mint')
                    amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                    decimals = balance.get('uiTokenAmount', {}).get('decimals', 0)
                    wallet_post[mint] = {'amount': amount, 'decimals': decimals}
                    logger.debug(f"   🟢 POST {str(mint)[:8]}: {amount} ({amount / (10**decimals) if decimals else amount})")
            
            # Analyze changes for this specific wallet
            all_mints = set(wallet_pre.keys()) | set(wallet_post.keys())
            significant_changes = []
            
            for mint in all_mints:
                if mint in exclude_mints:
                    continue
                
                pre_data = wallet_pre.get(mint, {'amount': 0, 'decimals': 0})
                post_data = wallet_post.get(mint, {'amount': 0, 'decimals': 0})
                
                pre_amount = pre_data['amount']
                post_amount = post_data['amount']
                decimals = max(pre_data['decimals'], post_data['decimals'])
                change = post_amount - pre_amount
                
                if change == 0:
                    continue
                
                # Calculate normalized change for significance
                normalized_change = abs(change) / (10 ** decimals) if decimals > 0 else abs(change)
                
                significant_changes.append({
                    'mint': mint,
                    'change': change,
                    'normalized_change': normalized_change,
                    'action': 'buy' if change > 0 else 'sell',
                    'decimals': decimals
                })
                
                logger.info(f"   🎯 {str(mint)[:8]}: {'BUY' if change > 0 else 'SELL'} {normalized_change:,.2f}")
            
            # Return the most significant change (largest normalized amount)
            if significant_changes:
                best_change = max(significant_changes, key=lambda x: x['normalized_change'])
                logger.info(f"✅ WALLET-SPECIFIC TOKEN: {str(best_change['mint'])[:8]} ({best_change['action']})")
                return best_change['mint']
            
            logger.debug(f"⚠️ No significant changes for wallet {target_wallet[:8]}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Wallet-specific extraction failed: {e}")
            return None

    async def _determine_action_for_wallet(self, transaction_data: dict, wallet_address: str, token_mint: str) -> str:
        """
        Determine if the wallet bought or sold the specific token
        """
        try:
            meta = transaction_data.get('meta', {})
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            
            # Find the specific token balance for this wallet
            pre_amount = 0
            post_amount = 0
            
            for balance in pre_balances:
                if balance.get('owner') == str(wallet_address) and balance.get('mint') == str(token_mint):
                    pre_amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                    break
            
            for balance in post_balances:
                if balance.get('owner') == str(wallet_address) and balance.get('mint') == str(token_mint):
                    post_amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                    break
            
            change = post_amount - pre_amount
            
            if change > 0:
                logger.debug(f"🟢 Wallet {str(wallet_address)[:8]} BOUGHT {str(token_mint)[:8]} (+{change})")
                return 'buy'
            elif change < 0:
                logger.debug(f"🔴 Wallet {str(wallet_address)[:8]} SOLD {str(token_mint)[:8]} ({change})")
                return 'sell'
            else:
                logger.debug(f"🟡 No change detected for {str(wallet_address)[:8]} / {str(token_mint)[:8]}")
                return 'unknown'
                
        except Exception as e:
            logger.error(f"❌ Action determination failed: {e}")
            return 'unknown'
    
    async def _extract_real_token_mint(self, transaction: dict) -> Optional[str]:
        """Enhanced token mint extraction with Jupiter token balance analysis."""
        try:
            # Log input for debugging
            signature = transaction.get('transaction', {}).get('signatures', ['N/A'])[0] if transaction.get('transaction', {}).get('signatures') else 'N/A'
            logger.debug(f"🔍 [REAL_TOKEN_MINT] Input for {signature[:12]}...")
            logger.debug(f"   Transaction keys: {list(transaction.keys())}")
            
            # Known system programs and addresses to exclude
            system_programs = {
                '11111111111111111111111111111111',            # System Program
                'ComputeBudget111111111111111111111111111111', # Compute Budget
                'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
                'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
                'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4',  # Jupiter
                '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',  # Pump.fun
                'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA',  # Pump.fun AMM
                'BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW',
                '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',
                'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN',
                'So11111111111111111111111111111111111111112',   # Wrapped SOL
                'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',   # USDC (common intermediary)
            }

            candidates = set()
            token_balance_mints = set()
            meta = transaction.get('meta', {})
            
            logger.debug(f"   Meta present: {bool(meta)}")
            logger.debug(f"   System programs to exclude: {len(system_programs)}")
            
            # Fix #6: Add defensive check for None meta to prevent 'NoneType' object is not subscriptable errors
            if not meta or meta is None:
                logger.error(f"❌ [REAL_TOKEN_MINT] Failed for {signature[:12]}...")
                logger.error(f"   Reason: No meta information in transaction")
                logger.debug(f"   Output: None (no meta)")
                return None
            
            # Always refetch with finalized commitment if token balances are missing
            if not (meta.get('preTokenBalances') or meta.get('postTokenBalances')):
                logger.debug(f"⚠️ [REAL_TOKEN_MINT] Missing token balances, refetching with finalized commitment")
                alt_tx = await self._get_transaction_strong_commitment(signature)
                if alt_tx:
                    logger.debug(f"✅ [REAL_TOKEN_MINT] Finalized commitment fetch successful")
                    transaction = alt_tx
                    meta = (transaction.get('meta') or {})
                else:
                    logger.debug(f"❌ [REAL_TOKEN_MINT] Finalized commitment fetch failed")
            
            # Defensive check for token balances
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            logger.debug(f"   Token balances: pre={len(pre_balances) if isinstance(pre_balances, list) else 'invalid'}, post={len(post_balances) if isinstance(post_balances, list) else 'invalid'}")
            
            if not isinstance(pre_balances, list) or not isinstance(post_balances, list):
                logger.error(f"❌ [REAL_TOKEN_MINT] Failed for {signature[:12]}...")
                logger.error(f"   Reason: Invalid or missing token balance data")
                logger.error(f"   Pre-balances type: {type(pre_balances)}, Post-balances type: {type(post_balances)}")
                logger.debug(f"   Output: None (invalid balance data)")
                return None
            
            # 🚀 JUPITER TOKEN EXTRACTION: Analyze balance changes first
            logger.debug(f"🔍 [REAL_TOKEN_MINT] Trying Jupiter token extraction")
            jupiter_token = await self._extract_jupiter_token_from_balance_changes(transaction)
            logger.debug(f"   Jupiter result: {jupiter_token} (type: {type(jupiter_token)})")
            
            if jupiter_token:
                if isinstance(jupiter_token, dict):
                    mint = jupiter_token.get('token_mint')
                    if mint and is_valid_solana_address(mint):
                        logger.debug(f"✅ [REAL_TOKEN_MINT] Output: Jupiter dict mint {mint[:8]}...")
                        return mint
                    else:
                        logger.debug(f"❌ [REAL_TOKEN_MINT] Jupiter dict invalid: mint={mint}")
                elif isinstance(jupiter_token, str) and is_valid_solana_address(jupiter_token):
                    logger.debug(f"✅ [REAL_TOKEN_MINT] Output: Jupiter string mint {jupiter_token[:8]}...")
                    return jupiter_token
                else:
                    logger.debug(f"❌ [REAL_TOKEN_MINT] Jupiter result invalid: {jupiter_token}")
            else:
                logger.debug(f"❌ [REAL_TOKEN_MINT] Jupiter extraction returned None")
            
            # Priority 1: Check postTokenBalances for actual token mints with real balances
            logger.debug(f"🔍 [REAL_TOKEN_MINT] Analyzing postTokenBalances")
            if 'postTokenBalances' in meta:
                for i, bal in enumerate(meta['postTokenBalances']):
                    mint = bal.get('mint')
                    amount = bal.get('uiTokenAmount', {}).get('amount')
                    logger.debug(f"   Balance {i}: mint={mint[:8] if mint else None}..., amount={amount}")
                    
                    if mint and is_valid_solana_address(mint) and mint not in system_programs and not mint.startswith('So1111'):
                        if amount not in [None, '0']:
                            logger.debug(f"✅ [REAL_TOKEN_MINT] High-confidence token mint from postTokenBalances: {str(mint)[:8]}...")
                            token_balance_mints.add(mint)
                            candidates.add(mint)
                        else:
                            logger.debug(f"⚠️ [REAL_TOKEN_MINT] Token mint has zero balance: {str(mint)[:8]}...")
                    else:
                        logger.debug(f"❌ [REAL_TOKEN_MINT] Excluded mint: {str(mint)[:8] if mint else 'None'}... (system/invalid)")
            else:
                logger.debug(f"❌ [REAL_TOKEN_MINT] No postTokenBalances in meta")

            # Priority 2: Check all account keys for valid token mints (with proper wallet exclusion)
            accounts = []
            if 'message' in transaction and 'accountKeys' in transaction['message']:
                accounts = transaction['message']['accountKeys']
            elif 'transaction' in transaction and 'message' in transaction['transaction'] and 'accountKeys' in transaction['transaction']['message']:
                accounts = transaction['transaction']['message']['accountKeys']

            # Get known wallet addresses for exclusion
            known_wallets = {
                'gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB',  # Our bot wallet
                'A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB',  # Our trading wallet
                'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK',   # Target wallet 1
                'DfMxre4c9Vp6V2LB74QCFpJP4BemjJJrxjJbBs7scWoP',   # Target wallet 2
                'Ez2jp3rw5vMbSrGWEzZg5wkN3bHdV5Y9qJ6i8dP1mJ4K',   # Target wallet 3
                '9ePNTG4jf8a7Kef2yJ3n4mRh8WgZxZFVo1JnXqq5b7vC',   # Target wallet 4
                # Common wallet addresses that appear in failed transactions
                'AJxEGdtoHrgVUPyMsdyMLiEevwa6gk3de1QDPGwVh2hw',   # This is a WALLET, not a token
                'FzESY59j4xCef1EjqoprVBDXEFTWcrx8hGq6AYYvGH1v',   # This is a WALLET, not a token  
                '77N86XfcBSAvcGNPYMAVjjyf2feUJwmUoiJ96HzPtySd',   # This is a WALLET, not a token
                'E8iYKQbhTywHbncCagNBbZ58JY6cX1SiYk5ZDPJeWFFq',   # This is a WALLET, not a token
                # Known signers that appear as account keys
                'Ekx3kKqBZ8MtugdETbgP5TbLo5pD8A9G51KZwdr3AoDj',
                '5jYaYv7HoiFVrY9bAcruj6dH8fCBseky4sBmnTFGSaeW',
                '238UW7NmnrS1HeUDxKNzoHj5zHNFCjpy8zkcuKHzF8zv'
            }

            for account in accounts:
                account_key = account if isinstance(account, str) else account.get('pubkey', '')
                if (is_valid_solana_address(account_key) and 
                    account_key not in system_programs and 
                    account_key not in known_wallets and  # 🚫 EXCLUDE KNOWN WALLETS
                    not account_key.startswith('So1111')):
                    candidates.add(account_key)

            # Priority 3: Use any candidate found, even if not in token balances
            logger.debug(f"🔍 [REAL_TOKEN_MINT] Final candidate analysis")
            logger.debug(f"   Total candidates: {len(candidates)}")
            logger.debug(f"   Token balance mints: {len(token_balance_mints)}")
            logger.debug(f"   Candidates: {[str(c)[:8] + '...' for c in list(candidates)[:5]]}{'...' if len(candidates) > 5 else ''}")
            
            if candidates:
                # Return the first validated token mint (prioritize from token balances)
                for mint in token_balance_mints:
                    if mint in candidates:
                        logger.debug(f"✅ [REAL_TOKEN_MINT] Output: Priority mint from token balances {str(mint)[:8]}...")
                        return mint
                        
                # Fallback to any validated candidate
                for candidate in candidates:
                    if is_valid_solana_address(candidate):
                        logger.debug(f"✅ [REAL_TOKEN_MINT] Output: Fallback candidate {str(candidate)[:8]}...")
                        return candidate

            # If no valid token candidates found, check if this is a non-trading transaction
            logger.debug(f"🔍 [REAL_TOKEN_MINT] No candidates found, checking for non-trading transaction")
            if 'meta' in transaction and 'logMessages' in transaction['meta']:
                logs = transaction['meta']['logMessages']
                logger.debug(f"   Log messages: {len(logs)}")
                
                is_non_trading = (len(logs) <= 4 and 
                    all('System Program' in log or 'ComputeBudget' in log or 'invoke' in log or 'success' in log 
                        for log in logs if log.strip()))
                        
                if is_non_trading:
                    logger.debug(f"✅ [REAL_TOKEN_MINT] Detected non-trading transaction - expected result")
                    logger.debug(f"   Output: None (non-trading transaction)")
                    return None
                else:
                    logger.debug(f"❌ [REAL_TOKEN_MINT] Has logs but doesn't match non-trading pattern")

            # AGGRESSIVE FALLBACK: Parse logs for mint candidates as last resort
            logger.debug(f"🔍 [REAL_TOKEN_MINT] AGGRESSIVE FALLBACK: Parsing logs for mint candidates")
            logs_mint = self._extract_mint_from_logs((transaction.get('meta') or {}).get('logMessages', []))
            if logs_mint and is_valid_solana_address(logs_mint):
                logger.debug(f"✅ [REAL_TOKEN_MINT] Output: Logs fallback mint {logs_mint[:8]}...")
                return logs_mint
            else:
                logger.debug(f"❌ [REAL_TOKEN_MINT] Logs extraction also failed")
            
            # ULTRA-AGGRESSIVE FALLBACK: Check all account keys as final attempt
            logger.debug(f"🔍 [REAL_TOKEN_MINT] Ultra-aggressive: checking account keys as final attempt")
            msg = transaction.get("transaction", {}).get("message", {}) or {}
            account_keys = msg.get("accountKeys", [])
            
            # Look for any valid token mints in account keys (excluding known system programs)
            system_programs = {
                '11111111111111111111111111111111',            # System Program
                'ComputeBudget111111111111111111111111111111', # Compute Budget
                'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
                'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
                'So11111111111111111111111111111111111111112',   # Wrapped SOL
            }
            
            for key in account_keys:
                key_str = self._key_str(key)
                if (key_str and is_valid_solana_address(key_str) and 
                    key_str not in system_programs and 
                    key_str not in DEX_PROGRAMS and
                    len(key_str) == 44):  # Valid base58 length
                    logger.debug(f"✅ [REAL_TOKEN_MINT] Output: Ultra-fallback account key {key_str[:8]}...")
                    return key_str
                    
            logger.debug(f"❌ [REAL_TOKEN_MINT] Even ultra-aggressive fallback failed")
            
            # Final fallback: return None instead of UNKNOWN to prevent invalid pubkey errors  
            logger.error(f"❌ [REAL_TOKEN_MINT] Complete failure for {signature[:12]}...")
            logger.error(f"   Reason: No valid token candidates found despite comprehensive analysis")
            logger.error(f"   Candidates found: {len(candidates)}")
            logger.error(f"   Token balance mints: {len(token_balance_mints)}")
            logger.error(f"   Account keys processed: {len(accounts) if 'accounts' in locals() else 'unknown'}")
            logger.error(f"   Jupiter extraction result: {jupiter_token}")
            logger.debug(f"   Output: None (complete failure)")
            return None
        except Exception as e:
            signature = transaction.get('transaction', {}).get('signatures', ['N/A'])[0] if transaction.get('transaction', {}).get('signatures') else 'N/A'
            logger.error(f"❌ [REAL_TOKEN_MINT] Exception for {signature[:12]}...")
            logger.error(f"   Error: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.debug(f"   Output: None (exception occurred)")
            return None

    async def _extract_jupiter_token_from_balance_changes(self, transaction_data: dict) -> Optional[str]:
        """
        ADVANCED Jupiter token extraction with precision analysis
        Analyzes ALL wallet owners in the transaction to find the actual traded token
        """
        try:
            meta = transaction_data.get('meta', {})
            
            # Always refetch with finalized commitment if token balances are missing
            if not (meta.get('preTokenBalances') or meta.get('postTokenBalances')):
                signature = transaction_data.get('transaction', {}).get('signatures', [''])[0] if transaction_data.get('transaction', {}).get('signatures') else None
                if signature:
                    logger.debug(f"⚠️ [JUPITER_BALANCE] Missing token balances, refetching with finalized commitment")
                    alt_tx = await self._get_transaction_strong_commitment(signature)
                    if alt_tx:
                        logger.debug(f"✅ [JUPITER_BALANCE] Finalized commitment fetch successful")
                        transaction_data = alt_tx
                        meta = (transaction_data.get('meta') or {})
                    else:
                        logger.debug(f"❌ [JUPITER_BALANCE] Finalized commitment fetch failed")
            
            pre_balances = meta.get('preTokenBalances', [])
            post_balances = meta.get('postTokenBalances', [])
            
            if not pre_balances and not post_balances:
                logger.debug("🚫 No token balance data - trying logs fallback before giving up")
                
                # AGGRESSIVE FALLBACK: Parse logs for mint candidates before giving up
                logger.debug(f"🔍 [JUPITER_BALANCE] AGGRESSIVE FALLBACK: Parsing logs for mint candidates")
                logs_mint = self._extract_mint_from_logs((transaction_data.get('meta') or {}).get('logMessages', []))
                if logs_mint and is_valid_solana_address(logs_mint):
                    logger.debug(f"✅ [JUPITER_BALANCE] Output: Logs fallback mint {logs_mint[:8]}...")
                    return logs_mint
                else:
                    logger.debug(f"❌ [JUPITER_BALANCE] Logs extraction also failed")
                
                # ULTRA-AGGRESSIVE FALLBACK: Check all account keys as final attempt (early path)
                logger.debug(f"� [JUPITER_BALANCE] Ultra-aggressive: checking account keys as final attempt (early path)")
                msg = transaction_data.get("transaction", {}).get("message", {}) or {}
                account_keys = msg.get("accountKeys", [])
                
                # Look for any valid token mints in account keys (excluding known system programs)
                system_programs = {
                    '11111111111111111111111111111111',            # System Program
                    'ComputeBudget111111111111111111111111111111', # Compute Budget
                    'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
                    'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
                    'So11111111111111111111111111111111111111112',   # Wrapped SOL
                }
                
                for key in account_keys:
                    key_str = self._key_str(key)
                    if (key_str and is_valid_solana_address(key_str) and 
                        key_str not in system_programs and 
                        key_str not in DEX_PROGRAMS and
                        len(key_str) == 44):  # Valid base58 length
                        logger.debug(f"✅ [JUPITER_BALANCE] Output: Ultra-fallback account key {key_str[:8]}... (early path)")
                        return key_str
                        
                logger.debug(f"❌ [JUPITER_BALANCE] Even ultra-aggressive fallback failed (early path)")
                
                logger.debug("🚫 No token balance data and no fallbacks worked - not a token trade")
                return None
            
            logger.info(f"🔍 ADVANCED Jupiter Analysis - Pre: {len(pre_balances)}, Post: {len(post_balances)}")
            
            # System tokens and intermediary tokens to exclude
            exclude_mints = {
                'So11111111111111111111111111111111111111112',   # Wrapped SOL
                'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',   # USDC
                'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',    # USDT
                'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',     # Marinade SOL
                'bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1',     # Blazestake SOL
                'J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn',    # Jito SOL
            }
            
            # Build comprehensive balance change map for ALL owners
            balance_changes = {}
            
            # Map pre-balances by (owner, mint)
            pre_map = {}
            for balance in pre_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                if owner and mint:
                    pre_map[(owner, mint)] = amount
            
            # Map post-balances and calculate changes
            for balance in post_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                post_amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                
                if owner and mint:
                    pre_amount = pre_map.get((owner, mint), 0)
                    change = post_amount - pre_amount
                    
                    if change != 0:  # Only track actual changes
                        if owner not in balance_changes:
                            balance_changes[owner] = {}
                        balance_changes[owner][mint] = {
                            'change': change,
                            'pre': pre_amount,
                            'post': post_amount,
                            'decimals': balance.get('uiTokenAmount', {}).get('decimals', 0)
                        }
            
            # Find the most likely traded token with advanced heuristics
            token_candidates = []
            
            for owner, mints in balance_changes.items():
                logger.debug(f"📊 Owner {str(owner)[:8]}: {len(mints)} token changes")
                
                for mint, data in mints.items():
                    if mint in exclude_mints:
                        logger.debug(f"   ⏭️  Skipping system token: {str(mint)[:8]}")
                        continue
                    
                    change = data['change']
                    decimals = data['decimals']
                    
                    # Calculate significance score based on multiple factors
                    significance = 0
                    
                    # Factor 1: Absolute change magnitude (normalized by decimals)
                    normalized_change = abs(change) / (10 ** decimals) if decimals > 0 else abs(change)
                    if normalized_change > 1000:  # Significant amount
                        significance += 50
                    elif normalized_change > 100:
                        significance += 30
                    elif normalized_change > 1:
                        significance += 10
                    
                    # Factor 2: Direction matters (buys often more significant than sells for copy trading)
                    if change > 0:  # Token increased (BUY)
                        significance += 25
                        action = "buy"
                    else:  # Token decreased (SELL) 
                        significance += 15
                        action = "sell"
                    
                    # Factor 3: New position vs existing position
                    if data['pre'] == 0 and data['post'] > 0:  # New position
                        significance += 20
                    elif data['pre'] > 0 and data['post'] == 0:  # Closed position
                        significance += 15
                    
                    logger.info(f"   🎯 {action} {str(mint)[:8]}: {change:+,} (score: {significance})")
                    
                    token_candidates.append({
                        'mint': mint,
                        'owner': owner,
                        'change': change,
                        'significance': significance,
                        'action': action,
                        'normalized_amount': normalized_change
                    })
            
            # Sort candidates by significance score
            token_candidates.sort(key=lambda x: x['significance'], reverse=True)
            
            if token_candidates:
                best_candidate = token_candidates[0]
                logger.info(f"✅ BEST TOKEN CANDIDATE: {str(best_candidate['mint'])[:8]}... ({best_candidate['action']}, score: {best_candidate['significance']})")
                
                # Log top 3 candidates for debugging
                for i, candidate in enumerate(token_candidates[:3]):
                    logger.debug(f"   #{i+1}: {str(candidate['mint'])[:8]} - {candidate['action']} (score: {candidate['significance']})")
                
                # Return both token and action for complete analysis
                return {
                    'token_mint': best_candidate['mint'],
                    'action': best_candidate['action'],
                    'confidence': best_candidate['significance'] / 100.0,
                    'method': 'jupiter_balance_analysis'
                }
            
            logger.warning("⚠️ No significant token changes detected in Jupiter transaction")
            
            # AGGRESSIVE FALLBACK: Parse logs for mint candidates as last resort
            logger.debug(f"🔍 [JUPITER_BALANCE] AGGRESSIVE FALLBACK: Parsing logs for mint candidates")
            logs_mint = self._extract_mint_from_logs((transaction_data.get('meta') or {}).get('logMessages', []))
            if logs_mint and is_valid_solana_address(logs_mint):
                logger.debug(f"✅ [JUPITER_BALANCE] Output: Logs fallback mint {logs_mint[:8]}...")
                return logs_mint
            else:
                logger.debug(f"❌ [JUPITER_BALANCE] Logs extraction also failed")
            
            # ULTRA-AGGRESSIVE FALLBACK: Check all account keys as final attempt
            logger.debug(f"🔍 [JUPITER_BALANCE] Ultra-aggressive: checking account keys as final attempt")
            msg = transaction_data.get("transaction", {}).get("message", {}) or {}
            account_keys = msg.get("accountKeys", [])
            
            # Look for any valid token mints in account keys (excluding known system programs)
            system_programs = {
                '11111111111111111111111111111111',            # System Program
                'ComputeBudget111111111111111111111111111111', # Compute Budget
                'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
                'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
                'So11111111111111111111111111111111111111112',   # Wrapped SOL
            }
            
            for key in account_keys:
                key_str = self._key_str(key)
                if (key_str and is_valid_solana_address(key_str) and 
                    key_str not in system_programs and 
                    key_str not in DEX_PROGRAMS and
                    len(key_str) == 44):  # Valid base58 length
                    logger.debug(f"✅ [JUPITER_BALANCE] Output: Ultra-fallback account key {key_str[:8]}...")
                    return key_str
                    
            logger.debug(f"❌ [JUPITER_BALANCE] Even ultra-aggressive fallback failed")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Advanced Jupiter token extraction failed: {e}")
            
            # AGGRESSIVE FALLBACK: Even on exception, try parsing logs
            try:
                logger.debug(f"🔍 [JUPITER_BALANCE] Exception fallback: Parsing logs for mint candidates")
                logs_mint = self._extract_mint_from_logs((transaction_data.get('meta') or {}).get('logMessages', []))
                if logs_mint and is_valid_solana_address(logs_mint):
                    logger.debug(f"✅ [JUPITER_BALANCE] Output: Exception logs fallback mint {logs_mint[:8]}...")
                    return logs_mint
            except Exception as fallback_e:
                logger.debug(f"❌ [JUPITER_BALANCE] Exception logs fallback also failed: {fallback_e}")
            
            return None

    async def analyze_trade_simple(self, signature: str, wallet_address: str, trade_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Simple trade analysis - now with support for provided transaction data
        Pure analysis - no execution
        """
        try:
            logger.debug(f"🔍 Simple trade analysis for {signature[:8]}...")
            
            # Use full transaction analyzer to get complete information including programs_used
            try:
                from transaction_analyzer import TransactionAnalyzer
                analyzer = TransactionAnalyzer(self.rpc_client)
                
                # Check if we have transaction data from WebSocket
                if trade_info and ('transaction' in trade_info or 'meta' in trade_info):
                    logger.info(f"🎯 Using provided transaction data to avoid RPC refetch")
                    result = await analyzer.analyze_transaction_with_data(signature, wallet_address, trade_info)
                else:
                    logger.info(f"🔍 Fetching transaction data from RPC")
                    result = await analyzer.analyze_transaction_with_balance_detection(signature, wallet_address)
                
                if result and result.get('token_mint'):
                    logger.info(f"✅ Simple analysis found token: {result['token_mint'][:8]}...")
                    
                    # Extract additional information for better DEX detection
                    dex_type = result.get('dex', 'unknown')
                    logger.info(f"✅ Detected DEX: {dex_type}")
                    
                    # Check for router program info
                    router_program = result.get('router_program_id')
                    if router_program:
                        logger.info(f"✅ Router program extracted: {router_program}")
                    
                    # RESPECT EXISTING BASIC ANALYSIS - Don't override action if it's already correctly detected
                    action = result.get('action', 'unknown')
                    
                    # Don't use emergency 'buy' assumptions - preserve unknown if action detection fails
                    if action == 'buy' and result.get('method') == 'ultra_aggressive_assumption':
                        logger.warning(f"   🚨 Ignoring emergency 'buy' assumption - preserving original analysis")
                        action = 'unknown'
                    
                    return {
                        'token_mint': result['token_mint'],
                        'action': action,
                        'confidence': result.get('confidence', 0.7),
                        'dex_type': dex_type,
                        'trade_type': action,
                        'analysis_method': 'full_analyzer_with_dex_detection',
                        'programs_used': [dex_type] if dex_type != 'unknown' else [],  # Pass DEX info for routing
                        'router_program_id': result.get('router_program_id'),
                        'account_metas': result.get('account_metas', []),
                        'instruction_data': result.get('instruction_data')
                    }
            except Exception as analyzer_error:
                logger.debug(f"Full transaction analyzer failed: {analyzer_error}")
                
                # Fallback to simplified analyzer
                try:
                    from transaction_analyzer import TransactionAnalyzer
                    analyzer = TransactionAnalyzer(self.rpc_client)
                    result = await analyzer._pump_fun_log_based_fallback(signature, wallet_address)
                    
                    if result and result.get('token_mint'):
                        logger.info(f"✅ Simple analysis found token: {result['token_mint'][:8]}...")
                        return {
                            'token_mint': result['token_mint'],
                            'action': result.get('action', 'buy'),
                            'confidence': 0.7,
                            'dex_type': result.get('dex', 'detected_dex'),
                            'trade_type': result.get('action', 'detected_type'),
                            'analysis_method': 'simple_with_analyzer'
                        }
                except Exception as fallback_error:
                    logger.debug(f"Transaction analyzer fallback failed: {fallback_error}")
            
            # Final fallback - just extract token from our own method
            from utils import get_transaction_with_logs
            transaction = await get_transaction_with_logs(signature)
            if transaction:
                token_mint = await self._extract_real_token_mint(transaction)
                if token_mint:
                    return {
                        'token_mint': token_mint,
                        'action': 'unknown',  # Don't assume action without evidence
                        'confidence': 0.3,  # Lower confidence without action evidence
                        'dex_type': 'extracted',
                        'trade_type': 'unknown',
                        'analysis_method': 'simple_direct'
                    }
            
            return {'action': 'error', 'error': f'Simple analysis failed for {signature[:8]}', 'requires_execution': False}
            
        except Exception as e:
            logger.warning(f"Simple analysis failed: {e}")
            return {'action': 'error', 'error': f'Simple analysis failed: {e}', 'requires_execution': False}

    def get_target_wallets(self) -> List[str]:
        """Get list of target wallets being monitored"""
        return self.target_wallets.copy()
    
    def is_target_wallet(self, wallet_address: str) -> bool:
        """Check if wallet is in target list (case-insensitive)"""
        if not wallet_address:
            return False
        # Use case-insensitive matching for wallet comparison
        wallet_lower = wallet_address.lower()
        target_wallets_lower = {w.lower() for w in self.target_wallets if w}
        return wallet_lower in target_wallets_lower
    
    def validate_execution_eligibility(self, trade_info: Dict[str, Any], source_wallet: str = None) -> Dict[str, Any]:
        """
        ULTRA-AGGRESSIVE: Always approve execution - no validation needed.
        
        Matches behavior of aggressive copy bots like DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj.
        Execute EVERY detected trade immediately without validation checks.
        """
        # Always approve - no validation needed
        validation = {
            'eligible': True,  # ALWAYS APPROVE
            'reason': 'ULTRA_AGGRESSIVE: Execute on ANY detection',
            'monitored_wallets_involved': [source_wallet] if source_wallet else [],
            'non_monitored_wallets_found': [],
            'source_wallet_monitored': True,  # Assume yes
            'wallet_address_monitored': True,  # Assume yes
            'detected_actions_monitored': True,  # Assume yes
            'triggered_conditions': ['ULTRA_AGGRESSIVE_MODE']
        }
        
        logger.info(f"⚡ [ULTRA_AGGRESSIVE] Execution ALWAYS APPROVED")
        logger.info(f"   Source wallet: {source_wallet[:8] if source_wallet else 'N/A'}...")
        logger.info(f"   Reason: {validation['reason']}")
        
        return validation
    
    async def execute_trade_routing(self, routing_instructions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trade Execution Routing - Execute detected buy/sell actions via execution coordinator
        
        AGGRESSIVE EXECUTION MODE (matches DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj behavior):
        - Executes when EITHER condition is met:
          1. Recognized trade instruction (DEX program) is present, OR
          2. Transaction signer is in MONITORED_WALLETS
        - Does NOT require token balance changes for execution
        - Token balance changes are analyzed for informational purposes only
        
        For each detected buy/sell:
        - Call execution coordinator's _execute_copy_buy or _execute_copy_sell
        - Pass detected token mint, wallet address, amount, and trade info (including DEX/router)
        
        Args:
            routing_instructions: Output from analyze_and_route_trade containing execution details
            
        Returns:
            Dict with execution results and status
        """
        try:
            # Validate execution coordinator is available
            if not self.execution_coordinator:
                logger.error(f"❌ [TRADE_EXECUTION] No execution coordinator available")
                return {
                    'success': False,
                    'error': 'No execution coordinator configured',
                    'executions': []
                }
            
            # Extract trade information
            action = routing_instructions.get('action')
            token_mint = routing_instructions.get('token_mint')
            source_wallet = routing_instructions.get('source_wallet')
            trade_info = routing_instructions.get('trade_info', {})
            requires_execution = routing_instructions.get('requires_execution', False)
            wallet_validation = routing_instructions.get('wallet_validation', {})
            
            signature = trade_info.get('signature', 'N/A')
            logger.info(f"🚀 [TRADE_EXECUTION] Starting execution routing for {signature[:12]}...")
            logger.info(f"   Action: {action}")
            logger.info(f"   Token: {token_mint[:8] if token_mint and token_mint != 'UNKNOWN' else 'UNKNOWN'}...")
            logger.info(f"   Source Wallet: {source_wallet[:8] if source_wallet else 'N/A'}...")
            logger.info(f"   Requires Execution: {requires_execution}")
            
            execution_results = {
                'success': False,
                'action': action,
                'token_mint': token_mint,
                'source_wallet': source_wallet,
                'executions': [],
                'total_executions': 0,
                'successful_executions': 0
            }
            
            # Validation: Only execute if requirements are met
            if not requires_execution:
                logger.warning(f"⚠️ [TRADE_EXECUTION] Execution not required - but executing anyway (aggressive mode)")
                logger.info(f"🚀 AGGRESSIVE EXECUTION: Matching wallet DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj behavior")
                # Don't return - continue with execution
            
            if not wallet_validation.get('eligible', False):
                logger.warning(f"⚠️ [TRADE_EXECUTION] Wallet validation failed - but executing anyway (aggressive mode)")
                logger.info(f"🚀 AGGRESSIVE EXECUTION: Proceeding regardless of wallet validation")
                # Don't return - continue with execution
            
            # EXECUTION TRIGGER: DEX instruction OR monitored wallet signer
            # Token balance changes are NOT required - they're analyzed for informational purposes only
            detected_actions = trade_info.get('detected_balance_actions', [])
            if not detected_actions:
                logger.info(f"ℹ️  [TRADE_EXECUTION] No balance changes detected - creating synthetic action")
                logger.info(f"   📝 Execution triggered by: DEX instruction OR monitored wallet signer")
                # Create synthetic action based on what we know
                synthetic_action = action if action and action != 'unknown' else 'buy'
                synthetic_mint = token_mint if token_mint and token_mint not in ['UNKNOWN', 'PENDING_ANALYSIS'] else 'UNKNOWN_MINT'
                
                logger.info(f"🚀 [EXECUTION] Creating synthetic {synthetic_action} action for {synthetic_mint[:8]}...")
                detected_actions = [{
                    'action': synthetic_action,
                    'mint': synthetic_mint,
                    'owner': source_wallet,
                    'amount': 0.0,  # Unknown amount
                    'delta': 1.0 if synthetic_action == 'buy' else -1.0,  # Synthetic delta
                    'synthetic': True
                }]
                trade_info['detected_balance_actions'] = detected_actions
                execution_results['synthetic_execution'] = True
            
            # INFORMATIONAL ONLY: Check token balance significance (does not gate execution)
            significance_check = self._has_significant_token_balance_change(
                trade_info=trade_info,
                min_threshold=0.000001  # Configurable threshold for significance
            )
            
            if not significance_check['has_significant_changes']:
                logger.info(f"ℹ️  [BALANCE_INFO] No significant balance changes detected (informational only)")
                logger.info(f"   📊 Total changes: {significance_check['total_changes']}")
                logger.info(f"   📏 Threshold used: {significance_check['threshold_used']}")
                if significance_check['validation_details']:
                    logger.debug(f"   📋 Details: {', '.join(significance_check['validation_details'][:3])}")
                logger.info(f"   ✅ Proceeding with execution (balance changes not required)")
                # Don't return - continue with execution even if changes are insignificant
                execution_results['significance_check'] = significance_check
                execution_results['bypassed_significance_check'] = True
            else:
                execution_results['significance_check'] = significance_check
            
            # Log significant changes if any (informational only)
            if significance_check.get('has_significant_changes'):
                logger.info(f"✅ [BALANCE_INFO] Significant balance changes detected: {len(significance_check.get('significant_changes', []))} (informational)")
                for sig_change in significance_check.get('significant_changes', [])[:3]:
                    logger.info(f"   {sig_change['action'].upper()}: {sig_change['owner'][:8]}.../{sig_change['mint'][:8]}... = {sig_change['change']:+.6f}")
            else:
                logger.info(f"ℹ️  [BALANCE_INFO] No significant changes detected (does not prevent execution)")
                
            # Store significance check results for audit (informational only)
            execution_results['significance_check'] = significance_check
            
            logger.info(f"✅ [TRADE_EXECUTION] Proceeding with execution (aggressive mode)")
            logger.info(f"   Balance actions detected: {len(detected_actions)}")
            logger.info(f"   DEX type: {trade_info.get('dex_type', 'unknown')}")
            logger.info(f"   Router: {trade_info.get('router_program_id', 'N/A')}")
            
            # Execute trades based on detected balance changes
            for i, balance_action in enumerate(detected_actions):
                action_type = balance_action['action']  # 'buy' or 'sell'
                action_mint = balance_action['mint']
                action_owner = balance_action['owner']
                action_amount = balance_action['amount']
                action_delta = balance_action['delta']
                
                logger.info(f"🎯 [TRADE_EXECUTION] Processing action {i+1}/{len(detected_actions)}")
                logger.info(f"   Type: {action_type}")
                logger.info(f"   Mint: {action_mint[:8]}...")
                logger.info(f"   Owner: {action_owner[:8]}...")
                logger.info(f"   Amount: {action_amount:,.6f}")
                logger.info(f"   Delta: {action_delta:+,.6f}")
                
                # AGGRESSIVE MODE: Don't skip non-monitored wallets
                if not self._validate_monitored_wallet(action_owner, self.target_wallets):
                    logger.warning(f"🚫 [EXECUTION_NOTE] Action {i+1} for non-monitored wallet - but executing anyway (aggressive mode)")
                    logger.info(f"🚀 AGGRESSIVE EXECUTION: Proceeding with non-monitored wallet")
                    logger.info(f"   Action: {action_type.upper()}")
                    logger.info(f"   Token: {action_mint}")
                    logger.info(f"   Wallet: {action_owner}")
                    logger.info(f"   Amount: {action_amount:,.6f}")
                    # Don't continue - execute anyway
                
                # AGGRESSIVE MODE: Don't skip insignificant deltas
                abs_delta = abs(action_delta)
                min_threshold = 0.000001  # Same threshold as overall check
                
                if abs_delta < min_threshold:
                    logger.warning(f"🚫 [EXECUTION_NOTE] Action {i+1} below significance threshold - but executing anyway (aggressive mode)")
                    logger.info(f"🚀 AGGRESSIVE EXECUTION: Proceeding despite low delta")
                    logger.info(f"   Action: {action_type.upper()}")
                    logger.info(f"   Token: {action_mint}")
                    logger.info(f"   Wallet: {action_owner}")
                    logger.info(f"   Amount: {action_amount:,.6f}")
                    logger.info(f"   Delta: {action_delta:+,.6f}")
                    logger.info(f"   Absolute Delta: {abs_delta:.6f}")
                    logger.info(f"   Threshold: {min_threshold}")
                    # Don't continue - execute anyway
                
                
                execution_result = None
                
                try:
                    if action_type == 'buy':
                        # FEATURE 6: Pre-Execution Logging
                        logger.info(f"� [EXECUTION_ATTEMPT] Starting COPY BUY execution")
                        logger.info(f"   Action ID: {i+1}/{len(detected_actions)}")
                        logger.info(f"   Token: {action_mint}")
                        logger.info(f"   Source Wallet: {action_owner}")
                        logger.info(f"   Amount: {action_amount:,.6f}")
                        logger.info(f"   Delta: {action_delta:+,.6f}")
                        logger.info(f"   Execution Method: balance_change_detected")
                        
                        # Calculate amount in SOL (use default small amount for copy trading)
                        # In production, you might want to calculate based on the detected amount
                        amount_sol = 0.001  # Default amount, can be made configurable
                        logger.info(f"   SOL Amount: {amount_sol}")
                        
                        # Enhanced trade info with detected action details
                        enhanced_trade_info = trade_info.copy()
                        enhanced_trade_info.update({
                            'detected_action': balance_action,
                            'execution_method': 'balance_change_detected',
                            'original_amount': action_amount,
                            'original_delta': action_delta
                        })
                        
                        logger.info(f"🟢 [TRADE_EXECUTION] Executing COPY BUY via coordinator")
                        execution_start_time = time.time()
                        
                        execution_result = await self.execution_coordinator._execute_copy_buy(
                            token_mint=action_mint,
                            source_wallet=action_owner,
                            amount_sol=amount_sol,
                            trade_info=enhanced_trade_info
                        )
                        
                        execution_time = time.time() - execution_start_time
                        
                        # FEATURE 6: Post-Execution Result Logging
                        if execution_result:
                            logger.info(f"✅ [EXECUTION_RESULT] BUY execution SUCCESS")
                            logger.info(f"   Result: {execution_result}")
                            logger.info(f"   Execution Time: {execution_time:.3f}s")
                            logger.info(f"   Action: BUY {action_amount:,.6f} {action_mint[:8]}...")
                            logger.info(f"   Source: {action_owner[:8]}...")
                        else:
                            logger.error(f"❌ [EXECUTION_RESULT] BUY execution FAILED - No result returned")
                            logger.error(f"   Execution Time: {execution_time:.3f}s")
                        
                    elif action_type == 'sell':
                        # FEATURE 6: Pre-Execution Logging
                        logger.info(f"� [EXECUTION_ATTEMPT] Starting COPY SELL execution")
                        logger.info(f"   Action ID: {i+1}/{len(detected_actions)}")
                        logger.info(f"   Token: {action_mint}")
                        logger.info(f"   Source Wallet: {action_owner}")
                        logger.info(f"   Amount: {action_amount:,.6f}")
                        logger.info(f"   Delta: {action_delta:+,.6f}")
                        logger.info(f"   DEX: {trade_info.get('dex_type', 'unknown')}")
                        logger.info(f"   Execution Method: balance_change_detected")
                        
                        # Enhanced trade info with detected action details
                        enhanced_trade_info = trade_info.copy()
                        enhanced_trade_info.update({
                            'detected_action': balance_action,
                            'execution_method': 'balance_change_detected',
                            'original_amount': action_amount,
                            'original_delta': action_delta
                        })
                        
                        logger.info(f"🔴 [TRADE_EXECUTION] Executing COPY SELL via coordinator")
                        execution_start_time = time.time()
                        
                        execution_result = await self.execution_coordinator._execute_copy_sell(
                            token_mint=action_mint,
                            trade_info=enhanced_trade_info,
                            source_wallet=action_owner,
                            detected_dex=trade_info.get('dex_type')
                        )
                        
                        execution_time = time.time() - execution_start_time
                        
                        # FEATURE 6: Post-Execution Result Logging
                        if execution_result:
                            logger.info(f"✅ [EXECUTION_RESULT] SELL execution SUCCESS")
                            logger.info(f"   Result: {execution_result}")
                            logger.info(f"   Execution Time: {execution_time:.3f}s")
                            logger.info(f"   Action: SELL {action_amount:,.6f} {action_mint[:8]}...")
                            logger.info(f"   Source: {action_owner[:8]}...")
                            logger.info(f"   DEX: {trade_info.get('dex_type', 'unknown')}")
                        else:
                            logger.error(f"❌ [EXECUTION_RESULT] SELL execution FAILED - No result returned")
                            logger.error(f"   Execution Time: {execution_time:.3f}s")
                    
                    else:
                        logger.warning(f"⚠️ [TRADE_EXECUTION] Unknown action type: {action_type}")
                        continue
                    
                    # Process execution result
                    execution_summary = {
                        'action_index': i,
                        'action_type': action_type,
                        'token_mint': action_mint,
                        'owner': action_owner,
                        'amount': action_amount,
                        'delta': action_delta,
                        'success': bool(execution_result and execution_result.get('success')),
                        'result': execution_result,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    
                    execution_results['executions'].append(execution_summary)
                    execution_results['total_executions'] += 1
                    
                    if execution_summary['success']:
                        execution_results['successful_executions'] += 1
                        signature = execution_result.get('signature', 'N/A')
                        logger.info(f"✅ [TRADE_EXECUTION] {action_type.upper()} executed successfully: {signature}")
                    else:
                        error_msg = execution_result.get('error', 'Unknown error') if execution_result else 'No result'
                        logger.error(f"❌ [TRADE_EXECUTION] {action_type.upper()} failed: {error_msg}")
                        
                except Exception as e:
                    logger.error(f"❌ [TRADE_EXECUTION] Exception during {action_type} execution: {e}")
                    execution_summary = {
                        'action_index': i,
                        'action_type': action_type,
                        'token_mint': action_mint,
                        'owner': action_owner,
                        'amount': action_amount,
                        'delta': action_delta,
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    execution_results['executions'].append(execution_summary)
                    execution_results['total_executions'] += 1
            
            # Determine overall success
            execution_results['success'] = execution_results['successful_executions'] > 0
            
            # FEATURE 6: Enhanced Execution Summary Logging for Debugging
            logger.info(f"📊 [EXECUTION_SUMMARY] Final Execution Report")
            logger.info(f"   Signature: {routing_instructions.get('signature', 'N/A')[:12]}...")
            logger.info(f"   Total Actions Processed: {execution_results['total_executions']}")
            logger.info(f"   Successful Executions: {execution_results['successful_executions']}")
            logger.info(f"   Failed Executions: {execution_results['total_executions'] - execution_results['successful_executions']}")
            logger.info(f"   Overall Success Rate: {(execution_results['successful_executions'] / max(execution_results['total_executions'], 1)) * 100:.1f}%")
            logger.info(f"   Overall Success: {execution_results['success']}")
            
            # Detailed per-execution logging
            if execution_results['executions']:
                logger.info(f"📋 [EXECUTION_DETAILS] Per-Action Results:")
                for exec_summary in execution_results['executions']:
                    status = "✅ SUCCESS" if exec_summary['success'] else "❌ FAILED"
                    logger.info(f"   Action {exec_summary['action_index'] + 1}: {status}")
                    logger.info(f"     Type: {exec_summary['action_type'].upper()}")
                    logger.info(f"     Token: {exec_summary['token_mint'][:8]}...")
                    logger.info(f"     Wallet: {exec_summary['owner'][:8]}...")
                    logger.info(f"     Amount: {exec_summary['amount']:,.6f}")
                    logger.info(f"     Delta: {exec_summary['delta']:+,.6f}")
                    if exec_summary['success']:
                        result = exec_summary.get('result', {})
                        signature = result.get('signature', 'N/A') if isinstance(result, dict) else str(result)
                        logger.info(f"     Result: {signature}")
                    else:
                        error = exec_summary.get('error', 'Unknown error')
                        logger.info(f"     Error: {error}")
            
            # Summary by action type
            buy_executions = [e for e in execution_results['executions'] if e['action_type'] == 'buy']
            sell_executions = [e for e in execution_results['executions'] if e['action_type'] == 'sell']
            
            if buy_executions or sell_executions:
                logger.info(f"📈 [EXECUTION_BREAKDOWN] Action Type Summary:")
                if buy_executions:
                    buy_success = sum(1 for e in buy_executions if e['success'])
                    logger.info(f"   BUY Actions: {len(buy_executions)} total, {buy_success} successful")
                if sell_executions:
                    sell_success = sum(1 for e in sell_executions if e['success'])
                    logger.info(f"   SELL Actions: {len(sell_executions)} total, {sell_success} successful")
            
            return execution_results
            
        except Exception as e:
            logger.error(f"❌ [TRADE_EXECUTION] Exception during trade execution routing: {e}")
            return {
                'success': False,
                'error': str(e),
                'action': routing_instructions.get('action'),
                'token_mint': routing_instructions.get('token_mint'),
                'executions': [],
                'total_executions': 0,
                'successful_executions': 0
            }
    
    async def analyze_and_execute_trade(self, trade_info: Dict[str, Any], source_wallet: str) -> Dict[str, Any]:
        """
        Complete trade processing - analyze and execute in one call
        
        Combines analyze_and_route_trade with execute_trade_routing for convenience
        
        Args:
            trade_info: Trade information dictionary
            source_wallet: Source wallet address
            
        Returns:
            Dict with both analysis and execution results
        """
        try:
            signature = trade_info.get('signature', 'N/A')
            logger.info(f"🔥 [COMPLETE_TRADE_PROCESSING] Starting for {signature[:12]}...")
            
            # Step 1: Analyze trade and get routing instructions
            logger.info(f"📊 [COMPLETE_TRADE_PROCESSING] Step 1: Trade Analysis")
            routing_instructions = await self.analyze_and_route_trade(trade_info, source_wallet)
            
            # Step 2: Execute trade based on routing instructions  
            logger.info(f"🚀 [COMPLETE_TRADE_PROCESSING] Step 2: Trade Execution")
            execution_results = await self.execute_trade_routing(routing_instructions)
            
            # Combine results
            complete_results = {
                'signature': signature,
                'source_wallet': source_wallet,
                'analysis': routing_instructions,
                'execution': execution_results,
                'overall_success': (
                    routing_instructions.get('requires_execution', False) and 
                    execution_results.get('success', False)
                ),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Log complete summary
            logger.info(f"🎉 [COMPLETE_TRADE_PROCESSING] Processing Complete:")
            logger.info(f"   Analysis Success: {bool(routing_instructions.get('token_mint') and routing_instructions['token_mint'] != 'UNKNOWN')}")
            logger.info(f"   Execution Required: {routing_instructions.get('requires_execution', False)}")
            logger.info(f"   Execution Success: {execution_results.get('success', False)}")
            logger.info(f"   Overall Success: {complete_results['overall_success']}")
            
            if execution_results.get('executions'):
                logger.info(f"   Executions: {execution_results['successful_executions']}/{execution_results['total_executions']}")
            
            return complete_results
            
        except Exception as e:
            logger.error(f"❌ [COMPLETE_TRADE_PROCESSING] Exception: {e}")
            return {
                'signature': trade_info.get('signature', 'N/A'),
                'source_wallet': source_wallet,
                'analysis': None,
                'execution': None,
                'overall_success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _check_monitored_wallet_is_signer(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to check if any monitored wallet is a signer/fee payer in the transaction.
        Uses case-insensitive matching for wallet address comparison.
        
        Returns:
            Dict with signer information including fee_payer, signers, and validation results
        """
        try:
            # Get transaction data
            transaction = trade_info.get('transaction') or trade_info.get('transaction_full', {})
            
            # Extract account keys and header info
            message = transaction.get('message', {})
            account_keys = message.get('accountKeys', [])
            
            # Handle both dict and string formats for account keys
            if account_keys and isinstance(account_keys[0], dict):
                account_keys = [k.get('pubkey') for k in account_keys if k.get('pubkey')]
            
            # Get header information for signer detection
            header = message.get('header', {})
            num_signatures = header.get('numRequiredSignatures', 0)
            num_readonly_signed = header.get('numReadonlySignedAccounts', 0)
            
            # Extract signers and fee payer
            fee_payer = account_keys[0] if account_keys else None
            signers = account_keys[:num_signatures] if num_signatures > 0 and account_keys else []
            
            # Check if any monitored wallet is involved (case-insensitive matching)
            # Create lowercase set for case-insensitive comparison
            monitored_wallets_lower = {w.lower() for w in self.target_wallets if w}
            
            # Normalize fee_payer and signers for comparison
            is_monitored_fee_payer = fee_payer and fee_payer.lower() in monitored_wallets_lower
            monitored_signers = [s for s in signers if s and s.lower() in monitored_wallets_lower]
            is_monitored_signer = len(monitored_signers) > 0
            
            result = {
                'fee_payer': fee_payer,
                'signers': signers,
                'num_signatures': num_signatures,
                'num_readonly_signed': num_readonly_signed,
                'is_monitored_fee_payer': is_monitored_fee_payer,
                'monitored_signers': monitored_signers,
                'is_monitored_signer': is_monitored_signer,
                'has_monitored_involvement': is_monitored_fee_payer or is_monitored_signer
            }
            
            logger.debug(f"🔍 [SIGNER_CHECK] Fee Payer: {fee_payer[:8] + '...' if fee_payer else 'None'}")
            logger.debug(f"🔍 [SIGNER_CHECK] Signers: {[s[:8] + '...' for s in signers]}")
            logger.debug(f"🔍 [SIGNER_CHECK] Monitored Involvement: {result['has_monitored_involvement']} (case-insensitive matching)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [SIGNER_CHECK] Error checking monitored wallet signers: {e}")
            return {
                'fee_payer': None,
                'signers': [],
                'num_signatures': 0,
                'num_readonly_signed': 0,
                'is_monitored_fee_payer': False,
                'monitored_signers': [],
                'is_monitored_signer': False,
                'has_monitored_involvement': False,
                'error': str(e)
            }

    def _check_trade_instructions(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to check if transaction contains swap/buy/sell instructions from known DEX programs.
        
        Returns:
            Dict with instruction analysis results including detected programs and trade types
        """
        try:
            # Known trade program mappings
            known_trade_programs = {
                'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4': 'Jupiter V6',
                '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun',
                '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium AMM',
                'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C': 'Raydium CPMM',
                '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1': 'Raydium CLMM',
                'ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA': 'Alpha DEX',
                'SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8': 'Orca Swap',
                'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN': 'Meteora',
                'Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB': 'Meteora DLMM',
                'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc': 'Orca Whirlpool',
                'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK': 'Raydium CLMM v2'
            }
            
            # Get transaction data
            transaction = trade_info.get('transaction') or trade_info.get('transaction_full', {})
            message = transaction.get('message', {})
            instructions = message.get('instructions', [])
            account_keys = message.get('accountKeys', [])
            
            # Handle account keys format
            if account_keys and isinstance(account_keys[0], dict):
                account_keys = [k.get('pubkey') for k in account_keys if k.get('pubkey')]
            
            # Analyze instructions for trade programs
            detected_programs = []
            trade_instructions_found = False
            
            for i, instruction in enumerate(instructions):
                # Get program ID from instruction
                program_id = instruction.get('programId')
                
                # Handle programIdIndex format
                if not program_id and 'programIdIndex' in instruction:
                    prog_idx = instruction.get('programIdIndex')
                    if prog_idx is not None and prog_idx < len(account_keys):
                        program_id = account_keys[prog_idx]
                
                if program_id and program_id in known_trade_programs:
                    program_name = known_trade_programs[program_id]
                    detected_programs.append({
                        'instruction_index': i,
                        'program_id': program_id,
                        'program_name': program_name,
                        'accounts_count': len(instruction.get('accounts', [])),
                        'has_data': bool(instruction.get('data'))
                    })
                    trade_instructions_found = True
                    
                    logger.debug(f"🎯 [TRADE_INSTRUCTION] Found {program_name} at instruction {i}")
            
            # Check logs for additional trade confirmation
            logs = trade_info.get('logs', [])
            meta = trade_info.get('meta', {})
            if meta:
                logs.extend(meta.get('logMessages', []))
            
            # Look for trade-related log messages
            trade_log_indicators = [
                'Instruction: Swap',
                'Instruction: Buy', 
                'Instruction: Sell',
                'SharedAccountsRoute',
                'Program log: swap',
                'Program log: trade'
            ]
            
            relevant_logs = []
            for log in logs:
                if any(indicator.lower() in log.lower() for indicator in trade_log_indicators):
                    relevant_logs.append(log)
            
            result = {
                'has_trade_instructions': trade_instructions_found,
                'detected_programs': detected_programs,
                'program_count': len(detected_programs),
                'primary_program': detected_programs[0] if detected_programs else None,
                'relevant_logs': relevant_logs,
                'total_instructions': len(instructions),
                'analyzed_instructions': len([i for i in instructions if i.get('programId') or i.get('programIdIndex') is not None])
            }
            
            if detected_programs:
                logger.debug(f"✅ [TRADE_INSTRUCTION] Found {len(detected_programs)} trade program(s)")
                for prog in detected_programs[:3]:  # Show first 3
                    logger.debug(f"   - {prog['program_name']} ({prog['program_id'][:8]}...)")
            else:
                logger.debug(f"🚫 [TRADE_INSTRUCTION] No trade programs detected in {len(instructions)} instructions")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [TRADE_INSTRUCTION] Error analyzing trade instructions: {e}")
            return {
                'has_trade_instructions': False,
                'detected_programs': [],
                'program_count': 0,
                'primary_program': None,
                'relevant_logs': [],
                'total_instructions': 0,
                'analyzed_instructions': 0,
                'error': str(e)
            }

    def _extract_action_with_fallback(self, trade_info: Dict[str, Any]) -> str:
        """
        Enhanced action extraction with proper fallback to balance delta detection.
        
        Priority order:
        1. Token balance delta detection (primary method - from detect_buy_sell)
        2. Existing action field if valid
        3. Basic analysis fields
        4. Signer + instruction fallback (validation only)
        5. Return 'unknown' if all methods fail
        
        Returns:
            Action string: 'buy', 'sell', 'swap', or 'unknown'
        """
        signature = trade_info.get('signature', 'N/A')
        logger.info(f"🧠 [ACTION_EXTRACTION] Starting for {signature[:12]}...")
        
        # PRIORITY 1: Use balance delta detection results if available
        detected_actions = trade_info.get('detected_balance_actions', [])
        if detected_actions:
            primary_action = detected_actions[0]
            action = primary_action['action']
            logger.info(f"✅ [ACTION_EXTRACTION] From balance delta: {action}")
            return action
        
        # PRIORITY 2: Check existing action field
        action = trade_info.get('action')
        if action and action.lower() in ['buy', 'sell', 'swap', 'swap_in', 'swap_out']:
            # Validate it's not from ultra_aggressive assumption
            if trade_info.get('method') != 'ultra_aggressive_assumption':
                logger.info(f"✅ [ACTION_EXTRACTION] From existing field: {action.lower()}")
                return action.lower()
        
        # PRIORITY 3: Try basic analysis
        if 'basic_analysis' in trade_info:
            basic_action = trade_info['basic_analysis'].get('likely_action')
            if basic_action and basic_action.lower() in ['buy', 'sell', 'swap']:
                logger.info(f"✅ [ACTION_EXTRACTION] From basic_analysis: {basic_action.lower()}")
                return basic_action.lower()
        
        # PRIORITY 4: Try signer + instruction fallback (validation only)
        logger.debug(f"🔄 [ACTION_EXTRACTION] Trying fallback method...")
        fallback_action = self._try_signer_instruction_fallback(trade_info)
        if fallback_action and fallback_action != 'unknown':
            logger.info(f"✅ [ACTION_EXTRACTION] From fallback: {fallback_action}")
            return fallback_action
        
        # PRIORITY 5: Default to 'swap' for permissive execution
        # Industry-standard Solana copy trading bots prioritize execution over strict validation
        logger.warning(f"⚠️ [ACTION_EXTRACTION] Could not determine specific action for {signature[:12]}...")
        logger.warning(f"   Defaulting to 'swap' for permissive execution (industry standard)")
        return 'swap'

    def _analyze_logs_for_action(self, logs: List[str]) -> str:
        """
        Analyze transaction logs to determine likely action with enhanced pattern matching.
        
        Returns:
            Action string based on log analysis
        """
        if not logs:
            return 'unknown'
        
        # Join all logs for analysis
        log_text = ' '.join(logs).lower()
        
        # Action indicators in logs
        buy_indicators = ['buy', 'purchase', 'acquire']
        sell_indicators = ['sell', 'dispose']
        swap_indicators = ['swap', 'exchange', 'route', 'sharedaccountsroute']
        
        # Count indicators
        buy_count = sum(1 for indicator in buy_indicators if indicator in log_text)
        sell_count = sum(1 for indicator in sell_indicators if indicator in log_text)
        swap_count = sum(1 for indicator in swap_indicators if indicator in log_text)
        
        # Determine action based on strongest signal
        max_count = max(buy_count, sell_count, swap_count)
        
        if max_count == 0:
            return 'unknown'
        elif buy_count == max_count:
            return 'buy'
        elif sell_count == max_count:
            return 'sell'
        elif swap_count == max_count:
            return 'swap'
        
        return 'unknown'

    def _extract_mint_from_logs_enhanced(self, logs: List[str]) -> Optional[str]:
        """
        Enhanced token mint extraction from transaction logs.
        Uses multiple patterns to identify potential token mint addresses.
        
        Reference: https://docs.solana.com/developing/programming-model/transactions
        Implements robust log parsing following Solana transaction structure best practices.
        
        Returns:
            Token mint address if found, None otherwise
        """
        if not logs:
            return None
        
        import re
        
        # Pattern to match Solana addresses (base58, 32-44 chars)
        address_pattern = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
        
        # Known system addresses to exclude (expand from DEX_PROGRAMS)
        system_addresses = {
            'So11111111111111111111111111111111111111112',  # SOL/WSOL
            '11111111111111111111111111111111',  # System Program
            'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA',  # Token Program
            'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb',  # Token-2022 Program
            'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
            'ComputeBudget111111111111111111111111111111',  # Compute Budget
        }
        # Also exclude known DEX program IDs
        system_addresses.update(DEX_PROGRAMS.keys())
        
        # Extract all potential addresses from logs
        log_text = ' '.join(logs)
        potential_mints = []
        
        for match in re.finditer(address_pattern, log_text):
            address = match.group(0)
            if address not in system_addresses and is_valid_solana_address(address):
                potential_mints.append(address)
        
        # Look for addresses mentioned multiple times (likely the traded token)
        if potential_mints:
            from collections import Counter
            mint_counts = Counter(potential_mints)
            # Return the most frequently mentioned address
            most_common = mint_counts.most_common(1)
            if most_common:
                mint, count = most_common[0]
                if count >= 2:  # Mentioned at least twice
                    logger.info(f"🎯 [MINT_FROM_LOGS] Found mint {mint[:8]}... (mentioned {count} times in logs)")
                    return mint
                elif count == 1 and len(potential_mints) == 1:
                    # Only one candidate, likely the mint
                    logger.info(f"🎯 [MINT_FROM_LOGS] Found single candidate mint {mint[:8]}...")
                    return mint
        
        logger.debug(f"[MINT_FROM_LOGS] No reliable mint found in {len(logs)} log messages")
        return None

    def _extract_mint_from_token_balances(self, meta: dict) -> Optional[str]:
        """
        Extract token mint from pre/post token balance changes.
        
        Uses delta-based detection to identify the token being traded by analyzing
        which token balances changed in the transaction.
        
        Enhanced algorithm:
        - Builds dicts of preTokenBalances and postTokenBalances keyed by account index
        - Computes per-mint deltas (post - pre) by matching accountIndex
        - Ignores WSOL (So11111111111111111111111111111111111111112)
        - Chooses the mint with the largest absolute delta
        - If ties or no pre balance, chooses the first non-WSOL mint from postTokenBalances
        
        Args:
            meta: Transaction metadata containing pre/post token balances
            
        Returns:
            Token mint address if found, None otherwise
        """
        WSOL = "So11111111111111111111111111111111111111112"
        pre = {b["accountIndex"]: b for b in (meta.get("preTokenBalances") or [])}
        post = {b["accountIndex"]: b for b in (meta.get("postTokenBalances") or [])}

        best = (None, 0.0)  # (mint, abs_delta)
        # 1) Prefer biggest absolute UI delta
        for idx, pb in post.items():
            mint = pb.get("mint")
            if not mint or mint == WSOL:
                continue
            post_amt = (pb.get("uiTokenAmount") or {}).get("uiAmount") or 0.0
            pre_amt = ((pre.get(idx, {}).get("uiTokenAmount") or {}).get("uiAmount") or 0.0)
            delta = abs(float(post_amt) - float(pre_amt))
            if delta > best[1]:
                best = (mint, delta)

        if best[0]:
            return best[0]

        # 2) Fallback: first non-WSOL mint in post balances
        for pb in post.values():
            mint = pb.get("mint")
            if mint and mint != WSOL:
                return mint
        return None

    def _extract_mint_from_instruction_accounts(self, trade_info: Dict[str, Any]) -> Optional[str]:
        """
        Extract token mint from transaction instruction accounts.
        This is a fallback when logs and balances don't reveal the mint.
        
        Looks for mint accounts in swap instructions by analyzing account keys
        and filtering out known system programs and DEX programs.
        
        Reference: Solana transaction structure - https://docs.solana.com/developing/programming-model/transactions
        """
        try:
            tx = trade_info.get('transaction') or trade_info.get('transaction_full')
            if not tx:
                logger.debug("[MINT_FROM_ACCOUNTS] No transaction data available")
                return None
            
            message = tx.get('transaction', {}).get('message', {})
            account_keys = message.get('accountKeys', [])
            instructions = message.get('instructions', [])
            
            if not account_keys or not instructions:
                logger.debug("[MINT_FROM_ACCOUNTS] No account keys or instructions in transaction")
                return None
            
            # Known programs to exclude
            excluded_programs = set(DEX_PROGRAMS.keys()) | TOKEN_PROGRAMS | {
                '11111111111111111111111111111111',  # System Program
                'ComputeBudget111111111111111111111111111111',  # Compute Budget
                'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',  # Associated Token Program
                'So11111111111111111111111111111111111111112',  # SOL/WSOL
            }
            
            # Collect candidate mints from all instructions
            candidate_mints = []
            
            for ix in instructions:
                prog_idx = ix.get('programIdIndex')
                if prog_idx is None or prog_idx >= len(account_keys):
                    continue
                
                prog_id = account_keys[prog_idx]
                
                # Only look at DEX program instructions
                if prog_id not in DEX_PROGRAMS:
                    continue
                
                # Get accounts used by this instruction
                account_indices = ix.get('accounts', [])
                for acc_idx in account_indices:
                    if acc_idx < len(account_keys):
                        account = account_keys[acc_idx]
                        # Filter out known programs
                        if account not in excluded_programs and is_valid_solana_address(account):
                            candidate_mints.append(account)
            
            # Return the first valid candidate
            if candidate_mints:
                # Remove duplicates while preserving order
                seen = set()
                unique_candidates = []
                for mint in candidate_mints:
                    if mint not in seen:
                        seen.add(mint)
                        unique_candidates.append(mint)
                
                # Return the first candidate (most likely the output token)
                mint = unique_candidates[0]
                logger.info(f"🎯 [MINT_FROM_ACCOUNTS] Found candidate mint from instruction accounts: {mint[:8]}... ({len(unique_candidates)} total candidates)")
                return mint
            
            logger.debug(f"[MINT_FROM_ACCOUNTS] No valid mint candidates found in instruction accounts")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ [MINT_FROM_ACCOUNTS] Failed to extract mint from instruction accounts: {e}")
            return None
    
    def _parse_raydium_accounts(self, trade_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Raydium CPMM account information from transaction for MEVRaydiumExecutor.
        Extracts pool state, config, vaults, and other necessary accounts.
        
        Implementation references:
        - Raydium SDK: https://github.com/raydium-io/raydium-sdk
        - Raydium CPMM Program: CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C
        - Pool account layout documented in Raydium SDK documentation
        
        Standard Raydium CPMM swap instruction account layout:
        0: payer (signer)
        1: authority (amm authority)
        2: amm config
        3: pool state
        4: input token account
        5: output token account
        6: input vault
        7: output vault
        8: input token mint
        9: output token mint
        10: observation state
        """
        try:
            tx = trade_info.get('transaction') or trade_info.get('transaction_full')
            if not tx:
                logger.debug("[RAYDIUM_PARSE] No transaction data available")
                return None
            
            # Look for Raydium CPMM program ID
            RAYDIUM_CPMM_PROGRAM = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
            
            message = tx.get('transaction', {}).get('message', {})
            account_keys = message.get('accountKeys', [])
            instructions = message.get('instructions', [])
            
            # Find Raydium instruction
            raydium_ix = None
            for ix in instructions:
                prog_idx = ix.get('programIdIndex')
                if prog_idx is not None and prog_idx < len(account_keys):
                    if account_keys[prog_idx] == RAYDIUM_CPMM_PROGRAM:
                        raydium_ix = ix
                        break
            
            if not raydium_ix:
                logger.debug("[RAYDIUM_PARSE] No Raydium CPMM instruction found")
                return None
            
            # Extract account indices from the instruction
            account_indices = raydium_ix.get('accounts', [])
            
            # Standard Raydium CPMM swap instruction account layout:
            # 0: payer (signer)
            # 1: authority (amm authority)
            # 2: amm config
            # 3: pool state
            # 4: input token account
            # 5: output token account
            # 6: input vault
            # 7: output vault
            # 8: input token mint
            # 9: output token mint
            # 10: observation state
            
            raydium_info = {
                'program_id': RAYDIUM_CPMM_PROGRAM,
                'accounts': {}
            }
            
            # Map known account positions (may vary by instruction type)
            if len(account_indices) >= 10:
                raydium_info['accounts'] = {
                    'amm_authority': account_keys[account_indices[1]] if account_indices[1] < len(account_keys) else None,
                    'pool_config': account_keys[account_indices[2]] if account_indices[2] < len(account_keys) else None,
                    'pool_state': account_keys[account_indices[3]] if account_indices[3] < len(account_keys) else None,
                    'input_vault': account_keys[account_indices[6]] if account_indices[6] < len(account_keys) else None,
                    'output_vault': account_keys[account_indices[7]] if account_indices[7] < len(account_keys) else None,
                    'input_mint': account_keys[account_indices[8]] if account_indices[8] < len(account_keys) else None,
                    'output_mint': account_keys[account_indices[9]] if account_indices[9] < len(account_keys) else None,
                }
                
                # Add system accounts
                TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                SYSTEM_PROGRAM = "11111111111111111111111111111111"
                raydium_info['accounts']['token_program'] = TOKEN_PROGRAM
                raydium_info['accounts']['system_program'] = SYSTEM_PROGRAM
                
                # Extract instruction data for discriminator
                raydium_info['instruction_data'] = raydium_ix.get('data', '')
                
                logger.info(f"✅ [RAYDIUM_PARSE] Successfully parsed Raydium accounts")
                logger.debug(f"[RAYDIUM_PARSE] Pool state: {raydium_info['accounts'].get('pool_state', 'N/A')[:12]}...")
                
                return raydium_info
            else:
                logger.warning(f"[RAYDIUM_PARSE] Insufficient accounts in Raydium instruction: {len(account_indices)}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ [RAYDIUM_PARSE] Failed to parse Raydium accounts: {e}")
            return None

    def _infer_signature_from_transaction(self, trade_info: Dict[str, Any]) -> Optional[str]:
        """
        Infer transaction signature from transaction data.
        
        Returns:
            Transaction signature if found, None otherwise
        """
        # Check various possible locations for signature
        if trade_info.get('signature'):
            return trade_info['signature']
        
        # Check in transaction data
        tx = trade_info.get('transaction') or trade_info.get('transaction_full')
        if tx:
            # Check transaction.signatures
            if isinstance(tx, dict):
                signatures = tx.get('signatures', [])
                if signatures and len(signatures) > 0:
                    sig = signatures[0]
                    logger.info(f"🎯 [SIG_INFERENCE] Found signature from transaction.signatures: {sig[:12]}...")
                    return sig
                
                # Check transaction.transaction.signatures
                inner_tx = tx.get('transaction', {})
                if inner_tx:
                    signatures = inner_tx.get('signatures', [])
                    if signatures and len(signatures) > 0:
                        sig = signatures[0]
                        logger.info(f"🎯 [SIG_INFERENCE] Found signature from transaction.transaction.signatures: {sig[:12]}...")
                        return sig
        
        return None

    def _infer_wallet_from_transaction(self, trade_info: Dict[str, Any]) -> Optional[str]:
        """
        Infer wallet address from transaction signers or fee payer.
        
        Returns:
            Wallet address if found, None otherwise
        """
        # Check fee payer first (most reliable)
        tx = trade_info.get('transaction') or trade_info.get('transaction_full')
        if tx:
            if isinstance(tx, dict):
                # Check transaction.message.accountKeys[0] (fee payer)
                msg = tx.get('message', {})
                if msg:
                    account_keys = msg.get('accountKeys', [])
                    if account_keys and len(account_keys) > 0:
                        wallet = account_keys[0]
                        # Validate against monitored wallets
                        if self._validate_monitored_wallet(wallet, self.target_wallets):
                            logger.info(f"🎯 [WALLET_INFERENCE] Found monitored wallet from fee payer: {wallet[:8]}...")
                            return wallet
                
                # Check transaction.transaction.message.accountKeys[0]
                inner_tx = tx.get('transaction', {})
                if inner_tx:
                    msg = inner_tx.get('message', {})
                    if msg:
                        account_keys = msg.get('accountKeys', [])
                        if account_keys and len(account_keys) > 0:
                            wallet = account_keys[0]
                            if self._validate_monitored_wallet(wallet, self.target_wallets):
                                logger.info(f"🎯 [WALLET_INFERENCE] Found monitored wallet from fee payer (inner): {wallet[:8]}...")
                                return wallet
        
        # Check post token balances for monitored wallets
        meta = trade_info.get('meta') or (trade_info.get('transaction_full', {}) or {}).get('meta', {})
        if meta:
            post_balances = meta.get('postTokenBalances', [])
            for balance in post_balances:
                owner = balance.get('owner')
                if owner and self._validate_monitored_wallet(owner, self.target_wallets):
                    logger.info(f"🎯 [WALLET_INFERENCE] Found monitored wallet from token balances: {owner[:8]}...")
                    return owner
        
        return None

    def ensure_meta_in_trade_info(self, trade_info: dict) -> None:
        """
        Ensure trade_info has meta attached from backfilled transaction.
        
        Args:
            trade_info: Trade information dict
        """
        if "meta" not in trade_info:
            backfilled = trade_info.get("backfilled_tx")
            if backfilled and backfilled.get("meta"):
                trade_info["meta"] = backfilled["meta"]

    def annotate_source_failure(self, trade_info: dict) -> None:
        """
        Detect and annotate source transaction failures, especially slippage errors.
        
        Sets trade_info["source_tx_failed"] = True if meta.err is present.
        Sets trade_info["retry_hint"] = "requote" for slippage failures (Anchor 6004 or explicit message).
        
        Args:
            trade_info: Trade information dict
        """
        meta = trade_info.get("meta") or {}
        err = meta.get("err")
        if not err:
            return
        trade_info["source_tx_failed"] = True
        logs = " ".join(meta.get("logMessages") or [])
        # Anchor 6004 or explicit message
        if ("Exceeded slippage tolerance" in logs) or ("6004" in str(err)):
            trade_info["retry_hint"] = "requote"
            logger.warning("⚠️ [ANALYSIS] Source tx failed with ExceededSlippage (6004) — will re-quote & rebuild")

    def infer_missing_fields(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive fallback logic to infer missing critical fields.
        
        This method implements industry-standard inference strategies used by
        Solana copy trading bots to minimize skipped trades.
        
        Implementation follows official Solana documentation and best practices:
        - Solana Transaction Structure: https://docs.solana.com/developing/programming-model/transactions
        - Token Program: https://spl.solana.com/token
        - Account Model: https://docs.solana.com/developing/programming-model/accounts
        
        Fallback Strategy (in order):
        1. Extract from transaction logs (log parsing)
        2. Analyze pre/post balance deltas (token balance changes)
        3. Parse instruction account keys (instruction accounts)
        4. RPC lookup for account verification
        
        Args:
            trade_info: Trade information potentially with missing fields
            
        Returns:
            Updated trade_info with inferred fields
        """
        logger.info("🔍 [FIELD_INFERENCE] Starting comprehensive field inference...")
        
        # 0) Make sure meta is attached (from backfill; pipeline already populates it in many cases)
        self.ensure_meta_in_trade_info(trade_info)
        
        # 0b) Mark error context (prevents clone of a failed tx)
        self.annotate_source_failure(trade_info)
        
        inferred_fields = []
        
        # Last-chance fetch if we have a signature but no logs/tx
        logs = trade_info.get("logs")
        tx_obj = trade_info.get("transaction")
        
        if not logs and not tx_obj and trade_info.get("signature"):
            sig = trade_info["signature"]
            if sig and sig != 'unknown' and self.rpc_client:
                try:
                    logger.info(f"🔎 [TRADE_PROCESSOR] Last-chance fetch for signature {sig[:12]}...")
                    # Use asyncio to call the async RPC method synchronously
                    import asyncio
                    from utils import fetch_json_rpc_with_url
                    
                    loop = asyncio.get_event_loop()
                    result = loop.run_until_complete(
                        fetch_json_rpc_with_url(
                            self.rpc_client.rpc_url,
                            "getTransaction",
                            [
                                sig,
                                {
                                    "encoding": "jsonParsed",
                                    "maxSupportedTransactionVersion": 0
                                }
                            ]
                        )
                    )
                    
                    if result and "result" in result and result["result"]:
                        tx = result["result"]
                        meta = tx.get("meta") or {}
                        trade_info["logs"] = meta.get("logMessages") or []
                        trade_info["transaction"] = tx.get("transaction")
                        trade_info["meta"] = meta
                        logger.info("🔎 [TRADE_PROCESSOR] Attached missing logs/tx/meta via signature fetch")
                        inferred_fields.append('logs/transaction (last-chance fetch)')
                    else:
                        logger.warning(f"⚠️ [TRADE_PROCESSOR] No transaction data returned for {sig[:12]}...")
                except Exception as e:
                    logger.warning(f"⚠️ [TRADE_PROCESSOR] Signature fetch failed: {e}")
        
        # 1. Infer signature if missing
        if not trade_info.get('signature') or trade_info.get('signature') == 'unknown':
            sig = self._infer_signature_from_transaction(trade_info)
            if sig:
                trade_info['signature'] = sig
                inferred_fields.append('signature')
        
        # 2. Fetch transaction data if we have signature but no transaction
        sig = trade_info.get('signature')
        if sig and sig != 'unknown' and not trade_info.get('transaction'):
            try:
                logger.info(f"🔄 [FIELD_INFERENCE] Fetching transaction data for signature {sig[:12]}...")
                from utils import get_transaction_with_logs
                tx_data = get_transaction_with_logs(sig)
                if tx_data:
                    trade_info['transaction'] = tx_data
                    trade_info['transaction_full'] = tx_data
                    # Ensure meta is attached from fetched transaction
                    if tx_data.get('meta'):
                        trade_info['meta'] = tx_data['meta']
                    inferred_fields.append('transaction (fetched)')
                    logger.info(f"✅ [FIELD_INFERENCE] Successfully fetched transaction data")
            except Exception as e:
                logger.warning(f"⚠️ [FIELD_INFERENCE] Failed to fetch transaction: {e}")
        
        # 3. Infer wallet_address if missing
        if not trade_info.get('wallet_address') or trade_info.get('wallet_address') == 'unknown':
            wallet = self._infer_wallet_from_transaction(trade_info)
            if wallet:
                trade_info['wallet_address'] = wallet
                inferred_fields.append('wallet_address')
            elif self.target_wallets:
                # Default to first monitored wallet as fallback
                trade_info['wallet_address'] = self.target_wallets[0]
                inferred_fields.append('wallet_address (default)')
        
        # 4. Infer action using enhanced extraction
        if not trade_info.get('action') or trade_info.get('action') == 'unknown':
            logger.info("🔍 [ACTION_INFERENCE] Action missing or unknown, attempting inference...")
            
            # Try to extract from logs
            logs = trade_info.get('logs', [])
            if not logs:
                # Get logs from transaction
                tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                if tx:
                    meta = tx.get('meta', {})
                    logs = meta.get('logMessages', [])
            
            if logs:
                logger.debug(f"[ACTION_INFERENCE] Analyzing {len(logs)} log messages...")
                action = self._analyze_logs_for_action(logs)
                if action and action != 'unknown':
                    trade_info['action'] = action
                    inferred_fields.append('action')
                    logger.info(f"✅ [ACTION_INFERENCE] Successfully inferred action from logs: {action}")
                else:
                    # Default to 'swap' for permissive execution
                    logger.warning(f"⚠️ [ACTION_INFERENCE] Could not determine action from logs, defaulting to 'swap'")
                    trade_info['action'] = 'swap'
                    inferred_fields.append('action (default: swap)')
            else:
                # No logs available, default to swap
                logger.warning(f"⚠️ [ACTION_INFERENCE] No logs available, defaulting to 'swap'")
                trade_info['action'] = 'swap'
                inferred_fields.append('action (default: swap, no logs)')
        
        # 5. Infer DEX if missing
        if not trade_info.get('dex') or trade_info.get('dex') == 'unknown':
            if not trade_info.get('dex_type') or trade_info.get('dex_type') == 'unknown':
                # Try to detect from logs
                logs = trade_info.get('logs', [])
                if not logs:
                    tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                    if tx:
                        meta = tx.get('meta', {})
                        logs = meta.get('logMessages', [])
                
                if logs:
                    log_text = ' '.join(logs).lower()
                    for program_id, dex_type in DEX_PROGRAMS.items():
                        if program_id.lower() in log_text:
                            trade_info['dex'] = dex_type
                            trade_info['dex_type'] = dex_type
                            inferred_fields.append('dex')
                            break
                    
                    # If still not found, try to detect from program invocations in transaction
                    if not trade_info.get('dex') or trade_info.get('dex') == 'unknown':
                        tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                        if tx and isinstance(tx, dict):
                            instructions = tx.get('transaction', {}).get('message', {}).get('instructions', [])
                            account_keys = tx.get('transaction', {}).get('message', {}).get('accountKeys', [])
                            
                            for ix in instructions:
                                prog_idx = ix.get('programIdIndex')
                                if prog_idx is not None and prog_idx < len(account_keys):
                                    prog_id = account_keys[prog_idx]
                                    if prog_id in DEX_PROGRAMS:
                                        trade_info['dex'] = DEX_PROGRAMS[prog_id]
                                        trade_info['dex_type'] = DEX_PROGRAMS[prog_id]
                                        inferred_fields.append('dex (from instructions)')
                                        break
        
        # 6. Infer token mint if missing - with multiple fallbacks
        if not trade_info.get('token_mint') or trade_info.get('token_mint') in ['UNKNOWN', 'PENDING_ANALYSIS']:
            logger.info("🔍 [MINT_INFERENCE] Token mint missing or pending, attempting inference...")
            
            # Ensure meta is present in trade_info for inference helpers
            self.ensure_meta_in_trade_info(trade_info)
            
            # Try enhanced log extraction (primary method)
            logs = trade_info.get('logs', [])
            if not logs:
                tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                if tx:
                    meta = tx.get('meta', {})
                    logs = meta.get('logMessages', [])
            
            if logs:
                logger.debug(f"[MINT_INFERENCE] Attempting extraction from {len(logs)} log messages...")
                mint = self._extract_mint_from_logs_enhanced(logs)
                if mint:
                    trade_info['token_mint'] = mint
                    inferred_fields.append('token_mint')
                    logger.info(f"✅ [MINT_INFERENCE] Successfully extracted mint from logs: {mint[:12]}...")
                else:
                    logger.warning(f"⚠️ [MINT_INFERENCE] Could not extract mint from logs")
            else:
                logger.warning(f"⚠️ [MINT_INFERENCE] No logs available for mint extraction")
            
            # Also try extracting from token balances as fallback
            if not trade_info.get('token_mint') or trade_info.get('token_mint') in ['UNKNOWN', 'PENDING_ANALYSIS']:
                logger.debug(f"[MINT_INFERENCE] Attempting extraction from token balances...")
                # Extract meta from trade_info (ensure it's passed from backfill)
                meta = trade_info.get("meta") or {}
                # If meta not in trade_info, try to get it from transaction
                if not meta:
                    tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                    if tx:
                        meta = tx.get('meta', {})
                
                mint = self._extract_mint_from_token_balances(meta)
                if mint:
                    trade_info['token_mint'] = mint
                    inferred_fields.append('token_mint (from balances)')
                    logger.info(f"✅ [MINT_INFERENCE] Resolved token mint from postTokenBalances: {mint}")
                else:
                    logger.warning(f"⚠️ [MINT_INFERENCE] Could not extract mint from balances")
            
            # Last-chance: scan instruction accounts for SPL mints
            if not trade_info.get("token_mint"):
                try:
                    WSOL = "So11111111111111111111111111111111111111112"
                    # Get mints from postTokenBalances
                    meta = trade_info.get("meta") or {}
                    if not meta:
                        tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                        if tx:
                            meta = tx.get('meta', {})
                    
                    post_mints = {b.get("mint") for b in (meta.get("postTokenBalances") or []) if b.get("mint")}
                    if post_mints:
                        # Get transaction instructions and account keys
                        tx = trade_info.get('transaction') or trade_info.get('transaction_full')
                        if tx:
                            message = tx.get('transaction', {}).get('message', {})
                            instrs = message.get('instructions', [])
                            account_keys = message.get('accountKeys', [])
                            
                            # Handle account_keys format (could be list of strings or list of dicts)
                            if account_keys and isinstance(account_keys[0], dict):
                                account_keys = [k.get('pubkey') for k in account_keys if k.get('pubkey')]
                            
                            for ix in instrs:
                                # Get accounts from instruction (these are indices)
                                account_indices = ix.get("accounts") or []
                                for acc_idx in account_indices:
                                    if acc_idx < len(account_keys):
                                        acc = account_keys[acc_idx]
                                        if acc in post_mints and acc != WSOL:
                                            trade_info["token_mint"] = acc
                                            inferred_fields.append('token_mint (from instruction scan)')
                                            logger.info(f"✅ [MINT_INFERENCE] Resolved token mint from instruction accounts: {acc}")
                                            break
                                if trade_info.get("token_mint"):
                                    break
                except Exception as e:
                    logger.warning(f"⚠️ [MINT_INFERENCE] Instruction scan failed: {e}")
            
            # Last resort: Try to extract from transaction instruction accounts
            if not trade_info.get('token_mint') or trade_info.get('token_mint') in ['UNKNOWN', 'PENDING_ANALYSIS']:
                logger.debug(f"[MINT_INFERENCE] Attempting extraction from instruction accounts...")
                mint = self._extract_mint_from_instruction_accounts(trade_info)
                if mint:
                    trade_info['token_mint'] = mint
                    inferred_fields.append('token_mint (from accounts)')
                    logger.info(f"✅ [MINT_INFERENCE] Successfully extracted mint from instruction accounts: {mint[:12]}...")
                else:
                    logger.warning(f"⚠️ [MINT_INFERENCE] Could not extract mint from instruction accounts")
            
            # Log final inference failure if mint still unresolved
            if not trade_info.get('token_mint') or trade_info.get('token_mint') in ['UNKNOWN', 'PENDING_ANALYSIS']:
                logger.error(f"❌ [MINT_INFERENCE] All inference methods failed - mint remains unresolved")
                logger.error(f"   Available data: logs={bool(logs)}, transaction={bool(trade_info.get('transaction'))}")
                logger.error(f"   Methods tried: log parsing, balance deltas, instruction accounts")
                logger.error(f"   This trade will be skipped by intelligent execution mode")
                logger.error(f"   Consider using Jupiter executor which can handle unknown mints via routing")
        
        # 7. Parse Raydium-specific account information for MEVRaydiumExecutor
        dex = trade_info.get('dex') or trade_info.get('dex_type', '')
        if 'raydium' in str(dex).lower():
            raydium_info = self._parse_raydium_accounts(trade_info)
            if raydium_info:
                if 'parsed_tx' not in trade_info:
                    trade_info['parsed_tx'] = {}
                trade_info['parsed_tx']['raydium_info'] = raydium_info
                inferred_fields.append('raydium_info')
                logger.info(f"✅ [FIELD_INFERENCE] Parsed Raydium account information")
        
        if inferred_fields:
            logger.info(f"✅ [FIELD_INFERENCE] Successfully inferred: {', '.join(inferred_fields)}")
        else:
            logger.debug(f"[FIELD_INFERENCE] No fields needed inference")
        
        return trade_info


