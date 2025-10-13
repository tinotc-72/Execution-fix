# listener.py

__all__ = [
    'HELIUS_RPC_URL',
    'identify_dex_and_instruction',
    'extract_trade_data',
    'extract_token_info',
    'listen_to_wallets',
    'handle_trade'
]

import asyncio
import base64
import json
import websockets
import aiohttp
from env_keys import kz

# === CONFIG ===
from config import MONITORED_WALLETS
HELIUS_WS_URL = kz.HELIUS_Standard_Websocket_URL
HELIUS_RPC_URL = kz.HELIUS_RPC_URL

# Known DEX Program IDs
DEX_PROGRAMS = {
    "PUMP": "GDDMwNyyx8uB6zrqwBFHjLLG3TBYk2F8Az4yrQC5RzMp",  # ✅ Correct Pump router
    "PUMP_NEW": "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95",  # ✅ New Pump program detected
    "PUMP_ROUTER": "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # ✅ Router program from logs
    "PUMP_TRADING": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # ✅ Trading program from logs
    "RAYDIUM": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "ORCA": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    "PHOENIX": "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY",
    "OPENBOOK": "srmqPvymJeFKQ4zGQed1GFELXCWuBvf9Ss623VQ5DA",
    "JUPITER_V6": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
    "JUPITER_V4": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
    "JUPITER_V3": "JUP3c2Uh3WA4Ng34tw6kPd2G4C5BB21Xo36Je1s32Ph",
}


async def fetch_transaction(signature: str) -> dict | None:
    """Fetch a transaction's data from the RPC"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        async with session.post(HELIUS_RPC_URL, json=payload) as resp:
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

def identify_dex_and_instruction(tx_data: dict) -> tuple[str, dict] | None:
    try:
        print("🔎 Scanning instructions...")

        for ix in tx_data["transaction"]["message"]["instructions"]:
            program_id = ix.get("programId")
            if not program_id and "programIdIndex" in ix:
                index = ix["programIdIndex"]
                program_id = tx_data["transaction"]["message"]["accountKeys"][index]
            print(f"🔍 Found program_id: {program_id}")

            for dex_name, dex_id in DEX_PROGRAMS.items():
                if program_id == dex_id:
                    print(f"✅ Matched DEX: {dex_name}")
                    return dex_name, ix
        return None
    except Exception as e:
        print(f"⚠️ Error identifying DEX: {e}")
        return None


def extract_trade_data(dex: str, instruction: dict, tx_data: dict) -> dict | None:
    """Extract trade data based on the DEX being used"""
    try:
        # For Jupiter, we need special handling
        if dex == "JUPITER":
            # Jupiter trades are complex with multiple instructions
            # We'll focus on the key swap information
            data = instruction.get("data", "")
            accounts = instruction.get("accounts", [])
            
            trade_info = {
                "dex": dex,
                "instruction_data": data,
                "accounts": accounts,
                "discriminator": "jupiter_swap",  # Jupiter uses different discriminators
                "raw_data": data,
            }
            
            # Extract information from transaction logs
            logs = tx_data.get("meta", {}).get("logMessages", [])
            for log in logs:
                if "Program log: price_impact_pc" in log:
                    # Extract price impact if available
                    try:
                        impact = float(log.split(":")[1].strip())
                        trade_info["price_impact"] = impact
                    except:
                        pass
                elif "Program log: in_amount" in log:
                    # Extract input amount if available
                    try:
                        amount = int(log.split(":")[1].strip())
                        trade_info["input_amount"] = amount
                    except:
                        pass
            
            return trade_info
        
        # For other DEXes, use the original logic
        data = base64.b64decode(instruction["data"])
        accounts = instruction["accounts"]
        
        trade_info = {
            "dex": dex,
            "instruction_data": data,
            "accounts": accounts,
            "discriminator": data[:8].hex(),
            "raw_data": instruction["data"],
        }
        
        if dex == "PUMP" or dex == "PUMP_NEW":
            trade_info.update({
                "amount": int.from_bytes(data[40:48], 'little') if len(data) >= 48 else None,
                "slippage": int.from_bytes(data[48:50], 'little') if len(data) >= 50 else None,
            })
        elif dex == "RAYDIUM":
            # Add Raydium-specific parsing
            pass
        elif dex == "ORCA":
            # Add Orca-specific parsing
            pass
        
        return trade_info
    except Exception as e:
        print(f"⚠️ Error extracting trade data: {e}")
        return None

def extract_token_info(tx_data: dict) -> tuple[str, str] | None:
    """Extract token mint addresses involved in the trade"""
    try:
        # Look through token balance changes
        pre_tokens = tx_data["meta"]["preTokenBalances"]
        post_tokens = tx_data["meta"]["postTokenBalances"]
        
        all_tokens = set()
        for balance in pre_tokens + post_tokens:
            all_tokens.add(balance["mint"])
        
        # Remove WSOL if present as it's usually just wrapped SOL
        wsol = "So11111111111111111111111111111111111111112"
        all_tokens.discard(wsol)
        
        if len(all_tokens) >= 2:
            # If we have multiple tokens, one is input and one is output
            return list(all_tokens)[:2]
        elif len(all_tokens) == 1:
            # If we have one token, it's probably a SOL pair
            return [wsol, list(all_tokens)[0]]
        return None
    except Exception as e:
        print(f"⚠️ Error extracting token info: {e}")
        return None

async def handle_trade(tx_data: dict, logs: list, mint: str, signature: str):
    """Process any detected trade with full information extraction"""
    print("\n🔍 ANALYZING TRADE")
    print("=" * 50)
    print(f"📝 Transaction: {signature}")
    
    # Identify DEX and extract instruction
    dex_info = identify_dex_and_instruction(tx_data)
    if not dex_info:
        print("❌ No recognized DEX instruction found")
        return
        
    dex_name, instruction = dex_info
    
    # Get trade data
    trade_data = extract_trade_data(dex_name, instruction, tx_data)
    if not trade_data:
        print("❌ Could not extract trade data")
        return
        
    # Get token information
    token_info = extract_token_info(tx_data)
    if not token_info:
        print("❌ Could not identify tokens involved")
        return
        
    input_token, output_token = token_info
    
    # Print detailed trade information
    print(f"\n🏛️  DEX: {dex_name}")
    print(f"💱 Trade Type: {trade_data['discriminator']}")
    print(f"\n🪙 Input Token: {input_token}")
    print(f"🎯 Output Token: {output_token}")
    
    if trade_data.get("amount"):
        print(f"💰 Amount: {trade_data['amount']}")
    if trade_data.get("slippage"):
        print(f"📊 Slippage: {trade_data['slippage']/100}%")
    if trade_data.get("price_impact"):
        print(f"📉 Price Impact: {trade_data['price_impact']}%")
    if trade_data.get("input_amount"):
        print(f"🔄 Input Amount: {trade_data['input_amount']}")
    
    print("\n📋 Instruction Data:")
    print(f"Discriminator: {trade_data['discriminator']}")
    print(f"Raw Data: {trade_data['raw_data']}")
    
    print("\n🏦 Account Layout:")
    for i, account in enumerate(trade_data['accounts']):
        print(f"{i}: {account}")
    
    print("\n✨ Trade Information Captured Successfully!")
    print("=" * 50)

async def listen_to_wallets(callback):
    """Main listening function for monitored wallets activity"""
    print("🧪 Callback passed to listener:", callback)
    print("🧪 Callback type:", type(callback))
    print(f"📡 Starting bot – mirroring wallets: {', '.join(MONITORED_WALLETS)}")

    while True:
        try:
            async with websockets.connect(HELIUS_WS_URL) as ws:
                for wallet in MONITORED_WALLETS:
                    await ws.send(json.dumps({
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "logsSubscribe",
                        "params": [
                            {"mentions": [wallet]},
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

                    # Look for any DEX trade
                    dex_info = identify_dex_and_instruction(tx_data)
                    if dex_info:
                        print(f"🔥 Detected {dex_info[0]} trade — analyzing")
                        try:
                            # Extract mint from token info for callback
                            token_info = extract_token_info(tx_data)
                            mint = token_info[1] if token_info else None
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

if __name__ == "__main__":
    asyncio.run(listen_to_wallets(handle_trade))