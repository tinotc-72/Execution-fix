import requests

signature = "3pH89QetQ2BhiWMjX2a5a9kEcngU3UGDMLMBVX7muWrBrnAGD51eHPiPJ6dCEYAUJpWp1YsPDHEqGcqUonRqt1NJ"
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTransaction",
    "params": [
        signature,
        {
            "encoding": "jsonParsed",
            "maxSupportedTransactionVersion": 0
        }
    ]
}
resp = requests.post("https://api.mainnet-beta.solana.com", json=payload)
print(resp.json())