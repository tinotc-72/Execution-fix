"""
Legacy utils wrapper to maintain compatibility with existing imports
"""

# Import from the parent utils.py file
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import everything from the original utils.py
try:
    from utils import (
        get_transaction_with_logs,
        load_keypair,
        rewrite_pda_if_wallet_a,
        fetch_json_rpc,
        create_ata_if_missing,
        WALLET_A,
        RPC_URL,
        RPCClient,
        get_latest_blockhash,
        get_account_info,
        get_multiple_accounts,
        get_balance,
        send_raw_transaction,
        get_signature_statuses,
        simulate_transaction,
        get_health,
        create_rpc_url,
        fetch_json_rpc_with_url,
        find_associated_token_address,
        create_associated_token_account_ix,
        get_associated_token_address,
        create_associated_token_account
    )
except ImportError as e:
    print(f"Warning: Could not import from utils.py: {e}")
    # Provide dummy functions if needed
    def get_transaction_with_logs(*args, **kwargs):
        return None
    def load_keypair(*args, **kwargs):
        return None
    def rewrite_pda_if_wallet_a(*args, **kwargs):
        return None
    # ... etc