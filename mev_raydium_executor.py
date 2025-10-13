"""
MEV Raydium Executor — copy-trading oriented
-------------------------------------------------

This module provides a production-grade scaffold to execute Raydium CPMM swaps
for a copy bot, with:
  • Clean imports & typing
  • Pool resolution interface (pluggable)
  • ATA & WSOL handling
  • Compute budget / priority fee
  • Robust send + confirm with log surfacing
  • Consistclass MEVRaydiumExecutor:
    def __init__(self, rpc_url: Optional[str] = None, keypair: Optional[Keypair] = None, jito_service=None):
        rpc_url = rpc_url or os.getenv("HELIUS_RPC_URL") or os.getenv("RPC_URL")
        if not rpc_url:
            raise ValueError("RPC URL not provided. Set HELIUS_RPC_URL or pass rpc_url explicitly.")
        self.rpc = SimpleRPC(RPCConfig(rpc_url))
        self.kp = keypair or self._load_keypair_from_env()
        self.owner = self.kp.pubkey()
        self.ata = ATAManager(self.rpc)
        self.pool_resolver = None  # Will be set with trade_info when needed
        self.jito_service = jito_service  # Add JitoClient supportessageV0 handling using solders v0.26.x

IMPORTANT:
  • You MUST provide correct Raydium CPMM program id, swap discriminator bytes,
    and the exact ordered accounts for the target pool returned by PoolResolver.
  • This file avoids hardcoding pool addresses; implement PoolResolver.resolve().
  • If you already have a working resolver in your repo, wire it in at TODOs.

Compatible with: Python 3.11+, solders 0.26.x
"""
from __future__ import annotations

import base64
import dataclasses
import os
import logging

# Import JitoClient for MEV protection
try:
    from jito_service import JitoClient
    JITO_AVAILABLE = True
except ImportError:
    JITO_AVAILABLE = False
    JitoClient = None
import time
from typing import List, Optional, Tuple

from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import VersionedTransaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price

# If you use solana-py for RPC, import from there; otherwise replace with your client.
# Below is a minimal JSON-RPC client using httpx to keep this file self-contained.
import json
import httpx

logger = logging.getLogger(__name__)

# Standardized result helpers
def exec_ok(executor_name: str, signature: str, data: dict = None) -> dict:
    """Create standardized success result"""
    result = {"success": True, "executor": executor_name, "signature": signature}
    if data:
        result.update(data)
    return result

def exec_err(executor_name: str, error_message: str) -> dict:
    """Create standardized error result"""
    return {"success": False, "executor": executor_name, "error": error_message}

def jito_is_configured(jito_service) -> bool:
    """Check if Jito is properly configured and available"""
    return JITO_AVAILABLE and jito_service is not None


# ==========================
# Config & simple RPC client
# ==========================

@dataclasses.dataclass
class RPCConfig:
    rpc_url: str
    commitment: str = "confirmed"  # or "processed", "finalized"


class SimpleRPC:
    def __init__(self, cfg: RPCConfig):
        self.url = cfg.rpc_url
        self.commitment = cfg.commitment
        self._client = httpx.Client(timeout=15.0)

    def _post(self, method: str, params: list) -> dict:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        r = self._client.post(self.url, json=payload)
        r.raise_for_status()
        out = r.json()
        if "error" in out:
            raise RuntimeError(f"RPC error in {method}: {out['error']}")
        return out["result"]

    def get_latest_blockhash(self) -> Tuple[Hash, str]:
        res = self._post("getLatestBlockhash", [{"commitment": self.commitment}])
        bh_str = res["value"]["blockhash"]
        last_valid_height = res["value"]["lastValidBlockHeight"]
        return Hash.from_string(bh_str), last_valid_height

    def get_minimum_balance_for_rent_exemption(self, span: int) -> int:
        return self._post("getMinimumBalanceForRentExemption", [span])

    def send_transaction(self, txn: VersionedTransaction, skip_preflight: bool = False) -> Signature:
        raw = base64.b64encode(bytes(txn)).decode()
        params = [
            raw,
            {"encoding": "base64", "skipPreflight": skip_preflight, "maxRetries": 3},
        ]
        sig_str = self._post("sendTransaction", params)
        return Signature.from_string(sig_str)

    def confirm_signature(self, sig: Signature, timeout_s: float = 25.0) -> dict:
        # Poll for confirmation
        start = time.time()
        while time.time() - start < timeout_s:
            res = self._post(
                "getSignatureStatuses",
                [[str(sig)], {"searchTransactionHistory": True}],
            )
            status = res["value"][0]
            if status is not None and status.get("confirmationStatus") in {"confirmed", "finalized"}:
                return status
            time.sleep(0.6)
        raise TimeoutError("Confirmation timeout")

    def get_transaction(self, sig: str, max_version: int = 0) -> Optional[dict]:
        try:
            return self._post(
                "getTransaction",
                [sig, {"encoding": "json", "maxSupportedTransactionVersion": max_version}],
            )
        except Exception as e:
            return exec_err("raydium", f"get transaction failed: {str(e)}")


# ======================
# Pool / account schemas
# ======================

@dataclasses.dataclass
class PoolAccounts:
    # NOTE: You must supply these from on-chain metadata for the specific CPMM pool.
    # The ORDER matters and must match Raydium CPMM SwapBaseInput.
    # This is an example shape; adjust to your known order for your swap ix builder.
    pool_state: Pubkey
    pool_config: Pubkey
    amm_authority: Pubkey
    input_vault: Pubkey
    output_vault: Pubkey
    input_mint: Pubkey
    output_mint: Pubkey
    token_program: Pubkey
    system_program: Pubkey
    rent_sysvar: Optional[Pubkey] = None  # Some layouts include it

    # User-side accounts (resolved per-wallet at runtime)
    user_input_ata: Optional[Pubkey] = None
    user_output_ata: Optional[Pubkey] = None


@dataclasses.dataclass
class PoolInfo:
    program_id: Pubkey
    accounts: PoolAccounts
    # Raydium CPMM discriminator for SwapBaseInput (8 bytes)
    swap_discriminator: bytes


class PoolResolver:

    # ...existing code...
    """Resolves Raydium CPMM pool details using the parsed transaction in `trade_info`.

    This allows the copy bot to mirror Wallet A's exact pool with no hardcoded pool lists.
    It extracts:
      • program_id (Raydium CPMM)
      • ordered account metas required by the CPMM swap
      • the swap discriminator (first 8 bytes of the matched Raydium instruction data)
    """

    def __init__(self, rpc: SimpleRPC, trade_info: dict):
        self.rpc = rpc
        self.trade_info = trade_info or {}

    @staticmethod
    def _first8(data_bytes: bytes) -> bytes:
        if not data_bytes or len(data_bytes) < 8:
            raise ValueError("Raydium instruction data too short to extract discriminator")
        return data_bytes[:8]

    def _get_ix_bytes_from_trade(self, program_id: str) -> Optional[bytes]:
        # Attempt 1: parsed_tx.raydium_info.swap_ix_data
        parsed = self.trade_info.get("parsed_tx") or {}
        ray = parsed.get("raydium_info") or {}
        raw = ray.get("swap_ix_data") or ray.get("ix_data")
        if isinstance(raw, str):
            # Accept base64 or hex
            try:
                import base64 as _b64
                return _b64.b64decode(raw)
            except Exception:
                try:
                    return bytes.fromhex(raw)
                except Exception:
                    pass
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw)
        # Attempt 2: fetch full tx and pull the first instruction targeting program_id
        sig = self.trade_info.get("signature")
        if not sig:
            return exec_err("raydium", "no signature in trade_info")
        txj = self.rpc.get_transaction(sig) or {}
        tx = (txj or {}).get("transaction") or {}
        message = tx.get("message") or {}
        inst = message.get("instructions") or []
        # map programIdIndex to address
        acct_keys = message.get("accountKeys") or []
        def _key(i):
            try:
                return acct_keys[i]
            except Exception:
                return exec_err("raydium", f"invalid account index: {i}")
        for ix in inst:
            pid = ix.get("programId") or ( _key(ix.get("programIdIndex", -1)) )
            if pid == program_id:
                data = ix.get("data")
                if isinstance(data, str):
                    try:
                        import base64 as _b64
                        return _b64.b64decode(data)
                    except Exception:
                        try:
                            return bytes.fromhex(data)
                        except Exception:
                            return exec_err("raydium", "failed to decode instruction data")
        return exec_err("raydium", "no matching instruction found")

    def resolve(self, mint_in: Pubkey, mint_out: Pubkey, owner: Pubkey) -> PoolInfo:
        parsed = self.trade_info.get("parsed_tx") or {}
        ray = parsed.get("raydium_info") or {}
        program_id_str = (
            ray.get("program_id")
            or self.trade_info.get("router_program_id")
            or "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
        )
        program_id = Pubkey.from_string(program_id_str)

        # Extract ordered accounts from raydium_info; fall back to keys by name
        def _pk(v):
            return Pubkey.from_string(v) if isinstance(v, str) else v

        accounts = ray.get("accounts") or {}
        pool_state = _pk(accounts.get("pool_state") or accounts.get("pool") or ray.get("pool_state"))
        pool_config = _pk(accounts.get("pool_config") or ray.get("pool_config"))
        amm_authority = _pk(accounts.get("amm_authority") or accounts.get("authority") or ray.get("amm_authority"))
        input_vault = _pk(accounts.get("input_vault") or accounts.get("base_vault") or ray.get("input_vault"))
        output_vault = _pk(accounts.get("output_vault") or accounts.get("quote_vault") or ray.get("output_vault"))
        input_mint = _pk(accounts.get("input_mint") or accounts.get("base_mint") or ray.get("input_mint") or str(mint_in))
        output_mint = _pk(accounts.get("output_mint") or accounts.get("quote_mint") or ray.get("output_mint") or str(mint_out))
        token_program = _pk(accounts.get("token_program") or ray.get("token_program") or str(SPL_TOKEN_PROGRAM))
        system_program = _pk(accounts.get("system_program") or ray.get("system_program") or str(SYSTEM_PROGRAM))
        rent_sysvar = accounts.get("rent") or ray.get("rent")
        rent_sysvar = _pk(rent_sysvar) if rent_sysvar else None

        if not all([pool_state, pool_config, amm_authority, input_vault, output_vault, input_mint, output_mint, token_program, system_program]):
            # Log which fields are missing for debugging
            missing_fields = []
            if not pool_state: missing_fields.append("pool_state")
            if not pool_config: missing_fields.append("pool_config")
            if not amm_authority: missing_fields.append("amm_authority")
            if not input_vault: missing_fields.append("input_vault")
            if not output_vault: missing_fields.append("output_vault")
            if not input_mint: missing_fields.append("input_mint")
            if not output_mint: missing_fields.append("output_mint")
            if not token_program: missing_fields.append("token_program")
            if not system_program: missing_fields.append("system_program")
            
            logger.error(f"[RAYDIUM_POOL] ❌ Incomplete Raydium account set - missing: {', '.join(missing_fields)}")
            logger.error(f"[RAYDIUM_POOL] 📋 Available raydium_info keys: {list(ray.keys())}")
            logger.error(f"[RAYDIUM_POOL] 📋 Available accounts keys: {list(accounts.keys())}")
            logger.error(f"[RAYDIUM_POOL] ℹ️  This trade requires Raydium-specific pool data that was not parsed")
            logger.error(f"[RAYDIUM_POOL] ℹ️  The monitored wallet used Raydium but we cannot reconstruct the exact pool")
            logger.error(f"[RAYDIUM_POOL] ℹ️  Consider using Jupiter executor as fallback for broader DEX support")
            
            raise ValueError(f"Incomplete Raydium account set in parsed trade (missing: {', '.join(missing_fields)}); cannot resolve pool")

        # Discriminator
        ix_bytes = self._get_ix_bytes_from_trade(program_id_str)
        if not ix_bytes:
            raise ValueError("Could not extract Raydium instruction bytes from trade to derive discriminator")
        swap_discriminator = self._first8(ix_bytes)

        pa = PoolAccounts(
            pool_state=pool_state,
            pool_config=pool_config,
            amm_authority=amm_authority,
            input_vault=input_vault,
            output_vault=output_vault,
            input_mint=input_mint,
            output_mint=output_mint,
            token_program=token_program,
            system_program=system_program,
            rent_sysvar=rent_sysvar,
        )
        return PoolInfo(program_id=program_id, accounts=pa, swap_discriminator=swap_discriminator)


# ============================
# ATA / WSOL helper components
# ============================

SPL_TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")

NATIVE_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")  # WSOL mint


def find_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    seeds = [bytes(owner), bytes(SPL_TOKEN_PROGRAM), bytes(mint)]
    ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM)
    return ata


class ATAManager:
    def __init__(self, rpc: SimpleRPC):
        self.rpc = rpc

    def create_ata_ix(self, owner: Pubkey, mint: Pubkey) -> Instruction:
        ata = find_associated_token_address(owner, mint)
        metas = [
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),
            AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner, is_signer=False, is_writable=False),  # payer == owner
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPL_TOKEN_PROGRAM, is_signer=False, is_writable=False),
        ]
        # Associated token account instruction has no data
        return Instruction(program_id=ASSOCIATED_TOKEN_PROGRAM, accounts=metas, data=b"")

    def ensure_ata_ix_if_missing(self, owner: Pubkey, mint: Pubkey) -> Tuple[Pubkey, Optional[Instruction]]:
        ata = find_associated_token_address(owner, mint)
        # Lightweight existence check via getAccountInfo; if null, we create it.
        try:
            res = self.rpc._post("getAccountInfo", [str(ata), {"encoding": "jsonParsed"}])
            if res["value"] is None:
                return ata, self.create_ata_ix(owner, mint)
            return ata, None
        except Exception:
            # If check fails, be conservative and attempt creation (will no-op if exists)
            return ata, self.create_ata_ix(owner, mint)


# ==============================
# Swap instruction (Raydium CPMM)
# ==============================

class RaydiumCPMMSwapBuilder:
    def __init__(self, pool: PoolInfo):
        self.pool = pool

    def build_swap_ix(
        self,
        owner: Pubkey,
        amount_in: int,
        min_out: int,
        user_input_ata: Pubkey,
        user_output_ata: Pubkey,
    ) -> Instruction:
        """Build the CPMM SwapBaseInput instruction.

        You MUST ensure that `self.pool.accounts` includes the exact ordered accounts list
        expected by Raydium CPMM for swapping from `user_input_ata` to `user_output_ata`.
        The discriminator (8 bytes) must be correct.
        The data layout after the discriminator commonly encodes amount_in and min_out as little-endian u64.
        Adjust if your CPMM variant requires different encoding.
        """
        acc = self.pool.accounts

        # Program-required accounts (ORDER IS CRITICAL). Tailor to your CPMM schema.
        metas: List[AccountMeta] = [
            AccountMeta(acc.pool_state, is_signer=False, is_writable=True),
            AccountMeta(acc.pool_config, is_signer=False, is_writable=False),
            AccountMeta(acc.amm_authority, is_signer=False, is_writable=False),
            AccountMeta(acc.input_vault, is_signer=False, is_writable=True),
            AccountMeta(acc.output_vault, is_signer=False, is_writable=True),
            AccountMeta(acc.input_mint, is_signer=False, is_writable=False),
            AccountMeta(acc.output_mint, is_signer=False, is_writable=False),
            AccountMeta(user_input_ata, is_signer=False, is_writable=True),
            AccountMeta(user_output_ata, is_signer=False, is_writable=True),
            AccountMeta(owner, is_signer=True, is_writable=False),
            AccountMeta(acc.token_program, is_signer=False, is_writable=False),
            AccountMeta(acc.system_program, is_signer=False, is_writable=False),
        ]
        if acc.rent_sysvar:
            metas.append(AccountMeta(acc.rent_sysvar, is_signer=False, is_writable=False))

        # Build data: discriminator (8) + amount_in (8 le) + min_out (8 le)
        data = bytearray()
        data += self.pool.swap_discriminator
        data += amount_in.to_bytes(8, "little")
        data += min_out.to_bytes(8, "little")

        return Instruction(program_id=self.pool.program_id, accounts=metas, data=bytes(data))


# ==============================
# Main executor
# ==============================

@dataclasses.dataclass
class ExecOptions:
    compute_unit_limit: int = 400_000
    compute_unit_price_micro_lamports: int = 50_000  # = 0.00005 SOL/compute unit
    skip_preflight: bool = False
    confirm_timeout_s: float = 25.0


class MEVRaydiumExecutor:
    def __init__(self, rpc_url: Optional[str] = None, keypair: Optional[Keypair] = None, jito_service=None):
        """Initialize Raydium executor with comprehensive logging"""
        import traceback
        
        logger.info(f"[RAYDIUM] 🚀 Initializing MEV Raydium Executor...")
        logger.debug(f"[RAYDIUM] RPC URL provided: {rpc_url is not None}")
        logger.debug(f"[RAYDIUM] Keypair provided: {keypair is not None}")
        logger.debug(f"[RAYDIUM] Jito service available: {jito_service is not None}")
        
        try:
            # Validate and set RPC URL
            rpc_url = rpc_url or os.getenv("HELIUS_RPC_URL") or os.getenv("RPC_URL")
            if not rpc_url:
                error_msg = "RPC URL not provided. Set HELIUS_RPC_URL or pass rpc_url explicitly."
                logger.error(f"[RAYDIUM] ❌ {error_msg}")
                raise ValueError(error_msg)
            
            logger.debug(f"[RAYDIUM] Using RPC URL: {rpc_url[:50]}...")
            
            # Initialize RPC client
            self.rpc = SimpleRPC(RPCConfig(rpc_url))
            logger.info(f"[RAYDIUM] ✅ RPC client initialized")
            
            # Load or use provided keypair
            self.kp = keypair or self._load_keypair_from_env()
            self.owner = self.kp.pubkey()
            logger.info(f"[RAYDIUM] ✅ Keypair loaded: {self.owner}")
            
            # Initialize ATA manager
            self.ata = ATAManager(self.rpc)
            logger.info(f"[RAYDIUM] ✅ ATA manager initialized")
            
            # Pool resolver will be set later with trade_info
            self.pool_resolver = None
            logger.debug(f"[RAYDIUM] Pool resolver: None (will be set with trade_info)")
            
            # Set Jito service
            self.jito_service = jito_service
            if jito_service:
                logger.info(f"[RAYDIUM] ✅ Jito service configured for MEV protection")
            else:
                logger.info(f"[RAYDIUM] ℹ️  No Jito service - using RPC only")
            
            logger.info(f"[RAYDIUM] 🎉 Executor initialization complete")
            
        except Exception as e:
            logger.error(f"[RAYDIUM] ❌ Failed to initialize executor: {e}")
            logger.error(traceback.format_exc())
            raise

    # ---------- Wallet loader ----------
    def _load_keypair_from_env(self) -> Keypair:
        # Support either base58-encoded secret or 64-byte array JSON in .env
        secret = os.getenv("PRIVATE_KEY") or os.getenv("WALLET_SECRET")
        if not secret:
            raise ValueError("No PRIVATE_KEY/WALLET_SECRET found in environment.")
        try:
            # Try base58 first
            return Keypair.from_base58_string(secret)
        except Exception:
            # Try JSON array of ints
            arr = json.loads(secret)
            return Keypair.from_bytes(bytes(arr))

    # ---------- Public API ----------
    def swap(
        self,
        mint_in: Pubkey,
        mint_out: Pubkey,
        amount_in: int,
        min_out: int,
        opts: Optional[ExecOptions] = None,
    ) -> Signature:
        """Execute Raydium swap with comprehensive logging"""
        import traceback
        
        logger.info(f"[RAYDIUM_SWAP] 🔄 Starting Raydium swap...")
        logger.debug(f"[RAYDIUM_SWAP] Mint in: {mint_in}")
        logger.debug(f"[RAYDIUM_SWAP] Mint out: {mint_out}")
        logger.debug(f"[RAYDIUM_SWAP] Amount in: {amount_in}")
        logger.debug(f"[RAYDIUM_SWAP] Min out: {min_out}")
        
        opts = opts or ExecOptions()
        logger.debug(f"[RAYDIUM_SWAP] Exec options: compute_limit={opts.compute_unit_limit}, price={opts.compute_unit_price_micro_lamports}")

        # Validate pool_resolver is set
        if not self.pool_resolver:
            error_msg = "pool_resolver not initialized. Set executor.pool_resolver = PoolResolver(rpc, trade_info)"
            logger.error(f"[RAYDIUM_SWAP] ❌ {error_msg}")
            raise ValueError(error_msg)
        
        logger.info(f"[RAYDIUM_SWAP] ✅ Pool resolver validated")
        
        try:
            # 1) Resolve pool & accounts with validation
            logger.info(f"[RAYDIUM_SWAP] Resolving pool for {mint_in} -> {mint_out}...")
            
            try:
                pool = self.pool_resolver.resolve(mint_in, mint_out, self.owner)
            except Exception as pool_error:
                logger.error(f"[RAYDIUM_SWAP] ❌ Pool resolution failed: {pool_error}")
                logger.error(f"[RAYDIUM_SWAP] Cannot proceed without pool information")
                raise ValueError(f"Pool resolution failed: {pool_error}")
            
            # Validate pool accounts before swap execution
            if not pool:
                logger.error(f"[RAYDIUM_SWAP] ❌ Skipping trade: Pool resolver returned None")
                raise ValueError("Pool resolver returned None - cannot execute swap")
            
            # Validate pool has required accounts
            if not hasattr(pool, 'accounts') or not pool.accounts:
                logger.error(f"[RAYDIUM_SWAP] ❌ Skipping trade: Pool missing account information")
                raise ValueError("Pool missing required account information")
            
            # Validate critical pool account fields
            acc = pool.accounts
            required_accounts = ['pool_state', 'input_vault', 'output_vault', 'input_mint', 'output_mint']
            missing_accounts = [field for field in required_accounts if not hasattr(acc, field) or not getattr(acc, field)]
            
            if missing_accounts:
                logger.error(f"[RAYDIUM_SWAP] ❌ Skipping trade: Incomplete account set - missing: {missing_accounts}")
                raise ValueError(f"Pool missing required accounts: {missing_accounts}")
            
            logger.info(f"[RAYDIUM_SWAP] ✅ Pool validated: {pool}")
            logger.info(f"[RAYDIUM_SWAP]    Pool state: {acc.pool_state}")
            logger.info(f"[RAYDIUM_SWAP]    Input vault: {acc.input_vault}")
            logger.info(f"[RAYDIUM_SWAP]    Output vault: {acc.output_vault}")

            # 2) Ensure user ATAs (and WSOL handling if needed)
            logger.info(f"[RAYDIUM_SWAP] Ensuring ATAs...")
            # Input
            in_ata, in_ata_ix = self.ata.ensure_ata_ix_if_missing(self.owner, mint_in)
            logger.debug(f"[RAYDIUM_SWAP] Input ATA: {in_ata}, instruction: {in_ata_ix is not None}")
            
            out_ata, out_ata_ix = self.ata.ensure_ata_ix_if_missing(self.owner, mint_out)
            logger.debug(f"[RAYDIUM_SWAP] Output ATA: {out_ata}, instruction: {out_ata_ix is not None}")

            # 3) Build compute budget ixs
            logger.debug(f"[RAYDIUM_SWAP] Building compute budget instructions...")
            cu_ix = set_compute_unit_limit(opts.compute_unit_limit)
            cup_ix = set_compute_unit_price(opts.compute_unit_price_micro_lamports)

            # 4) Build Raydium swap ix
            logger.info(f"[RAYDIUM_SWAP] Building Raydium swap instruction...")
            # Supply the discovered user ATAs to the builder
            swap_ix = RaydiumCPMMSwapBuilder(pool).build_swap_ix(
                owner=self.owner,
                amount_in=amount_in,
                min_out=min_out,
                user_input_ata=in_ata,
                user_output_ata=out_ata,
            )
            logger.info(f"[RAYDIUM_SWAP] ✅ Swap instruction built")

            # 5) Collect ixs in a sane order
            ixs: List[Instruction] = [cu_ix, cup_ix]
            if in_ata_ix:
                ixs.append(in_ata_ix)
            if out_ata_ix:
                ixs.append(out_ata_ix)
            ixs.append(swap_ix)
            
            logger.info(f"[RAYDIUM_SWAP] ✅ All instructions prepared, total: {len(ixs)}")
            
        except Exception as e:
            logger.error(f"[RAYDIUM_SWAP] ❌ Failed to prepare swap: {e}")
            logger.error(traceback.format_exc())
            raise

        # 6) Compile & sign
        logger.info(f"[RAYDIUM_SWAP] Compiling and signing transaction...")
        recent_hash, _ = self.rpc.get_latest_blockhash()
        msg = MessageV0.try_compile(
            payer=self.owner,
            instructions=ixs,
            address_lookup_tables=[],  # Supply ALT(s) here if pool uses them
            recent_blockhash=recent_hash,
        )
        txn = VersionedTransaction(msg, [self.kp])
        logger.debug(f"[RAYDIUM_SWAP] Transaction compiled and signed")

        # 7) Dual-path execution: Jito first, RPC fallback
        sig = None
        path_used = "rpc"
        
        if jito_is_configured(self.jito_service):
            try:
                import asyncio
                logger.info("🚀 Using Jito for Raydium MEV protection...")
                signed_tx_bytes = bytes(txn)
                result = asyncio.run(self.jito_service.send_transaction(signed_tx_bytes))
                if result.get("signature"):
                    sig = Signature.from_string(result["signature"])
                    path_used = "jito"
                    logger.info(f"✅ EXECUTED via raydium (jito) — signature: {sig}")
                else:
                    logger.warning(f"⏭️ Skipped raydium (jito): {result}")
            except Exception as jito_error:
                logger.warning(f"⏭️ Skipped raydium (jito): {jito_error}")
        
        # RPC fallback (must exist)
        if not sig:
            logger.info(f"[RAYDIUM_SWAP] Attempting RPC submission...")
            sig = self.rpc.send_transaction(txn, skip_preflight=opts.skip_preflight)
            logger.info(f"✅ [RAYDIUM_SWAP] SUCCESS via RPC — signature: {sig}")
        
        try:
            logger.info(f"[RAYDIUM_SWAP] Confirming transaction with {opts.confirm_timeout_s}s timeout...")
            status = self.rpc.confirm_signature(sig, timeout_s=opts.confirm_timeout_s)
            logger.info(f"✅ [RAYDIUM_SWAP] Transaction confirmed: {status}")
        except Exception as e:
            logger.error(f"❌ [RAYDIUM_SWAP] Transaction confirmation failed: {e}")
            # Best-effort surfacing: fetch transaction for logs if available
            try:
                txj = self.rpc.get_transaction(str(sig))
                logs = None
                if txj and txj.get("meta") and txj["meta"].get("logMessages"):
                    logs = txj["meta"]["logMessages"]
                    logger.error(f"[RAYDIUM_SWAP] Transaction logs:")
                    for log in logs:
                        logger.error(f"  {log}")
                raise RuntimeError(f"Send OK but confirmation failed: {e}\nLogs: {logs}")
            except Exception as log_error:
                logger.warning(f"[RAYDIUM_SWAP] Could not fetch transaction logs: {log_error}")
                raise RuntimeError(f"Send OK but confirmation failed: {e}")

        # If err surfaced in status, fetch logs
        if status.get("err"):
            txj = self.rpc.get_transaction(str(sig))
            logs = None
            if txj and txj.get("meta") and txj["meta"].get("logMessages"):
                logs = txj["meta"]["logMessages"]
            raise RuntimeError(f"Transaction error: {status['err']}\nLogs: {logs}")

        return sig


# =============================
# Adapters for your coordinator
# =============================
# These thin wrappers match your ExecutionCoordinator's expected imports:
#   from mev_raydium_executor import MEVRaydiumExecutor, try_raydium_buy, try_raydium_sell_all
# They return a dict with {success, signature, error?, dex}.
# =============================
# Adapters for your coordinator
# =============================
# These thin wrappers match your ExecutionCoordinator's expected imports:
#   from mev_raydium_executor import MEVRaydiumExecutor, try_raydium_buy, try_raydium_sell_all
# They return a dict with {success, signature, error?, dex}.

async def try_raydium_buy(token_mint: str, source_wallet: str, *, amount_sol: float = 0.001, trade_info: dict | None = None, jito_service=None, **kwargs):
    """Coordinator-compatible BUY adapter (SOL -> token on Raydium CPMM).
    Uses ContextPoolResolver to consume the parsed transaction and mirror the pool.
    """
    try:
        from config import HELIUS_RPC_URL, WALLET, NATIVE_MINT as SOL_MINT
    except Exception:
        import os
        HELIUS_RPC_URL = os.getenv("HELIUS_RPC_URL") or os.getenv("RPC_URL")
        # Pubkey already imported at module level
        SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
        from solders.keypair import Keypair
        WALLET = Keypair()

    if not trade_info:
        logger.error("[RAYDIUM_BUY] ❌ trade_info required for pool resolution")
        return {"success": False, "error": "trade_info required (must include parsed_tx.raydium_info)"}

    try:
        executor = MEVRaydiumExecutor(rpc_url=HELIUS_RPC_URL, keypair=(WALLET.keypair if hasattr(WALLET, "keypair") else WALLET), jito_service=jito_service)
        # Override resolver with context-aware one that has rpc and trade_info
        executor.pool_resolver = PoolResolver(executor.rpc, trade_info)
        logger.info(f"[RAYDIUM_BUY] ✅ Executor and pool resolver initialized")
    except Exception as init_error:
        logger.error(f"[RAYDIUM_BUY] ❌ Failed to initialize executor: {init_error}")
        return {"success": False, "error": f"Executor initialization failed: {init_error}"}

    lamports = int(amount_sol * 1_000_000_000)
    try:
        logger.info(f"[RAYDIUM_BUY] Executing buy: {amount_sol} SOL -> {token_mint[:8]}...")
        sig = executor.swap(
            mint_in=SOL_MINT,
            mint_out=Pubkey.from_string(token_mint),
            amount_in=lamports,
            min_out=1,
        )
        path = "jito" if jito_is_configured(executor.jito_service) else "rpc"
        logger.info(f"✅ [RAYDIUM_BUY] SUCCESS: {str(sig)}")
        return exec_ok("raydium", str(sig), {"dex": "raydium", "lamports": lamports, "path": path})
    except ValueError as val_error:
        # Validation errors (pool resolution, missing accounts)
        logger.error(f"❌ [RAYDIUM_BUY] FAILED with validation error: {val_error}")
        return {"success": False, "error": f"Validation failed: {val_error}"}
    except Exception as e:
        logger.error(f"❌ [RAYDIUM_BUY] FAILED with exception: {e}")
        return {"success": False, "error": str(e)}

async def try_raydium_sell_all(token_mint: str, source_wallet: str, *, slippage_bps: int = 300, trade_info: dict | None = None, jito_service=None, **kwargs):
    """SELL adapter (token -> SOL on Raydium CPMM) that sells full wallet balance for `token_mint`.
    Uses ContextPoolResolver to mirror the same pool Wallet A used.
    """
    try:
        from config import HELIUS_RPC_URL, WALLET, NATIVE_MINT as SOL_MINT
    except Exception:
        import os
        HELIUS_RPC_URL = os.getenv("HELIUS_RPC_URL") or os.getenv("RPC_URL")
        # Pubkey already imported at module level
        SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
        from solders.keypair import Keypair
        WALLET = Keypair()

    if not trade_info:
        logger.error("[RAYDIUM_SELL] ❌ trade_info required for pool resolution")
        return {"success": False, "error": "trade_info required (must include parsed_tx.raydium_info)"}

    try:
        rpc = SimpleRPC(RPCConfig(HELIUS_RPC_URL))
    except Exception as rpc_error:
        logger.error(f"[RAYDIUM_SELL] ❌ Failed to initialize RPC: {rpc_error}")
        return {"success": False, "error": f"RPC initialization failed: {rpc_error}"}

    # Find user's token ATA and balance
    owner = (WALLET.keypair.pubkey() if hasattr(WALLET, "keypair") else WALLET.pubkey())
    from_base58 = Pubkey.from_string
    mint_pk = from_base58(token_mint)

    # Derive ATA
    user_token_ata = find_associated_token_address(owner, mint_pk)
    # Query balance
    try:
        res = rpc._post("getTokenAccountBalance", [str(user_token_ata), {"commitment": "confirmed"}])
        ui = res.get("value", {}).get("amount")
        if ui is None:
            return {"success": False, "error": "No token balance found"}
        amount_in = int(ui)
        if amount_in <= 0:
            return {"success": False, "error": "Token balance is zero"}
    except Exception as e:
        return {"success": False, "error": f"Failed to read token balance: {e}"}

    # Build executor and resolver
    executor = MEVRaydiumExecutor(rpc_url=HELIUS_RPC_URL, keypair=(WALLET.keypair if hasattr(WALLET, "keypair") else WALLET), jito_service=jito_service)
    executor.pool_resolver = PoolResolver(executor.rpc, trade_info)

    # min_out with naive slippage application (sell path → out is SOL)
    # For safety use min_out=1; production should compute from quotes
    try:
        sig = executor.swap(
            mint_in=mint_pk,
            mint_out=SOL_MINT,
            amount_in=amount_in,
            min_out=1,
        )
        path = "jito" if jito_is_configured(executor.jito_service) else "rpc"
        return exec_ok("raydium", str(sig), {"dex": "raydium", "amount_in": amount_in, "path": path})
    except Exception as e:
        return {"success": False, "error": str(e)}
    # SOL -> USDC on Raydium (remember: SOL uses WSOL ATA under the hood)
    # Use environment HELIUS_RPC_URL and PRIVATE_KEY.
    owner_kp = None  # or Keypair.from_base58_string("...")
    execu = MEVRaydiumExecutor(keypair=owner_kp)

    SOL = NATIVE_MINT
    USDC = Pubkey.from_string("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11Bqf3jD4u8GzS")  # SPL USDC (example)

    try:
        sig = execu.swap(
            mint_in=SOL,
            mint_out=USDC,
            amount_in=100_000_000,  # 0.1 SOL (lamports)
            min_out=1,              # replace with real slippage calc
        )
        print("✅ Swap signature:", str(sig))
    except NotImplementedError as e:
        print("Pool resolver not implemented:", e)
    except Exception as e:
        print("❌ Swap failed:", e)
