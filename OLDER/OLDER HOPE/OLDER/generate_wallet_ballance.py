import os
from dotenv import load_dotenv
import aiohttp
import asyncio

load_dotenv()  # ⬅️ Load variables from .env into os.environ

HELIUS_RPC = os.getenv("HELIUS_RPC_URL")
wallet_pubkey = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"

async def get_balance():
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_pubkey]
        }
        async with session.post(HELIUS_RPC, json=payload) as resp:
            result = await resp.json()
            print("🔍 Raw RPC response:", result)

            if "result" in result:
                lamports = result["result"]["value"]
                print(f"💰 Wallet balance: {lamports / 1e9:.6f} SOL")
            else:
                print("❌ Error from RPC:", result.get("error"))

asyncio.run(get_balance())
