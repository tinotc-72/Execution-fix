#!/usr/bin/env python3
"""
Find the actual working sell discriminator by examining pump.fun website transactions
"""

import asyncio
import time
import logging
import json
import aiohttp
import base64
from typing import Dict, List, Any, Optional

from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PUMP_TRADE_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
KNOWN_BUY_DISCRIMINATOR = "66063d1201daebea"

# Environment
keys = EnvKeys()
RPC_URL = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"

async def monitor_pump_transactions_realtime() -> Optional[str]:
    """Monitor pump.fun transactions in real-time to catch a sell"""
    logger.info(f"🔍 Monitoring pump.fun transactions for sell instructions...")
    logger.info("This will run for 60 seconds to catch live transactions")
    
    async with aiohttp.ClientSession() as session:
        last_signature = None
        start_time = time.time()
        
        while time.time() - start_time < 60:  # Monitor for 60 seconds
            try:
                # Get recent transactions
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getSignaturesForAddress",
                    "params": [
                        PUMP_TRADE_PROGRAM,
                        {
                            "limit": 10,
                            "commitment": "confirmed"
                        }
                    ]
                }
                
                if last_signature:
                    payload["params"][1]["until"] = last_signature
                
                async with session.post(RPC_URL, json=payload) as response:
                    data = await response.json()
                    
                if "result" not in data:
                    logger.error(f"Failed to get signatures: {data}")
                    await asyncio.sleep(2)
                    continue
                    
                signatures = data["result"]
                
                if not signatures:
                    await asyncio.sleep(2)
                    continue
                
                # Process new transactions
                new_sigs = []
                for sig_info in signatures:
                    sig = sig_info["signature"]
                    if sig == last_signature:
                        break
                    new_sigs.append(sig_info)
                
                if new_sigs:
                    logger.info(f"Found {len(new_sigs)} new transactions")
                    last_signature = signatures[0]["signature"]
                    
                    # Analyze each new transaction
                    for sig_info in new_sigs:
                        if sig_info.get("err"):  # Skip failed transactions
                            continue
                            
                        sig = sig_info["signature"]
                        
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
                        
                        # Analyze this transaction
                        sell_discriminator = analyze_transaction_for_sell(tx_result, sig)
                        if sell_discriminator:
                            logger.info(f"🎉 FOUND SELL DISCRIMINATOR: {sell_discriminator}")
                            return sell_discriminator
                else:
                    last_signature = signatures[0]["signature"] if signatures else None
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring: {e}")
                await asyncio.sleep(2)
                
        logger.info("Monitoring period ended")
        return None

def analyze_transaction_for_sell(tx_data: Dict[str, Any], signature: str) -> Optional[str]:
    """Analyze a transaction to see if it contains a sell instruction"""
    try:
        message = tx_data["transaction"]["message"]
        instructions = message["instructions"]
        account_keys = message.get("accountKeys", [])
        
        for i, instruction in enumerate(instructions):
            if instruction.get("programId") == PUMP_TRADE_PROGRAM:
                data = instruction.get("data", "")
                if not data:
                    continue
                
                try:
                    # Decode instruction data
                    data_bytes = base64.b64decode(data)
                    discriminator = data_bytes[:8].hex()
                    
                    # Skip if this is the known buy discriminator
                    if discriminator == KNOWN_BUY_DISCRIMINATOR:
                        logger.info(f"  Found BUY instruction: {signature}")
                        continue
                    
                    # This might be a sell instruction
                    logger.info(f"  Found NON-BUY instruction: {signature}")
                    logger.info(f"  Discriminator: {discriminator}")
                    logger.info(f"  Solscan: https://solscan.io/tx/{signature}")
                    
                    # Try to determine if this is a sell by looking at token transfers
                    if is_likely_sell_transaction(tx_data):
                        logger.info(f"  ✅ This appears to be a SELL transaction!")
                        return discriminator
                    else:
                        logger.info(f"  ❓ Not clearly a sell transaction")
                        
                except Exception as e:
                    logger.error(f"Failed to decode instruction data: {e}")
                    
    except Exception as e:
        logger.error(f"Error analyzing transaction {signature}: {e}")
        
    return None

def is_likely_sell_transaction(tx_data: Dict[str, Any]) -> bool:
    """Determine if a transaction is likely a sell based on token transfers"""
    try:
        # Check pre and post token balances
        pre_token_balances = tx_data.get("meta", {}).get("preTokenBalances", [])
        post_token_balances = tx_data.get("meta", {}).get("postTokenBalances", [])
        
        # Look for a decrease in user token balance
        for pre_balance in pre_token_balances:
            pre_amount = float(pre_balance.get("uiTokenAmount", {}).get("uiAmount", 0))
            owner = pre_balance.get("owner")
            mint = pre_balance.get("mint")
            
            # Find corresponding post balance
            for post_balance in post_token_balances:
                if (post_balance.get("owner") == owner and 
                    post_balance.get("mint") == mint):
                    post_amount = float(post_balance.get("uiTokenAmount", {}).get("uiAmount", 0))
                    
                    # If token balance decreased, this might be a sell
                    if post_amount < pre_amount:
                        logger.info(f"    Token balance decreased: {pre_amount} → {post_amount}")
                        return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking if sell transaction: {e}")
        return False

async def main():
    """Main function to find the real sell discriminator"""
    logger.info("🚀 Starting real-time pump.fun sell discriminator detection")
    logger.info("=" * 60)
    
    try:
        sell_discriminator = await monitor_pump_transactions_realtime()
        
        if sell_discriminator:
            logger.info(f"\n🎉 SUCCESS! Found working sell discriminator:")
            logger.info(f"🔑 SELL DISCRIMINATOR: {sell_discriminator}")
        else:
            logger.warning("\n❌ No sell transactions found during monitoring period")
            logger.info("💡 Try running the script again to catch more transactions")
        
        logger.info("\n✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
