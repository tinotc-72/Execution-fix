import asyncio
import aiohttp

async def inspect_account(pubkey: str):
    url = "https://api.mainnet-beta.solana.com"  # You can also use your Helius URL here
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            pubkey,
            {
                "encoding": "jsonParsed",
                "commitment": "confirmed"
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            print("\n🔍 Raw account info:")
            print(data)

async def main():
    await inspect_account("9heeb6JBHFB48jz7pV7umHpG3aKD6KibV4fVq2vJHPsq")

if __name__ == "__main__":
    asyncio.run(main())
