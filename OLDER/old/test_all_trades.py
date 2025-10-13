#!/usr/bin/env python3
"""
Analyze historical trades from any DEX for Wallet A
"""

import asyncio
import aiohttp
from listener import (
    WALLET_A_ADDRESS,
    HELIUS_RPC_URL,
    identify_dex_and_instruction,
    extract_trade_data,
    extract_token_info
)

async def get_recent_signatures(before: str = None, limit: int = 100) -> list:
    """Get recent transaction signatures for Wallet A"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getSignaturesForAddress",
            "params": [
                WALLET_A_ADDRESS,
                {
                    "limit": limit,
                    "before": before
                }
            ]
        }
        async with session.post(HELIUS_RPC_URL, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("result", [])
            return []

async def get_transaction(signature: str) -> dict:
    """Get full transaction data"""
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
            result = await resp.json()
            return result.get("result", {})

async def analyze_transaction(sig: str) -> None:
    """Analyze a single transaction for trades"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getTransaction",
            "params": [
                sig,
                {
                    "encoding": "json",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        async with session.post(HELIUS_RPC_URL, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                tx_data = result.get("result")
                if not tx_data:
                    return

                print(f"\n🔍 Analyzing transaction: {sig}")
                print("=" * 50)

                dex_info = identify_dex_and_instruction(tx_data)
                if not dex_info:
                    print("⏭️  No recognized DEX instruction found")
                    return

                dex_name, instruction = dex_info
                print(f"🏛️  Found {dex_name} trade!")

                trade_data = extract_trade_data(dex_name, instruction, tx_data)
                if not trade_data:
                    print("❌ Could not extract trade data")
                    return

                token_info = extract_token_info(tx_data)
                if not token_info:
                    print("❌ Could not identify tokens involved")
                    return

                input_token, output_token = token_info
                print(f"🪙 Input Token: {input_token}")
                print(f"🎯 Output Token: {output_token}")
                print("📋 Trade Details:")
                print(json.dumps(trade_data, indent=2))

async def main():
    """Main analysis function"""
    print("🎯 Starting multi-DEX trade analysis for Wallet A...")
    print(f"📬 Wallet Address: {WALLET_A_ADDRESS}")

    # Get last 1000 transactions in batches
    all_sigs = []
    batch_size = 100
    total_needed = 1000
    last_sig = None

    while len(all_sigs) < total_needed:
        print(f"📥 Fetching transactions {len(all_sigs)}-{len(all_sigs) + batch_size}")
        batch = await get_recent_signatures(last_sig, batch_size)
        if not batch:
            break
        all_sigs.extend(batch)
        last_sig = batch[-1]["signature"]

    print(f"📝 Found {len(all_sigs)} transactions")
    print("Analyzing each transaction for trade data from any DEX...")

    # Analyze transactions
    for sig_data in all_sigs:
        await analyze_transaction(sig_data["signature"])

    print("\n🏁 Analysis complete!")

if __name__ == "__main__":
    import json
    asyncio.run(main())
