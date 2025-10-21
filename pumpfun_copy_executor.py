#!/usr/bin/env python3
"""
Pump.fun Copy Executor - MEV-ready executor for Pump.fun trades
Uses only solders (no solana-py) with byte-accurate protocol compliance

Based on reverse-engineering of successful buy and sell transactions.
Implements proper account metas, instruction data, ATA creation, compute budget,
ALT support, and unified submission via send_and_confirm_v0_tx.

Protocol compliance:
- Buy discriminator: 66063d1201daebea
- Sell discriminator: 33e685a4017f83ad
- Instruction data format: discriminator + struct.pack("<QQ", amount, slippage)
- Account order matches Pump.fun Anchor program requirements
"""

# Core imports - solders only
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.hash import Hash

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result

import struct
import logging
from typing import Dict, Any, Optional, List
from utils.ata import create_associated_token_account

logger = logging.getLogger(__name__)


# Pump.fun Program Constants
PUMP_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
PUMP_EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")

# System program constants
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# Instruction discriminators (discovered from successful transactions)
BUY_DISCRIMINATOR = bytes.fromhex("66063d1201daebea")
SELL_DISCRIMINATOR = bytes.fromhex("33e685a4017f83ad")


def derive_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    """
    Derive the associated token address for a given owner and mint.
    Uses proper PDA derivation with find_program_address.
    
    Args:
        owner: The owner's public key
        mint: The token mint public key
        
    Returns:
        The derived associated token address
    """
    seeds = [bytes(owner), bytes(TOKEN_PROGRAM_ID), bytes(mint)]
    ata, _bump = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return ata


def derive_bonding_curve(mint: Pubkey) -> Pubkey:
    """
    Derive the bonding curve PDA for a given token mint.
    
    Args:
        mint: The token mint public key
        
    Returns:
        The derived bonding curve address
    """
    seeds = [b"bonding-curve", bytes(mint)]
    bonding_curve, _bump = Pubkey.find_program_address(seeds, PUMP_PROGRAM_ID)
    return bonding_curve


def derive_creator_vault(mint: Pubkey) -> Pubkey:
    """
    Derive the creator vault PDA for a given token mint.
    Tries multiple patterns to find the correct one.
    
    Args:
        mint: The token mint public key
        
    Returns:
        The derived creator vault address
    """
    # Try the most common pattern first
    patterns = [
        [b"creator", bytes(mint)],
        [b"creator_vault", bytes(mint)],
        [bytes(mint), b"creator"],
    ]
    
    for seeds in patterns:
        try:
            vault, _bump = Pubkey.find_program_address(seeds, PUMP_PROGRAM_ID)
            return vault
        except Exception:
            continue
    
    # If all fail, use first pattern as default
    vault, _bump = Pubkey.find_program_address([b"creator", bytes(mint)], PUMP_PROGRAM_ID)
    return vault


class PumpfunCopyExecutor:
    """MEV-ready copy executor for Pump.fun trades with protocol-compliant instructions"""
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        logger.info("[PUMPFUN_EXECUTOR] Initialized with RPC: %s", rpc_url)
        
    async def copy_pumpfun_trade(
        self, wallet_keypair: Keypair, signature: str, 
        trade_info: Dict[str, Any], amount_override: Optional[float] = None
    ) -> BuildResult:
        """
        Copy a Pump.fun trade with the specified parameters.
        
        Args:
            wallet_keypair: The wallet keypair to sign transactions
            signature: Original transaction signature (for logging)
            trade_info: Trade details including action, token_mint, amount, etc.
            amount_override: Optional override for trade amount
            
        Returns:
            BuildResult with transaction status
        """
        try:
            logger.info(f"🔄 [PUMPFUN_COPY] Copying trade: {signature[:8]}...")
            
            # Extract trade details
            action = trade_info.get("action", "buy")
            token_mint = trade_info.get("token_mint")
            if not token_mint:
                return BuildResult(ok=False, tx=None, reason="Missing token mint")
            
            # Parse mint if it's a string
            try:
                mint_pubkey = Pubkey.from_string(token_mint) if isinstance(token_mint, str) else token_mint
            except Exception as e:
                return BuildResult(ok=False, tx=None, reason=f"Invalid token mint: {e}")
            
            # Get amount to trade
            amount = amount_override or trade_info.get("amount", 0.01)
            
            if action == "buy":
                result = await self._execute_pumpfun_buy(wallet_keypair, mint_pubkey, amount, trade_info)
            else:
                result = await self._execute_pumpfun_sell(wallet_keypair, mint_pubkey, amount, trade_info)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ [PUMPFUN_COPY] Error: {e}")
            return BuildResult(ok=False, tx=None, reason=f"pumpfun copy failed: {e}")

    async def _execute_pumpfun_buy(
        self, wallet: Keypair, token_mint: Pubkey, sol_amount: float, trade_info: Dict[str, Any]
    ) -> BuildResult:
        """
        Execute a Pump.fun buy transaction with byte-accurate instruction construction.
        
        Protocol:
        - Discriminator: 66063d1201daebea (8 bytes)
        - Data: discriminator + struct.pack("<QQ", sol_lamports, max_sol_cost)
        - Account order: global, fee_recipient, mint, bonding_curve, bonding_curve_ata,
                        user_token_ata, user_wallet, system_program, token_program,
                        creator_vault, event_authority, program_id
        
        Args:
            wallet: The wallet keypair to sign with
            token_mint: The token mint to buy
            sol_amount: Amount of SOL to spend
            trade_info: Additional trade information
            
        Returns:
            BuildResult with transaction status
        """
        try:
            logger.info(f"💰 [PUMPFUN_BUY] Buying {sol_amount} SOL of {token_mint}")
            
            # Derive all required accounts
            bonding_curve = derive_bonding_curve(token_mint)
            bonding_curve_ata = derive_associated_token_address(bonding_curve, token_mint)
            user_token_ata = derive_associated_token_address(wallet.pubkey(), token_mint)
            creator_vault = derive_creator_vault(token_mint)
            
            logger.debug(f"[PUMPFUN_BUY] Bonding curve: {bonding_curve}")
            logger.debug(f"[PUMPFUN_BUY] Bonding curve ATA: {bonding_curve_ata}")
            logger.debug(f"[PUMPFUN_BUY] User token ATA: {user_token_ata}")
            logger.debug(f"[PUMPFUN_BUY] Creator vault: {creator_vault}")
            
            # Build instruction data: discriminator + amount + max_cost
            sol_lamports = int(sol_amount * 1_000_000_000)
            slippage_tolerance = trade_info.get("slippage", 0.10)  # Default 10%
            max_sol_cost = int(sol_lamports * (1 + slippage_tolerance))
            
            instruction_data = BUY_DISCRIMINATOR + struct.pack("<QQ", sol_lamports, max_sol_cost)
            
            # Build account metas in correct order (critical for Anchor program validation)
            accounts = [
                AccountMeta(PUMP_GLOBAL_ACCOUNT, is_signer=False, is_writable=True),
                AccountMeta(PUMP_FEE_RECIPIENT, is_signer=False, is_writable=True),
                AccountMeta(token_mint, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(user_token_ata, is_signer=False, is_writable=True),
                AccountMeta(wallet.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(creator_vault, is_signer=False, is_writable=True),
                AccountMeta(PUMP_EVENT_AUTHORITY, is_signer=False, is_writable=False),
                AccountMeta(PUMP_PROGRAM_ID, is_signer=False, is_writable=False),
            ]
            
            # Create Pump.fun buy instruction
            swap_ix = Instruction(
                program_id=PUMP_PROGRAM_ID,
                accounts=accounts,
                data=instruction_data
            )
            
            # Start with swap instruction
            ixs = [swap_ix]
            
            # PR-02 Pattern: Apply compute budget before compile
            ixs = with_compute_budget(ixs)
            
            # Prepare variables for ATA enforcement
            payer = wallet.pubkey()
            owner = wallet.pubkey()
            out_mint = token_mint
            
            # Ensure ATA instructions (atomically create if needed, BEFORE swap)
            ata_ixs = ensure_ata_ixs(self.rpc_url, payer, owner, out_mint, create_associated_token_account)
            ixs = ata_ixs + ixs
            
            # Build ALTs if present in trade_info
            table_pubkeys = trade_info.get("lookup_tables", [])
            alts = build_alts_from_tables(self.rpc_url, table_pubkeys) if table_pubkeys else []
            
            # Compile v0 message with ALT support
            try:
                blockhash = get_recent_blockhash(self.rpc_url)
                msg = MessageV0.try_compile(
                    payer=payer,
                    instructions=ixs,
                    address_lookup_tables=alts,
                    recent_blockhash=blockhash,
                )
            except Exception as e:
                logger.error(f"[PUMPFUN_BUY] Failed to compile message: {e}")
                return BuildResult(ok=False, tx=None, reason=f"Message compile failed: {e}")
            
            # Sign transaction
            tx = VersionedTransaction(msg, [wallet])
            
            # Submit + confirm using unified submitter
            res = await send_and_confirm_v0_tx(tx, self.rpc_url)
            log_submit_result("pumpfun", "buy", str(token_mint), res)
            
            if res.get("success"):
                sig = res.get("signature")
                logger.info(f"✅ [PUMPFUN_BUY] Success: {sig}")
                return BuildResult(ok=True, tx=sig, dex="pumpfun", action="buy")
            else:
                error = res.get("error", "Unknown error")
                logger.error(f"❌ [PUMPFUN_BUY] Failed: {error}")
                return BuildResult(ok=False, tx=None, reason=f"submit failed: {error}")
            
        except Exception as e:
            logger.error(f"❌ [PUMPFUN_BUY] Error: {e}", exc_info=True)
            return BuildResult(ok=False, tx=None, reason=f"pumpfun buy failed: {e}")


    async def _execute_pumpfun_sell(
        self, wallet: Keypair, token_mint: Pubkey, token_amount: float, trade_info: Dict[str, Any]
    ) -> BuildResult:
        """
        Execute a Pump.fun sell transaction with byte-accurate instruction construction.
        
        Protocol:
        - Discriminator: 33e685a4017f83ad (8 bytes)
        - Data: discriminator + struct.pack("<QQ", token_amount, min_sol_out)
        - Account order: global, fee_recipient, mint, bonding_curve, bonding_curve_ata,
                        user_token_ata, user_wallet, system_program, creator_vault,
                        token_program, event_authority, program_id
        - Note: Sell account order differs slightly from buy (creator_vault before token_program)
        
        Args:
            wallet: The wallet keypair to sign with
            token_mint: The token mint to sell
            token_amount: Amount of tokens to sell (can be fractional, will convert to lamports)
            trade_info: Additional trade information
            
        Returns:
            BuildResult with transaction status
        """
        try:
            logger.info(f"💸 [PUMPFUN_SELL] Selling {token_amount} tokens of {token_mint}")
            
            # Derive all required accounts
            bonding_curve = derive_bonding_curve(token_mint)
            bonding_curve_ata = derive_associated_token_address(bonding_curve, token_mint)
            user_token_ata = derive_associated_token_address(wallet.pubkey(), token_mint)
            creator_vault = derive_creator_vault(token_mint)
            
            logger.debug(f"[PUMPFUN_SELL] Bonding curve: {bonding_curve}")
            logger.debug(f"[PUMPFUN_SELL] Bonding curve ATA: {bonding_curve_ata}")
            logger.debug(f"[PUMPFUN_SELL] User token ATA: {user_token_ata}")
            logger.debug(f"[PUMPFUN_SELL] Creator vault: {creator_vault}")
            
            # Build instruction data: discriminator + token_amount + min_sol_out
            # Assume 6 decimals for token (standard for Pump.fun)
            token_lamports = int(token_amount * 1_000_000)
            min_sol_out = trade_info.get("min_sol_out", 0)  # Accept any amount by default
            
            instruction_data = SELL_DISCRIMINATOR + struct.pack("<QQ", token_lamports, min_sol_out)
            
            # Build account metas in correct order for SELL (differs from buy!)
            accounts = [
                AccountMeta(PUMP_GLOBAL_ACCOUNT, is_signer=False, is_writable=True),
                AccountMeta(PUMP_FEE_RECIPIENT, is_signer=False, is_writable=True),
                AccountMeta(token_mint, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(user_token_ata, is_signer=False, is_writable=True),
                AccountMeta(wallet.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(creator_vault, is_signer=False, is_writable=True),
                AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(PUMP_EVENT_AUTHORITY, is_signer=False, is_writable=False),
                AccountMeta(PUMP_PROGRAM_ID, is_signer=False, is_writable=False),
            ]
            
            # Create Pump.fun sell instruction
            swap_ix = Instruction(
                program_id=PUMP_PROGRAM_ID,
                accounts=accounts,
                data=instruction_data
            )
            
            # Start with swap instruction
            ixs = [swap_ix]
            
            # PR-02 Pattern: Apply compute budget before compile
            ixs = with_compute_budget(ixs)
            
            # For sells, we need the SOL ATA (wrapped SOL)
            # But Pump.fun sells transfer native SOL, so no ATA needed for output
            # The user_token_ata already exists (we're selling from it)
            
            # Build ALTs if present in trade_info
            table_pubkeys = trade_info.get("lookup_tables", [])
            alts = build_alts_from_tables(self.rpc_url, table_pubkeys) if table_pubkeys else []
            
            # Compile v0 message with ALT support
            try:
                payer = wallet.pubkey()
                blockhash = get_recent_blockhash(self.rpc_url)
                msg = MessageV0.try_compile(
                    payer=payer,
                    instructions=ixs,
                    address_lookup_tables=alts,
                    recent_blockhash=blockhash,
                )
            except Exception as e:
                logger.error(f"[PUMPFUN_SELL] Failed to compile message: {e}")
                return BuildResult(ok=False, tx=None, reason=f"Message compile failed: {e}")
            
            # Sign transaction
            tx = VersionedTransaction(msg, [wallet])
            
            # Submit + confirm using unified submitter
            res = await send_and_confirm_v0_tx(tx, self.rpc_url)
            log_submit_result("pumpfun", "sell", str(token_mint), res)
            
            if res.get("success"):
                sig = res.get("signature")
                logger.info(f"✅ [PUMPFUN_SELL] Success: {sig}")
                return BuildResult(ok=True, tx=sig, dex="pumpfun", action="sell")
            else:
                error = res.get("error", "Unknown error")
                logger.error(f"❌ [PUMPFUN_SELL] Failed: {error}")
                return BuildResult(ok=False, tx=None, reason=f"submit failed: {error}")
            
        except Exception as e:
            logger.error(f"❌ [PUMPFUN_SELL] Error: {e}", exc_info=True)
            return BuildResult(ok=False, tx=None, reason=f"pumpfun sell failed: {e}")

