"""
Utils package - Utility modules for the execution system
"""

from .async_timeout import run_with_watchdog
from .fees import with_compute_budget, get_compute_unit_limit, get_compute_unit_price
from .alts import alts_from_lookups, fetch_address_lookup_table, build_alt_account
from .ata import (
    associated_token_address,
    create_associated_token_account,
    ensure_ata_for,
    SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID,
    SPL_TOKEN_PROGRAM_ID,
    SYSTEM_PROGRAM_ID,
    RENT_SYSVAR_ID,
)
from .ata_enforce import (
    rpc_call,
    ata_exists,
    ensure_ata_ixs,
)

# Import missing functions from main utils.py for backward compatibility
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from utils import get_transaction_with_logs, load_keypair, RPCClient
    # Also import other commonly used functions
    from utils import get_associated_token_address, create_associated_token_account
    # Import additional constants that might be needed
    try:
        from utils import TOKEN_PROGRAM_ID
    except ImportError:
        # Use SPL_TOKEN_PROGRAM_ID as alias for TOKEN_PROGRAM_ID
        TOKEN_PROGRAM_ID = SPL_TOKEN_PROGRAM_ID
except ImportError:
    # If that fails, try importing from the parent directory utils.py
    import importlib.util
    utils_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils.py')
    if os.path.exists(utils_path):
        spec = importlib.util.spec_from_file_location("utils_main", utils_path)
        utils_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils_main)
        get_transaction_with_logs = utils_main.get_transaction_with_logs
        load_keypair = utils_main.load_keypair
        RPCClient = utils_main.RPCClient
        get_associated_token_address = utils_main.get_associated_token_address
        create_associated_token_account = utils_main.create_associated_token_account
        try:
            TOKEN_PROGRAM_ID = utils_main.TOKEN_PROGRAM_ID
        except AttributeError:
            TOKEN_PROGRAM_ID = SPL_TOKEN_PROGRAM_ID
    else:
        # Create placeholder implementations
        async def get_transaction_with_logs(signature: str):
            raise ImportError("get_transaction_with_logs not available")
        def load_keypair():
            raise ImportError("load_keypair not available") 
        class RPCClient:
            def __init__(self, *args, **kwargs):
                raise ImportError("RPCClient not available")
        def get_associated_token_address(*args, **kwargs):
            raise ImportError("get_associated_token_address not available")
        def create_associated_token_account(*args, **kwargs):
            raise ImportError("create_associated_token_account not available")
        TOKEN_PROGRAM_ID = SPL_TOKEN_PROGRAM_ID

__all__ = [
    'run_with_watchdog',
    'with_compute_budget',
    'get_compute_unit_limit',
    'get_compute_unit_price',
    'alts_from_lookups',
    'fetch_address_lookup_table',
    'build_alt_account',
    'associated_token_address',
    'create_associated_token_account',
    'ensure_ata_for',
    'SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID',
    'SPL_TOKEN_PROGRAM_ID',
    'SYSTEM_PROGRAM_ID',
    'RENT_SYSVAR_ID',
    'rpc_call',
    'ata_exists',
    'ensure_ata_ixs',
    'get_transaction_with_logs',
    'load_keypair',
    'RPCClient',
    'get_associated_token_address',
    'create_associated_token_account',
    'TOKEN_PROGRAM_ID',
]
