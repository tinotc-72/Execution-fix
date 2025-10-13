def extract_launchlab_buy_params(tx):
    """
    Extracts all required accounts and instruction data for a Raydium LaunchLab BuyExactIn from a transaction dict.
    Returns a dict of parameters to pass to try_raydium_launchlab_buy.
    """
    # Find the LaunchLab instruction
    instructions = tx["transaction"]["message"]["instructions"]
    account_keys = tx["transaction"]["message"]["accountKeys"]
    for ix in instructions:
        if ix["programId"] == "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj":
            accounts = ix["accounts"]
            # Map account indices to pubkeys
            pubkeys = [account_keys[a]["pubkey"] if isinstance(account_keys[a], dict) else account_keys[a] for a in accounts]
            # Instruction data (base64 or hex)
            data = ix.get("data")
            if isinstance(data, list):
                encoding, raw = data
                decoded = base64.b64decode(raw)
            elif isinstance(data, str):
                decoded = base64.b64decode(data)
            else:
                decoded = b""
            # Unpack instruction data: amount_in (u64), min_out (u64), share_fee_rate (u64)
            import struct
            if len(decoded) >= 24:
                amount_in, min_out, share_fee_rate = struct.unpack("<QQQ", decoded[:24])
            else:
                amount_in = min_out = share_fee_rate = 0
            return {
                "payer": pubkeys[0],
                "authority": pubkeys[1],
                "global_config": pubkeys[2],
                "platform_config": pubkeys[3],
                "pool_state": pubkeys[4],
                "user_base_token": pubkeys[5],
                "user_quote_token": pubkeys[6],
                "base_vault": pubkeys[7],
                "quote_vault": pubkeys[8],
                "base_token_mint": pubkeys[9],
                "quote_token_mint": pubkeys[10],
                "base_token_program": pubkeys[11],
                "quote_token_program": pubkeys[12],
                "event_authority": pubkeys[13],
                "amount_in": amount_in,
                "minimum_amount_out": min_out,
                "share_fee_rate": share_fee_rate
            }
    return None
def demo_launchlab_executor(sig):
    """
    Demo: Extract params from a LaunchLab buy and show how to call the executor.
    """
    tx = fetch_transaction(sig)
    if not tx:
        print("❌ Transaction not found.")
        return
    params = extract_launchlab_buy_params(tx)
    if not params:
        print("❌ No LaunchLab instruction found.")
        return
    print("\n✅ Extracted LaunchLab buy params:")
    for k, v in params.items():
        print(f"  {k}: {v}")
    print("\n# Example call:")
    print("result = await try_raydium_launchlab_buy(wallet_keypair, ")
    for k, v in params.items():
        print(f"    {k}={repr(v)},")
    print(")")
# 1_analyze_tx.py - A script to analyze Solana transactions by fetching details from the Helius RPC API.
#  It decodes and displays transaction instructions, account information, and logs.

import requests
import base64
import json
from solders.pubkey import Pubkey
from env_keys import EnvKeys

# Initialize environment and get RPC URL
env = EnvKeys()
RPC_URL = env.HELIUS_RPC_URL

# Known program IDs
PROGRAM_LABELS = {
    "PUMP_FUN_PROGRAM": "6UeJ1dSDyZ6XtWqUVeuW5tka4UzyKkHcKcCj6jy3BwF6",
    "JUPITER_AGGREGATOR": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
    "RAYDIUM_AMM": "RVKd61ztZW9nRkG2Z3C7yfFCXf1FZr4dq6n3Gd6zLRt",
    "ORCA_WHIRLPOOL": "whirLb6F9rFKksSmHNuE52Tz3tDGC5nHz9QeVq2cL7c",
    "MANGO": "4MEXDugYf64RTPnBdbTQ1TYatEJfLtxSDJd1cX1HKiBM",
    "CLMM_PROGRAM": "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK"
}

def fetch_transaction(signature: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0,
                "commitment": "confirmed"
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(RPC_URL, headers=headers, json=payload).json()
    return res.get("result", None)

def analyze_instruction(ix, account_keys):
    program_id = ix["programId"]
    label = next((k for k, v in PROGRAM_LABELS.items() if v == program_id), "UNKNOWN")
    
    print(f"\n📦 Program: {label} ({program_id})")
    print(f"🔢 Instruction Type: {ix.get('parsed', {}).get('type', 'raw')}")
    
    print("👥 Accounts:")
    accounts = ix.get("accounts", [])
    
    # Create a lookup of pubkeys to their metadata
    account_lookup = {}
    for acc in account_keys:
        if isinstance(acc, dict):
            pubkey = acc.get("pubkey")
            if pubkey:
                account_lookup[pubkey] = acc
        else:
            account_lookup[str(acc)] = {"pubkey": str(acc), "signer": False, "writable": False}

    for i, acc_ref in enumerate(accounts):
        # Handle both index-based and direct pubkey references
        if isinstance(acc_ref, (int, str)):
            if str(acc_ref) in account_lookup:
                # Direct pubkey reference
                acc_info = account_lookup[str(acc_ref)]
            else:
                # Try as index
                try:
                    idx = int(acc_ref)
                    acc_info = account_keys[idx] if isinstance(account_keys[idx], dict) else {"pubkey": str(account_keys[idx]), "signer": False, "writable": False}
                except (ValueError, IndexError):
                    acc_info = {"pubkey": str(acc_ref), "signer": False, "writable": False}
        
        pubkey = acc_info.get("pubkey", str(acc_info))
        signer = acc_info.get("signer", False)
        writable = acc_info.get("writable", False)
        print(f"  [{i}] {pubkey} | Signer: {signer} | Writable: {writable}")

    # Show raw data
    if "data" in ix:
        data = ix["data"]
        if isinstance(data, list):
            encoding, raw = data
            print(f"📨 Raw Data ({encoding}): {raw}")
            try:
                decoded = base64.b64decode(raw)
                print(f"    Hex: {decoded.hex()}")
            except Exception:
                print("    ⚠️ Failed to decode data")
        elif isinstance(data, str):
            print(f"📨 Raw Data: {data}")
        else:
            print("📨 Raw Data: [unknown format]")

def analyze_transaction(sig: str):
    print(f"\n🔍 Analyzing transaction: {sig}")
    tx = fetch_transaction(sig)
    if tx is None:
        print("❌ Transaction not found or invalid.")
        return

    account_keys = tx["transaction"]["message"]["accountKeys"]
    instructions = tx["transaction"]["message"]["instructions"]
    meta = tx.get("meta", {})
    logs = meta.get("logMessages", [])

    print(f"\n✅ Found {len(instructions)} instruction(s)")
    for i, ix in enumerate(instructions):
        print(f"\n=== Instruction {i + 1} ===")
        analyze_instruction(ix, account_keys)

    print("\n📜 Logs:")
    for log in logs:
        print("  " + log)

if __name__ == "__main__":
    # Example usage: analyze or extract LaunchLab params
    SIG = input("Enter a Solana transaction signature: ").strip()
    analyze_transaction(SIG)
    print("\n---\n")
    demo_launchlab_executor(SIG)
