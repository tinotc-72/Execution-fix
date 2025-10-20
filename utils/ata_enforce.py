"""
ATA Enforcement Utilities
==========================

RPC-based helper functions to check Associated Token Account (ATA) existence
and ensure ATAs are created before swaps/transfers to prevent runtime failures.

This module provides:
- RPC helper to check ATA existence via getTokenAccountsByOwner
- Wrapper to append ATA creation instructions using create_associated_token_account
"""
from __future__ import annotations
from typing import List, Optional
import requests
from solders.pubkey import Pubkey
from solders.instruction import Instruction


def rpc_call(rpc_url: str, method: str, params: list, timeout: float = 10.0) -> dict:
    """
    Make a JSON-RPC call to a Solana RPC endpoint.
    
    Args:
        rpc_url: The Solana RPC endpoint URL
        method: The RPC method to call (e.g., "getTokenAccountsByOwner")
        params: List of parameters for the RPC method
        timeout: Request timeout in seconds (default: 10.0)
        
    Returns:
        The JSON-RPC response as a dictionary
        
    Raises:
        requests.exceptions.RequestException: If the RPC request fails
    """
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    r = requests.post(rpc_url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def ata_exists(rpc_url: str, owner: str, mint: str) -> bool:
    """
    Check if an Associated Token Account exists for a given owner and mint.
    
    Uses a heuristic: queries token accounts by owner filtered by mint.
    Returns True if any account exists.
    
    Args:
        rpc_url: The Solana RPC endpoint URL
        owner: The owner's public key as a string
        mint: The token mint public key as a string
        
    Returns:
        True if at least one token account exists for the owner and mint, False otherwise
    """
    params = [
        owner,
        {
            "mint": mint,
            "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        }
    ]
    try:
        resp = rpc_call(rpc_url, "getTokenAccountsByOwner", params)
        result = resp.get("result", {})
        value = result.get("value", [])
        return bool(value)
    except Exception:
        # If RPC call fails, assume ATA doesn't exist to be safe
        # This ensures we attempt to create the ATA
        return False


def ensure_ata_ixs(
    rpc_url: str,
    payer: Pubkey,
    owner: Pubkey,
    mint: Pubkey,
    create_ata_fn
) -> List[Instruction]:
    """
    Ensure an Associated Token Account exists, creating it if necessary.
    
    This function:
    1. Checks if the ATA exists via RPC query
    2. If it doesn't exist, returns an ATA creation instruction
    3. If it exists, returns an empty list
    
    Args:
        rpc_url: The Solana RPC endpoint URL
        payer: The account that will pay for ATA creation (if needed)
        owner: The owner of the ATA
        mint: The token mint public key
        create_ata_fn: Function to create ATA instruction (e.g., create_associated_token_account)
                      Should accept (payer: Pubkey, owner: Pubkey, mint: Pubkey) -> Instruction
        
    Returns:
        Empty list if ATA exists, or list with one ATA creation instruction if it doesn't
        
    Example:
        from utils.ata import create_associated_token_account
        
        instructions = ensure_ata_ixs(
            rpc_url="https://api.mainnet-beta.solana.com",
            payer=wallet_keypair.pubkey(),
            owner=wallet_keypair.pubkey(),
            mint=token_mint_pubkey,
            create_ata_fn=create_associated_token_account
        )
        # Add instructions to transaction before swap instruction
    """
    if ata_exists(rpc_url, str(owner), str(mint)):
        return []
    return [create_ata_fn(payer, owner, mint)]
