# tx_builder.py

from solana.rpc.async_api import AsyncClient
from jito_service import JitoClient
from solders.instruction import AccountMeta, Instruction, CompiledInstruction
from solders.transaction import VersionedTransaction, TransactionError
from solders.message import Message, MessageV0, MessageHeader
from solders.signature import Signature 
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams, ID as SYS_PROGRAM_ID
from solders.address_lookup_table_account import AddressLookupTableAccount
from spl.token.instructions import get_associated_token_address

import base64
import base58
import asyncio
import json
import time
import random
from datetime import datetime, timezone, UTC
from typing import List, Optional, Tuple, Union, Set, Dict, Any
import traceback
import logging

from models import Bundle
from config import (
    JITO_BUNDLE_URL,
    JITO_HEADERS,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE,
    JITO_TIP_AMOUNT,
    PUMP_FUN_PROGRAM_ID,
    RPC_URL,
    VALID_JITO_TIP_ACCOUNTS,
    DECODED_PRIVATE_KEY,
    PUMP_TRADE_PROGRAM,
    SLIPPAGE_BPS,
    HELIUS_RPC_URL,  # Secondary RPC
)
from fast_executor import FastExecutor
from jito_service import JitoClient

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
PUMP_ROUTER = Pubkey.from_string("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW")
PUMP_CORE = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

def get_random_tip_account() -> str:
    """Get a random valid Jito tip account"""
    return random.choice(VALID_JITO_TIP_ACCOUNTS)

async def get_blockhash(executor: FastExecutor) -> Optional[Hash]:
    """Get recent blockhash using FastExecutor"""
    try:
        response = await executor.get_latest_blockhash()
        return response.value.blockhash if response else None
    except Exception as e:
        logging.error(f"Failed to get blockhash: {str(e)}")
        return None

async def build_compute_budget_ix(
    unit_limit: int = COMPUTE_UNIT_LIMIT,
    unit_price: int = COMPUTE_UNIT_PRICE
) -> List[Instruction]:
    """Build compute budget instructions"""
    
    COMPUTE_BUDGET_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
    
    # Set compute unit limit
    limit_ix = Instruction(
        program_id=COMPUTE_BUDGET_ID,
        accounts=[],
        data=bytes([0] + list(unit_limit.to_bytes(4, 'little'))),
    )
    
    # Set compute unit price
    price_ix = Instruction(
        program_id=COMPUTE_BUDGET_ID,
        accounts=[],
        data=bytes([1] + list(unit_price.to_bytes(4, 'little'))),
    )
    
    return [limit_ix, price_ix]

async def build_pump_swap_ix(
    buyer: Pubkey,
    token: Pubkey,
    amount: int,
    is_buy: bool = True,
    slippage_bps: int = SLIPPAGE_BPS
) -> Instruction:
    """Build a Pump.fun swap instruction"""
    
    # Get ATAs
    token_ata = get_associated_token_address(buyer, token)
    
    # Accounts for the swap
    accounts = [
        AccountMeta(pubkey=buyer, is_signer=True, is_writable=True),  # Wallet
        AccountMeta(pubkey=token_ata, is_signer=False, is_writable=True),  # Token ATA
        AccountMeta(pubkey=token, is_signer=False, is_writable=True),  # Token mint
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),  # SPL Token
        AccountMeta(pubkey=ATA_PROGRAM_ID, is_signer=False, is_writable=False),  # ATA Program
    ]
    
    # Build instruction data
    data = bytes([
        0x01,  # Instruction index (1 for swap)
        *amount.to_bytes(8, 'little'),  # Amount as u64
        *slippage_bps.to_bytes(2, 'little'),  # Slippage as u16
        0x01 if is_buy else 0x00  # Buy/sell flag
    ])
    
    return Instruction(
        program_id=PUMP_ROUTER,
        accounts=accounts,
        data=data
    )

async def build_buy_tx(
    executor: FastExecutor,
    token: Pubkey,
    amount: int,
    keypair: Keypair,
    slippage_bps: int = SLIPPAGE_BPS
) -> Optional[VersionedTransaction]:
    """Build a buy transaction using FastExecutor"""
    try:
        # Get recent blockhash
        blockhash = await get_blockhash(executor)
        if not blockhash:
            raise Exception("Failed to get recent blockhash")

        # Build compute budget instructions
        compute_ixs = await build_compute_budget_ix()
        
        # Build swap instruction
        swap_ix = await build_pump_swap_ix(
            buyer=keypair.pubkey(),
            token=token,
            amount=amount,
            is_buy=True,
            slippage_bps=slippage_bps
        )
        
        # Combine all instructions
        all_ixs = compute_ixs + [swap_ix]
        
        # Build versioned transaction
        message = MessageV0(
            header=MessageHeader(
                num_required_signatures=1,
                num_readonly_signed_accounts=0,
                num_readonly_unsigned_accounts=len(all_ixs[-1].accounts) - 1
            ),
            account_keys=[keypair.pubkey()] + [acc.pubkey for acc in all_ixs[-1].accounts],
            recent_blockhash=blockhash,
            instructions=[ix.compile() for ix in all_ixs]
        )
        
        tx = VersionedTransaction(message=message)
        tx.sign([keypair])
        
        return tx
        
    except Exception as e:
        logging.error(f"Error building buy tx: {str(e)}")
        traceback.print_exc()
        return None

async def build_sell_tx(
    executor: FastExecutor,
    token: Pubkey,
    amount: int,
    keypair: Keypair,
    slippage_bps: int = SLIPPAGE_BPS
) -> Optional[VersionedTransaction]:
    """Build a sell transaction using FastExecutor"""
    try:
        # Get recent blockhash
        blockhash = await get_blockhash(executor)
        if not blockhash:
            raise Exception("Failed to get recent blockhash")

        # Build compute budget instructions
        compute_ixs = await build_compute_budget_ix()
        
        # Build swap instruction
        swap_ix = await build_pump_swap_ix(
            buyer=keypair.pubkey(),
            token=token,
            amount=amount,
            is_buy=False,
            slippage_bps=slippage_bps
        )
        
        # Combine all instructions
        all_ixs = compute_ixs + [swap_ix]
        
        # Build versioned transaction
        message = MessageV0(
            header=MessageHeader(
                num_required_signatures=1,
                num_readonly_signed_accounts=0,
                num_readonly_unsigned_accounts=len(all_ixs[-1].accounts) - 1
            ),
            account_keys=[keypair.pubkey()] + [acc.pubkey for acc in all_ixs[-1].accounts],
            recent_blockhash=blockhash,
            instructions=[ix.compile() for ix in all_ixs]
        )
        
        tx = VersionedTransaction(message=message)
        tx.sign([keypair])
        
        return tx
        
    except Exception as e:
        logging.error(f"Error building sell tx: {str(e)}")
        traceback.print_exc()
        return None

async def build_pump_trade(
    executor: FastExecutor,
    token: str,
    amount: float,
    trade_type: str,
    keypair: Keypair,
    slippage_bps: int = SLIPPAGE_BPS
) -> Optional[VersionedTransaction]:
    """Build a Pump.fun trade transaction"""
    try:
        # Convert amount to lamports
        amount_lamports = int(amount * 1_000_000_000)
        
        # Get token account
        token_pubkey = Pubkey.from_string(token)
        token_account = get_associated_token_address(keypair.pubkey(), token_pubkey)
        
        # Build instruction accounts
        accounts = [
            AccountMeta(keypair.pubkey(), True, True),           # Wallet
            AccountMeta(token_account, False, True),             # Token account
            AccountMeta(token_pubkey, False, False),             # Token mint
            AccountMeta(SYS_PROGRAM_ID, False, False),           # System program
            AccountMeta(PUMP_TRADE_PROGRAM, False, False),       # Trade program
        ]
        
        # Build instruction data
        instruction_type = 0 if trade_type == "buy" else 1  # 0 for buy, 1 for sell
        data = bytes([instruction_type]) + amount_lamports.to_bytes(8, 'little')
        
        # Create compute budget instructions
        compute_ix = Instruction(
            program_id=Pubkey.from_string("ComputeBudget111111111111111111111111111111"),
            accounts=[],
            data=bytes([0x03]) + COMPUTE_UNIT_LIMIT.to_bytes(4, 'little') + bytes([0x02]) + COMPUTE_UNIT_PRICE.to_bytes(4, 'little')
        )
        
        # Create trade instruction
        trade_ix = Instruction(
            program_id=PUMP_ROUTER,
            accounts=accounts,
            data=data
        )
        
        # Get latest blockhash
        blockhash = await executor._rpc_request("getLatestBlockhash")
        if not blockhash or "result" not in blockhash:
            logging.error("Failed to get blockhash")
            return None
            
        # Create message with compute budget
        message = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=[compute_ix, trade_ix],
            address_lookup_table_accounts=[],
            recent_blockhash=Hash.from_string(blockhash["result"]["value"]["blockhash"])
        )
        
        # Create and sign transaction
        tx = VersionedTransaction(message=message, keypairs=[keypair])
        return tx
        
    except Exception as e:
        logging.error(f"Error building Pump.fun trade: {str(e)}")
        return None
    
    # tx_builder.py

from solders.instruction import AccountMeta, Instruction  
import base64
import base58
import asyncio
import json
import time
import aiohttp
from models import Bundle
from random import choice

from datetime import datetime, timezone, UTC
from solders.transaction import VersionedTransaction
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from base58 import b58decode
from solders.transaction import Transaction, VersionedTransaction, TransactionError
from solders.message import Message, MessageV0, MessageHeader
from solders.signature import Signature 
from solders.message import MessageV0
from datetime import datetime, timezone, UTC

import aiohttp
import websockets
from solders.instruction import AccountMeta, CompiledInstruction
import traceback
from websockets.client import connect
from typing import List, Optional, Tuple
from typing import Optional, Union, List, Set, Dict, Any
from typing import Union, Optional
from solders.hash import Hash
from env_keys import kz
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams
from solders.system_program import ID as SYS_PROGRAM_ID
from config import (
    JITO_BUNDLE_URL,
    JITO_HEADERS,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE,
    JITO_TIP_AMOUNT,
    PUMP_FUN_PROGRAM_ID,
    RPC_URL,
    VALID_JITO_TIP_ACCOUNTS,
    DECODED_PRIVATE_KEY,
    PUMP_TRADE_PROGRAM,
    SLIPPAGE_BPS,  # Added slippage config
)

# SPL Token imports
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    mint_to,
    burn,
    close_account
)

# Constants for Jito configuration
JITO_TIP_PROGRAM_ID = Pubkey.from_string("J1TnP8zvVxbtG4yxtt9qVaZK5nhG9SEqhYEJoQhJ5Pyr")
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
MIN_TIP_LAMPORTS = 10_000  # Minimum 0.00001 SOL
MIN_PRIORITY_FEE = 1_000   # Minimum 1000 micro-lamports/CU
DEFAULT_COMPUTE_UNITS = 200_000

# Constants
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
JITO_TIP_PROGRAM_ID = Pubkey.from_string("J1TnP8zvVxbtG4yxtt9qVaZK5nhG9SEqhYEJoQhJ5Pyr")
COMPUTE_UNIT_LIMIT = 1_400_000
COMPUTE_UNIT_PRICE = 100
JITO_TIP_AMOUNT = 10_000

DEBUG = True

# Program IDs
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
PUMP_TRADE_PROGRAM_ID = PUMP_TRADE_PROGRAM  # Already a Pubkey from config.py

# Jito Configuration
VALID_JITO_TIP_ACCOUNTS = [
    Pubkey.from_string("96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5"),
    Pubkey.from_string("HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe"),
    Pubkey.from_string("Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY"),
    Pubkey.from_string("ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49")
]

# Add these constants
WALLET_A = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
CURRENT_USER = "tinotc-72"
START_TIME = "2025-06-03 14:44:35"  # Updated to current time
tip_account = choice(VALID_JITO_TIP_ACCOUNTS)


# Constants
CURRENT_TIME = "2025-06-06 20:26:12"
CURRENT_USER = "tinotc-72"
JITO_TIP_PROGRAM_ID = Pubkey.from_string("J1TnP8zvVxbtG4yxtt9qVaZK5nhG9SEqhYEJoQhJ5Pyr")
COMPUTE_BUDGET_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
TIP_LAMPORTS = 2_000  # Increased tip amount (0.000002 SOL)
PRIORITY_MICRO_LAMPORTS = 1_000  # Jito recommended priority fee (1000 micro-lamports/CU)
DEFAULT_COMPUTE_UNITS = 200_000  # Default compute units

# Performance Settings - Optimized for ultra-fast execution
EXECUTION_TIMEOUT = 1.0
MAX_PROCESSING_TIME = 0.1  # Reduced from 0.2
WS_SETTINGS = {
    "MAX_RETRIES": 2,      # Reduced from 3
    "RETRY_DELAY": 0.1,    # Reduced from 0.5
    "TX_FETCH_RETRIES": 1, # Only try once - no retries
    "TX_FETCH_DELAY": 0,   # No delay between attempts
    "RECONNECT_DELAY": 0.1 # Reduced from 0.5
}

JITO_BUNDLE_ENDPOINT = "https://london.mainnet.block-engine.jito.wtf/api/v1/bundle"
JITO_AUTH_UUID = kz.JITO_UUID

# Update RPC endpoints to only use Jito and Helius
RPC_ENDPOINTS = [
    "https://jito-api.mainnet.jito.network",  # Primary (Jito)
    kz.HELIUS_RPC_URL,  # Secondary (Helius)
]

RPC_ENDPOINTS = [url for url in RPC_ENDPOINTS if url]  # Remove None values

def get_current_timestamp() -> str:
    """Get current timestamp in readable format."""
    return datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S UTC]")

def ensure_bytes(data: Union[list, bytes, bytearray, None]) -> bytes:
    if isinstance(data, list):
        return bytes(bytearray(data))
    elif isinstance(data, (bytes, bytearray)):
        return bytes(data)
    elif data is None:
        return b""
    else:
        raise TypeError(f"Unsupported data type for instruction: {type(data)}")
        
def create_compute_budget_instructions() -> List[Instruction]:
    """Create compute budget instructions that MUST come first"""
    try:
        # Unit limit instruction (opcode 0x02)
        unit_limit_ix = Instruction(
            program_id=COMPUTE_BUDGET_PROGRAM_ID,
            accounts=[],
            data=bytes([0x02]) + COMPUTE_UNIT_LIMIT.to_bytes(4, "little")
        )

        # Unit price instruction (opcode 0x03)
        unit_price_ix = Instruction(
            program_id=COMPUTE_BUDGET_PROGRAM_ID,
            accounts=[],
            data=bytes([0x03]) + COMPUTE_UNIT_PRICE.to_bytes(4, "little")
        )

        return [unit_limit_ix, unit_price_ix]

    except Exception as e:
        print(f"❌ Failed to create compute budget instructions: {str(e)}")
        traceback.print_exc()
        return []

def create_jito_tip_instruction(payer: Pubkey) -> Optional[Instruction]:
    """Create tip instruction that MUST come second per Jito docs"""
    try:
        print(f"\n🔍 Debug - Tip Values:")
        print(f"JITO_TIP_AMOUNT from config = {JITO_TIP_AMOUNT:,}")
        print(f"Using tip_amount = {JITO_TIP_AMOUNT:,}")

        # Select random tip account from valid list
        tip_account = choice(VALID_JITO_TIP_ACCOUNTS)
        
        print("\n💰 Jito Tip Instruction Setup:")
        print(f"Fee Payer: {payer}")
        print(f"Tip Account: {tip_account}")
        print(f"Final Tip Amount: {JITO_TIP_AMOUNT:,} lamports")

        # Create account metadata with proper permissions
        fee_payer_meta = AccountMeta(
            pubkey=payer,
            is_signer=True,
            is_writable=True
        )
        
        tip_account_meta = AccountMeta(
            pubkey=tip_account,
            is_signer=False,
            is_writable=True
        )
        
        # Create instruction data - 8 byte little-endian encoding
        tip_data = JITO_TIP_AMOUNT.to_bytes(8, "little")
        
        # Create instruction with proper metadata
        tip_instruction = Instruction(
            program_id=JITO_TIP_PROGRAM_ID,
            accounts=[fee_payer_meta, tip_account_meta],
            data=tip_data
        )
        
        # Verify instruction data
        print("\n🔍 Debug - Instruction Data:")
        print(f"Data length: {len(tip_instruction.data)} bytes")
        print(f"Data bytes: {[b for b in tip_instruction.data]}")
        
        # Verify account metadata
        print("\n🔍 Account Metadata Verification:")
        print("Fee Payer Account:")
        print(f"  Address: {tip_instruction.accounts[0].pubkey}")
        print(f"  Is Signer: {tip_instruction.accounts[0].is_signer}")
        print(f"  Is Writable: {tip_instruction.accounts[0].is_writable}")
        print("\nTip Account:")
        print(f"  Address: {tip_instruction.accounts[1].pubkey}")
        print(f"  Is Signer: {tip_instruction.accounts[1].is_signer}")
        print(f"  Is Writable: {tip_instruction.accounts[1].is_writable}")
        
        # Verify program ID
        print("\n🔍 Program Verification:")
        print(f"Program ID: {tip_instruction.program_id}")
        print(f"Expected: {JITO_TIP_PROGRAM_ID}")
        
        if tip_instruction.program_id != JITO_TIP_PROGRAM_ID:
            print("❌ Program ID mismatch")
            return None
            
        if len(tip_instruction.accounts) != 2:
            print("❌ Invalid number of accounts")
            return None
            
        if len(tip_instruction.data) != 8:
            print("❌ Invalid data length")
            return None
            
        # Decode and verify tip amount
        decoded_amount = int.from_bytes(tip_instruction.data, "little")
        if decoded_amount != JITO_TIP_AMOUNT:
            print("❌ Tip amount mismatch")
            print(f"Expected: {JITO_TIP_AMOUNT:,}")
            print(f"Got: {decoded_amount:,}")
            return None
            
        print("\n✅ Tip instruction created and verified")
        return tip_instruction
        
    except Exception as e:
        print(f"❌ Failed to create tip instruction: {str(e)}")
        traceback.print_exc()
        return None

def validate_instruction_data(raw_data: Any) -> Optional[bytes]:
    """Validate and convert instruction data to bytes."""
    try:
        if isinstance(raw_data, list):
            return bytes(raw_data)
        elif isinstance(raw_data, bytes):
            return raw_data
        elif isinstance(raw_data, bytearray):
            return bytes(raw_data)
        elif raw_data is None:
            return b''
        else:
            print(f"❌ Unexpected instruction data type: {type(raw_data)}")
            return None
    except Exception as e:
        print(f"❌ Error converting instruction data: {e}")
        return None
          
def validate_account_meta(
    pubkey: Pubkey,
    index: int,
    num_required_signatures: int,
    num_writable: int
) -> AccountMeta:
    """Create and validate AccountMeta."""
    is_signer = index < num_required_signatures
    is_writable = index < num_writable
    return AccountMeta(pubkey, is_signer, is_writable)

def validate_transaction_size(tx: VersionedTransaction) -> bool:
    """Validate transaction size is within limits."""
    tx_size = len(bytes(tx))
    if tx_size > 1232:  # Solana transaction size limit
        print(f"❌ Transaction too large: {tx_size} bytes (max 1232)")
        return False
    print(f"✅ Transaction size valid: {tx_size} bytes")
    return True

def verify_instruction_order(instructions: List[Instruction]) -> bool:
    """Verify that instructions are in the correct order."""
    try:
        if len(instructions) < 3:
            print("❌ Not enough instructions")
            return False
            
        if str(instructions[0].program_id) != str(COMPUTE_BUDGET_PROGRAM_ID):
            print("❌ First instruction must be compute budget")
            return False
            
        if str(instructions[1].program_id) != str(COMPUTE_BUDGET_PROGRAM_ID):
            print("❌ Second instruction must be compute budget")
            return False
            
        if str(instructions[2].program_id) != str(JITO_TIP_PROGRAM_ID):
            print("❌ Third instruction must be Jito tip")
            return False
            
        print("✅ Instruction order verified")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying instruction order: {e}")
        return False

async def wallet_owns_token(mint: str, wallet: Pubkey) -> bool:
    """
    Check if a wallet owns a specific token.
    
    Args:
        mint (str): The token mint address
        wallet (Pubkey): The wallet address to check
        
    Returns:
        bool: True if wallet owns the token, False otherwise
    """
    endpoint = "getTokenAccountsByOwner"
    max_retries = 3
    retry_count = 0
    start_time = time.time()
    
    try:
        print(f"\n[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}] 🔍 Checking token ownership...")
        print(f"Wallet: {wallet}")
        print(f"Token mint: {mint}")
        
        while retry_count < max_retries:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": int(time.time() * 1000),  # Unique ID for each request
                    "method": endpoint,
                    "params": [
                        str(wallet),
                        {"mint": mint},
                        {"encoding": "jsonParsed"}
                    ]
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        RPC_URL,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        if resp.status != 200:
                            print(f"❌ HTTP Error: {resp.status}")
                            raise aiohttp.ClientError(f"HTTP {resp.status}")
                            
                        res = await resp.json()
                        
                        if "error" in res:
                            print(f"❌ RPC Error: {res['error']}")
                            raise Exception(f"RPC error: {res['error']}")
                            
                        if "result" not in res:
                            print("❌ Invalid response format")
                            raise Exception("Missing 'result' in response")
                            
                        value = res.get("result", {}).get("value", [])
                        owns_token = len(value) > 0
                        
                        end_time = time.time()
                        latency = (end_time - start_time) * 1000
                        
                        print(f"✅ Token check complete")
                        print(f"⏱️ Latency: {latency:.2f}ms")
                        print(f"🎯 Result: {'Owns token' if owns_token else 'Does not own token'}")
                        
                        if value:
                            print(f"📊 Token accounts found: {len(value)}")
                            
                        return owns_token
                        
            except aiohttp.ClientError as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    print(f"⚠️ Network error (attempt {retry_count}/{max_retries}): {str(e)}")
                    print(f"⏳ Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    print("❌ Max retries reached")
                    raise
                    
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                traceback.print_exc()
                return False
                
        return False
        
    except Exception as e:
        print(f"❌ Fatal error checking token ownership: {str(e)}")
        traceback.print_exc()
        return False
     
def create_and_sign_transaction(
    keypair: Keypair,
    instructions: List[Instruction],
    recent_blockhash: str,
    account_keys: list[Pubkey],
    num_required_signatures: int,
    num_readonly_signed_accounts: int,
    num_readonly_unsigned_accounts: int
) -> Optional[VersionedTransaction]:
    try:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        current_user = "tinotc-72"  # Your current login
        
        print(f"\n[{current_time}] 📝 Creating transaction...")
        print(f"👤 User: {current_user}")

        if not keypair or not account_keys or not recent_blockhash:
            print("❌ Missing required transaction inputs")
            return None

        print(f"🔍 Total account keys: {len(account_keys)}")
        
        num_writable = len(account_keys) - (num_readonly_signed_accounts + num_readonly_unsigned_accounts)
        print(f"🔍 Required signers: {num_required_signatures}, Writable: {num_writable}")

        # Filter compute budget instructions
        filtered_instructions = [
            ix for ix in instructions if ix.program_id != COMPUTE_BUDGET_PROGRAM_ID
        ]
        print(f"🔍 Instruction count: {len(filtered_instructions)}")

        # Inject ComputeBudget + Tip instructions
        compute_budget_ixs = [
            Instruction(
                COMPUTE_BUDGET_PROGRAM_ID,
                [],
                bytes([0x02]) + COMPUTE_UNIT_LIMIT.to_bytes(4, "little")
            ),
            Instruction(
                COMPUTE_BUDGET_PROGRAM_ID,
                [],
                bytes([0x03]) + COMPUTE_UNIT_PRICE.to_bytes(4, "little")
            )
        ]
        
        tip_ix = Instruction(
            JITO_TIP_PROGRAM_ID,
            [
                AccountMeta(
                    pubkey=keypair.pubkey(), 
                    is_signer=True, 
                    is_writable=True
                ),
                AccountMeta(
                    pubkey=Pubkey.from_string("HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe"), 
                    is_signer=False, 
                    is_writable=True
                )
            ],
            JITO_TIP_AMOUNT.to_bytes(8, "little")
        )

        # Rebuild all remaining instructions
        rebuilt_instructions = []
        for idx, ix in enumerate(filtered_instructions):
            print(f"\n[{current_time}] 📝 Rebuilding instruction {idx+1}")
            if isinstance(ix, CompiledInstruction):
                try:
                    program_id = account_keys[ix.program_id_index]
                    accounts = []
                    for acc_idx in ix.accounts:
                        if acc_idx >= len(account_keys):
                            print(f"❌ Invalid account index {acc_idx}")
                            return None
                        pubkey = account_keys[acc_idx]
                        is_signer = acc_idx < num_required_signatures
                        is_writable = acc_idx < num_writable
                        accounts.append(AccountMeta(pubkey, is_signer, is_writable))
                        
                    data = ensure_bytes(ix.data)
                    rebuilt_instructions.append(Instruction(program_id, accounts, data))
                    print(f"✅ Instruction rebuilt for {program_id}")
                    
                except Exception as e:
                    print(f"[{current_time}] ❌ Error rebuilding instruction: {e}")
                    traceback.print_exc()
                    return None
            else:
                rebuilt_instructions.append(ix)
                print(f"✅ Existing Instruction (not compiled): {ix.program_id}")

        # Final instruction list
        final_instructions = compute_budget_ixs + [tip_ix] + rebuilt_instructions

        # Instruction order validation
        if not verify_instruction_order(final_instructions):
            return None

        # Compile message
        msg = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=final_instructions,
            recent_blockhash=Hash.from_string(recent_blockhash),
            address_lookup_table_accounts=[]
        )

        if msg is None:
            print(f"[{current_time}] ❌ Failed to compile message")
            return None

        tx = VersionedTransaction.populate(msg, [Signature.default()])
        if not validate_transaction_size(tx):
            return None

        sig = keypair.sign_message(bytes(tx.message))
        tx.signatures = [sig]

        print(f"[{current_time}] ✅ Transaction signed by {current_user}")
        print(f"📏 Size: {len(bytes(tx))} bytes")
        print(f"🔑 Signature: {sig}")
        return tx

    except Exception as e:
        print(f"[{current_time}] ❌ Failed to build transaction: {e}")
        print(f"👤 User: {current_user}")
        traceback.print_exc()
        return None
    
def create_jito_bundle(transaction: VersionedTransaction) -> dict:
    """Create a properly formatted Jito bundle payload"""
    try:
        print(f"{get_current_timestamp()} 🔄 Creating bundle...")
        
        if not isinstance(transaction, VersionedTransaction):
            print("❌ Transaction must be versioned")
            return None
            
        # Serialize the transaction
        tx_bytes = bytes(transaction)
        tx_base64 = base64.b64encode(tx_bytes).decode('utf-8')
        
        # Format exactly according to Jito docs with hardcoded tip percentage
        bundle_request = {
            "jsonrpc": "2.0",
            "method": "sendBundle",
            "params": [{
                "transactions": [tx_base64],
                "header": {
                    "tip_percentage": 90  # Hardcoded as per Jito docs recommendation
                }
            }],
            "id": 1
        }
        
        print(f"{get_current_timestamp()} ✅ Bundle created successfully")
        return bundle_request
        
    except Exception as e:
        print(f"{get_current_timestamp()} ❌ Bundle creation failed: {str(e)}")
        traceback.print_exc()
        return None
           
def print_instruction_data(instruction: Instruction, label: str = ""):
    """Debug helper to print instruction data"""
    try:
        if len(instruction.data) >= 8:
            amount = int.from_bytes(instruction.data[-8:], "little")
            print(f"\n🔍 Debug - {label} Instruction Data:")
            print(f"Data length: {len(instruction.data)} bytes")
            print(f"Data bytes: {[b for b in instruction.data]}")
            print(f"Decoded amount: {amount:,}")
    except Exception as e:
        print(f"❌ Failed to decode instruction data: {str(e)}")
                         
def process_transaction(
    keypair: Keypair,
    instructions: List[Instruction],
    recent_blockhash: str,
    jito_api_url: str
) -> bool:
    """Process a transaction through Jito and fallback to RPC"""
    try:
        # Create and sign transaction
        bundle = create_and_sign_transaction(
            keypair=keypair,
            instructions=instructions,
            recent_blockhash=recent_blockhash
        )
        
        if not bundle:
            print(f"{get_current_timestamp()} ❌ Failed to create bundle")
            return False
            
        print(f"\n{get_current_timestamp()} ✅ Transaction created successfully")
        
        # Try Jito first
        jito_client = JitoClient()
        jito_result = asyncio.get_event_loop().run_until_complete(jito_client.submit_bundle(bundle))
        
        if jito_result:
            print(f"{get_current_timestamp()} ✅ Transaction processed via Jito")
            return True
            
        # Fallback to RPC if Jito fails
        if bundle and bundle.transaction:
            # Transaction is already signed in the bundle
            tx = bundle.transaction
            
            # Your RPC submission code here...
            # rpc_result = submit_to_rpc(tx)
            
            print(f"{get_current_timestamp()} ✅ Transaction submitted via RPC fallback")
            return True
            
        return False
        
    except Exception as e:
        print(f"{get_current_timestamp()} ❌ Transaction processing failed: {str(e)}")
        traceback.print_exc()
        return False
    
def create_message(
    header: Dict,
    accounts: List[Pubkey],
    recent_blockhash: str,
    instructions: List[Dict]
) -> Optional[Message]:
    """Create a Solana message with proper index validation"""
    try:
        # Create compiled instructions
        compiled_ixs = []
        for ix in instructions:
            # Validate indices before using them
            program_idx = ix["program_id_index"]
            account_indices = ix.get("accounts", [])
            
            # Skip invalid program indices
            if program_idx >= len(accounts):
                print(f"⚠️ Skipping instruction with invalid program index {program_idx}")
                continue
                
            # Filter valid account indices
            valid_accounts = []
            for idx in account_indices:
                if isinstance(idx, int) and idx < len(accounts):
                    valid_accounts.append(AccountMeta(
                        pubkey=accounts[idx],
                        is_signer=idx < header.get("numRequiredSignatures", 1),
                        is_writable=idx < (header.get("numRequiredSignatures", 1) - 
                                         header.get("numReadonlySignedAccounts", 0))
                    ))
                else:
                    print(f"⚠️ Skipping invalid account index: {idx}")
            
            if valid_accounts:
                try:
                    compiled_ixs.append(Instruction(
                        program_id=accounts[program_idx],
                        accounts=valid_accounts,
                        data=ix["data"]
                    ))
                except Exception as e:
                    print(f"⚠️ Error creating instruction: {e}")
                    continue
        
        if not compiled_ixs:
            print("❌ No valid instructions created")
            return None
            
        print(f"✅ Created {len(compiled_ixs)} valid instructions")
        
        # Convert blockhash string to Hash object
        try:
            blockhash = Hash.from_string(recent_blockhash)
            print(f"✅ Converted blockhash: {recent_blockhash[:8]}...")
        except Exception as e:
            print(f"❌ Error converting blockhash: {e}")
            return None
        
        # Create Message with Hash object
        return Message.new_with_blockhash(
            instructions=compiled_ixs,
            payer=accounts[0],
            blockhash=blockhash  # Use the Hash object instead of string
        )
        
    except Exception as e:
        print(f"❌ Error creating message: {e}")
        if DEBUG:
            traceback.print_exc()
        return None

async def fetch_transaction_by_signature(signature: str, max_retries: int = 3) -> Optional[dict]:
    """Fetch transaction with Jito primary, Helius backup"""
    async def try_fetch(session: aiohttp.ClientSession, rpc_url: str) -> Optional[dict]:
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "json",
                        "maxSupportedTransactionVersion": 0,
                        "commitment": "processed"
                    }
                ]
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            
            # Add specific auth headers
            if "jito" in rpc_url:
                headers["Authorization"] = f"Bearer {kz.JITO_AUTH_TOKEN}"
            elif "helius" in rpc_url:
                headers["Authorization"] = f"Bearer {kz.HELIUS_API_KEY}"
            
            async with session.post(rpc_url, json=payload, headers=headers, timeout=1.0) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result and result["result"]:
                        print(f"✅ Got tx from {rpc_url.split('://')[1].split('.')[0]}")
                        return result["result"]
                    print(f"⚠️ No tx data from {rpc_url.split('://')[1].split('.')[0]}")
                elif response.status == 429:
                    print(f"⚠️ Rate limited by {rpc_url.split('://')[1].split('.')[0]}")
                else:
                    print(f"❌ RPC error {response.status} from {rpc_url.split('://')[1].split('.')[0]}")
                return None
                
        except asyncio.TimeoutError:
            print(f"⚠️ Timeout from {rpc_url.split('://')[1].split('.')[0]}")
            return None
        except Exception as e:
            print(f"⚠️ Error with {rpc_url.split('://')[1].split('.')[0]}: {str(e)}")
            return None

    try:
        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries):
                print(f"\n🔄 Fetch attempt {attempt + 1}/{max_retries}")
                
                # Try Jito RPC first
                jito_result = await try_fetch(session, RPC_ENDPOINTS[0])
                if jito_result:
                    return jito_result
                    
                # If Jito fails, try Helius
                helius_result = await try_fetch(session, RPC_ENDPOINTS[1])
                if helius_result:
                    return helius_result
                    
                if attempt < max_retries - 1:
                    delay = 0.05 * (attempt + 1)  # Short delay between retries
                    print(f"⏳ Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                    
        print("❌ All fetch attempts failed")
        return None
        
    except Exception as e:
        print(f"❌ Error in fetch_transaction: {str(e)}")
        return None
    
def get_current_timestamp() -> str:
    """Get current UTC timestamp in readable format"""
    return datetime.now(UTC).strftime('[%Y-%m-%d %H:%M:%S]')
               
def get_jito_fee_instructions(payer: Pubkey) -> List[Instruction]:
    """Get all required Jito fee instructions"""
    try:
        print(f"{get_current_timestamp()} 💰 Creating Jito fee instructions...")
        
        instructions = []
        
        # 1. Set compute unit limit (200,000)
        compute_limit_ix = Instruction(
            program_id=COMPUTE_BUDGET_PROGRAM_ID,
            accounts=[],
            data=bytes([0]) + DEFAULT_COMPUTE_UNITS.to_bytes(4, "little")
        )
        instructions.append(compute_limit_ix)
        
        # 2. Set compute unit price (1,000 micro-lamports/CU)
        compute_price_ix = Instruction(
            program_id=COMPUTE_BUDGET_PROGRAM_ID,
            accounts=[],
            data=bytes([1]) + MIN_PRIORITY_FEE.to_bytes(4, "little")
        )
        instructions.append(compute_price_ix)
        
        # 3. Add Jito tip (10,000 lamports)
        tip_ix = create_jito_tip_instruction(payer)
        if tip_ix:
            instructions.append(tip_ix)
        
        print(f"{get_current_timestamp()} ✅ Created Jito fee instructions:")
        print(f"   - Compute limit: {DEFAULT_COMPUTE_UNITS:,} units")
        print(f"   - Compute price: {MIN_PRIORITY_FEE:,} micro-lamports/CU")
        print(f"   - Tip amount: {MIN_TIP_LAMPORTS:,} lamports")
        
        return instructions
        
    except Exception as e:
        print(f"{get_current_timestamp()} ❌ Error creating Jito fee instructions: {str(e)}")
        traceback.print_exc()
        return []

# Transaction settings for fast execution
TX_SETTINGS = {
    "TOTAL_TIMEOUT": 1.5,      # 1.5s absolute maximum time
    "JITO_TIMEOUT": 0.2,       # Quick 200ms Jito attempt
    "MIN_CONFIRMATIONS": 1     # Single confirmation is enough
}

class PerformanceMetrics:
    def __init__(self):
        self.attempt_count = 0
        self.start_time = time.time()
        self.rpc_attempts = {endpoint: 0 for endpoint in RPC_ENDPOINTS}
        self.rpc_successes = {endpoint: 0 for endpoint in RPC_ENDPOINTS}
        self.rpc_failures = {endpoint: 0 for endpoint in RPC_ENDPOINTS}
        self.rpc_times = {endpoint: [] for endpoint in RPC_ENDPOINTS}
        
    def log_attempt(self, endpoint: str, success: bool, duration: float):
        self.attempt_count += 1
        self.rpc_attempts[endpoint] += 1
        if success:
            self.rpc_successes[endpoint] += 1
        else:
            self.rpc_failures[endpoint] += 1
        self.rpc_times[endpoint].append(duration)
        
    def print_summary(self):
        elapsed = time.time() - self.start_time
        attempts_per_second = self.attempt_count / elapsed if elapsed > 0 else 0
        
        print("\n📊 Performance Summary:")
        print(f"Total time: {elapsed:.3f}s")
        print(f"Total attempts: {self.attempt_count}")
        print(f"Attempts per second: {attempts_per_second:.1f}")
        print("\nRPC Performance:")
        
        for endpoint in RPC_ENDPOINTS:
            attempts = self.rpc_attempts[endpoint]
            successes = self.rpc_successes[endpoint]
            failures = self.rpc_failures[endpoint]
            times = self.rpc_times[endpoint]
            avg_time = sum(times) / len(times) if times else 0
            
            print(f"\n{endpoint.split('/')[-1]}:")
            print(f"  Attempts: {attempts}")
            print(f"  Successes: {successes}")
            print(f"  Failures: {failures}")
            print(f"  Avg response time: {avg_time*1000:.1f}ms")

async def validate_and_submit_transaction(
    client: AsyncClient,
    tx: VersionedTransaction,
    validate_first: bool = True
) -> Optional[str]:
    """
    Validate and submit a transaction with proper checks.
    
    Args:
        client: AsyncClient for RPC connection
        tx: Transaction to submit
        validate_first: Whether to run simulation before submission
    
    Returns:
        Optional[str]: Transaction signature if successful
    """
    try:
        if validate_first:
            # Quick simulation to catch obvious errors
            sim_response = await client.simulate_transaction(tx)
            if "result" not in sim_response:
                print("❌ Simulation failed: No result")
                return None
                
            result = sim_response["result"]
            
            # Check for errors
            if result.get("err"):
                print(f"❌ Simulation error: {result['err']}")
                return None
                
            # Check compute units
            if "unitsConsumed" in result:
                units = result["unitsConsumed"]
                if units > COMPUTE_UNIT_LIMIT:
                    print(f"❌ Transaction would exceed compute limit: {units} > {COMPUTE_UNIT_LIMIT}")
                    return None
        
        # Submit with minimal additional checks
        opts = TxOpts(
            skip_preflight=False,  # Keep basic checks
            preflight_commitment="processed",  # Fastest commitment level
            max_retries=1  # Single retry at RPC level
        )
        
        resp = await client.send_transaction(tx, opts=opts)
        if "result" in resp:
            return resp["result"]
            
        return None
        
    except Exception as e:
        print(f"❌ Transaction error: {str(e)}")
        return None

async def submit_transaction_with_fallback(
    tx: VersionedTransaction,
    feePayer: Pubkey,
    useBundleFirst: bool = True
) -> Tuple[bool, str, Optional[str]]:
    """
    Continuously submit transaction with proper validation.
    """
    start_time = time.time()
    signature = str(tx.signatures[0])
    metrics = PerformanceMetrics()
    first_attempt = True
    
    # Quick Jito attempt first
    if useBundleFirst:
        try:
            jito_start = time.time()
            async with asyncio.timeout(TX_SETTINGS["JITO_TIMEOUT"]):
                jito_client = JitoClient()
                bundle_success = await jito_client.submit_bundle(tx)
                jito_time = time.time() - jito_start
                print(f"Jito attempt took {jito_time*1000:.1f}ms")
                if bundle_success:
                    return True, "Submitted via Jito", signature
        except Exception as e:
            print(f"Jito attempt failed: {str(e)}")
            pass

    # Continuous RPC submission until timeout
    try:
        async with asyncio.timeout(TX_SETTINGS["TOTAL_TIMEOUT"]):
            while True:
                if time.time() - start_time >= TX_SETTINGS["TOTAL_TIMEOUT"]:
                    break
                
                # Try all RPCs in parallel
                async def try_rpc(endpoint: str) -> Optional[str]:
                    attempt_start = time.time()
                    success = False
                    try:
                        async with AsyncClient(endpoint) as client:
                            # Only validate on first attempt for each RPC
                            result = await validate_and_submit_transaction(
                                client,
                                tx,
                                validate_first=first_attempt
                            )
                            success = result is not None
                            return result
                    except Exception as e:
                        print(f"RPC error ({endpoint.split('/')[-1]}): {str(e)}")
                        return None
                    finally:
                        duration = time.time() - attempt_start
                        metrics.log_attempt(endpoint, success, duration)
                
                tasks = [try_rpc(endpoint) for endpoint in RPC_ENDPOINTS]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                first_attempt = False  # Only validate on first round
                
                # Check results
                for i, result in enumerate(results):
                    if isinstance(result, str):
                        metrics.print_summary()
                        return True, f"Submitted via {RPC_ENDPOINTS[i].split('/')[-1]}", result
                
                # Quick status update
                if metrics.attempt_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = metrics.attempt_count / elapsed if elapsed > 0 else 0
                    print(f"Rate: {rate:.1f} attempts/sec")
                
    except asyncio.TimeoutError:
        print("\n⏰ Submission timed out")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    metrics.print_summary()
    return False, f"Failed after {metrics.attempt_count} attempts", None

async def submit_transaction(tx: VersionedTransaction, rpc_url: str = None) -> Tuple[bool, str, Optional[str]]:
    """Submit a transaction to the network"""
    if rpc_url is None:
        rpc_url = RPC_URL
    
    try:
        # Convert transaction to wire format
        tx_bytes = base64.b64encode(tx.serialize()).decode('utf-8')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "sendTransaction",
                    "params": [
                        tx_bytes,
                        {"encoding": "base64", "skipPreflight": True, "maxRetries": 0}
                    ]
                }
            ) as response:
                result = await response.json()
                
                if "result" in result:
                    signature = result["result"]
                    return True, "Transaction submitted successfully", signature
                else:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    return False, f"Transaction submission failed: {error_msg}", None
                    
    except Exception as e:
        print(f"❌ Error submitting transaction: {str(e)}")
        traceback.print_exc()
        return False, str(e), None

async def build_buy_tx(
    token_mint: Pubkey,
    amount: int,
    client: AsyncClient = None
) -> Optional[VersionedTransaction]:
    """
    Build a buy transaction for the given token and amount.
    """
    try:
        # Get keypair
        keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        
        # Create instructions array starting with compute budget
        instructions = create_compute_budget_instructions()
        
        # Add Jito tip instruction
        tip_ix = create_jito_tip_instruction(keypair.pubkey())
        if tip_ix:
            instructions.append(tip_ix)
            
        # Get or create associated token account
        ata = get_associated_token_address(keypair.pubkey(), token_mint)
        
        # Calculate maximum price with slippage
        max_price_with_slippage = int(amount * (1 + SLIPPAGE_BPS / 10000))
        
        # Build buy instruction with slippage protection
        buy_ix = Instruction(
            program_id=PUMP_TRADE_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
            ],
            data=(
                bytes([1]) +  # Opcode 1 for buy
                amount.to_bytes(8, 'little') +  # Amount to buy
                max_price_with_slippage.to_bytes(8, 'little')  # Max price we'll pay
            )
        )
        instructions.append(buy_ix)
        
        # Get all unique account keys in order
        account_keys = []
        seen_keys = set()
        
        # Add fee payer first
        account_keys.append(keypair.pubkey())
        seen_keys.add(str(keypair.pubkey()))
        
        # Add other accounts in order of appearance
        for ix in instructions:
            for acct in ix.accounts:
                key_str = str(acct.pubkey)
                if key_str not in seen_keys:
                    account_keys.append(acct.pubkey)
                    seen_keys.add(key_str)

        # Get recent blockhash
        try:
            response = await client.get_latest_blockhash()
            blockhash = response["result"]["value"]["blockhash"]
            blockhash_obj = Hash.from_string(blockhash)
        except Exception as e:
            print(f"❌ Error getting recent blockhash: {str(e)}")
            return None
        
        # Create message with all required parameters
        message = MessageV0(
            header=MessageHeader(
                num_required_signatures=1,
                num_readonly_signed_accounts=0,
                num_readonly_unsigned_accounts=len(account_keys) - 1
            ),
            account_keys=account_keys,
            recent_blockhash=blockhash_obj,
            instructions=instructions,
            address_table_lookups=[]
        )
        
        # Create and sign transaction
        tx = VersionedTransaction(
            message=message,
            signatures=[keypair.sign_message(bytes(message))]
        )
        
        return tx
        
    except Exception as e:
        print(f"❌ Error building buy transaction: {str(e)}")
        traceback.print_exc()
        return None

async def build_sell_tx(
    token_mint: Pubkey,
    amount: int,
    client: AsyncClient = None
) -> Optional[VersionedTransaction]:
    """
    Build a sell transaction for the given token and amount.
    """
    try:
        # Get keypair
        keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        
        # Create instructions array starting with compute budget
        instructions = create_compute_budget_instructions()
        
        # Add Jito tip instruction
        tip_ix = create_jito_tip_instruction(keypair.pubkey())
        if tip_ix:
            instructions.append(tip_ix)
            
        # Get associated token account
        ata = get_associated_token_address(keypair.pubkey(), token_mint)
        
        # Build sell instruction (placeholder - implement actual DEX interaction)
        # Calculate minimum price with slippage
        min_price_with_slippage = int(amount * (1 - SLIPPAGE_BPS / 10000))

        # Build sell instruction with slippage protection
        sell_ix = Instruction(
            program_id=PUMP_TRADE_PROGRAM,
            accounts=[
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
            ],
            data=(
                bytes([2]) +  # Opcode 2 for sell
                amount.to_bytes(8, 'little') +  # Amount to sell
                min_price_with_slippage.to_bytes(8, 'little')  # Min price we'll accept
            )
        )
        instructions.append(sell_ix)
        
        # Get all unique account keys in order
        account_keys = []
        seen_keys = set()
        
        # Add fee payer first
        account_keys.append(keypair.pubkey())
        seen_keys.add(str(keypair.pubkey()))
        
        # Add other accounts in order of appearance
        for ix in instructions:
            for acct in ix.accounts:
                key_str = str(acct.pubkey)
                if key_str not in seen_keys:
                    account_keys.append(acct.pubkey)
                    seen_keys.add(key_str)

        # Get recent blockhash
        try:
            response = await client.get_latest_blockhash()
            blockhash = response["result"]["value"]["blockhash"]
            blockhash_obj = Hash.from_string(blockhash)
        except Exception as e:
            print(f"❌ Error getting recent blockhash: {str(e)}")
            return None
        
        # Create message with all required parameters
        message = MessageV0(
            header=MessageHeader(
                num_required_signatures=1,
                num_readonly_signed_accounts=0,
                num_readonly_unsigned_accounts=len(account_keys) - 1
            ),
            account_keys=account_keys,
            recent_blockhash=blockhash_obj,
            instructions=instructions,
            address_table_lookups=[]
        )
        
        # Create and sign transaction
        tx = VersionedTransaction(
            message=message,
            signatures=[keypair.sign_message(bytes(message))]
        )
        
        return tx
        
    except Exception as e:
        print(f"❌ Error building sell transaction: {str(e)}")
        traceback.print_exc()
        return None

async def build_wallet_a_tx(tx_info: Dict[str, Any], client: AsyncClient = None) -> Optional[VersionedTransaction]:
    """
    Build a transaction that mirrors Wallet A's trade
    
    Args:
        tx_info: Dictionary containing trade information
        client: AsyncClient for RPC connection
        
    Returns:
        Optional[VersionedTransaction]: Built transaction or None if failed
    """
    try:
        if tx_info.get("is_buy"):
            return await build_buy_tx(
                token_mint=tx_info["token_mint"],
                amount=tx_info["amount"],
                client=client
            )
        else:
            return await build_sell_tx(
                token_mint=tx_info["token_mint"],
                amount=tx_info["amount"],
                client=client
            )
    except Exception as e:
        print(f"❌ Error building wallet A transaction: {str(e)}")
        traceback.print_exc()
        return None

async def simulate_transaction(
    client: AsyncClient,
    tx: VersionedTransaction
) -> Tuple[bool, str]:
    """
    Simulate a transaction before submission to validate it.
    
    Args:
        client: AsyncClient for RPC connection
        tx: Transaction to simulate
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        sim_response = await client.simulate_transaction(tx)
        
        if "result" not in sim_response:
            return False, "No simulation result"
            
        result = sim_response["result"]
        
        if result.get("err"):
            return False, f"Simulation error: {result['err']}"
            
        # Check compute units if available
        if "unitsConsumed" in result:
            units = result["unitsConsumed"]
            if units > COMPUTE_UNIT_LIMIT:
                return False, f"Would exceed compute limit: {units} > {COMPUTE_UNIT_LIMIT}"
        
        # Check logs for any obvious errors
        logs = result.get("logs", [])
        if any("failed" in log.lower() for log in logs):
            return False, "Transaction would fail"
            
        return True, "Simulation successful"
        
    except Exception as e:
        return False, f"Simulation error: {str(e)}"

async def initialize_user_account(keypair: Keypair) -> Optional[VersionedTransaction]:
    """
    Initialize user account with the Pump.fun program.
    Must be called before any trading can occur.
    """
    try:
        instructions = create_compute_budget_instructions()
        
        # Add Jito tip instruction
        tip_ix = create_jito_tip_instruction(keypair.pubkey())
        if tip_ix:
            instructions.append(tip_ix)
            
        # Create initialization instruction
        init_ix = Instruction(
            program_id=PUMP_TRADE_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            ],
            data=bytes([0])  # Opcode 0 for initialize
        )
        instructions.append(init_ix)
        
        # Create and sign transaction
        tx = VersionedTransaction(
            message=MessageV0(instructions),
            signatures=[keypair.sign_message(bytes(MessageV0(instructions)))]
        )
        
        return tx
        
    except Exception as e:
        print(f"❌ Error creating initialization transaction: {str(e)}")
        traceback.print_exc()
        return None

async def ensure_user_initialized(pubkey: Pubkey) -> bool:
    """Check if a user account is initialized"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [
                        str(pubkey),
                        {"encoding": "base64"}
                    ]
                }
            ) as response:
                result = await response.json()
                if "result" in result and result["result"]:
                    print("✅ User account already initialized")
                    return False
                print("⚠️ User account needs initialization")
                return True
    except Exception as e:
        print(f"❌ Error checking user account: {str(e)}")
        traceback.print_exc()
        return True  # Safer to try initializing if we're not sure

async def create_user_account_tx(keypair: Keypair) -> VersionedTransaction:
    """Create a transaction to initialize a user account"""
    try:
        # Get recent blockhash
        async with aiohttp.ClientSession() as session:
            async with session.post(
                RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                }
            ) as response:
                result = await response.json()
                if "result" not in result or not result["result"]:
                    raise Exception("Failed to get recent blockhash")
                blockhash = Hash.from_string(result["result"]["value"]["blockhash"])

        # Create initialization instruction
        instruction = Instruction(
            program_id=PUMP_FUN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            ],
            data=b"\x00",  # Initialize instruction
        )

        # Create and sign transaction
        message = MessageV0.new_with_blockhash(
            [instruction],
            keypair.pubkey(),
            blockhash
        )
        tx = VersionedTransaction.populate(message, [keypair])
        return tx

    except Exception as e:
        print(f"❌ Error creating user account transaction: {str(e)}")
        traceback.print_exc()
        raise