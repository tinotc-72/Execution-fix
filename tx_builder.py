# tx_builder.py

from solders.instruction import AccountMeta, Instruction  
from solana.rpc.async_api import AsyncClient  # At top with other imports
import base64
import base58
import asyncio
from models import Bundle
from random import choice
import json
import time

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
import keyZ as kz
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
    VALID_JITO_TIP_ACCOUNTS
)

# SPL Token imports
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    mint_to,
    burn,
    close_account
)

# ✅ OFFICIAL JITO CONSTANTS - Verified with Jito Documentation
JITO_TIP_PROGRAM_ID = Pubkey.from_string("J1TnP8zvVxbtG4yxtt9qVaZK5nhG9SEqhYEJoQhJ5Pyr")  # Official Jito Tip Program
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
MIN_TIP_LAMPORTS = 10_000  # Minimum 0.00001 SOL for auction eligibility
MIN_PRIORITY_FEE = 1_000   # Minimum 1000 micro-lamports/CU
DEFAULT_COMPUTE_UNITS = 200_000
COMPUTE_UNIT_LIMIT = 400_000  # Optimized for meme coin trades
COMPUTE_UNIT_PRICE = 20_000   # Higher priority for MEV protection
JITO_TIP_AMOUNT = 10_000      # Standard tip amount for bundle inclusion

DEBUG = True

# Program IDs
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

# ✅ OFFICIAL JITO TIP ACCOUNTS - From Jito Documentation
VALID_JITO_TIP_ACCOUNTS = [
    Pubkey.from_string("96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5"),  # Tip Account 1
    Pubkey.from_string("HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe"),  # Tip Account 2  
    Pubkey.from_string("Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY"),  # Tip Account 3
    Pubkey.from_string("ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49"),  # Tip Account 4
    Pubkey.from_string("DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh"),  # Tip Account 5
    Pubkey.from_string("ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt"),  # Tip Account 6
    Pubkey.from_string("DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL"),  # Tip Account 7
    Pubkey.from_string("3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT")   # Tip Account 8
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
        
def create_compute_budget_instructions(
    compute_units: int = None, 
    priority_fee_microlamports: int = None
) -> List[Instruction]:
    """
    ✅ OFFICIAL COMPUTE BUDGET INSTRUCTIONS - Following Solana Documentation
    Creates compute budget instructions that MUST come before the tip instruction
    
    Args:
        compute_units: Compute unit limit (default: 400,000 for meme coins)
        priority_fee_microlamports: Priority fee in micro-lamports per CU (default: 20,000)
        
    Returns:
        List[Instruction]: Two compute budget instructions [limit, price]
    """
    try:
        if compute_units is None:
            compute_units = COMPUTE_UNIT_LIMIT
        if priority_fee_microlamports is None:
            priority_fee_microlamports = COMPUTE_UNIT_PRICE
            
        print(f"\n🔧 CREATING COMPUTE BUDGET INSTRUCTIONS")
        print(f"   ⚡ Compute Units: {compute_units:,}")
        print(f"   💰 Priority Fee: {priority_fee_microlamports:,} micro-lamports/CU")
        
        # ✅ OFFICIAL: SetComputeUnitLimit instruction (opcode 0x02)
        # Data: [0x02, limit_u32_le]
        unit_limit_instruction = Instruction(
            program_id=COMPUTE_BUDGET_PROGRAM_ID,
            accounts=[],  # No accounts needed for compute budget
            data=bytes([0x02]) + compute_units.to_bytes(4, "little")
        )

        # ✅ OFFICIAL: SetComputeUnitPrice instruction (opcode 0x03)  
        # Data: [0x03, price_u64_le]
        unit_price_instruction = Instruction(
            program_id=COMPUTE_BUDGET_PROGRAM_ID,
            accounts=[],  # No accounts needed for compute budget
            data=bytes([0x03]) + priority_fee_microlamports.to_bytes(8, "little")
        )

        print(f"✅ COMPUTE BUDGET INSTRUCTIONS CREATED")
        print(f"   1️⃣ SetComputeUnitLimit: {compute_units:,} units")
        print(f"   2️⃣ SetComputeUnitPrice: {priority_fee_microlamports:,} μ-lamports/CU")
        
        return [unit_limit_instruction, unit_price_instruction]

    except Exception as e:
        print(f"❌ FAILED TO CREATE COMPUTE BUDGET INSTRUCTIONS: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_jito_tip_instruction(payer: Pubkey, tip_lamports: int = None) -> Optional[Instruction]:
    """
    ✅ OFFICIAL JITO TIP INSTRUCTION - Following Jito Documentation
    Creates a tip instruction that makes the bundle eligible for auction
    
    Args:
        payer: The wallet paying the tip (must be signer and writable)
        tip_lamports: Tip amount in lamports (default: 10,000 = 0.00001 SOL)
        
    Returns:
        Instruction: Valid Jito tip instruction or None if creation fails
    """
    try:
        if tip_lamports is None:
            tip_lamports = JITO_TIP_AMOUNT
            
        print(f"\n🎯 CREATING JITO TIP INSTRUCTION")
        print(f"   💰 Tip Amount: {tip_lamports:,} lamports ({tip_lamports / 1e9:.6f} SOL)")
        print(f"   👤 Payer: {payer}")

        # ✅ CRITICAL: Select random tip account to distribute load
        tip_account_str = choice(VALID_JITO_TIP_ACCOUNTS)
        tip_account = Pubkey.from_string(tip_account_str) if isinstance(tip_account_str, str) else tip_account_str
        print(f"   🎯 Selected Tip Account: {tip_account}")
        
        # ✅ OFFICIAL: Use System Program for SOL transfer (NOT Jito Tip Program)
        # The "Jito Tip Program" is just for identification, actual transfer uses System Program
        SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
        
        # ✅ CRITICAL: Create proper account metadata
        accounts = [
            AccountMeta(
                pubkey=payer,
                is_signer=True,   # ✅ MUST be signer (pays the tip)
                is_writable=True  # ✅ MUST be writable (SOL balance decreases)
            ),
            AccountMeta(
                pubkey=tip_account,
                is_signer=False,  # ✅ Tip account is not a signer
                is_writable=True  # ✅ MUST be writable (receives SOL)
            )
        ]
        
        # ✅ OFFICIAL: Create SOL transfer instruction data
        # System Program transfer instruction: [2, ...8_bytes_lamports]
        instruction_data = bytes([2]) + tip_lamports.to_bytes(8, "little")
        
        # ✅ Create the tip instruction
        tip_instruction = Instruction(
            program_id=SYSTEM_PROGRAM_ID,  # ✅ Use System Program for SOL transfer
            accounts=accounts,
            data=instruction_data
        )
        
        # ✅ VALIDATION: Verify instruction is properly formed
        print(f"\n🔍 TIP INSTRUCTION VALIDATION")
        print(f"   🎯 Program ID: {tip_instruction.program_id}")
        print(f"   📊 Accounts: {len(tip_instruction.accounts)}")
        print(f"   📦 Data Length: {len(tip_instruction.data)} bytes")
        print(f"   💰 Decoded Amount: {int.from_bytes(tip_instruction.data[1:9], 'little'):,} lamports")
        
        # ✅ CRITICAL CHECKS for Jito eligibility
        if len(tip_instruction.accounts) != 2:
            print(f"❌ INVALID: Expected 2 accounts, got {len(tip_instruction.accounts)}")
            return None
            
        if not tip_instruction.accounts[1].is_writable:
            print(f"❌ INVALID: Tip account must be writable for auction eligibility")
            return None
            
        if tip_lamports < MIN_TIP_LAMPORTS:
            print(f"❌ INVALID: Tip amount {tip_lamports} < minimum {MIN_TIP_LAMPORTS}")
            return None
            
        print(f"✅ TIP INSTRUCTION CREATED - Bundle is eligible for Jito auction!")
        return tip_instruction
        
    except Exception as e:
        print(f"❌ FAILED TO CREATE TIP INSTRUCTION: {e}")
        import traceback
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

        sig = keypair.sign_message(tx.message.to_bytes())
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
        jito_result = submit_to_jito_api(bundle, jito_api_url)
        
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

__all__ = [
    'create_compute_budget_instructions',
    'create_jito_tip_instruction',
    'create_and_sign_transaction',
    'get_jito_fee_instructions',
    'process_transaction'
]

async def submit_to_jito_block_engine(bundle: dict, auth_token: str) -> bool:
    """Submit bundle to Jito Block Engine via HTTP"""
    try:
        print(f"{get_current_timestamp()} 🚀 Submitting to Jito Block Engine...")

        # Define all available mainnet endpoints
        endpoints = [
            "https://london.mainnet.block-engine.jito.wtf",      # 🇬🇧 London
            "https://amsterdam.mainnet.block-engine.jito.wtf",   # 🇳🇱 Amsterdam
            "https://frankfurt.mainnet.block-engine.jito.wtf",   # 🇩🇪 Frankfurt
            "https://ny.mainnet.block-engine.jito.wtf",          # 🇺🇸 New York
            "https://tokyo.mainnet.block-engine.jito.wtf",       # 🇯🇵 Tokyo
            "https://slc.mainnet.block-engine.jito.wtf",         # 🇺🇸 Salt Lake City
            "https://mainnet.block-engine.jito.wtf"              # Global
        ]

        # Add /api/v1/bundles to each endpoint
        endpoints = [f"{endpoint}/api/v1/bundles" for endpoint in endpoints]

        # Create headers
        headers = {
            "x-jito-auth": auth_token,
            "Content-Type": "application/json"
        }

        # Validate presence of transactions
        try:
            transactions = bundle["params"][0]["transactions"]
        except (KeyError, IndexError, TypeError):
            print(f"{get_current_timestamp()} ❌ Could not extract transactions from bundle structure.")
            return False

        # Construct the correct JSON-RPC payload
        rpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendBundle",
            "params": {
                "bundle": {
                    "transactions": transactions,
                    "blockhash": bundle.get("blockhash", ""),
                    "timestamp": int(time.time())
                }
            }
        }

        # Try all endpoints concurrently
        async def try_endpoint(session: aiohttp.ClientSession, url: str) -> tuple[bool, int, dict]:
            try:
                async with session.post(
                    url,
                    headers=headers,
                    json=rpc_request,
                    timeout=aiohttp.ClientTimeout(total=2)  # Short timeout for speed
                ) as response:
                    response_data = await response.json()
                    return response.status == 200, response.status, response_data
            except Exception as e:
                return False, 0, {"error": str(e)}

        async with aiohttp.ClientSession() as session:
            # Submit to all endpoints concurrently
            tasks = [try_endpoint(session, url) for url in endpoints]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Track responses
            successful_endpoints = []
            rate_limited_endpoints = []
            failed_endpoints = []

            # Process results
            for i, result in enumerate(results):
                if isinstance(result, tuple):
                    success, status, response_data = result
                    endpoint_name = endpoints[i].split("//")[1].split(".")[0]  # Extract location name

                    if success:
                        successful_endpoints.append(endpoint_name)
                    elif status == 429:
                        rate_limited_endpoints.append(endpoint_name)
                    else:
                        failed_endpoints.append((endpoint_name, status, response_data.get('error', 'Unknown error')))

            # Log results
            if successful_endpoints:
                print(f"{get_current_timestamp()} ✅ Bundle submitted successfully via: {', '.join(successful_endpoints)}")
                return True

            if rate_limited_endpoints:
                print(f"{get_current_timestamp()} ⚠️ Rate limited on: {', '.join(rate_limited_endpoints)}")

            if failed_endpoints:
                print(f"{get_current_timestamp()} ❌ Failed submissions:")
                for name, status, error in failed_endpoints:
                    print(f"  - {name}: Status {status}, Error: {error}")

            return False

    except Exception as e:
        print(f"{get_current_timestamp()} ❌ Bundle submission error: {str(e)}")
        traceback.print_exc()
        return False

class Bot:
    def __init__(self, keypair: Keypair, client: AsyncClient):
        """
        Initialize the trading bot.
        
        Args:
            keypair: Solana keypair for transaction signing
            client: AsyncClient for RPC communication
        """
        self.keypair = keypair
        self.client = client
        self.start_time = datetime.strptime("2025-06-05 11:29:48", "%Y-%m-%d %H:%M:%S")
        self.current_user = "tinotc-72"
        
        # Initialize performance metrics
        self.total_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        self.last_transaction_time = None
        
        print(f"🤖 Bot initialized for user: {self.current_user}")
        print(f"📅 Start time (UTC): {self.start_time}")
        print(f"🔑 Using public key: {self.keypair.pubkey()}")

    async def copy_trade(self, txSigned: str, epochInfo: dict, senderAddress: str) -> Optional[str]:
        try:
            timestamp = datetime.now(UTC).strftime("[%Y-%m-%d %H:%M:%S]")
            print(f"\n{timestamp} 🔄 Processing transaction from {senderAddress[:8]}...")
            
            # Decode transaction
            decoded_tx = VersionedTransaction.from_bytes(base64.b64decode(txSigned))
            
            # Get relevant transaction info
            recent_blockhash = decoded_tx.message.recent_blockhash
            instructions = decoded_tx.message.instructions
            
            # Create our instructions with Jito requirements
            all_instructions = []
            
            # 1. Add compute budget instructions FIRST
            compute_budget_ixs = create_compute_budget_instructions()
            if not compute_budget_ixs:
                print(f"{timestamp} ❌ Failed to create compute budget instructions")
                return None
            all_instructions.extend(compute_budget_ixs)
            
            # 2. Add Jito tip instruction SECOND
            tip_ix = create_jito_tip_instruction(self.keypair.pubkey())
            if not tip_ix:
                print(f"{timestamp} ❌ Failed to create tip instruction")
                return None
            all_instructions.append(tip_ix)
                
            # 3. Add original instructions LAST
            all_instructions.extend(instructions)
            
            print(f"{timestamp} 📝 Creating transaction with {len(all_instructions)} instructions")

            # Process transaction with fallback
            success = await process_transaction(
                keypair=self.keypair,
                instructions=all_instructions,
                recent_blockhash=str(recent_blockhash),
                client=self.client
            )
            
            if success:
                self.total_transactions += 1
                self.successful_transactions += 1
                self.last_transaction_time = datetime.now(UTC)
                return "Transaction processed successfully"
            else:
                self.failed_transactions += 1
                return None

        except Exception as e:
            self.failed_transactions += 1
            print(f"{timestamp} ❌ Error in copy_trade: {str(e)}")
            traceback.print_exc()
            return None

    async def validate_transaction(self, txSigned: str, senderAddress: str) -> bool:
        """
        Validate transaction before processing.
        
        Args:
            txSigned: Base64 encoded transaction
            senderAddress: Address of the transaction sender
            
        Returns:
            bool: True if transaction is valid, False otherwise
        """
        try:
            # Decode transaction first
            decoded_tx = VersionedTransaction.from_bytes(base64.b64decode(txSigned))
            
            # Basic validation checks
            if not decoded_tx or not decoded_tx.message or not decoded_tx.signatures:
                print("❌ Invalid transaction structure")
                return False
                
            # Validate sender address
            if not senderAddress or len(senderAddress) != 44:  # Base58 Solana address length
                print("❌ Invalid sender address")
                return False
                
            # Check if transaction is too old
            current_time = datetime.now(UTC)
            if self.last_transaction_time:
                time_diff = (current_time - self.last_transaction_time).total_seconds()
                if time_diff < 0.1:  # Minimum time between transactions
                    print("⚠️ Transaction too soon after previous")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {str(e)}")
            return False

async def process_transaction(
    keypair: Keypair,
    instructions: List[Instruction],
    recent_blockhash: str,
    client: AsyncClient
) -> bool:
    try:
        timestamp = datetime.now(UTC).strftime("[%Y-%m-%d %H:%M:%S]")
        print(f"\n{timestamp} 🔄 Processing transaction...")

        # Create and sign transaction
        msg = MessageV0.try_compile(
            payer=keypair.pubkey(),
            instructions=instructions,
            recent_blockhash=Hash.from_string(recent_blockhash),
            address_lookup_table_accounts=[]
        )
        
        tx = VersionedTransaction.populate(
            message=msg,
            signatures=[Signature.default()]
        )
        
        signature = keypair.sign_message(tx.message.to_bytes())
        tx.signatures = [signature]

        # 1. Try Jito first
        print(f"{timestamp} 🚀 Attempting Jito bundle submission...")
        bundle = create_jito_bundle(tx)
        if bundle:
            try:
                jito_success = await submit_to_jito_block_engine(
                    bundle=bundle,
                    auth_token=kz.JITO_AUTH_TOKEN
                )
                if jito_success:
                    print(f"{timestamp} ✅ Transaction processed via Jito")
                    return True
            except Exception as e:
                print(f"{timestamp} ⚠️ Jito submission failed: {str(e)}")

        # 2. RPC Fallback
        print(f"{timestamp} 🔄 Falling back to RPC submission...")
        try:
            result = await client.send_transaction(
                tx,
                opts=TxOpts(
                    skip_preflight=True,
                    preflight_commitment=Processed,
                    max_retries=3
                )
            )
            
            if result.value:
                print(f"{timestamp} ✅ Transaction processed via RPC fallback")
                print(f"📝 Signature: {result.value}")
                return True
            else:
                print(f"{timestamp} ❌ RPC submission failed")
                return False

        except Exception as e:
            print(f"{timestamp} ❌ RPC fallback failed: {str(e)}")
            return False

    except Exception as e:
        print(f"{timestamp} ❌ Transaction processing failed: {str(e)}")
        traceback.print_exc()
        return False
                                                                                             
def validate_transaction(tx: VersionedTransaction, payer: Pubkey) -> bool:
    """Validate transaction structure and contents"""
    try:
        if not tx or not tx.message:
            print("❌ Invalid transaction object")
            return False
            
        if not tx.signatures or len(tx.signatures) == 0:
            print("❌ Transaction not signed")
            return False
            
        if len(tx.message.static_account_keys) == 0:
            print("❌ No account keys")
            return False
            
        if tx.message.static_account_keys[0] != payer:
            print("❌ First account is not payer")
            return False
            
        if len(tx.message.instructions) < 4:  # At least our 3 fee instructions + 1
            print("❌ Not enough instructions")
            return False
            
        # Validate first instruction is Jito tip
        tip_ix = tx.message.instructions[0]
        if (tip_ix.program_id != SYS_PROGRAM_ID or
            len(tip_ix.accounts) != 2 or
            tip_ix.accounts[1].pubkey not in VALID_JITO_TIP_ACCOUNTS):
            print("❌ Invalid Jito tip instruction")
            return False
            
        print("✅ Transaction validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False
             
def prepare_transaction_for_jito(transaction: VersionedTransaction) -> dict:
    """Prepare transaction for Jito bundle submission"""
    try:
        if not isinstance(transaction, VersionedTransaction):
            raise ValueError("Expected VersionedTransaction")

        # First sign the transaction if not signed
        if not transaction.signatures or all(sig == [0]*64 for sig in transaction.signatures):
            print("⚠️ Transaction not signed, signing required")
            return None

        # Serialize the transaction using modern method
        tx_bytes = bytes(transaction)
        serialized_tx = base64.b64encode(tx_bytes).decode('utf-8')
        
        # Create bundle request
        bundle_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendBundle",
            "params": [{
                "transactions": [serialized_tx],
                "header": {
                    "tip_percentage": 90
                }
            }]
        }
        
        return bundle_request

    except Exception as e:
        print(f"❌ Error preparing Jito bundle: {str(e)}")
        traceback.print_exc()
        return None
      
# === Utility Functions ===

# === Instruction Builders ===
def set_compute_unit_limit(units: int) -> Instruction:
    return Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([0x02]) + units.to_bytes(4, "little")  # Changed from 0x00 to 0x02
    )

def set_compute_unit_price(microlamports: int) -> Instruction:
    return Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([0x03]) + microlamports.to_bytes(4, "little")  # Using correct opcode 0x03
    )

# === Transaction Builders ===

async def build_buy_tx(mint_str: str, amount: int, curve_str: str, wallet: Keypair) -> VersionedTransaction:
    wallet_pubkey = wallet.pubkey()
    mint = Pubkey.from_string(mint_str)
    curve = Pubkey.from_string(curve_str)
    client = AsyncClient(RPC_URL)

    # PDAs
    global_pda, _ = Pubkey.find_program_address([b"global"], PUMP_FUN_PROGRAM_ID)
    fee_recipient, _ = Pubkey.find_program_address([b"fee-recipient", bytes(curve)], PUMP_FUN_PROGRAM_ID)
    assoc_curve, _ = Pubkey.find_program_address([b"associated-bonding-curve", bytes(curve)], PUMP_FUN_PROGRAM_ID)
    event_authority, _ = Pubkey.find_program_address([b"event-authority"], PUMP_FUN_PROGRAM_ID)
    assoc_user, _ = Pubkey.find_program_address([b"associated-user", bytes(wallet_pubkey), bytes(curve)], PUMP_FUN_PROGRAM_ID)
    user_ata = get_associated_token_address(wallet_pubkey, mint)

    # Check and create ATAs if needed
    ixs = []
    ata_info = await client.get_account_info(user_ata)
    if ata_info.value is None:
        create_ata_ix = create_associated_token_account(wallet_pubkey, wallet_pubkey, mint)
        ixs.append(create_ata_ix)

    # Check and initialize associated user account if needed
    assoc_user_info = await client.get_account_info(assoc_user)
    if assoc_user_info.value is None:
        init_user_ix = Instruction(
            program_id=PUMP_FUN_PROGRAM_ID,
            accounts=[
                AccountMeta(assoc_user, False, True),
                AccountMeta(wallet_pubkey, True, True),
                AccountMeta(curve, False, False),
                AccountMeta(SYS_PROGRAM_ID, False, False)
            ],
            data=bytes([0])  # Init instruction
        )
        ixs.append(init_user_ix)

    buy_ix = Instruction(
        program_id=PUMP_FUN_PROGRAM_ID,
        accounts=[
            AccountMeta(global_pda, False, True),
            AccountMeta(fee_recipient, False, True),
            AccountMeta(mint, False, True),
            AccountMeta(curve, False, True),
            AccountMeta(assoc_curve, False, True),
            AccountMeta(assoc_user, False, True),
            AccountMeta(wallet_pubkey, True, True),
            AccountMeta(SYS_PROGRAM_ID, False, False),
            AccountMeta(TOKEN_PROGRAM_ID, False, False),
            AccountMeta(RENT_PROGRAM_ID, False, False),
            AccountMeta(event_authority, False, False),
            AccountMeta(PUMP_FUN_PROGRAM_ID, False, False),
        ],
        data=amount.to_bytes(8, "little") + int(amount * 1.30).to_bytes(8, "little")  # 30% slippage
    )

    # Add Compute + Tip instructions at the start
    jito_ixs = get_jito_fee_instructions(wallet_pubkey, total_lamports=5_000)
    ixs = jito_ixs + ixs + [buy_ix]

    # Debug tip instruction
    tip_ix = ixs[0]
    tip_target = tip_ix.accounts[1]
    print("🧪 Tip Target Pubkey:", str(tip_target.pubkey))
    print("🧪 Tip Target Writable:", tip_target.is_writable)
    print("🧪 Tip Amount:", int.from_bytes(tip_ix.data[1:], "little"))

    print("✅ Final instruction list:")
    for i, ix in enumerate(ixs):
        print(f"  - ixs[{i}]:", ix)
    
    # Validate tip instruction
    tip_ix = ixs[0]
    assert tip_ix.program_id == SYS_PROGRAM_ID, "🚨 Tip instruction is not SystemProgram"
    assert int.from_bytes(tip_ix.data[1:], "little") >= 1000, "🚨 Tip amount < 1000"

    blockhash_obj: Hash = (await client.get_latest_blockhash()).value.blockhash
    msg = MessageV0.try_compile(
        payer=wallet_pubkey,
        instructions=ixs,
        recent_blockhash=blockhash_obj,
        address_lookup_table_accounts=[]
    )

    await client.close()
    return VersionedTransaction(msg, [wallet])

async def build_sell_tx(mint_str: str, amount: int, curve_str: str, wallet: Keypair) -> VersionedTransaction:
    wallet_pubkey = wallet.pubkey()
    mint = Pubkey.from_string(mint_str)
    curve = Pubkey.from_string(curve_str)
    client = AsyncClient(RPC_URL)

    # Get PDAs and accounts
    global_pda, _ = Pubkey.find_program_address([b"global"], PUMP_FUN_PROGRAM_ID)
    fee_recipient, _ = Pubkey.find_program_address([b"fee-recipient", bytes(curve)], PUMP_FUN_PROGRAM_ID)
    assoc_curve, _ = Pubkey.find_program_address([b"associated-bonding-curve", bytes(curve)], PUMP_FUN_PROGRAM_ID)
    event_authority, _ = Pubkey.find_program_address([b"event-authority"], PUMP_FUN_PROGRAM_ID)
    assoc_user, _ = Pubkey.find_program_address([b"associated-user", bytes(wallet_pubkey), bytes(curve)], PUMP_FUN_PROGRAM_ID)
    base_ata = get_associated_token_address(wallet_pubkey, mint)

    # Initialize instructions array
    ixs = []

    # 1. Check and initialize associated user account if needed
    assoc_user_info = await client.get_account_info(assoc_user)
    if assoc_user_info.value is None:
        print("⚠️ Initializing associated user account...")
        init_user_ix = Instruction(
            program_id=PUMP_FUN_PROGRAM_ID,
            accounts=[
                AccountMeta(assoc_user, False, True),
                AccountMeta(wallet_pubkey, True, True),
                AccountMeta(curve, False, False),
                AccountMeta(SYS_PROGRAM_ID, False, False)
            ],
            data=bytes([0])  # Init instruction
        )
        ixs.append(init_user_ix)
        print("✅ Added initialization instruction")

    # 2. Create the sell instruction with base_ata
    print("📝 Creating sell instruction...")
    sell_ix = Instruction(
        program_id=PUMP_FUN_PROGRAM_ID,
        accounts=[
            AccountMeta(global_pda, False, True),
            AccountMeta(fee_recipient, False, True),
            AccountMeta(mint, False, True),
            AccountMeta(curve, False, True),
            AccountMeta(assoc_curve, False, True),
            AccountMeta(assoc_user, False, True),  # Now initialized
            AccountMeta(wallet_pubkey, True, True),
            AccountMeta(base_ata, False, True),    # Added token account
            AccountMeta(SYS_PROGRAM_ID, False, False),
            AccountMeta(TOKEN_PROGRAM_ID, False, False),
            AccountMeta(RENT_PROGRAM_ID, False, False),
            AccountMeta(event_authority, False, False)
        ],
        data=amount.to_bytes(8, "little") + int(amount * 0.70).to_bytes(8, "little")  # 30% slippage
    )

    # 3. Add compute budget and Jito tip instructions
    jito_ixs = get_jito_fee_instructions(wallet_pubkey, total_lamports=5_000)
    ixs = jito_ixs + ixs + [sell_ix]

    # 4. Create and sign transaction
    blockhash = (await client.get_latest_blockhash()).value.blockhash
    msg = MessageV0.try_compile(
        payer=wallet_pubkey,
        instructions=ixs,
        recent_blockhash=blockhash,
        address_lookup_table_accounts=[]
    )

    await client.close()
    return VersionedTransaction(msg, [wallet])

def get_transaction_type(tx: VersionedTransaction) -> str:
    """Determine transaction type from instructions"""
    try:
        for ix in tx.message.instructions:
            # Check for Pump trades
            if ix.program_id == PUMP_FUN_PROGRAM_ID:
                if ix.data[0] == 0:
                    return "PumpBuy"
                elif ix.data[0] == 1:
                    return "PumpSell"
                    
            # Add other DEX checks here
                    
        return "Unknown"
        
    except Exception as e:
        print(f"❌ Error getting transaction type: {str(e)}")
        return "Error"

def clone_instruction_data(original_data: bytes, tx_type: str) -> bytes:
    """Clone instruction data with proper modifications"""
    try:
        if tx_type == "PumpBuy":
            amount = int.from_bytes(original_data[:8], "little")
            # Increase slippage for buys to 30%
            min_out = int(amount * 0.70)  # 30% slippage (allowing price to be up to 30% higher)
            return amount.to_bytes(8, "little") + min_out.to_bytes(8, "little")
        elif tx_type == "PumpSell":
            amount = int.from_bytes(original_data[:8], "little")
            # Increase slippage for sells to 30%
            min_out = int(amount * 0.70)  # 30% slippage (allowing price to be up to 30% lower)
            return amount.to_bytes(8, "little") + min_out.to_bytes(8, "little")
            
        return original_data
        
    except Exception as e:
        print(f"❌ Error cloning instruction data: {str(e)}")
        return original_data
         
# === Additional Transaction Builders ===

async def build_wallet_a_tx(mint_str: str, amount: int, curve_str: str, wallet: Keypair) -> VersionedTransaction:
    wallet_pubkey = wallet.pubkey()
    mint = Pubkey.from_string(mint_str)
    VAULT_PROGRAM_ID = Pubkey.from_string("24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi")
    TOKEN_MINT = Pubkey.default()

    client = AsyncClient(RPC_URL)

    # Get token accounts
    input_ata = get_associated_token_address(wallet_pubkey, mint)
    output_ata = get_associated_token_address(wallet_pubkey, TOKEN_MINT)

    # Check if output ATA needs to be created
    ata_info = await client.get_account_info(output_ata)
    create_output_ata_ix = None
    if ata_info.value is None:
        create_output_ata_ix = create_associated_token_account(wallet_pubkey, wallet_pubkey, TOKEN_MINT)

    # Create instructions
    deposit_ix = Instruction(
        program_id=VAULT_PROGRAM_ID,
        accounts=[
            AccountMeta(input_ata, False, True),
            AccountMeta(output_ata, False, True),
            AccountMeta(wallet_pubkey, True, True)
        ],
        data=base64.b64decode("PgQWtn8ozix97ThBEhs9eqi6GHYtmS9xb")
    )

    withdraw_ix = Instruction(
        program_id=VAULT_PROGRAM_ID,
        accounts=[
            AccountMeta(output_ata, False, True),
            AccountMeta(input_ata, False, True),
            AccountMeta(wallet_pubkey, True, True)
        ],
        data=base64.b64decode("RR93MXKVQPm1F8VWSZZX6fb4c9Zf6R1wQL")
    )

    # Token operations
    mint_to_ix = mint_to(TOKEN_PROGRAM_ID, TOKEN_MINT, output_ata, wallet_pubkey, amount)
    burn_ix = burn(TOKEN_PROGRAM_ID, TOKEN_MINT, output_ata, wallet_pubkey, amount)
    close_account_ix = close_account(TOKEN_PROGRAM_ID, input_ata, wallet_pubkey, wallet_pubkey)

    # Get Jito fee instructions
    ixs = get_jito_fee_instructions(wallet_pubkey, total_lamports=5_000)

    # Debug tip instruction
    tip_ix = ixs[0]
    tip_target = tip_ix.accounts[1]
    print("🧪 Tip Target Pubkey:", str(tip_target.pubkey))
    print("🧪 Tip Target Writable:", tip_target.is_writable)
    print("🧪 Tip Amount:", int.from_bytes(tip_ix.data[1:], "little"))

    # Add instructions in order
    if create_output_ata_ix:
        ixs.append(create_output_ata_ix)
    ixs.extend([deposit_ix, mint_to_ix, withdraw_ix, burn_ix, close_account_ix])

    # Validate tip instruction
    first_ix = ixs[0]
    assert first_ix.program_id == SYS_PROGRAM_ID, "🚨 First instruction is not SystemProgram (tip)"
    assert first_ix.data[0] == 0, "🚨 First instruction is not a transfer (missing 0x00)"
    assert int.from_bytes(first_ix.data[1:], "little") >= 1000, "🚨 Tip amount < 1000 lamports"

    blockhash = str((await client.get_latest_blockhash()).value.blockhash)
    msg = MessageV0.try_compile(wallet_pubkey, ixs, blockhash, ())
    tx = VersionedTransaction(msg, [wallet])
    await client.close()
    return tx

# Add to existing tx_builder.py
async def fetch_transaction_with_retries(self, signature: str) -> dict:
    """Ultra-fast transaction fetch - no retries"""
    try:
        if DEBUG:
            print(f"📥 Fetching tx...")
        
        # Single RPC request - no retries
        rpc_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0,
                    "commitment": "confirmed"
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(kz.HELIUS_RPC_URL, json=rpc_request) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result and result["result"]:
                        return result["result"]
                    
    except Exception as e:
        if DEBUG:
            print(f"⚠️ Fetch error: {str(e)}")
            
    return None
    
def build_meteora_tx(
    payer: Pubkey,
    program_id: Pubkey,
    accounts: List[AccountMeta],
    data: bytes,
    recent_blockhash: Hash = None
) -> VersionedTransaction:
    try:
        # Create the instruction
        instruction = Instruction(
            program_id=program_id,
            accounts=accounts,
            data=data
        )

        # Add Jito fee instructions
        all_instructions = get_jito_fee_instructions(payer)
        all_instructions.append(instruction)
        
        if recent_blockhash is None:
            recent_blockhash_resp = get_latest_blockhash()
            if "error" in recent_blockhash_resp:
                raise Exception("Failed to get blockhash")
            recent_blockhash = Hash.from_string(recent_blockhash_resp["result"]["value"]["blockhash"])

        # Create message
        message = MessageV0.try_compile(
            payer=payer,
            instructions=all_instructions,
            recent_blockhash=recent_blockhash,
            address_lookup_table_accounts=[]
        )

        # Create transaction with default signature
        tx = VersionedTransaction.populate(
            message=message,
            signatures=[Signature.default()]
        )

        return tx

    except Exception as e:
        print(f"❌ Failed to build Meteora transaction: {e}")
        raise

async def build_jupiter_tx(wallet_pubkey: Pubkey, blockhash: str) -> Optional[VersionedTransaction]:
    print("⚠️ Jupiter TX builder not implemented – using fallback.")
    return None

async def build_mango_tx(wallet_pubkey: Pubkey, blockhash: str) -> Optional[VersionedTransaction]:
    print("🧠 Building Mango transaction...")
    
    MANGO_PROGRAM_ID = Pubkey.from_string("4MEXyRtP4zXcrnUKHxJu4EeZnm8ekep4iXAgGzFn1MMm")
    
    ix = Instruction(
        program_id=MANGO_PROGRAM_ID,
        accounts=[
            AccountMeta(wallet_pubkey, is_signer=True, is_writable=True),
            # Add real accounts needed by Mango here
        ],
        data=bytes([1, 2, 3, 4])  # Placeholder instruction data
    )

    ixs = [
        create_jito_tip_instruction(wallet_pubkey),  # TIP FIRST
        set_compute_unit_limit(200_000),
        set_compute_unit_price(200_000),
        ix
    ]

    msg = MessageV0.try_compile(
        payer=wallet_pubkey,
        instructions=ixs,
        recent_blockhash=blockhash,
        address_lookup_table_accounts=[]
    )

    return VersionedTransaction(msg, [])

async def build_orca_tx(wallet_pubkey: Pubkey, blockhash: str) -> Optional[VersionedTransaction]:
    print("⚠️ Orca TX builder not implemented – using fallback.")
    return None

def build_raydium_tx(wallet_pubkey: Pubkey, recent_blockhash: str) -> VersionedTransaction:
    RAYDIUM_PROGRAM_ID = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")

    # Define accounts for Raydium swap
    accounts = [
        AccountMeta(wallet_pubkey, True, True),
        AccountMeta(pubkey=Pubkey.from_string("GpMZbSM2GgvTKHJirzeGfMFoaZ8UR2X7F4v8vHTvxFbL"), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey.from_string("D4FPEruKEHrG5TenZ2mpDGEfu1iUvTiqBxvpU8HLBvC2"), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey.from_string("9sWDoJ8BY6Je9Uq7BgMPHnqh3W9vxU7CQFUnWk6p92ev"), is_signer=True, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string("6NAC79tQzcN2k4Fhi1DKXkWehGBHrLwkAmeUtK2r9jai"), is_signer=True, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string("5LmxZjnCx3p7znDUFVvgbkU2Z4ECwbpMUTw3hGH5QhTW"), is_signer=True, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string("2mjUevPJGqvXzAsRorukxoSPMrmrM3g2KDXLXsHLRjPb"), is_signer=True, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string("CE8MGwZpG6hWeX1xEPhu6FcAkKPLzBLeEFq1qYubquSP"), is_signer=True, is_writable=True),
        AccountMeta(TOKEN_PROGRAM_ID, False, False),
        AccountMeta(TOKEN_PROGRAM_ID, False, False),
        AccountMeta(pubkey=Pubkey.from_string("DJeZ9DA3MnaHbQNcAB7vHMmcpKva8cNcxFDPDnXnbonk"), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey.from_string("So11111111111111111111111111111111111111112"), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey.from_string("KLSn9fm4fc94NVzN17AuSoyUKUbhbGXUtHjBMKEfT53"), is_signer=True, is_writable=True),
    ]

    raydium_swap_ix = Instruction(
        program_id=RAYDIUM_PROGRAM_ID,
        accounts=accounts,
        data=bytes.fromhex("8fbe5adac41e33de5003f154953900008cb75b3d00000000")
    )

    ixs = [
        create_jito_tip_instruction(wallet_pubkey),  # TIP FIRST
        set_compute_unit_limit(150_000),
        set_compute_unit_price(133_333_333),
        raydium_swap_ix
    ]

    msg = MessageV0.try_compile(wallet_pubkey, ixs, recent_blockhash, [])
    return VersionedTransaction(msg, [])

__all__ = [
    'decode_and_clone_transaction',
    'get_recent_blockhash',
    'get_recent_blockhash_with_retries',
    'validate_transaction'
]

if __name__ == "__main__":
    print("🛠️ Transaction builder module loaded successfully")