"""
Script to scan a wallet's recent transactions and summarize trade patterns for tailored copy trading.
"""
import asyncio
from utils import get_transaction_with_logs

from solders.pubkey import Pubkey

async def fetch_and_summarize(wallet_address: str, signatures: list[str]):
    print(f"\n=== Trade Pattern Summary for {wallet_address} ===\n")
    for sig in signatures:
        tx = await get_transaction_with_logs(sig)
        if not tx:
            print(f"❌ Could not fetch transaction {sig}")
            continue
        msg = tx['transaction']['message']
        print(f"Signature: {sig}")
        print(f"  Recent Blockhash: {msg.get('recentBlockhash')}")
        print(f"  Account Keys: {msg['accountKeys']}")
        print(f"  Instructions:")
        for ix in msg['instructions']:
            prog_id_idx = ix['programIdIndex']
            prog_id = msg['accountKeys'][prog_id_idx]
            print(f"    - Program: {prog_id}")
            # Safely print account keys, handling out-of-range indices
            account_keys = []
            for i in ix['accounts']:
                if 0 <= i < len(msg['accountKeys']):
                    account_keys.append(msg['accountKeys'][i])
                else:
                    account_keys.append(f"<Invalid index {i}>")
            print(f"      Accounts: {account_keys}")
            print(f"      Data (base58): {ix['data']}")
        print(f"  Logs: {tx['meta'].get('logMessages', [])}")
        print()

if __name__ == "__main__":
    # Default: use provided wallet and signatures
    wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
    sigs = [
        # sell
        "3NftLiijmGPvb5Q75KCcC6UWVYty5pkpSeRjnG6272RUSzPau9bNBPMKgnMRqfZSxEQ2FFXeGN51L53hGhGDwHy6",
        # buy
        "3pH89QetQ2BhiWMjX2a5a9kEcngU3UGDMLMBVX7muWrBrnAGD51eHPiPJ6dCEYAUJpWp1YsPDHEqGcqUonRqt1NJ",
        # buy
        "5NPdhAzdMWhWyPMbGDUh8hqbLp5b8ivcXwqmHuM6eVZJ9dQ7KV2sw8ytfjXg1hBHeRiZy5NMtTQKUmwZCDrAGny3",
        # sell
        "5BTuEm1WK71wuuPD4BkYTAxFgNJ9UhGVkn1LNcW2YhLSthp1csLfz47RwGfPs7AZrHAbc16QMJ8VqDDvGAdYsSoN",
        # buy
        "VC7B3vJFTndNX7LrqXetcLhcc6eG8Cgm17GuWmaDiLWdmNAFnMYtehqWZKQozd6ufw33pobL9NosKpNJYtkKCDj",
        # sell
        "BN8t4dVLJGFU4WFcLirD2SfoRTwNKGrbSTUz2gwzb2Zo1S5sVXCAaYXG7oFBkeBCokgrRiBUm5gE6UJgFfmmb9K"
    ]
    asyncio.run(fetch_and_summarize(wallet, sigs))
