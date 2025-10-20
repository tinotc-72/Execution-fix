# Synchronous ALT Fetch Helpers Implementation

## Overview
This implementation adds synchronous Address Lookup Table (ALT) fetching utilities to complement the existing async ALT helpers. The new helpers use the `getAddressLookupTable` RPC method and the `requests` library for synchronous code paths.

## Problem Statement
The existing `utils/alts.py` provides async ALT helpers using `aiohttp` and `getAccountInfo` RPC. However:
- Some code paths may need synchronous ALT fetching
- The `getAddressLookupTable` RPC method is more direct for fetching ALT data
- Synchronous code may not be able to use async helpers

## Solution

### New Module: `utils/alt_fetch.py`

Created a new utility module with three main functions that follow the exact specification:

#### `rpc_call(rpc_url, method, params, timeout=10.0)`
- **Purpose**: Generic synchronous JSON-RPC call function
- **Input**: 
  - `rpc_url`: RPC endpoint URL
  - `method`: RPC method name
  - `params`: List of parameters
  - `timeout`: Request timeout in seconds (default: 10.0)
- **Library**: Uses `requests.post()`
- **Returns**: JSON-RPC response dictionary
- **Error Handling**: Raises `requests.exceptions.RequestException` on HTTP errors

#### `fetch_lookup_table(rpc_url, table_pubkey)`
- **Purpose**: Fetch addresses from an Address Lookup Table
- **Method**: Uses `getAddressLookupTable` RPC call (more direct than `getAccountInfo`)
- **Input**: 
  - `rpc_url`: RPC endpoint URL
  - `table_pubkey`: ALT address as string
- **Returns**: List of address strings; empty list if not found or on error
- **Error Handling**: Logs errors but returns empty list to allow graceful degradation

#### `build_alts_from_tables(rpc_url, table_pubkeys)`
- **Purpose**: Fetch multiple ALTs and build `AddressLookupTableAccount` objects
- **Input**:
  - `rpc_url`: RPC endpoint URL
  - `table_pubkeys`: List of ALT addresses as strings
- **Process**:
  1. Iterates through each ALT address
  2. Calls `fetch_lookup_table()` for each
  3. Converts string addresses to `Pubkey` objects
  4. Constructs `AddressLookupTableAccount(key, addresses)`
- **Returns**: `List[AddressLookupTableAccount]` ready for `MessageV0.try_compile()`
- **Error Handling**: Skips ALTs that fail to fetch or parse

## Key Differences from Async Helpers

| Feature | `utils/alts.py` (Async) | `utils/alt_fetch.py` (Sync) |
|---------|------------------------|----------------------------|
| Concurrency | `async`/`await` | Synchronous |
| HTTP Library | `aiohttp` | `requests` |
| RPC Method | `getAccountInfo` | `getAddressLookupTable` |
| Data Parsing | Manual binary parsing | RPC returns parsed addresses |
| Use Case | Async code paths | Sync code paths |

## Integration Guidance

### Detecting v0 Transactions
```python
# Check for Address Lookup Tables
address_table_lookups = message.get("addressTableLookups", [])

if address_table_lookups:
    # This is a v0 transaction
    pass
```

### Extracting ALT Addresses
```python
# Extract ALT addresses from message
table_pubkeys = [lookup["accountKey"] for lookup in address_table_lookups]
```

### Using Synchronous Helpers
```python
from utils.alt_fetch import build_alts_from_tables

# Fetch and build ALT accounts (synchronous)
alts = build_alts_from_tables(rpc_url, table_pubkeys)
```

### Using Async Helpers
```python
from utils.alts import alts_from_lookups

# Fetch and build ALT accounts (asynchronous)
alts = await alts_from_lookups(rpc_url, address_table_lookups)
```

### Building MessageV0 with ALTs
```python
from solders.message import MessageV0

if address_lookup_tables:
    # Use MessageV0 for v0 transactions
    new_message = MessageV0.try_compile(
        payer_pubkey,
        instructions,
        alts,  # Pass ALT accounts here
        recent_blockhash
    )
else:
    # Use legacy Message for non-v0 transactions
    new_message = Message.new_with_blockhash(
        instructions,
        payer_pubkey,
        recent_blockhash
    )
```

## Important Notes

### meta.loadedAddresses vs message.addressTableLookups
- **`meta.loadedAddresses`**: Contains the resolved account addresses that were loaded from ALTs
- **`message.addressTableLookups`**: Contains the ALT references (table addresses) needed for cloning
- **For cloning**: Always use `message.addressTableLookups`, NOT `meta.loadedAddresses`

### When to Use Which Helper
- **Use `utils/alt_fetch.py` (sync)**: 
  - Synchronous code paths
  - Non-async functions
  - Script/CLI tools
  
- **Use `utils/alts.py` (async)**: 
  - Async functions (e.g., `transaction_cloner.py`)
  - Event loops/coroutines
  - Async HTTP contexts

## Testing

### Test: `test_alt_fetch.py`
Validates the synchronous helpers:
- ✅ `rpc_call()` makes correct RPC requests
- ✅ `fetch_lookup_table()` fetches ALT addresses
- ✅ `build_alts_from_tables()` builds `AddressLookupTableAccount` objects
- ✅ ALT accounts are compatible with `MessageV0.try_compile()`
- ✅ Error handling works correctly (empty ALTs, invalid addresses, RPC errors)

### Demo: `demo_alt_fetch.py`
Demonstrates usage patterns:
- ✅ Basic ALT fetching
- ✅ Building AddressLookupTableAccount objects
- ✅ V0 transaction cloning workflow
- ✅ Recommended integration pattern

## Code Example

```python
from utils.alt_fetch import build_alts_from_tables
from solders.message import MessageV0, Message
from solders.transaction import VersionedTransaction

# 1. Parse transaction message
message = tx_data["transaction"]["message"]

# 2. Check for ALTs
address_table_lookups = message.get("addressTableLookups", [])
address_lookup_tables = []

if address_table_lookups:
    # 3. Extract ALT addresses
    table_pubkeys = [lookup["accountKey"] for lookup in address_table_lookups]
    
    # 4. Fetch and build ALT accounts (synchronous)
    address_lookup_tables = build_alts_from_tables(rpc_url, table_pubkeys)

# 5. Build message based on ALT presence
if address_lookup_tables:
    # Use MessageV0 for v0 transactions
    new_message = MessageV0.try_compile(
        payer_pubkey,
        instructions,
        address_lookup_tables,
        recent_blockhash
    )
else:
    # Use legacy Message for non-v0 transactions
    new_message = Message.new_with_blockhash(
        instructions,
        payer_pubkey,
        recent_blockhash
    )

# 6. Create and sign transaction
tx = VersionedTransaction(message=new_message, keypairs=[payer])
```

## Files Added

1. `utils/alt_fetch.py` - New file with synchronous ALT helpers
2. `test_alt_fetch.py` - New test file
3. `demo_alt_fetch.py` - New demonstration script
4. `ALT_FETCH_IMPLEMENTATION.md` - This documentation

## Existing Integration

The repository already has ALT support via `utils/alts.py`:
- `transaction_cloner.py` uses async `alts_from_lookups()` 
- V0 transactions are properly detected and handled
- `MessageV0.try_compile()` is used with ALTs
- Legacy transactions fall back to `Message.new_with_blockhash()`

The new synchronous helpers complement this existing implementation.

## Definition of Done

✅ **ALT fetch helpers exist in `utils/alt_fetch.py`**
- `rpc_call()` - Generic RPC call function
- `fetch_lookup_table()` - Fetch ALT addresses via `getAddressLookupTable`
- `build_alts_from_tables()` - Build `AddressLookupTableAccount` objects

✅ **Integration guidance provided**
- Documented in `utils/alt_fetch.py` module docstring
- Demo script showing usage patterns
- Clear notes on when to use sync vs async helpers

✅ **Clone/submit paths reference ALTs correctly**
- Existing `transaction_cloner.py` already uses async ALT helpers
- Synchronous helpers available for sync code paths
- Documentation clarifies `meta.loadedAddresses` vs `message.addressTableLookups`

✅ **Tests validate functionality**
- All functions tested with mock data
- Integration with `MessageV0` validated
- Error handling verified

## Summary

This implementation adds synchronous ALT fetching utilities using the `getAddressLookupTable` RPC method and `requests` library. These helpers complement the existing async utilities and follow the exact specification in the problem statement. The implementation includes comprehensive tests, demonstration scripts, and integration guidance for clone/submit paths.
