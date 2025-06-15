# listener.py

import asyncio
import base64
import json
import websockets
import aiohttp
import keyZ as kz

# === CONFIG ===
WALLET_A_ADDRESS = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
HELIUS_WS_URL = kz.HELIUS_Standard_Websocket_URL
HELIUS_RPC_URL = kz.HELIUS_RPC_URL


async def fetch_transaction(signature: str) -> dict | None:
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "base64",  # ✅ THIS IS THE CORRECT FORMAT
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        async with session.post(HELIUS_RPC_URL, json=payload) as resp:
            print(f"🌐 Request to getTransaction for {signature}")
            if resp.status == 200:
                res = await resp.json()
                if not res.get("result"):
                    print("❌ No result in RPC response:", json.dumps(res, indent=2))
                    return None
                return res["result"]
            else:
                print(f"❌ Failed fetch: HTTP {resp.status}")
                try:
                    error = await resp.text()
                    print("❌ RPC error message:", error)
                except:
                    pass
                return None


def extract_mint_from_transaction(tx: dict) -> str | None:
    try:
        inner_instructions = tx["meta"]["innerInstructions"]
        for group in inner_instructions:
            for instr in group.get("instructions", []):
                if instr["program"] == "spl-token":
                    accounts = instr.get("parsed", {}).get("info", {})
                    mint = accounts.get("mint")
                    if mint:
                        print(f"✅ Mint found in inner instruction: {mint}")
                        return mint
        return None
    except Exception as e:
        print(f"⚠️ Could not extract mint from transaction: {e}")
        return None


async def listen_to_wallet_a(callback):
    print("🧪 Callback passed to listener:", callback)
    print("🧪 Callback type:", type(callback))
    print(f"📡 Starting bot – mirroring Wallet A: {WALLET_A_ADDRESS}")

    while True:
        try:
            async with websockets.connect(HELIUS_WS_URL) as ws:
                await ws.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [WALLET_A_ADDRESS]},
                        {"commitment": "finalized"}
                    ]
                }))

                print("✅ Subscribed to Wallet A activity...")

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    result = data.get("params", {}).get("result", {})
                    logs = result.get("value", {}).get("logs", [])
                    sig = result.get("value", {}).get("signature")

                    if not logs or not sig:
                        continue  # Skip irrelevant messages

                    print("🔍 Fetching transaction:", sig)
                    tx_data = await fetch_transaction(sig)
                    if not tx_data:
                        print("❌ Failed to fetch tx_data.")
                        continue

                    print("🧠 Full logs received:")
                    for log in tx_data.get("meta", {}).get("logMessages", []):
                        print("    ", log)

                    # Extract mint
                    from log_utils import extract_mint_from_logs
                    mint = extract_mint_from_logs(logs)

                    trade_keywords = ["Swap", "Buy", "Sell", "PumpAmmSwap", "SwapBaseInput", "SwapBaseOutput", "SwapExactInput", "SwapExactOutput"]
                    if any(any(kw in log for kw in trade_keywords) for log in logs):
                        print("🔥 Detected trade instruction — triggering replicator")
                        try:
                            await callback(tx_data, logs, mint, sig)
                        except Exception as e:
                            print("❌ ERROR during handle_trade callback execution:")
                            import traceback
                            traceback.print_exc()
                    else:
                        print("🛑 Ignored non-trade transaction")

        except Exception as e:
            print(f"⚠️ Listener error: {e}")
            print("🔁 Reconnecting in 2s...")
            await asyncio.sleep(2)
