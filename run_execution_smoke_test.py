#!/usr/bin/env python3
"""
Smoke test: trigger your ExecutionCoordinator directly to execute a real BUY
without waiting for a live websocket event.

Usage examples:
  python run_execution_smoke_test.py --mint <TOKEN_MINT> --dex raydium --amount 0.001
  python run_execution_smoke_test.py --mint <TOKEN_MINT> --dex meteora --amount 0.001
  python run_execution_smoke_test.py --mint <TOKEN_MINT> --dex unknown --amount 0.001

Notes:
- Uses your existing WALLET from config.py
- Uses your HELIUS_RPC_URL from env_keys.py
- Tries the executor order defined in execution_coordinator.ROUTE_MAP
- Sends a real transaction (real funds) if your wallet has SOL
"""

from types import SimpleNamespace
import argparse
import asyncio
import logging

# Project imports (must exist in your repo runtime)
from env_keys import EnvKeys
from config import WALLET
from execution_coordinator import ExecutionCoordinator
from solana.rpc.async_api import AsyncClient

# Known router/program IDs for better routing hints
RAYDIUM_CPMM = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
RAYDIUM_CPMM_ALT = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
JUPITER_ROUTER = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
PUMPFUN_ROUTER = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
METEORA_DBC = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"

DEX_HINT_TO_ROUTER = {
    "raydium": RAYDIUM_CPMM,
    "raydium_cpmm": RAYDIUM_CPMM,
    "jupiter": JUPITER_ROUTER,
    "pumpfun": PUMPFUN_ROUTER,
    "meteora": METEORA_DBC,
    "unknown": None,
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("smoke_test")

def build_config_ns(investment_amount_sol: float) -> SimpleNamespace:
    """
    Minimal config object with the attributes ExecutionCoordinator expects.
    Adjust values if your coordinator reads more fields.
    """
    return SimpleNamespace(
        investment_amount_sol=investment_amount_sol,
        use_jito=False,
        priority_fee=2_000_000,            # micro-lamports
        compute_limit=400_000,             # units
        max_copy_time_ms=500.0,
        jito_tip_amount=100_000,
        slippage_tolerance=0.05,
        max_retries=3,
        priority_fee_increase_factor=1.5,
        rpc_url=EnvKeys().HELIUS_RPC_URL,
        target_wallets=[],
    )

async def main():
    parser = argparse.ArgumentParser(description="ExecutionCoordinator smoke test")
    parser.add_argument("--mint", required=True, help="Token mint to buy (e.g., So111... for WSOL or a meme coin)")
    parser.add_argument("--dex", default="unknown", choices=["raydium", "meteora", "pumpfun", "jupiter", "unknown"], help="DEX hint for routing")
    parser.add_argument("--amount", type=float, default=0.001, help="Amount of SOL to spend")
    parser.add_argument("--source", default=None, help="(Optional) Source wallet (copied wallet); defaults to your wallet")
    args = parser.parse_args()

    env = EnvKeys()
    rpc = AsyncClient(env.HELIUS_RPC_URL)
    cfg = build_config_ns(args.amount)
    wallet = WALLET
    source_wallet = args.source or str(wallet.pubkey())

    # Build a minimal trade_info that your router understands
    router_program_id = DEX_HINT_TO_ROUTER.get(args.dex)
    trade_info = {
        "signature": "manual-smoke-test",             # marker; not used by builders
        "wallet_address": source_wallet,
        "token_mint": args.mint,
        "dex_type": args.dex,                         # primary hint
        "basic_analysis": {"detected_dex": args.dex}, # secondary hint
    }
    if router_program_id:
        trade_info["router_program_id"] = router_program_id
        trade_info["logs"] = [f"Program {router_program_id} invoke [1]"]

    logger.info("🔧 Initializing ExecutionCoordinator...")
    coord = ExecutionCoordinator(wallet, rpc_client=rpc, jito_service=None, config=cfg)

    logger.info(f"🚀 Triggering BUY via coordinator: mint={args.mint[:8]}… dex_hint={args.dex} amount={args.amount} SOL")
    try:
        res = await coord._execute_copy_buy(
            token_mint=args.mint,
            source_wallet=source_wallet,
            amount_sol=args.amount,
            trade_info=trade_info,
        )
        if res and res.get("success"):
            logger.info(f"✅ SUCCESS — Signature: {res.get('signature')}  (executor: {res.get('method', 'unknown')})")
        else:
            logger.error(f"❌ FAILED — {res}")
    finally:
        await rpc.close()

if __name__ == "__main__":
    asyncio.run(main())
