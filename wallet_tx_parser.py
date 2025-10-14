# wallet_tx_parser.py

import asyncio
import aiohttp
import traceback
import websockets
import json
import re
import time
import logging
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List, Callable
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Only import what's available to avoid import errors
try:
    from simulate_clone import clone_transaction_from_wallet_a
except ImportError:
    clone_transaction_from_wallet_a = None

# wallet_tx_parser.py
# Transaction parsing, DEX detection, modular per-DEX decoders, robust ALT decoding
# Best-practice upgrade: legacy logic and fallback removed, modular structure added

import json
import logging
from solders.pubkey import Pubkey

# Optional: import Helius SDK or custom decoder modules here
# from helius import decode_transaction, decode_instruction

# Constants for enhanced log parsing
JUPITER_PROGRAM = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
METEORA_AGGREGATOR = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def enhance_from_logs_and_meta(trade: dict) -> dict:
    """
    Enhanced log/meta-based parser for Jupiter/Meteora transactions.
    Fills in dex/action/mint/amount fields from logs and metadata when signatures are not available.
    """
    logs = trade.get("logs") or []
    meta = trade.get("meta") or {}
    log_line = " | ".join(logs)

    # DEX detection
    if JUPITER_PROGRAM in log_line:
        trade["dex"] = "jupiter"
    if METEORA_AGGREGATOR in log_line:
        # If both appear, prefer the aggregator recorded under Jupiter router: we'll still route fine.
        trade.setdefault("dex", "meteora")

    # Action (coarse but robust) - set action for any detected DEX
    if ("Instruction: RouteV2" in log_line or "Instruction: Swap" in log_line or 
        JUPITER_PROGRAM in log_line or METEORA_AGGREGATOR in log_line):
        # We can't always infer buy vs sell without wallet POV; default to 'buy'
        trade.setdefault("action", "buy")

    # Mint inference: choose the *non-USDC* token in postTokenBalances if present
    ptb = (meta.get("postTokenBalances") or []) + (meta.get("preTokenBalances") or [])
    candidate = None
    for b in ptb:
        mint = b.get("mint")
        if mint and mint != USDC_MINT:
            candidate = mint
            break
    if candidate:
        trade["mint"] = candidate

    # Amount default for buys if not present (budgeted buy)
    trade.setdefault("amount", trade.get("budget_sol", 0.001))
    return trade

class ModularDEXDecoder:
    """
    Enhanced Modular DEX decoder registry with comprehensive action detection.
    Flags swap/buy/sell instructions even when balance delta is not detected.
    """
    def __init__(self):
        self.decoders = {}
        self.register_default_decoders()
        
        # Enhanced DEX program mapping for comprehensive detection
        self.dex_programs = {
            # Jupiter
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter",
            
            # Raydium
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium",
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium", 
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium",
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium",
            
            # Pump.fun
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump.fun",
            
            # Orca
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca",
            "SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8": "Orca",
            
            # Meteora
            "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "Meteora",
            "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora",
            
            # Other DEXs
            "ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA": "Alpha",
        }
        
        # Action detection patterns for instruction data and logs
        self.action_patterns = {
            'buy': ['buy', 'purchase', 'acquire', 'in', 'deposit'],
            'sell': ['sell', 'dispose', 'out', 'withdraw'],
            'swap': ['swap', 'exchange', 'route', 'trade', 'convert'],
        }

    def register_default_decoders(self):
        self.decoders["Jupiter"] = self.decode_jupiter
        self.decoders["Raydium"] = self.decode_raydium
        self.decoders["Pump.fun"] = self.decode_pumpfun
        self.decoders["Orca"] = self.decode_orca
        self.decoders["Meteora"] = self.decode_meteora
        self.decoders["Alpha"] = self.decode_alpha
        self.decoders["ALT"] = self.decode_alt

    def decode(self, dex_type, tx_data):
        decoder = self.decoders.get(dex_type, self.decode_unknown)
        result = decoder(tx_data)
        
        # Enhanced: Always attempt action detection regardless of balance data
        action_info = self._detect_action_from_instructions(tx_data, dex_type)
        result.update(action_info)
        
        return result
    
    def _detect_action_from_instructions(self, tx_data, dex_type):
        """
        Enhanced action detection from instruction analysis.
        Works independently of balance delta detection.
        """
        try:
            instructions = tx_data.get("instructions", [])
            logs = tx_data.get("logs", []) or []  # Handle None logs
            meta = tx_data.get("meta", {})
            
            # Add log messages from meta if available
            if meta and "logMessages" in meta and meta["logMessages"]:
                logs.extend(meta["logMessages"])
            
            detected_actions = []
            instruction_details = []
            
            # Analyze each instruction for trade patterns
            for i, instruction in enumerate(instructions):
                program_id = instruction.get("programId")
                if not program_id:
                    continue
                
                # Check if this is a known DEX program
                if program_id in self.dex_programs:
                    dex_name = self.dex_programs[program_id]
                    
                    # Analyze instruction for action patterns
                    action_result = self._analyze_instruction_for_action(instruction, logs, dex_name, i)
                    if action_result:
                        detected_actions.append(action_result)
                        instruction_details.append({
                            'instruction_index': i,
                            'program_id': program_id,
                            'dex_name': dex_name,
                            'action': action_result.get('action'),
                            'confidence': action_result.get('confidence', 0)
                        })
            
            # Determine primary action
            primary_action = 'unknown'
            max_confidence = 0
            
            if detected_actions:
                # Find action with highest confidence
                for action_result in detected_actions:
                    if action_result.get('confidence', 0) > max_confidence:
                        max_confidence = action_result['confidence']
                        primary_action = action_result['action']
            
            return {
                'detected_action': primary_action,
                'action_confidence': max_confidence,
                'instruction_actions': detected_actions,
                'instruction_details': instruction_details,
                'has_trade_instructions': len(detected_actions) > 0
            }
            
        except Exception as e:
            return {
                'detected_action': 'unknown',
                'action_confidence': 0,
                'instruction_actions': [],
                'instruction_details': [],
                'has_trade_instructions': False,
                'error': str(e)
            }
    
    def _analyze_instruction_for_action(self, instruction, logs, dex_name, instruction_index):
        """
        Analyze individual instruction to determine trade action.
        """
        try:
            # Get instruction data and accounts
            data = instruction.get("data", "")
            accounts = instruction.get("accounts", [])
            
            # Look for relevant logs for this instruction
            relevant_logs = [log for log in logs if f"invoke [{instruction_index + 1}]" in log or f"Program {instruction.get('programId')}" in log]
            
            # Combine instruction data and logs for analysis
            analysis_text = f"{data} {' '.join(relevant_logs)}".lower()
            
            # Score each action type
            action_scores = {}
            for action_type, patterns in self.action_patterns.items():
                score = sum(1 for pattern in patterns if pattern in analysis_text)
                if score > 0:
                    action_scores[action_type] = score
            
            # Special handling for different DEXs
            action_scores = self._apply_dex_specific_logic(dex_name, instruction, logs, action_scores)
            
            if not action_scores:
                return None
            
            # Determine best action
            best_action = max(action_scores.items(), key=lambda x: x[1])
            confidence = min(best_action[1] * 0.3, 1.0)  # Scale confidence
            
            return {
                'action': best_action[0],
                'confidence': confidence,
                'method': f'{dex_name}_instruction_analysis',
                'scores': action_scores,
                'relevant_logs': relevant_logs[:3]  # Limit log count
            }
            
        except Exception as e:
            return None
    
    def _apply_dex_specific_logic(self, dex_name, instruction, logs, action_scores):
        """
        Apply DEX-specific logic to improve action detection accuracy.
        """
        log_text = ' '.join(logs).lower()
        
        if dex_name == "Jupiter":
            # Jupiter-specific patterns
            if 'sharedaccountsroute' in log_text:
                action_scores['swap'] = action_scores.get('swap', 0) + 2
            if 'route' in log_text or 'swap' in log_text:
                action_scores['swap'] = action_scores.get('swap', 0) + 1
                
        elif dex_name == "Pump.fun":
            # Pump.fun typically involves buying new tokens
            if 'buy' in log_text or 'purchase' in log_text:
                action_scores['buy'] = action_scores.get('buy', 0) + 2
            else:
                # Default to buy for pump.fun if unclear
                action_scores['buy'] = action_scores.get('buy', 0) + 1
                
        elif dex_name in ["Raydium", "Orca", "Meteora"]:
            # AMM DEXs - look for swap patterns
            if any(pattern in log_text for pattern in ['swap', 'trade', 'exchange']):
                action_scores['swap'] = action_scores.get('swap', 0) + 2
        
        return action_scores

    def decode_jupiter(self, tx_data):
        """Enhanced Jupiter decoder with comprehensive action detection"""
        instructions = tx_data.get("instructions", [])
        accounts = tx_data.get("accounts", [])
        meta = tx_data.get("meta", {})
        logs = tx_data.get("logs", []) or []  # Handle None logs
        if meta and "logMessages" in meta and meta["logMessages"]:
            logs.extend(meta["logMessages"])
        
        swap_info = {}
        action_info = {'action': 'swap', 'confidence': 0}
        
        # Parse Jupiter instructions
        jupiter_instructions_found = 0
        for ix in instructions:
            if ix.get("programId") in ["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4", "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB"]:
                jupiter_instructions_found += 1
                swap_info["in_token"] = ix.get("accounts", [])[0] if ix.get("accounts") else None
                swap_info["out_token"] = ix.get("accounts", [])[1] if len(ix.get("accounts", [])) > 1 else None
                swap_info["amount_in"] = ix.get("data", {}).get("amountIn")
                swap_info["amount_out_min"] = ix.get("data", {}).get("minOut")
        
        # Enhanced action detection
        if jupiter_instructions_found > 0:
            log_text = ' '.join(logs).lower()
            confidence = 0.7  # Base confidence for Jupiter swap
            
            # Boost confidence based on log analysis
            if any(pattern in log_text for pattern in ['sharedaccountsroute', 'route', 'swap']):
                confidence += 0.2
            if 'jupiter' in log_text:
                confidence += 0.1
                
            action_info = {'action': 'swap', 'confidence': min(confidence, 1.0)}
        
        swap_info["user_wallet"] = tx_data.get("signer", None)
        swap_info["fee"] = meta.get("fee", None)
        swap_info.update(action_info)
        
        return {"dex": "Jupiter", "parsed": True, "swap_info": swap_info}

    def decode_raydium(self, tx_data):
        """Enhanced Raydium decoder with comprehensive action detection"""
        instructions = tx_data.get("instructions", [])
        accounts = tx_data.get("accounts", [])
        meta = tx_data.get("meta", {})
        logs = tx_data.get("logs", [])
        if meta and "logMessages" in meta:
            logs.extend(meta["logMessages"])
        
        raydium_info = {}
        action_info = {'action': 'swap', 'confidence': 0}
        
        # Parse Raydium instructions (AMM, CPMM, CLMM)
        raydium_programs = [
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",  # AMM
            "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",  # CPMM
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",  # CLMM
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"   # Legacy
        ]
        
        raydium_instructions_found = 0
        for ix in instructions:
            if ix.get("programId") in raydium_programs:
                raydium_instructions_found += 1
                raydium_info["pool"] = ix.get("accounts", [])[0] if ix.get("accounts") else None
                raydium_info["in_token"] = ix.get("accounts", [])[1] if len(ix.get("accounts", [])) > 1 else None
                raydium_info["out_token"] = ix.get("accounts", [])[2] if len(ix.get("accounts", [])) > 2 else None
                raydium_info["amount_in"] = ix.get("data", {}).get("amountIn")
                raydium_info["amount_out_min"] = ix.get("data", {}).get("minOut")
        
        # Enhanced action detection
        if raydium_instructions_found > 0:
            log_text = ' '.join(logs).lower()
            confidence = 0.6  # Base confidence for Raydium swap
            action = 'swap'
            
            # Analyze logs for specific actions
            if any(pattern in log_text for pattern in ['buy', 'purchase', 'acquire']):
                action = 'buy'
                confidence += 0.2
            elif any(pattern in log_text for pattern in ['sell', 'dispose', 'withdraw']):
                action = 'sell'
                confidence += 0.2
            elif any(pattern in log_text for pattern in ['swap', 'trade', 'exchange']):
                confidence += 0.2
            
            if 'raydium' in log_text:
                confidence += 0.1
                
            action_info = {'action': action, 'confidence': min(confidence, 1.0)}
        
        raydium_info["user_wallet"] = tx_data.get("signer", None)
        raydium_info["fee"] = meta.get("fee", None)
        raydium_info.update(action_info)
        
        return {"dex": "Raydium", "parsed": True, "raydium_info": raydium_info}

    def decode_pumpfun(self, tx_data):
        """Enhanced Pump.fun decoder with comprehensive action detection"""
        instructions = tx_data.get("instructions", [])
        accounts = tx_data.get("accounts", [])
        meta = tx_data.get("meta", {})
        logs = tx_data.get("logs", [])
        if meta and "logMessages" in meta:
            logs.extend(meta["logMessages"])
        
        pumpfun_info = {}
        action_info = {'action': 'buy', 'confidence': 0}  # Default to buy for pump.fun
        
        # Parse Pump.fun instructions
        pumpfun_programs = [
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
        ]
        
        pumpfun_instructions_found = 0
        for ix in instructions:
            if ix.get("programId") in pumpfun_programs:
                pumpfun_instructions_found += 1
                pumpfun_info["token_mint"] = ix.get("accounts", [])[0] if ix.get("accounts") else None
                pumpfun_info["amount_in"] = ix.get("data", {}).get("amountIn")
                pumpfun_info["amount_out_min"] = ix.get("data", {}).get("minOut")
        
        # Enhanced action detection - Pump.fun is typically for buying new tokens
        if pumpfun_instructions_found > 0:
            log_text = ' '.join(logs).lower()
            confidence = 0.8  # High base confidence for pump.fun buy
            action = 'buy'  # Default action
            
            # Analyze logs for specific actions
            if any(pattern in log_text for pattern in ['sell', 'dispose', 'out', 'withdraw']):
                action = 'sell'
                confidence = 0.7  # Lower confidence for sells on pump.fun
            elif any(pattern in log_text for pattern in ['buy', 'purchase', 'acquire', 'in']):
                action = 'buy'
                confidence += 0.1
            
            if 'pump' in log_text or 'pumpfun' in log_text:
                confidence += 0.1
                
            action_info = {'action': action, 'confidence': min(confidence, 1.0)}
        
        pumpfun_info["user_wallet"] = tx_data.get("signer", None)
        pumpfun_info["fee"] = meta.get("fee", None)
        pumpfun_info.update(action_info)
        
        return {"dex": "Pump.fun", "parsed": True, "pumpfun_info": pumpfun_info}

    def decode_orca(self, tx_data):
        """Enhanced Orca decoder with action detection"""
        instructions = tx_data.get("instructions", [])
        meta = tx_data.get("meta", {})
        logs = tx_data.get("logs", [])
        if meta and "logMessages" in meta:
            logs.extend(meta["logMessages"])
        
        orca_info = {}
        action_info = {'action': 'swap', 'confidence': 0}
        
        orca_programs = [
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",  # Whirlpools
            "SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8"   # Legacy Orca
        ]
        
        orca_instructions_found = 0
        for ix in instructions:
            if ix.get("programId") in orca_programs:
                orca_instructions_found += 1
                accounts = ix.get("accounts", [])
                orca_info["pool"] = accounts[0] if accounts else None
                orca_info["in_token"] = accounts[1] if len(accounts) > 1 else None
                orca_info["out_token"] = accounts[2] if len(accounts) > 2 else None
        
        if orca_instructions_found > 0:
            log_text = ' '.join(logs).lower()
            confidence = 0.6
            action = 'swap'
            
            if any(pattern in log_text for pattern in ['swap', 'whirlpool']):
                confidence += 0.2
            if 'orca' in log_text:
                confidence += 0.1
                
            action_info = {'action': action, 'confidence': min(confidence, 1.0)}
        
        orca_info["user_wallet"] = tx_data.get("signer", None)
        orca_info.update(action_info)
        
        return {"dex": "Orca", "parsed": True, "orca_info": orca_info}
    
    def decode_meteora(self, tx_data):
        """Enhanced Meteora decoder with action detection"""
        instructions = tx_data.get("instructions", [])
        meta = tx_data.get("meta", {})
        logs = tx_data.get("logs", [])
        if meta and "logMessages" in meta:
            logs.extend(meta["logMessages"])
        
        meteora_info = {}
        action_info = {'action': 'swap', 'confidence': 0}
        
        meteora_programs = [
            "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN",
            "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"
        ]
        
        meteora_instructions_found = 0
        for ix in instructions:
            if ix.get("programId") in meteora_programs:
                meteora_instructions_found += 1
                accounts = ix.get("accounts", [])
                meteora_info["pool"] = accounts[0] if accounts else None
        
        if meteora_instructions_found > 0:
            log_text = ' '.join(logs).lower()
            confidence = 0.6
            
            if any(pattern in log_text for pattern in ['swap', 'meteora']):
                confidence += 0.2
                
            action_info = {'action': 'swap', 'confidence': min(confidence, 1.0)}
        
        meteora_info["user_wallet"] = tx_data.get("signer", None)
        meteora_info.update(action_info)
        
        return {"dex": "Meteora", "parsed": True, "meteora_info": meteora_info}
    
    def decode_alpha(self, tx_data):
        """Enhanced Alpha DEX decoder with action detection"""
        instructions = tx_data.get("instructions", [])
        meta = tx_data.get("meta", {})
        logs = tx_data.get("logs", [])
        if meta and "logMessages" in meta:
            logs.extend(meta["logMessages"])
        
        alpha_info = {}
        action_info = {'action': 'swap', 'confidence': 0}
        
        alpha_instructions_found = 0
        for ix in instructions:
            if ix.get("programId") == "ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA":
                alpha_instructions_found += 1
                accounts = ix.get("accounts", [])
                alpha_info["pool"] = accounts[0] if accounts else None
        
        if alpha_instructions_found > 0:
            confidence = 0.6
            action_info = {'action': 'swap', 'confidence': confidence}
        
        alpha_info["user_wallet"] = tx_data.get("signer", None)
        alpha_info.update(action_info)
        
        return {"dex": "Alpha", "parsed": True, "alpha_info": alpha_info}

    def decode_alt(self, tx_data):
        """ALT decoder: extract address lookup table usage and resolved accounts"""
        alt_info = {}
        alt_info["lookup_tables"] = tx_data.get("addressTableLookups", [])
        alt_info["resolved_accounts"] = tx_data.get("resolvedAccounts", [])
        alt_info["user_wallet"] = tx_data.get("signer", None)
        alt_info["action"] = "alt_usage"
        alt_info["confidence"] = 0.5
        return {"dex": "ALT", "parsed": True, "alt_info": alt_info}

    def decode_unknown(self, tx_data):
        """Fallback for unknown DEXs with basic action attempt"""
        unknown_info = {
            "user_wallet": tx_data.get("signer", None),
            "action": "unknown",
            "confidence": 0
        }
        
        # Try to detect any trading patterns in logs
        logs = tx_data.get("logs", [])
        meta = tx_data.get("meta", {})
        if meta and "logMessages" in meta:
            logs.extend(meta["logMessages"])
        
        if logs:
            log_text = ' '.join(logs).lower()
            if any(pattern in log_text for pattern in ['swap', 'trade', 'buy', 'sell']):
                unknown_info["action"] = "possible_trade"
                unknown_info["confidence"] = 0.3
        
        return {"dex": "Unknown", "parsed": False, "unknown_info": unknown_info}


def parse_from_logs_and_meta(trade):
    """
    Enhanced log parsing to extract Pump.fun and other DEX details from logs and metadata
    when signatures are not available. Now includes Jupiter/Meteora enhancement.
    """
    # FIRST: Apply the new Jupiter/Meteora enhancer
    trade = enhance_from_logs_and_meta(trade)
    
    logs = trade.get("logs") or []
    meta = trade.get("meta") or {}
    
    # Extend logs with meta logMessages if available
    if meta and "logMessages" in meta and meta["logMessages"]:
        logs.extend(meta["logMessages"])

    # 1) Detect Pump.fun (only if not already detected by enhancer)
    if not trade.get("dex"):
        is_pumpfun = any("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW" in str(s) for s in logs)
        if is_pumpfun:
            trade["dex"] = "pumpfun"
            trade["dex_type"] = "pumpfun"

    # 2) Action detection from logs (only if not already set by enhancer)
    if not trade.get("action"):
        for log in logs:
            log_str = str(log)
            if "Instruction: PumpBuy" in log_str:
                trade["action"] = "buy"
                break
            elif "Instruction: PumpSell" in log_str:
                trade["action"] = "sell"
                break
            elif "buy" in log_str.lower() and ("pump" in log_str.lower() or "swap" in log_str.lower()):
                trade["action"] = "buy"
            elif "sell" in log_str.lower() and ("pump" in log_str.lower() or "swap" in log_str.lower()):
                trade["action"] = "sell"

    # 3) Mint extraction (only if not already set by enhancer)
    if not trade.get("mint"):
        ptb = meta.get("postTokenBalances") or []
        if ptb and len(ptb) > 0 and "mint" in ptb[0]:
            trade["mint"] = ptb[0]["mint"]
            trade["token_mint"] = ptb[0]["mint"]
        else:
            # Try to extract mint from logs (look for token addresses)
            for log in logs:
                log_str = str(log)
                # Look for mint addresses (typical Solana token format)
                if "pump" in log_str and len([word for word in log_str.split() if len(word) > 40]) > 0:
                    # Find potential token addresses in the log
                    words = log_str.split()
                    for word in words:
                        if len(word) > 40 and word.isalnum():  # Likely a Solana address
                            trade["mint"] = word
                            trade["token_mint"] = word
                            break

    # 4) Amount estimation (only if not already set by enhancer)
    if not trade.get("amount"):
        # If it's a sell: try to derive from token balance changes
        if trade.get("action") == "sell":
            pre_balances = meta.get("preTokenBalances") or []
            post_balances = meta.get("postTokenBalances") or []
            if pre_balances and post_balances:
                # Calculate token amount difference
                for pre, post in zip(pre_balances, post_balances):
                    if pre.get("mint") == post.get("mint"):
                        pre_amount = float(pre.get("uiTokenAmount", {}).get("uiAmount") or 0)
                        post_amount = float(post.get("uiTokenAmount", {}).get("uiAmount") or 0)
                        if pre_amount > post_amount:  # Tokens decreased (sell)
                            trade["amount"] = pre_amount - post_amount
                            break
        
        # If it's a buy: use configured budget if no amount specified
        if trade.get("action") == "buy" and trade.get("amount") is None:
            trade["amount"] = trade.get("budget_sol", 0.001)  # Default buy amount

    return trade

class WalletTransactionParser:
    def __init__(self, rpc_client):
        self.rpc_client = rpc_client
        self.dex_decoder = ModularDEXDecoder()
        self.logger = logging.getLogger(__name__)

    def parse_transaction(self, tx_data):
        """
        Main entrypoint for transaction parsing. Always returns standardized format.
        Ensures consistent output structure with required fields.
        """
        # Import normalize_dex function
        try:
            from execution_coordinator import normalize_dex
        except ImportError:
            # Fallback if import fails
            def normalize_dex(label: str) -> str:
                if not label:
                    return "unknown"
                return label.lower()
        
        # EARLY METEORA DETECTION: Check all instructions for Meteora program ID
        instructions = tx_data.get("instructions", [])
        meteora_program_id = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"
        early_meteora_detected = False
        
        for ix in instructions:
            pid = ix.get("programId") or ix.get("program")
            if pid == meteora_program_id:
                early_meteora_detected = True
                self.logger.info(f"✅ [PARSER] Early Meteora detection: programId={meteora_program_id[:8]}...")
                break
        
        # Get original decoder result
        dex_type = self.identify_dex(tx_data)
        decoder_result = self.dex_decoder.decode(dex_type, tx_data)
        
        # Extract standardized information
        signature = tx_data.get("signature", None)
        
        # Extract DEX from decoder result
        dex_raw = decoder_result.get("dex", dex_type)
        # Ensure proper normalization (handle case-insensitive matching)
        if dex_raw:
            dex = normalize_dex(dex_raw.lower().replace(".", ""))
        else:
            dex = "unknown"
        
        # Apply early Meteora detection override
        if early_meteora_detected:
            dex = "meteora"
            self.logger.info(f"✅ [PARSER] Applied early Meteora detection override: dex=meteora")
        
        # Extract action from decoder result
        action = "unknown"
        mint = None
        amount = None
        source_wallet = None
        
        # Get action and other info from the decoder result based on DEX type
        if dex == "jupiter":
            swap_info = decoder_result.get("swap_info", {})
            action = swap_info.get("action", "swap")
            mint = swap_info.get("out_token")  # For swaps, we care about the output token
            amount = swap_info.get("amount_in")
            source_wallet = swap_info.get("user_wallet")
            
        elif dex == "raydium":
            raydium_info = decoder_result.get("raydium_info", {})
            action = raydium_info.get("action", "swap")
            mint = raydium_info.get("out_token") or raydium_info.get("in_token")
            amount = raydium_info.get("amount_in")
            source_wallet = raydium_info.get("user_wallet")
            
        elif dex == "pumpfun":
            pumpfun_info = decoder_result.get("pumpfun_info", {})
            action = pumpfun_info.get("action", "buy")
            mint = pumpfun_info.get("token_mint")
            amount = pumpfun_info.get("amount_in")
            source_wallet = pumpfun_info.get("user_wallet")
            
        elif dex == "meteora":
            meteora_info = decoder_result.get("meteora_info", {})
            action = meteora_info.get("action", "swap")
            source_wallet = meteora_info.get("user_wallet")
            
        elif dex == "orca":
            orca_info = decoder_result.get("orca_info", {})
            action = orca_info.get("action", "swap")
            source_wallet = orca_info.get("user_wallet")
            
        else:
            # Unknown DEX - try to extract from unknown_info
            unknown_info = decoder_result.get("unknown_info", {})
            action = unknown_info.get("action", "unknown")
            source_wallet = unknown_info.get("user_wallet")
        
        # Fallback: try to extract from general decoder result
        if action == "unknown":
            action = decoder_result.get("detected_action", "unknown")
        if not source_wallet:
            source_wallet = tx_data.get("signer")
        
        # Apply early Meteora action override if action is still unknown
        if early_meteora_detected and action in (None, "unknown"):
            action = "swap"
            self.logger.info(f"✅ [PARSER] Applied early Meteora action override: action=swap")
        
        # Enhanced log parsing when regular parsing fails or returns unknown
        if dex == "unknown" or action == "unknown" or mint is None:
            self.logger.debug(f"[PARSER] Regular parsing incomplete - trying log/meta analysis...")
            
            # Create a trade dict with current parsed data and tx_data
            trade_for_enhancement = {
                "dex": dex,
                "dex_type": dex,
                "action": action,
                "mint": mint,
                "token_mint": mint,
                "amount": amount,
                "signature": signature,
                "source_wallet": source_wallet,
                "logs": tx_data.get("logs", []),
                "meta": tx_data.get("meta", {}),
                "budget_sol": 0.001  # Default budget for buys
            }
            
            # Apply log parsing enhancement
            enhanced_trade = parse_from_logs_and_meta(trade_for_enhancement)
            
            # Update our values if the enhancement found better data
            if enhanced_trade.get("dex") != dex and enhanced_trade.get("dex") != "unknown":
                dex = enhanced_trade.get("dex")
                self.logger.info(f"[PARSER] ✅ Enhanced DEX detection: {dex}")
            
            if enhanced_trade.get("action") != action and enhanced_trade.get("action") != "unknown":
                action = enhanced_trade.get("action")
                self.logger.info(f"[PARSER] ✅ Enhanced action detection: {action}")
            
            if enhanced_trade.get("mint") != mint and enhanced_trade.get("mint") is not None:
                mint = enhanced_trade.get("mint")
                self.logger.info(f"[PARSER] ✅ Enhanced mint detection: {mint[:8]}...")
            
            if enhanced_trade.get("amount") != amount and enhanced_trade.get("amount") is not None:
                amount = enhanced_trade.get("amount")
                self.logger.info(f"[PARSER] ✅ Enhanced amount detection: {amount}")

        # Log when DEX is still unknown after enhancement
        if dex == "unknown":
            self.logger.warning(f"[PARSER] DEX=unknown after enhancement; proceeding with fallback route. mint={mint} action={action} amount={amount}")
        
        # Return standardized format
        return {
            "dex": dex,
            "action": action,
            "mint": mint,
            "amount": amount,
            "signature": signature,
            "source_wallet": source_wallet,
            # Include original decoder result for compatibility
            "original_result": decoder_result
        }

    def identify_dex(self, tx_data):
        """
        Identify DEX type from transaction data. Checks program IDs in instructions.
        """
        instructions = tx_data.get("instructions", [])
        for ix in instructions:
            program_id = ix.get("programId")
            if program_id == "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4":
                return "Jupiter"
            if program_id in ["675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"]:
                return "Raydium"
            if program_id in ["6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P", "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"]:
                return "Pump.fun"
        # ALT detection: check for addressTableLookups
        if tx_data.get("addressTableLookups"):
            return "ALT"
        return "Unknown"


# WebSocket configuration
HELIUS_WS_URL = "wss://atlas-mainnet.helius-rpc.com/?api-key=YOUR_API_KEY"  # Fallback, replaced by env_keys


class WebSocketWalletMonitor:
    """Real-time WebSocket-based wallet monitoring for meme coin buy/sell detection"""
    def __init__(self, target_wallets: List[str], ws_url: str = None):
        self.target_wallets = target_wallets
        # Use env_keys configuration if available
        if ws_url is None:
            try:
                from env_keys import kz
                self.ws_url = kz.HELIUS_Standard_Websocket_URL
                log_debug(f"🔗 Using WebSocket URL from env_keys: {self.ws_url}")
            except Exception as e:
                self.ws_url = HELIUS_WS_URL
                log_debug(f"⚠️ Fallback to default WebSocket URL: {e}")
        else:
            self.ws_url = ws_url
        self.subscription_ids = {}
        self.websockets = {}  # Store separate connections for each wallet
        self.is_running = False
        self.trade_callback = None
    def _get_http_rpc_url(self) -> str:
        """Convert WebSocket URL to HTTP RPC URL"""
        try:
            from env_keys import kz
            return kz.HELIUS_RPC_URL
        except:
            # Fallback: convert WebSocket URL to HTTP RPC URL
            return self.ws_url.replace('wss://rpc.helius.xyz/', 'https://mainnet.helius-rpc.com/v0')
    def set_trade_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback function to handle detected trades"""
        self.trade_callback = callback
        
    async def start_monitoring(self):
        """🚀 OFFICIAL: Start WebSocket monitoring with separate connections per wallet"""
        print("🚀 Starting OFFICIAL WebSocket monitoring...")
        print(f"🎯 Target wallets: {len(self.target_wallets)}")
        
        self.is_running = True
        
        # Create separate connection for each wallet (official limitation)
        tasks = []
        for i, wallet in enumerate(self.target_wallets):
            print(f"📡 [{i+1}/{len(self.target_wallets)}] Setting up connection for: {wallet[:8]}...")
            task = asyncio.create_task(
                self._monitor_wallet(wallet, i),
                name=f"wallet_monitor_{i}"
            )
            tasks.append(task)
        
        try:
            # Run all wallet monitoring tasks concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"❌ Error in monitoring: {e}")
        finally:
            self.is_running = False

    async def _monitor_wallet(self, wallet_address: str, connection_id: int):
        """Monitor a single wallet with official WebSocket best practices"""
        retry_count = 0
        max_retries = 10
        
        while self.is_running and retry_count < max_retries:
            try:
                log_debug(f"� [{connection_id}] Connecting to monitor: {wallet_address[:8]}... (attempt {retry_count + 1})")
                
                # Official WebSocket connection with recommended settings
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=30,   # Official: Send ping every 30 seconds  
                    ping_timeout=10,    # Official: Wait 10 seconds for pong
                    close_timeout=10,   # Official: 10 second close timeout
                    max_size=10**7,     # Official: Large message buffer
                    compression=None    # Official: Disable compression for speed
                ) as websocket:
                    log_debug(f"✅ [{connection_id}] Connected successfully for {wallet_address[:8]}...")
                    
                    # Store websocket reference
                    self.websockets[connection_id] = websocket
                    
                    # Official subscription method - only ONE wallet per subscription
                    subscription_success = await self._subscribe_to_wallet_logs_new(websocket, wallet_address, connection_id)
                    
                    if subscription_success:
                        # Listen for messages with proper error handling
                        await self._listen_for_messages_new(websocket, wallet_address, connection_id)
                    else:
                        log_debug(f"❌ [{connection_id}] Failed to subscribe to {wallet_address[:8]}...")
                    
            except websockets.exceptions.ConnectionClosed as e:
                retry_count += 1
                log_debug(f"⚠️ [{connection_id}] Connection closed for {wallet_address[:8]}...: {e}")
                
                if retry_count < max_retries:
                    # Official exponential backoff strategy
                    backoff_time = min(2 ** retry_count, 30)  # Cap at 30 seconds
                    log_debug(f"🔄 [{connection_id}] Reconnecting in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    log_debug(f"❌ [{connection_id}] Max retries reached for {wallet_address[:8]}...")
                    
            except Exception as e:
                retry_count += 1
                log_debug(f"❌ [{connection_id}] Error monitoring {wallet_address[:8]}...: {e}")
                
                if retry_count < max_retries:
                    backoff_time = min(2 ** retry_count, 30)
                    log_debug(f"� [{connection_id}] Retrying in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)

    async def _subscribe_to_wallet_logs_new(self, websocket, wallet_address: str, connection_id: int):
        """Subscribe to wallet logs using official logsSubscribe method"""
        
        # OFFICIAL METHOD: logsSubscribe with mentions filter
        # Note: mentions only supports ONE wallet per subscription
        subscribe_message = {
            "jsonrpc": "2.0",
            "id": connection_id + 1,
            "method": "logsSubscribe",
            "params": [
                {
                    "mentions": [wallet_address]  # Official: Only one wallet per subscription
                },
                {
                    "commitment": "processed"  # Official: fastest confirmation for trading
                }
            ]
        }
        
        log_debug(f"📤 [{connection_id}] Sending subscription for {wallet_address[:8]}...")
        await websocket.send(json.dumps(subscribe_message))
        
        # Wait for subscription confirmation
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            response_data = json.loads(response)
            
            if "result" in response_data:
                subscription_id = response_data["result"]
                self.subscription_ids[connection_id] = {
                    'subscription_id': subscription_id,
                    'wallet_address': wallet_address
                }
                log_debug(f"✅ [{connection_id}] Subscribed to {wallet_address[:8]}... (ID: {subscription_id})")
                return True
            else:
                log_debug(f"❌ [{connection_id}] Subscription failed: {response_data}")
                return False
                
        except asyncio.TimeoutError:
            log_debug(f"❌ [{connection_id}] Subscription timeout for {wallet_address[:8]}...")
            return False

    async def _listen_for_messages_new(self, websocket, wallet_address: str, connection_id: int):
        """Listen for transaction messages with official parsing"""
        log_debug(f"👂 [{connection_id}] Listening for transactions from {wallet_address[:8]}...")
        
        while self.is_running:
            try:
                # Official: Wait for WebSocket messages
                message = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                message_data = json.loads(message)
                
                # Official: Check if it's a transaction notification
                if message_data.get("method") == "logsNotification":
                    await self._process_transaction_notification_new(message_data, wallet_address, connection_id)
                    
                # Official: Handle ping/pong for keepalive
                elif message_data.get("method") == "ping":
                    await websocket.send(json.dumps({"jsonrpc": "2.0", "method": "pong"}))
                    
            except asyncio.TimeoutError:
                # Official: Send ping to keep connection alive
                log_debug(f"💓 [{connection_id}] Sending keepalive ping...")
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0", 
                    "method": "ping",
                    "id": int(time.time())
                }))
                
            except websockets.exceptions.ConnectionClosed:
                log_debug(f"📡 [{connection_id}] Connection closed for {wallet_address[:8]}...")
                break
                
            except Exception as e:
                log_debug(f"❌ [{connection_id}] Error processing message: {e}")

    async def _process_transaction_notification_new(self, message_data: Dict[str, Any], wallet_address: str, connection_id: int):
        """Process transaction notifications using official format"""
        try:
            params = message_data.get("params", {})
            result = params.get("result", {})
            value = result.get("value", {})  # ✅ FIXED: The data is in the "value" field
            
            signature = value.get("signature", "Unknown")
            logs = value.get("logs", [])
            err = value.get("err")
            
            # Official: Check if transaction succeeded
            if err is None:
                log_debug(f"🎯 [{connection_id}] NEW TRANSACTION from {wallet_address[:8]}...")
                log_debug(f"   📝 Signature: {signature[:12] if signature else 'None'}...")
                log_debug(f"   📊 Log lines: {len(logs)}")
                
                # Analyze logs for trading activity using integrated balance-based detection
                await self._analyze_transaction_logs(signature, logs, wallet_address)
                
            else:
                log_debug(f"❌ [{connection_id}] Failed transaction from {wallet_address[:8]}...: {err}")
                
        except Exception as e:
            log_debug(f"❌ Error processing notification: {e}")

    # OLD FLAWED DETECTION METHOD REMOVED: _analyze_transaction_logs_enhanced

    # OLD FLAWED METHOD REMOVED: _extract_token_from_logs

    async def _stable_message_loop(self, websocket):
        """🚀 STABLE: Message processing loop with proper error handling"""
        last_ping = asyncio.get_event_loop().time()
        ping_interval = 30  # Send manual ping every 30 seconds
        
        try:
            while self.is_running:
                try:
                    # 🚀 STABLE: Use shorter timeout for responsiveness
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    await self._process_websocket_message(json.loads(message))
                    
                except asyncio.TimeoutError:
                    # Timeout is normal, check if we need to ping
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_ping > ping_interval:
                        try:
                            await websocket.ping()
                            last_ping = current_time
                            log_debug("💓 Manual WebSocket ping sent")
                        except Exception as ping_error:
                            log_debug(f"❌ Ping failed: {ping_error}")
                            break  # Exit to trigger reconnection
                    continue
                    
                except websockets.exceptions.ConnectionClosed:
                    log_debug("❌ WebSocket connection closed during message loop")
                    break  # Exit to trigger reconnection
                    
                except json.JSONDecodeError as e:
                    log_debug(f"⚠️ Invalid JSON received: {e}")
                    continue  # Skip invalid messages
                    
                except Exception as e:
                    log_debug(f"❌ Message processing error: {e}")
                    continue  # Continue processing other messages
                    
        except Exception as e:
            log_debug(f"❌ Stable message loop error: {e}")
            traceback.print_exc()
            
    async def _subscribe_to_wallet_logs(self, websocket, wallet_address: str, subscription_id: int):
        """Subscribe to logs for a specific wallet using official logsSubscribe method"""
        
        # OFFICIAL SOLANA LOGSSUBSCRIBE FORMAT - Updated for copy trading speed
        subscribe_message = {
            "jsonrpc": "2.0",
            "id": subscription_id,
            "method": "logsSubscribe",
            "params": [
                {
                    "mentions": [wallet_address]  # Only ONE wallet per subscription (per docs)
                },
                {
                    "commitment": "processed"  # Use processed for fastest meme coin trading
                }
            ]
        }
        
        await websocket.send(json.dumps(subscribe_message))
        self.subscription_ids[subscription_id] = wallet_address
        log_debug(f"📡 Subscribed to wallet logs: {wallet_address[:8]}...{wallet_address[-8:]}")
        
    async def _subscribe_to_wallet_account(self, websocket, wallet_address: str, subscription_id: int):
        """Subscribe to account changes for a specific wallet using official accountSubscribe method"""
        
        # OFFICIAL SOLANA ACCOUNTSUBSCRIBE FORMAT - Updated for copy trading speed
        subscribe_message = {
            "jsonrpc": "2.0",
            "id": subscription_id,
            "method": "accountSubscribe",
            "params": [
                wallet_address,  # Account pubkey
                {
                    "encoding": "jsonParsed",
                    "commitment": "processed"  # Use processed for fastest meme coin trading
                }
            ]
        }
        
        await websocket.send(json.dumps(subscribe_message))
        self.subscription_ids[subscription_id] = f"account_{wallet_address}"
        log_debug(f"📡 Subscribed to wallet account: {wallet_address[:8]}...{wallet_address[-8:]}")
        
    async def _process_websocket_message(self, message: dict):
        """Process incoming WebSocket messages for trade detection"""
        try:
            method = message.get('method', 'unknown')
            # Handle subscription confirmations and capture REAL subscription IDs
            if "result" in message and "id" in message:
                request_id = message['id']
                real_subscription_id = message['result']
                original_mapping = self.subscription_ids.get(request_id)
                if original_mapping:
                    self.subscription_ids[real_subscription_id] = original_mapping
                    log_debug(f"✅ Subscription confirmed:")
                    log_debug(f"   Request ID: {request_id} -> Real Subscription ID: {real_subscription_id}")
                    log_debug(f"   Mapped to: {original_mapping}")
                else:
                    log_debug(f"✅ Subscription confirmed for ID: {request_id} -> {real_subscription_id}")
                return
            # Handle log notifications - OFFICIAL FORMAT
            if message.get("method") == "logsNotification":
                params = message.get("params", {})
                result = params.get("result", {})
                value = result.get("value", {})
                error = value.get("err")
                signature = value.get("signature")  
                logs = value.get("logs", [])
                if not error:
                    log_debug(f"🔔 LogsNotification received!")
                    log_debug(f"   Subscription: {params.get('subscription')}")
                    log_debug(f"   Signature: {signature[:8] if signature else 'None'}...")
                    log_debug(f"   Log count: {len(logs)}")
                    log_debug(f"   Error: None")
                else:
                    if 'DEBUG' in globals() and DEBUG and signature:
                        print(f"🔍 ❌ Transaction failed: {signature[:8]}... Error: {error}")
                if signature and logs and not error:
                    subscription_id = params.get("subscription")
                    wallet_address = self.subscription_ids.get(subscription_id)
                    log_debug(f"🔍 SUBSCRIPTION DEBUG:")
                    log_debug(f"   Subscription ID from message: {subscription_id}")
                    log_debug(f"   Wallet address found: {wallet_address}")
                    log_debug(f"   All subscription IDs: {list(self.subscription_ids.keys())}")
                    if wallet_address and not wallet_address.startswith("account_"):
                        log_debug(f"✅ Calling _analyze_transaction_logs for {wallet_address[:8]}...")
                        await self._analyze_transaction_logs(signature, logs, wallet_address)
                    else:
                        log_debug(f"❌ CRITICAL: Cannot find wallet for subscription {subscription_id}")
                        log_debug(f"   Available subscriptions: {self.subscription_ids}")
                        log_debug(f"   This is why trades aren't being processed!")
                        # PATCH: Fallback to recent transaction fetch for all target wallets
                        log_debug(f"   PATCH: Attempting fallback to recent transaction fetch for all target wallets!")
                        for fallback_wallet in self.target_wallets:
                            log_debug(f"   Fallback: Trying {fallback_wallet[:8]}...")
                            try:
                                await self._analyze_transaction_logs(signature, logs, fallback_wallet)
                            except Exception as fallback_e:
                                log_debug(f"   Fallback failed for {fallback_wallet[:8]}: {fallback_e}")
                elif not signature:
                    log_debug(f"❌ No signature in logsNotification! Skipping event.")
                elif not logs:
                    log_debug(f"❌ No logs in logsNotification! Skipping event.")
                elif error:
                    log_debug(f"❌ Error in logsNotification! Skipping event.")
                return
            # Handle account notifications - OFFICIAL FORMAT  
            elif message.get("method") == "accountNotification":
                params = message.get("params", {})
                result = params.get("result", {})
                value = result.get("value", {})
                log_debug(f"🔔 AccountNotification received!")
                log_debug(f"   Subscription: {params.get('subscription')}")
                log_debug(f"   Has lamports: {bool(value.get('lamports'))}")
                subscription_id = params.get("subscription")
                account_info = self.subscription_ids.get(subscription_id)
                if account_info and account_info.startswith("account_"):
                    wallet_address = account_info.replace("account_", "")
                    log_debug(f"🎯 Account change detected for {wallet_address[:8]}... - fetching recent transactions")
                    # PATCH: Attempt to fetch recent transactions for this wallet as fallback
                    try:
                        await self._fetch_and_analyze_recent_transactions(wallet_address)
                    except Exception as fetch_e:
                        log_debug(f"   Fallback fetch failed for {wallet_address[:8]}: {fetch_e}")
                else:
                    log_debug(f"❌ Could not map accountNotification to wallet address for subscription {subscription_id}")
            # ...existing code...
        except Exception as e:
            log_debug(f"❌ Error processing WebSocket message: {e}")
            traceback.print_exc()

    async def _fetch_and_analyze_recent_transactions(self, wallet_address: str, max_transactions: int = 5):
        """Fetch recent transactions for a wallet and analyze them as a fallback if mapping fails"""
        try:
            from solders.pubkey import Pubkey
            if not hasattr(self, 'rpc_client') or not self.rpc_client:
                log_debug(f"❌ No RPC client available for fallback fetch!")
                return
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(wallet_address),
                limit=max_transactions
            )
            if not response.value:
                log_debug(f"❌ No recent transactions found for {wallet_address[:8]}...")
                return
            for tx_info in response.value:
                signature = str(tx_info.signature)
                if hasattr(self, 'processed_signatures') and signature in self.processed_signatures:
                    continue
                log_debug(f"🆕 Fallback processing missed transaction: {signature[:8]}...")
                # Attempt to fetch logs for this transaction (if possible)
                # This is a placeholder: you may need to implement log fetching if not available
                # For now, just call analyze with empty logs
                await self._analyze_transaction_logs(signature, [], wallet_address)
        except Exception as e:
            log_debug(f"❌ Error in fallback fetch for {wallet_address[:8]}: {e}")
            
    async def _analyze_transaction_logs(self, signature: str, logs: List[str], wallet_address: str):
        """
        Analyze transaction logs to detect trade activities with STRICT balance change requirement.
        
        Execution ONLY occurs when:
        1. Token balance changes are detected for monitored wallets, AND
        2. Transaction involves monitored wallet (validated)
        
        Balance changes are REQUIRED - no synthetic trades or zero-delta execution.
        """
        try:
            log_debug(f"🔍 ANALYSIS: {signature[:8]}... from {wallet_address[:8]}...")
            log_debug(f"   📊 Total logs: {len(logs)}")
            
            # Show first few logs for debugging
            for i, log in enumerate(logs[:5]):
                log_debug(f"   Log {i}: {log}")

            # PRIMARY: Try balance analysis (REQUIRED for execution)
            log_debug(f"🔧 Running balance analysis (REQUIRED for execution)...")
            trade_info = await self._analyze_with_official_balance_method(signature, wallet_address, logs)
            
            if trade_info:
                log_debug(f"✅ Balance analysis SUCCESS! Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
                log_debug(f"🚨 TRADE DETECTED! Calling main bot callback...")
                log_debug(f"   💎 Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
                log_debug(f"   🏪 DEX: {trade_info.get('dex', 'Unknown')}")
                log_debug(f"   🎬 Action: {trade_info['action'].upper()}")
                log_debug(f"   📝 Signature: {signature[:12]}...")
                
                # Call the callback if set
                if self.trade_callback:
                    log_debug(f"📡 Calling trade_callback now...")
                    await self.trade_callback(trade_info)
                    log_debug(f"✅ Trade callback completed successfully!")
                else:
                    log_debug(f"❌ ERROR: No trade_callback set!")
            else:
                log_debug(f"⚠️ NO TRADE DETECTED - No balance changes for monitored wallets")
                log_debug(f"   🔍 Balance changes are REQUIRED for trade detection")
                log_debug(f"   📋 No execution will occur without balance changes")
                    
        except Exception as e:
            log_debug(f"❌ ERROR in _analyze_transaction_logs: {e}")
            import traceback
            log_debug(f"   Full traceback: {traceback.format_exc()}")

    async def _analyze_with_official_balance_method(self, signature: str, wallet_address: str, logs: List[str]) -> Optional[Dict[str, Any]]:
        """
        Balance-based trade detection - REQUIRED for execution.
        Uses actual balance changes to determine buy/sell/swap actions and token info.
        NO execution without balance changes.
        
        This method analyzes token balance changes to detect trades.
        Returns None if no balance changes are detected, which prevents execution.
        Balance changes are the PRIMARY requirement for trade detection and execution.
        """
        
        log_debug(f"🎯 BALANCE-BASED ANALYSIS for {signature[:12]}...")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",
                    "commitment": "confirmed",  # 🚀 RPC requirement - but we'll use log fallback for speed
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(self._get_http_rpc_url(), json=payload) as response:
                    data = await response.json()
                    
                    if 'error' in data:
                        log_debug(f"   ❌ RPC Error: {data['error']}")
                        # Balance analysis failed - return None (no execution without balance changes)
                        log_debug(f"   ⚠️ Cannot proceed without balance data - skipping")
                        return None
                    
                    result = data.get('result')
                    if not result:
                        log_debug(f"   ❌ No transaction data")
                        # Balance analysis failed - return None (no execution without balance changes)
                        log_debug(f"   ⚠️ Cannot proceed without transaction data - skipping")
                        return None
                    
                    meta = result.get('meta', {})
                    transaction = result.get('transaction', {})
                    
                    # Check transaction success
                    if meta.get('err'):
                        log_debug(f"   ❌ Transaction failed: {meta.get('err')}")
                        return None
                    
                    # Find wallet index in account keys
                    message = transaction.get('message', {})
                    account_keys = message.get('accountKeys', [])
                    
                    wallet_index = None
                    for i, account in enumerate(account_keys):
                        if account == wallet_address:
                            wallet_index = i
                            break
                    
                    if wallet_index is None:
                        log_debug(f"   ❌ Target wallet not found in transaction")
                        return None
                    
                    # Analyze SOL balance changes
                    pre_balances = meta.get('preBalances', [])
                    post_balances = meta.get('postBalances', [])
                    
                    if wallet_index >= len(pre_balances) or wallet_index >= len(post_balances):
                        log_debug(f"   ❌ Balance data incomplete")
                        return None
                    
                    sol_delta = (post_balances[wallet_index] - pre_balances[wallet_index]) / 1e9  # Convert to SOL
                    
                    # Analyze token balance changes
                    pre_token_balances = meta.get('preTokenBalances', [])
                    post_token_balances = meta.get('postTokenBalances', [])
                    
                    # Track token changes for our wallet
                    token_changes = {}
                    
                    # Process pre-transaction token balances
                    for balance in pre_token_balances:
                        if balance.get('owner') == wallet_address:
                            mint = balance.get('mint')
                            ui_amount = balance.get('uiTokenAmount', {})
                            amount = float(ui_amount.get('uiAmount', 0) or 0)
                            token_changes[mint] = {
                                'pre': amount,
                                'post': 0,
                                'symbol': ui_amount.get('symbol', mint[:8]),
                                'decimals': ui_amount.get('decimals', 0)
                            }
                    
                    # Process post-transaction token balances
                    for balance in post_token_balances:
                        if balance.get('owner') == wallet_address:
                            mint = balance.get('mint')
                            ui_amount = balance.get('uiTokenAmount', {})
                            amount = float(ui_amount.get('uiAmount', 0) or 0)
                            
                            if mint in token_changes:
                                token_changes[mint]['post'] = amount
                            else:
                                token_changes[mint] = {
                                    'pre': 0,
                                    'post': amount,
                                    'symbol': ui_amount.get('symbol', mint[:8]),
                                    'decimals': ui_amount.get('decimals', 0)
                                }
                    
                    # Calculate token deltas
                    gained_tokens = []
                    lost_tokens = []
                    significant_changes = []
                    
                    for mint, change in token_changes.items():
                        delta = change['post'] - change['pre']
                        if abs(delta) > 0.000001:  # Ignore dust
                            change['delta'] = delta
                            significant_changes.append((mint, change))
                            
                            if delta > 0:
                                gained_tokens.append((mint, delta, change['symbol']))
                            else:
                                lost_tokens.append((mint, abs(delta), change['symbol']))
                    
                    # Determine action with HIGH confidence
                    action = None
                    confidence = "LOW"
                    reasoning = ""
                    primary_token = None
                    
                    log_debug(f"   💰 SOL delta: {sol_delta:+.6f} SOL")
                    log_debug(f"   🪙 Token changes: {len(gained_tokens)} gained, {len(lost_tokens)} lost")
                    
                    for mint, amount, symbol in gained_tokens:
                        log_debug(f"      ✅ Gained {amount:,.6f} {symbol}")
                    for mint, amount, symbol in lost_tokens:
                        log_debug(f"      ❌ Lost {amount:,.6f} {symbol}")
                    
                    # DECISION LOGIC - HIGH CONFIDENCE DETECTION
                    if sol_delta < -0.001 and len(gained_tokens) > 0 and len(lost_tokens) == 0:
                        # Spent SOL and gained tokens = BUY
                        action = "buy"
                        confidence = "HIGH"
                        reasoning = f"Spent {abs(sol_delta):.6f} SOL, gained {gained_tokens[0][1]:,.6f} {gained_tokens[0][2]}"
                        primary_token = gained_tokens[0][0]
                        
                    elif sol_delta > 0.001 and len(lost_tokens) > 0 and len(gained_tokens) == 0:
                        # Gained SOL and lost tokens = SELL
                        action = "sell"
                        confidence = "HIGH"
                        reasoning = f"Gained {sol_delta:+.6f} SOL, sold {lost_tokens[0][1]:,.6f} {lost_tokens[0][2]}"
                        primary_token = lost_tokens[0][0]
                        
                    elif len(gained_tokens) > 0 and len(lost_tokens) > 0:
                        # Token-to-token swap
                        action = "swap"
                        confidence = "MEDIUM"
                        reasoning = f"Swapped {lost_tokens[0][1]:,.6f} {lost_tokens[0][2]} for {gained_tokens[0][1]:,.6f} {gained_tokens[0][2]}"
                        primary_token = gained_tokens[0][0] if len(gained_tokens) > 0 else lost_tokens[0][0]
                        
                    elif abs(sol_delta) > 0.001 and len(significant_changes) == 0:
                        # Pure SOL transfer (not trading)
                        log_debug(f"   ℹ️ Pure SOL transfer, not a trade")
                        return None
                        
                    else:
                        log_debug(f"   ❓ Unclear transaction pattern")
                        return None
                    
                    if action:
                        trade_result = {
                            'signature': signature,
                            'wallet_address': wallet_address,
                            'action': action,
                            'confidence': confidence,
                            'reasoning': reasoning,
                            'dex': 'balance_detected',  # Will be refined by further analysis
                            'token_mint': primary_token,
                            'sol_delta': sol_delta,
                            'gained_tokens': gained_tokens,
                            'lost_tokens': lost_tokens,
                            'timestamp': datetime.now(UTC),
                            'method': 'balance_based_detection'
                        }
                        
                        log_debug(f"   ✅ {action.upper()} detected with {confidence} confidence")
                        log_debug(f"   🎯 Reasoning: {reasoning}")
                        
                        return trade_result
                    
                    return None
                        
        except Exception as e:
            log_debug(f"   ❌ Error in balance analysis: {e}")
            # Balance analysis failed - return None (no execution without balance changes)
            log_debug(f"   ⚠️ Cannot proceed without balance analysis - skipping")
            return None

    def _check_dex_instruction_in_logs(self, logs: List[str]) -> bool:
        """
        Check if logs contain DEX trade instructions.
        Returns True if any known DEX program or trade instruction is found.
        """
        # Known DEX program IDs
        dex_programs = [
            'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4',  # Jupiter V6
            'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB',  # Jupiter V4
            '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',  # Pump.fun
            '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',  # Raydium AMM
            'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C',  # Raydium CPMM
            '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1',  # Raydium CLMM
            'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK',  # Raydium CLMM v2
            'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc',  # Orca Whirlpool
            'SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8',  # Orca Swap
            'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN',  # Meteora Aggregator
            'Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB',  # Meteora DLMM
            'ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA',  # Alpha DEX
        ]
        
        # Trade instruction keywords
        trade_keywords = [
            'Instruction: Swap',
            'Instruction: Buy',
            'Instruction: Sell',
            'Instruction: Route',
            'Program log: swap',
            'Program log: trade',
            'SharedAccountsRoute'
        ]
        
        for log in logs:
            # Check for DEX programs
            for program_id in dex_programs:
                if program_id in log:
                    log_debug(f"   ✅ DEX program found in logs: {program_id[:8]}...")
                    return True
            
            # Check for trade keywords
            for keyword in trade_keywords:
                if keyword.lower() in log.lower():
                    log_debug(f"   ✅ Trade keyword found in logs: {keyword}")
                    return True
        
        return False
    
    def _is_monitored_wallet(self, wallet_address: str) -> bool:
        """
        Check if wallet is in the monitored wallets list (case-insensitive).
        """
        if not hasattr(self, 'target_wallets') or not self.target_wallets:
            return False
        
        wallet_lower = wallet_address.lower()
        for monitored in self.target_wallets:
            if monitored.lower() == wallet_lower:
                log_debug(f"   ✅ Wallet is monitored: {wallet_address[:8]}...")
                return True
        
        return False
    
    async def _create_synthetic_trade_info(self, signature: str, wallet_address: str, logs: List[str], has_dex_instruction: bool) -> Optional[Dict[str, Any]]:
        """
        DEPRECATED: This method created synthetic trades without balance changes.
        This violates the principle of requiring actual balance changes for execution.
        Returns None to prevent execution without balance proof.
        """
        log_debug(f"⚠️ DEPRECATED METHOD CALLED: _create_synthetic_trade_info")
        log_debug(f"   This method is deprecated and returns None")
        log_debug(f"   Balance changes are REQUIRED for trade detection")
        return None

    async def _analyze_logs_for_trade_smart(self, signature: str, wallet_address: str, logs: List[str]) -> Optional[Dict[str, Any]]:
        """
        DEPRECATED: This method attempted log-based trade detection without balance changes.
        This violates the principle of requiring actual balance changes for execution.
        Returns None to prevent execution without balance proof.
        """
        log_debug(f"⚠️ DEPRECATED METHOD CALLED: _analyze_logs_for_trade_smart")
        log_debug(f"   This method is deprecated and returns None")
        log_debug(f"   Balance changes are REQUIRED for trade detection")
        return None

        """OFFICIAL: Extract token mint using official Solana getTransaction with jsonParsed encoding"""
        try:
            log_debug(f"   🔧 OFFICIAL BALANCE ANALYSIS: Using Solana jsonParsed for {signature[:8]}...")
            
            import aiohttp
            
            # Official Solana getTransaction with jsonParsed encoding
            tx_params = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction", 
                "params": [
                    signature,
                    {
                        "encoding": "jsonParsed",
                        "maxSupportedTransactionVersion": 0,
                        "commitment": "processed"  # 🚀 FIXED: Match WebSocket notification level
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self._get_http_rpc_url(),
                                      json=tx_params,
                                      headers={'Content-Type': 'application/json'}) as response:
                    tx_data = await response.json()
            
            result = tx_data.get("result")
            if not result:
                log_debug(f"   ❌ No transaction result")
                return None
                
            # Check transaction success
            meta = result.get("meta", {})
            if meta.get("err"):
                log_debug(f"   ❌ Transaction failed: {meta.get('err')}")
                return None
                
            # Official token balance analysis using preTokenBalances/postTokenBalances
            pre_token_balances = meta.get("preTokenBalances", [])
            post_token_balances = meta.get("postTokenBalances", [])
            
            log_debug(f"   🔍 Official analysis: {len(pre_token_balances)} pre-balances, {len(post_token_balances)} post-balances")
            
            # Build balance change map using official structure
            balance_changes = {}
            
            # Process pre-transaction balances
            for pre_balance in pre_token_balances:
                owner = pre_balance.get("owner")
                mint = pre_balance.get("mint")
                ui_amount = pre_balance.get("uiTokenAmount", {}).get("uiAmount")
                
                if owner == wallet_address and mint and ui_amount is not None:
                    balance_changes[mint] = {"pre": float(ui_amount), "post": 0.0}
                    
            # Process post-transaction balances
            for post_balance in post_token_balances:
                owner = post_balance.get("owner")
                mint = post_balance.get("mint")
                ui_amount = post_balance.get("uiTokenAmount", {}).get("uiAmount")
                
                if owner == wallet_address and mint and ui_amount is not None:
                    if mint in balance_changes:
                        balance_changes[mint]["post"] = float(ui_amount)
                    else:
                        balance_changes[mint] = {"pre": 0.0, "post": float(ui_amount)}
            
            # Filter known system tokens (WSOL, USDC, etc.)
            SYSTEM_TOKENS = {
                "So11111111111111111111111111111111111111112",  # WSOL
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            }
            
            # Find the token with the largest positive balance change (BUY)
            best_token = None
            max_increase = 0.0
            
            for mint, changes in balance_changes.items():
                if mint in SYSTEM_TOKENS:
                    continue
                    
                pre_amount = changes["pre"]
                post_amount = changes["post"]
                increase = post_amount - pre_amount
                
                log_debug(f"   📊 {mint[:8]}...: {pre_amount} → {post_amount} (Δ: {increase:+.6f})")
                
                if increase > max_increase:
                    max_increase = increase
                    best_token = mint
            
            if best_token and max_increase > 0:
                log_debug(f"   ✅ OFFICIAL TOKEN DETECTED: {best_token[:8]}... (increase: +{max_increase:.6f})")
                return best_token
            else:
                log_debug(f"   ❌ No token increases found in balance analysis")
                return None
                
        except Exception as e:
            log_debug(f"   ❌ Error in balance-based analysis: {e}")
            return None
            
    # OLD FLAWED METHOD REMOVED: _parse_logs_for_trade

    # OLD FLAWED METHOD REMOVED: _detect_dex_from_logs
        
    # OLD FLAWED METHOD REMOVED: _detect_trade_action

    # OLD FLAWED METHOD REMOVED: _detect_significant_activity

    # OLD FLAWED METHOD REMOVED: _analyze_token_flow

    # OLD FLAWED METHOD REMOVED: _extract_token_mint_from_logs

    def _extract_trade_details(self, logs: List[str]) -> Dict[str, Any]:
        """Extract additional trade details from logs"""
        details = {}
        
        try:
            full_log_text = ' '.join(logs)
            
            # Try to extract amounts (this is complex and may need refinement)
            amount_patterns = [
                r'amount[:\s]+(\d+)',
                r'lamports[:\s]+(\d+)',
                r'tokens[:\s]+(\d+)',
            ]
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, full_log_text, re.IGNORECASE)
                if matches:
                    details['raw_amounts'] = matches
                    break
                    
            # Extract instruction type if available
            instruction_match = re.search(r'Instruction:\s+(\w+)', full_log_text)
            if instruction_match:
                details['instruction_type'] = instruction_match.group(1)
                
        except Exception as e:
            log_debug(f"❌ Error extracting trade details: {e}")
            
        return details
        
    def stop_monitoring(self):
        """🛑 CLEAN STOP: Properly stop WebSocket monitoring"""
        log_debug("🛑 Stopping WebSocket monitoring...")
        self.is_running = False
        
        # Clear subscription mappings
        self.subscription_ids.clear()
        log_debug("✅ WebSocket monitoring stopped cleanly")

    async def _extract_real_token_from_failed_transaction(self, signature: str) -> Optional[str]:
        """🔍 Extract real token mint from failed transaction for ultra-aggressive mode"""
        try:
            print(f"🔍 Extracting real token from transaction {signature[:8]}...")
            
            # Get transaction data
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ws_url, json=payload) as response:
                    data = await response.json()
                    
                    result = data.get('result')
                    if not result:
                        return None
                    
                    # Look for token mints in account keys
                    transaction = result.get('transaction', {})
                    message = transaction.get('message', {})
                    account_keys = message.get('accountKeys', [])
                    
                    # Filter out known system programs
                    system_programs = {
                        "11111111111111111111111111111111",
                        "ComputeBudget111111111111111111111111111111",
                        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
                    }
                    
                    # Find potential token mints (44 character Base58 strings that aren't system programs)
                    for account in account_keys:
                        if len(account) == 44 and account not in system_programs:
                            # This could be a token mint
                            print(f"   🎯 Potential token mint found: {account[:8]}...")
                            return account
                    
                    return None
                    
        except Exception as e:
            print(f"   ❌ Error extracting real token: {e}")
            return None

class WalletATxParser:
    def __init__(self, wallet: Keypair):
        self.wallet = wallet
        self.pubkey = wallet.pubkey()
        self.last_signature = None
        self.session = None
        print(f"📝 Initialized TX parser for wallet: {self.pubkey}")
        print(f"👀 Monitoring Wallet A: {WALLET_A}")
        print(f"⏰ Current Time (UTC): 2025-06-15 14:30:51")
        print(f"👤 Current User: tinotc-72")

    async def create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    def parse_transaction_logs(self, logs: list) -> Optional[Dict[str, Any]]:
        """Parse transaction logs to identify trade information"""
        if not logs:
            return None

        try:
            # Initialize result dictionary
            result = {
                "program_id": None,
                "instruction": None,
                "dex": None,
                "type": None
            }

            # First pass - look for Pump.fun programs
            for i, log in enumerate(logs):
                if "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke" in log:
                    result["dex"] = "Pump.fun"
                    result["program_id"] = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
                    break
                # REMOVED LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj - this is a token mint, not a program

            if result["program_id"]:
                # Second pass - look for instruction type
                for log in logs:
                    # Check for buy instructions
                    if "Instruction: BuyExactIn" in log:
                        result["instruction"] = "Buy"
                        result["type"] = "BuyExactIn"
                        print("✅ Detected Pump.fun BUY (BuyExactIn) - Processing trade...")
                        return result
                    # Check for sell instructions
                    elif "Instruction: SellExactIn" in log:
                        result["instruction"] = "Sell"
                        result["type"] = "SellExactIn"
                        print("✅ Detected Pump.fun SELL (SellExactIn) - Processing trade...")
                        return result

                # OLD CODE REMOVED: References to deleted BUY_KEYWORDS and SELL_KEYWORDS

            if DEBUG and result["program_id"]:
                print(f"⚠️ Unknown instruction type for program: {result['program_id']}")
                print("First few logs:")
                for log in logs[:5]:
                    print(f"  {log[:100]}...")

            return None

        except Exception as e:
            print(f"❌ Error parsing transaction logs: {str(e)}")
            traceback.print_exc()
            return None

    async def get_next_transaction(self):
        """Monitor and get the next transaction from Wallet A"""
        try:
            session = await self.create_session()
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    # Get recent signatures for Wallet A
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignaturesForAddress",
                        "params": [
                            str(WALLET_A),
                            {
                                "limit": 1,
                                "before": self.last_signature
                            }
                        ]
                    }

                    async with session.post(RPC_URL, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if "result" in data and data["result"]:
                                signature = data["result"][0]["signature"]
                                
                                # If this is a new transaction
                                if signature != self.last_signature:
                                    self.last_signature = signature
                                    
                                    # Get transaction details with improved error handling
                                    tx_data = await self.get_transaction_details(signature)
                                    if tx_data:
                                        print(f"🔍 Found new transaction from Wallet A: {signature[:8]}...")
                                        
                                        # Parse logs to determine if it's a relevant trade
                                        if "meta" in tx_data and "logMessages" in tx_data["meta"]:
                                            trade_info = self.parse_transaction_logs(tx_data["meta"]["logMessages"])
                                            if trade_info:  # If it's a relevant trade
                                                print(f"📊 Trade Details:")
                                                print(f"   DEX: {trade_info['dex']}")
                                                print(f"   Type: {trade_info['type']}")
                                                print(f"   Instruction: {trade_info['instruction']}")
                                                return tx_data
                                        
                                    return None

                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        
                except Exception as e:
                    print(f"⚠️ Attempt {attempt + 1} error: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
            
            return None

        except Exception as e:
            print(f"❌ Error monitoring Wallet A: {e}")
            traceback.print_exc()
            return None

    async def get_transaction_details(self, signature: str) -> Optional[dict]:
        """Get detailed transaction information with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                tx_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        signature,
                        {
                            "encoding": "json",
                            "maxSupportedTransactionVersion": 0,
                            "commitment": "processed"  # 🚀 FIXED: Match WebSocket notification level
                        }
                    ]
                }
                
                async with self.session.post(RPC_URL, json=tx_payload) as tx_response:
                    if tx_response.status == 200:
                        tx_data = await tx_response.json()
                        if "result" in tx_data and tx_data["result"]:
                            return tx_data["result"]
                    
                    print(f"⚠️ Attempt {attempt + 1}: Failed to fetch transaction details")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} error: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))
                
        return None

    async def __aenter__(self):
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()
        
def extract_mint_from_meta(data: dict) -> str | None:
    post_balances = data.get("meta", {}).get("postTokenBalances", [])
    if post_balances and "mint" in post_balances[0]:
        return post_balances[0]["mint"]

    instructions = data.get("transaction", {}).get("message", {}).get("instructions", [])
    for ix in instructions:
        parsed = ix.get("parsed", {})
        if isinstance(parsed, dict) and parsed.get("type") == "transferChecked":
            return parsed.get("info", {}).get("mint")
    return None

def get_program_ids(data: dict) -> list[str]:
    try:
        transaction = data.get("transaction", {})
        message = transaction.get("message", {})
        instructions = message.get("instructions", [])
        return [
            ix.get("programId")
            for ix in instructions
            if isinstance(ix, dict) and "programId" in ix
        ]
    except Exception as e:
        print(f"⚠️ get_program_ids failed: {e}")
        return []

# Convenience functions for integration with main.py
async def create_websocket_monitor(target_wallets: List[str], trade_callback: Callable[[Dict[str, Any]], None], ws_url: str = None) -> WebSocketWalletMonitor:
    """Create and configure a WebSocket wallet monitor"""
    monitor = WebSocketWalletMonitor(target_wallets, ws_url)
    monitor.set_trade_callback(trade_callback)
    
    # Test the callback immediately to ensure it works (with SHORT timeout to prevent hanging)
    log_debug("🧪 Testing callback with dummy trade...")
    test_trade = {
        'signature': 'test123',
        'wallet_address': target_wallets[0] if target_wallets else 'test_wallet',
        'action': 'buy',
        'dex': 'Pump.fun',
        'token_mint': 'TEST_TOKEN_MINT',
        'timestamp': datetime.now(UTC)
    }
    
    try:
        # CRITICAL FIX: Use very short timeout to prevent initialization hangs
        await asyncio.wait_for(trade_callback(test_trade), timeout=1.0)
        log_debug("✅ Callback test successful!")
    except asyncio.TimeoutError:
        log_debug("⚠️ Callback test timed out (this is usually fine for copy trading bots)")
    except Exception as e:
        log_debug(f"⚠️ Callback test failed: {e}")
        # Don't fail initialization just because of callback test
    
    return monitor

async def start_realtime_monitoring(target_wallets: List[str], trade_callback: Callable[[Dict[str, Any]], None], ws_url: str = None):
    """Start real-time WebSocket monitoring for the given wallets"""
    log_debug(f"🚀 Starting real-time monitoring for {len(target_wallets)} wallets")
    
    monitor = await create_websocket_monitor(target_wallets, trade_callback, ws_url)
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        log_debug("⏹️ Monitoring stopped by user")
    except Exception as e:
        log_debug(f"❌ Monitoring error: {e}")
        traceback.print_exc()
    finally:
        monitor.stop_monitoring()

    async def _extract_real_token_from_failed_transaction(self, signature: str) -> Optional[str]:
        """🔍 Extract real token mint from failed transaction for ultra-aggressive mode"""
        try:
            print(f"🔍 Extracting real token from transaction {signature[:8]}...")
            
            # Get transaction data
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.websocket_url, json=payload) as response:
                    data = await response.json()
                    
                    result = data.get('result')
                    if not result:
                        return None
                    
                    # Look for token mints in account keys
                    transaction = result.get('transaction', {})
                    message = transaction.get('message', {})
                    account_keys = message.get('accountKeys', [])
                    
                    # Filter for potential token mints (44 character Base58 strings)
                    potential_tokens = []
                    system_programs = {
                        "11111111111111111111111111111111",
                        "ComputeBudget111111111111111111111111111111",
                        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
                        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun program
                        "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"  # Pump.fun router
                    }
                    
                    for account in account_keys:
                        if (len(account) >= 32 and 
                            account not in system_programs and
                            not account.startswith('So1111') and  # Not WSOL
                            not account.startswith('4wTV1Y') and  # Not Pump.fun global
                            not account.startswith('CebN5W')):    # Not fee account
                            potential_tokens.append(account)
                    
                    # Return the first potential token mint found
                    if potential_tokens:
                        token_mint = potential_tokens[0]
                        print(f"✅ Found potential token: {token_mint[:8]}...")
                        return token_mint
                    
                    print(f"⚠️ No token mints found in account keys")
                    return None
                    
        except Exception as e:
            print(f"❌ Error extracting real token: {e}")
            return None

# Example usage and testing
async def example_trade_handler(trade_info: Dict[str, Any]):
    """Example callback function to handle detected trades"""
    print(f"🚨 TRADE DETECTED!")
    print(f"   👤 Wallet: {trade_info['wallet_address'][:8]}...")
    print(f"   🎬 Action: {trade_info['action'].upper()}")
    print(f"   💎 Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
    print(f"   🏪 DEX: {trade_info.get('dex', 'Unknown')}")
    print(f"   📝 Signature: {trade_info['signature'][:12]}...")
    print(f"   ⏰ Time: {trade_info['timestamp']}")
    
    # Here you would integrate with your copy trading logic
    if trade_info['action'] == 'buy':
        print(f"   🎯 COPY BUY SIGNAL: Execute copy trade for {trade_info.get('token_mint', 'Unknown')}")
    elif trade_info['action'] == 'sell':
        print(f"   🎯 COPY SELL SIGNAL: Execute copy sell for {trade_info.get('token_mint', 'Unknown')}")

if __name__ == "__main__":
    # Example usage
    test_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Example wallet 1
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Example wallet 2
    ]
    
    print("🔍 Testing WebSocket wallet monitoring...")
    asyncio.run(start_realtime_monitoring(test_wallets, example_trade_handler))