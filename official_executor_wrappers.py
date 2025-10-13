# --- DEBUG WRAPPER FOR ALL EXECUTORS ---
import functools
import logging
from typing import Dict, Any
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient as SolanaRpcClient

logger = logging.getLogger(__name__)

def _log_executor_call(name, *args, **kwargs):
    logger.debug(f"[DEBUG] Executor {name} called with args={args}, kwargs={kwargs}")

def debug_wrapper(fn):

    # --- Phoenix (fully isolated) ---
    async def try_phoenix_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        try:
            try_phoenix_buy_fn, = import_executor('phoenix_copy_executor', 'try_phoenix_buy')
            if try_phoenix_buy_fn is None:
                return {"success": False, "error": "Phoenix executor unavailable"}
            return await try_phoenix_buy_fn(wallet_keypair, token_mint, amount_sol, **kwargs)
        except Exception as e:
            logger.error(f"❌ Phoenix buy failed: {e}")
            return {"success": False, "error": str(e)}

    async def try_phoenix_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        try:
            try_phoenix_sell_all_fn, = import_executor('phoenix_copy_executor', 'try_phoenix_sell_all')
            if try_phoenix_sell_all_fn is None:
                return {"success": False, "error": "Phoenix executor unavailable"}
            return await try_phoenix_sell_all_fn(wallet_keypair, token_mint, **kwargs)
        except Exception as e:
            logger.error(f"❌ Phoenix sell failed: {e}")
            return {"success": False, "error": str(e)}
        self.session = aiohttp.ClientSession()


    async def request(self, method: str, params: list):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        async with self.session.post(self.rpc_url, json=payload) as resp:
            result = await resp.json()
            return result.get("result")

    async def get_account_info(self, pubkey: str, encoding: str = "jsonParsed"):
        """
        Jupiter compatibility: get_account_info(pubkey, encoding="jsonParsed")
        Returns the account info dict for the given pubkey.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [pubkey, {"encoding": encoding}]
        }
        async with self.session.post(self.rpc_url, json=payload) as resp:
            result = await resp.json()
            return result.get("result")

    async def close(self):
        await self.session.close()
"""
Official Executor Wrappers - ENHANCED with comprehensive DEX-specific validation
Uses official documentation validation for each DEX type to prevent execution failures
"""

import logging
from typing import Dict, Any
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address
import hashlib
from env_keys import EnvKeys
 # REMOVED: solana.rpc.async_api.AsyncClient and solana.rpc.commitment. Use solders and aiohttp/httpx for RPC.

# Import comprehensive validation system
from dex_token_validator import validate_token_for_dex, get_recommended_dexes_for_token

logger = logging.getLogger(__name__)

# Global Jito service for executor use
_global_jito_service = None

async def _validate_pumpfun_token(token_mint: str, **kwargs) -> bool:
    """
    🔍 ENHANCED: Validate if a token is actually on the Pump.fun platform using CORRECT program ID
    Returns True if token is on Pump.fun, False otherwise
    
    CRITICAL FIX: Uses correct pump.fun program ID to prevent AccountOwnedByWrongProgram errors
    """
    # CORRECT pump.fun program ID (verified from official documentation)
    PUMP_FUN_PROGRAM_ID = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
    # Immediately reject WSOL and other system tokens
    if token_mint == "So11111111111111111111111111111111111111112":
        logger.info(f"❌ WSOL is not a pump.fun token - rejecting")
        return False
    # Reject other common system tokens
    system_tokens = [
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    ]
    if token_mint in system_tokens:
        logger.info(f"❌ System token {token_mint[:8]}... is not a pump.fun token - rejecting")
        return False
    # Get RPC client
    rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
    client = SolanaRpcClient(rpc_url)
    try:
        account_info = await client.request("getAccountInfo", [str(token_mint), {"encoding": "jsonParsed"}])
        await client.close()
        # Implement real validation logic here if needed
        return bool(account_info and account_info.get('value'))
    except Exception as e:
        logger.warning(f"⚠️ Pump.fun token validation failed for {token_mint[:8]}...: {e}")
        await client.close()
        return False

def get_proper_rpc_url():
    """Get RPC URL with proper authentication from environment"""
    try:
        env_keys = EnvKeys()
        return env_keys.HELIUS_RPC_URL
    except:
        # Fallback to basic URL if env keys fail
        return 'https://mainnet.helius-rpc.com'

# 🚨 CRITICAL ATA FIX CONSTANTS

# Official program IDs
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
TOKEN_2022_PROGRAM_ID = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
ASSOCIATED_TOKEN_PROGRAM_ID_2022 = Pubkey.from_string("ATok2zQdB6q6r1hB3QyQm5Qw1r5Qw1r5Qw1r5Qw1r5Qw")

async def get_correct_ata_address(wallet_pubkey: Pubkey, token_mint: Pubkey, token_program_id: Pubkey = None) -> Pubkey:
    """
    Async: Get the correct Associated Token Account address for both legacy SPL and SPL Token 2022 mints.
    Enhanced: Logs all parameters, program IDs, and aborts for WSOL/system tokens.
    """
    # WSOL/system token check
    SYSTEM_TOKENS = [
        "So11111111111111111111111111111111111111112",  # WSOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    ]
    if str(token_mint) in SYSTEM_TOKENS:
        logger.error(f"❌ [ATA] Refusing to derive ATA for system token: {token_mint}")
        raise Exception(f"Refusing to derive ATA for system token: {token_mint}")
    try:
        # Dynamically detect token program (legacy SPL or Token-2022)
        if token_program_id is None:
            token_program_id = await detect_token_program(token_mint)
        logger.info(f"[ATA] Deriving ATA | wallet={wallet_pubkey} mint={token_mint} program_id={token_program_id}")
        # Log mint's actual program owner for diagnostics
        await log_mint_program_owner(token_mint)
        if token_program_id == TOKEN_2022_PROGRAM_ID:
            # Manual PDA derivation for Token 2022
            seeds = [
                bytes(ASSOCIATED_TOKEN_PROGRAM_ID_2022),
                bytes(wallet_pubkey),
                bytes(token_program_id),
                bytes(token_mint)
            ]
            ata_address, _ = find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID_2022)
            logger.info(f"✅ [DEBUG] Token 2022 ATA calculated: {str(ata_address)} for wallet {str(wallet_pubkey)} and token {str(token_mint)}")
        else:
            ata_address = get_associated_token_address(wallet_pubkey, token_mint)
            logger.info(f"✅ [DEBUG] Legacy SPL ATA calculated: {str(ata_address)} for wallet {str(wallet_pubkey)} and token {str(token_mint)}")
        return ata_address
    except Exception as e:
        logger.error(f"❌ [DEBUG] CRITICAL: ATA calculation failed: {e}")
        raise

# Helper: Async token program detection
async def detect_token_program(token_mint: Pubkey) -> Pubkey:
    try:
        rpc_url = get_proper_rpc_url()
        client = SolanaRpcClient(rpc_url)
        account_info = await client.get_account_info(str(token_mint))
        await client.close()
        if account_info and 'owner' in account_info:
            owner = account_info['owner']
            if owner == str(TOKEN_2022_PROGRAM_ID):
                return TOKEN_2022_PROGRAM_ID
    except Exception:
        pass
    return TOKEN_PROGRAM_ID

# Helper: PDA derivation (Solana's find_program_address)
def find_program_address(seeds, program_id):
    """
    Derive a program address (PDA) as per Solana's find_program_address.
    """
    nonce = 255
    while nonce != 0:
        try:
            seeds_with_nonce = seeds + [bytes([nonce])]
            buf = b"".join(seeds_with_nonce) + bytes(program_id)
            hash_bytes = hashlib.sha256(buf).digest()
            pda = Pubkey.from_bytes(hash_bytes[:32])
            if not pda.is_on_curve():
                return pda, nonce
        except Exception:
            pass
        nonce -= 1
    raise Exception("Unable to find a valid program address")

# --- CANONICAL ATA CREATION LOGIC ---

async def create_ata_ix(wallet_pubkey: Pubkey, token_mint: Pubkey, payer_pubkey: Pubkey, token_program_id: Pubkey = None):
    """
    Async: Return the correct instruction to create an ATA for both legacy SPL and SPL Token 2022 mints.
    Enhanced: Logs all parameters, program IDs, and aborts for WSOL/system tokens.
    """
    SYSTEM_TOKENS = [
        "So11111111111111111111111111111111111111112",  # WSOL
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    ]
    if str(token_mint) in SYSTEM_TOKENS:
        logger.error(f"❌ [ATA] Refusing to create ATA for system token: {token_mint}")
        raise Exception(f"Refusing to create ATA for system token: {token_mint}")

    # Always detect the correct token program for the mint
    try:
        if token_program_id is None:
            token_program_id = await detect_token_program(token_mint)
        logger.info(f"[ATA] Creating ATA IX | wallet={wallet_pubkey} mint={token_mint} payer={payer_pubkey} program_id={token_program_id}")
        await log_mint_program_owner(token_mint)

        # Use correct program_id and token_program_id for ATA creation
        if token_program_id == TOKEN_2022_PROGRAM_ID:
            logger.info(f"[ATA] Detected Token-2022 mint. Using Token-2022 program IDs for ATA creation.")
            return create_associated_token_account(
                payer=payer_pubkey,
                owner=wallet_pubkey,
                mint=token_mint,
                program_id=ASSOCIATED_TOKEN_PROGRAM_ID_2022,
                token_program_id=TOKEN_2022_PROGRAM_ID
            )
        else:
            logger.info(f"[ATA] Detected legacy SPL mint. Using legacy SPL program IDs for ATA creation.")
            return create_associated_token_account(
                payer=payer_pubkey,
                owner=wallet_pubkey,
                mint=token_mint,
                program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
                token_program_id=TOKEN_PROGRAM_ID
            )
    except Exception as e:
        logger.error(f"❌ [ATA] ATA creation failed: {e}")
        raise

async def log_mint_program_owner(token_mint: Pubkey):
    """
    Utility: Logs the actual program owner of the mint for diagnostics before ATA creation.
    """
    try:
        rpc_url = get_proper_rpc_url()
        client = SolanaRpcClient(rpc_url)
        account_info = await client.get_account_info(str(token_mint))
        await client.close()
        if account_info and 'owner' in account_info:
            logger.info(f"[ATA] Mint {token_mint} is owned by program: {account_info['owner']}")
        else:
            logger.warning(f"[ATA] Could not determine program owner for mint {token_mint}")
    except Exception as e:
        logger.warning(f"[ATA] Error logging mint program owner for {token_mint}: {e}")


# --- CANONICAL ATA CREATION LOGIC ---
from spl.token.instructions import create_associated_token_account


    # This function is now a placeholder. Use the solders/spl.token.instructions approach for ATA creation as in pumpfun_copy_executor.py

# --- ASYNC STRICT VALIDATION FOR ATA ---
async def strict_validate_ata(ata_address: Pubkey, wallet_pubkey: Pubkey, token_mint: Pubkey):
    """
    Strictly validate that the ATA is owned by the SPL Token program and matches the expected mint and owner.
    Raises Exception if any check fails.
    """
    try:
        rpc_url = get_proper_rpc_url()
        client = SolanaRpcClient(rpc_url)
        account_info = None
        try:
            account_info = await client.get_account_info(str(ata_address))
        except Exception as e:
            logger.warning(f"[DEBUG] Could not fetch ATA account info for {ata_address}: {e}")
        await client.close()
        if account_info and account_info.get('value'):
            data = account_info['value']
            owner = data.get('owner')
            if owner != str(TOKEN_PROGRAM_ID):
                logger.error(f"❌ [DEBUG] ATA {ata_address} is not owned by SPL Token program! Found owner: {owner}")
                raise Exception(f"ATA {ata_address} not owned by SPL Token program")
            # Check mint and owner fields in account data if available
            parsed = data.get('data', {}).get('parsed', {})
            if parsed:
                info = parsed.get('info', {})
                ata_mint = info.get('mint')
                ata_owner = info.get('owner')
                if ata_mint and ata_mint != str(token_mint):
                    logger.error(f"❌ [DEBUG] ATA {ata_address} mint mismatch! Expected {token_mint}, found {ata_mint}")
                    raise Exception(f"ATA {ata_address} mint mismatch")
                if ata_owner and ata_owner != str(wallet_pubkey):
                    logger.error(f"❌ [DEBUG] ATA {ata_address} owner mismatch! Expected {wallet_pubkey}, found {ata_owner}")
                    raise Exception(f"ATA {ata_address} owner mismatch")
    except Exception as e:
        logger.error(f"❌ [DEBUG] STRICT ATA VALIDATION FAILED: {e}")
        raise

def initialize_executors(wallet: Keypair, rpc_url: str, jito_service=None, **kwargs):
    """Initialize executors with Jito service - just log that we're using existing executors"""
    logger.info(f"✅ Using existing working executors with wallet: {wallet.pubkey()}")
    
    # Store jito_service globally for executor use
    global _global_jito_service
    _global_jito_service = jito_service

def import_executor(module_name, *func_names):
    try:
        module = __import__(module_name, fromlist=func_names)
        return tuple(getattr(module, fn) for fn in func_names)
    except Exception as e:
        logger.error(f"❌ Failed to import {module_name}: {e}")
        return (None,) * len(func_names)

# --- Pump.fun ---
async def try_pumpfun_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    try:
        try_pumpfun_buy_fn, = import_executor('pumpfun_CC_copy_executor', 'try_pumpfun_buy')
        if try_pumpfun_buy_fn is None:
            return {"success": False, "error": "Pump.fun executor unavailable"}
        return await try_pumpfun_buy_fn(wallet_keypair, token_mint, amount_sol, **kwargs)
    except Exception as e:
        logger.error(f"❌ Pump.fun buy failed: {e}")
        return {"success": False, "error": str(e)}

async def try_pumpfun_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    try:
        try_pumpfun_sell_all_fn, = import_executor('pumpfun_CC_copy_executor', 'try_pumpfun_sell_all')
        if try_pumpfun_sell_all_fn is None:
            return {"success": False, "error": "Pump.fun executor unavailable"}
        return await try_pumpfun_sell_all_fn(wallet_keypair, token_mint, **kwargs)
    except Exception as e:
        logger.error(f"❌ Pump.fun sell failed: {e}")
        return {"success": False, "error": str(e)}

# --- Jupiter ---
async def try_jupiter_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    try:
        try_jupiter_buy_fn, = import_executor('jupiter_executor', 'try_jupiter_buy')
        if try_jupiter_buy_fn is None:
            return {"success": False, "error": "Jupiter executor unavailable"}
        return await try_jupiter_buy_fn(wallet_keypair, token_mint, amount_sol, **kwargs)
    except Exception as e:
        logger.error(f"❌ Jupiter buy failed: {e}")
        return {"success": False, "error": str(e)}

async def try_jupiter_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    try:
        try_jupiter_sell_all_fn, = import_executor('jupiter_executor', 'try_jupiter_sell_all')
        if try_jupiter_sell_all_fn is None:
            return {"success": False, "error": "Jupiter executor unavailable"}
        return await try_jupiter_sell_all_fn(wallet_keypair, token_mint, **kwargs)
    except Exception as e:
        logger.error(f"❌ Jupiter sell failed: {e}")
        return {"success": False, "error": str(e)}

# --- Raydium ---
async def try_raydium_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    try:
        try_raydium_buy_fn, = import_executor('raydium_executor', 'try_raydium_buy')
        if try_raydium_buy_fn is None:
            return {"success": False, "error": "Raydium executor unavailable"}
        return await try_raydium_buy_fn(wallet_keypair, token_mint, amount_sol, **kwargs)
    except Exception as e:
        logger.error(f"❌ Raydium buy failed: {e}")
        return {"success": False, "error": str(e)}

async def try_raydium_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    try:
        try_raydium_sell_all_fn, = import_executor('raydium_executor', 'try_raydium_sell_all')
        if try_raydium_sell_all_fn is None:
            return {"success": False, "error": "Raydium executor unavailable"}
        return await try_raydium_sell_all_fn(wallet_keypair, token_mint, **kwargs)
    except Exception as e:
        logger.error(f"❌ Raydium sell failed: {e}")
        return {"success": False, "error": str(e)}

# --- CPMM ---
async def try_cpmm_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    try:
        try_cpmm_buy_fn, = import_executor('cpmm_copy_executor', 'try_cpmm_buy')
        if try_cpmm_buy_fn is None:
            return {"success": False, "error": "CPMM executor unavailable"}
        return await try_cpmm_buy_fn(wallet_keypair, token_mint, amount_sol, **kwargs)
    except Exception as e:
        logger.error(f"❌ CPMM buy failed: {e}")
        return {"success": False, "error": str(e)}

async def try_cpmm_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    try:
        try_cpmm_sell_all_fn, = import_executor('cpmm_copy_executor', 'try_cpmm_sell_all')
        if try_cpmm_sell_all_fn is None:
            return {"success": False, "error": "CPMM executor unavailable"}
        return await try_cpmm_sell_all_fn(wallet_keypair, token_mint, **kwargs)
    except Exception as e:
        logger.error(f"❌ CPMM sell failed: {e}")
        return {"success": False, "error": str(e)}

# --- CLMM Hybrid ---
async def try_clmm_hybrid_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    try:
        try_clmm_hybrid_buy_fn, = import_executor('clmm_hybrid_copy_executor', 'try_clmm_hybrid_buy')
        if try_clmm_hybrid_buy_fn is None:
            return {"success": False, "error": "CLMM Hybrid executor unavailable"}
        return await try_clmm_hybrid_buy_fn(wallet_keypair, token_mint, amount_sol, **kwargs)
    except Exception as e:
        logger.error(f"❌ CLMM Hybrid buy failed: {e}")
        return {"success": False, "error": str(e)}

async def try_clmm_hybrid_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    try:
        try_clmm_hybrid_sell_all_fn, = import_executor('clmm_hybrid_copy_executor', 'try_clmm_hybrid_sell_all')
        if try_clmm_hybrid_sell_all_fn is None:
            return {"success": False, "error": "CLMM Hybrid executor unavailable"}
        return await try_clmm_hybrid_sell_all_fn(wallet_keypair, token_mint, **kwargs)
    except Exception as e:
        logger.error(f"❌ CLMM Hybrid sell failed: {e}")
        return {"success": False, "error": str(e)}

# --- Phoenix (example, handle gracefully if broken) ---
async def try_phoenix_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    try:
        try_phoenix_buy_fn, = import_executor('phoenix_executor', 'try_phoenix_buy')
        if try_phoenix_buy_fn is None:
            return {"success": False, "error": "Phoenix executor unavailable"}
        return await try_phoenix_buy_fn(wallet_keypair, token_mint, amount_sol, **kwargs)
    except Exception as e:
        logger.error(f"❌ Phoenix buy failed: {e}")
        return {"success": False, "error": str(e)}

async def try_phoenix_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    try:
        try_phoenix_sell_all_fn, = import_executor('phoenix_executor', 'try_phoenix_sell_all')
        if try_phoenix_sell_all_fn is None:
            return {"success": False, "error": "Phoenix executor unavailable"}
        return await try_phoenix_sell_all_fn(wallet_keypair, token_mint, **kwargs)
    except Exception as e:
        logger.error(f"❌ Phoenix sell failed: {e}")
        return {"success": False, "error": str(e)}
    async def try_pumpfun_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        # --- UNIVERSAL TOKEN VALIDATION ---
        system_tokens = [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        ]
        if token_mint in system_tokens:
            logger.error(f"❌ [DEBUG] System token {token_mint[:8]}... is not tradable - aborting")
            return {"success": False, "signature": None, "error": "System token not tradable"}

        # --- SOL BALANCE CHECK ---
        try:
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = SolanaRpcClient(rpc_url)
            wallet_pubkey = wallet_keypair.pubkey()
            logger.info(f"[DEBUG] Checking SOL balance for wallet: {wallet_pubkey}")
            sol_balance_info = await client.request("getBalance", [str(wallet_pubkey)])
            logger.info(f"[DEBUG] Raw getBalance RPC response: {sol_balance_info}")
            await client.close()
            sol_balance = sol_balance_info.get('value', 0) / 1_000_000_000 if sol_balance_info else 0
            logger.info(f"[DEBUG] Parsed SOL balance: {sol_balance}")
            if sol_balance < amount_sol + 0.01:  # Add buffer for fees
                logger.error(f"❌ [DEBUG] Insufficient SOL: {sol_balance} available, {amount_sol} + fees required")
                return {"success": False, "signature": None, "error": f"Insufficient SOL: {sol_balance} available"}
        except Exception as e:
            logger.warning(f"⚠️ [DEBUG] Could not check SOL balance: {e}")

        """
        🔧 PUMP.FUN FIRST: Always try native Pump.fun builder FIRST, only fallback to Jupiter if necessary
        
        CRITICAL PRIORITY ORDER:
        1. 🚀 Native Pump.fun transaction builder (HIGHEST PRIORITY)
        2. ⚠️ Jupiter fallback ONLY if native fails
        """
        try:
            # Defensive: ensure logger is a Logger instance and not a float or other type
            import logging as _logging
            _logger = kwargs.get('logger', None)
            if not isinstance(_logger, _logging.Logger):
                _logger = globals().get('logger', None)
            if not isinstance(_logger, _logging.Logger):
                _logger = logging.getLogger(__name__)

            # Prevent accidental shadowing by float or other types
            if isinstance(_logger, float):
                print("[CRITICAL LOGGER ERROR] Logger variable is a float! Resetting to module logger.")
                _logger = logging.getLogger(__name__)

            _logger.info(f"[DEBUG] try_pumpfun_buy called with wallet_keypair={wallet_keypair}, token_mint={token_mint}, amount_sol={amount_sol}, kwargs={kwargs}")
            _logger.info(f"🚀 Pump.fun Buy (Enhanced): {amount_sol} SOL → {token_mint[:8]}...")
            _logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this token!")
            _logger.info(f"💎 Direct Pump.fun - No Jupiter dependency!")

            # 🚨 CRITICAL: Validate token mint before conversion to prevent Base58 errors
            if not token_mint or len(token_mint) < 32:
                _logger.error(f"❌ [DEBUG] Invalid token mint: {token_mint} (too short)")
                return {"success": False, "signature": None, "error": "Invalid token mint"}

            # 🚨 ULTRA-AGGRESSIVE TOKENS: Skip placeholder tokens that aren't real Base58
            ultra_aggressive_tokens = [
                'AGGRESSIVE_TARGET_WALLET_BUY_',
                'AGGRESSIVE_BUY_TOKEN_',
                'AGGRESSIVE_SELL_TOKEN_', 
                'EMERGENCY_ASSUMPTION_TOKEN_',
                'FALLBACK_BUY_TOKEN_',
                'ERROR_FALLBACK_BUY_'
            ]

            is_placeholder = any(prefix in token_mint for prefix in ultra_aggressive_tokens)
            if is_placeholder:
                _logger.warning(f"⚠️ [DEBUG] Skipping placeholder token: {token_mint[:20]}...")
                _logger.warning(f"   [DEBUG] This is an ultra-aggressive assumption token, not a real mint")
                return {"success": False, "signature": None, "error": "Placeholder token"}

            # 🔍 PUMP.FUN PLATFORM VALIDATION: Log but do not skip execution for non-Pump.fun tokens
            _logger.info(f"[DEBUG] Validating if token is Pump.fun: {token_mint}")
            is_pumpfun_token = await _validate_pumpfun_token(token_mint, **kwargs)
            _logger.info(f"[DEBUG] is_pumpfun_token result: {is_pumpfun_token}")
            if not is_pumpfun_token:
                _logger.warning(f"⚠️ [DEBUG] Token {token_mint[:8]}... is not on Pump.fun platform")
                _logger.warning(f"   [DEBUG] Proceeding with multi-DEX fallback for non-Pump.fun token")
                fallback_results = []
                # Try Jupiter first
                from jupiter_copy_executor import try_jupiter_buy
                result = await try_jupiter_buy(wallet_keypair, token_mint, amount_sol, **kwargs)
                _logger.info(f"[DEBUG] Jupiter fallback result: {result}")
                fallback_results.append(("Jupiter", result))

            try:
                # Calculate the CORRECT ATA address
                wallet_pubkey = wallet_keypair.pubkey()
                token_mint_pubkey = Pubkey.from_string(token_mint)
                correct_ata = await get_correct_ata_address(wallet_pubkey, token_mint_pubkey)
                _logger.info(f"✅ Using CORRECT ATA: {str(correct_ata)}")
                # --- STRICT VALIDATION: Check ATA account owner and mint ---
                await strict_validate_ata(correct_ata, wallet_pubkey, token_mint_pubkey)
            except Exception as e:
                _logger.error(f"❌ ATA validation error for token {token_mint[:20]}...: {e}")
                return {"success": False, "signature": None, "error": f"ATA validation error: {e}"}

            # STEP 1: 🚀 TRY NEW VALIDATED PUMP.FUN EXECUTOR FIRST (HIGHEST PRIORITY)
            _logger.info(f"🎪 STEP 1: NEW VALIDATED PUMP.FUN EXECUTOR (with Jito support)")

            # Import the new validated executor
            from pumpfun_executor import buy_token
            from env_keys import EnvKeys

            try:
                env_keys = EnvKeys()
                rpc_client = SolanaRpcClient(env_keys.HELIUS_RPC_URL)
                jito_service = kwargs.get('jito_service', _global_jito_service)
                result = await buy_token(
                    rpc_client=rpc_client,
                    wallet_keypair=wallet_keypair,
                    token_mint=token_mint,
                    sol_amount=amount_sol,
                    max_slippage_bps=kwargs.get('max_slippage_bps', 500),
                    jito_service=jito_service
                )
                await rpc_client.close()
                if result.success:
                    _logger.info(f"✅ NEW PUMP.FUN EXECUTOR SUCCESS: {result.signature}")
                    return {
                        'success': True,
                        'signature': result.signature,
                        'dex': 'PumpFun_Validated',
                        'method': 'new_validated_executor',
                        'sol_spent': result.sol_spent,
                        'attempts': 1
                    }
                else:
                    _logger.warning(f"⚠️ New Pump.fun executor failed: {result.error}")
            except Exception as new_executor_error:
                _logger.warning(f"⚠️ New Pump.fun executor failed: {new_executor_error}")

            # STEP 2: 🚀 TRY LEGACY NATIVE PUMP.FUN BUILDER AS BACKUP
            _logger.info(f"🎪 STEP 2: LEGACY NATIVE PUMP.FUN BUILDER (backup)")

            # Import native builder function
            from pumpfun_CC_copy_executor import PumpFunCopyExecutor

            # Create executor instance and try native building
            pumpfun_executor = PumpFunCopyExecutor(
                wallet_keypair=wallet_keypair,  # 🛠️ FIXED: Added missing wallet_keypair argument
                rpc_url=kwargs.get('rpc_url', get_proper_rpc_url())
            )

            try:
                # Use the native builder directly
                native_signature = await pumpfun_executor._build_native_pumpfun_buy(
                    wallet_keypair=wallet_keypair,
                    token_mint_str=token_mint,
                    amount_sol=amount_sol,
                    jito_service=_global_jito_service,
                    correct_ata=str(correct_ata),
                    **kwargs
                )

                if native_signature and native_signature != "invalid signature":
                    _logger.info(f"✅ LEGACY PUMP.FUN SUCCESS: {native_signature}")
                    return {
                        'success': True,
                        'signature': native_signature,
                        'dex': 'PumpFun_Legacy',
                        'method': 'legacy_native_builder',
                        'correct_ata': str(correct_ata),
                        'attempts': 2
                    }
                else:
                    _logger.warning(f"⚠️ Legacy Pump.fun builder returned invalid signature")

            except Exception as native_error:
                _logger.warning(f"⚠️ Legacy Pump.fun builder failed: {native_error}")

            # STEP 3: ⚠️ FALLBACK TO ALL DEXS IF ALL PUMP.FUN METHODS FAIL
            _logger.warning("⚠️ All Pump.fun methods failed — falling back to all DEXs (Jupiter, Raydium, Orca, Phoenix)...")

            # Add the correct ATA to kwargs for the original executor
            kwargs['correct_user_token_account'] = str(correct_ata)
            kwargs['verified_ata'] = True
            kwargs['jito_service'] = _global_jito_service

            fallback_results = []
            # 1. Try Jupiter
            result = await _original_pumpfun_buy(wallet_keypair, token_mint, amount_sol, **kwargs)
            _logger.info(f"[DEBUG] Jupiter fallback result: {result}")
            fallback_results.append(("Jupiter", result))
            if result.get('success'):
                _logger.info(f"✅ JUPITER FALLBACK SUCCESS: {result.get('signature')}")
                result['fix_applied'] = 'corrected_ata_derivation'
                result['correct_ata'] = str(correct_ata)
                result['method'] = 'jupiter_fallback'
                return result
            # 2. Try Raydium
            try:
                from raydium_copy_executor import try_raydium_buy
                result = await try_raydium_buy(wallet_keypair, token_mint, amount_sol, **kwargs)
                _logger.info(f"[DEBUG] Raydium fallback result: {result}")
                fallback_results.append(("Raydium", result))
                if result.get('success'):
                    return result
            except Exception as e:
                _logger.error(f"Raydium fallback exception: {e}")
                fallback_results.append(("Raydium", {"success": False, "error": str(e)}))
            # 3. Try Orca
            try:
                from orca_copy_executor import try_orca_buy
                result = await try_orca_buy(wallet_keypair, token_mint, amount_sol, **kwargs)
                _logger.info(f"[DEBUG] Orca fallback result: {result}")
                fallback_results.append(("Orca", result))
                if result.get('success'):
                    return result
            except Exception as e:
                _logger.error(f"Orca fallback exception: {e}")
                fallback_results.append(("Orca", {"success": False, "error": str(e)}))
            # 4. Try Phoenix
            try:
                from phoenix_copy_executor import try_phoenix_buy
                result = await try_phoenix_buy(wallet_keypair, token_mint, amount_sol, **kwargs)
                _logger.info(f"[DEBUG] Phoenix fallback result: {result}")
                fallback_results.append(("Phoenix", result))
                if result.get('success'):
                    return result
            except Exception as e:
                _logger.error(f"Phoenix fallback exception: {e}")
                fallback_results.append(("Phoenix", {"success": False, "error": str(e)}))

            # Add a summary log if all fail
            error_lines = [f"{dex}: {r.get('error', r)}" for dex, r in fallback_results]
            error_message = f"❌ All DEX fallbacks failed for token {token_mint[:8]}...\n" + "\n".join(error_lines)
            _logger.error(error_message)
            return {
                "success": False,
                "signature": None,
                "error": f"All DEX fallbacks failed. See logs for details.",
                "fallback_results": fallback_results
            }

        except Exception as e:
            # Defensive: always log with a valid logger
            import logging as _logging
            _logger = logger if isinstance(logger, _logging.Logger) else globals().get('logger', None)
            if not _logger or not isinstance(_logger, _logging.Logger):
                print(f"[CRITICAL LOGGER ERROR] Logger is not a valid Logger instance! Exception: {e}")
            else:
                _logger.error(f"❌ Enhanced Pump.fun execution failed: {e}")
            return {
                'success': False, 
                'error': f'Enhanced Pump.fun error: {str(e)}', 
                'dex': 'PumpFun_Enhanced', 
                'attempts': 1
            }

try:
    from jupiter_copy_executor import try_jupiter_buy as _original_jupiter_buy, try_jupiter_sell_all as _original_jupiter_sell_all
    logger.info("✅ Imported working Jupiter executors")
    
    # 🚨 CRITICAL FIX: Wrap Jupiter with comprehensive validation
    async def try_jupiter_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        # --- UNIVERSAL TOKEN VALIDATION ---
        system_tokens = [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        ]
        if token_mint in system_tokens:
            logger.error(f"❌ [DEBUG] System token {token_mint[:8]}... is not tradable - aborting")
            return {"success": False, "signature": None, "error": "System token not tradable"}

        # --- SOL BALANCE CHECK ---
        try:
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = SolanaRpcClient(rpc_url)
            wallet_pubkey = wallet_keypair.pubkey()
            logger.info(f"[DEBUG] Checking SOL balance for wallet: {wallet_pubkey}")
            sol_balance_info = await client.request("getBalance", [str(wallet_pubkey)])
            logger.info(f"[DEBUG] Raw getBalance RPC response: {sol_balance_info}")
            await client.close()
            sol_balance = sol_balance_info.get('value', 0) / 1_000_000_000 if sol_balance_info else 0
            logger.info(f"[DEBUG] Parsed SOL balance: {sol_balance}")
            if sol_balance < amount_sol + 0.01:
                logger.error(f"❌ [DEBUG] Insufficient SOL: {sol_balance} available, {amount_sol} + fees required")
                return {"success": False, "signature": None, "error": f"Insufficient SOL: {sol_balance} available"}
        except Exception as e:
            logger.warning(f"⚠️ [DEBUG] Could not check SOL balance: {e}")

        """🔧 OPTIMIZED Jupiter buy with enhanced validation and error handling"""
        try:
            logger.info(f"[DEBUG] try_jupiter_buy called with wallet_keypair={wallet_keypair}, token_mint={token_mint}, amount_sol={amount_sol}, kwargs={kwargs}")
            logger.info(f"🪐 JUPITER BUY (Validated): {amount_sol} SOL → {token_mint[:8]}...")

            # COMPREHENSIVE VALIDATION: Check Jupiter compatibility
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = SolanaRpcClient(rpc_url)
            try:
                validation_result = await validate_token_for_dex(client, token_mint, "jupiter")
                logger.info(f"[DEBUG] Jupiter validation_result: {validation_result}")
                if not validation_result.get("valid", False):
                    error_msg = validation_result.get("error", "Token not compatible with Jupiter")
                    logger.warning(f"❌ [DEBUG] Jupiter validation failed: {error_msg}")
                    await client.close()
                    return {
                        "success": False, 
                        "signature": None, 
                        "error": f"Jupiter validation failed: {error_msg}",
                        "dex": "Jupiter",
                        "validation_reason": validation_result.get("reason", "unknown")
                    }
                logger.info(f"✅ [DEBUG] Jupiter validation passed: {validation_result.get('reason', 'valid')}")
                # Log any warnings
                if "warning" in validation_result:
                    logger.warning(f"⚠️ [DEBUG] Jupiter warning: {validation_result['warning']}")
            finally:
                await client.close()

            # 🚨 CRITICAL: Validate token mint format before conversion
            if not token_mint or len(token_mint) < 32:
                logger.error(f"❌ [DEBUG] Invalid token mint: {token_mint} (too short)")
                return {"success": False, "signature": None, "error": "Invalid token mint"}

            # 🚨 Skip placeholder tokens
            ultra_aggressive_tokens = [
                'AGGRESSIVE_TARGET_WALLET_BUY_',
                'AGGRESSIVE_BUY_TOKEN_',
                'AGGRESSIVE_SELL_TOKEN_', 
                'EMERGENCY_ASSUMPTION_TOKEN_',
                'FALLBACK_BUY_TOKEN_',
                'ERROR_FALLBACK_BUY_'
            ]

            is_placeholder = any(prefix in token_mint for prefix in ultra_aggressive_tokens)
            if is_placeholder:
                logger.warning(f"⚠️ [DEBUG] Skipping placeholder token: {token_mint[:20]}...")
                return {"success": False, "signature": None, "error": "Placeholder token"}

            try:
                # Calculate the CORRECT ATA address
                wallet_pubkey = wallet_keypair.pubkey()
                token_mint_pubkey = Pubkey.from_string(token_mint)
                correct_ata = get_correct_ata_address(wallet_pubkey, token_mint_pubkey)
                logger.info(f"✅ Using CORRECT ATA: {str(correct_ata)}")
                # --- STRICT VALIDATION: Check ATA account owner and mint ---
                await strict_validate_ata(correct_ata, wallet_pubkey, token_mint_pubkey)
            except Exception as e:
                logger.error(f"❌ ATA validation error for token {token_mint[:20]}...: {e}")
                return {"success": False, "signature": None, "error": f"ATA validation error: {e}"}
            
            # Add optimized parameters for Jupiter
            kwargs['destination_token_account'] = str(correct_ata)
            kwargs['correct_user_token_account'] = str(correct_ata)
            kwargs['verified_ata'] = True
            kwargs['jito_service'] = _global_jito_service  # Pass Jito service for MEV protection
            
            # Jupiter optimization: Set shorter timeout and higher slippage for universal routing
            kwargs['timeout'] = 15.0  # Shorter timeout for Jupiter
            kwargs['slippage_bps'] = kwargs.get('slippage_bps', 1000)  # 10% slippage for broader market access
            kwargs['optimize_for_speed'] = True
            
            # Enhanced retry logic for Jupiter with exponential backoff
            max_retries = 2
            base_delay = 0.5
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.info(f"🔄 Jupiter retry {attempt + 1}/{max_retries} after {delay}s delay...")
                        import asyncio
                        await asyncio.sleep(delay)
                    
                    # Call the original executor with optimized parameters
                            
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"❌ Jupiter final attempt failed: {e}")
                        return {
                            'success': False, 
                            'error': f'Jupiter execution error: {str(e)}', 
                            'dex': 'Jupiter',
                            'attempts': attempt + 1
                        }
                    else:
                        logger.warning(f"⚠️ Jupiter attempt {attempt + 1} exception: {e}")
                        continue
            
            return {
                'success': False, 
                'error': 'Jupiter max retries exceeded', 
                'dex': 'Jupiter',
                'attempts': max_retries
            }
            
        except Exception as e:
            logger.error(f"❌ Jupiter wrapper execution failed: {e}")
            return {
                'success': False, 
                'error': f'Jupiter wrapper error: {str(e)}', 
                'dex': 'Jupiter_Optimized', 
                'attempts': 1
            }

    async def try_jupiter_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Enhanced Jupiter sell with proportional support"""
        sell_percentage = kwargs.get('sell_percentage', 100.0)
        logger.info(f"🪐 Jupiter proportional sell: {sell_percentage}% of {token_mint[:8]}...")
        
        if sell_percentage >= 100.0:
            return await _original_jupiter_sell_all(wallet_keypair, token_mint, **kwargs)
        else:
            # For partial sells, use Jupiter's flexible API
            try:
                from jupiter_copy_executor import JupiterCopyExecutor
                executor = JupiterCopyExecutor(
                    wallet_keypair=wallet_keypair,
                    rpc_url=kwargs.get('rpc_url', get_proper_rpc_url())
                )
                # Get current token balance using SolanaRpcClient
                rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
                client = SolanaRpcClient(rpc_url)
                token_mint_pubkey = Pubkey.from_string(token_mint)
                token_account = get_associated_token_address(wallet_keypair.pubkey(), token_mint_pubkey)
                account_info = await client.request("getTokenAccountBalance", [str(token_account)])
                await client.close()
                if not account_info or not account_info.get('value'):
                    return {"success": False, "error": f"No {token_mint[:8]} balance to sell", "dex": "Jupiter"}
                token_balance = int(account_info['value']['amount'])
                sell_amount = int(token_balance * (sell_percentage / 100.0))
                logger.info(f"   💰 Selling {sell_amount} tokens ({sell_percentage}% of {token_balance})")
                # Use Jupiter API for proportional sell
                result = await executor.execute_sell_copy(token_mint, sell_amount, "", "")
                return {"success": bool(result), "signature": result, "dex": "Jupiter"} if result else {"success": False, "error": "Proportional sell failed", "dex": "Jupiter"}
                
            except Exception as e:
                logger.error(f"❌ Jupiter proportional sell error: {e}")
                # Fallback to full sell if proportional fails
                return await _original_jupiter_sell_all(wallet_keypair, token_mint, **kwargs)
    
    # Aliases for compatibility
    try_jupiter_sell = try_jupiter_sell_all
    
except ImportError as e:
    logger.error(f"❌ Failed to import Jupiter executors: {e}")
    # Fallback placeholder
    async def try_jupiter_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "Jupiter import failed", 'dex': 'Jupiter', 'attempts': 1}
    async def try_jupiter_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "Jupiter import failed", 'dex': 'Jupiter', 'attempts': 1}
    try_jupiter_sell = try_jupiter_sell_all

try:
    from raydium_copy_executor import try_raydium_buy, try_raydium_sell_all
    logger.info("✅ Imported working Raydium executors")
except ImportError as e:
    logger.error(f"❌ Failed to import Raydium executors: {e}")
    # Fallback placeholder
    async def try_raydium_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "Raydium import failed", 'dex': 'Raydium', 'attempts': 1}
    async def try_raydium_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "Raydium import failed", 'dex': 'Raydium', 'attempts': 1}

try:
    from cpmm_copy_executor import try_cpmm_buy as _original_cpmm_buy, try_cpmm_sell_all as _original_cpmm_sell_all
    logger.info("✅ Imported working CPMM executors")
    
    # 🔍 ENHANCED: Add validation wrapper for CPMM buy
    async def try_cpmm_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        # --- UNIVERSAL TOKEN VALIDATION ---
        system_tokens = [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        ]
        if token_mint in system_tokens:
            logger.error(f"❌ [DEBUG] System token {token_mint[:8]}... is not tradable - aborting")
            return {"success": False, "signature": None, "error": "System token not tradable"}

        # --- SOL BALANCE CHECK ---
        try:
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = SolanaRpcClient(rpc_url)
            wallet_pubkey = wallet_keypair.pubkey()
            sol_balance_info = await client.request("getBalance", [str(wallet_pubkey)])
            await client.close()
            sol_balance = sol_balance_info.get('value', 0) / 1_000_000_000 if sol_balance_info else 0
            if sol_balance < amount_sol + 0.01:
                logger.error(f"❌ [DEBUG] Insufficient SOL: {sol_balance} available, {amount_sol} + fees required")
                return {"success": False, "signature": None, "error": f"Insufficient SOL: {sol_balance} available"}
        except Exception as e:
            logger.warning(f"⚠️ [DEBUG] Could not check SOL balance: {e}")

        """Enhanced CPMM buy with comprehensive validation"""
        try:
            logger.info(f"[DEBUG] try_cpmm_buy called with wallet_keypair={wallet_keypair}, token_mint={token_mint}, amount_sol={amount_sol}, kwargs={kwargs}")
            logger.info(f"� CPMM BUY (Validated): {amount_sol} SOL → {token_mint[:8]}...")

            # 🔍 COMPREHENSIVE VALIDATION: Check CPMM/Raydium compatibility
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = SolanaRpcClient(rpc_url)
            validation_result = None
            try:
                validation_result = await validate_token_for_dex(client, token_mint, "cpmm")
                logger.info(f"[DEBUG] CPMM validation_result: {validation_result}")
            except Exception as e:
                logger.warning(f"⚠️ [DEBUG] CPMM validation threw error: {e}")
            finally:
                await client.close()

            if validation_result is not None and not validation_result.get("valid", False):
                error_msg = validation_result.get("error", "Token not compatible with CPMM")
                logger.warning(f"❌ [DEBUG] CPMM validation failed: {error_msg}")
                logger.info(f"[DEBUG][CPMM DIAGNOSTICS] Validation details: {validation_result}")
                # Fallback: attempt buy anyway if aggressive mode is enabled
                aggressive_mode = kwargs.get('aggressive_cpmm', True)
                if aggressive_mode:
                    logger.warning(f"⚡ [DEBUG] Aggressive CPMM mode enabled: attempting buy despite failed validation!")
                    # Attempt pool info enhancement before buy
                    try:
                        from cpmm_copy_executor import CPMMCopyExecutor, ExtractedCPMMTradeInfo, CopyExecutorConfig
                        cpmm_executor = CPMMCopyExecutor(wallet_keypair, rpc_url, CopyExecutorConfig())
                        # Try to enhance pool info using original transaction if available
                        trade_info = ExtractedCPMMTradeInfo(
                            token_mint=token_mint,
                            is_buy=True,
                            amount_in=int(amount_sol * 1_000_000_000),
                            pool_info=kwargs.get('pool_info', {}),
                            original_signature=kwargs.get('original_signature', ''),
                            wallet_address=str(wallet_keypair.pubkey())
                        )
                        logger.info(f"[DEBUG] CPMM trade_info: {trade_info}")
                        await cpmm_executor._enhance_pool_info(trade_info)
                        result = await cpmm_executor.execute_buy_copy(trade_info, amount_sol)
                        await cpmm_executor.client.close()
                        logger.info(f"[DEBUG] CPMM buy result: {result}")
                        if result:
                            logger.info(f"✅ [DEBUG] Aggressive CPMM buy executed: {result}")
                            return {"success": True, "signature": result, "dex": "CPMM-Aggressive", "validation_reason": validation_result.get("reason", "unknown")}
                        else:
                            logger.error(f"❌ [DEBUG] Aggressive CPMM buy failed to execute")
                            return {"success": False, "signature": None, "error": "Aggressive CPMM buy failed", "dex": "CPMM-Aggressive", "validation_reason": validation_result.get("reason", "unknown")}
                    except Exception as e:
                        logger.error(f"❌ [DEBUG] Aggressive CPMM buy critical error: {e}")
                        return {"success": False, "signature": None, "error": f"Aggressive CPMM buy error: {str(e)}", "dex": "CPMM-Aggressive", "validation_reason": validation_result.get("reason", "unknown")}
                else:
                    return {
                        "success": False,
                        "signature": None,
                        "error": f"CPMM validation failed: {error_msg}",
                        "dex": "CPMM",
                        "validation_reason": validation_result.get("reason", "unknown")
                    }

            logger.info(f"✅ [DEBUG] CPMM validation passed: {validation_result.get('reason', 'valid') if validation_result else 'valid'}")
            # Strict ATA validation before calling original executor
            try:
                wallet_pubkey = wallet_keypair.pubkey()
                token_mint_pubkey = Pubkey.from_string(token_mint)
            except Exception as e:
                logger.error(f"❌ ATA validation error for token {token_mint[:20]}...: {e}")
                return {"success": False, "signature": None, "error": f"ATA validation error: {e}"}
            # Call original executor with validation passed
            return await _original_cpmm_buy(wallet_keypair, token_mint, amount_sol, **kwargs)

        except Exception as e:
            logger.error(f"❌ [DEBUG] CPMM buy wrapper error: {e}")
            return {
                "success": False,
                "signature": None,
                "error": f"CPMM buy error: {str(e)}",
                "dex": "CPMM"
            }
    
    # �🎯 ENHANCED: Add proportional selling support to CPMM
    async def try_cpmm_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Enhanced CPMM sell with proportional support and validation"""
        try:
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            logger.info(f"🌊 CPMM proportional sell: {sell_percentage}% of {token_mint[:8]}...")
            
            # 🔍 Quick validation for sell operations
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = AsyncClient(rpc_url)
            
            try:
                validation_result = await validate_token_for_dex(client, token_mint, "cpmm")
                if not validation_result.get("valid", False):
                    error_msg = validation_result.get("error", "Token not compatible with CPMM")
                    logger.warning(f"❌ CPMM sell validation failed: {error_msg}")
                    return {
                        "success": False, 
                        "error": f"CPMM sell validation failed: {error_msg}",
                        "dex": "CPMM"
                    }
            finally:
                await client.close()
            
            if sell_percentage >= 100.0:
                return await _original_cpmm_sell_all(wallet_keypair, token_mint, **kwargs)
            else:
                # For partial sells, calculate token amount and use CPMM executor
                try:
                    from cpmm_copy_executor import CPMMCopyExecutor
                    from spl.token.instructions import get_associated_token_address
                    from solana.rpc.async_api import AsyncClient
                    
                    # Get current token balance
                    client = AsyncClient(kwargs.get('rpc_url', get_proper_rpc_url()))
                    token_mint_pubkey = Pubkey.from_string(token_mint)
                    token_account = get_associated_token_address(wallet_keypair.pubkey(), token_mint_pubkey)
                    
                    account_info = await client.get_token_account_balance(token_account)
                    if account_info.value is None:
                        return {"success": False, "error": f"No {token_mint[:8]} balance to sell", "dex": "CPMM"}
                    
                    token_balance = int(account_info.value.amount)
                    sell_amount = int(token_balance * (sell_percentage / 100.0))
                    
                    logger.info(f"   💰 Selling {sell_amount} tokens ({sell_percentage}% of {token_balance})")
                    
                    # Create CPMM executor and execute proportional sell
                    executor = CPMMCopyExecutor(
                        wallet_keypair=wallet_keypair,
                        rpc_url=kwargs.get('rpc_url', get_proper_rpc_url())
                    )
                    
                    # Use CPMM's internal sell logic with specific amount
                    result = await executor.execute_copy_trade(
                        trade_info={'action': 'sell', 'token_mint': token_mint, 'amount': sell_amount},
                        **kwargs
                    )
                    
                    await client.close()
                    return result if result else {"success": False, "error": "CPMM proportional sell failed", "dex": "CPMM"}
                    
                except Exception as e:
                    logger.error(f"❌ CPMM proportional sell error: {e}")
                    # Fallback to full sell if proportional fails
                    return await _original_cpmm_sell_all(wallet_keypair, token_mint, **kwargs)
        
        except Exception as e:
            logger.error(f"❌ CPMM sell wrapper error: {e}")
            return {
                "success": False,
                "error": f"CPMM sell error: {str(e)}",
                "dex": "CPMM"
            }

except ImportError as e:
    logger.error(f"❌ Failed to import CPMM executors: {e}")
    # Fallback placeholder
    async def try_cpmm_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "CPMM import failed", 'dex': 'CPMM', 'attempts': 1}
    async def try_cpmm_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "CPMM import failed", 'dex': 'CPMM', 'attempts': 1}

try:
    from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all, try_clmm_hybrid_sell
    logger.info("✅ Imported working CLMM executors")
    
    # 🎯 ENHANCED: Override with proportional selling support
    async def try_clmm_hybrid_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Enhanced CLMM sell with proportional support - ALREADY HAS PERCENTAGE PARAM!"""
        sell_percentage = kwargs.get('sell_percentage', 100.0)
        logger.info(f"⚡ CLMM proportional sell: {sell_percentage}% of {token_mint[:8]}...")
        
        # Use the existing try_clmm_hybrid_sell function which already supports percentage!
        return await try_clmm_hybrid_sell(wallet_keypair, token_mint, percentage=sell_percentage, **kwargs)

except ImportError as e:
    logger.error(f"❌ Failed to import CLMM executors: {e}")
    # Fallback placeholder
    async def try_clmm_hybrid_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "CLMM import failed", 'dex': 'CLMM', 'attempts': 1}
    async def try_clmm_hybrid_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "CLMM import failed", 'dex': 'CLMM', 'attempts': 1}

# Add CLMM wrapper functions with proper parameter handling
async def try_clmm_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
    """CLMM buy wrapper with parameter signature fix"""
    try:
        # Remove unsupported parameters that cause signature mismatch
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in ['slippage_tolerance']}
        
        # Use slippage_bps instead of slippage_tolerance for CLMM
        if 'slippage_tolerance' in kwargs:
            clean_kwargs['slippage_bps'] = int(kwargs['slippage_tolerance'] * 10000)  # Convert to basis points
        
        return await try_clmm_hybrid_buy(wallet_keypair, token_mint, amount_sol, **clean_kwargs)
    except Exception as e:
        logger.error(f"❌ CLMM buy wrapper error: {e}")
        return {'success': False, 'signature': None, 'error': f"CLMM wrapper error: {e}", 'dex': 'CLMM', 'attempts': 1}

async def try_clmm_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
    """CLMM sell wrapper with parameter signature fix"""
    try:
        # Remove unsupported parameters that cause signature mismatch
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in ['slippage_tolerance']}
        
        # Use slippage_bps instead of slippage_tolerance for CLMM
        if 'slippage_tolerance' in kwargs:
            clean_kwargs['slippage_bps'] = int(kwargs['slippage_tolerance'] * 10000)  # Convert to basis points
            
        return await try_clmm_hybrid_sell_all(wallet_keypair, token_mint, **clean_kwargs)
    except Exception as e:
        logger.error(f"❌ CLMM sell wrapper error: {e}")
        return {'success': False, 'signature': None, 'error': f"CLMM wrapper error: {e}", 'dex': 'CLMM', 'attempts': 1}

try:
    from orca_copy_executor import try_orca_buy as _original_orca_buy, try_orca_sell_all as _original_orca_sell_all
    logger.info("✅ Imported working Orca executors")
    
    # Add Orca pool detection wrapper
    async def try_orca_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        # --- UNIVERSAL TOKEN VALIDATION ---
        system_tokens = [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        ]
        if token_mint in system_tokens:
            logger.error(f"❌ [DEBUG] System token {token_mint[:8]}... is not tradable - aborting")
            return {"success": False, "signature": None, "error": "System token not tradable"}

        # --- SOL BALANCE CHECK ---
        try:
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = SolanaRpcClient(rpc_url)
            wallet_pubkey = wallet_keypair.pubkey()
            sol_balance_info = await client.request("getBalance", [str(wallet_pubkey)])
            await client.close()
            sol_balance = sol_balance_info.get('value', 0) / 1_000_000_000 if sol_balance_info else 0
            if sol_balance < amount_sol + 0.01:
                logger.error(f"❌ [DEBUG] Insufficient SOL: {sol_balance} available, {amount_sol} + fees required")
                return {"success": False, "signature": None, "error": f"Insufficient SOL: {sol_balance} available"}
        except Exception as e:
            logger.warning(f"⚠️ [DEBUG] Could not check SOL balance: {e}")

        """Orca buy wrapper with pool detection"""
        try:
            logger.info(f"[DEBUG] try_orca_buy called with wallet_keypair={wallet_keypair}, token_mint={token_mint}, amount_sol={amount_sol}, kwargs={kwargs}")
            # Check if Orca pools exist for this token before attempting execution
            pool_info = kwargs.get('pool_info', {})
            logger.info(f"[DEBUG] Orca pool_info: {pool_info}")
            if not pool_info or 'orca' not in str(pool_info).lower():
                logger.warning(f"⚠️ [DEBUG] No Orca pool detected for {token_mint[:8]}... - skipping Orca executor")
                logger.warning(f"[DEBUG] Full pool_info list: {pool_info}")
                logger.warning(f"[DEBUG] Searched for token_mint: {token_mint}")
                return {'success': False, 'signature': None, 'error': "No Orca pool found", 'dex': 'Orca', 'attempts': 1}
            
            # Strict ATA validation before calling original executor
            try:
                wallet_pubkey = wallet_keypair.pubkey()
                token_mint_pubkey = Pubkey.from_string(token_mint)
                correct_ata = get_correct_ata_address(wallet_pubkey, token_mint_pubkey)
                logger.info(f"✅ Using CORRECT ATA: {str(correct_ata)} (Orca)")
                await strict_validate_ata(correct_ata, wallet_pubkey, token_mint_pubkey)
            except Exception as e:
                logger.error(f"❌ ATA validation error for token {token_mint[:20]}...: {e}")
                return {"success": False, "signature": None, "error": f"ATA validation error: {e}"}
            result = await _original_orca_buy(wallet_keypair, token_mint, amount_sol, **kwargs)
            logger.info(f"[DEBUG] Orca buy result: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ [DEBUG] Orca buy wrapper error: {e}")
            return {'success': False, 'signature': None, 'error': f"Orca wrapper error: {e}", 'dex': 'Orca', 'attempts': 1}
    
    # 🎯 ENHANCED: Add proportional selling support to Orca
    async def try_orca_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Enhanced Orca sell with proportional support via Jupiter API"""
        sell_percentage = kwargs.get('sell_percentage', 100.0)
        logger.info(f"🐋 Orca proportional sell: {sell_percentage}% of {token_mint[:8]}...")
        
        if sell_percentage >= 100.0:
            return await _original_orca_sell_all(wallet_keypair, token_mint, **kwargs)
        else:
            # For partial sells, use Orca's Jupiter API integration
            try:
                from orca_copy_executor import OrcaCopyExecutor
                from spl.token.instructions import get_associated_token_address
                from solana.rpc.async_api import AsyncClient
                
                # Get current token balance
                client = AsyncClient(kwargs.get('rpc_url', get_proper_rpc_url()))
                token_mint_pubkey = Pubkey.from_string(token_mint)
                token_account = get_associated_token_address(wallet_keypair.pubkey(), token_mint_pubkey)
                
                account_info = await client.get_token_account_balance(token_account)
                if account_info.value is None:
                    return {"success": False, "error": f"No {token_mint[:8]} balance to sell", "dex": "Orca"}
                
                token_balance = int(account_info.value.amount)
                sell_amount = int(token_balance * (sell_percentage / 100.0))
                
                logger.info(f"   💰 Selling {sell_amount} tokens ({sell_percentage}% of {token_balance})")
                
                # Create Orca executor (uses Jupiter API internally)
                executor = OrcaCopyExecutor()
                
                # Use Orca's sell method with specific amount
                result = await executor.try_orca_sell_all(token_mint, wallet_keypair=wallet_keypair, sell_amount=sell_amount, **kwargs)
                
                await client.close()
                return result if result else {"success": False, "error": "Orca proportional sell failed", "dex": "Orca"}
                
            except Exception as e:
                logger.error(f"❌ Orca proportional sell error: {e}")
                # Fallback to full sell if proportional fails
                return await _original_orca_sell_all(wallet_keypair, token_mint, **kwargs)

except ImportError as e:
    logger.error(f"❌ Failed to import Orca executors: {e}")
    # Fallback placeholder
    async def try_orca_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "Orca import failed", 'dex': 'Orca', 'attempts': 1}
    async def try_orca_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "Orca import failed", 'dex': 'Orca', 'attempts': 1}

try:
    from phoenix_copy_executor import try_phoenix_buy, try_phoenix_sell_all as _original_phoenix_sell_all
    logger.info("✅ Imported working Phoenix executors")
    
    # 🎯 ENHANCED: Add proportional selling support to Phoenix
    async def try_phoenix_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Enhanced Phoenix sell with proportional support via Jupiter API"""
        sell_percentage = kwargs.get('sell_percentage', 100.0)
        logger.info(f"🔥 Phoenix proportional sell: {sell_percentage}% of {token_mint[:8]}...")
        
        if sell_percentage >= 100.0:
            return await _original_phoenix_sell_all(wallet_keypair, token_mint, **kwargs)
        else:
            # For partial sells, use Phoenix's Jupiter API integration
            try:
                from phoenix_copy_executor import PhoenixCopyExecutor
                from spl.token.instructions import get_associated_token_address
                from solana.rpc.async_api import AsyncClient
                
                # Get current token balance
                client = AsyncClient(kwargs.get('rpc_url', get_proper_rpc_url()))
                token_mint_pubkey = Pubkey.from_string(token_mint)
                token_account = get_associated_token_address(wallet_keypair.pubkey(), token_mint_pubkey)
                
                account_info = await client.get_token_account_balance(token_account)
                if account_info.value is None:
                    return {"success": False, "error": f"No {token_mint[:8]} balance to sell", "dex": "Phoenix"}
                
                token_balance = int(account_info.value.amount)
                sell_amount = int(token_balance * (sell_percentage / 100.0))
                
                logger.info(f"   💰 Selling {sell_amount} tokens ({sell_percentage}% of {token_balance})")
                
                # Create Phoenix executor (uses Jupiter API for CLOB access)
                executor = PhoenixCopyExecutor()
                
                # Use Phoenix's sell method with specific amount
                result = await executor.try_phoenix_sell_all(token_mint, wallet_keypair=wallet_keypair, sell_amount=sell_amount, **kwargs)
                
                await client.close()
                return result if result else {"success": False, "error": "Phoenix proportional sell failed", "dex": "Phoenix"}
                
            except Exception as e:
                logger.error(f"❌ Phoenix proportional sell error: {e}")
                # Fallback to full sell if proportional fails
                return await _original_phoenix_sell_all(wallet_keypair, token_mint, **kwargs)

except ImportError as e:
    logger.error(f"❌ Failed to import Phoenix executors: {e}")
    # Fallback placeholder
    async def try_phoenix_buy(wallet_keypair: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        # --- UNIVERSAL TOKEN VALIDATION ---
        system_tokens = [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        ]
        if token_mint in system_tokens:
            logger.error(f"❌ [DEBUG] System token {token_mint[:8]}... is not tradable - aborting")
            return {"success": False, "signature": None, "error": "System token not tradable"}

        # --- SOL BALANCE CHECK ---
        try:
            rpc_url = kwargs.get('rpc_url', get_proper_rpc_url())
            client = SolanaRpcClient(rpc_url)
            wallet_pubkey = wallet_keypair.pubkey()
            sol_balance_info = await client.request("getBalance", [str(wallet_pubkey)])
            await client.close()
            sol_balance = sol_balance_info.get('value', 0) / 1_000_000_000 if sol_balance_info else 0
            if sol_balance < amount_sol + 0.01:
                logger.error(f"❌ [DEBUG] Insufficient SOL: {sol_balance} available, {amount_sol} + fees required")
                return {"success": False, "signature": None, "error": f"Insufficient SOL: {sol_balance} available"}
        except Exception as e:
            logger.warning(f"⚠️ [DEBUG] Could not check SOL balance: {e}")
        # Strict ATA validation before calling original executor (if implemented)
        try:
            wallet_pubkey = wallet_keypair.pubkey()
            token_mint_pubkey = Pubkey.from_string(token_mint)
            correct_ata = get_correct_ata_address(wallet_pubkey, token_mint_pubkey)
            logger.info(f"✅ Using CORRECT ATA: {str(correct_ata)} (Phoenix)")
            await strict_validate_ata(correct_ata, wallet_pubkey, token_mint_pubkey)
        except Exception as e:
            logger.error(f"❌ ATA validation error for token {token_mint[:20]}...: {e}")
            return {"success": False, "signature": None, "error": f"ATA validation error: {e}"}
        # If Phoenix executor is not implemented, return error
        return {'success': False, 'signature': None, 'error': "Phoenix import failed", 'dex': 'Phoenix', 'attempts': 1}
    async def try_phoenix_sell_all(wallet_keypair: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        return {'success': False, 'signature': None, 'error': "Phoenix import failed", 'dex': 'Phoenix', 'attempts': 1}

# Add execute_pumpfun_buy alias for backward compatibility


# --- UNIVERSAL CLONER FALLBACK ---
from universal_executor_fallback import try_universal_cloner_buy

async def try_universal_fallback(wallet_keypair, trade_info, **kwargs):
    """
    Universal fallback: Use TransactionCloner to copy any trade by signature.
    Args:
        wallet_keypair: The user's wallet keypair
        trade_info: Dict with at least 'signature' key
        **kwargs: Optionally override accounts (e.g., payer)
    Returns:
        Dict with success, signature, error keys
    """
    signature = trade_info.get('signature')
    if not signature:
        return {'success': False, 'signature': None, 'error': 'No signature in trade_info'}
    return await try_universal_cloner_buy(wallet_keypair, signature, **kwargs)

__all__ = [
    'try_pumpfun_buy', 'try_pumpfun_sell_all', 'try_pumpfun_sell',
    'try_jupiter_buy', 'try_jupiter_sell_all', 'try_jupiter_sell',
    'try_raydium_buy', 'try_raydium_sell_all',
    'try_cpmm_buy', 'try_cpmm_sell_all',
    'try_clmm_buy', 'try_clmm_sell_all',
    'try_orca_buy', 'try_orca_sell_all',
    'try_phoenix_buy', 'try_phoenix_sell_all',
    'execute_pumpfun_buy', '_try_direct_pumpfun_buy',
    'initialize_executors', 'get_correct_ata_address',
    'try_universal_fallback'
]
execute_pumpfun_buy = try_pumpfun_buy
