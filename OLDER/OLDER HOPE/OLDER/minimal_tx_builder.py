"""
Minimal transaction builder using only solders for PUMP trades.
Uses the production PUMP router (BSfD6...) and creates Solders-based transactions.
"""
import base58
import os
import base64
import hashlib
import traceback
import json
import logging
from datetime import datetime, timezone, UTC
from typing import List, Union, Tuple, Any, Optional, Dict, TYPE_CHECKING, Protocol

from solders.message import MessageV0, MessageHeader 
from solders.address_lookup_table_account import AddressLookupTableAccount
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.instruction import CompiledInstruction, Instruction, AccountMeta
from solders.keypair import Keypair
from solders.system_program import ID as SYS_PROGRAM_ID, transfer, TransferParams, CreateAccountParams
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.system_program import create_account
from solders.sysvar import RENT as RENT_SYSVAR_KEY
from solders.transaction import VersionedTransaction
from config import SLIPPAGE_BPS
from utils import create_sell_instruction

# Define a Protocol for FastExecutor to use in type hints
class ExecutorProtocol(Protocol):
    async def get_balance(self, pubkey: Pubkey) -> int: ...
    async def get_account_info(self, pubkey: Pubkey) -> Optional[Any]: ...
    async def send_transaction(self, transaction: VersionedTransaction, signers: List[Keypair], **kwargs) -> Optional[str]: ...
    async def get_latest_blockhash(self) -> Hash: ...

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inspect module imports
import sys
logger.info("=== Module Inspection ===")
logger.info(f"Keypair module: {Keypair.__module__}")
logger.info(f"Keypair in sys.modules: {Keypair.__module__ in sys.modules}")
logger.info(f"Module path: {sys.modules[Keypair.__module__].__file__}")
logger.info("=======================")

class RPCHandler:
    def __init__(self):
        self.rpc_endpoints = [
            "https://mainnet.helius-rpc.com/v0/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315",  # Your current Helius endpoint
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com"
        ]
        
    async def get_healthy_rpc(self):
        for endpoint in self.rpc_endpoints:
            try:
                # Test endpoint health
                response = await self.test_rpc_health(endpoint)
                if response:
                    return endpoint
            except:
                continue
        return None

    async def test_rpc_health(self, endpoint: str) -> bool:
        try:
            # Add your RPC health check logic here
            return True
        except:
            return False

# === Constants as Pubkey objects ===
TOKEN_PROGRAM_KEY = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA_PROGRAM_KEY = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_PROGRAM_KEY = Pubkey.from_string("11111111111111111111111111111111")
NATIVE_MINT_KEY = Pubkey.from_string("So11111111111111111111111111111111111111112")
METADATA_PROGRAM_KEY = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")

# Define string constants first
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
ATA_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
SYSTEM_PROGRAM_ID = "11111111111111111111111111111111"
NATIVE_MINT = "So11111111111111111111111111111111111111112"
METADATA_PROGRAM_ID = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
PUMP_ROUTER_STR = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
PUMP_TRADE_PROGRAM_STR = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
PUMP_WSOL_VAULT_STR = "HQ7zcHCsBwquAk7aBuF9CeFqQJX9rrCZaKigufDtRjM6"
PUMP_FEE_ACCOUNT_STR = "AVUCZyuT35YSuj4RH7fwiyPu82Djn2Hfg7y2ND2XcnZH"
PUMP_FEE_AUTHORITY_STR = "6Ghc5hr7MWa3pujTew43ggQnfTdVfTZvZMgQ2XAe8dT1"

# Convert to Pubkey objects
PUMP_ROUTER = Pubkey.from_string(PUMP_ROUTER_STR)
PUMP_TRADE_PROGRAM_KEY = Pubkey.from_string(PUMP_TRADE_PROGRAM_STR)  # Used as _KEY for historical compatibility
PUMP_WSOL_VAULT_KEY = Pubkey.from_string(PUMP_WSOL_VAULT_STR)  # Used as _KEY for historical compatibility
PUMP_FEE_ACCOUNT_KEY = Pubkey.from_string(PUMP_FEE_ACCOUNT_STR)  # Used as _KEY for historical compatibility
PUMP_FEE_AUTHORITY_KEY = Pubkey.from_string(PUMP_FEE_AUTHORITY_STR)  # Used as _KEY for historical compatibility

# Aliases for consistency
PUMP_TRADE_KEY = PUMP_TRADE_PROGRAM_KEY  # For get_user_pda function
PUMP_TRADE_PROGRAM = PUMP_TRADE_PROGRAM_KEY  # Alternative name

# PDA seeds for Pump.fun V2 (verified from mainnet)
CONFIG_SEED = b"config"
ROUTE_SEED = b"route"
STATE_SEED = b"state"
VAULT_SEED = b"vault"
USER_STATE_SEED = b"user-state"

# Target token mint for testing (your meme coin)
TARGET_TOKEN_MINT = "5qCtARHJfxANZyczUokjjSA8rthDoMBVBxoTosPfbonk"

# MEME token mainnet info (optional for testing or replay)
MEME_MINT = "BngZsgk4R9TNuLJsHnyEKCTUcBCc4ThcD1zfwfqvpump"
PUMP_CONFIG = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
PUMP_ROUTE_PARAMS = "HQ7zcHCsBwquAk7aBuF9CeFqQJX9rrCZaKigufDtRjM6"
PUMP_ROUTE_STATE = "Buh7NJ571ZW5xQzNTwiGxsZyitAMzLy959bAq6wyfBBD"

PUMP_CONFIG_KEY = Pubkey.from_string(PUMP_CONFIG)
PUMP_ROUTE_PARAMS_KEY = Pubkey.from_string(PUMP_ROUTE_PARAMS)
PUMP_ROUTE_STATE_KEY = Pubkey.from_string(PUMP_ROUTE_STATE)
MEME_MINT_KEY = Pubkey.from_string(MEME_MINT)

# Instruction discriminator for PUMP router instructions (mainnet verified from successful transaction)
PUMP_BUY_DISCRIMINATOR = bytes.fromhex("66063d1201daebea")  # Buy instruction discriminator
PUMP_SELL_DISCRIMINATOR = bytes.fromhex("33e685a4017f83ad")  # Sell instruction discriminator
# PUMP Router address and Pubkey object
PUMP_ROUTER = Pubkey.from_string("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW")  # Base router Pubkey object

# Additional PUMP constants for sell/buy instructions
PUMP_ROUTER_STATE = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FEE_ACCOUNT = Pubkey.from_string("62qc2CNXwrYqQScmEdiZFFAnJR262PxWEuNQtxfafNgV")
PUMP_VAULT_AUTHORITY = Pubkey.from_string("893s38tuZ4gFF8yYvLRKiyPVsw7ZpwN8H6wBPeHvgHLP")
PUMP_TOKEN_VAULT = Pubkey.from_string("7LUvbhrBNxUehijBYX6nqQUsoctF4uJ2SFzdzrf7KNJR")
PUMP_WSOL_VAULT = Pubkey.from_string("HQ7zcHCsBwquAk7aBuF9CeFqQJX9rrCZaKigufDtRjM6")

# Example raw buy instruction data decoded from base64 (for MEME token)
PUMP_BUY_IX_DATA = base64.b64decode("57rQahYVzDKpAxTmJ5dZtsfoPzp1AVfuxRq6b2wUaxxGACKqxoXxeNI=")

# MEME token buy instruction example accounts (base58 strings)
MEME_PUMP_ROUTER = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
MEME_PUMP_BUY_DATA_B58 = "57rQahYVzDKpAxTmJ5dZtsfoPzp1AVfuxRq6b2wUaxxGACKqxoXxeNK"
MEME_PUMP_BUY_DATA = base58.b58decode(MEME_PUMP_BUY_DATA_B58)

MEME_ACCOUNTS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
    "HQ7zcHCsBwquAk7aBuF9CeFqQJX9rrCZaKigufDtRjM6",
    "Buh7NJ571ZW5xQzNTwiGxsZyitAMzLy959bAq6wyfBBD",
    "893s38tuZ4gFF8yYvLRKiyPVsw7ZpwN8H6wBPeHvgHLP",
    "GM8KAofy5rJ5FJooNQUNPZRUkpeEkpfVXxgQa9AC4H3i",
    "6Ghc5hr7MWa3pujTew43ggQnfTdVfTZvZMgQ2XAe8dT1",
    "6AUXdaeod2NRTPpKFLcxMesTKtxAATaK8QTdUuyE7ixt",
    "11111111111111111111111111111111",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
    "BngZsgk4R9TNuLJsHnyEKCTUcBCc4ThcD1zfwfqvpump",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",
    "ComputeBudget111111111111111111111111111111",
    "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",
    "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"
]

def get_current_time() -> str:
    """Get current time in UTC with proper formatting."""
    try:
        return datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.error(f"Error getting current time: {e}")
        return "Unknown"
    
# Add these helper functions after your constants section:

def get_current_datetime() -> str:
    """Get current datetime in UTC."""
    try:
        from datetime import datetime, UTC
        return datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.error(f"Error getting datetime: {str(e)}")
        return "Unknown"

def get_current_user() -> str:
    """Get current user's login name."""
    try:
        import os
        return os.getlogin()
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return "Unknown"
    
# 1. Basic Utility Functions
def find_program_address(seeds: List[bytes], program_id: Pubkey) -> Tuple[Pubkey, int]:
    """Find a program derived address and its bump seed.
    
    Args:
        seeds: List of seed bytes to derive the PDA
        program_id: The program ID to derive the PDA for
        
    Returns:
        Tuple[Pubkey, int]: The derived address and bump seed
        
    Raises:
        ValueError: If no valid program address is found
    """
    logger.debug(f"Finding program address with {len(seeds)} seeds")
    
    # Start with bump seed 255 and work down
    for bump in range(255, -1, -1):
        try:
            all_seeds = seeds + [bytes([bump])]
            address = Pubkey.create_program_address(all_seeds, program_id)
            logger.debug(f"Found address {address} with bump {bump}")
            return address, bump
        except Exception as e:
            continue
            
    raise ValueError("Unable to find viable program address")

def get_associated_token_address(wallet_address: Pubkey, token_mint_address: Pubkey) -> Pubkey:
    """Find the associated token account address using the official derivation.
    
    Args:
        wallet_address (Pubkey): The wallet that owns the ATA
        token_mint_address (Pubkey): The mint address of the token
        
    Returns:
        Pubkey: The derived Associated Token Account address
        
    Example:
        >>> wallet = Pubkey.from_string("A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
        >>> mint = Pubkey.from_string("So11111111111111111111111111111111111111112")
        >>> ata = get_associated_token_address(wallet, mint)
    """
    logger.debug(f"Deriving ATA for wallet {wallet_address} and mint {token_mint_address}")
    
    # Convert string inputs to Pubkey if needed
    if isinstance(token_mint_address, str):
        token_mint_address = Pubkey.from_string(token_mint_address)
    if isinstance(wallet_address, str):
        wallet_address = Pubkey.from_string(wallet_address)

    # Construct seeds for the PDA derivation
    seeds = [
        bytes(wallet_address),  # Allow auto-conversion from Pubkey to bytes
        bytes(TOKEN_PROGRAM_KEY),
        bytes(token_mint_address)
    ]

    # Official SPL Token ATA derivation
    program_address = Pubkey.find_program_address(
        seeds,
        ATA_PROGRAM_KEY
    )
    logger.debug(f"Derived ATA: {program_address[0]}")
    return program_address[0]  # Return only the derived address without bump

def get_minimum_balance_for_rent_exemption(space: int) -> int:
    """Calculate minimum balance required for rent exemption.
    
    Args:
        space: The space in bytes needed
        
    Returns:
        int: The minimum balance in lamports
    """
    LAMPORTS_PER_BYTE_YEAR = 3480
    EXEMPTION_THRESHOLD = 2
    RENT_EXEMPT_MINIMUM = 890880
    
    rent = max(
        RENT_EXEMPT_MINIMUM,
        (LAMPORTS_PER_BYTE_YEAR * space * EXEMPTION_THRESHOLD) // 1
    )
    logger.debug(f"Calculated rent for {space} bytes: {rent} lamports")
    return rent

def validate_blockhash(blockhash: Hash) -> bool:
    """Validate that a blockhash is properly formed.
    
    Args:
        blockhash: The blockhash to validate
        
    Returns:
        bool: True if valid, False if not
    """
    try:
        # Check that it's not the default zero hash
        if blockhash == Hash.default():
            logger.error("Invalid blockhash: Cannot use default hash")
            return False
            
        # Check that it has the proper length
        hash_bytes = bytes(blockhash)
        if len(hash_bytes) != 32:
            logger.error(f"Invalid blockhash length: {len(hash_bytes)} != 32")
            return False
            
        # Check that it's not all zeros
        if all(b == 0 for b in hash_bytes):
            logger.error("Invalid blockhash: All zero bytes")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating blockhash: {str(e)}")
        return False


# 2. PDA Derivation Functions
async def derive_token_ata(token_mint: Pubkey, owner: Pubkey) -> Pubkey:
    """Derive the Associated Token Account address."""
    logger.debug(f"Deriving token ATA for mint {token_mint} and owner {owner}")
    ata = get_associated_token_address(owner, token_mint)
    logger.debug(f"Derived token ATA: {ata}")
    return ata

def derive_config_pda() -> Pubkey:
    """Derive the config PDA for the PUMP protocol.
    
    Returns:
        Pubkey: The derived config address
    """
    logger.debug("Deriving config PDA")
    seeds = [CONFIG_SEED]
    address, bump = find_program_address(seeds, PUMP_TRADE_PROGRAM_KEY)
    logger.debug(f"Found address {address} with bump {bump}")
    return address

def derive_route_params_pda(token_mint: Pubkey) -> Pubkey:
    """Derive the route params PDA for a given token.
    
    Args:
        token_mint: The token mint address
        
    Returns:
        Pubkey: The derived route params address
    """
    logger.debug(f"Deriving route params PDA for token {token_mint}")
    seeds = [ROUTE_SEED, bytes(token_mint)]
    address, bump = find_program_address(seeds, PUMP_TRADE_PROGRAM_KEY)
    logger.debug(f"Found address {address} with bump {bump}")
    return address

def derive_route_state_pda(token_mint: Pubkey) -> Pubkey:
    """Derive the route state PDA for a given token.
    
    Args:
        token_mint: The token mint address
        
    Returns:
        Pubkey: The derived route state address
    """
    logger.debug(f"Deriving route state PDA for token {token_mint}")
    seeds = [STATE_SEED, bytes(token_mint)]
    address, bump = find_program_address(seeds, PUMP_TRADE_PROGRAM_KEY)
    logger.debug(f"Found address {address} with bump {bump}")
    return address

def derive_token_vault_pda(token_mint: Pubkey) -> Pubkey:
    """Derive the token vault PDA for a given token.
    
    Args:
        token_mint: The token mint address
        
    Returns:
        Pubkey: The derived token vault address
    """
    logger.debug(f"Deriving token vault PDA for token {token_mint}")
    seeds = [VAULT_SEED, bytes(token_mint)]
    address, bump = find_program_address(seeds, PUMP_TRADE_PROGRAM_KEY)
    logger.debug(f"Found address {address} with bump {bump}")
    return address

def get_metadata_address(mint: Pubkey) -> Pubkey:
    """Find the metadata account PDA for a token mint."""
    seeds = [
        b"metadata",
        bytes(METADATA_PROGRAM_KEY),
        bytes(mint)
    ]
    metadata_key, _bump = Pubkey.find_program_address(
        seeds,
        METADATA_PROGRAM_KEY
    )
    return metadata_key

def get_user_pda_with_bump(wallet: Pubkey) -> Tuple[Pubkey, int]:
    """Get the user's PDA address and bump seed.
    
    Args:
        wallet (Pubkey): The wallet to get the PDA for
    
    Returns:
        Tuple[Pubkey, int]: (pda_address, bump_seed)
    """
    # We now use only the wallet pubkey and USER_STATE_SEED for derivation
    seeds = [
        USER_STATE_SEED,  # "user-state"
        bytes(wallet)
    ]
    
    # Use find_program_address to get both PDA and bump, using PUMP_ROUTER
    address, bump = Pubkey.find_program_address(
        seeds=seeds,
        program_id=PUMP_ROUTER  # Changed from PUMP_TRADE_PROGRAM_KEY to PUMP_ROUTER
    )
    
    logger.info(f"Derived user PDA {address} with bump {bump}")
    logger.info(f"PDA derivation details:")
    logger.info(f"  Seeds:")
    logger.info(f"    - USER_STATE_SEED: {USER_STATE_SEED.hex()}")
    logger.info(f"    - Wallet bytes: {bytes(wallet).hex()}")
    logger.info(f"  Program ID: {PUMP_ROUTER}")
    logger.info(f"  Bump: {bump}")
    
    return address, bump

def get_user_pda(wallet: Pubkey) -> Pubkey:
    """Get just the user's PDA address (wrapper for backward compatibility).
    
    Args:
        wallet (Pubkey): The wallet to get the PDA for
    
    Returns:
        Pubkey: The PDA address
    """
    address, _ = get_user_pda_with_bump(wallet)
    return address


# 7. Account Creation Functions
def create_account_instruction(
    payer: Pubkey,
    space: int,
    program_id: Pubkey,
    new_account: Optional[Keypair] = None,
) -> Tuple[Instruction, Keypair]:
    """Create an instruction to create a new account"""
    # Generate new keypair for the account if not provided
    account_keypair = new_account if new_account else Keypair()
    logger.debug(f"Creating account instruction for {account_keypair.pubkey()}")
    
    lamports = get_minimum_balance_for_rent_exemption(space)
    
    ix = Instruction(
        program_id=SYS_PROGRAM_ID,
        accounts=[
            AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
            AccountMeta(pubkey=account_keypair.pubkey(), is_signer=True, is_writable=True),
        ],                data=bytes([0]) +  # Create account instruction discriminator
                     lamports.to_bytes(8, 'little') +  # Lamports
                     space.to_bytes(8, 'little') +  # Space
                     bytes(program_id.to_bytes())  # Program ID
    )
    
    return ix, account_keypair
# Add alias for compatibility (after the function definition)
create_account_ix = create_account_instruction

def create_associated_token_account(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey
) -> Instruction:
    """Create an instruction to create an Associated Token Account"""
    ata = get_associated_token_address(owner, mint)
    
    accounts = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ATA_PROGRAM_KEY, is_signer=False, is_writable=False),
    ]
    
    return Instruction(
        program_id=ATA_PROGRAM_KEY,
        accounts=accounts,
        data=bytes([])  # Empty data for create instruction
    )

def create_associated_token_account_idempotent(payer: Pubkey, wallet: Pubkey, mint: Pubkey) -> List[Instruction]:
    """Create instructions to create and initialize the ATA if it doesn't exist"""
    ata = get_associated_token_address(wallet, mint)
    
    # First create the ATA with CreateIdempotent
    create_ata_ix = Instruction(
        program_id=ATA_PROGRAM_KEY,  # ATA program
        accounts=[
            AccountMeta(pubkey=payer, is_signer=True, is_writable=True),  # Payer
            AccountMeta(pubkey=ata, is_signer=False, is_writable=True),   # ATA to create
            AccountMeta(pubkey=wallet, is_signer=False, is_writable=False), # Wallet to own ATA
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),  # Token mint
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),  # System program
            AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),  # Token program
            AccountMeta(pubkey=ATA_PROGRAM_KEY, is_signer=False, is_writable=False),  # ATA program
        ],
        data=bytes([1])  # CreateIdempotent instruction
    )
    
    # For WSOL, we also need to initialize the account
    if mint == NATIVE_MINT_KEY:
        init_ata_ix = Instruction(
            program_id=TOKEN_PROGRAM_KEY,  # Token program
            accounts=[
                AccountMeta(pubkey=ata, is_signer=False, is_writable=True),  # ATA to initialize
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),  # WSOL mint
                AccountMeta(pubkey=wallet, is_signer=False, is_writable=False),  # Owner
                AccountMeta(pubkey=payer, is_signer=True, is_writable=True),  # Rent payer
            ],
            data=bytes([1]) + bytes(wallet)  # InitializeAccount3 instruction + owner pubkey
        )
        return [create_ata_ix, init_ata_ix]
    
    return [create_ata_ix]

async def ensure_accounts_exist(
    executor: ExecutorProtocol,
    accounts_to_check: List[Tuple[Pubkey, bool]],
    payer: Pubkey,
    instructions: List[Instruction]
) -> bool:
    """Check if accounts exist and create them if necessary"""
    try:
        for pubkey, is_writable in accounts_to_check:
            account_info = await executor.get_account_info(pubkey)
            if not account_info and is_writable:
                logger.info(f"Creating account {pubkey}")
                
                # Calculate space based on account type
                space = 165  # Default space for token accounts
                if "route_params" in str(pubkey):
                    space = 200  # Adjust for route params
                elif "route_state" in str(pubkey):
                    space = 300  # Adjust for route state
                elif "token_vault" in str(pubkey):
                    space = 165  # Standard token account size
                
                create_ix = create_account_instruction(
                    payer=payer,
                    space=space,
                    program_id=PUMP_ROUTER,
                    new_account_pubkey=pubkey
                )
                instructions.insert(0, create_ix)
                logger.info(f"Added creation instruction for account {pubkey}")
        return True
    except Exception as e:
        logger.error(f"Failed to check/create accounts: {e}")
        traceback.print_exc()
        return False
 
async def check_ata_exists(executor, ata: Pubkey) -> bool:
    """Check if an ATA exists by querying its info"""
    if hasattr(executor, 'get_account_info'):
        info = await executor.get_account_info(ata)
        return info is not None
    return False  # If no way to check, assume it doesn't exist

# 3. Instruction Creation Functions
def create_compute_budget_ix(compute_units: int = 200_000, compute_unit_price: Optional[int] = None) -> Instruction:
    """Create a compute budget instruction.
    
    Args:
        compute_units: Number of compute units to request
        compute_unit_price: Optional price per compute unit in micro-lamports
        
    Returns:
        Instruction: The compute budget instruction
    """
    logger.debug(f"Creating compute budget instruction with {compute_units} units and price {compute_unit_price}")
    
    # Create compute unit limit instruction
    compute_budget_ix = set_compute_unit_limit(compute_units)
    
    # Add compute unit price if specified
    if compute_unit_price is not None:
        compute_budget_ix = set_compute_unit_price(compute_unit_price)
        
    return compute_budget_ix

def create_compute_budget_instructions(
    unit_limit: int = 1_400_000,
    unit_price: int = 100
) -> List[Instruction]:
    """Create compute budget instructions."""
    return [
        set_compute_unit_limit(unit_limit),
        set_compute_unit_price(unit_price)
    ]

def create_account_ix(
    payer: Pubkey,
    space: int,
    program_id: Pubkey,
    new_account_pubkey: Pubkey
) -> Optional[Instruction]:
    """Create an instruction to create a new account.
    
    Args:
        payer: The account that will pay for creation
        space: The space needed in bytes
        program_id: The program that will own the account
        new_account_pubkey: The address of the new account
        
    Returns:
        Optional[Instruction]: The creation instruction if needed
    """
    logger.debug(f"Creating account instruction for {new_account_pubkey}")
    
    # Calculate minimum rent
    lamports = get_minimum_balance_for_rent_exemption(space)
    logger.debug(f"Calculated rent for {space} bytes: {lamports} lamports")
    
    # Use solders' create_account helper
    from solders.system_program import create_account, CreateAccountParams
    
    # Create the instruction using the proper helper
    create_account_ix = create_account(
        CreateAccountParams(
            from_pubkey=payer,           # Funding account (signer)
            to_pubkey=new_account_pubkey, # New account
            lamports=lamports,            # Rent-exempt amount
            space=space,                  # Account data size
            owner=program_id             # Program that will own the account
        )
    )
    
    return create_account_ix

async def create_buy_instruction(
    token_mint: Pubkey,      # Changed from token to token_mint for clarity
    owner: Pubkey,
    amount: int,
    slippage_bps: int,
    token_ata: Pubkey,
    wsol_vault: Pubkey = PUMP_WSOL_VAULT_KEY,     # Added default
    fee_account: Pubkey = PUMP_FEE_ACCOUNT_KEY,   # Added default
) -> Instruction:
    """
    Create a buy instruction for PUMP trading.
    
    Args:
        token_mint (Pubkey): The mint address of the token to buy
        owner (Pubkey): The owner's public key
        amount (int): Amount of SOL to spend in lamports
        slippage_bps (int): Slippage tolerance in basis points (1 bp = 0.01%)
        token_ata (Pubkey): The user's Associated Token Account for the token
        wsol_vault (Pubkey, optional): WSOL vault address. Defaults to PUMP_WSOL_VAULT_KEY
        fee_account (Pubkey, optional): Fee account address. Defaults to PUMP_FEE_ACCOUNT_KEY
    
    Returns:
        Instruction: The compiled buy instruction
    """
    logger.info("\n🔍 DEBUG: Starting create_buy_instruction")
    logger.info(f"Input Parameters:")
    logger.info(f"Token Mint: {token_mint}")
    logger.info(f"Owner: {owner}")
    logger.info(f"Amount: {amount} lamports")
    logger.info(f"Slippage BPS: {slippage_bps}")
    logger.info(f"Token ATA: {token_ata}")

    # Validate input parameters
    if amount <= 0:
        logger.error("❌ Amount must be positive")
        raise ValueError("Amount must be positive")

    # Get PDAs
    config_pda = derive_config_pda()
    route_params_pda = derive_route_params_pda(token_mint)
    route_state_pda = derive_route_state_pda(token_mint)
    token_vault_pda = derive_token_vault_pda(token_mint)
    metadata_key = get_metadata_address(token_mint)

    logger.info("\n🧮 Calculating min_amount_out:")
    min_amount_out = max(1, int(amount * (1 - slippage_bps / 10000)))
    logger.info(f"Min amount out: {min_amount_out} lamports")

    # Debug instruction data construction
    logger.info("\n🔧 Building instruction data:")
    try:
        instruction_data = (
            PUMP_BUY_DISCRIMINATOR +
            amount.to_bytes(8, "little") +
            min_amount_out.to_bytes(8, "little")
        )
        logger.info(f"Discriminator (hex): {PUMP_BUY_DISCRIMINATOR.hex()}")
        logger.info(f"Amount bytes (hex): {amount.to_bytes(8, 'little').hex()}")
        logger.info(f"Min amount bytes (hex): {min_amount_out.to_bytes(8, 'little').hex()}")
    except Exception as e:
        logger.error(f"❌ Failed to construct instruction data: {e}")
        raise

    # Debug account construction - Updated to match successful transaction structure
    logger.info("\n📝 Constructing accounts list")
    try:
        # Based on successful transaction analysis - match exact order from mainnet
        accounts = [
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=False),  # 0: Config/authority (first in successful tx)
            AccountMeta(pubkey=fee_account, is_signer=False, is_writable=True),  # 1: Fee account  
            AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # 2: Token mint
            AccountMeta(pubkey=token_vault_pda, is_signer=False, is_writable=True),  # 3: Token vault
            AccountMeta(pubkey=route_state_pda, is_signer=False, is_writable=True),  # 4: Route state
            AccountMeta(pubkey=token_ata, is_signer=False, is_writable=True),  # 5: User token account
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # 6: User wallet (signer) - position matches successful tx
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),  # 7: System program
            AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),  # 8: Token program
            AccountMeta(pubkey=wsol_vault, is_signer=False, is_writable=True),  # 9: WSOL vault or other account
            AccountMeta(pubkey=METADATA_PROGRAM_KEY, is_signer=False, is_writable=False),  # 10: Event authority/metadata
            AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # 11: Trade program (last)
        ]
    except Exception as e:
        logger.error(f"❌ Failed to construct accounts list: {e}")
        raise

    # Validate critical accounts
    logger.info("\n🔍 Validating critical accounts:")
    logger.info(f"WSOL Vault: {wsol_vault}")
    logger.info(f"Fee Account: {fee_account}")
    logger.info(f"Trade Program: {PUMP_TRADE_PROGRAM_KEY}")

    logger.info("\n📊 Accounts included in instruction:")
    for i, acc in enumerate(accounts):
        writable_status = '[writable]' if acc.is_writable else ''
        signer_status = '[signer]' if acc.is_signer else ''
        logger.info(f"  {i}: {acc.pubkey} {signer_status} {writable_status}")

    logger.info("\n🏗️ Creating final instruction")
    return Instruction(
        program_id=PUMP_TRADE_PROGRAM_KEY,  # Use trade program, not router
        accounts=accounts,
        data=instruction_data
    )

def create_account_instruction(
    payer: Pubkey,
    space: int,
    program_id: Pubkey,
    new_account_pubkey: Pubkey,
) -> Instruction:
    """Create an instruction to create a new account

    Args:
        payer (Pubkey): The account that will pay for creation
        space (int): Space in bytes to allocate
        program_id (Pubkey): Program that will own the account
        new_account_pubkey (Pubkey): Public key of account to create
    """

def create_user_init_instruction(owner: Pubkey) -> Instruction:
    """
    Create an instruction to initialize a user's PDA in the PUMP protocol.
    Verified against mainnet transactions.
    
    Args:
        owner: The owner's public key (must be signer)
    """
    logger.info("\n🔧 Creating user init instruction")
    logger.info(f"Owner: {owner}")
    
    # Get PDA and bump using PUMP_ROUTER
    user_pda, bump = get_user_pda_with_bump(owner)
    logger.info(f"User PDA: {user_pda}")
    logger.info(f"Bump seed: {bump}")
    
    # Verified mainnet discriminator for initialize_user
    discriminator = bytes.fromhex("b5f9b1e8179d8e84")
    instruction_data = (
        discriminator +  # 8 bytes: Anchor discriminator
        bytes([bump])    # 1 byte: Bump seed
    )
    
    logger.info(f"Instruction data (hex): {instruction_data.hex()}")
    
    # Get config PDA
    config_pda = derive_config_pda()
    
    # Create account list in mainnet-verified order
    accounts = [
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),
        AccountMeta(pubkey=user_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=config_pda, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    
    logger.info("Accounts in order:")
    for i, acc in enumerate(accounts):
        flags = []
        if acc.is_signer: flags.append("signer")
        if acc.is_writable: flags.append("writable")
        logger.info(f"  {i}. {acc.pubkey} [{', '.join(flags)}]")
    
    initialize_ix = Instruction(
        program_id=PUMP_ROUTER,
        accounts=accounts,
        data=instruction_data
    )
    
    logger.info("\n✅ User init instruction created")
    logger.info(f"Program ID: {PUMP_ROUTER}")
    return initialize_ix

def build_meme_buy_instruction(payer: Pubkey):
    """Build the meme coin buy instruction using mainnet-exact data, with payer as signer."""
    accounts = []
    for i, a in enumerate(MEME_ACCOUNTS):
        is_signer = (Pubkey.from_string(a) == payer)
        accounts.append(AccountMeta(pubkey=Pubkey.from_string(a), is_signer=is_signer, is_writable=True))
    return Instruction(
        program_id=Pubkey.from_string(MEME_PUMP_ROUTER),
        accounts=accounts,
        data=MEME_PUMP_BUY_DATA
    )

# === Transaction Builder Functions ===

def swap_instruction_payload(
    amount_in: int,
    min_amount_out: int,
    slippage_bps: int
) -> bytes:
    """Create the swap instruction payload with proper mainnet format.
    
    Args:
        amount_in: Amount of SOL in lamports
        min_amount_out: Minimum amount of tokens to receive
        slippage_bps: Slippage tolerance in basis points
        
    Returns:
        bytes: The instruction payload
    """
    try:
        # Verified mainnet discriminator for initialize_and_buy
        discriminator = bytes.fromhex("adf0bdc6df9c34d1")
        if len(discriminator) != 8:
            logger.error(f"❌ Invalid discriminator length: {len(discriminator)}")
            return b''
            
        # Validate input values
        if amount_in <= 0 or min_amount_out <= 0 or slippage_bps <= 0:
            logger.error(f"❌ Invalid input values: {amount_in}, {min_amount_out}, {slippage_bps}")
            return b''
            
        # Pack instruction data exactly as mainnet expects
        instruction_data = (
            discriminator +                              # 8 bytes: Anchor discriminator
            amount_in.to_bytes(8, "little") +           # 8 bytes: Amount in (u64)
            min_amount_out.to_bytes(8, "little") +      # 8 bytes: Min amount out (u64)
            slippage_bps.to_bytes(2, "little")          # 2 bytes: Slippage bps (u16)
        )
        
        # Validate final data length
        expected_len = 8 + 8 + 8 + 2  # discriminator + amount_in + min_out + slippage
        if len(instruction_data) != expected_len:
            logger.error(f"❌ Invalid instruction data length: {len(instruction_data)} (expected {expected_len})")
            return b''
            
        logger.info(f"✅ Swap instruction data created successfully:")
        logger.info(f"  Length: {len(instruction_data)} bytes")
        logger.info(f"  Discriminator: {discriminator.hex()}")
        logger.info(f"  Amount in: {amount_in} lamports")
        logger.info(f"  Min amount out: {min_amount_out} units")
        logger.info(f"  Slippage: {slippage_bps} bps")
        
        return instruction_data
        
    except Exception as e:
        logger.error(f"❌ Error creating swap instruction data: {str(e)}")
        return b''

async def build_buy_tx(
    token_mint: Pubkey,
    amount_in: int,
    max_sol_cost: int,
    owner: Pubkey,
    signer: Keypair,
    executor: ExecutorProtocol,
    slippage_bps: Optional[int] = 300  # Default to 3% slippage
) -> Tuple[Optional[VersionedTransaction], Optional[List[Instruction]]]:
    """
    Build a transaction to buy tokens using the PUMP router.
    Verified against mainnet transactions.
    """
    try:
        # Input validation
        logger.info("\n🔍 Starting build_buy_tx")
        
        if not isinstance(signer, Keypair):
            logger.error(f"❌ Invalid signer type: {type(signer)}")
            return None, None
            
        if str(owner) != str(signer.pubkey()):
            logger.error("❌ Owner does not match signer's pubkey")
            return None, None
            
        logger.info("\n📊 Transaction Parameters:")
        logger.info(f"Token mint: {token_mint}")
        logger.info(f"Amount in: {amount_in:,} lamports ({amount_in/1e9:.6f} SOL)")
        logger.info(f"Max cost: {max_sol_cost:,} lamports ({max_sol_cost/1e9:.6f} SOL)")
        logger.info(f"Owner: {owner}")
        logger.info(f"Slippage: {slippage_bps/100:.1f}%")
        
        # Verify wallet balance
        balance = await executor.get_balance(owner)
        logger.info(f"\n💰 Current balance: {balance/1e9:.6f} SOL")
        if balance < max_sol_cost:
            logger.error("❌ Insufficient balance")
            return None, None
            
        # Get ATAs and PDAs
        token_ata = get_associated_token_address(owner, token_mint)
        wsol_ata = get_associated_token_address(owner, NATIVE_MINT_KEY)
        user_pda, bump = get_user_pda_with_bump(owner)
        
        # Get mainnet-verified route/program PDAs
        config_pda = derive_config_pda()
        route_params_pda = derive_route_params_pda(token_mint)
        route_state_pda = derive_route_state_pda(token_mint)
        token_vault_pda = derive_token_vault_pda(token_mint)
        
        # Check if user PDA needs initialization
        needs_init = await verify_user_pda_needs_init(executor, user_pda, owner)
        
        # Build instructions in mainnet-verified order:
        instructions = []
        
        # 1. Always add compute budget first (mainnet uses 1.4M CU)
        compute_ix = create_compute_budget_ix(1_400_000)
        instructions.append(compute_ix)
        
        # 2. Add PDA initialization if needed
        if needs_init:
            logger.info("\n🔧 Adding PDA initialization")
            init_ix = create_user_init_instruction(owner)
            instructions.append(init_ix)
            
        # 3. Add ATA creation (idempotent)
        logger.info("\n🏗️ Adding ATA creation")
        ata_ixs = create_associated_token_account_idempotent(owner, owner, token_mint)
        instructions.extend(ata_ixs)
        
        # 4. Add WSOL handling (transfer + sync)
        transfer_ix = transfer(TransferParams(
            from_pubkey=owner,
            to_pubkey=wsol_ata,
            lamports=amount_in
        ))
        sync_ix = Instruction(
            program_id=TOKEN_PROGRAM_KEY,
            accounts=[AccountMeta(pubkey=wsol_ata, is_writable=True, is_signer=False)],
            data=bytes([17])  # SyncNative instruction
        )
        instructions.extend([transfer_ix, sync_ix])
        
        # 5. Build the swap instruction with mainnet-verified account order
        logger.info("\n🔄 Creating swap instruction")
        
        # Calculate min amount out based on slippage
        min_amount_out = max(1, int(amount_in * (1 - slippage_bps/10000)))
        logger.info(f"Min amount out: {min_amount_out:,} lamports")
        
        instruction_data = swap_instruction_payload(
            amount_in=amount_in,
            min_amount_out=min_amount_out,
            slippage_bps=slippage_bps
        )
        
        # Validate instruction data
        if not instruction_data or len(instruction_data) == 0:
            logger.error("❌ Swap instruction data is empty")
            return None, None
            
        logger.info(f"Swap instruction data length: {len(instruction_data)} bytes")
        logger.info(f"Swap instruction data (hex): {instruction_data.hex()}")
        
        # Validate PDAs
        logger.info("\n🔍 Validating PDAs:")
        logger.info(f"Route state PDA: {route_state_pda}")
        logger.info(f"Token vault PDA: {token_vault_pda}")
        logger.info(f"User PDA: {user_pda}")
        
        # Create swap instruction with mainnet-verified account order
        accounts = [
            # Config and parameters (first 3 must be in this order)
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=False),
            AccountMeta(pubkey=route_params_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=route_state_pda, is_signer=False, is_writable=True),
            
            # Token accounts
            AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_WSOL_VAULT_KEY, is_signer=False, is_writable=True),
            AccountMeta(pubkey=token_vault_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=token_ata, is_signer=False, is_writable=True),
            
            # User accounts
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),
            AccountMeta(pubkey=user_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=wsol_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=PUMP_FEE_AUTHORITY_KEY, is_signer=False, is_writable=False),
            
            # Required programs
            AccountMeta(pubkey=TOKEN_PROGRAM_KEY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=ATA_PROGRAM_KEY, is_signer=False, is_writable=False)
        ]
        
        swap_ix = Instruction(
            program_id=PUMP_ROUTER,
            accounts=accounts,
            data=instruction_data
        )
        instructions.append(swap_ix)
        
        # Log all instructions
        logger.info("\n📋 Final instruction list:")
        for idx, ix in enumerate(instructions):
            logger.info(f"\nInstruction {idx}:")
            logger.info(f"  Program: {ix.program_id}")
            logger.info(f"  Data (hex): {ix.data.hex()}")
            logger.info(f"  Accounts ({len(ix.accounts)}):")
            for i, acc in enumerate(ix.accounts):
                logger.info(f"    {i}: {acc.pubkey} (signer={acc.is_signer}, writable={acc.is_writable})")
        
        # Build the final transaction
        tx = await build_tx_with_blockhash(
            instructions=instructions,
            signers=[signer],
            payer=owner,
            executor=executor
        )
        
        if not tx:
            raise ValueError("Failed to build transaction")
            
        return tx, instructions
            
    except Exception as e:
        logger.error(f"❌ Error in build_buy_tx: {str(e)}")
        logger.error(traceback.format_exc())
        return None, None

async def build_sell_tx(
    token_mint: Pubkey,
    amount_in: int,
    min_out: int,
    owner: Pubkey,
    signer: Keypair,
    executor: ExecutorProtocol,
    slippage_bps: int = 300
) -> Tuple[Optional[VersionedTransaction], Optional[List[Instruction]]]:
    """
    Build a sell transaction for a token using PUMP protocol.
    
    Args:
        token_mint (Pubkey): The token mint address
        amount_in (int): Amount of SOL in lamports to spend
        min_out (int): Minimum amount of tokens to receive (after slippage)
        owner (Pubkey): The owner's public key (must be signer.pubkey())
        signer (Keypair): The full Keypair instance that will sign
        executor (ExecutorProtocol): The executor instance for RPC calls
        slippage_bps (int): Slippage tolerance in basis points (default 300 = 3%)
        
    Returns:
        Tuple[Optional[VersionedTransaction], Optional[List[Instruction]]]: 
        Returns (transaction, instructions) or (None, None) on failure
    """
    # Validate signer first
    if not validate_keypair_for_tx(signer, "build_sell_tx"):
        logger.error("❌ Invalid signer passed to build_sell_tx")
        return None, None
        
    # Verify owner matches signer's pubkey
    if str(owner) != str(signer.pubkey()):
        logger.error(f"❌ Owner ({owner}) does not match signer's pubkey ({signer.pubkey()})")
        return None, None

    try:
        # Initial logging
        logger.info("\n🔍 DEBUG: Starting build_sell_tx")
        logger.info("=================================")
        
        # Transaction context logging
        logger.info("\n📊 Transaction Context:")
        logger.info(f"  Token mint: {token_mint}")
        logger.info(f"  Amount in: {amount_in:,} lamports ({amount_in/1e9:.6f} SOL)")
        logger.info(f"  Min output: {min_out:,} lamports ({min_out/1e9:.6f} SOL)")
        logger.info(f"  Owner: {owner}")
        logger.info(f"  Slippage: {slippage_bps/100:.1f}%")

        # Check owner's SOL balance
        logger.info("\n💰 Checking owner balance")
        balance = await executor.get_balance(owner)
        logger.info(f"  Current balance: {balance:,} lamports ({balance/1e9:.6f} SOL)")
        
        if balance < amount_in:
            raise ValueError(
                f"Insufficient balance: {balance:,} < {amount_in:,} lamports "
                f"({balance/1e9:.6f} < {amount_in/1e9:.6f} SOL)"
            )
        logger.info("Balance check passed")

        # Get token ATA
        logger.info("\n🔑 Deriving token ATA")
        try:
            token_ata = get_associated_token_address(owner, token_mint)
            logger.info(f"  Token ATA: {token_ata}")
        except Exception as e:
            logger.error(f"Failed to derive token ATA: {e}")
            return None, None

        # Create compute budget instructions
        logger.info("\n💻 Creating compute budget instructions")
        try:
            compute_ix = create_compute_budget_ix(compute_units=200_000)
            logger.info("Compute budget instruction created")
        except Exception as e:
            logger.error(f"Failed to create compute budget instruction: {e}")
            return None, None

        # Derive PDAs
        logger.info("\n🔐 Deriving PDAs")
        try:
            config_pda = derive_config_pda()
            route_params_pda = derive_route_params_pda(token_mint)
            route_state_pda = derive_route_state_pda(token_mint)
            token_vault_pda = derive_token_vault_pda(token_mint)

            logger.info("PDAs derived:")
            logger.info(f"  Config: {config_pda}")
            logger.info(f"  Route Params: {route_params_pda}")
            logger.info(f"  Route State: {route_state_pda}")
            logger.info(f"  Token Vault: {token_vault_pda}")
        except Exception as e:
            logger.error(f"Failed to derive PDAs: {e}")
            return None, None

        # Create required accounts
        logger.info("\n🏗️ Creating required account instructions")
        account_instructions = []
        
        for pda, name, space in [
            (route_params_pda, "Route Params", 165),
            (route_state_pda, "Route State", 165),
            (token_vault_pda, "Token Vault", 165)
        ]:
            try:
                logger.info(f"Creating instruction for {name}: {pda}")
                create_ix = create_account_ix(
                    payer=owner,
                    space=space,
                    program_id=PUMP_TRADE_PROGRAM_KEY,
                    new_account_pubkey=pda
                )
                if create_ix:
                    account_instructions.append(create_ix)
                    logger.info(f"Added creation instruction for {name}")
            except Exception as e:
                logger.error(f"Failed to create account instruction for {name}: {e}")
                return None, None

        # Create sell instruction using utils
        logger.info("\n📝 Creating sell instruction")
        try:
            sell_ix = await create_sell_instruction(
                token_mint=token_mint,
                owner=owner,
                amount=amount_in,
                min_output=min_out,
                slippage_bps=slippage_bps,
                token_ata=token_ata,
                wsol_vault=PUMP_WSOL_VAULT_KEY,
                fee_account=PUMP_FEE_ACCOUNT_KEY,
                program_id=PUMP_TRADE_PROGRAM_KEY
            )
            logger.info("Sell instruction created successfully")
        except Exception as e:
            logger.error(f"Failed to create sell instruction: {e}")
            return None, None

        # Compile all instructions
        logger.info("\n📦 Compiling final instruction list")
        all_instructions = []
        all_instructions.extend(account_instructions)
        all_instructions.append(compute_ix)
        all_instructions.append(sell_ix)
        logger.info(f"Total instructions: {len(all_instructions)}")

        # Build transaction
        logger.info("\n🏗️ Building final transaction")
        try:
            # Re-verify signer before building transaction
            if not validate_keypair_for_tx(signer, "pre-build verification"):
                logger.error("❌ Signer validation failed before building transaction")
                return None, None
                
            # Ensure we pass the actual Keypair
            tx_signers = [signer]  # List containing single verified Keypair
            
            logger.info("\n🔑 Using verified signer:")
            logger.info(f"  Type: {type(signer)}")
            logger.info(f"  Pubkey: {signer.pubkey()}")
            logger.info(f"  Can sign: {hasattr(signer, 'sign_message')}")
            
            # Build unsigned transaction with verified signer
            tx = await build_tx_with_blockhash(
                instructions=all_instructions,
                signers=tx_signers,  # Pass list of verified Keypairs
                executor=executor
            )
            
            if not tx:
                logger.error("Failed to build transaction")
                return None, None
                
            logger.info("\n✅ Transaction built successfully")
            return tx, all_instructions

        except Exception as e:
            logger.error(f"Failed to build transaction: {e}")
            logger.error("Stack trace:")
            traceback.print_exc()
            return None, None

    except Exception as e:
        logger.error(f"❌ Failed building sell transaction: {str(e)}")
        logger.error("Stack trace:")
        traceback.print_exc()
        return None, None

async def build_tx_with_blockhash(
    instructions: List[Instruction],
    signer: Keypair = None,
    executor: ExecutorProtocol = None,
    validate_accounts: bool = True,
    lookup_table_accounts: Optional[List[AddressLookupTableAccount]] = None,
    payer: Pubkey = None,
    signers: List[Keypair] = None
) -> Optional[VersionedTransaction]:
    """Build a versioned transaction with the latest blockhash."""
    try:
        logger.info("\n🏗️ Building transaction with blockhash")
        
        # 1. Validate basic parameters
        if not instructions:
            logger.error("❌ No instructions provided")
            return None
            
        # 2. Validate signers
        actual_signers = signers if signers else ([signer] if signer else [])
        if not actual_signers:
            logger.error("❌ No signers provided")
            return None
            
        # Validate all signers
        for idx, current_signer in enumerate(actual_signers):
            if not validate_keypair_for_tx(current_signer, f"Signer {idx+1}"):
                logger.error(f"❌ Invalid signer at position {idx}")
                return None
                
        # Use provided payer or first signer
        actual_payer = payer if payer else actual_signers[0].pubkey()
        logger.info(f"Using payer: {actual_payer}")
            
        # 3. Get blockhash
        recent_blockhash = None
        try:
            recent_blockhash = await executor.get_latest_blockhash()
            logger.info(f"Got blockhash: {recent_blockhash}")
        except Exception as e:
            logger.error(f"❌ Error getting blockhash: {e}")
            return None
                
        # 4. Build message
        try:
            message = MessageV0.try_compile(
                payer=actual_payer,
                instructions=instructions,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=lookup_table_accounts or []
            )
            logger.info("✅ Message compiled successfully")
        except Exception as e:
            logger.error(f"❌ Error compiling message: {e}")
            return None
            
        # 5. Create and sign transaction
        try:
            # Create and sign transaction in one step with all signers
            try:
                tx = VersionedTransaction(message=message, keypairs=actual_signers)
                logger.info("✅ Transaction created and signed successfully")
                logger.info(f"  Signatures: {len(tx.signatures)}")
                
                # Verify all signatures are present
                if len(tx.signatures) != len(actual_signers):
                    logger.error(f"❌ Missing signatures. Expected {len(actual_signers)}, got {len(tx.signatures)}")
                    return None
                
                return tx
            except Exception as e:
                logger.error(f"❌ Error creating/signing transaction: {e}")
                return None
                    
            # Verify we have all required signatures
            if len(tx.signatures) != len(actual_signers):
                logger.error(f"❌ Missing signatures. Expected {len(actual_signers)}, got {len(tx.signatures)}")
                return None
                
            logger.info("✅ Transaction built and signed successfully")
            return tx
            
        except Exception as e:
            logger.error(f"❌ Error creating/signing transaction: {e}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error in build_tx_with_blockhash: {e}")
        traceback.print_exc()
        return None

def validate_keypair_for_tx(keypair: Any, context: str = "unknown") -> bool:
    """
    Validate that a keypair is a proper Keypair instance and can sign.
    
    Args:
        keypair: The keypair to validate
        context: A string describing where this validation is happening
        
    Returns:
        bool: True if keypair is valid and can sign, False otherwise
    """
    try:
        if not isinstance(keypair, Keypair):
            logger.error(f"❌ {context}: Invalid type {type(keypair)}. Must be solders.keypair.Keypair")
            return False
            
        logger.info(f"✓ {context}: Valid Keypair type")
        logger.info(f"  Module: {keypair.__class__.__module__}")
        logger.info(f"  Type: {type(keypair)}")
        
        # Test signing capability
        try:
            test_message = bytes([1, 2, 3, 4])
            test_sig = keypair.sign_message(test_message)
            if not test_sig:
                logger.error(f"❌ {context}: Signing test failed - null signature")
                return False
            logger.info(f"✓ {context}: Signing capability verified")
            return True
        except Exception as e:
            logger.error(f"❌ {context}: Signing test failed: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {context}: Validation error: {str(e)}")
        return False

def get_user_pda_size_and_rent() -> Tuple[int, int]:
    """Get the required size and rent for a user PDA.
    
    Returns:
        Tuple[int, int]: (space, minimum_balance) for the PDA
    """
    space = 128  # Fixed size for Pump.fun user state
    rent = get_minimum_balance_for_rent_exemption(space)
    return space, rent

def create_user_init_instructions(owner: Pubkey) -> List[Instruction]:
    """
    Create all instructions needed to initialize a user's PDA in the PUMP protocol.
    
    Args:
        owner (Pubkey): The owner's public key (must be signer)
        
    Returns:
        List[Instruction]: List of instructions needed for full initialization
    """
    logger.info("Creating user initialization instructions")
    
    # Get the user's PDA address and bump
    user_pda = get_user_pda(owner)
    logger.info(f"User PDA derived: {user_pda}")
    
    # Get required space and rent
    space, rent = get_user_pda_size_and_rent()
    logger.info(f"User PDA requirements: {space} bytes, {rent} lamports rent")
    
    # Create system instruction to allocate space and rent
    # Build the CreateAccount instruction manually since we're working with a PDA
    # Format: [0, from_pubkey, to_pubkey, lamports, space, owner]
    create_data = bytes([0]) + rent.to_bytes(8, 'little') + space.to_bytes(8, 'little') + bytes(PUMP_TRADE_PROGRAM_KEY)
    
    create_account_ix = Instruction(
        program_id=SYS_PROGRAM_ID,
        accounts=[
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),      # From
            AccountMeta(pubkey=user_pda, is_signer=False, is_writable=True),  # To
        ],
        data=create_data
    )
    
    logger.info("System program create account instruction:")
    logger.info(f"  Program: {create_account_ix.program_id}")
    logger.info(f"  From: {owner}")
    logger.info(f"  To: {user_pda}")
    logger.info(f"  Space: {space}")
    logger.info(f"  Lamports: {rent}")
    logger.info(f"  Data (hex): {create_data.hex()}")
    
    # Verify create_account instruction
    logger.info("System program create account instruction:")
    logger.info(f"  Program: {create_account_ix.program_id}")
    logger.info(f"  From: {owner}")
    logger.info(f"  To: {user_pda}")
    logger.info(f"  Space: {space}")
    logger.info(f"  Lamports: {rent}")
    logger.info(f"  Owner: {PUMP_TRADE_PROGRAM_KEY}")
    
    # Create initialization instruction
    init_ix = create_user_init_instruction(owner)
    
    # Log details for both instructions
    logger.info("\n📋 User PDA Initialization Instructions:")
    logger.info("1. Create account instruction:")
    logger.info(f"  - Program: {create_account_ix.program_id}")
    logger.info(f"  - Accounts: {len(create_account_ix.accounts)}")
    logger.info(f"  - Data size: {len(create_account_ix.data)} bytes")
    logger.info("2. Initialize user instruction:")
    logger.info(f"  - Program: {init_ix.program_id}")
    logger.info(f"  - Accounts: {len(init_ix.accounts)}")
    logger.info(f"  - Data size: {len(init_ix.data)} bytes")
    logger.info(f"  - Data (hex): {init_ix.data.hex()}")
    
    return [create_account_ix, init_ix]
    
    # Create initialization instruction
    init_ix = create_user_init_instruction(owner)
    
    logger.info("Created user initialization instructions:")
    logger.info("1. Create account instruction:")
    logger.info(f"  From: {owner}")
    logger.info(f"  To: {user_pda}")
    logger.info(f"  Space: {space}")
    logger.info(f"  Rent: {rent}")
    logger.info(f"  Owner: {PUMP_TRADE_PROGRAM_KEY}")
    logger.info("2. Initialize user instruction:")
    logger.info(f"  Program: {PUMP_TRADE_PROGRAM_KEY}")
    logger.info(f"  User PDA: {user_pda}")
    
    return [create_account_ix, init_ix]

async def verify_user_pda_needs_init(executor: ExecutorProtocol, pda: Pubkey, owner: Pubkey) -> bool:
    """Verify if a user's PDA needs initialization.
    
    Args:
        executor: The executor for querying account info
        pda: The PDA to check
        owner: The owner's pubkey
        
    Returns:
        bool: True if PDA needs initialization, False if already properly initialized
    """
    logger.info("\n🔍 Checking PDA initialization state")
    logger.info(f"PDA: {pda}")
    logger.info(f"Owner: {owner}")
    
    try:
        # Get account info
        account_info = await executor.get_account_info(pda)
        
        if not account_info:
            logger.info("✅ PDA does not exist - needs initialization")
            return True
            
        # Check owner
        if str(account_info.get("owner")) != str(PUMP_ROUTER):
            logger.info(f"❌ PDA has wrong owner: {account_info.get('owner')}")
            logger.info(f"Expected owner: {PUMP_ROUTER}")
            return True
            
        # Check data
        data = account_info.get("data", [])
        if not data or not isinstance(data, list) or not data[0]:
            logger.info("❌ PDA has no data")
            return True
            
        # Check discriminator (first 8 bytes of data)
        try:
            raw_data = base64.b64decode(data[0])
            discriminator = raw_data[:8]
            expected_discriminator = bytes.fromhex("b5f9b1e8179d8e84")  # initialize_user
            if discriminator != expected_discriminator:
                logger.info("❌ PDA has wrong discriminator")
                logger.info(f"Found: {discriminator.hex()}")
                logger.info(f"Expected: {expected_discriminator.hex()}")
                return True
        except Exception as e:
            logger.error(f"Error checking discriminator: {e}")
            return True
            
        logger.info("✅ PDA is properly initialized")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error checking PDA state: {e}")
        return True
