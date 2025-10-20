"""
utils/alt_fetch.py

Synchronous Address Lookup Table (ALT) fetching utilities using requests library.
These helpers use the getAddressLookupTable RPC method to fetch ALT data.

INTEGRATION GUIDANCE:
--------------------

For cloned v0 transactions, ALT data must be fetched and passed to MessageV0 construction.

1. Detecting v0 transactions:
   Check if transaction.message contains "addressTableLookups" field.

2. Extracting ALT addresses:
   Get the list of table addresses from message.addressTableLookups:
   ```python
   address_table_lookups = message.get("addressTableLookups", [])
   table_pubkeys = [lookup["accountKey"] for lookup in address_table_lookups]
   ```

3. Fetching and building ALT accounts:
   ```python
   from utils.alt_fetch import build_alts_from_tables
   
   alts = build_alts_from_tables(rpc_url, table_pubkeys)
   ```

4. Using with MessageV0:
   ```python
   from solders.message import MessageV0
   
   new_message = MessageV0.try_compile(
       payer_pubkey,
       instructions,
       alts,  # Pass the ALT accounts here
       recent_blockhash
   )
   ```

For async code paths, use utils.alts.alts_from_lookups() instead:
```python
from utils.alts import alts_from_lookups

alts = await alts_from_lookups(rpc_url, address_table_lookups)
```

NOTE: meta.loadedAddresses contains the resolved addresses, not the ALT references.
      Always use message.addressTableLookups to get the actual ALT addresses.
"""
from __future__ import annotations
import logging
import requests
from typing import List, Dict, Any
from solders.pubkey import Pubkey
from solders.address_lookup_table_account import AddressLookupTableAccount

logger = logging.getLogger(__name__)


def rpc_call(rpc_url: str, method: str, params: List[Any], timeout: float = 10.0) -> dict:
    """
    Make a synchronous JSON-RPC call to Solana RPC.
    
    Args:
        rpc_url: RPC endpoint URL
        method: RPC method name
        params: List of parameters for the RPC method
        timeout: Request timeout in seconds
        
    Returns:
        JSON-RPC response as dictionary
        
    Raises:
        requests.exceptions.RequestException: If the HTTP request fails
    """
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    r = requests.post(rpc_url, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_lookup_table(rpc_url: str, table_pubkey: str) -> List[str]:
    """
    Fetch addresses from an Address Lookup Table via getAddressLookupTable RPC call.
    
    Args:
        rpc_url: RPC endpoint URL
        table_pubkey: The lookup table address as a string
        
    Returns:
        List of address strings in the table; empty list if not found or error occurs
    """
    try:
        resp = rpc_call(rpc_url, "getAddressLookupTable", [table_pubkey])
        value = (resp.get("result") or {}).get("value")
        if not value:
            return []
        addrs = value.get("addresses") or []
        return addrs
    except Exception as e:
        # Log error but return empty list to allow caller to handle gracefully
        logger.error(f"Failed to fetch lookup table {table_pubkey}: {e}")
        return []


def build_alts_from_tables(rpc_url: str, table_pubkeys: List[str]) -> List[AddressLookupTableAccount]:
    """
    Fetch multiple Address Lookup Tables and build AddressLookupTableAccount objects.
    
    Args:
        rpc_url: RPC endpoint URL
        table_pubkeys: List of ALT addresses as strings
        
    Returns:
        List of AddressLookupTableAccount objects for use with MessageV0.try_compile()
    """
    alts: List[AddressLookupTableAccount] = []
    for tbl in table_pubkeys:
        addrs = fetch_lookup_table(rpc_url, tbl)
        if not addrs:
            continue
        try:
            # Convert string addresses to Pubkey objects
            alt_key = Pubkey.from_string(tbl)
            address_pubkeys = [Pubkey.from_string(a) for a in addrs]
            
            # Create AddressLookupTableAccount
            alt_account = AddressLookupTableAccount(key=alt_key, addresses=address_pubkeys)
            alts.append(alt_account)
        except Exception as e:
            logger.error(f"Failed to build ALT account for {tbl}: {e}")
            continue
    
    return alts
