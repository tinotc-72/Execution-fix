# utils.py

import aiohttp
import json
from typing import Any, Dict
from solders.keypair import Keypair  # New import
from solders.hash import Hash
from solders.pubkey import Pubkey
import base58
import keyZ as kz

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
    



    