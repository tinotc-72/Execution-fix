import asyncio
from listener import fetch_transaction, handle_trade

TX_SIG = "5QzEXs4Wgae4KcydEAAqhsm7VwQeZWprrAdgo5Gth6FXeumh6xkd5p7CCjPPMFaagzNzsvfmfpKa1WXmBcaDwMWQ"

async def test():
    tx_data = await fetch_transaction(TX_SIG)
    if not tx_data:
        print("Failed to fetch transaction")
        return
    logs = tx_data.get("meta", {}).get("logMessages", [])
    mint = tx_data.get("meta", {}).get("postTokenBalances", [{}])[-1].get("mint")
    await handle_trade(tx_data, logs, mint, TX_SIG)

asyncio.run(test())
