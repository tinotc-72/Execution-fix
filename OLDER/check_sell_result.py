#!/usr/bin/env python3
"""
Check the result of the sell transaction to see why it failed
"""

import asyncio
import logging
import json
import aiohttp

from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TARGET_TX = "4qSo5zE2Q9Lraoy9CwbQtZ7sDpdjND2KSp4XTaLfBJQpFQeWyK44YNy3w3vq4J4Ry8RGUNtiRvhF5dTVeUR11CdE"

# Environment
keys = EnvKeys()
RPC_URL = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"

async def check_transaction_result():
    """Check the result of our sell transaction"""
    logger.info(f"🔍 Checking transaction: {TARGET_TX}")
    logger.info(f"🔗 Solscan: https://solscan.io/tx/{TARGET_TX}")
    
    async with aiohttp.ClientSession() as session:
        # Get transaction details
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                TARGET_TX,
                {
                    "encoding": "jsonParsed",
                    "commitment": "confirmed",
                    "maxSupportedTransactionVersion": 0
                }
            ]
        }
        
        async with session.post(RPC_URL, json=payload) as response:
            data = await response.json()
            
        if "result" not in data or not data["result"]:
            logger.error(f"Transaction not found or failed to fetch: {data}")
            return
            
        tx_data = data["result"]
        
        # Check if transaction was successful
        if tx_data.get("meta", {}).get("err"):
            logger.error("❌ TRANSACTION FAILED!")
            logger.error(f"Error: {tx_data['meta']['err']}")
        else:
            logger.info("✅ Transaction was successful")
            
        # Check program logs
        logs = tx_data.get("meta", {}).get("logMessages", [])
        logger.info(f"\n📜 PROGRAM LOGS ({len(logs)} total):")
        for i, log in enumerate(logs):
            logger.info(f"  [{i:2d}] {log}")
            
        # Analyze instruction details
        instructions = tx_data.get("transaction", {}).get("message", {}).get("instructions", [])
        logger.info(f"\n🔍 INSTRUCTIONS ({len(instructions)} total):")
        
        for i, instruction in enumerate(instructions):
            program_id = instruction.get("programId")
            logger.info(f"  [{i}] Program: {program_id}")
            
            if program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":  # Pump program
                logger.info(f"      Data: {instruction.get('data', 'N/A')}")
                logger.info(f"      Accounts: {len(instruction.get('accounts', []))}")
                
        # Check balance changes
        pre_balances = tx_data.get("meta", {}).get("preBalances", [])
        post_balances = tx_data.get("meta", {}).get("postBalances", [])
        account_keys = tx_data.get("transaction", {}).get("message", {}).get("accountKeys", [])
        
        logger.info(f"\n💰 BALANCE CHANGES:")
        for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
            if pre != post:
                account = account_keys[i] if i < len(account_keys) else "Unknown"
                if isinstance(account, dict):
                    account = account.get("pubkey", "Unknown")
                change = post - pre
                logger.info(f"  {account}: {pre/1e9:.6f} → {post/1e9:.6f} SOL ({change/1e9:+.6f})")
                
        # Check token balance changes
        pre_token_balances = tx_data.get("meta", {}).get("preTokenBalances", [])
        post_token_balances = tx_data.get("meta", {}).get("postTokenBalances", [])
        
        if pre_token_balances or post_token_balances:
            logger.info(f"\n🪙 TOKEN BALANCE CHANGES:")
            logger.info(f"Pre-transaction tokens: {len(pre_token_balances)}")
            for balance in pre_token_balances:
                logger.info(f"  Account: {balance.get('owner')}")
                logger.info(f"  Mint: {balance.get('mint')}")
                logger.info(f"  Amount: {balance.get('uiTokenAmount', {}).get('uiAmount', 0)}")
                
            logger.info(f"Post-transaction tokens: {len(post_token_balances)}")
            for balance in post_token_balances:
                logger.info(f"  Account: {balance.get('owner')}")
                logger.info(f"  Mint: {balance.get('mint')}")
                logger.info(f"  Amount: {balance.get('uiTokenAmount', {}).get('uiAmount', 0)}")

async def main():
    """Main function"""
    logger.info("🚀 Checking sell transaction result")
    logger.info("=" * 50)
    
    try:
        await check_transaction_result()
        logger.info("\n✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
