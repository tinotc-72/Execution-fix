"""
utils/alts.py

Address Lookup Table (ALT) reconstruction utilities for cloned v0 transactions.
Fetches ALT data from RPC and builds AddressLookupTableAccount objects.
"""

import logging
import aiohttp
from typing import List, Dict, Any, Optional
from solders.address_lookup_table_account import AddressLookupTableAccount
from solders.pubkey import Pubkey

logger = logging.getLogger(__name__)


async def alts_from_meta_loaded(
    rpc_url: str,
    meta_loaded: Dict[str, List[str]]
) -> List[AddressLookupTableAccount]:
    """
    Reconstruct Address Lookup Table accounts from meta.loadedAddresses.
    
    Args:
        rpc_url: RPC endpoint URL
        meta_loaded: The meta.loadedAddresses dict containing 'writable' and 'readonly' lists
        
    Returns:
        List of AddressLookupTableAccount objects for use with MessageV0.try_compile()
    """
    # Extract all unique ALT addresses from writable and readonly
    # In the transaction response, loadedAddresses contains the actual account addresses
    # that were loaded from ALTs, but we need to reconstruct the original ALT references
    # from the message.addressTableLookups field
    
    # Note: This function needs the addressTableLookups from the message, not loadedAddresses
    # The caller should pass message.addressTableLookups instead
    logger.warning("alts_from_meta_loaded: This scaffold needs message.addressTableLookups, not meta.loadedAddresses")
    return []


async def alts_from_lookups(
    rpc_url: str,
    address_table_lookups: List[Dict[str, Any]]
) -> List[AddressLookupTableAccount]:
    """
    Reconstruct Address Lookup Table accounts from message.addressTableLookups.
    
    Args:
        rpc_url: RPC endpoint URL
        address_table_lookups: List of address table lookup entries from message
                              Each entry has 'accountKey', 'writableIndexes', 'readonlyIndexes'
        
    Returns:
        List of AddressLookupTableAccount objects for use with MessageV0.try_compile()
    """
    if not address_table_lookups:
        return []
    
    alt_accounts = []
    
    for lookup in address_table_lookups:
        try:
            # Extract the ALT address
            account_key = lookup.get("accountKey")
            if not account_key:
                logger.warning("Missing accountKey in address table lookup")
                continue
            
            # Fetch the ALT account data via RPC
            alt_data = await fetch_address_lookup_table(rpc_url, account_key)
            if not alt_data:
                logger.error(f"Failed to fetch ALT data for {account_key}")
                continue
            
            # Build AddressLookupTableAccount
            alt_account = build_alt_account(account_key, alt_data)
            if alt_account:
                alt_accounts.append(alt_account)
                logger.info(f"✅ Reconstructed ALT: {account_key}")
            
        except Exception as e:
            logger.error(f"Error processing ALT lookup: {e}")
            continue
    
    return alt_accounts


async def fetch_address_lookup_table(
    rpc_url: str,
    alt_address: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch Address Lookup Table account data via getAccountInfo RPC call.
    
    Args:
        rpc_url: RPC endpoint URL
        alt_address: The address of the ALT account
        
    Returns:
        Account data dict or None if fetch fails
    """
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                alt_address,
                {
                    "encoding": "base64",
                    "commitment": "confirmed"
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(rpc_url, json=payload) as response:
                data = await response.json()
                if "result" in data and data["result"] and "value" in data["result"]:
                    return data["result"]["value"]
                else:
                    logger.error(f"Failed to fetch ALT {alt_address}: {data}")
                    return None
                    
    except Exception as e:
        logger.error(f"Exception fetching ALT {alt_address}: {e}")
        return None


def build_alt_account(
    alt_address: str,
    account_data: Dict[str, Any]
) -> Optional[AddressLookupTableAccount]:
    """
    Build AddressLookupTableAccount from RPC account data.
    
    Args:
        alt_address: The ALT account address as string
        account_data: The account data from getAccountInfo
        
    Returns:
        AddressLookupTableAccount or None if build fails
    """
    try:
        # Parse the account data
        data_field = account_data.get("data")
        if not data_field:
            logger.error(f"No data field in ALT account {alt_address}")
            return None
        
        # Data is base64-encoded
        import base64
        if isinstance(data_field, list) and len(data_field) > 0:
            data_b64 = data_field[0]
        elif isinstance(data_field, str):
            data_b64 = data_field
        else:
            logger.error(f"Unexpected data format in ALT account {alt_address}")
            return None
        
        data_bytes = base64.b64decode(data_b64)
        
        # Parse ALT account data format
        # ALT account data structure:
        # - bytes 0-3: discriminator (should be 1 for initialized ALT)
        # - bytes 4-11: deactivation slot (u64)
        # - bytes 12-19: last extended slot (u64)
        # - bytes 20-51: authority (32 bytes pubkey)
        # - bytes 52+: addresses array
        
        if len(data_bytes) < 52:
            logger.error(f"ALT account data too short: {len(data_bytes)} bytes")
            return None
        
        # Skip header (52 bytes) and parse addresses
        # Each address is 32 bytes
        addresses_data = data_bytes[52:]
        num_addresses = len(addresses_data) // 32
        
        addresses = []
        for i in range(num_addresses):
            start = i * 32
            end = start + 32
            addr_bytes = addresses_data[start:end]
            try:
                pubkey = Pubkey(addr_bytes)
                addresses.append(pubkey)
            except Exception as e:
                logger.warning(f"Failed to parse address {i} in ALT: {e}")
                continue
        
        # Convert ALT address to Pubkey
        alt_pubkey = Pubkey.from_string(alt_address)
        
        # Create AddressLookupTableAccount
        alt_account = AddressLookupTableAccount(
            key=alt_pubkey,
            addresses=addresses
        )
        
        logger.info(f"Built ALT account with {len(addresses)} addresses")
        return alt_account
        
    except Exception as e:
        logger.error(f"Error building ALT account: {e}")
        return None
