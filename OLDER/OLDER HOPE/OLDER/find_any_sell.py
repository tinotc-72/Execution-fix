#!/usr/bin/env python3
"""
Find any recent successful sell transactions from pump.fun to understand the account structure
"""

import asyncio
import base64
import json
import logging
from typing import Dict, List, Any

import aiohttp
from solders.pubkey import Pubkey

from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PUMP_TRADE_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
SELL_DISCRIMINATOR = "33e685a4017f83ad"

# Environment
keys = EnvKeys()
RPC_URL = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"

async def find_any_sell_transactions() -> List[Dict[str, Any]]:
    """Find any recent successful sell transactions"""
    logger.info(f"🔍 Searching for any recent sell transactions")
    
    async with aiohttp.ClientSession() as session:
        # Get recent transactions for the pump program
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                PUMP_TRADE_PROGRAM,
                {
                    "limit": 100,
                    "commitment": "confirmed"
                }
            ]
        }
        
        async with session.post(RPC_URL, json=payload) as response:
            data = await response.json()
            
        if "result" not in data:
            logger.error(f"Failed to get signatures: {data}")
            return []
            
        signatures = data["result"]
        logger.info(f"Found {len(signatures)} recent transactions")
        
        sell_txs = []
        for i, sig_info in enumerate(signatures):
            if sig_info.get("err"):  # Skip failed transactions
                continue
                
            sig = sig_info["signature"]
            logger.info(f"Analyzing transaction {i+1}/{len(signatures)}: {sig}")
            
            # Get transaction details
            tx_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    sig,
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
            
            # Check if this is a sell transaction
            if is_sell_transaction(tx_result):
                logger.info(f"✅ Found sell transaction: {sig}")
                sell_txs.append({
                    "signature": sig,
                    "data": tx_result
                })
                
                if len(sell_txs) >= 3:  # Get first 3 sell transactions
                    break
                    
        return sell_txs

def is_sell_transaction(tx_data: Dict[str, Any]) -> bool:
    """Check if transaction is a sell"""
    try:
        message = tx_data["transaction"]["message"]
        instructions = message["instructions"]
        
        for instruction in instructions:
            if instruction.get("programId") == PUMP_TRADE_PROGRAM:
                # Check instruction data for sell discriminator
                data = instruction.get("data", "")
                if data.startswith(SELL_DISCRIMINATOR):
                    return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking transaction: {e}")
        return False

def analyze_sell_instruction(tx_data: Dict[str, Any]) -> None:
    """Analyze the sell instruction structure"""
    logger.info("🔍 Analyzing sell instruction structure")
    
    try:
        message = tx_data["transaction"]["message"]
        instructions = message["instructions"]
        account_keys = message.get("accountKeys", [])
        
        for i, instruction in enumerate(instructions):
            if instruction.get("programId") == PUMP_TRADE_PROGRAM:
                data = instruction.get("data", "")
                if data.startswith(SELL_DISCRIMINATOR):
                    logger.info(f"\n=== SELL INSTRUCTION {i} ===")
                    logger.info(f"Program ID: {instruction['programId']}")
                    logger.info(f"Data: {data}")
                    
                    # Decode instruction data
                    try:
                        data_bytes = base64.b64decode(data)
                        discriminator = data_bytes[:8].hex()
                        token_amount = int.from_bytes(data_bytes[8:16], "little")
                        min_sol_out = int.from_bytes(data_bytes[16:24], "little")
                        
                        logger.info(f"Discriminator: {discriminator}")
                        logger.info(f"Token amount: {token_amount}")
                        logger.info(f"Min SOL out: {min_sol_out}")
                    except Exception as e:
                        logger.error(f"Failed to decode instruction data: {e}")
                    
                    # Analyze accounts
                    accounts = instruction.get("accounts", [])
                    logger.info(f"\n🏦 ACCOUNTS ({len(accounts)} total):")
                    
                    for j, account_idx in enumerate(accounts):
                        if isinstance(account_idx, int) and account_idx < len(account_keys):
                            account = account_keys[account_idx]
                            if isinstance(account, dict):
                                pubkey = account.get("pubkey")
                                is_signer = account.get("signer", False)
                                is_writable = account.get("writable", False)
                            else:
                                pubkey = account
                                is_signer = False
                                is_writable = False
                            
                            # Identify account type
                            account_type = identify_account_type(pubkey)
                            
                            logger.info(f"  [{j:2d}] {pubkey} - {account_type}")
                            logger.info(f"       Signer: {is_signer}, Writable: {is_writable}")
                    
                    break
                    
    except Exception as e:
        logger.error(f"Error analyzing instruction: {e}")

def identify_account_type(pubkey: str) -> str:
    """Identify the type of account based on known addresses"""
    known_accounts = {
        "11111111111111111111111111111111": "System Program",
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump Trade Program",
        "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf": "Pump Config",
        "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Event Authority",
    }
    
    if pubkey in known_accounts:
        return known_accounts[pubkey]
    
    # Check if it looks like a token mint (44 characters, base58)
    if len(pubkey) == 44:
        try:
            pubkey_obj = Pubkey.from_string(pubkey)
            return "Token/Mint/Account"
        except:
            return "Invalid Pubkey"
    
    return "Unknown"

async def main():
    """Main function to analyze recent sell transactions"""
    logger.info("🚀 Starting analysis of any recent sell transactions")
    logger.info("=" * 60)
    
    try:
        # Find recent sell transactions
        sell_txs = await find_any_sell_transactions()
        
        if not sell_txs:
            logger.warning("❌ No sell transactions found")
            return
        
        logger.info(f"📊 Analyzing {len(sell_txs)} sell transactions")
        
        # Analyze each transaction
        for i, tx_info in enumerate(sell_txs):
            logger.info(f"\n{'='*20} TRANSACTION {i+1} {'='*20}")
            logger.info(f"Signature: {tx_info['signature']}")
            logger.info(f"Solscan: https://solscan.io/tx/{tx_info['signature']}")
            
            analyze_sell_instruction(tx_info['data'])
            
        logger.info("\n✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
