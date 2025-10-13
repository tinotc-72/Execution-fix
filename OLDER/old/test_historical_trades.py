#!/usr/bin/env python3
"""
Analyze recent historical trades from Wallet A to verify our extraction logic
"""

import asyncio
import aiohttp
import json
from listener import (
    WALLET_A_ADDRESS, 
    HELIUS_RPC_URL,
    extract_instruction_data,
    extract_accounts_layout,
    extract_trade_params,
    is_pump_trade
)
from log_utils import extract_mint_from_logs

async def get_recent_signatures() -> list:
    """Get recent transaction signatures for Wallet A"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                WALLET_A_ADDRESS,
                {
                    "limit": 20  # Get last 20 transactions
                }
            ]
        }
        async with session.post(HELIUS_RPC_URL, json=payload) as resp:
            result = await resp.json()
            if "result" in result:
                return [tx["signature"] for tx in result["result"]]
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

async def analyze_transaction(signature: str):
    """Analyze a single transaction"""
    print(f"\n🔍 Analyzing transaction: {signature}")
    print("=" * 50)
    
    tx_data = await get_transaction(signature)
    if not tx_data:
        print("❌ Could not fetch transaction data")
        return
        
    # Get logs
    logs = tx_data.get("meta", {}).get("logMessages", [])
    
    # Only process if it's a PUMP trade
    if not is_pump_trade(tx_data):
        print("⏭️  Not a PUMP router trade")
        return
        
    # Extract trade information
    mint = extract_mint_from_logs(logs)
    instruction_data = extract_instruction_data(tx_data)
    accounts = extract_accounts_layout(tx_data)
    trade_params = extract_trade_params(instruction_data) if instruction_data else None
    
    if not all([mint, instruction_data, accounts, trade_params]):
        print("❌ Missing some trade information")
        if not mint: print("- No mint address found")
        if not instruction_data: print("- No instruction data found")
        if not accounts: print("- No accounts layout found")
        if not trade_params: print("- No trade parameters found")
        return
        
    amount, slippage = trade_params
    
    # Print detailed trade information
    print(f"\n🪙 Token Mint: {mint}")
    print(f"💰 Amount: {amount}")
    print(f"📊 Slippage: {slippage/100}%")
    print("\n📋 Instruction Data:")
    print(f"Discriminator: {instruction_data[:8].hex()}")
    print(f"Full Data: {instruction_data.hex()}")
    print("\n🏦 Accounts Layout:")
    for i, account in enumerate(accounts):
        print(f"{i}: {account}")
    
    print("\n✨ Trade Information Extracted Successfully!")
    print("=" * 50)

async def main():
    print("🎯 Starting historical trade analysis for Wallet A...")
    print(f"📬 Wallet Address: {WALLET_A_ADDRESS}")
    
    signatures = await get_recent_signatures()
    if not signatures:
        print("❌ No recent transactions found")
        return
        
    print(f"📝 Found {len(signatures)} recent transactions")
    print("Analyzing each transaction for trade data...")
    
    for sig in signatures:
        await analyze_transaction(sig)
    
    print("\n🏁 Analysis complete!")

if __name__ == "__main__":
    asyncio.run(main())
