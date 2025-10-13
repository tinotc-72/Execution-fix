"""
Analyze a working BONK trade on mainnet to extract instruction format.
"""
import asyncio
import aiohttp
import base64
import json
from solders.pubkey import Pubkey

# Transaction to analyze (successful BONK trade)
TX_SIG = "4E3uiNLGfcHqh4kqokRcxNVHNqsJ8mXG9rYhNVqYRLa5wbXjmMjG3KuCXFqvjvxxapD7jD3KxSZDEGc5TK6kySXe"

async def analyze_tx():
    """Analyze transaction instruction data"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://mainnet.helius-rpc.com/?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    TX_SIG,
                    {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
                ]
            }
        ) as response:
            data = await response.json()
            
            print("\n=== Transaction Analysis ===")
            
            # Get the main instruction (index 2 after compute budget)
            ix = data["result"]["transaction"]["message"]["instructions"][2]
            
            # Print instruction data
            print("\nInstruction Data (base64):")
            print(ix["data"])
            
            # Decode and analyze instruction data
            raw_data = base64.b64decode(ix["data"])
            print("\nInstruction Data (hex):")
            print(raw_data.hex())
            
            # Print account order
            print("\nAccount Order:")
            for idx, acc in enumerate(ix["accounts"]):
                addr = Pubkey.from_string(acc)
                print(f"{idx}: {addr}")

if __name__ == "__main__":
    asyncio.run(analyze_tx())
