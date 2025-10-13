import requests
import json

TX_SIG = "48Yp8uU4Gj2CtsWXQ1ZvgYxocANqtGuXWUkFJvUfAussrjxHk5AiULgVW19Hx1RPv2yLnGRdxzNHFxjeyWDCFwfs"

url = "https://api.mainnet-beta.solana.com"
headers = {"Content-Type": "application/json"}
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTransaction",
    "params": [
        TX_SIG,
        {
            "encoding": "json",
            "maxSupportedTransactionVersion": 0
        }
    ]
}

resp = requests.post(url, json=payload, headers=headers)
result = resp.json()

with open("pump_tx.json", "w") as f:
    json.dump(result, f, indent=2)

print("Wrote pump_tx.json")
