#!/usr/bin/env python3
"""
Analyze a known successful pump.fun sell transaction to extract the correct instruction structure
"""

import asyncio
import base64
import logging
import json
import aiohttp
from typing import Dict, Any, Optional

from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment
keys = EnvKeys()
RPC_URL = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"

# Let's analyze a known sell transaction - I'll find one from pump.fun
# This signature represents a successful sell transaction on pump.fun
KNOWN_SELL_TX = "3kbmBhq8ZjAVj8LVpRbCh4C2S6z8f2QwUVd5XkjNdBhR5SZQvEFAhD8R2LRyQ1YJ4KjS9D7F6R2LRyQ1YJ4KjS9D"  # Placeholder - we'll find a real one

async def analyze_known_sell_transaction(signature: str) -> Optional[Dict[str, Any]]:
    """Analyze a known sell transaction to extract instruction details"""
    logger.info(f"🔍 Analyzing sell transaction: {signature}")
    
    async with aiohttp.ClientSession() as session:
        # Get transaction details
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                signature,
                {
                    "encoding": "json",  # Use json encoding instead of jsonParsed to get raw data
                    "commitment": "confirmed",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        
        async with session.post(RPC_URL, json=payload) as response:
            data = await response.json()
            
        if "result" not in data or not data["result"]:
            logger.error(f"Transaction not found: {data}")
            return None
            
        tx_data = data["result"]
        logger.info("✅ Transaction found - analyzing...")
        
        return analyze_sell_instruction_details(tx_data, signature)

def analyze_sell_instruction_details(tx_data: Dict[str, Any], signature: str) -> Optional[Dict[str, Any]]:
    """Extract detailed instruction information from sell transaction"""
    try:
        transaction = tx_data["transaction"]
        message = transaction["message"]
        instructions = message["instructions"]
        account_keys = message["accountKeys"]
        
        logger.info(f"📊 Transaction has {len(instructions)} instructions")
        logger.info(f"📊 Transaction has {len(account_keys)} accounts")
        
        # Look for pump.fun program instruction
        for i, instruction in enumerate(instructions):
            program_id_index = instruction["programIdIndex"]
            program_id = account_keys[program_id_index]
            
            if program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":  # Pump program
                logger.info(f"\n🎯 Found pump.fun instruction at index {i}")
                
                # Get instruction data
                data_base64 = instruction["data"]
                logger.info(f"📄 Raw data (base64): {data_base64}")
                
                try:
                    # Decode instruction data
                    data_bytes = base64.b64decode(data_base64)
                    discriminator = data_bytes[:8].hex()
                    
                    logger.info(f"🔑 Discriminator: {discriminator}")
                    
                    if len(data_bytes) >= 24:
                        amount1 = int.from_bytes(data_bytes[8:16], "little")
                        amount2 = int.from_bytes(data_bytes[16:24], "little")
                        logger.info(f"📊 Amount 1: {amount1}")
                        logger.info(f"📊 Amount 2: {amount2}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to decode data: {e}")
                
                # Analyze accounts
                accounts = instruction["accounts"]
                logger.info(f"\n🏦 Instruction uses {len(accounts)} accounts:")
                
                for j, account_index in enumerate(accounts):
                    account_pubkey = account_keys[account_index]
                    logger.info(f"  [{j:2d}] {account_pubkey}")
                
                return {
                    "discriminator": discriminator,
                    "accounts": [account_keys[idx] for idx in accounts],
                    "raw_data": data_base64,
                    "signature": signature
                }
                
        logger.warning("❌ No pump.fun instruction found")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error analyzing transaction: {e}")
        return None

async def find_recent_sell_from_pump_website():
    """
    Let's find a recent sell transaction by looking at pump.fun's recent activity
    We'll look for transactions that have token balance decreases (indicating sells)
    """
    logger.info("🔍 Searching for recent sell transactions...")
    
    async with aiohttp.ClientSession() as session:
        # Get very recent transactions from pump program
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump program
                {
                    "limit": 50,
                    "commitment": "confirmed"
                }
            ]
        }
        
        async with session.post(RPC_URL, json=payload) as response:
            data = await response.json()
            
        if "result" not in data:
            logger.error(f"Failed to get signatures: {data}")
            return None
            
        signatures = data["result"]
        logger.info(f"Found {len(signatures)} recent transactions")
        
        # Check each transaction for sell characteristics
        for i, sig_info in enumerate(signatures[:20]):  # Check first 20
            if sig_info.get("err"):  # Skip failed transactions
                continue
                
            signature = sig_info["signature"]
            logger.info(f"Checking transaction {i+1}/20: {signature[:20]}...")
            
            # Get transaction details with token balances
            tx_payload = {
                "jsonrpc": "2.0", 
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "jsonParsed",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            async with session.post(RPC_URL, json=tx_payload) as response:
                tx_data = await response.json()
                
            if "result" not in tx_data or not tx_data["result"]:
                continue
                
            tx_result = tx_data["result"]
            
            # Check if this looks like a sell (token balance decrease)
            if is_sell_transaction(tx_result):
                logger.info(f"🎉 FOUND POTENTIAL SELL: {signature}")
                logger.info(f"🔗 Solscan: https://solscan.io/tx/{signature}")
                return signature
                
        logger.warning("❌ No clear sell transactions found in recent activity")
        return None

def is_sell_transaction(tx_data: Dict[str, Any]) -> bool:
    """Check if transaction represents a sell (token balance decrease)"""
    try:
        pre_token_balances = tx_data.get("meta", {}).get("preTokenBalances", [])
        post_token_balances = tx_data.get("meta", {}).get("postTokenBalances", [])
        
        # Look for token balance decrease
        for pre_balance in pre_token_balances:
            pre_amount = float(pre_balance.get("uiTokenAmount", {}).get("uiAmount", 0))
            owner = pre_balance.get("owner")
            mint = pre_balance.get("mint")
            
            if pre_amount <= 0:
                continue
                
            # Find corresponding post balance
            for post_balance in post_token_balances:
                if (post_balance.get("owner") == owner and 
                    post_balance.get("mint") == mint):
                    post_amount = float(post_balance.get("uiTokenAmount", {}).get("uiAmount", 0))
                    
                    # Significant decrease indicates a sell
                    if post_amount < pre_amount * 0.9:  # 10%+ decrease
                        logger.info(f"  Token decrease detected: {pre_amount} → {post_amount}")
                        return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking sell transaction: {e}")
        return False

async def main():
    """Main function to find and analyze sell transaction"""
    logger.info("🚀 Finding correct pump.fun sell instruction structure")
    logger.info("=" * 60)
    
    try:
        # Step 1: Find a recent sell transaction
        sell_signature = await find_recent_sell_from_pump_website()
        
        if not sell_signature:
            logger.warning("❌ Could not find a recent sell transaction")
            logger.info("💡 Manual approach needed:")
            logger.info("   1. Go to pump.fun website")
            logger.info("   2. Execute a small sell transaction")
            logger.info("   3. Copy the transaction signature")
            logger.info("   4. Use that signature in this script")
            return
        
        # Step 2: Analyze the sell transaction
        logger.info(f"\n🔍 Analyzing sell transaction: {sell_signature}")
        
        # Re-analyze with raw JSON to get exact instruction data
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction", 
                "params": [
                    sell_signature,
                    {
                        "encoding": "json",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            async with session.post(RPC_URL, json=payload) as response:
                data = await response.json()
                
            if "result" in data and data["result"]:
                sell_info = analyze_sell_instruction_details(data["result"], sell_signature)
                
                if sell_info:
                    logger.info("\n🎉 SUCCESS! Found sell instruction details:")
                    logger.info(f"🔑 Discriminator: {sell_info['discriminator']}")
                    logger.info(f"📄 Raw data: {sell_info['raw_data']}")
                    logger.info(f"🏦 Account count: {len(sell_info['accounts'])}")
                    logger.info("\n📋 Account structure:")
                    for i, account in enumerate(sell_info['accounts']):
                        logger.info(f"  [{i:2d}] {account}")
                        
                else:
                    logger.error("❌ Could not extract sell instruction details")
            else:
                logger.error("❌ Could not re-fetch transaction details")
        
        logger.info("\n✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
