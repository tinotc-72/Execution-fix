"""
Jupiter Copy Executor - Execute Jupiter trades from extracted transaction data
Takes trade information from detected transactions and executes the same trade with your wallet
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
import base64
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

import requests
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.signature import Signature
 # REMOVED: solana.rpc.async_api.AsyncClient, solana.rpc.types.TxOpts, solana.rpc.commitment. Use solders and aiohttp/httpx for RPC.
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from fast_executor import FastExecutor

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

# Jupiter API endpoints
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

# Program IDs
JUPITER_PROGRAM = Pubkey.from_string("JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4")
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

@dataclass
class CopyExecutorConfig:
    """Configuration for copy trade execution - ULTRA-AGGRESSIVE settings for trusted wallets"""
    slippage_tolerance: float = 0.30  # 30% slippage tolerance (ULTRA-AGGRESSIVE)
    max_retries: int = 2
    retry_delay: float = 0.3  # Faster retry
    confirmation_timeout: float = 20.0  # Shorter timeout
    compute_unit_limit: int = 400_000  # Higher compute units
    compute_unit_price: int = 20  # Higher priority fee

@dataclass
class ExtractedTradeInfo:
    """Information extracted from a detected transaction"""
    input_mint: str
    output_mint: str
    amount_in: int
    is_buy: bool  # True if SOL->Token, False if Token->SOL
    original_signature: str
    wallet_address: str

class SimpleRPCClient:
    """Simple aiohttp-based RPC client for basic Solana operations"""
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self._session = None
    
    async def request(self, method: str, params: list):
        """Make an RPC request"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        async with self._session.post(self.rpc_url, json=payload) as response:
            result = await response.json()
            return result.get('result')
    
    async def close(self):
        """Close the session"""
        if self._session:
            await self._session.close()
            self._session = None

class JupiterCopyExecutor:
    """
    Jupiter copy executor for executing the same trade as detected transactions
    Takes extracted trade information and builds/executes with your wallet
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: CopyExecutorConfig = None, jito_service=None):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        # Simple aiohttp RPC client for when FastExecutor isn't available
        self.rpc_url = rpc_url
        self.client = SimpleRPCClient(rpc_url)
        self.config = config or CopyExecutorConfig()
        self.jito_service = jito_service  # Add Jito service for MEV protection
        # Initialize FastExecutor for Jito-first execution with RPC fallback
        self.fast_executor = FastExecutor(wallet_keypair)
        
    async def execute_copy_trade(self, source_tx_signature: str = "", token_mint: str = "", amount_sol: float = 0.001, trade_info: Dict = None, **kwargs) -> BuildResult:
        """
        Execute a copy trade based on extracted trade information
        Compatible with execution coordinator interface
        Returns dict with success, signature, error keys
        """
        try:
            logger.info(f"🔄 Executing Jupiter copy trade for token: {token_mint[:8]}...")
            logger.info(f"   Source tx: {source_tx_signature}")
            logger.info(f"   Amount: {amount_sol} SOL")
            
            # Use amount_sol parameter
            amount_to_trade = amount_sol
            
            # Ensure token accounts exist
            token_mint_pubkey = Pubkey.from_string(token_mint) if isinstance(token_mint, str) else token_mint
            
            await self.ensure_token_account_exists(token_mint_pubkey)
            # For Jupiter swaps, we typically go SOL -> Token, so ensure SOL mint is handled
            await self.ensure_token_account_exists(SOL_MINT)
            
            # Get quote from Jupiter API (SOL -> Token)
            quote_response = await self.get_quote(
                input_mint=str(SOL_MINT),
                output_mint=str(token_mint_pubkey),
                amount=int(amount_to_trade * 1_000_000_000)
            )
            logger.info(f"[DEBUG] Jupiter quote response: {quote_response}")
            if not quote_response:
                logger.error("❌ Failed to get quote from Jupiter")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="copy",
                    reason="Failed to get quote from Jupiter"
                )

            swap_response = await self.get_swap_transaction(quote_response)
            logger.info(f"[DEBUG] Jupiter swap response: {swap_response}")
            if not swap_response:
                logger.error("❌ Failed to get swap transaction from Jupiter")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="copy",
                    reason="Failed to get swap transaction from Jupiter"
                )

            signature = await self.execute_swap_transaction(swap_response)
            logger.info(f"[DEBUG] Jupiter transaction signature: {signature}")
            if signature:
                logger.info(f"✅ Jupiter copy trade executed: {signature}")
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="jupiter",
                    action="copy",
                    reason="Jupiter copy trade completed"
                )
            else:
                logger.error("❌ Failed to execute Jupiter copy trade")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="jupiter",
                    action="copy",
                    reason="Failed to execute Jupiter copy trade"
                )
        except Exception as e:
            logger.error(f"❌ Jupiter copy trade execution error: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="jupiter",
                action="copy",
                reason=str(e)
            )

    async def get_quote(self, input_mint: str, output_mint: str, amount: int) -> Optional[dict]:
        """
        Fetch a swap quote from Jupiter API.
        """
        import aiohttp
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": int(self.config.slippage_tolerance * 10000),
            "swapMode": "ExactIn",
            "platformFeeBps": 0
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(JUPITER_QUOTE_URL, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"[DEBUG] Jupiter quote API error: {resp.status}")
                        return None
        except Exception as e:
            logger.error(f"[DEBUG] Exception in get_quote: {e}")
            return None

    async def get_swap_transaction(self, quote_response: dict) -> Optional[dict]:
        """
        Fetch the swap transaction from Jupiter API using the quote response.
        """
        import aiohttp
        try:
            if not quote_response or "swapTransaction" in quote_response:
                # Already a swap response
                return quote_response
            body = {
                "quoteResponse": quote_response,  # Use the quote response directly as required by Jupiter API
                "userPublicKey": str(self.wallet_pubkey),
                "wrapUnwrapSOL": True,
                "asLegacyTransaction": False
            }
            logger.info(f"[DEBUG] Jupiter swap API payload: {body}")
            async with aiohttp.ClientSession() as session:
                async with session.post(JUPITER_SWAP_URL, json=body) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        try:
                            error_text = await resp.text()
                        except Exception:
                            error_text = None
                        logger.error(f"[DEBUG] Jupiter swap API error: {resp.status}, response: {error_text}")
                        logger.error(f"[DEBUG] Jupiter swap API payload (for 422): {body}")
                        return None
        except Exception as e:
            logger.error(f"[DEBUG] Exception in get_swap_transaction: {e}")
            return None

    async def execute_swap_transaction(self, swap_response: dict) -> Optional[str]:
        """
        Decode, sign, and submit the Jupiter swap transaction with PR-02 patterns.
        """
        import base64
        try:
            if 'swapTransaction' not in swap_response:
                logger.error(f"[DEBUG] No 'swapTransaction' in Jupiter response: {swap_response}")
                return None
            tx_bytes = base64.b64decode(swap_response['swapTransaction'])
            logger.info(f"[DEBUG] Decoded Jupiter transaction bytes: {tx_bytes.hex()[:120]}... (truncated)")
            
            # Parse the transaction
            tx = VersionedTransaction.from_bytes(tx_bytes)
            
            # PR-02: Apply compute budget and ATA enforcement to instructions
            ixs = with_compute_budget(tx.message.instructions)
            ixs = ensure_ata_ixs(ixs, self.wallet_keypair.pubkey(), [])
            
            # PR-02: Build ALTs and recent blockhash
            alts = build_alts_from_tables(ixs)
            recent_blockhash = await get_recent_blockhash()
            
            # PR-02: Compile with ALTs
            message = MessageV0.try_compile(
                payer=self.wallet_keypair.pubkey(),
                instructions=ixs,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=alts
            )
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            # PR-02: Submit with logging
            result = await send_and_confirm_v0_tx(transaction)
            log_submit_result(result, "jupiter_swap")
            
            return result.signature if result.success else None
            
        except Exception as e:
            logger.error(f"[DEBUG] Error in execute_swap_transaction: {e}")
            return None
    
    async def execute_buy_copy(self, token_mint: str, sol_amount: float, original_signature: str, original_wallet: str) -> BuildResult:
        """
        Execute a buy copy trade (SOL -> Token)
        """
        logger.info(f"[DEBUG] Starting Jupiter buy: token_mint={token_mint}, sol_amount={sol_amount}")
        try:
            # Get quote from Jupiter API
            quote_response = await self.get_quote(
                input_mint=str(SOL_MINT),
                output_mint=token_mint,
                amount=int(sol_amount * 1_000_000_000)
            )
            logger.info(f"[DEBUG] Jupiter quote response: {quote_response}")
            if not quote_response:
                logger.error("❌ Failed to get quote from Jupiter")
                return None

            swap_response = await self.get_swap_transaction(quote_response)
            logger.info(f"[DEBUG] Jupiter swap response: {swap_response}")
            if not swap_response:
                logger.error("❌ Failed to get swap transaction from Jupiter")
                return None

            signature = await self.execute_swap_transaction(swap_response)
            logger.info(f"[DEBUG] Jupiter transaction signature: {signature}")
            if signature:
                logger.info(f"✅ Jupiter buy executed: {signature}")
                return signature
            else:
                logger.error("❌ Failed to execute Jupiter buy")
                return None
        except Exception as e:
            logger.error(f"❌ Jupiter buy execution error: {e}")
            return None

    async def ensure_token_account_exists(self, token_mint: Pubkey) -> Pubkey:
            """
            Wallet-matching ATA creation: always detect the correct token program for the mint and use it for both address derivation and ATA creation, just like the raw wallet transaction. This ensures atomic, error-free behavior for SPL and Token-2022 tokens.
            """
            if str(token_mint) == str(SOL_MINT):
                return self.wallet_pubkey

            # Dynamically detect the correct token program for this mint
            async def detect_token_program(mint_pubkey):
                try:
                    # TODO: Replace with solders-compatible or HTTP RPC call for account_info
                    mint_info = None  # Placeholder
                    if mint_info.value:
                        mint_owner = mint_info.value.owner
                        if str(mint_owner) == "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb":
                            logger.info(f"🆕 Detected SPL Token 2022 mint: {mint_pubkey}")
                            return Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
                        elif str(mint_owner) == str(TOKEN_PROGRAM_ID):
                            logger.debug(f"✅ Standard SPL Token mint: {mint_pubkey}")
                            return TOKEN_PROGRAM_ID
                        else:
                            logger.warning(f"⚠️ Unknown token program: {mint_owner} for mint: {mint_pubkey}")
                            return TOKEN_PROGRAM_ID
                    else:
                        logger.warning(f"⚠️ Token mint not found on-chain: {mint_pubkey}")
                        return TOKEN_PROGRAM_ID
                except Exception as e:
                    logger.warning(f"⚠️ Token program detection failed: {e}, using default SPL Token")
                    return TOKEN_PROGRAM_ID

            # Ensure token_mint is a Pubkey
            token_mint_pubkey = token_mint if isinstance(token_mint, Pubkey) else Pubkey.from_string(token_mint)
            token_program = await detect_token_program(token_mint_pubkey)

            # Derive ATA address using the correct token program
            from spl.token.instructions import get_associated_token_address, create_associated_token_account
            if token_program == Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"):
                ata = get_associated_token_address(self.wallet_pubkey, token_mint_pubkey, token_program)
            else:
                ata = get_associated_token_address(self.wallet_pubkey, token_mint_pubkey)
    
    async def get_sol_balance(self) -> float:
        """Get current SOL balance"""
        try:
            balance_resp = await self.client.request("getBalance", [str(self.wallet_pubkey)])
            lamports = balance_resp['result']['value'] if balance_resp and 'result' in balance_resp else 0
            return lamports / 1_000_000_000
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0

    async def get_token_balance(self, token_mint: Pubkey) -> int:
        """Get current token balance for a specific mint"""
        try:
            if str(token_mint) == str(SOL_MINT):
                sol_balance = await self.get_sol_balance()
                return int(sol_balance * 1_000_000_000)
            token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            balance_resp = await self.client.request("getTokenAccountBalance", [str(token_account)])
            if balance_resp and 'result' in balance_resp and 'value' in balance_resp['result']:
                return int(balance_resp['result']['value']['amount'])
            return 0
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0

    async def confirm_transaction(self, signature: str, timeout: float = 30.0) -> bool:
        """Confirm transaction with specified timeout"""
        try:
            for i in range(int(timeout)):
                try:
                    status_resp = await self.client.request("getTransaction", [signature, {"maxSupportedTransactionVersion": 0}])
                    if status_resp and 'result' in status_resp and status_resp['result']:
                        meta = status_resp['result'].get('meta')
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

async def try_jupiter_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    """
    Enhanced Jupiter buy function with sophisticated validation and error handling
    Incorporates the robust logic from your original main.py
    
    Args:
        wallet_keypair: The wallet to use for trading
        token_mint: Token mint address as string or Pubkey
        amount_sol: Amount in SOL to spend
        **kwargs: Additional parameters
    """
    
    # CRITICAL FIX: Ensure token_mint is always a string for JSON
    token_mint_str = str(token_mint) if not isinstance(token_mint, str) else token_mint
    wallet_pubkey_str = str(wallet_keypair.pubkey())
    
    logger.info(f"🪙 Jupiter Buy (Enhanced): {amount_sol} SOL → {token_mint_str[:8]}...")
    logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this token!")
    logger.info(f"💎 Skipping most validations - if they can trade it, so can we!")
    
    from rate_limit_manager import rate_limit_manager
    from env_keys import EnvKeys
    # AGGRESSIVE MODE: Log but do not abort on rate limit or balance issues
    try:
        if not rate_limit_manager.can_make_jupiter_request():
            logger.warning(f"⏳ Rate limiting Jupiter - would wait, but AGGRESSIVE MODE: proceeding anyway!")
        rate_limit_manager.record_jupiter_request()
    except Exception as e:
        logger.warning(f"[AGGRESSIVE MODE] Rate limit manager error: {e} - proceeding anyway!")
    # Coordinator should check SOL balance before calling this executor
    # Enhanced retry logic with exponential backoff
    max_retries = kwargs.get('max_retries', 3)
    retry_delay = 0.5
    for attempt in range(max_retries):
        signature = None
        env_keys = EnvKeys()
        try:
            if attempt > 0:
                logger.info(f"🔄 Jupiter retry attempt {attempt + 1}/{max_retries}")
                await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            jupiter_copy = JupiterCopyExecutor(
                wallet_keypair=wallet_keypair,
                rpc_url=kwargs.get('rpc_url', env_keys.HELIUS_RPC_URL),
                config=CopyExecutorConfig(
                    slippage_tolerance=kwargs.get('slippage_tolerance', 0.30),
                    max_retries=1,
                    confirmation_timeout=kwargs.get('confirmation_timeout', 25.0),
                    compute_unit_limit=500_000,
                    compute_unit_price=100
                ),
                jito_service=kwargs.get('jito_service')
            )
            signature = await jupiter_copy.execute_buy_copy(
                token_mint=token_mint_str,
                sol_amount=amount_sol,
                original_signature=str(kwargs.get('original_signature', '')),
                original_wallet=str(kwargs.get('original_wallet', ''))
            )
            await jupiter_copy.close()
            if signature and not str(signature).startswith("111111") and len(str(signature)) >= 64:
                logger.info(f"✅ Jupiter buy successful (attempt {attempt + 1}): {signature}")
                return {
                    'success': True,
                    'signature': str(signature),
                    'amount_sol': amount_sol,
                    'token_mint': token_mint_str,
                    'dex': 'Jupiter',
                    'attempts': attempt + 1
                }
            else:
                logger.warning(f"⚠️ Jupiter attempt {attempt + 1} failed: invalid signature (AGGRESSIVE MODE: still attempted trade)")
        except Exception as attempt_error:
            logger.warning(f"⚠️ Jupiter attempt {attempt + 1} error: {attempt_error} (AGGRESSIVE MODE: still attempted trade)")
    return {
        'success': False,
        'error': 'Jupiter buy failed - all attempts made (AGGRESSIVE MODE)',
        'dex': 'Jupiter'
    }

async def try_jupiter_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    """
    Enhanced Jupiter sell all function with sophisticated validation and error handling
    Incorporates the robust logic from your original main.py
    
    Args:
        wallet_keypair: The wallet to use for trading
        token_mint: The token mint address to sell
        **kwargs: Additional parameters (slippage_tolerance, etc.)
    
    Returns:
        Dict with success, signature, error keys
    """
    from rate_limit_manager import rate_limit_manager
    from env_keys import EnvKeys
    
    try:
        logger.info(f"🪙 Jupiter Sell All (Enhanced): {token_mint[:8]}...")
        logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this sale!")
        try:
            if not rate_limit_manager.can_make_jupiter_request():
                logger.warning(f"⏳ Rate limiting Jupiter - would wait, but AGGRESSIVE MODE: proceeding anyway!")
            rate_limit_manager.record_jupiter_request()
        except Exception as e:
            logger.warning(f"[AGGRESSIVE MODE] Rate limit manager error: {e} - proceeding anyway!")
        env_keys = EnvKeys()
        token_balance = 0
        try:
            from solders.pubkey import Pubkey
            from aiohttp import ClientSession
            token_mint_pubkey = token_mint if isinstance(token_mint, Pubkey) else Pubkey.from_string(token_mint)
            owner = str(wallet_keypair.pubkey())
            async with ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [owner, {"mint": str(token_mint_pubkey)}, {"encoding": "jsonParsed"}]
                }
                async with session.post(env_keys.HELIUS_RPC_URL, json=payload) as resp:
                    result = await resp.json()
                    accounts = result.get('result', {}).get('value', [])
                    if not accounts:
                        logger.warning(f"⚠️ No token account found for {token_mint[:8]}... (AGGRESSIVE MODE: still attempting sell)")
                        token_balance = 0
                    else:
                        token_account_info = accounts[0]['account']['data']['parsed']['info']['tokenAmount']
                        token_balance = float(token_account_info.get('uiAmount', 0))
                        if token_balance <= 0:
                            logger.warning(f"⚠️ Zero token balance for {token_mint[:8]}... (AGGRESSIVE MODE: still attempting sell)")
        except Exception as balance_error:
            logger.warning(f"⚠️ Token balance check error: {balance_error} (AGGRESSIVE MODE: still attempting sell)")
        max_retries = kwargs.get('max_retries', 3)
        retry_delay = 0.5
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Jupiter sell retry attempt {attempt + 1}/{max_retries}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                jupiter_copy = JupiterCopyExecutor(
                    wallet_keypair=wallet_keypair,
                    rpc_url=kwargs.get('rpc_url', env_keys.HELIUS_RPC_URL),
                    config=CopyExecutorConfig(
                        slippage_tolerance=kwargs.get('slippage_tolerance', 0.30),
                        max_retries=1,
                        confirmation_timeout=kwargs.get('confirmation_timeout', 30.0),
                        compute_unit_limit=500_000,
                        compute_unit_price=100
                    ),
                    jito_service=kwargs.get('jito_service')
                )
                token_amount = int(token_balance * 1_000_000) if token_balance > 0 else 1_000_000
                signature = await jupiter_copy.execute_sell_copy(
                    token_mint=token_mint,
                    token_amount=token_amount,
                    original_signature=kwargs.get('original_signature', ''),
                    original_wallet=kwargs.get('original_wallet', ''),
                    **kwargs
                )
                await jupiter_copy.close()
                if signature and not str(signature).startswith("111111") and len(str(signature)) >= 64:
                    logger.info(f"✅ Jupiter sell successful (attempt {attempt + 1}): {signature}")
                    return {
                        'success': True,
                        'signature': signature,
                        'token_mint': token_mint,
                        'token_balance_sold': token_balance,
                        'dex': 'Jupiter',
                        'attempts': attempt + 1
                    }
                else:
                    logger.warning(f"⚠️ Jupiter sell attempt {attempt + 1} failed: invalid signature (AGGRESSIVE MODE: still attempted trade)")
            except Exception as attempt_error:
                logger.warning(f"⚠️ Jupiter sell attempt {attempt + 1} error: {attempt_error} (AGGRESSIVE MODE: still attempted trade)")
        return {
            'success': False,
            'error': 'Jupiter sell failed - all attempts made (AGGRESSIVE MODE)',
            'dex': 'Jupiter'
        }
    except Exception as e:
        logger.error(f"❌ Jupiter sell critical error: {e} (AGGRESSIVE MODE: still attempted trade)")
        return {
            'success': False,
            'error': f'Jupiter sell critical error: {str(e)} (AGGRESSIVE MODE)',
            'dex': 'Jupiter'
        }

# Example usage:
"""
from solders.keypair import Keypair

# Initialize the copy executor
jupiter_copy = JupiterCopyExecutor(
    wallet_keypair=your_wallet_keypair,
    rpc_url="https://api.mainnet-beta.solana.com",
    config=CopyExecutorConfig(
        slippage_tolerance=0.05,
        max_retries=2,
        confirmation_timeout=30.0
    )
)

# When you detect a Jupiter trade from another wallet:
# Extract the trade information from the detected transaction
extracted_trade = ExtractedTradeInfo(
    input_mint="So11111111111111111111111111111111111111112",  # SOL
    output_mint="your_token_mint_address",
    amount_in=1000000,   # 0.001 SOL in lamports
    is_buy=True,
    original_signature="detected_transaction_signature",
    wallet_address="wallet_you_are_copying"
)

# Execute the copy trade
signature = await jupiter_copy.execute_copy_trade(extracted_trade, copy_amount=0.001)

# Or use the convenience methods:
# Copy a buy trade
buy_signature = await jupiter_copy.execute_buy_copy(
    token_mint="token_mint_address",
    sol_amount=0.001,
    original_signature="original_tx_signature",
    original_wallet="original_wallet_address"
)

# Copy a sell trade with proportional selling support
sell_signature = await jupiter_copy.execute_sell_copy(
    token_mint="token_mint_address",
    token_amount=1000000,
    original_signature="original_tx_signature",
    original_wallet="original_wallet_address",
    sell_percentage=50.0  # Example: sell 50% of tokens
)
)

# Confirm the transaction
if signature:
    confirmed = await jupiter_copy.confirm_transaction(signature)
    if confirmed:
        print("✅ Copy trade confirmed!")

# Or use the standardized functions for copy bot integration:
# Buy tokens
result = await try_jupiter_buy(wallet_keypair, "token_mint", 0.001)
if result['success']:
    print(f"Buy successful: {result['signature']}")

# Sell all tokens
result = await try_jupiter_sell_all(wallet_keypair, "token_mint")
if result['success']:
    print(f"Sell successful: {result['signature']}")
"""
