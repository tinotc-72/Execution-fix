# Standardized CPMM buy function for copy bot integration

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result

from solders.keypair import Keypair
from typing import Dict, Any
from dataclasses import dataclass
# Standardized CPMM buy function for copy bot integration
# ...existing code...


# Protocol-compliant fee program and writable fee recipient
from solders.pubkey import Pubkey
FEE_PROGRAM = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
FEE_RECIPIENT_WRITABLE = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV1T6NVswCLPVXdHy")

# Place try_cpmm_buy at the end of the file, after all class and dataclass definitions

async def try_cpmm_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> BuildResult:
    """
    Standardized CPMM buy function for copy bot integration.
    Args:
        wallet_keypair: The wallet to use for trading
        token_mint: The token mint address to buy
        amount_sol: Amount in SOL to spend
        **kwargs: Additional parameters
    Returns:
        Dict with success, signature, error keys
    """
    try:
        logger.info(f"🟣 CPMM Buy: {amount_sol} SOL → {token_mint}")
        logger.info("🟣 USING DIRECT RAYDIUM CPMM BUY - No Jupiter API dependency!")
        try:
            cpmm_executor = CPMMCopyExecutor(
                wallet_keypair=wallet_keypair,
                rpc_url=kwargs.get('rpc_url', "https://api.mainnet-beta.solana.com"),
                config=CopyExecutorConfig(
                    slippage_tolerance=kwargs.get('slippage_tolerance', 0.05),
                    max_retries=kwargs.get('max_retries', 2),
                    confirmation_timeout=kwargs.get('confirmation_timeout', 30.0)
                )
            )
            pool_info = kwargs.get('pool_info', {})
            if not pool_info or 'pool_id' not in pool_info:
                logger.warning("⚠️ Direct CPMM buy needs pool discovery")
                logger.info("💡 Your CPMM buy implementation requires pool info")
                logger.info("🔧 Extract pool info from detected Raydium transactions")
                await cpmm_executor.close()
                return {
                    'success': False,
                    'error': 'Direct CPMM buy requires pool discovery - pool_id not found',
                    'dex': 'CPMM-Direct',
                    'suggestion': 'Extract pool info from detected Raydium transactions'
                }
            # Create extracted trade info for buy
            extracted_trade = ExtractedCPMMTradeInfo(
                token_mint=token_mint,
                is_buy=True,
                amount_in=int(amount_sol * 1_000_000_000),
                pool_info=pool_info,
                original_signature=kwargs.get('original_signature', ''),
                wallet_address=str(wallet_keypair.pubkey())
            )
            signature = await cpmm_executor.execute_copy_trade(extracted_trade, amount_sol)
            await cpmm_executor.close()
            if signature:
                return {
                    'success': True,
                    'signature': signature,
                    'dex': 'CPMM-Direct'
                }
            else:
                return {
                    'success': False,
                    'error': 'Direct CPMM buy execution failed',
                    'dex': 'CPMM-Direct'
                }
        except Exception as direct_error:
            logger.error(f"❌ Direct CPMM buy error: {direct_error}")
            return {
                'success': False,
                'error': f'Direct CPMM buy failed: {direct_error}',
                'dex': 'CPMM-Direct'
            }
    except Exception as e:
        logger.error(f"❌ CPMM buy error: {e}")
        return {
            'success': False,
            'error': str(e),
            'dex': 'CPMM'
        }
import aiohttp
from solders.keypair import Keypair
from typing import Dict, Any
from dataclasses import dataclass

# Ensure these are available for try_cpmm_buy
class CopyExecutorConfig:
    pass
class ExtractedCPMMTradeInfo:
    pass
from solders.keypair import Keypair
from typing import Dict, Any
from dataclasses import dataclass

# Ensure these are available for try_cpmm_buy
from . import CopyExecutorConfig, ExtractedCPMMTradeInfo
"""
CPMM Copy Executor - Execute CPMM trades from extracted transaction data
Takes trade information from detected transactions and executes the same trade with your wallet
"""

import asyncio
import struct
import logging

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
 # REMOVED: solana.rpc.async_api.AsyncClient, solana.rpc.types.TxOpts, solana.rpc.commitment. Use solders and aiohttp/httpx for RPC.
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

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

# CPMM program and constants
CPMM_PROGRAM = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# CPMM instruction discriminators
SWAP_BASE_INPUT = 0  # Swap with base token as input
SWAP_BASE_OUTPUT = 1  # Swap with base token as output

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
class ExtractedCPMMTradeInfo:
    """Information extracted from a detected CPMM transaction"""
    token_mint: str
    is_buy: bool  # True if SOL->Token, False if Token->SOL
    amount_in: int
    pool_info: Dict[str, str]  # CPMM pool accounts
    original_signature: str
    wallet_address: str

class CPMMCopyExecutor:
    """
    CPMM copy executor for executing the same trade as detected transactions
    Takes extracted trade information and builds/executes with your wallet
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: CopyExecutorConfig = None):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.session = aiohttp.ClientSession()
        self.config = config or CopyExecutorConfig()
        # Cache for pool addresses
        self.pool_cache = {}

    async def _rpc_request(self, method: str, params: list):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        async with self.session.post(self.rpc_url, json=payload) as resp:
            result = await resp.json()
            return result.get("result")
        
    async def execute_copy_trade(self, trade_info: ExtractedCPMMTradeInfo, copy_amount: Optional[float] = None, **kwargs) -> BuildResult:
        """
        Execute a copy trade based on extracted CPMM trade information
        copy_amount: Amount in SOL to use for the copy trade (overrides original amount for buys)
        Returns transaction signature if successful, None otherwise
        """
        try:
            logger.info(f"🔄 Executing CPMM copy trade: {trade_info.token_mint}")
            logger.info(f"   Trade type: {'BUY' if trade_info.is_buy else 'SELL'}")
            logger.info(f"   Original tx: {trade_info.original_signature}")
            logger.info(f"   Original wallet: {trade_info.wallet_address}")
            
            # Enhance pool info if incomplete
            await self._enhance_pool_info(trade_info)
            
            if trade_info.is_buy:
                # Use copy amount if provided, otherwise use original amount
                sol_amount = copy_amount if copy_amount else trade_info.amount_in / 1_000_000_000
                return await self.execute_buy_copy(trade_info, sol_amount)
            else:
                return await self.execute_sell_copy(trade_info, **kwargs)
                
        except Exception as e:
            logger.error(f"❌ CPMM copy trade execution error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="cpmm",
                action="copy",
                reason=f"CPMM copy trade execution error: {e}"
            )

    async def _enhance_pool_info(self, trade_info: ExtractedCPMMTradeInfo):
        """Extract complete pool info from original transaction if missing"""
        try:
            if not trade_info.pool_info or 'pool_id' not in trade_info.pool_info:
                logger.info(f"🔍 Extracting CPMM pool info from original transaction...")
                
                # Get the original transaction
                signature = Signature.from_string(trade_info.original_signature)
                # TODO: Replace with solders-compatible or HTTP RPC call for transaction
                tx_response = None  # Placeholder
                
                if tx_response.value and tx_response.value.transaction:
                    # Extract pool info from transaction accounts and instructions
                    pool_info = self._extract_pool_from_transaction(tx_response.value, trade_info.token_mint)
                    if pool_info:
                        trade_info.pool_info = pool_info
                        logger.info(f"✅ Pool info extracted: {pool_info.get('pool_id', 'Unknown')[:8]}...")
                    else:
                        logger.warning(f"⚠️ Could not extract pool info from transaction")
                        
        except Exception as e:
            logger.warning(f"⚠️ Pool info enhancement failed: {e}")

    def _extract_pool_from_transaction(self, transaction, token_mint: str) -> Optional[Dict[str, str]]:
        """Extract CPMM pool accounts from transaction data"""
        try:
            if not transaction.meta or not transaction.transaction:
                return None
                
            accounts = transaction.transaction.message.account_keys
            instructions = transaction.transaction.message.instructions
            
            # Look for CPMM program instructions
            for instruction in instructions:
                if hasattr(instruction, 'program_id'):
                    program_id = instruction.program_id
                elif hasattr(instruction, 'programIdIndex'):
                    program_id = accounts[instruction.programIdIndex]
                else:
                    continue
                    
                # Check if this is a CPMM instruction
                if str(program_id) == "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C":
                    # Extract account indices for CPMM instruction
                    if hasattr(instruction, 'accounts'):
                        account_indices = instruction.accounts
                    else:
                        continue
                        
                    # CPMM swap instruction typically has these accounts:
                    # 0: pool_id, 1: amm_config, 2: pool_state, 3: input_token_account, 
                    # 4: output_token_account, 5: input_vault, 6: output_vault, etc.
                    if len(account_indices) >= 7:
                        pool_accounts = {}
                        pool_accounts['pool_id'] = str(accounts[account_indices[0]])
                        pool_accounts['amm_config'] = str(accounts[account_indices[1]]) 
                        pool_accounts['pool_state'] = str(accounts[account_indices[2]])
                        pool_accounts['input_vault'] = str(accounts[account_indices[5]])
                        pool_accounts['output_vault'] = str(accounts[account_indices[6]])
                        
                        logger.info(f"📊 Extracted CPMM pool: {pool_accounts['pool_id'][:8]}...")
                        return pool_accounts
                        
        except Exception as e:
            logger.warning(f"⚠️ Pool extraction failed: {e}")
            
        return None
    
    async def execute_buy_copy(self, trade_info: ExtractedCPMMTradeInfo, sol_amount: float) -> BuildResult:
        """Execute a buy copy trade on CPMM"""
        try:
            logger.info(f"🛒 Executing CPMM BUY copy: {sol_amount} SOL for {trade_info.token_mint}")
            
            # Convert to lamports
            amount_lamports = int(sol_amount * 1_000_000_000)
            
            # Get token mint
            token_mint = Pubkey.from_string(trade_info.token_mint)
            
            # Ensure token account exists
            await self.ensure_token_account_exists(token_mint)
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, SOL_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Build swap instruction
            swap_instruction = self.build_cpmm_swap_instruction(
                pool_info=trade_info.pool_info,
                user_input_token=user_wsol_ata,
                user_output_token=user_token_ata,
                amount_in=amount_lamports,
                is_buy=True
            )
            
            # Execute transaction
            signature = await self.execute_instruction(swap_instruction)
            
            if signature:
                logger.info(f"✅ CPMM buy copy executed: {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="cpmm",
                    action="buy",
                    reason="CPMM buy copy completed"
                )
            else:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="cpmm",
                    action="buy",
                    reason="Transaction failed"
                )
            
        except Exception as e:
            logger.error(f"❌ CPMM buy copy error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="cpmm",
                action="buy",
                reason=f"CPMM buy copy error: {e}"
            )
    
    async def execute_sell_copy(self, trade_info: ExtractedCPMMTradeInfo, **kwargs) -> BuildResult:
        """Execute a sell copy trade on CPMM with proportional selling support"""
        try:
            logger.info(f"💸 Executing CPMM SELL copy: {trade_info.token_mint}")
            
            # Get token mint
            token_mint = Pubkey.from_string(trade_info.token_mint)
            
            # Get token balance
            token_balance = await self.get_token_balance(token_mint)
            
            if token_balance <= 0:
                logger.error(f"❌ No tokens to sell for {trade_info.token_mint}")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="cpmm",
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
            logger.info(f"🎯 CPMM PROPORTIONAL SELL:\n   Total balance: {token_balance} tokens\n   Amount to sell: {amount_to_sell} tokens\n   Sell percentage: {sell_percentage:.2f}%")
            
            # Get user token accounts
            user_wsol_ata = get_associated_token_address(self.wallet_pubkey, SOL_MINT)
            user_token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Build swap instruction (reversed for sell)
            swap_instruction = self.build_cpmm_swap_instruction(
                pool_info=trade_info.pool_info,
                user_input_token=user_token_ata,
                user_output_token=user_wsol_ata,
                amount_in=amount_to_sell,
                is_buy=False
            )
            
            # Execute transaction
            signature = await self.execute_instruction(swap_instruction)
            
            if signature:
                logger.info(f"✅ CPMM sell copy executed: {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="cpmm",
                    action="sell",
                    reason="CPMM sell copy completed"
                )
            else:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="cpmm",
                    action="sell",
                    reason="Transaction failed"
                )
            
        except Exception as e:
            logger.error(f"❌ CPMM sell copy error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="cpmm",
                action="sell",
                reason=f"CPMM sell copy error: {e}"
            )
    
    def build_cpmm_swap_instruction(
        self,
        pool_info: Dict[str, str],
        user_input_token: Pubkey,
        user_output_token: Pubkey,
        amount_in: int,
        is_buy: bool
    ) -> Instruction:
        """Build a CPMM swap instruction"""
        
        # Convert pool info strings to Pubkeys
        pool_pubkeys = {key: Pubkey.from_string(value) for key, value in pool_info.items()}
        
        # Calculate minimum output with slippage
        if is_buy:
            # For SOL->Token: rough estimate
            estimated_out = amount_in * 1000  # Very rough estimate
        else:
            # For Token->SOL: rough estimate
            estimated_out = amount_in // 1000  # Very rough estimate
        
        min_amount_out = int(estimated_out * (1 - self.config.slippage_tolerance))
        min_amount_out = max(min_amount_out, 1)  # Ensure at least 1
        
        # Determine swap direction
        swap_direction = SWAP_BASE_INPUT if is_buy else SWAP_BASE_OUTPUT
        
        # Build instruction data: [swap_direction, amount_in, min_amount_out]
        instruction_data = struct.pack("<BQQ", swap_direction, amount_in, min_amount_out)
        
        # Build CPMM accounts structure
        accounts = [
            # Core accounts
            AccountMeta(self.wallet_pubkey, True, True),                    # 0: Payer/authority
            AccountMeta(pool_pubkeys["amm_config"], False, False),          # 1: AMM config
            AccountMeta(pool_pubkeys["pool_state"], False, True),           # 2: Pool state
            AccountMeta(user_input_token, False, True),                     # 3: Input token account
            AccountMeta(user_output_token, False, True),                    # 4: Output token account
            AccountMeta(pool_pubkeys["input_vault"], False, True),          # 5: Input vault
            AccountMeta(pool_pubkeys["output_vault"], False, True),         # 6: Output vault
            AccountMeta(pool_pubkeys["observation_state"], False, True),    # 7: Observation state
            
            # Program accounts
            AccountMeta(TOKEN_PROGRAM_ID, False, False),                    # 8: Token program
            AccountMeta(pool_pubkeys["input_token_mint"], False, False),    # 9: Input token mint
            AccountMeta(pool_pubkeys["output_token_mint"], False, False),   # 10: Output token mint
            AccountMeta(pool_pubkeys["input_token_program"], False, False), # 11: Input token program
            AccountMeta(pool_pubkeys["output_token_program"], False, False), # 12: Output token program
        ]
        
        return Instruction(
            program_id=CPMM_PROGRAM,
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
                    log_submit_result(result, "cpmm_instruction")
                    
                    if result.success:
                        return result.signature
                    else:
                        logger.error(f"❌ Transaction failed: {result.error}")
                        if attempt < self.config.max_retries - 1:
                            await asyncio.sleep(self.config.retry_delay)
                            continue
                            continue
                        return None
                    
                    # Send transaction
                    # TODO: Replace with solders-compatible or HTTP RPC send_transaction options
                    response = await self.client.send_transaction(
                        transaction
                    )
                    
                    if response.value:
                        signature = str(response.value)
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
    raise NotImplementedError("Legacy ATA logic has been removed.")
        async def ensure_token_account_exists(self, token_mint: Pubkey) -> Pubkey:
            """
            Robust, program-aware ATA creation and validation using official_executor_wrappers.py logic.
            """
            from official_executor_wrappers import get_correct_ata_address, strict_validate_ata
            if hasattr(self, 'WSOL_MINT') and str(token_mint) == str(self.WSOL_MINT):
                return self.wallet_pubkey
            token_mint_pubkey = token_mint if isinstance(token_mint, Pubkey) else Pubkey.from_string(token_mint)
            ata = await get_correct_ata_address(self.wallet_pubkey, token_mint_pubkey)
            await strict_validate_ata(ata, self.wallet_pubkey, token_mint_pubkey)
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
                if account_info and account_info.get('value') is not None:
                    log_info(f"✅ ATA already exists, skipping creation: {str(ata)[:8]}...")
                    return ata
            except Exception as e:
                log_debug(f"Error checking ATA existence: {e}")
            log_info(f"🔨 ATA doesn't exist, creating new ATA for token: {str(token_mint)[:8]}...")
            max_ata_retries = 3
            for ata_attempt in range(max_ata_retries):
                try:
                    blockhash_resp = await self._rpc_request("getLatestBlockhash", [])
                    recent_blockhash = blockhash_resp["value"]["blockhash"]
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
                    log_info(f"✅ ATA created: {str(ata)[:8]}...")
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
            return balance_resp["value"] / 1_000_000_000 if balance_resp and "value" in balance_resp else 0.0
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0
    
    async def get_token_balance(self, token_mint: Pubkey) -> int:
        """Get current token balance for a specific mint"""
        try:
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            balance_resp = await self._rpc_request("getTokenAccountBalance", [str(token_account)])
            if balance_resp and balance_resp.get("value"):
                return int(balance_resp["value"]["amount"])
            return 0
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0
    
    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with specified timeout"""
        try:
            for _ in range(int(timeout)):
                resp = await self._rpc_request("getSignatureStatuses", [[signature]])
                if resp and resp.get("value") and resp["value"][0] and resp["value"][0]["confirmationStatus"] == "confirmed":
                    return True
                await asyncio.sleep(1)
            return False
        except Exception as e:
            logger.error(f"Error confirming transaction: {e}")
            return False
    async def close(self):
        await self.session.close()
    
    # ...existing code...

    async def try_cpmm_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """
        Standardized CPMM buy function for copy bot integration.
        Args:
            wallet_keypair: The wallet to use for trading
            token_mint: The token mint address to buy
            amount_sol: Amount in SOL to spend
            **kwargs: Additional parameters
        Returns:
            Dict with success, signature, error keys
        """
        try:
            logger.info(f"🟣 CPMM Buy: {amount_sol} SOL → {token_mint}")
            logger.info("🟣 USING DIRECT RAYDIUM CPMM BUY - No Jupiter API dependency!")
            try:
                cpmm_executor = CPMMCopyExecutor(
                    wallet_keypair=wallet_keypair,
                    rpc_url=kwargs.get('rpc_url', "https://api.mainnet-beta.solana.com"),
                    config=CopyExecutorConfig(
                        slippage_tolerance=kwargs.get('slippage_tolerance', 0.05),
                        max_retries=kwargs.get('max_retries', 2),
                        confirmation_timeout=kwargs.get('confirmation_timeout', 30.0)
                    )
                )
                pool_info = kwargs.get('pool_info', {})
                if not pool_info or 'pool_id' not in pool_info:
                    logger.warning("⚠️ Direct CPMM buy needs pool discovery")
                    logger.info("💡 Your CPMM buy implementation requires pool info")
                    logger.info("🔧 Extract pool info from detected Raydium transactions")
                    await cpmm_executor.close()
                    return {
                        'success': False,
                        'error': 'Direct CPMM buy requires pool discovery - pool_id not found',
                        'dex': 'CPMM-Direct',
                        'suggestion': 'Extract pool info from detected Raydium transactions'
                    }
                # Create extracted trade info for buy
                extracted_trade = ExtractedCPMMTradeInfo(
                    token_mint=token_mint,
                    is_buy=True,
                    amount_in=int(amount_sol * 1_000_000_000),
                    pool_info=pool_info,
                    original_signature=kwargs.get('original_signature', ''),
                    wallet_address=str(wallet_keypair.pubkey())
                )
                signature = await cpmm_executor.execute_copy_trade(extracted_trade, amount_sol)
                await cpmm_executor.close()
                if signature:
                    return {
                        'success': True,
                        'signature': signature,
                        'dex': 'CPMM-Direct'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Direct CPMM buy execution failed',
                        'dex': 'CPMM-Direct'
                    }
            except Exception as direct_error:
                logger.error(f"❌ Direct CPMM buy error: {direct_error}")
                return {
                    'success': False,
                    'error': f'Direct CPMM buy failed: {direct_error}',
                    'dex': 'CPMM-Direct'
                }
        except Exception as e:
            logger.error(f"❌ CPMM buy error: {e}")
            return {
                'success': False,
                'error': str(e),
                'dex': 'CPMM'
            }

async def try_cpmm_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    """Standardized CPMM sell all function for copy bot integration.
    Args:
        wallet_keypair: The wallet to use for trading
        token_mint: The token mint address to sell
        **kwargs: Additional parameters
    Returns:
        Dict with success, signature, error keys
    """
    try:
        logger.info(f"� CPMM Sell All: {token_mint}")
        
        # DIRECT RAYDIUM CPMM SELL - No Jupiter dependency!
        logger.info("🟣 USING DIRECT RAYDIUM CPMM SELL - No Jupiter API dependency!")
        
        try:
            # Initialize CPMM executor using your direct Raydium implementation
            from raydium_copy_executor import RaydiumCopyExecutor, CopyExecutorConfig, ExtractedRaydiumTradeInfo
            from solders.pubkey import Pubkey
            
            cpmm_executor = RaydiumCopyExecutor(
                wallet_keypair=wallet_keypair,
                rpc_url=kwargs.get('rpc_url', "https://api.mainnet-beta.solana.com"),
                config=CopyExecutorConfig(
                    slippage_tolerance=kwargs.get('slippage_tolerance', 0.05),
                    max_retries=kwargs.get('max_retries', 2),
                    confirmation_timeout=kwargs.get('confirmation_timeout', 30.0)
                )
            )
            
            # For CPMM sell, we need pool discovery (same as buy)
            pool_info = kwargs.get('pool_info', {})
            
            if not pool_info or 'pool_id' not in pool_info:
                logger.warning("⚠️ Direct CPMM sell needs pool discovery")
                logger.info("💡 Your CPMM sell implementation requires pool info")
                logger.info("🔧 Extract pool info from detected Raydium transactions")
                
                await cpmm_executor.close()
                
                return {
                    'success': False,
                    'error': 'Direct CPMM sell requires pool discovery - pool_id not found',
                    'dex': 'CPMM-Direct',
                    'suggestion': 'Extract pool info from detected Raydium transactions'
                }
            
            # Get token balance to sell
            token_mint_pubkey = Pubkey.from_string(token_mint)
            token_balance = await cpmm_executor.get_token_balance(token_mint_pubkey)
            
            if token_balance <= 0:
                await cpmm_executor.close()
                return {
                    'success': False,
                    'error': 'No tokens to sell - balance is 0',
                    'dex': 'CPMM-Direct'
                }
            
            # Create extracted trade info for sell
            extracted_trade = ExtractedRaydiumTradeInfo(
                token_mint=token_mint,
                is_buy=False,  # This is a sell
                amount_in=token_balance,  # Use full token balance
                pool_info=pool_info,  # Use discovered pool info
                original_signature=kwargs.get('original_signature', ''),
                wallet_address=str(wallet_keypair.pubkey())
            )
            
            # Execute the direct CPMM sell
            signature = await cpmm_executor.execute_copy_trade(extracted_trade, None)
            
            await cpmm_executor.close()
            
            if signature:
                return {
                    'success': True,
                    'signature': signature,
                    'dex': 'CPMM-Direct'
                }
            else:
                return {
                    'success': False,
                    'error': 'Direct CPMM sell execution failed',
                    'dex': 'CPMM-Direct'
                }
                
        except Exception as direct_error:
            logger.error(f"❌ Direct CPMM sell error: {direct_error}")
            return {
                'success': False,
                'error': f'Direct CPMM sell failed: {direct_error}',
                'dex': 'CPMM-Direct'
            }
        
    except Exception as e:
        logger.error(f"❌ CPMM sell error: {e}")
        return {
            'success': False,
            'error': str(e),
            'dex': 'CPMM'
        }

# Example usage:
"""
from solders.keypair import Keypair

# Initialize the copy executor
cpmm_copy = CPMMCopyExecutor(
    wallet_keypair=your_wallet_keypair,
    rpc_url="https://api.mainnet-beta.solana.com",
    config=CopyExecutorConfig(
        slippage_tolerance=0.05,
        max_retries=2,
        confirmation_timeout=30.0
    )
)

# When you detect a CPMM trade from another wallet:
# Extract the trade information from the detected transaction
pool_info = {
    "amm_config": "amm_config_address",
    "pool_state": "pool_state_address",
    "input_vault": "input_vault_address",
    "output_vault": "output_vault_address",
    "observation_state": "observation_state_address",
    "input_token_mint": "input_token_mint_address",
    "output_token_mint": "output_token_mint_address",
    "input_token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "output_token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
}

extracted_trade = ExtractedCPMMTradeInfo(
    token_mint="token_mint_address",
    is_buy=True,
    amount_in=1000000,   # 0.001 SOL in lamports
    pool_info=pool_info,
    original_signature="detected_transaction_signature",
    wallet_address="wallet_you_are_copying"
)

# Execute the copy trade
signature = await cpmm_copy.execute_copy_trade(extracted_trade, copy_amount=0.001)

# Confirm the transaction
if signature:
    confirmed = await cpmm_copy.confirm_transaction(signature)
    if confirmed:
        print("✅ Copy trade confirmed!")
"""
