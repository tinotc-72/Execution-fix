# --- FIX: Add create_ata_if_missing for generic executor compatibility ---
from solders.pubkey import Pubkey
from config import WALLET
def create_ata_if_missing(wallet_pubkey: Pubkey, token_mint: Pubkey, rpc_client=None) -> str:
    """
    Dummy implementation: Returns the associated token address as a string.
    Replace with real logic for actual ATA creation if needed.
    """
    return str(token_mint)
# utils.py

import aiohttp
import json
from typing import Any, Dict
from solders.hash import Hash
from solders.pubkey import Pubkey
from env_keys import EnvKeys

# Use your actual RPC URL here
env_keys = EnvKeys()
RPC_URL = env_keys.HELIUS_RPC_URL

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
    
def load_keypair():
    """Return the WALLET from config.py (loaded from .env)"""
    return WALLET
    
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

async def fetch_json_rpc(method: str, params: list) -> Dict[str, Any]:
    """
    Make a JSON-RPC request to the Solana network
    """
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            async with session.post(RPC_URL, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ HTTP Error {response.status}: {await response.text()}")
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Network error: {e}")
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

async def get_balance(pubkey: str) -> Dict[str, Any]:
    """
    Get SOL balance for a given public key
    """
    try:
        response = await fetch_json_rpc(
            method="getBalance",
            params=[pubkey, {"commitment": "processed"}]
        )
        
        if "error" in response:
            print(f"🚨 Balance error: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Balance error: {e}")
        return {"error": str(e)}

async def send_raw_transaction(serialized_tx: bytes, skip_preflight: bool = False, preflight_commitment: str = "processed", max_retries: int = 0) -> Dict[str, Any]:
    """
    Send a raw transaction to the Solana network.
    
    DEPRECATED: This function is kept for backward compatibility only.
    New code should use executors.submit.send_and_confirm_v0_tx() for consistent
    confirmation polling and structured logging.
    """
    import base64
    try:
        # Encode transaction as base64
        tx_b64 = base64.b64encode(serialized_tx).decode('utf-8')
        
        response = await fetch_json_rpc(
            method="sendTransaction",
            params=[
                tx_b64,
                {
                    "skipPreflight": skip_preflight,
                    "preflightCommitment": preflight_commitment,
                    "encoding": "base64",
                    "maxRetries": max_retries
                }
            ]
        )
        
        if "error" in response:
            print(f"🚨 Send transaction error: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Send transaction error: {e}")
        return {"error": str(e)}

async def get_signature_statuses(signatures: list[str]) -> Dict[str, Any]:
    """
    Get status of transaction signatures
    """
    try:
        response = await fetch_json_rpc(
            method="getSignatureStatuses",
            params=[signatures, {"searchTransactionHistory": True}]
        )
        
        if "error" in response:
            print(f"🚨 Signature status error: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Signature status error: {e}")
        return {"error": str(e)}

async def simulate_transaction(serialized_tx: bytes, accounts_encoding: str = "base64") -> Dict[str, Any]:
    """
    Simulate a transaction
    """
    import base64
    try:
        tx_b64 = base64.b64encode(serialized_tx).decode('utf-8')
        
        response = await fetch_json_rpc(
            method="simulateTransaction",
            params=[
                tx_b64,
                {
                    "encoding": "base64",
                    "commitment": "processed",
                    "accounts": {
                        "encoding": accounts_encoding
                    }
                }
            ]
        )
        
        if "error" in response:
            print(f"🚨 Simulate transaction error: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Simulate transaction error: {e}")
        return {"error": str(e)}

async def get_health() -> Dict[str, Any]:
    """
    Check Solana RPC health status
    """
    try:
        response = await fetch_json_rpc(
            method="getHealth",
            params=[]
        )
        
        if "error" in response:
            print(f"🚨 Health check error: {response['error']}")
            return {"error": response["error"]}
            
        return response
        
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return {"error": str(e)}

# Helper function to create RPC client with URL
def create_rpc_url(rpc_url: str = None) -> str:
    """
    Get RPC URL from parameter or default from env
    """
    if rpc_url:
        return rpc_url
    return RPC_URL

async def fetch_json_rpc_with_url(rpc_url: str, method: str, params: list) -> Dict[str, Any]:
    """
    Make a JSON-RPC request to a specific Solana RPC URL
    """
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            async with session.post(rpc_url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ HTTP Error {response.status}: {await response.text()}")
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Network error: {e}")
            return {"error": str(e)}

# ============================================================================
# SPL Token Helper Functions - Solders-Only Implementation
# ============================================================================

from solders.instruction import Instruction, AccountMeta
from typing import Optional, Tuple

# SPL Token Program IDs
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")

def find_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    """
    Derive the associated token address for a given owner and mint.
    Uses solders PDA derivation.
    
    Args:
        owner: The owner's public key
        mint: The token mint public key
        
    Returns:
        The derived associated token address
    """
    seeds = [bytes(owner), bytes(TOKEN_PROGRAM_ID), bytes(mint)]
    ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return ata

def create_associated_token_account_ix(
    payer: Pubkey,
    owner: Pubkey, 
    mint: Pubkey
) -> Instruction:
    """
    Create an instruction to create an associated token account.
    Uses solders instruction construction.
    
    Args:
        payer: The account that will pay for the creation
        owner: The owner of the associated token account
        mint: The token mint
        
    Returns:
        Instruction to create the associated token account
    """
    ata = find_associated_token_address(owner, mint)
    
    metas = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    
    # Associated token account instruction has no data
    return Instruction(program_id=ASSOCIATED_TOKEN_PROGRAM_ID, accounts=metas, data=b"")

def get_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    """
    Alias for find_associated_token_address for compatibility with spl.token.instructions API.
    
    Args:
        owner: The owner's public key
        mint: The token mint public key
        
    Returns:
        The derived associated token address
    """
    return find_associated_token_address(owner, mint)

def create_associated_token_account(
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey
) -> Instruction:
    """
    Alias for create_associated_token_account_ix for compatibility with spl.token.instructions API.
    
    Args:
        payer: The account that will pay for the creation
        owner: The owner of the associated token account
        mint: The token mint
        
    Returns:
        Instruction to create the associated token account
    """
    return create_associated_token_account_ix(payer, owner, mint)

# RPC Client class to replace AsyncClient from solana-py
class RPCClient:
    """
    Replacement for AsyncClient using direct JSON-RPC calls with aiohttp
    """
    
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
    
    async def get_balance(self, pubkey):
        """Get SOL balance for a pubkey"""
        pubkey_str = str(pubkey) if hasattr(pubkey, '__str__') else pubkey
        result = await fetch_json_rpc_with_url(
            self.rpc_url,
            "getBalance",
            [pubkey_str, {"commitment": "processed"}]
        )
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        # Return a simple object with .value attribute for compatibility
        class BalanceResult:
            def __init__(self, value):
                self.value = value
        
        return BalanceResult(result.get("result", {}).get("value", 0))
    
    async def get_latest_blockhash(self, commitment: str = "processed"):
        """Get latest blockhash"""
        result = await fetch_json_rpc_with_url(
            self.rpc_url,
            "getLatestBlockhash",
            [{"commitment": commitment}]
        )
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        # Return object with .value.blockhash for compatibility
        from solders.hash import Hash
        
        class BlockhashValue:
            def __init__(self, blockhash_str):
                self.blockhash = Hash.from_string(blockhash_str)
        
        class BlockhashResult:
            def __init__(self, blockhash_str):
                self.value = BlockhashValue(blockhash_str)
        
        blockhash_str = result.get("result", {}).get("value", {}).get("blockhash")
        return BlockhashResult(blockhash_str)
    
    async def get_account_info(self, pubkey, encoding: str = "base64", commitment: str = "processed"):
        """Get account info"""
        pubkey_str = str(pubkey) if hasattr(pubkey, '__str__') else pubkey
        result = await fetch_json_rpc_with_url(
            self.rpc_url,
            "getAccountInfo",
            [pubkey_str, {"encoding": encoding, "commitment": commitment}]
        )
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        # Return object with .value for compatibility
        class AccountInfoResult:
            def __init__(self, account_data):
                self.value = account_data
        
        return AccountInfoResult(result.get("result", {}).get("value"))
    
    async def send_raw_transaction(self, serialized_tx: bytes, opts: dict = None):
        """Send raw transaction"""
        import base64
        tx_b64 = base64.b64encode(serialized_tx).decode('utf-8')
        
        # Handle opts parameter
        skip_preflight = False
        preflight_commitment = "processed"
        max_retries = 0
        
        if opts:
            skip_preflight = opts.get("skip_preflight", False)
            preflight_commitment = opts.get("preflight_commitment", "processed")
            max_retries = opts.get("max_retries", 0)
        
        result = await fetch_json_rpc_with_url(
            self.rpc_url,
            "sendTransaction",
            [
                tx_b64,
                {
                    "skipPreflight": skip_preflight,
                    "preflightCommitment": preflight_commitment,
                    "encoding": "base64",
                    "maxRetries": max_retries
                }
            ]
        )
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        # Return object with .value for compatibility
        class SendResult:
            def __init__(self, signature):
                self.value = signature
        
        return SendResult(result.get("result"))
    
    async def send_transaction(self, transaction, opts: dict = None):
        """Send transaction (handles both VersionedTransaction and legacy)"""
        # Serialize the transaction
        serialized_tx = bytes(transaction)
        return await self.send_raw_transaction(serialized_tx, opts)
    
    async def get_signature_statuses(self, signatures: list):
        """Get signature statuses"""
        sig_strings = [str(sig) for sig in signatures]
        result = await fetch_json_rpc_with_url(
            self.rpc_url,
            "getSignatureStatuses",
            [sig_strings, {"searchTransactionHistory": True}]
        )
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        # Return object with .value for compatibility
        class SignatureStatusResult:
            def __init__(self, statuses):
                self.value = statuses
        
        return SignatureStatusResult(result.get("result", {}).get("value", []))
    
    async def simulate_transaction(self, transaction, commitment: str = "processed"):
        """Simulate transaction"""
        import base64
        serialized_tx = bytes(transaction)
        tx_b64 = base64.b64encode(serialized_tx).decode('utf-8')
        
        result = await fetch_json_rpc_with_url(
            self.rpc_url,
            "simulateTransaction",
            [
                tx_b64,
                {
                    "encoding": "base64",
                    "commitment": commitment
                }
            ]
        )
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        # Return object with .value for compatibility
        class SimulateResult:
            def __init__(self, sim_data):
                self.value = sim_data
        
        return SimulateResult(result.get("result", {}).get("value"))
    
    async def get_health(self):
        """Check RPC health"""
        result = await fetch_json_rpc_with_url(
            self.rpc_url,
            "getHealth",
            []
        )
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        return result.get("result", "ok")
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass



    