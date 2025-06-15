# tx_builder.py - old before deleting and cleaning up 

from solders.instruction import AccountMeta, Instruction, CompiledInstruction  # Added CompiledInstruction
from solana.rpc.async_api import AsyncClient  # At top with other imports
import base64
import base58
import asyncio
from random import choice
import json
from solders.signature import Signature 
from solders.message import MessageV0
from solders.transaction import Transaction, VersionedTransaction
from datetime import datetime, UTC
import traceback 
from solders.keypair import Keypair 
import aiohttp
from typing import List, Optional, Tuple
from typing import Optional, Union, List, Dict, Any
from typing import Union, Optional
from solders.hash import Hash
import keyZ as kz
from solders.pubkey import Pubkey
from solders.message import Message, MessageV0 
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams
from solders.system_program import ID as SYS_PROGRAM_ID

# SPL Token imports
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    mint_to,
    burn,
    close_account
)

# Local imports
# tx_builder.py
from config import (
    DECODED_PRIVATE_KEY,
    BOT_PUBKEY,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE,
    JITO_TIP_AMOUNT,
    VALID_JITO_TIP_ACCOUNTS,
    COMPUTE_BUDGET_PROGRAM_ID,
    SYS_PROGRAM_ID,
)

# === Constants ===
DEBUG = True
MAX_RETRIES = 3
RETRY_DELAY = 0.1
COMPUTE_UNIT_LIMIT = 200_000
COMPUTE_UNIT_PRICE = 1000
JITO_TIP_AMOUNT = 5000

# Program IDs
SYS_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")

# Jito Configuration
VALID_JITO_TIP_ACCOUNTS = [
    Pubkey.from_string("96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5"),
    Pubkey.from_string("HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe"),
    Pubkey.from_string("Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY"),
    Pubkey.from_string("ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49")
]

# Add these constants
COMPUTE_UNIT_LIMIT = 200_000  # Standard compute unit limit
COMPUTE_UNIT_PRICE = 1000  # Base price in microlamports
JITO_TIP_AMOUNT = 5000  # Base Jito tip in lamports
WALLET_A = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
CURRENT_USER = "tinotc-72"
START_TIME = "2025-06-03 14:44:35"  # Updated to current time
tip_account = choice(VALID_JITO_TIP_ACCOUNTS)

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

JITO_BUNDLE_ENDPOINT = "https://mainnet.block-engine.jito.wtf/api/v1/bundles/sendBundle"
JITO_AUTH_UUID = kz.JITO_UUID

# Update RPC endpoints to only use Jito and Helius
RPC_ENDPOINTS = [
    "https://jito-api.mainnet.jito.network",  # Primary (Jito)
    kz.HELIUS_RPC_URL,  # Secondary (Helius)
]

RPC_ENDPOINTS = [url for url in RPC_ENDPOINTS if url]  # Remove None values

def decode_instruction_data(data: str) -> bytes:
    """Safely decode instruction data from base64"""
    try:
        # Add padding if needed
        padding_needed = len(data) % 4
        if padding_needed:
            data += '=' * (4 - padding_needed)
        return base64.b64decode(data)
    except Exception as e:
        print(f"⚠️ Error decoding instruction data: {e}")
        return b""

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

async def decode_and_clone_transaction(tx_data: Union[str, bytes], keypair: Keypair, recent_blockhash: str) -> Optional[VersionedTransaction]:
    """
    Decodes a transaction, adds Jito tip, and creates a new signed transaction.
    
    Args:
        tx_data: Original transaction data (base64 string or bytes)
        keypair: The Keypair to sign with
        recent_blockhash: Recent blockhash as string
    
    Returns:
        Optional[VersionedTransaction]: The new signed transaction or None if failed
    """
    try:
        # Decode the original transaction
        decoded_data = base64.b64decode(tx_data) if isinstance(tx_data, str) else tx_data
        original_tx = VersionedTransaction.from_bytes(decoded_data)
        
        print(f"📝 Original accounts count: {len(original_tx.message.account_keys)}")
        
        # Create new instructions list
        instructions = [create_jito_tip_instruction(keypair.pubkey())]
        
        # Add original instructions
        instructions.extend(original_tx.message.instructions)
        
        try:
            print("🔄 Creating and signing transaction...")
            
            # Convert blockhash to Hash object
            blockhash = Hash.from_string(recent_blockhash)
            
            # Create message with blockhash
            message = Message.new_with_blockhash(
                instructions=instructions,
                payer=keypair.pubkey(),
                blockhash=blockhash  # Using Hash object now
            )
            
            # Create transaction with message (proven method from test)
            tx = Transaction(
                from_keypairs=[keypair],
                message=message,
                recent_blockhash=blockhash
            )
            
            # Convert to versioned transaction
            final_tx = VersionedTransaction.from_legacy(tx)
            
            print("✅ Successfully created and signed transaction")
            print(f"📝 Instructions count: {len(instructions)}")
            print(f"📝 Signatures count: {len(final_tx.signatures)}")
            
            # Verify the transaction
            verify_result = final_tx.verify_with_results()
            print(f"🔍 Transaction verification result: {verify_result}")
            
            return final_tx
            
        except Exception as e:
            print(f"❌ Error creating transaction: {str(e)}")
            traceback.print_exc()
            return None
                
    except Exception as e:
        print(f"❌ Error in decode_and_clone_transaction: {str(e)}")
        traceback.print_exc()
        return None

def create_and_sign_transaction(
    keypair: Keypair,
    instructions: List[Instruction],
    recent_blockhash: str
) -> Optional[VersionedTransaction]:
    """
    Creates and signs a transaction using the working approach.
    
    Args:
        keypair: The Keypair to sign with and pay for the transaction
        instructions: List of Solana instructions to include in the transaction
        recent_blockhash: Recent blockhash as string (from get_latest_blockhash)
    
    Returns:
        Optional[VersionedTransaction]: The signed versioned transaction or None if failed
    
    Raises:
        Exception: If transaction creation or signing fails
    """
    try:
        print(f"🔄 Creating transaction with {len(instructions)} instructions...")
        
        # Convert blockhash string to Hash object
        try:
            blockhash = Hash.from_string(recent_blockhash)
            print(f"✅ Converted blockhash: {recent_blockhash[:8]}...")
        except Exception as e:
            print(f"❌ Error converting blockhash: {str(e)}")
            raise
        
        # Create message with blockhash
        try:
            message = Message.new_with_blockhash(
                instructions=instructions,
                payer=keypair.pubkey(),
                blockhash=blockhash  # Using Hash object
            )
            print("✅ Created message")
        except Exception as e:
            print(f"❌ Error creating message: {str(e)}")
            raise
        
        # Create and sign transaction
        try:
            tx = Transaction(
                from_keypairs=[keypair],
                message=message,
                recent_blockhash=blockhash
            )
            print("✅ Created and signed transaction")
        except Exception as e:
            print(f"❌ Error creating transaction: {str(e)}")
            raise
        
        # Convert to versioned transaction
        try:
            versioned_tx = VersionedTransaction.from_legacy(tx)
            print("✅ Converted to versioned transaction")
        except Exception as e:
            print(f"❌ Error converting to versioned transaction: {str(e)}")
            raise
        
        # Verify the transaction
        try:
            verify_result = versioned_tx.verify_with_results()
            print(f"🔍 Transaction verification result: {verify_result}")
            
            if not all(verify_result):
                print("⚠️ Transaction verification failed!")
                return None
        except Exception as e:
            print(f"❌ Error verifying transaction: {str(e)}")
            raise
        
        # Print transaction details
        print(f"\n📝 Transaction Details:")
        print(f"- Instructions: {len(instructions)}")
        print(f"- Signatures: {len(versioned_tx.signatures)}")
        print(f"- Message type: {type(versioned_tx.message)}")
        print(f"- Version: {versioned_tx.version}")
        
        return versioned_tx
        
    except Exception as e:
        print(f"❌ Transaction creation failed: {str(e)}")
        traceback.print_exc()
        return None

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

    async def copy_trade(self, txSigned: str, epochInfo: dict, senderAddress: str) -> Optional[str]:
        """
        Copy and execute a trade transaction.
        
        Args:
            txSigned: Base64 encoded transaction
            epochInfo: Epoch information
            senderAddress: Address of the transaction sender
            
        Returns:
            Optional[str]: Transaction signature if successful, None otherwise
        """
        try:
            print(f"\n🔄 Processing transaction from {senderAddress[:8]}...")
            
            # Decode transaction
            decoded_tx = VersionedTransaction.from_bytes(base64.b64decode(txSigned))
            
            # Get relevant transaction info
            recent_blockhash = decoded_tx.message.recent_blockhash
            instructions = decoded_tx.message.instructions
            
            # Add Jito tip instruction
            all_instructions = [create_jito_tip_instruction(self.keypair.pubkey())]
            all_instructions.extend(instructions)
            
            print(f"📝 Creating transaction with {len(all_instructions)} instructions")
            
            # Create our own transaction with the same instructions
            versioned_tx = create_and_sign_transaction(
                keypair=self.keypair,
                instructions=all_instructions,
                recent_blockhash=str(recent_blockhash)
            )
            
            if not versioned_tx:
                print("❌ Failed to create transaction")
                return None
            
            # Convert to base64 for sending
            tx_bytes = bytes(versioned_tx)
            tx_base64 = base64.b64encode(tx_bytes).decode('utf-8')
            
            print("🚀 Sending transaction...")
            
            # Send transaction with optimized settings
            response = await self.client._provider.send_transaction(
                tx_base64,
                opts=TxOpts(
                    skip_preflight=True,
                    max_retries=1,
                    preflight_commitment="processed"
                )
            )
            
            # Update metrics
            self.total_transactions += 1
            self.successful_transactions += 1
            self.last_transaction_time = datetime.now(UTC)
            
            print(f"✅ Transaction sent: {response[:8]}...")
            return response
            
        except Exception as e:
            self.failed_transactions += 1
            print(f"❌ Error in copy_trade: {str(e)}")
            traceback.print_exc()
            return None

    async def process_transaction(self, txSigned: str, epochInfo: dict, senderAddress: str) -> Optional[str]:
        """
        Process an incoming transaction.
        
        Args:
            txSigned: Base64 encoded transaction
            epochInfo: Epoch information
            senderAddress: Address of the transaction sender
            
        Returns:
            Optional[str]: Transaction signature if successful, None otherwise
        """
        try:
            # Validate transaction first
            if not await self.validate_transaction(txSigned, senderAddress):
                print("❌ Transaction validation failed")
                return None
                
            # Check if we're still within operating time
            current_time = datetime.now(UTC)
            if current_time < self.start_time:
                print("⏳ Bot not yet active")
                return None
                
            # Use the copy_trade method to execute the transaction
            response = await self.copy_trade(txSigned, epochInfo, senderAddress)
            
            # Log performance metrics
            if response:
                print(f"\n📊 Performance Metrics:")
                print(f"Total Transactions: {self.total_transactions}")
                print(f"Successful: {self.successful_transactions}")
                print(f"Failed: {self.failed_transactions}")
                success_rate = (self.successful_transactions / self.total_transactions * 100) if self.total_transactions > 0 else 0
                print(f"Success Rate: {success_rate:.1f}%")
            
            return response
            
        except Exception as e:
            print(f"❌ Error in process_transaction: {str(e)}")
            traceback.print_exc()
            return None

    def get_metrics(self) -> dict:
        """Get bot performance metrics."""
        return {
            "total_transactions": self.total_transactions,
            "successful_transactions": self.successful_transactions,
            "failed_transactions": self.failed_transactions,
            "success_rate": (self.successful_transactions / self.total_transactions * 100) if self.total_transactions > 0 else 0,
            "last_transaction_time": self.last_transaction_time.isoformat() if self.last_transaction_time else None,
            "uptime": (datetime.now(UTC) - self.start_time).total_seconds()
        }
                                                                                      
def create_fee_instructions(payer: Pubkey) -> List[Instruction]:
    """Create fee-related instructions"""
    instructions = []
    
    # Add Jito tip
    tip_ix = Instruction(
        program_id=SYS_PROGRAM_ID,
        accounts=[
            AccountMeta(payer, True, True),
            AccountMeta(VALID_JITO_TIP_ACCOUNTS[0], False, True)
        ],
        data=bytes([0]) + JITO_TIP_AMOUNT.to_bytes(8, "little")
    )
    instructions.append(tip_ix)
    print("✅ Added Jito tip instruction")
    
    # Add compute budget instructions
    compute_limit_ix = Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([0]) + COMPUTE_UNIT_LIMIT.to_bytes(4, "little")
    )
    instructions.append(compute_limit_ix)
    
    compute_price_ix = Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([3]) + COMPUTE_UNIT_PRICE.to_bytes(8, "little")
    )
    instructions.append(compute_price_ix)
    print("✅ Added compute budget instructions")
    
    return instructions

async def get_recent_blockhash(rpc_url: str) -> Optional[str]:
    """Get recent blockhash from the network"""
    try:
        async with aiohttp.ClientSession() as session:
            json_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getLatestBlockhash",
                "params": [{"commitment": "confirmed"}]
            }
            
            async with session.post(rpc_url, json=json_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result and "value" in result["result"]:
                        blockhash = result["result"]["value"]["blockhash"]
                        print(f"✅ Got blockhash: {blockhash[:10]}...")
                        return blockhash
                print("⚠️ Failed to get blockhash from network")
                return None
    except Exception as e:
        print(f"❌ Network error getting blockhash: {str(e)}")
        return None

async def get_recent_blockhash_with_retries(rpc_url: str) -> Optional[str]:
    """Get recent blockhash with retries"""
    MAX_RETRIES = 3
    RETRY_DELAY = 0.5
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"📡 Getting blockhash (attempt {attempt + 1}/{MAX_RETRIES})")
            blockhash = await get_recent_blockhash(rpc_url)
            if blockhash:
                return blockhash
            if attempt < MAX_RETRIES - 1:  # Don't sleep on last attempt
                await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"❌ Error on attempt {attempt + 1}: {str(e)}")
            if attempt < MAX_RETRIES - 1:  # Don't sleep on last attempt
                await asyncio.sleep(RETRY_DELAY)
    
    print("❌ Failed to get blockhash after all retries")
    return None

def decode_transaction(tx_data: Union[str, dict]) -> Optional[Dict]:
    """Decode transaction data into a dictionary containing message and signatures"""
    try:
        if isinstance(tx_data, dict):
            print("📦 Processing dictionary transaction data...")
            message = tx_data.get("message", {})
            signatures = tx_data.get("signatures", [])
            
            if not message:
                print("❌ No message found")
                return None
                
            if DEBUG:
                print(f"🔍 Message keys: {list(message.keys())}")
                print(f"📝 Number of signatures: {len(signatures)}")

            header = message.get("header", {})
            account_keys = message.get("accountKeys", [])
            recent_blockhash = message.get("recentBlockhash", "")
            instructions = message.get("instructions", [])

            if not all([header, account_keys, recent_blockhash, instructions]):
                print("❌ Missing required message components")
                return None

            # Convert account keys
            try:
                accounts = [Pubkey.from_string(key) for key in account_keys]
                print(f"✅ Converted {len(accounts)} account keys")
            except Exception as e:
                print(f"❌ Error converting account keys: {e}")
                return None

            # Process instructions
            compiled_instructions = []
            for idx, ix in enumerate(instructions):
                program_idx = ix.get("programIdIndex")
                account_indices = ix.get("accounts", [])
                data = decode_instruction_data(ix.get("data", ""))
                
                compiled_instructions.append({
                    "program_id_index": program_idx,
                    "accounts": account_indices,
                    "data": data
                })
                
            print(f"✅ Processed {len(compiled_instructions)} instructions")
            if DEBUG:
                for idx, ix in enumerate(compiled_instructions):
                    print(f"  📎 Instruction {idx}: {len(ix['data'])} bytes")

            # Return decoded data as dictionary
            return {
                "header": header,
                "accounts": accounts,
                "blockhash": recent_blockhash,
                "instructions": compiled_instructions,
                "signatures": signatures
            }

        else:
            print("🔄 Processing base64 string input...")
            decoded_data = base64.b64decode(tx_data)
            # Return raw bytes for base64 input
            return {"raw_data": decoded_data}

    except Exception as e:
        print(f"❌ Error decoding transaction: {e}")
        if DEBUG:
            traceback.print_exc()
        return None

__all__ = [
    'decode_and_clone_transaction',
    'get_recent_blockhash',
    'get_recent_blockhash_with_retries'
]

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
      
def clone_transaction(transaction_data: str, new_payer: Pubkey, blockhash: str) -> VersionedTransaction:
    """Clone a transaction with a new payer and blockhash"""
    try:
        # Decode transaction data
        decoded_data = base64.b64decode(transaction_data)
        
        # Create new versioned transaction
        tx = VersionedTransaction.deserialize(decoded_data)
        
        # Get the message
        message = tx.message
        
        # Replace the blockhash
        message.recent_blockhash = blockhash
        
        # Replace the fee payer
        message.static_account_keys[0] = new_payer
        
        # Create new transaction
        new_tx = VersionedTransaction(message=message, signatures=[])
        
        return new_tx
    
    except Exception as e:
        print(f"❌ Error cloning transaction: {str(e)}")
        return None

def prepare_transaction_for_jito(transaction: VersionedTransaction) -> dict:
    """Prepare transaction for Jito bundle submission"""
    try:
        if not isinstance(transaction, VersionedTransaction):
            raise ValueError("Expected VersionedTransaction")

        # First sign the transaction if not signed
        if not transaction.signatures or all(sig == [0]*64 for sig in transaction.signatures):
            print("⚠️ Transaction not signed, signing required")
            return None

        # Serialize the transaction
        tx_bytes = transaction.serialize()
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

async def submit_bundle(base64_tx: str):
    headers = {
        "Authorization": f"Bearer {JITO_AUTH_UUID}",
        "Content-Type": "application/json"
    }
    payload = {"bundle": [base64_tx]}

    async with httpx.AsyncClient() as client:
        response = await client.post(JITO_BUNDLE_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

# === Instruction Builders ===
def set_compute_unit_limit(units: int) -> Instruction:
    print(f"[tx_builder.py] Instruction class: {Instruction} (module: {Instruction.__module__})")
    print(f"[tx_builder.py] AccountMeta class: {AccountMeta} (module: {AccountMeta.__module__})")

    return Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([0]) + units.to_bytes(4, "little")  # tag = 0
    )

def set_compute_unit_price(microlamports: int) -> Instruction:
    print(f"[tx_builder.py] Instruction class: {Instruction} (module: {Instruction.__module__})")
    print(f"[tx_builder.py] AccountMeta class: {AccountMeta} (module: {AccountMeta.__module__})")

    return Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([3]) + microlamports.to_bytes(8, "little")  # tag = 3
    )

def create_jito_tip_instruction(keypair_pubkey: Pubkey) -> Instruction:  # Changed return type back to Instruction
    """Creates a Jito tip instruction with proper tip amounts"""
    try:
        # Use one of the approved tip addresses from Jito docs
        TIP_ACCOUNT = Pubkey.from_string("96gYZGLnJYVFmbjzopPSU4QiEV5fGqZNyN9nmNhvrZU5")
        
        # Define the accounts for the tip instruction
        accounts = [
            AccountMeta(
                pubkey=keypair_pubkey,  # Payer
                is_signer=True,
                is_writable=True
            ),
            AccountMeta(
                pubkey=TIP_ACCOUNT,  # Jito tip address
                is_signer=False,
                is_writable=True
            )
        ]
        
        # Create transfer instruction for the tip (5,000 lamports)
        return Instruction(
            program_id=SYS_PROGRAM_ID,  # System program for transfer
            accounts=accounts,
            data=bytes([2]) + (5_000).to_bytes(8, "little")  # Transfer instruction with 5,000 lamports
        )
        
    except Exception as e:
        print(f"❌ Error creating Jito tip instruction: {str(e)}")
        traceback.print_exc()
        return None
    
def create_priority_fee_instruction() -> Instruction:
    """Creates priority fee instruction"""
    try:
        PRIORITY_FEE = 5_000  # 5,000 lamports for priority fee
        
        # Create compute budget instruction for priority fee
        return Instruction(
            program_id=COMPUTE_BUDGET_PROGRAM_ID,
            accounts=[],
            data=bytes([3]) + PRIORITY_FEE.to_bytes(8, "little")
        )
    except Exception as e:
        print(f"❌ Error creating priority fee instruction: {str(e)}")
        return None

def get_jito_fee_instructions(payer: Pubkey) -> List[Instruction]:
    """Get all required Jito fee instructions"""
    instructions = []
    
    # 1. Add searcher tip (5,000 lamports)
    tip_ix = create_jito_tip_instruction(payer)
    if tip_ix:
        instructions.append(tip_ix)
    
    # 2. Add compute unit limit (200,000)
    compute_limit_ix = Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([0]) + (200_000).to_bytes(4, "little")
    )
    instructions.append(compute_limit_ix)
    
    # 3. Add priority fee (5,000 lamports)
    priority_fee_ix = Instruction(
        program_id=COMPUTE_BUDGET_PROGRAM_ID,
        accounts=[],
        data=bytes([3]) + (5_000).to_bytes(8, "little")
    )
    instructions.append(priority_fee_ix)
    
    return instructions

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

    ata_info = await client.get_account_info(user_ata)
    create_ata_ix = None
    if ata_info.value is None:
        create_ata_ix = create_associated_token_account(wallet_pubkey, wallet_pubkey, mint)

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
        data=amount.to_bytes(8, "little") + int(amount * 1.2).to_bytes(8, "little")
    )

    # Compute + Tip
    ixs = get_jito_fee_instructions(wallet_pubkey, total_lamports=5_000)
    if create_ata_ix:
        ixs.append(create_ata_ix)
    ixs.append(buy_ix)

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
        address_lookup_table_accounts=[]  # required
    )

    await client.close()
    return VersionedTransaction(msg, [wallet])

async def build_sell_tx(mint_str: str, amount: int, curve_str: str, wallet: Keypair) -> VersionedTransaction:
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
    base_ata = get_associated_token_address(wallet_pubkey, mint)

    ata_info = await client.get_account_info(base_ata)
    create_ata_ix = None
    if ata_info.value is None:
        create_ata_ix = create_associated_token_account(wallet_pubkey, wallet_pubkey, mint)

    sell_ix = Instruction(
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
        ],
        data=amount.to_bytes(8, "little") + int(amount * 0.8).to_bytes(8, "little")
    )

    # Compute + Tip
    ixs = get_jito_fee_instructions(wallet_pubkey, total_lamports=5_000)
    if create_ata_ix:
        ixs.append(create_ata_ix)
    ixs.append(sell_ix)

    # Debug tip instruction
    tip_ix = ixs[0]
    tip_target = tip_ix.accounts[1]
    print("🧪 Tip Target Pubkey:", str(tip_target.pubkey))
    print("🧪 Tip Target Writable:", tip_target.is_writable)
    print("🧪 Tip Amount:", int.from_bytes(tip_ix.data[1:], "little"))

    # Print instruction data for debugging
    for i, ix in enumerate(ixs):
        print(f"Instruction {i} data bytes:", list(ix.data))

    print("✅ Final instruction list:")
    for i, ix in enumerate(ixs):
        print(f"  - ixs[{i}]:", ix)

    # Validate tip instruction
    first_ix = ixs[0]
    assert first_ix.program_id == SYS_PROGRAM_ID, "🚨 First instruction is not SystemProgram (tip)"
    assert first_ix.data[0] == 0, "🚨 First instruction is not a transfer (missing 0x00)"
    assert int.from_bytes(first_ix.data[1:], "little") >= 1000, "🚨 Tip amount < 1000 lamports"

    # Compile transaction
    blockhash_obj: Hash = (await client.get_latest_blockhash()).value.blockhash
    msg = MessageV0.try_compile(
        payer=wallet_pubkey,
        instructions=ixs,
        recent_blockhash=blockhash_obj,
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
            # Increase slippage for buys
            min_out = int(amount * 0.90)  # 10% slippage
            return amount.to_bytes(8, "little") + min_out.to_bytes(8, "little")
        elif tx_type == "PumpSell":
            amount = int.from_bytes(original_data[:8], "little")
            # Increase slippage for sells
            min_out = int(amount * 0.85)  # 15% slippage
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





# new main.py

import base64
import time
import aiohttp
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from models import Bundle
from simulate_clone import clone_transaction_from_wallet_a
from tx_builder import create_and_sign_transaction
from fast_executor import FastExecutor
from config import HELIUS_RPC_URL, COMPUTE_UNIT_LIMIT, COMPUTE_UNIT_PRICE, JITO_TIP_AMOUNT

class CopyTradingBot:
    def __init__(self, keypair: Keypair, target_wallet: str):
        self.keypair = keypair
        self.target_wallet = target_wallet
        self.executor = FastExecutor(keypair)

    async def initialize(self):
        await self.executor.initialize()

    async def process_transaction_data(self, tx_data: dict):
        try:
            start_time = time.time()

            raw_tx = tx_data.get("transaction")
            if not raw_tx:
                print("❌ No transaction field in tx_data")
                return

            if isinstance(raw_tx, list):
                tx_base64 = raw_tx[0]
                decoded = base64.b64decode(tx_base64)
                print(f"✅ Base64 decoded transaction ({len(decoded)} bytes)")
            else:
                print("❌ Unexpected transaction format")
                return

            # 1. Attempt to build custom transaction
            blockhash = tx_data.get("meta", {}).get("recentBlockhash")  # Optional if not provided
            tx = create_and_sign_transaction(
                keypair=self.keypair,
                instructions=[],  # Fill with parsed instructions logic if needed
                recent_blockhash=blockhash or "",
                unit_limit=COMPUTE_UNIT_LIMIT,
                unit_price=COMPUTE_UNIT_PRICE,
                tip_amount=JITO_TIP_AMOUNT
            )

            # 2. If custom builder fails, fallback to clone
            if not tx:
                print("⚠️ Builder failed – trying fallback clone from Wallet A...")
                tx = await clone_transaction_from_wallet_a(tx_data, self.keypair)

            if not tx:
                print("❌ No transaction built or cloned – skipping")
                return

            # 3. Wrap in bundle
            bundle = Bundle(transactions=[tx])

            # 4. Submit transaction
            signature = await self.executor.submit_transaction(bundle)
            if not signature:
                print("❌ Submission failed")
                return

            print(f"🎯 Transaction submitted: {signature}")

            # 5. Post-submission check
            await self.verify_submission(signature)

        except Exception as e:
            print(f"❌ Error processing transaction: {str(e)}")

    async def verify_submission(self, signature: str):
        print("🔍 Verifying transaction status on-chain...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getSignatureStatuses",
                    "params": [[signature], {"searchTransactionHistory": True}]
                }
                async with session.post(HELIUS_RPC_URL, json=payload) as response:
                    result = await response.json()
                    statuses = result.get("result", {}).get("value", [])
                    if statuses and statuses[0] and statuses[0].get("confirmationStatus"):
                        print(f"✅ Transaction confirmed with status: {statuses[0]['confirmationStatus']}")
                    else:
                        print("⚠️ No confirmation status returned yet")
        except Exception as e:
            print(f"❌ Error verifying submission: {e}")
