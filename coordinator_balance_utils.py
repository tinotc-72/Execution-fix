import logging
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient

async def check_wallet_sol_balance(wallet_keypair: Keypair, amount_sol: float, rpc_url: str, logger: logging.Logger = None, fee_buffer: float = 0.01) -> bool:
    """
    Checks if the wallet has enough SOL for the trade (amount_sol + fee_buffer).
    Returns True if sufficient, False otherwise.
    """
    if logger is None:
        logger = logging.getLogger("coordinator_balance_utils")
    client = AsyncClient(rpc_url)
    try:
        wallet_pubkey = wallet_keypair.pubkey() if hasattr(wallet_keypair, 'pubkey') else wallet_keypair
        resp = await client.get_balance(wallet_pubkey)
        sol_balance = resp.value / 1_000_000_000 if hasattr(resp, 'value') else 0
        logger.info(f"[Coordinator] Wallet SOL balance: {sol_balance}")
        if sol_balance < amount_sol + fee_buffer:
            logger.error(f"[Coordinator] Insufficient SOL: {sol_balance} available, {amount_sol} + fees required")
            await client.close()
            return False
        await client.close()
        return True
    except Exception as e:
        logger.error(f"[Coordinator] Error checking SOL balance: {e}")
        await client.close()
        return False