# mev_router_account_resolver.py
"""
Fetches all account addresses (including address lookup table entries) for a given Solana transaction signature.
Prints the full ordered list of accounts for any instruction, ready for use in a bot or transaction builder.

Usage:
    python3 mev_router_account_resolver.py <TRANSACTION_SIGNATURE>
"""

import sys
import base64
import asyncio
from solana.rpc.async_api import AsyncClient
try:
    from solana.publickey import PublicKey
except ImportError:
    from solders.pubkey import Pubkey as PublicKey

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mev_router_account_resolver.py <TRANSACTION_SIGNATURE>")
        return
    sig = sys.argv[1]
    from solders.signature import Signature
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    sig_obj = Signature.from_string(sig)
    resp = await client.get_transaction(sig_obj, encoding="json", max_supported_transaction_version=0)
    if resp.value is None:
        print("No transaction found for this signature.")
        await client.close()
        return
    tx = resp.value
    print("DEBUG: tx.value type:", type(tx))
    print("DEBUG: tx.value dir:", dir(tx))
    # Extract message from nested structure
    msg = tx.transaction.transaction.message
    # account_keys is a list of Pubkey objects
    account_keys = [str(k) for k in msg.account_keys]
    # Get address table lookups
    import base64
    import aiohttp
    lookups = getattr(msg, 'address_table_lookups', [])
    lookup_addresses = []
    async def fetch_lookup_table_addresses(table_addr):
        # Use raw RPC call to fetch and decode lookup table
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [table_addr, {"encoding": "base64"}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=headers) as resp:
                data = await resp.json()
                value = data.get("result", {}).get("value", {})
                if not value:
                    return []
                raw_data = value.get("data", [None])[0]
                if not raw_data:
                    return []
                decoded = base64.b64decode(raw_data)
                # ALT layout: https://docs.solanalabs.com/runtime/address-lookup-table#serialization
                # Skip 4 bytes (discriminator), then 32 bytes (authority), then 8 bytes (last extended slot), then 4 bytes (length)
                if len(decoded) < 48:
                    return []
                num_addresses = int.from_bytes(decoded[44:48], "little")
                addresses = []
                offset = 48
                for i in range(num_addresses):
                    addr = decoded[offset:offset+32]
                    if len(addr) != 32:
                        print(f"ALT decode warning: address {i} slice is {len(addr)} bytes, skipping.")
                        break
                    addresses.append(str(PublicKey(addr)))
                    offset += 32
                return addresses

    if lookups:
        for lookup in lookups:
            table_addr = str(lookup.account_key)
            table_addrs = await fetch_lookup_table_addresses(table_addr)
            # Order: first all writable, then all readonly
            writable = [table_addrs[i] for i in lookup.writable_indexes] if table_addrs else []
            readonly = [table_addrs[i] for i in lookup.readonly_indexes] if table_addrs else []
            lookup_addresses.extend(writable + readonly)
    # Build full account list
    full_accounts = account_keys + lookup_addresses
    print(f"\nFull ordered account list for transaction {sig}:")
    for i, addr in enumerate(full_accounts):
        print(f"  [{i}] {addr}")
    # Print all instructions and their account indices
    print("\nInstructions and account indices:")
    for idx, inst in enumerate(msg.instructions):
        prog = full_accounts[inst.program_id_index]
        print(f"Instruction {idx} (program: {prog}):")
        print(f"  Account indices: {list(inst.accounts)}")
        print(f"  Data (base64): {inst.data}")
    # Get address table lookups
    lookups = getattr(msg, 'address_table_lookups', [])
    lookup_addresses = []
    for lookup in lookups:
        table_addr = str(lookup.account_key)
        table_resp = await client.get_address_lookup_table(table_addr)
        table_value = table_resp['result']['value']
        if not table_value:
            continue
        table_addrs = table_value['addresses']
        # Order: first all writable, then all readonly
        writable = [table_addrs[i] for i in lookup.writable_indexes]
        readonly = [table_addrs[i] for i in lookup.readonly_indexes]
        lookup_addresses.extend(writable + readonly)
    # Build full account list
    full_accounts = account_keys + lookup_addresses
    print(f"\nFull ordered account list for transaction {sig}:")
    for i, addr in enumerate(full_accounts):
        print(f"  [{i}] {addr}")
    # Print all instructions and their account indices
    print("\nInstructions and account indices:")
    for idx, inst in enumerate(msg.instructions):
        prog = full_accounts[inst.program_id_index]
        print(f"Instruction {idx} (program: {prog}):")
        print(f"  Account indices: {list(inst.accounts)}")
        print(f"  Data (base64): {inst.data}")
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
