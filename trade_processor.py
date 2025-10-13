import time
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
    
    def __init__(self, target_wallets: List[str], rpc_client=None):
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
            'orca_whirlpool': ['orca'],  # unified orca naming
            'phoenix': ['phoenix'],
            'unknown': ['jupiter', 'raydium']  # Safe defaults
        }
    
    async def validate_trade_info(self, trade_info: Dict[str, Any]) -> bool:
        logger.debug(f"[DEBUG] validate_trade_info called with trade_info: {trade_info}")
        if not trade_info:
            logger.warning("[VALIDATION] trade_info is None or empty.")
            return False

        required_fields = ["signature"]  # logs are nice-to-have, not must-have
        missing = [f for f in required_fields if not trade_info.get(f)]
        if missing:
            logger.warning(f"[VALIDATION] Missing or empty fields in trade_info: {missing}")
            return False

        return True
    
    async def analyze_and_route_trade(self, trade_info: Dict[str, Any], source_wallet: str) -> Dict[str, Any]:
        source_wallet = self._key_str(source_wallet)
        logger.debug(f"[DEBUG] analyze_and_route_trade called with trade_info: {trade_info}, source_wallet: {source_wallet}")
        """
        Analyze trade and return routing instructions (NO EXECUTION)
        
        Returns:
            Dict with routing instructions for the execution coordinator
        """
        try:
            # Extract action from trade info
            action = self._extract_action(trade_info)
            logger.debug(f"[DEBUG] _extract_action result: {action}")
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
            # --- FINAL ACTION RESOLUTION ---
            if (
                (action in (None, 'unknown'))
                and is_valid_solana_address(token_mint)
                and trade_info.get('wallet_address')
                and (trade_info.get('transaction_full') or trade_info.get('transaction'))
            ):
                try:
                    tx_for_action = trade_info.get('transaction_full') or trade_info.get('transaction')
                    action_guess = await self._determine_action_for_wallet(
                        tx_for_action, trade_info['wallet_address'], token_mint
                    )
                    if action_guess and action_guess != 'unknown':
                        action = action_guess
                        trade_info['action'] = action_guess
                        logger.info(f"🎯 FINAL ACTION RESOLVED: {action_guess}")
                except Exception as e:
                    logger.debug(f"[ACTION RESOLUTION] fallback failed: {e}")

            # === MINT/ACTION UNCERTAINTY DEBUGGING ===
            if action == 'unknown' or token_mint in ['UNKNOWN', 'PENDING_ANALYSIS']:
                logger.error(f"Uncertain action or token mint detected: action={action}, token_mint={token_mint}, trade_info={trade_info}")
                logger.error(f"   Signature: {trade_info.get('signature', 'missing')}")
                logger.error(f"   DEX Type: {trade_info.get('dex_type', 'missing')}")
                logger.error(f"   Router Program: {trade_info.get('router_program_id', 'missing')}")
                logger.error(f"   Extracted Info: {trade_info.get('extracted_info', 'missing')}")

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
                    source_ok
                ),
                'forced_execution': False
            }

            logger.info(f"[ROUTING] mint={token_mint[:8] if token_mint != 'UNKNOWN' else 'UNKNOWN'} dex_type={trade_info.get('dex_type')} router={trade_info.get('router_program_id')}")
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

    def _extract_action(self, trade_info: Dict[str, Any]) -> str:
        """
        Extract trade action from trade info - STRICT VERSION
        Only allows 'buy'/'sell'/'swap' if there is actual token balance change
        """
        
        # Log input for debugging
        signature = trade_info.get('signature', 'N/A')
        trade_keys = list(trade_info.keys())
        logger.debug(f"🔍 [ACTION_EXTRACTION] STRICT mode for {signature[:12]}...")
        logger.debug(f"   Available keys: {trade_keys}")
        logger.debug(f"   Basic analysis present: {'basic_analysis' in trade_info}")
        logger.debug(f"   Direct action field: {trade_info.get('action', 'None')}")
        logger.debug(f"   Method: {trade_info.get('method', 'None')}")
        
        # STRICT REQUIREMENT: Check for actual token balance changes first
        has_balance_change = self._has_actual_token_balance_change(trade_info)
        logger.debug(f"🔍 [ACTION_EXTRACTION] Token balance change detected: {has_balance_change}")
        
        # If no token balance change, return 'unknown' regardless of other indicators
        if not has_balance_change:
            logger.warning(f"❌ [ACTION_EXTRACTION] STRICT: No token balance change for {signature[:12]}...")
            logger.warning(f"   Reason: Cannot determine buy/sell/swap without actual token movement")
            logger.debug(f"   Output: 'unknown' (no balance change)")
            return 'unknown'
        
        # PRIORITY 1: Check basic_analysis first (most reliable)
        if 'basic_analysis' in trade_info:
            basic_action = trade_info['basic_analysis'].get('likely_action')
            if basic_action and basic_action != 'unknown':
                # Validate that the action makes sense with balance changes
                if basic_action.lower() in ['buy', 'sell', 'swap']:
                    logger.debug(f"✅ [ACTION_EXTRACTION] STRICT: Using basic_analysis action: {basic_action}")
                    logger.debug(f"   Output: '{basic_action.lower()}' from basic_analysis (validated)")
                    return basic_action.lower()
                else:
                    logger.debug(f"⚠️ [ACTION_EXTRACTION] STRICT: Basic analysis action '{basic_action}' not valid trade action")
            else:
                logger.debug(f"⚠️ [ACTION_EXTRACTION] Basic analysis present but action is '{basic_action}'")
        
        # PRIORITY 2: Try direct action field 
        action = trade_info.get('action')
        if action and action != 'unknown':
            # Skip emergency/ultra-aggressive assumptions
            if trade_info.get('method') == 'ultra_aggressive_assumption':
                logger.warning(f"❌ [ACTION_EXTRACTION] STRICT: Skipping emergency assumption action: {action}")
                logger.debug(f"   Reason: Method is 'ultra_aggressive_assumption' - unreliable")
                action = None
            elif action.lower() in ['buy', 'sell', 'swap']:
                logger.debug(f"✅ [ACTION_EXTRACTION] STRICT: Using direct action field: {action}")
                logger.debug(f"   Output: '{action.lower()}' from direct field (validated)")
                return action.lower()
            else:
                logger.debug(f"⚠️ [ACTION_EXTRACTION] STRICT: Direct action '{action}' not valid trade action")
        
        # PRIORITY 3: Determine action directly from token balance changes
        logger.info(f"🔍 [ACTION_EXTRACTION] STRICT: Analyzing balance changes to determine action for {signature[:12]}...")
        
        # Extract token balance changes to determine buy/sell
        meta = trade_info.get('meta', {})
        pre_balances = meta.get('preTokenBalances', [])
        post_balances = meta.get('postTokenBalances', [])
        
        if pre_balances and post_balances:
            # Build maps for efficient lookup
            pre_map = {}
            post_map = {}
            
            for balance in pre_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                if owner and mint:
                    pre_map[(owner, mint)] = amount
                    
            for balance in post_balances:
                owner = balance.get('owner')
                mint = balance.get('mint')
                amount = int(balance.get('uiTokenAmount', {}).get('amount', '0'))
                if owner and mint:
                    post_map[(owner, mint)] = amount
            
            # Look for any non-SOL token balance changes to determine direction
            token_changes = []
            for (owner, mint) in set(list(pre_map.keys()) + list(post_map.keys())):
                # Skip SOL (native currency) - focus on token changes
                if mint == "So11111111111111111111111111111111111111112":  # SOL mint
                    continue
                    
                pre_amt = pre_map.get((owner, mint), 0)
                post_amt = post_map.get((owner, mint), 0)
                delta = post_amt - pre_amt
                
                if delta != 0:
                    token_changes.append({
                        'owner': owner,
                        'mint': mint,
                        'delta': delta,
                        'action': 'buy' if delta > 0 else 'sell'
                    })
            
            if token_changes:
                # Take the most significant change (largest absolute value)
                primary_change = max(token_changes, key=lambda x: abs(x['delta']))
                detected_action = primary_change['action']
                
                logger.info(f"✅ [ACTION_EXTRACTION] STRICT: Determined action from balance: {detected_action}")
                logger.info(f"   Primary change: {primary_change['owner'][:8]}.../{primary_change['mint'][:8]}... Δ{primary_change['delta']:+,}")
                logger.debug(f"   Total balance changes analyzed: {len(token_changes)}")
                logger.debug(f"   Output: '{detected_action}' (balance-based detection)")
                return detected_action
            else:
                logger.warning(f"⚠️ [ACTION_EXTRACTION] STRICT: Balance changes found but no token changes (only SOL)")
        
        # FALLBACK: If we still can't determine, return 'unknown'
        logger.warning(f"⚠️ [ACTION_EXTRACTION] STRICT: Has balance changes but cannot determine action for {signature[:12]}...")
        logger.warning(f"   Reason: Could not analyze token balance changes effectively")
        logger.warning(f"   Available data: basic_analysis={trade_info.get('basic_analysis', {}).get('likely_action')}, action={trade_info.get('action')}, method={trade_info.get('method')}")
        logger.debug(f"   Output: 'unknown' (analysis failed)")
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
        """Check if wallet is in target list"""
        return wallet_address in self.target_wallets
