import requests
import base64
from solders.transaction import VersionedTransaction
from solders.pubkey import Pubkey

RPC_URL = "https://api.mainnet-beta.solana.com"
TX_SIG = "igY6NJB1KDq3dC4xuxUcd6RMy7DE6EGRfEbDhyi2NhaQi1PdSJdeoXKWAoDv2BfwSjsFsKgpEtmQLTHrtQkSA3S"

def fetch_and_decode_tx(signature: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "base64",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    response = requests.post(RPC_URL, json=payload)
    result = response.json()
    
    if "result" not in result or result["result"] is None:
        print("Transaction not found or empty result")
        return
    
    raw_tx_base64 = result["result"]["transaction"][0]
    raw_tx_bytes = base64.b64decode(raw_tx_base64)
    
    versioned_tx = VersionedTransaction.from_bytes(raw_tx_bytes)
    message = versioned_tx.message
    
    # Extract ALT accounts from meta.loadedAddresses
    meta = result["result"].get("meta", {})
    loaded_addresses = []
    
    # writable and readonly addresses from loadedAddresses
    loaded_writable = meta.get("loadedAddresses", {}).get("writable", [])
    loaded_readonly = meta.get("loadedAddresses", {}).get("readonly", [])
    
    # Convert all loaded addresses to Pubkey
    loaded_addresses.extend([Pubkey.from_string(addr) for addr in loaded_writable])
    loaded_addresses.extend([Pubkey.from_string(addr) for addr in loaded_readonly])
    
    # Combine base account keys + loadedAddresses (ALTs)
    full_account_keys = list(message.account_keys) + loaded_addresses
    
    print("\n=== Account Keys ===")
    for i, pk in enumerate(full_account_keys):
        print(f"{i}: {pk}")
    
    print("\n=== Instructions ===")
    for i, ix in enumerate(message.instructions):
        # Resolve program id safely
        try:
            program_id = full_account_keys[ix.program_id_index]
        except IndexError:
            print(f"Warning: instruction {i} program_id_index {ix.program_id_index} out of range")
            program_id = "<Invalid>"
        
        # Resolve accounts safely with warnings
        accounts = []
        for a in ix.accounts:
            if a < len(full_account_keys):
                accounts.append(full_account_keys[a])
            else:
                accounts.append(f"<Invalid index {a}>")
                print(f"Warning: instruction {i} account index {a} out of range")
        
        data_hex = ix.data.hex()
        
        print(f"\nInstruction {i}:")
        print(f"  Program ID: {program_id}")
        print(f"  Accounts ({len(accounts)}):")
        for acc in accounts:
            print(f"    {acc}")
        print(f"  Data (hex): {data_hex}")
        print(f"  Data length: {len(ix.data)}")

if __name__ == "__main__":
    fetch_and_decode_tx(TX_SIG)
