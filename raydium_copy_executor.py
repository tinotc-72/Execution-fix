# --- Raydium LaunchLab/Launchpad Sell Executor ---
# --- Raydium CPMM Anchor IDL REQUIRED ---
# All swap instruction construction in this file must use the official Raydium CPMM Anchor IDL
# (discriminator and argument layout from the IDL, not hardcoded or reverse-engineered)

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
async def try_raydium_launchlab_sell(
    wallet_keypair: Keypair,
    payer: str,
    authority: str,
    global_config: str,
    platform_config: str,
    pool_state: str,
    user_base_token: str,
    user_quote_token: str,
    base_vault: str,
    quote_vault: str,
    base_token_mint: str,
    quote_token_mint: str,
    base_token_program: str,
    quote_token_program: str,
    event_authority: str,
    amount_in: int,
    minimum_amount_out: int,
    share_fee_rate: int = 0,
    **kwargs
) -> dict:
    """
    Execute a Raydium LaunchLab/Launchpad sell (swap base token for quote token, e.g. ACS for WSOL).
    Args: All required accounts and sell parameters.
    Returns: Dict with success, signature, error keys.
    """
    logger.info(f"🚀 Raydium LaunchLab Sell: {amount_in} base token for min {minimum_amount_out} quote token")
    try:
        from solders.instruction import Instruction, AccountMeta
        from solders.pubkey import Pubkey
        import struct

        # Prepare accounts in the exact order required by the program
        accounts = [
            AccountMeta(Pubkey.from_string(payer), True, True),
            AccountMeta(Pubkey.from_string(authority), False, False),
            AccountMeta(Pubkey.from_string(global_config), False, False),
            AccountMeta(Pubkey.from_string(platform_config), False, False),
            AccountMeta(Pubkey.from_string(pool_state), False, True),
            AccountMeta(Pubkey.from_string(user_base_token), False, True),
            AccountMeta(Pubkey.from_string(user_quote_token), False, True),
            AccountMeta(Pubkey.from_string(base_vault), False, True),
            AccountMeta(Pubkey.from_string(quote_vault), False, True),
            AccountMeta(Pubkey.from_string(base_token_mint), False, False),
            AccountMeta(Pubkey.from_string(quote_token_mint), False, False),
            AccountMeta(Pubkey.from_string(base_token_program), False, False),
            AccountMeta(Pubkey.from_string(quote_token_program), False, False),
            AccountMeta(Pubkey.from_string(event_authority), False, False),
            AccountMeta(Pubkey.from_string("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj"), False, False),
        ]

        # Instruction data: amount_in (u64), minimum_amount_out (u64), share_fee_rate (u64)
        instruction_data = struct.pack("<QQQ", amount_in, minimum_amount_out, share_fee_rate)

        instruction = Instruction(
            program_id=Pubkey.from_string("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj"),
            accounts=accounts,
            data=instruction_data
        )

        # --- Transaction creation, signing, and sending logic ---
        from solana.rpc.async_api import AsyncClient
        from solana.rpc.types import TxOpts
        from solders.transaction import Transaction
        import os
        
        # Use environment variable or default for RPC endpoint
        rpc_url = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        client = AsyncClient(rpc_url)
        
        # Build transaction
        tx = Transaction()
        tx.add(instruction)
        
        # Sign transaction
        tx.sign([wallet_keypair])
        
        # Send transaction
        try:
            response = await client.send_transaction(tx, wallet_keypair, opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
            await client.close()
            sig = response.value if hasattr(response, 'value') else response['result']
            logger.info(f"✅ Raydium LaunchLab sell sent: {sig}")
            return {"success": True, "signature": sig}
        except Exception as send_err:
            await client.close()
            logger.error(f"❌ Raydium LaunchLab sell send error: {send_err}")
            return {"success": False, "error": str(send_err)}
    except Exception as e:
        logger.error(f"Raydium LaunchLab sell error: {e}")
        return {"success": False, "error": str(e)}
# --- Raydium LaunchLab/Launchpad Buy Executor ---
import base64

LAUNCHLAB_PROGRAM_ID = Pubkey.from_string("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj")

async def try_raydium_launchlab_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> dict:
    """
    Execute a Raydium LaunchLab/Launchpad buy (swap WSOL for token).
    
    Based on successful transaction analysis:
    - Program: LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj
    - Instruction data: amount_in (u64), minimum_amount_out (u64), share_fee_rate (u64)
    - 15 accounts required in specific order
    
    Args:
        wallet_keypair: The wallet to use for trading
        token_mint: The token mint address to buy
        amount_sol: Amount of SOL to spend
        **kwargs: Additional parameters including pool info
    Returns:
        Dict with success, signature, error keys
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Raydium LaunchLab Buy: {amount_sol} SOL → {token_mint[:8]}...")
    
    try:
        from solders.instruction import Instruction, AccountMeta
        from solders.transaction import VersionedTransaction
        from solders.message import MessageV0
        # from solders.address_lookup_table import AddressLookupTableAccount  # Not needed for basic implementation
        import struct
        import asyncio
        
        # Convert amount to proper units
        amount_wsol = int(amount_sol * 1_000_000_000)  # Convert SOL to lamports
        
        # Calculate minimum out with slippage (5% slippage tolerance)
        # This would need proper calculation based on pool reserves
        minimum_amount_out = 1  # Placeholder - needs proper calculation
        share_fee_rate = 0      # As seen in the transaction
        
        # Get required accounts - these would need to be fetched/calculated
        # Based on the successful transaction structure:
        user_pubkey = wallet_keypair.pubkey()
        
        # Prepare accounts in the exact order required by the program (must be provided in kwargs)
        from solders.instruction import Instruction, AccountMeta
        accounts = [
            AccountMeta(Pubkey.from_string(kwargs['payer']), True, True),
            AccountMeta(Pubkey.from_string(kwargs['authority']), False, False),
            AccountMeta(Pubkey.from_string(kwargs['global_config']), False, False),
            AccountMeta(Pubkey.from_string(kwargs['platform_config']), False, False),
            AccountMeta(Pubkey.from_string(kwargs['pool_state']), False, True),
            AccountMeta(Pubkey.from_string(kwargs['user_base_token']), False, True),
            AccountMeta(Pubkey.from_string(kwargs['user_quote_token']), False, True),
            AccountMeta(Pubkey.from_string(kwargs['base_vault']), False, True),
            AccountMeta(Pubkey.from_string(kwargs['quote_vault']), False, True),
            AccountMeta(Pubkey.from_string(kwargs['base_token_mint']), False, False),
            AccountMeta(Pubkey.from_string(kwargs['quote_token_mint']), False, False),
            AccountMeta(Pubkey.from_string(kwargs['base_token_program']), False, False),
            AccountMeta(Pubkey.from_string(kwargs['quote_token_program']), False, False),
            AccountMeta(Pubkey.from_string(kwargs['event_authority']), False, False),
            AccountMeta(Pubkey.from_string("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj"), False, False),
        ]

        # Instruction data: amount_in (u64), minimum_amount_out (u64), share_fee_rate (u64)
        instruction_data = struct.pack("<QQQ", amount_wsol, minimum_amount_out, share_fee_rate)

        instruction = Instruction(
            program_id=Pubkey.from_string("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj"),
            accounts=accounts,
            data=instruction_data
        )

        # --- Transaction creation, signing, and sending logic ---
        from solana.rpc.async_api import AsyncClient
        from solana.rpc.types import TxOpts
        from solders.transaction import Transaction
        import os

        # Use environment variable or default for RPC endpoint
        rpc_url = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        client = AsyncClient(rpc_url)

        # Build transaction
        tx = Transaction()
        tx.add(instruction)

        # Sign transaction
        tx.sign([wallet_keypair])

        # Send transaction
        try:
            response = await client.send_transaction(tx, wallet_keypair, opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
            await client.close()
            sig = response.value if hasattr(response, 'value') else response['result']
            logger.info(f"✅ Raydium LaunchLab buy sent: {sig}")
            return {"success": True, "signature": sig}
        except Exception as send_err:
            await client.close()
            logger.error(f"❌ Raydium LaunchLab buy send error: {send_err}")
            return {"success": False, "error": str(send_err)}
        
    except Exception as e:
        logger.error(f"❌ Raydium LaunchLab buy error: {e}")
        return {"success": False, "error": str(e), "executor_type": "raydium_launchlab"}


"""
Raydium Copy Executor - Execute Raydium V4 AMM trades from extracted transaction data
Takes trade information from detected transactions and executes the same trade with your wallet
"""

import asyncio
import struct
import logging

import logging as _logging
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
    if isinstance(logger_candidate, _logging.Logger):
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
import aiohttp
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

# Remove redundant logger reassignment and duplicate DummyLogger definition

# Program IDs
RAYDIUM_V4_AMM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")

@dataclass
class CopyExecutorConfig:
    """Configuration for copy trade execution"""
    slippage_tolerance: float = 0.05  # 5% slippage tolerance
    max_retries: int = 2
    retry_delay: float = 0.5
    confirmation_timeout: float = 30.0
    compute_unit_limit: int = 200_000
    compute_unit_price: int = 1

@dataclass
class ExtractedRaydiumTradeInfo:
    """Information extracted from a detected Raydium transaction"""
    token_mint: str
    is_buy: bool  # True if SOL->Token, False if Token->SOL
    amount_in: int
    pool_info: Dict[str, str]  # All pool-related accounts
    original_signature: str
    wallet_address: str

class RaydiumCopyExecutor:
    """
    Raydium copy executor for executing the same trade as detected transactions
    Takes extracted trade information and builds/executes with your wallet
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: CopyExecutorConfig = None):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.client = None  # Placeholder for compatibility; use aiohttp for requests
        self.config = config or CopyExecutorConfig()
        # Common tokens
        self.USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        # Cache for pool addresses
        self.pool_cache = {}
        
    async def execute_copy_trade(self, trade_info: ExtractedRaydiumTradeInfo, copy_amount: Optional[float] = None, **kwargs) -> BuildResult:
        """
        Execute a copy trade based on extracted Raydium trade information
        copy_amount: Amount in SOL to use for the copy trade (overrides original amount for buys)
        Returns transaction signature if successful, None otherwise
        """
        try:
            logger.info(f"🔄 Executing Raydium copy trade: {trade_info.token_mint}")
            logger.info(f"   Trade type: {'BUY' if trade_info.is_buy else 'SELL'}")
            logger.info(f"   Original tx: {trade_info.original_signature}")
            logger.info(f"   Original wallet: {trade_info.wallet_address}")
            
            if trade_info.is_buy:
                # Use copy amount if provided, otherwise use original amount
                sol_amount = copy_amount if copy_amount else trade_info.amount_in / 1_000_000_000
                return await self.execute_buy_copy(trade_info, sol_amount)
            else:
                return await self.execute_sell_copy(trade_info, **kwargs)
                
        except Exception as e:
            logger.error(f"❌ Raydium copy trade execution error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="raydium",
                action="copy",
                reason=f"Raydium copy trade execution error: {e}"
            )
    
    async def execute_buy_copy(self, trade_info: ExtractedRaydiumTradeInfo, sol_amount: float) -> BuildResult:
        """Execute a buy copy trade on Raydium V4 AMM"""
        try:
            logger.info(f"🛒 Executing Raydium BUY copy: {sol_amount} SOL for {trade_info.token_mint}")
            
            # Convert to lamports
            amount_lamports = int(sol_amount * 1_000_000_000)
            
            # Get token mint
            token_mint = Pubkey.from_string(trade_info.token_mint)
            
            # Ensure token account exists (aggressive mode: log but do not abort)
            try:
                await self.ensure_token_account_exists(token_mint)
            except Exception as e:
                logger.warning(f"[AGGRESSIVE MODE] ATA check error: {e} - proceeding anyway!")
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, SOL_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Build swap instruction
            swap_instruction = self.build_raydium_swap_instruction(
                pool_info=trade_info.pool_info,
                user_input_token=user_wsol_ata,
                user_output_token=user_token_ata,
                amount_in=amount_lamports,
                is_buy=True
            )
            
            # Execute transaction
            signature = await self.execute_instruction(swap_instruction)
            
            if signature:
                logger.info(f"✅ Raydium buy copy executed: {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="raydium",
                    action="buy",
                    reason="Raydium buy copy completed"
                )
            else:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="raydium",
                    action="buy",
                    reason="Transaction failed"
                )
            
        except Exception as e:
            logger.error(f"❌ Raydium buy copy error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="raydium",
                action="buy",
                reason=f"Raydium buy copy error: {e}"
            )
    
    async def execute_sell_copy(self, trade_info: ExtractedRaydiumTradeInfo, **kwargs) -> BuildResult:
        """Execute a sell copy trade on Raydium V4 AMM"""
        try:
            logger.info(f"💸 Executing Raydium SELL copy: {trade_info.token_mint}")
            
            # Get token mint
            token_mint = Pubkey.from_string(trade_info.token_mint)
            
            # Get token balance
            token_balance = await self.get_token_balance(token_mint)
            
            if token_balance <= 0:
                logger.warning(f"[AGGRESSIVE MODE] No tokens to sell for {trade_info.token_mint} - still attempting sell!")
                # Proceed with attempt (may fail, but aggressive mode)
            
            # Use all available tokens for sell
            # Proportional sell calculation
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            if sell_percentage <= 0 or sell_percentage > 100.0:
                logger.warning(f"⚠️ Invalid sell_percentage {sell_percentage}, defaulting to 100%.")
                sell_percentage = 100.0
            
            # Calculate proportional amount to sell
            amount_to_sell = int(token_balance * (sell_percentage / 100.0))
            logger.info(f"🎯 PROPORTIONAL SELL:\n   Total balance: {token_balance} tokens\n   Amount to sell: {amount_to_sell} tokens\n   Sell percentage: {sell_percentage:.2f}%")
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, SOL_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Build swap instruction (reversed for sell)
            swap_instruction = self.build_raydium_swap_instruction(
                pool_info=trade_info.pool_info,
                user_input_token=user_token_ata,
                user_output_token=user_wsol_ata,
                amount_in=amount_to_sell,
                is_buy=False
            )
            
            # Execute transaction
            signature = await self.execute_instruction(swap_instruction)
            
            if signature:
                logger.info(f"✅ Raydium sell copy executed: {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="raydium",
                    action="sell",
                    reason="Raydium sell copy completed"
                )
            else:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="raydium",
                    action="sell",
                    reason="Transaction failed"
                )
            
        except Exception as e:
            logger.error(f"❌ Raydium sell copy error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="raydium",
                action="sell",
                reason=f"Raydium sell copy error: {e}"
            )
    
    def build_raydium_swap_instruction(
        self,
        pool_info: Dict[str, str],
        user_input_token: Pubkey,
        user_output_token: Pubkey,
        amount_in: int,
        is_buy: bool
    ) -> Instruction:
        """
        Build a Raydium CPMM swap instruction using the real Anchor IDL discriminator and argument layout.
        Uses swap_base_input for buy (SOL->Token) and swap_base_output for sell (Token->SOL).
        """
        # Convert pool info strings to Pubkeys
        pool_pubkeys = {key: Pubkey.from_string(value) for key, value in pool_info.items()}

        # Calculate minimum output with slippage
        if is_buy:
            # For SOL->Token: rough estimate
            estimated_out = amount_in * 1000  # Placeholder, should use pool reserves for real calc
        else:
            # For Token->SOL: rough estimate
            estimated_out = amount_in // 1000  # Placeholder

        min_amount_out = int(estimated_out * (1 - self.config.slippage_tolerance))
        min_amount_out = max(min_amount_out, 1)

        # Raydium CPMM program ID (from IDL)
        CPMM_PROGRAM_ID = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")

        # Discriminators from IDL
        SWAP_BASE_INPUT_DISCRIMINATOR = bytes([143, 190, 90, 218, 196, 30, 51, 222])
        SWAP_BASE_OUTPUT_DISCRIMINATOR = bytes([55, 217, 98, 86, 163, 74, 180, 173])

        # Instruction data layout: discriminator + args (all u64)
        if is_buy:
            # swap_base_input(amount_in, minimum_amount_out)
            data = SWAP_BASE_INPUT_DISCRIMINATOR + struct.pack("<QQ", amount_in, min_amount_out)
        else:
            # swap_base_output(max_amount_in, amount_out)
            # For sell, treat amount_in as max_amount_in, min_amount_out as amount_out
            data = SWAP_BASE_OUTPUT_DISCRIMINATOR + struct.pack("<QQ", amount_in, min_amount_out)

        # Build account metas according to IDL (see swap_base_input/swap_base_output)
        # Order: payer, authority, amm_config, pool_state, input_token_account, output_token_account,
        # input_vault, output_vault, input_token_program, output_token_program, input_token_mint, output_token_mint, observation_state
        accounts = [
            AccountMeta(self.wallet_pubkey, True, True),  # payer (signer)
            AccountMeta(pool_pubkeys["authority"], False, False),
            AccountMeta(pool_pubkeys["amm_config"], False, False),
            AccountMeta(pool_pubkeys["pool_state"], False, True),
            AccountMeta(user_input_token, False, True),
            AccountMeta(user_output_token, False, True),
            AccountMeta(pool_pubkeys["input_vault"], False, True),
            AccountMeta(pool_pubkeys["output_vault"], False, True),
            AccountMeta(pool_pubkeys["input_token_program"], False, False),
            AccountMeta(pool_pubkeys["output_token_program"], False, False),
            AccountMeta(pool_pubkeys["input_token_mint"], False, False),
            AccountMeta(pool_pubkeys["output_token_mint"], False, False),
            AccountMeta(pool_pubkeys["observation_state"], False, True),
        ]

        return Instruction(
            program_id=CPMM_PROGRAM_ID,
            accounts=accounts,
            data=data
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
                    log_submit_result(result, "raydium_instruction")
                    
                    if result.success:
                        return result.signature
                    else:
                        logger.error(f"❌ Transaction failed: {result.error}")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay)
                            continue
                            continue
                        return None
                    
                    # Send transaction using aiohttp-based RPC
                    import base64
                    tx_bytes = base64.b64encode(transaction.serialize()).decode("utf-8")
                    send_resp = await self._rpc_request("sendTransaction", [tx_bytes.hex(), {"encoding": "base64"}])
                    signature = send_resp.get('result')
                    if signature:
                        logger.info(f"✅ Transaction sent: {signature}")
                        return signature
                    
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)
                        
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
        ENHANCED: Check first, create only if needed - ELIMINATES IllegalOwner errors
        """
        from official_executor_wrappers import get_correct_ata_address, create_ata_ix
        # Get the correct ATA address (handles Token-2022 and legacy SPL)
        ata = await get_correct_ata_address(self.wallet_pubkey, token_mint)
        logger.info(f"🔍 Checking if ATA exists for token {str(token_mint)[:8]}...")
        try:
            account_info = await self._rpc_request("getAccountInfo", [str(ata), {"encoding": "jsonParsed"}])
            acc_val = account_info.get('result', {}).get('value')
            if acc_val is not None:
                logger.info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                return ata
        except Exception as e:
            logger.debug(f"Error checking ATA existence: {e}")
        logger.info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
        logger.info(f"🔨 Creating ATA for token: {token_mint}")
        try:
            # Use robust canonical ATA creation logic
            create_ata_ix_obj = await create_ata_ix(self.wallet_pubkey, token_mint, self.wallet_pubkey)
            recent_blockhash = await self._get_latest_blockhash()
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[
                    set_compute_unit_limit(self.config.compute_unit_limit),
                    set_compute_unit_price(self.config.compute_unit_price),
                    create_ata_ix_obj
                ],
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            import base64
            tx_bytes = base64.b64encode(transaction.serialize()).decode("utf-8")
            send_resp = await self._rpc_request("sendTransaction", [tx_bytes.hex(), {"encoding": "base64"}])
            if send_resp.get('result'):
                logger.info(f"✅ ATA created: {ata}")
                await asyncio.sleep(2)
            return ata
        except Exception as e:
            logger.error(f"Error creating ATA: {e}")
            return ata
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
            account_info = await self._rpc_request("getAccountInfo", [str(ata), {"encoding": "jsonParsed"}])
            acc_val = account_info.get('result', {}).get('value')
            if acc_val is not None:
                log_info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                return ata
        except Exception as e:
            log_debug(f"Error checking ATA existence: {e}")
        log_info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
        max_ata_retries = 3
        for ata_attempt in range(max_ata_retries):
            try:
                recent_blockhash = await self._get_latest_blockhash()
                create_ata_ix = create_associated_token_account(
                    payer=self.wallet_pubkey,
                    owner=self.wallet_pubkey,
                    mint=token_mint
                )
                message = MessageV0.try_compile(
                    payer=self.wallet_pubkey,
                    instructions=[
                        set_compute_unit_limit(self.config.compute_unit_limit),
                        set_compute_unit_price(self.config.compute_unit_price),
                        create_ata_ix
                    ],
                    recent_blockhash=recent_blockhash,
                    address_lookup_table_accounts=[]
                )
                transaction = VersionedTransaction(message, [self.wallet_keypair])
                import base64
                tx_bytes = base64.b64encode(transaction.serialize()).decode("utf-8")
                send_resp = await self._rpc_request("sendTransaction", [tx_bytes.hex(), {"encoding": "base64"}])
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
            ENHANCED: Check first, create only if needed - ELIMINATES IllegalOwner errors
            Defensive logger and robust retry/fallback logic.
            """
            # Logger helpers
            import logging
            log = None
            try:
                log = logger if isinstance(logger, logging.Logger) else None
            except Exception:
                pass
            def log_info(msg):
                if log:
                    log.info(msg)
                else:
                    print(msg)
            def log_warning(msg):
                if log:
                    log.warning(msg)
                else:
                    print("[WARN]", msg)
            def log_error(msg):
                if log:
                    log.error(msg)
                else:
                    print("[ERROR]", msg)
            def log_debug(msg):
                if log:
                    log.debug(msg)
                else:
                    print("[DEBUG]", msg)
            ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            log_info(f"🔍 Checking if ATA exists for token {str(token_mint)[:8]}...")
            try:
                account_info = await self._rpc_request("getAccountInfo", [str(ata), {"encoding": "jsonParsed"}])
                acc_val = account_info.get('result', {}).get('value')
                if acc_val is not None:
                    log_info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                    return ata
            except Exception as e:
                log_debug(f"Error checking ATA existence: {e}")
            log_info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
            max_ata_retries = 3
            for ata_attempt in range(max_ata_retries):
                try:
                    recent_blockhash = await self._get_latest_blockhash()
                    create_ata_ix = create_associated_token_account(
                        payer=self.wallet_pubkey,
                        owner=self.wallet_pubkey,
                        mint=token_mint
                    )
                    message = MessageV0.try_compile(
                        payer=self.wallet_pubkey,
                        instructions=[
                            set_compute_unit_limit(self.config.compute_unit_limit),
                            set_compute_unit_price(self.config.compute_unit_price),
                            create_ata_ix
                        ],
                        recent_blockhash=recent_blockhash,
                        address_lookup_table_accounts=[]
                    )
                    transaction = VersionedTransaction(message, [self.wallet_keypair])
                    import base64
                    tx_bytes = base64.b64encode(transaction.serialize()).decode("utf-8")
                    send_resp = await self._rpc_request("sendTransaction", [tx_bytes.hex(), {"encoding": "base64"}])
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
    
    async def get_sol_balance(self) -> float:
        """Get current SOL balance"""
        try:
            balance_resp = await self._rpc_request("getBalance", [str(self.wallet_pubkey)])
            lamports = balance_resp.get('result', {}).get('value', 0)
            return lamports / 1_000_000_000
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0
    
    async def get_token_balance(self, token_mint: Pubkey) -> int:
        """Get current token balance for a specific mint"""
        try:
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            balance_resp = await self._rpc_request("getTokenAccountBalance", [str(token_account)])
            amount = int(balance_resp.get('result', {}).get('value', {}).get('amount', 0))
            return amount
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0
    
    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with specified timeout"""
        try:
            for i in range(int(timeout)):
                try:
                    status = await self._rpc_request("getTransaction", [signature, {"maxSupportedTransactionVersion": 0}])
                    result = status.get('result')
                    if result:
                        meta = result.get('meta')
                        if meta and meta.get('err'):
                            logger.error(f"Transaction failed: {meta['err']}")
                            return False
                        else:
                            logger.info(f"✅ Transaction confirmed: {signature}")
                            return True
                except Exception:
                    pass
                await asyncio.sleep(1)
            logger.warning("⚠️ Transaction confirmation timeout")
            return False
        except Exception as e:
            logger.error(f"Error confirming transaction: {e}")
            return False
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()

# Standardized interface functions for copy bot integration

async def try_raydium_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> BuildResult:
    """
    Enhanced Raydium buy function with sophisticated validation and error handling
    Incorporates the robust logic from your original main.py
    
    Args:
        wallet_keypair: The wallet to use for trading
        token_mint: The token mint address to buy
        amount_sol: Amount of SOL to spend
        **kwargs: Additional parameters (pool_info, slippage_tolerance, etc.)
    
    Returns:
        Dict with success, signature, error keys
    """
    from rate_limit_manager import rate_limit_manager
    from env_keys import EnvKeys
    # ULTRA-AGGRESSIVE MODE: Skip validations for trusted wallet copy trading
    logger.info(f"🟣 Raydium Buy (Enhanced): {amount_sol} SOL → {token_mint[:8]}...")
    logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this token!")
    logger.info(f"💎 Raydium V4 AMM - Direct DEX execution!")
    # Unified SOL balance check and logging
    # Coordinator should check SOL balance before calling this executor
    # Enhanced retry logic with exponential backoff
    max_retries = kwargs.get('max_retries', 3)
    retry_delay = 0.5
    async def fetch_raydium_pool_info(token_mint: str):
        """Fetch Raydium pool info for a given token mint using the official Raydium API."""
        import aiohttp
        raydium_api = "https://api.raydium.io/v2/sdk/liquidity/mainnet.json"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(raydium_api) as resp:
                    data = await resp.json()
                    pools = data.get('official', []) + data.get('unOfficial', [])
                    for pool in pools:
                        if pool.get('baseMint') == token_mint or pool.get('quoteMint') == token_mint:
                            # Map Raydium API fields to expected pool_info keys
                            return {
                                'pool_id': pool.get('id'),
                                'amm_authority': pool.get('authority'),
                                'open_orders': pool.get('openOrders'),
                                'target_orders': pool.get('targetOrders'),
                                'base_vault': pool.get('baseVault'),
                                'quote_vault': pool.get('quoteVault'),
                                'serum_program': pool.get('serumProgramId'),
                                'market_id': pool.get('marketId'),
                                'market_bids': pool.get('marketBids'),
                                'market_asks': pool.get('marketAsks'),
                                'market_event_queue': pool.get('marketEventQueue'),
                                'market_base_vault': pool.get('marketBaseVault'),
                                'market_quote_vault': pool.get('marketQuoteVault'),
                                'market_authority': pool.get('marketAuthority'),
                            }
                    return None
        except Exception as e:
            logger.warning(f"Raydium pool info fetch failed: {e}")
            return None
    for attempt in range(max_retries):
        signature = None
        from env_keys import EnvKeys
        env_keys = EnvKeys()
        try:
            if attempt > 0:
                logger.info(f"🔄 Raydium retry attempt {attempt + 1}/{max_retries}")
                await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            # Check if we have pool_info, if not, try to discover it
            pool_info = kwargs.get('pool_info', {})
            if not pool_info or 'pool_id' not in pool_info:
                logger.info(f"🔍 No pool info provided - attempting pool discovery for {token_mint[:8]}...")
                pool_info = await fetch_raydium_pool_info(token_mint)
                if not pool_info or 'pool_id' not in pool_info:
                    logger.warning(f"⚠️ No Raydium pool found for {token_mint[:8]}...")
                    if attempt == max_retries - 1:
                        return {
                            'success': False,
                            'error': f'No Raydium pool found for {token_mint}',
                            'dex': 'Raydium',
                            'attempts': max_retries
                        }
                    continue
            # Initialize Raydium executor with enhanced config
            raydium_copy = RaydiumCopyExecutor(
                wallet_keypair=wallet_keypair,
                rpc_url=kwargs.get('rpc_url', env_keys.HELIUS_RPC_URL),
                config=CopyExecutorConfig(
                    slippage_tolerance=kwargs.get('slippage_tolerance', 0.30),  # 30% aggressive slippage
                    max_retries=1,  # Handle retries at this level
                    confirmation_timeout=kwargs.get('confirmation_timeout', 25.0),
                    compute_unit_limit=400_000,  # High compute units for AMM swaps
                    compute_unit_price=100  # High priority fee for speed
                )
            )
            # Create extracted trade info with discovered/provided pool info
            extracted_trade = ExtractedRaydiumTradeInfo(
                token_mint=token_mint,
                is_buy=True,
                amount_in=int(amount_sol * 1_000_000_000),  # Convert SOL to lamports
                pool_info=pool_info,
                original_signature=kwargs.get('original_signature', ''),
                wallet_address=str(wallet_keypair.pubkey())
            )
            # Execute buy with enhanced error handling
            signature = await raydium_copy.execute_buy_copy(extracted_trade)
            await raydium_copy.close()
            if signature and len(signature) > 10:  # Basic signature validation
                logger.info(f"✅ Raydium buy successful (attempt {attempt + 1}): {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="raydium",
                    action="buy",
                    reason=f"Raydium buy successful after {attempt + 1} attempts"
                )
            else:
                logger.warning(f"⚠️ Raydium attempt {attempt + 1} failed: invalid signature")
                if attempt == max_retries - 1:  # Last attempt
                    return BuildResult(
                        ok=False,
                        tx=None,
                        dex="raydium",
                        action="buy",
                        reason=f"Raydium buy failed after {max_retries} attempts - no valid signature"
                    )
        except Exception as attempt_error:
            logger.warning(f"⚠️ Raydium attempt {attempt + 1} error: {attempt_error}")
            if attempt == max_retries - 1:  # Last attempt
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="raydium",
                    action="buy",
                    reason=f"Raydium buy failed after {max_retries} attempts: {str(attempt_error)}"
                )
    # Should not reach here
    return BuildResult(
        ok=False,
        tx=None,
        dex="raydium",
        action="buy",
        reason="Raydium buy failed - unexpected execution path"
    )

async def try_raydium_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> BuildResult:
    """
    Standardized Raydium sell all function for copy bot integration
    
    Args:
        wallet_keypair: The wallet to use for trading
        token_mint: The token mint address to sell
        **kwargs: Additional parameters (pool_info, original_signature, etc.)
    
    Returns:
        Dict with success, signature, error keys
    """
    try:
        logger.info(f"🟣 Raydium Sell All: {token_mint}")
        
        # Initialize Raydium executor
        raydium_copy = RaydiumCopyExecutor(
            wallet_keypair=wallet_keypair,
            rpc_url=kwargs.get('rpc_url', "https://api.mainnet-beta.solana.com"),
            config=CopyExecutorConfig(
                slippage_tolerance=kwargs.get('slippage_tolerance', 0.05),
                max_retries=kwargs.get('max_retries', 2),
                confirmation_timeout=kwargs.get('confirmation_timeout', 30.0)
            )
        )
        
        # Get token balance using aiohttp
        import aiohttp
        from solders.pubkey import Pubkey
        async with aiohttp.ClientSession() as session:
            owner = str(wallet_keypair.pubkey())
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [owner, {"mint": token_mint}, {"encoding": "jsonParsed"}]
            }
            async with session.post(kwargs.get('rpc_url', "https://api.mainnet-beta.solana.com"), json=payload) as resp:
                result = await resp.json()
                accounts = result.get('result', {}).get('value', [])
                if not accounts:
                    await raydium_copy.close()
                    return {
                        'success': False,
                        'error': 'No token account found',
                        'dex': 'Raydium'
                    }
                token_account_info = accounts[0]['account']['data']['parsed']['info']['tokenAmount']
                token_amount = int(token_account_info.get('amount', 0))
                if token_amount == 0:
                    await raydium_copy.close()
                    return {
                        'success': False,
                        'error': 'No tokens to sell',
                        'dex': 'Raydium'
                    }
        
        # Create extracted trade info
        extracted_trade = ExtractedRaydiumTradeInfo(
            token_mint=token_mint,
            is_buy=False,
            amount_in=token_amount,
            pool_info=kwargs.get('pool_info', {}),
            original_signature=kwargs.get('original_signature', ''),
            wallet_address=kwargs.get('original_wallet', '')
        )
        
        # Execute sell
        signature = await raydium_copy.execute_copy_trade(extracted_trade, copy_amount=0)  # 0 for sell all
        
        await raydium_copy.close()
        
        if signature:
            logger.info(f"✅ Raydium sell successful: {signature}")
            return BuildResult(
                ok=True,
                tx=signature,
                dex="raydium",
                action="sell",
                reason="Raydium sell completed"
            )
        else:
            return BuildResult(
                ok=False,
                tx=None,
                dex="raydium",
                action="sell",
                reason="Raydium sell failed - no signature returned"
            )
            
    except Exception as e:
        logger.error(f"❌ Raydium sell error: {e}")
        return BuildResult(
            ok=False,
            tx=None,
            dex="raydium",
            action="sell",
            reason=str(e)
        )

# Example usage:
"""
from solders.keypair import Keypair

# Initialize the copy executor
raydium_copy = RaydiumCopyExecutor(
    wallet_keypair=your_wallet_keypair,
    rpc_url="https://api.mainnet-beta.solana.com",
    config=CopyExecutorConfig(
        slippage_tolerance=0.05,
        max_retries=2,
        confirmation_timeout=30.0
    )
)

# When you detect a Raydium trade from another wallet:
# Extract the trade information from the detected transaction
pool_info = {
    "pool_id": "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2",
    "amm_authority": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
    "open_orders": "HRk9CMrpq7Jn9sh7mzxE8CChHG2dGZyk6dwqnkirkein",
    "target_orders": "4UzK7Sgm84xQwr51rtygVuHUXZTjPrkJRfbDtw9AYUjg",
    "base_vault": "DQyrAcCrDXQ7NeoqGgDCZwBvWDcYmFCjSb9JtteuvPpz",
    "quote_vault": "HLmqeL62xR1QoZ1HKKbXRrdN1p3phKpxRMb2VVopvBBz",
    "serum_program": "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX",
    "market_id": "9wFFyRfZBsuAha4YcuxcXLKwMxJR43S7fPfQLusDBzvT",
    "market_bids": "14ivtgssEBoBjuZJtSAPKYWpuuttqKNDbbQMUQy9cDge",
    "market_asks": "CEQdAFKdycHugujQg9nDiNMRf2KwWb9jA9eCL6Btt2vV",
    "market_event_queue": "8CvwxZ9Db6XbLD46NZwwmVDZZRDy7eydFcAGkXKh9axa",
    "market_base_vault": "36c6YqAwyGKQG66XEp2dJc5JqjaBNv7sVghEtJv4c7u6",
    "market_quote_vault": "8CFo8bL8mZQK8abbFyypFMwEDd8tVJjHTTojMLgQTUSZ",
    "market_authority": "F8Vyqk3unwxkXukZFQeYyGmFfTG3CAX4v24iyrjEYBJV"
}

extracted_trade = ExtractedRaydiumTradeInfo(
    token_mint="token_mint_address",
    is_buy=True,
    amount_in=1000000,   # 0.001 SOL in lamports
    pool_info=pool_info,
    original_signature="detected_transaction_signature",
    wallet_address="wallet_you_are_copying"
)

# Execute the copy trade
signature = await raydium_copy.execute_copy_trade(extracted_trade, copy_amount=0.001)

# Confirm the transaction
if signature:
    confirmed = await raydium_copy.confirm_transaction(signature)
    if confirmed:
        print("✅ Copy trade confirmed!")

# Or use the standardized functions for copy bot integration:
# Buy tokens
result = await try_raydium_buy(wallet_keypair, "token_mint", 0.001)
if result['success']:
    print(f"Buy successful: {result['signature']}")

# Sell all tokens
result = await try_raydium_sell_all(wallet_keypair, "token_mint")
if result['success']:
    print(f"Sell successful: {result['signature']}")
"""
"""
from solders.keypair import Keypair

# Initialize the copy executor
raydium_copy = RaydiumCopyExecutor(
    wallet_keypair=your_wallet_keypair,
    rpc_url="https://api.mainnet-beta.solana.com",
    config=CopyExecutorConfig(
        slippage_tolerance=0.05,
        max_retries=2,
        confirmation_timeout=30.0
    )
)

# When you detect a Raydium trade from another wallet:
# Extract the trade information from the detected transaction
pool_info = {
    "pool_id": "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2",
    "amm_authority": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
    "open_orders": "HRk9CMrpq7Jn9sh7mzxE8CChHG2dGZyk6dwqnkirkein",
    "target_orders": "4UzK7Sgm84xQwr51rtygVuHUXZTjPrkJRfbDtw9AYUjg",
    "base_vault": "DQyrAcCrDXQ7NeoqGgDCZwBvWDcYmFCjSb9JtteuvPpz",
    "quote_vault": "HLmqeL62xR1QoZ1HKKbXRrdN1p3phKpxRMb2VVopvBBz",
    "serum_program": "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX",
    "market_id": "9wFFyRfZBsuAha4YcuxcXLKwMxJR43S7fPfQLusDBzvT",
    "market_bids": "14ivtgssEBoBjuZJtSAPKYWpuuttqKNDbbQMUQy9cDge",
    "market_asks": "CEQdAFKdycHugujQg9nDiNMRf2KwWb9jA9eCL6Btt2vV",
    "market_event_queue": "8CvwxZ9Db6XbLD46NZwwmVDZZRDy7eydFcAGkXKh9axa",
    "market_base_vault": "36c6YqAwyGKQG66XEp2dJc5JqjaBNv7sVghEtJv4c7u6",
    "market_quote_vault": "8CFo8bL8mZQK8abbFyypFMwEDd8tVJjHTTojMLgQTUSZ",
    "market_authority": "F8Vyqk3unwxkXukZFQeYyGmFfTG3CAX4v24iyrjEYBJV"
}

extracted_trade = ExtractedRaydiumTradeInfo(
    token_mint="token_mint_address",
    is_buy=True,
    amount_in=1000000,   # 0.001 SOL in lamports
    pool_info=pool_info,
    original_signature="detected_transaction_signature",
    wallet_address="wallet_you_are_copying"
)

# Execute the copy trade
signature = await raydium_copy.execute_copy_trade(extracted_trade, copy_amount=0.001)

# Confirm the transaction
if signature:
    confirmed = await raydium_copy.confirm_transaction(signature)
    if confirmed:
        print("✅ Copy trade confirmed!")
"""
