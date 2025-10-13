
import sys
import base64
import requests
import json
from env_keys import EnvKeys

# Use the RPC URL from .env via EnvKeys
env = EnvKeys()
RPC_URL = env.HELIUS_RPC_URL
PUMPFUN_PROGRAM_IDS = [
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
]

def fetch_tx(sig):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
    }
    resp = requests.post(RPC_URL, json=payload)
    resp.raise_for_status()
    return resp.json()["result"]

def print_instruction(ix, idx, account_keys):
    print(f"\n=== Instruction {idx+1} ===")
    print(f"Program: {ix['programId']}")
    print(f"Program Name: {ix.get('program', 'UNKNOWN')}")
    print(f"Data (base64): {ix.get('data', '')}")
    try:
        data_bytes = base64.b64decode(ix.get('data', ''))
        print(f"Data (hex): {data_bytes.hex()}")
    except Exception:
        pass
    if 'accounts' in ix:
        print("Accounts:")
        for i, acc_idx in enumerate(ix['accounts']):
            acc = account_keys[acc_idx] if isinstance(acc_idx, int) else acc_idx
            print(f"  [{i}] {acc}")
    else:
        print("Accounts: (none listed)")

def main():
    if len(sys.argv) < 2:
        sig = input("Enter Solana transaction signature: ").strip()
        if not sig:
            print("No signature provided. Exiting.")
            sys.exit(1)
    else:
        sig = sys.argv[1]
    tx = fetch_tx(sig)
    print(f"Signature: {sig}")
    print(f"Slot: {tx['slot']}")
    print(f"Block Time: {tx.get('blockTime')}")
    print(f"\n--- Instructions ---")
    message = tx['transaction']['message']
    account_keys = message['accountKeys']
    for idx, ix in enumerate(message['instructions']):
        print_instruction(ix, idx, account_keys)
    print("\n--- Logs ---")
    for log in tx['meta']['logMessages']:
        print(log)

if __name__ == "__main__":
    main()
