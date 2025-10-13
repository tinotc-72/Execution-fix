"""
Universal Executor Fallback for unsupported DEX/router trades.
Uses TransactionCloner to fetch, parse, and replay any transaction.
"""
import logging
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from transaction_cloner import TransactionCloner
from env_keys import EnvKeys

def get_rpc_url():
    try:
        return EnvKeys().HELIUS_RPC_URL
    except Exception:
        return "https://api.mainnet-beta.solana.com"

async def try_universal_cloner_buy(wallet_keypair: Keypair, signature: str, **kwargs):
    """
    Universal fallback: Copy any trade by cloning the original transaction.
    Args:
        wallet_keypair: The user's wallet keypair
        signature: The original transaction signature to clone
        **kwargs: Optionally override accounts (e.g., payer)
    Returns:
        Dict with success, signature, error keys
    """
    logger = logging.getLogger(__name__)
    try:
        rpc_url = kwargs.get('rpc_url', get_rpc_url())
        cloner = TransactionCloner(rpc_url, wallet_keypair)
        # Optionally override payer (account 0)
        override_accounts = kwargs.get('override_accounts', {0: wallet_keypair.pubkey()})
        tx = cloner.clone_transaction(signature, override_accounts=override_accounts)
        if not tx:
            return {'success': False, 'signature': None, 'error': 'Failed to clone transaction'}
        tx_sig = cloner.send_cloned_transaction(tx)
        if tx_sig:
            return {'success': True, 'signature': tx_sig, 'dex': 'UniversalCloner'}
        else:
            return {'success': False, 'signature': None, 'error': 'Failed to send cloned transaction'}
    except Exception as e:
        logger.error(f"Universal cloner error: {e}")
        return {'success': False, 'signature': None, 'error': str(e)}
