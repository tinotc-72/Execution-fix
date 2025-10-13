# File: generate_solscan_data.py

import requests

TX_SIG = "2EuwsAQmNNVG2TbhRZBVkkABWU45KEet8Yfuz2PUJ1bZxRX8Rwuv2tJdQ6ffGwwKZiRUingxubpou2Eu9edgduT5"
RPC_URL = "https://api.mainnet-beta.solana.com"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTransaction",
    "params": [
        TX_SIG,
        {
            "encoding": "base64",
            "maxSupportedTransactionVersion": 0
        }
    ]
}

response = requests.post(RPC_URL, json=payload)
result = response.json()

transaction_field = result.get("result", {}).get("transaction")

if isinstance(transaction_field, list):
    raw_tx_base64 = transaction_field[0]  # Base64 string
    print("Raw transaction data (base64):", raw_tx_base64)
else:
    print("Unexpected transaction format:", transaction_field)
