# utils.py

import aiohttp
import json
import logging
from typing import Any, Dict, Optional
from solders.keypair import Keypair
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.system_program import ID as SYS_PROGRAM_ID
import base58
from env_keys import kz
import asyncio
import os
import traceback
from datetime import datetime, UTC

# Constants from minimal_tx_builder that we need
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
PUMP_ROUTER = Pubkey.from_string("BSfD6Vz2UxXz6byH5ouA9VqZdJW44gYVi8J2AEgdcJAm")  # Production PUMP router

# Configure logging
logger = logging.getLogger(__name__)
import json
from typing import Any, Dict, Optional
from solders.keypair import Keypair  # New import
from solders.hash import Hash
from solders.pubkey import Pubkey
import base58
from env_keys import kz
import asyncio
import os
import traceback
from datetime import datetime, UTC

# Use your actual RPC URL here
RPC_URL = kz.HELIUS_RPC_URL

WALLET_A = Pubkey.from_string("suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK")

async def get_transaction_with_logs(signature: str) -> Dict[str, Any]:
    """Fetch a transaction including its logs"""
    try:
        response = await fetch_json_rpc(
            method="getTransaction",
            params=[
                signature,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0,
                    "commitment": "confirmed",
                    "rewards": False
                }
            ]
        )
        
        if "result" not in response or not response["result"]:
            print(f"❌ No transaction data for {signature}")
            return None
            
        if "meta" not in response["result"] or "logMessages" not in response["result"]["meta"]:
            print(f"❌ No logs in transaction {signature}")
            return None
            
        return response["result"]
        
    except Exception as e:
        print(f"❌ Error fetching transaction: {e}")
        return None
    
def load_keypair() -> Keypair:
    """Load wallet keypair from private key"""
    try:
        # Get private key from your keyZ.py file
        private_key = kz.PRIVATE_KEY
        
        # Convert to bytes if it's a string
        if isinstance(private_key, str):
            if private_key.startswith('['):  # Array format
                private_key = bytes([int(x) for x in private_key.strip('[]').split(',')])
            else:  # Base58 format
                private_key = base58.b58decode(private_key)
                
        # Create Keypair
        keypair = Keypair.from_bytes(private_key)
        print(f"✅ Wallet loaded successfully: {keypair.pubkey()}")
        return keypair

    except Exception as e:
        print(f"❌ Failed to load wallet: {e}")
        return None
    
def rewrite_pda_if_wallet_a(original_key: Pubkey, program_id: Pubkey, wallet_a: Pubkey, new_payer: Pubkey) -> Pubkey:
    """
    Rewrite PDA addresses if they were derived using Wallet A
    """
    try:
        # Common PDA seeds that might contain Wallet A
        potential_seeds = [
            [bytes(wallet_a)],
            [bytes(wallet_a), b"nft"],
            [bytes(wallet_a), b"metadata"],
            [bytes(wallet_a), b"escrow"],
            # Add more common seed patterns if needed
        ]

        # Try to find if this is a PDA derived using Wallet A
        for seeds in potential_seeds:
            try:
                pda, _ = Pubkey.find_program_address(seeds, program_id)
                if pda == original_key:
                    # Found a match! Create new PDA with new_payer
                    new_seeds = [bytes(new_payer) if s == bytes(wallet_a) else s for s in seeds]
                    new_pda, _ = Pubkey.find_program_address(new_seeds, program_id)
                    print(f"🔄 Rewrote PDA: {original_key} -> {new_pda}")
                    return new_pda
            except Exception:
                continue

        # If no PDA match found, return the original key
        return original_key

    except Exception as e:
        print(f"⚠️ PDA rewrite failed: {e}")
        return original_key

async def fetch_json_rpc(method: str, params: list = None, url: str = None) -> Dict[str, Any]:
    """Make a JSON-RPC request to the Solana network"""
    if url is None:
        url = RPC_URL
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or []
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ RPC request failed with status {response.status}: {await response.text()}")
                    return {"error": f"HTTP {response.status}"}
    except Exception as e:
        print(f"❌ RPC request error: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}

async def get_latest_blockhash() -> Dict[str, Any]:
    """
    Get the latest blockhash from the Solana network
    """
    try:
        response = await fetch_json_rpc(
            method="getLatestBlockhash",
            params=[{"commitment": "processed"}]
        )
        
        if "error" in response:
            print(f"🚨 Failed to get blockhash: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Blockhash error: {e}")
        return {"error": str(e)}

async def get_account_info(pubkey: str) -> Dict[str, Any]:
    """
    Get account info for a given public key
    """
    try:
        response = await fetch_json_rpc(
            method="getAccountInfo",
            params=[
                pubkey,
                {
                    "encoding": "base64",
                    "commitment": "processed"
                }
            ]
        )
        
        if "error" in response:
            print(f"🚨 Account info error: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Account info error: {e}")
        return {"error": str(e)}

async def get_multiple_accounts(pubkeys: list[str]) -> Dict[str, Any]:
    """
    Get info for multiple accounts
    """
    try:
        response = await fetch_json_rpc(
            method="getMultipleAccounts",
            params=[
                pubkeys,
                {
                    "encoding": "base64",
                    "commitment": "processed"
                }
            ]
        )
        
        if "error" in response:
            print(f"🚨 Multiple accounts error: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Multiple accounts error: {e}")
        return {"error": str(e)}

def get_formatted_datetime() -> str:
    """Get current datetime in UTC formatted as string"""
    return datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

async def get_token_account_balance(token_account: Pubkey) -> int:
    """Get token balance for a token account with retries.
    
    Args:
        token_account: The token account to check
        
    Returns:
        int: The token balance amount
        
    Raises:
        ValueError: If the balance cannot be retrieved
    """
    try:
        response = await fetch_json_rpc(
            method="getTokenAccountBalance",
            params=[str(token_account)]
        )
        
        if "result" in response and "value" in response["result"]:
            return int(response["result"]["value"]["amount"])
            
        raise ValueError("Invalid response format")
        
    except Exception as e:
        raise ValueError(f"Failed to get token balance: {str(e)}")

async def check_token_account_exists(token_account: Pubkey) -> bool:
    """Check if a token account exists and is initialized"""
    try:
        response = await fetch_json_rpc(
            method="getAccountInfo",
            params=[
                str(token_account),
                {"encoding": "jsonParsed"}
            ]
        )
        
        return (
            "result" in response 
            and response["result"] is not None 
            and response["result"]["value"] is not None
        )
    except Exception:
        return False

async def wait_for_token_balance(
    executor,
    token_account: Pubkey,
    max_retries: int = 10,
    retry_delay: float = 2.0,
    min_balance: int = 1
) -> Dict[str, Any]:
    """Wait for token balance to be available with detailed logging"""
    print(f"\n🔍 Checking token balance for account: {token_account}")
    
    for attempt in range(max_retries):
        print(f"\n⏳ Balance check attempt {attempt + 1}/{max_retries}")
        
        # First check if account exists
        exists = await check_token_account_exists(token_account)
        if not exists:
            print("❌ Token account does not exist yet")
            await asyncio.sleep(retry_delay)
            continue
            
        # Then check balance
        result = await get_token_account_balance(token_account)
        if result["success"]:
            balance = result["balance"]
            decimals = result["decimals"]
            print(f"💰 Current balance: {balance} ({balance / 10**decimals:.9f} tokens)")
            
            if balance >= min_balance:
                return {
                    "success": True,
                    "balance": balance,
                    "decimals": decimals
                }
            print(f"⚠️ Balance too low: {balance} < {min_balance}")
        else:
            print(f"⚠️ Balance check failed: {result.get('error', 'Unknown error')}")
            
        await asyncio.sleep(retry_delay)
        
    return {
        "success": False,
        "error": "Timeout waiting for token balance",
        "balance": 0,
        "decimals": 0
    }

def get_current_user() -> str:
    """Get current user's login name"""
    try:
        return os.getlogin()
    except:
        return "unknown-user"

def create_sell_instruction(
    token_mint: Pubkey,
    owner: Pubkey,
    amount: int,
    slippage_bps: int,
    token_ata: Pubkey,
    config_pda: Pubkey,
    route_params_pda: Pubkey,
    route_state_pda: Pubkey,
    token_vault_pda: Pubkey
) -> Optional[Instruction]:
    """
    Create an instruction to sell tokens through the PUMP router.
    
    Args:
        token_mint (Pubkey): The mint address of the token to sell
        owner (Pubkey): The owner's public key
        amount (int): The amount of tokens to sell
        slippage_bps (int): Slippage tolerance in basis points (1 bp = 0.01%)
        token_ata (Pubkey): The associated token account for the token
        config_pda (Pubkey): The configuration PDA
        route_params_pda (Pubkey): The route parameters PDA
        route_state_pda (Pubkey): The route state PDA
        token_vault_pda (Pubkey): The token vault PDA
        
    Returns:
        Instruction: The sell instruction
    """
    try:
        # Account metas for the sell instruction
        accounts = [
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),          # Owner/signer
            AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),   # Token mint
            AccountMeta(pubkey=token_ata, is_signer=False, is_writable=True),     # Owner's token account
            AccountMeta(pubkey=config_pda, is_signer=False, is_writable=False),   # Config PDA
            AccountMeta(pubkey=route_params_pda, is_signer=False, is_writable=True),  # Route params
            AccountMeta(pubkey=route_state_pda, is_signer=False, is_writable=True),   # Route state
            AccountMeta(pubkey=token_vault_pda, is_signer=False, is_writable=True),   # Token vault
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False), # Token program
            AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),   # System program
        ]
        
        # Create instruction data
        # Format: [command_byte(1), amount(u64), slippage_bps(u16)]
        instruction_data = bytes([2])  # Command byte for sell
        instruction_data += amount.to_bytes(8, 'little')  # Amount as u64
        instruction_data += slippage_bps.to_bytes(2, 'little')  # Slippage as u16
        
        # Create instruction
        instruction = Instruction(
            program_id=PUMP_ROUTER,  # Use the PUMP router program ID
            accounts=accounts,
            data=instruction_data
        )
        
        return instruction
    
    except Exception as e:
        logger.error(f"Error creating sell instruction: {e}")
        return None

