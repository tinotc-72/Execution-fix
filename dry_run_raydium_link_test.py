# dry_run_raydium_link_test.py
# Verifies that detection → coordinator → Raydium adapter is wired correctly.
# It monkey-patches the executor's .swap() so no network/transaction is sent.

from execution_coordinator import ExecutionCoordinator
from mev_raydium_executor import MEVRaydiumExecutor
from config import WALLET, CopyTradeConfig
from solana.rpc.async_api import AsyncClient

# --- Monkey-patch: skip real chain work and just return a signature string
def _patched_swap(self, mint_in, mint_out, amount_in, min_out, opts=None):
    print("✅ MEVRaydiumExecutor.swap() was called with:",
          f"mint_in={mint_in}", f"mint_out={mint_out}",
          f"amount_in={amount_in}", f"min_out={min_out}")
    return "DRY_RUN_SIGNATURE_123"

MEVRaydiumExecutor.swap = _patched_swap  # <- patch class method

# --- Minimal trade_info shaped like what main/coordinator passes for Raydium
trade_info = {
    "dex_type": "raydium",
    "signature": "dummy_sig_for_context",  # not used in dry run
    "parsed_tx": {
        "raydium_info": {
            # Any strings are fine here in dry run; swap is patched before resolve()
            "program_id": "CPMM_PROGRAM_ID_PLACEHOLDER",
            "accounts": {
                "pool_state": "11111111111111111111111111111111",
                "pool_config": "11111111111111111111111111111111",
                "amm_authority": "11111111111111111111111111111111",
                "input_vault": "11111111111111111111111111111111",
                "output_vault": "11111111111111111111111111111111",
                "input_mint": "So11111111111111111111111111111111111111112",
                "output_mint": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11Bqf3jD4u8GzS",  # USDC mint
                "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                "system_program": "11111111111111111111111111111111",
            },
            "swap_ix_data": "AAAAAAAAAAA="  # 8 zero bytes, base64
        }
    }
}

# --- Coordinator instance (use your real logger if you have one)
config = CopyTradeConfig()
rpc_client = AsyncClient(config.rpc_url)
coordinator = ExecutionCoordinator(
    wallet=WALLET,
    rpc_client=rpc_client,
    jito_service=None,
    config=config
)

# Token to BUY (Raydium CPMM path expects SOL -> token). Pick a valid SPL mint.
token_mint = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11Bqf3jD4u8GzS"  # USDC (example)
source_wallet = "CHOSEN_WALLET_A"  # label only; adapter uses your signer from config

import asyncio

async def main():
    res = await coordinator._execute_copy_buy(
        token_mint=token_mint,
        source_wallet=source_wallet,
        amount_sol=0.001,          # any value; we don't hit the chain
        trade_info=trade_info,      # CRITICAL: gets forwarded to adapter
    )
    print("Result:", res)

if __name__ == "__main__":
    asyncio.run(main())
