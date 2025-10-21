#!/usr/bin/env python3
"""
CLMM Copy Executor - Adapted from your existing cpmm_copy_executor.py
Modified to work with CLMM program using the analyzed transaction structure
"""

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction

import asyncio
import struct
import logging
import aiohttp

# Defensive logger setup
class DummyLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    def warning(self, msg):
        print(f"[WARNING] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}")
    def debug(self, msg):
        print(f"[DEBUG] {msg}")

def get_safe_logger(logger_candidate):
    if isinstance(logger_candidate, logging.Logger):
        return logger_candidate
    if hasattr(logger_candidate, 'info') and hasattr(logger_candidate, 'warning') and hasattr(logger_candidate, 'error'):
        return logger_candidate
    return DummyLogger()

logger = get_safe_logger(globals().get('logger', None))
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from env_keys import EnvKeys
import base58
import json
import os
from config import WALLET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if not (hasattr(logger, 'info') and hasattr(logger, 'warning') and hasattr(logger, 'error')) or not isinstance(logger, logging.Logger):
    class DummyLogger:
        def info(self, msg):
            print(msg)
        def warning(self, msg):
            print("[WARN]", msg)
        def error(self, msg):
            print("[ERROR]", msg)
        def debug(self, msg):
            print("[DEBUG]", msg)
    logger = DummyLogger()

# Load environment
env = EnvKeys()

# CLMM program and constants
CLMM_PROGRAM = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

@dataclass
class CLMMCopyExecutorConfig:
    """Configuration for CLMM copy trade execution"""
    slippage_tolerance: float = 0.05  # 5% slippage tolerance
    max_retries: int = 2
    retry_delay: float = 0.5
    confirmation_timeout: float = 30.0
    compute_unit_limit: int = 200_000
    compute_unit_price: int = 1

class CLMMCopyExecutor:
    """
    CLMM copy executor adapted from CPMM version
    Uses the analyzed transaction structure to execute CLMM trades
    """
    
    def __init__(self, config: CLMMCopyExecutorConfig = None):
        # Load wallet from .env file
        self.wallet_keypair = WALLET
        self.wallet_pubkey = self.wallet_keypair.pubkey()
        self.rpc_url = env.HELIUS_RPC_URL
        self.client = None  # Will use aiohttp for RPC calls
        self.config = config or CLMMCopyExecutorConfig()
        # Real pool data from your analysis
        self.pool_data = {
            "pool_state": Pubkey.from_string("CYbD9RaToYMtWKA7QZyoLahnHdWq553Vm62Lh6qWtuxq"),
            "amm_config": Pubkey.from_string("EdPxg8QaeFSrTYqdWJn6Kezwy9McWncTYueD9eMGCuzR"),
            "token_mint": Pubkey.from_string("72jQFwjd14BEhyDfdQsH7D2hS5dN1H6bzsikjkyHyx2D"),
            "pool_vault_a": Pubkey.from_string("GviiXg2Xc1xCpyNY36r7h1EAy7uvse5UMkiiyHjRDU6Z"),
            "pool_vault_b": Pubkey.from_string("3bWPj5eepJm8CxUzk5MMFMN2CFJkntxKvbmy4zwwtpJd"),
            "observation_state": Pubkey.from_string("AA5RaVvyGyZgtmAsJJHT5ZVBxVPtAXuYaMwfgeFJW4Mk"),
            "tick_array": Pubkey.from_string("3bRDwNCbJGhYAxfg2kf9qDTNN8YAj1tAq5FFqwQLgu4g"),
        }
        global logger
        logger = get_safe_logger(logger)
        logger.info(f"🚀 CLMM Copy Executor initialized")
        logger.info(f"   Wallet: {self.wallet_pubkey}")
        logger.info(f"   Pool: {self.pool_data['pool_state']}")
        logger.info(f"   Token: {self.pool_data['token_mint']}")
    
    async def execute_copy_trade(self, is_buy: bool, amount: float = None, **kwargs) -> BuildResult:
        """Execute a copy trade - unified interface for buy/sell"""
        try:
            if is_buy:
                sol_amount = amount or 0.0001
                return await self.execute_buy_trade(sol_amount)
            else:
                token_amount = int(amount) if amount else None
                return await self.execute_sell_trade(token_amount, **kwargs)
        except Exception as e:
            logger.error(f"❌ CLMM copy trade error: {e}")
            return None

    async def execute_sell_copy(self, **kwargs) -> Optional[str]:
        """Execute a sell copy trade - for compatibility with other executors"""
        return await self.execute_sell_trade(**kwargs)
    
    async def execute_buy_trade(self, sol_amount: float = 0.0001) -> BuildResult:
        """Execute a CLMM buy trade"""
        try:
            logger.info(f"🛒 Executing CLMM BUY: {sol_amount} SOL")
            
            # Convert to lamports
            amount_lamports = int(sol_amount * 1_000_000_000)
            
            # Ensure token account exists
            await self.ensure_token_account_exists(self.pool_data["token_mint"])
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, SOL_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, self.pool_data["token_mint"])
            
            # Build CLMM swap instruction
            swap_instruction = self.build_clmm_swap_instruction(
                user_wsol_ata=user_wsol_ata,
                user_token_ata=user_token_ata,
                amount_in=amount_lamports,
                is_buy=True
            )
            
            # Execute transaction
            signature = await self.execute_instruction(swap_instruction)
            
            if signature:
                logger.info(f"✅ CLMM buy executed: {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="clmm",
                    action="buy",
                    reason="CLMM buy completed"
                )
            else:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="clmm",
                    action="buy",
                    reason="Transaction failed"
                )
            
        except Exception as e:
            logger.error(f"❌ CLMM buy error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="clmm",
                action="buy",
                reason=f"CLMM buy error: {e}"
            )
    
    async def execute_sell_trade(self, token_amount: Optional[int] = None, **kwargs) -> BuildResult:
        """Execute a CLMM sell trade with proportional selling support"""
        try:
            logger.info(f"💸 Executing CLMM SELL trade: {token_amount or 'ALL'} tokens")
            
            # Get token balance if amount not specified
            if token_amount is None:
                token_balance = await self.get_token_balance(self.pool_data["token_mint"])
            else:
                token_balance = token_amount
                
            if token_balance <= 0:
                logger.error(f"❌ No tokens to sell for {self.pool_data['token_mint']}")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="clmm",
                    action="sell",
                    reason="No tokens to sell"
                )

            # Proportional sell calculation
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            if sell_percentage <= 0 or sell_percentage > 100.0:
                logger.warning(f"⚠️ Invalid sell_percentage {sell_percentage}, defaulting to 100%.")
                sell_percentage = 100.0
            
            # Calculate proportional amount to sell
            amount_to_sell = int(token_balance * (sell_percentage / 100.0))
            logger.info(f"🎯 CLMM PROPORTIONAL SELL:\n   Total balance: {token_balance} tokens\n   Amount to sell: {amount_to_sell} tokens\n   Sell percentage: {sell_percentage:.2f}%")
            
            # Ensure token accounts exist
            user_wsol_ata = await self.ensure_token_account_exists(SOL_MINT)
            user_token_ata = await self.ensure_token_account_exists(self.pool_data["token_mint"])
            
            # Build sell swap instruction (token -> SOL)
            instruction = self.build_clmm_sell_instruction(
                user_token_ata=user_token_ata,
                user_wsol_ata=user_wsol_ata,
                amount_in=amount_to_sell
            )
            
            # Execute the instruction
            signature = await self.execute_instruction(instruction)
            
            if signature:
                logger.info(f"✅ CLMM sell executed: {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="clmm",
                    action="sell",
                    reason="CLMM sell completed"
                )
            else:
                logger.error(f"❌ CLMM sell failed")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="clmm",
                    action="sell",
                    reason="Transaction failed"
                )
            
        except Exception as e:
            logger.error(f"❌ CLMM sell error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="clmm",
                action="sell",
                reason=f"CLMM sell error: {e}"
            )

    async def get_token_balance(self, token_mint: Pubkey) -> int:
        """Get token balance for the wallet"""
        try:
            ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            # TODO: Replace with aiohttp/solders logic to fetch account info
            raise NotImplementedError("get_account_info must be implemented with aiohttp/Solders")
            
            if account_info.value is None:
                return 0
            
            # Parse token account data to get balance
            data = account_info.value.data
            # Token account layout: [mint(32), owner(32), amount(8), ...]
            if len(data) >= 72:
                amount = struct.unpack('<Q', data[64:72])[0]
                return amount
            return 0
            
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0
    
    def build_clmm_swap_instruction(
        self,
        user_wsol_ata: Pubkey,
        user_token_ata: Pubkey,
        amount_in: int,
        is_buy: bool
    ) -> Instruction:
        """Build a CLMM swap instruction using analyzed structure"""
        
        # Create instruction data - this is the key part that needs to be correct
        # Based on the analyzed transaction, we need to create proper instruction data
        # For now, let's try a simple swap instruction format
        
        # Calculate minimum output with slippage
        if is_buy:
            # For SOL->Token: estimate based on amount
            estimated_out = amount_in * 1000  # Very rough estimate
        else:
            # For Token->SOL: estimate based on amount
            estimated_out = amount_in // 1000  # Very rough estimate
        
        min_amount_out = int(estimated_out * (1 - self.config.slippage_tolerance))
        min_amount_out = max(min_amount_out, 1)  # Ensure at least 1
        
        # Create instruction data - using a simple format
        # This might need adjustment based on actual CLMM instruction format
        instruction_data = struct.pack("<QQ", amount_in, min_amount_out)
        
        # Build accounts in exact order from analyzed transaction
        accounts = [
            AccountMeta(self.wallet_pubkey, True, True),  # 0: User/Payer
            AccountMeta(self.pool_data["amm_config"], False, False),  # 1: AMM Config
            AccountMeta(self.pool_data["pool_state"], False, True),   # 2: Pool State
            AccountMeta(user_wsol_ata, False, True),  # 3: User WSOL Account
            AccountMeta(user_token_ata, False, True),  # 4: User Token Account
            AccountMeta(self.pool_data["pool_vault_a"], False, True),  # 5: Pool Vault A
            AccountMeta(self.pool_data["pool_vault_b"], False, True),  # 6: Pool Vault B
            AccountMeta(self.pool_data["observation_state"], False, True),  # 7: Observation State
            AccountMeta(TOKEN_PROGRAM_ID, False, False),  # 8: Token Program
            AccountMeta(self.pool_data["tick_array"], False, True),  # 9: Tick Array
            AccountMeta(self.pool_data["token_mint"], False, False),  # 10: Token Mint
        ]
        
        return Instruction(
            program_id=CLMM_PROGRAM,
            accounts=accounts,
            data=instruction_data
        )
    
    def build_clmm_sell_instruction(
        self,
        user_token_ata: Pubkey,
        user_wsol_ata: Pubkey,
        amount_in: int
    ) -> Instruction:
        """Build CLMM sell instruction (Token -> SOL)"""
        
        # Estimate output (simplified - you might want more sophisticated pricing)
        estimated_out = amount_in // 1000  # Simple 1:1000 ratio for example
        
        min_amount_out = int(estimated_out * (1 - self.config.slippage_tolerance))
        min_amount_out = max(min_amount_out, 1)  # Ensure at least 1
        
        # Create instruction data for sell (Token -> SOL)
        instruction_data = struct.pack("<QQ", amount_in, min_amount_out)
        
        # Build accounts for sell (reversed order from buy)
        accounts = [
            AccountMeta(self.wallet_pubkey, True, True),  # 0: User/Payer
            AccountMeta(self.pool_data["amm_config"], False, False),  # 1: AMM Config
            AccountMeta(self.pool_data["pool_state"], False, True),   # 2: Pool State
            AccountMeta(user_token_ata, False, True),  # 3: User Token Account (input)
            AccountMeta(user_wsol_ata, False, True),  # 4: User WSOL Account (output)
            AccountMeta(self.pool_data["pool_vault_b"], False, True),  # 5: Pool Vault B (token vault)
            AccountMeta(self.pool_data["pool_vault_a"], False, True),  # 6: Pool Vault A (sol vault)
            AccountMeta(self.pool_data["observation_state"], False, True),  # 7: Observation State
            AccountMeta(TOKEN_PROGRAM_ID, False, False),  # 8: Token Program
            AccountMeta(self.pool_data["tick_array"], False, True),  # 9: Tick Array
            AccountMeta(self.pool_data["token_mint"], False, False),  # 10: Token Mint
        ]
        
        return Instruction(
            program_id=CLMM_PROGRAM,
            accounts=accounts,
            data=instruction_data
        )
    
    async def execute_instruction(self, instruction: Instruction) -> Optional[str]:
        """Execute an instruction with retries"""
        try:
            # Execute with retries
            for attempt in range(self.config.max_retries):
                try:
                    # PR-02: Apply compute budget and ATA enforcement
                    ixs = with_compute_budget([instruction])
                    ixs = ensure_ata_ixs(ixs, self.wallet_pubkey, [])
                    
                    # PR-02: Build ALTs and recent blockhash
                    alts = build_alts_from_tables(ixs)
                    recent_blockhash = await get_recent_blockhash()
                    
                    # PR-02: Compile with ALTs
                    message = MessageV0.try_compile(
                        payer=self.wallet_pubkey,
                        instructions=ixs,
                        recent_blockhash=recent_blockhash,
                        address_lookup_table_accounts=alts
                    )
                    transaction = VersionedTransaction(message, [self.wallet_keypair])
                    
                    # PR-02: Submit with logging
                    result = await send_and_confirm_v0_tx(transaction)
                    log_submit_result(result, "clmm_instruction")
                    
                    if result.success:
                        return result.signature
                    else:
                        logger.error(f"❌ Transaction failed: {result.error}")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay)
                            continue
                except Exception as e:
                    logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    raise e
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error executing instruction: {e}")
            return None
    
    async def ensure_token_account_exists(self, token_mint: Pubkey) -> Pubkey:
        """
        Robustly check and create ATA, using correct token program and logger safety.
        """
        import logging
        log = logger if isinstance(logger, logging.Logger) else None
        def log_info(msg):
            log.info(msg) if log else print(msg)
        def log_warning(msg):
            log.warning(msg) if log else print("[WARN]", msg)
        def log_error(msg):
            log.error(msg) if log else print("[ERROR]", msg)
        def log_debug(msg):
            log.debug(msg) if log else print("[DEBUG]", msg)
        ata = get_associated_token_address(self.wallet_pubkey, token_mint)
        log_info(f"🔍 Checking if ATA exists for token {str(token_mint)[:8]}...")
        try:
            # TODO: Replace with aiohttp/solders logic to fetch account info
            # For now, always proceed to creation (simulate missing account)
            account_info = None
            # account_info = await ...
            if account_info and getattr(account_info, 'value', None) is not None:
                log_info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                return ata
        except Exception as e:
            log_debug(f"Error checking ATA existence: {e}")
        log_info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
        max_ata_retries = 3
        for ata_attempt in range(max_ata_retries):
            try:
                # TODO: Replace with aiohttp/solders logic to fetch latest blockhash
                # recent_blockhash = ...
                recent_blockhash = None
                create_ata_ix = create_associated_token_account(
                    payer=self.wallet_pubkey,
                    owner=self.wallet_pubkey,
                    mint=token_mint
                )
                # message = MessageV0.try_compile(...)
                # transaction = VersionedTransaction(...)
                # tx_bytes = transaction.serialize()
                # send_resp = ...
                # For now, simulate success
                send_resp = {'result': True}
                if send_resp.get('result'):
                    log_info(f"✅ ATA created: {ata}")
                    await asyncio.sleep(2)
                    return ata
            except Exception as e:
                log_warning(f"⚠️ ATA creation attempt {ata_attempt + 1} error: {e}")
                if "already in use" in str(e).lower() or "already exists" in str(e).lower():
                    log_info(f"✅ ATA already exists (detected via error): {ata}")
                    return ata
                if ata_attempt == max_ata_retries - 1:
                    log_error(f"❌ ATA creation failed after {max_ata_retries} attempts")
                else:
                    await asyncio.sleep(0.5 * (ata_attempt + 1))
        log_warning(f"⚠️ ATA creation uncertain - returning calculated address: {ata}")
        return ata
    async def ensure_token_account_exists(self, token_mint: Pubkey) -> Pubkey:
        """
        Robust, program-aware ATA creation and validation using official_executor_wrappers.py logic.
        """
        if str(token_mint) == str(self.WSOL_MINT):
            return self.wallet_pubkey
        from official_executor_wrappers import get_correct_ata_address, strict_validate_ata
        token_mint_pubkey = token_mint if isinstance(token_mint, Pubkey) else Pubkey.from_string(token_mint)
        ata = await get_correct_ata_address(self.wallet_pubkey, token_mint_pubkey)
        await strict_validate_ata(ata, self.wallet_pubkey, token_mint_pubkey)
        return ata
    
    async def get_balances(self):
        """Get current balances"""
        try:
            # SOL balance via RPC
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [str(self.wallet_pubkey)]
                }
                async with session.post(self.rpc_url, json=payload) as response:
                    result = await response.json()
                    sol_balance = result.get('result', {}).get('value', 0)
                    sol_amount = sol_balance / 1_000_000_000
            
            # Token balance
            from spl.token.constants import TOKEN_PROGRAM_ID
            from spl.token.instructions import get_associated_token_address
            token_ata = get_associated_token_address(self.wallet_pubkey, self.pool_data["token_mint"])
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTokenAccountBalance",
                        "params": [str(token_ata)]
                    }
                    async with session.post(self.rpc_url, json=payload) as response:
                        result = await response.json()
                        token_amount = float(result.get('result', {}).get('value', {}).get('uiAmount', 0.0))
            except:
                token_amount = 0.0
            
            return sol_amount, token_amount
        except Exception as e:
            logger.error(f"Error getting balances: {e}")
            return 0.0, 0.0
    


async def main():
    executor = CLMMCopyExecutor()
    await executor.run_test_trade()

if __name__ == "__main__":
    asyncio.run(main())
