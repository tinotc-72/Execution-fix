import requests

WALLET = "CzDin6HGmxMQaRNBk6RxGcDgNosErrqYB2bF6pwAMGB6"
RPC_URL = "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTokenAccountsByOwner",
    "params": [
        WALLET,
        {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"encoding": "jsonParsed"}
    ]
}

resp = requests.post(RPC_URL, json=payload)
accounts = resp.json()["result"]["value"]

if not accounts:
    print("❌ No token accounts found (you likely don't hold any tokens right now).")
else:
    print(f"✅ Found {len(accounts)} token account(s):")
    for acc in accounts:
        info = acc["account"]["data"]["parsed"]["info"]
        mint = info["mint"]
        amount = int(info["tokenAmount"]["amount"]) / (10 ** int(info["tokenAmount"]["decimals"]))
        print(f"- Mint: {mint}, Amount: {amount}")
