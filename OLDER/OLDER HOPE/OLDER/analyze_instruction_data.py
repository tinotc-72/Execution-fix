#!/usr/bin/env python3
"""
Analyze the instruction data from successful pump.fun transactions
"""

import asyncio
import json
import aiohttp
import base64
from env_keys import EnvKeys

async def analyze_instruction_data(tx_sig: str):
    """Analyze instruction data from successful transaction"""
    keys = EnvKeys()
    rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_sig,
            {
                "encoding": "base64",  # Get raw data
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            result = await response.json()
    
    if "result" in result and result["result"]:
        tx_data = result["result"]
        
        # Get transaction in base64 format for raw instruction data
        tx_raw = tx_data.get("transaction", [])
        if isinstance(tx_raw, list) and len(tx_raw) > 0:
            print("=== Raw Transaction Analysis ===")
            print(f"Raw data length: {len(tx_raw[0])}")
            
        # Also get JSON version for readable structure
        payload_json = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                tx_sig,
                {
                    "encoding": "json",
                    "commitment": "confirmed",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        
        async with session.post(rpc_url, json=payload_json) as response:
            result_json = await response.json()
            
    if "result" in result_json and result_json["result"]:
            tx_json = result_json["result"]
            message = tx_json["transaction"]["message"]
            
            print("\n=== Instruction Data Analysis ===")
            
            for i, ix in enumerate(message.get("instructions", [])):
                accounts = message.get("accountKeys", [])
                program_idx = ix.get("programIdIndex", 0)
                program_id = accounts[program_idx] if program_idx < len(accounts) else "Unknown"
                
                if program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    print(f"\nPump.fun Instruction {i}:")
                    print(f"Program: {program_id}")
                    
                    data = ix.get("data", "")
                    if data:
                        # Decode base58 data
                        try:
                            import base58
                            raw_data = base58.b58decode(data)
                            print(f"Data (base58): {data}")
                            print(f"Data (hex): {raw_data.hex()}")
                            print(f"Data length: {len(raw_data)} bytes")
                            
                            if len(raw_data) >= 8:
                                discriminator = raw_data[:8]
                                print(f"Discriminator: {discriminator.hex()}")
                                
                                # Rest of data
                                if len(raw_data) > 8:
                                    rest = raw_data[8:]
                                    print(f"Remaining data: {rest.hex()}")
                                    
                                    # Try to parse as amounts (8-byte little endian)
                                    if len(rest) >= 8:
                                        amount1 = int.from_bytes(rest[:8], 'little')
                                        print(f"First amount: {amount1} ({amount1/1e9:.6f} SOL)")
                                        
                                    if len(rest) >= 16:
                                        amount2 = int.from_bytes(rest[8:16], 'little')
                                        print(f"Second amount: {amount2} ({amount2/1e9:.6f} SOL)")
                                        
                        except Exception as e:
                            print(f"Error decoding data: {e}")
                    
                    # Show account structure
                    account_indices = ix.get("accounts", [])
                    print(f"Accounts ({len(account_indices)}):")
                    for j, acc_idx in enumerate(account_indices):
                        if acc_idx < len(accounts):
                            print(f"  {j}: {accounts[acc_idx]}")

async def main():
    # Analyze successful SELL transaction 
    print("=== SUCCESSFUL SELL TRANSACTION ===")
    await analyze_instruction_data("VfqeM43anBaxsR7fezsKVMY1P4DGp9LBKsxAoCbL2BQNt5LUZhec5bHqPb1DzUVYQNFqaYCHz65zirGvnfabPcX")

if __name__ == "__main__":
    asyncio.run(main())
