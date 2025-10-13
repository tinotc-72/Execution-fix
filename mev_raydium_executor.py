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
        self.pool_resolver = PoolResolver()
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
        except Exception:
            return None


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
            return None
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
                return None
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
                            return None
        return None

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
            raise ValueError("Incomplete Raydium account set in parsed trade; cannot resolve pool")

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
        rpc_url = rpc_url or os.getenv("HELIUS_RPC_URL") or os.getenv("RPC_URL")
        if not rpc_url:
            raise ValueError("RPC URL not provided. Set HELIUS_RPC_URL or pass rpc_url explicitly.")
        self.rpc = SimpleRPC(RPCConfig(rpc_url))
        self.kp = keypair or self._load_keypair_from_env()
        self.owner = self.kp.pubkey()
        self.ata = ATAManager(self.rpc)
        self.pool_resolver = PoolResolver()
        self.jito_service = jito_service  # Add JitoClient support

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
        opts = opts or ExecOptions()

        # 1) Resolve pool & accounts
        pool = self.pool_resolver.resolve(mint_in, mint_out, self.owner)

        # 2) Ensure user ATAs (and WSOL handling if needed)
        # Input
        in_ata, in_ata_ix = self.ata.ensure_ata_ix_if_missing(self.owner, mint_in)
        out_ata, out_ata_ix = self.ata.ensure_ata_ix_if_missing(self.owner, mint_out)

        # 3) Build compute budget ixs
        cu_ix = set_compute_unit_limit(opts.compute_unit_limit)
        cup_ix = set_compute_unit_price(opts.compute_unit_price_micro_lamports)

        # 4) Build Raydium swap ix
        # Supply the discovered user ATAs to the builder
        swap_ix = RaydiumCPMMSwapBuilder(pool).build_swap_ix(
            owner=self.owner,
            amount_in=amount_in,
            min_out=min_out,
            user_input_ata=in_ata,
            user_output_ata=out_ata,
        )

        # 5) Collect ixs in a sane order
        ixs: List[Instruction] = [cu_ix, cup_ix]
        if in_ata_ix:
            ixs.append(in_ata_ix)
        if out_ata_ix:
            ixs.append(out_ata_ix)
        ixs.append(swap_ix)

        # 6) Compile & sign
        recent_hash, _ = self.rpc.get_latest_blockhash()
        msg = MessageV0.try_compile(
            payer=self.owner,
            instructions=ixs,
            address_lookup_tables=[],  # Supply ALT(s) here if pool uses them
            recent_blockhash=recent_hash,
        )
        txn = VersionedTransaction(msg, [self.kp])

        # 7) Send & confirm - Try Jito first for MEV protection
        sig = None
        if hasattr(self, 'jito_service') and self.jito_service:
            try:
                # Try Jito for MEV protection (synchronous call)
                import asyncio
                signed_tx_bytes = bytes(txn)
                result = asyncio.run(self.jito_service.send_transaction(signed_tx_bytes))
                if result.get("signature"):
                    sig = Signature.from_string(result["signature"])
                else:
                    # Jito failed, fall back to RPC
                    sig = self.rpc.send_transaction(txn, skip_preflight=opts.skip_preflight)
            except Exception:
                # Jito error, fall back to RPC
                sig = self.rpc.send_transaction(txn, skip_preflight=opts.skip_preflight)
        else:
            # No Jito service, use standard RPC
            sig = self.rpc.send_transaction(txn, skip_preflight=opts.skip_preflight)
        
        try:
            status = self.rpc.confirm_signature(sig, timeout_s=opts.confirm_timeout_s)
        except Exception as e:
            # Best-effort surfacing: fetch transaction for logs if available
            txj = self.rpc.get_transaction(str(sig))
            logs = None
            if txj and txj.get("meta") and txj["meta"].get("logMessages"):
                logs = txj["meta"]["logMessages"]
            raise RuntimeError(f"Send OK but confirmation failed: {e}\nLogs: {logs}")

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
        from solders.pubkey import Pubkey
        SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
        from solders.keypair import Keypair
        WALLET = Keypair()

    if not trade_info:
        return {"success": False, "error": "trade_info required (must include parsed_tx.raydium_info)"}

    executor = MEVRaydiumExecutor(rpc_url=HELIUS_RPC_URL, keypair=(WALLET.keypair if hasattr(WALLET, "keypair") else WALLET), jito_service=jito_service)
    # Override resolver with context-aware one
    executor.pool_resolver = ContextPoolResolver(executor.rpc, trade_info)

    lamports = int(amount_sol * 1_000_000_000)
    try:
        sig = executor.swap(
            mint_in=SOL_MINT,
            mint_out=Pubkey.from_string(token_mint),
            amount_in=lamports,
            min_out=1,
        )
        return {"success": True, "signature": str(sig), "dex": "raydium"}
    except Exception as e:
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
        from solders.pubkey import Pubkey
        SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
        from solders.keypair import Keypair
        WALLET = Keypair()

    if not trade_info:
        return {"success": False, "error": "trade_info required (must include parsed_tx.raydium_info)"}

    rpc = SimpleRPC(RPCConfig(HELIUS_RPC_URL))

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
    executor.pool_resolver = ContextPoolResolver(executor.rpc, trade_info)

    # min_out with naive slippage application (sell path → out is SOL)
    # For safety use min_out=1; production should compute from quotes
    try:
        sig = executor.swap(
            mint_in=mint_pk,
            mint_out=SOL_MINT,
            amount_in=amount_in,
            min_out=1,
        )
        return {"success": True, "signature": str(sig), "dex": "raydium"}
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
