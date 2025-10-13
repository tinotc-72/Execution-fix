import requests
import json
import base58
import base64

# Transaction with successful PUMP buy
TX_SIG = "48Yp8uU4Gj2CtsWXQ1ZvgYxocANqtGuXWUkFJvUfAussrjxHk5AiULgVW19Hx1RPv2yLnGRdxzNHFxjeyWDCFwfs"

def get_tx_data():
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            TX_SIG,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

print("\nFetching transaction data...")
result = get_tx_data()

if "result" not in result or not result["result"]:
    print("Failed to fetch transaction")
    exit(1)

tx_data = result["result"]

# Extract PUMP router instruction
print("\nPUMP Router Instruction Details:")
print("=" * 50)

# Find the PUMP router instruction
pump_ix = None
for ix in tx_data["transaction"]["message"]["instructions"]:
    if "programId" in ix and ix["programId"] == "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW":
        pump_ix = ix
        break

if pump_ix:
    print("\nProgram: PUMP Router")
    print("\nAccounts in order:")
    account_keys = tx_data["transaction"]["message"]["accountKeys"]
    
    for i, acc_idx in enumerate(pump_ix["accounts"]):
        acc = account_keys[acc_idx]
        print(f"{i}: {acc['pubkey']}")
        if acc.get("signer", False):
            print("   [signer]")
        if acc.get("writable", False):
            print("   [writable]")
    
    # Extract key accounts we need
    route_params = account_keys[pump_ix["accounts"][1]]["pubkey"]
    route_state = account_keys[pump_ix["accounts"][2]]["pubkey"]
    token_mint = account_keys[pump_ix["accounts"][3]]["pubkey"]
    wsol_vault = account_keys[pump_ix["accounts"][4]]["pubkey"]
    token_vault = account_keys[pump_ix["accounts"][5]]["pubkey"]
    
    print("\nKey Accounts for Trading:")
    print(f"Route Params:  {route_params}")
    print(f"Route State:   {route_state}")
    print(f"Token Mint:    {token_mint}")
    print(f"WSOL Vault:    {wsol_vault}")
    print(f"Token Vault:   {token_vault}")
    
    print("\nInstruction Data:")
    data = base58.b58decode(pump_ix["data"])
    print(f"Raw (hex): {data.hex()}")
    print(f"Discriminator: {data[:8].hex()}")

# Print logs
print("\nTransaction Logs:")
print("=" * 50)
for log in tx_data["meta"]["logMessages"]:
    if "Program BSfD6SHZ" in log or "PumpBuy" in log or "bonding_curve" in log:
        print(log)
