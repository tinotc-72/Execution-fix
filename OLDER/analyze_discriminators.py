#!/usr/bin/env python3
"""
Analyze all pump.fun instructions to find the correct sell discriminator
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
BUY_DISCRIMINATOR = "66063d1201daebea"

# Environment
keys = EnvKeys()
RPC_URL = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"

async def analyze_pump_instructions() -> Dict[str, int]:
    """Analyze all pump.fun instructions to find discriminator patterns"""
    logger.info(f"🔍 Analyzing all pump.fun instructions")
    
    discriminator_counts = {}
    
    async with aiohttp.ClientSession() as session:
        # Get recent transactions for the pump program
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                PUMP_TRADE_PROGRAM,
                {
                    "limit": 50,  # Reduced for detailed analysis
                    "commitment": "confirmed"
                }
            ]
        }
        
        async with session.post(RPC_URL, json=payload) as response:
            data = await response.json()
            
        if "result" not in data:
            logger.error(f"Failed to get signatures: {data}")
            return {}
            
        signatures = data["result"]
        logger.info(f"Found {len(signatures)} recent transactions")
        
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
            
            # Analyze all pump instructions
            analyze_instructions(tx_result, discriminator_counts)
                    
        return discriminator_counts

def analyze_instructions(tx_data: Dict[str, Any], discriminator_counts: Dict[str, int]) -> None:
    """Analyze all instructions to find discriminator patterns"""
    try:
        message = tx_data["transaction"]["message"]
        instructions = message["instructions"]
        
        for instruction in instructions:
            if instruction.get("programId") == PUMP_TRADE_PROGRAM:
                data = instruction.get("data", "")
                if data:
                    try:
                        # Decode and get first 8 bytes as discriminator
                        data_bytes = base64.b64decode(data)
                        discriminator = data_bytes[:8].hex()
                        
                        # Count this discriminator
                        if discriminator in discriminator_counts:
                            discriminator_counts[discriminator] += 1
                        else:
                            discriminator_counts[discriminator] = 1
                            
                        # If this is not the known buy discriminator, analyze it
                        if discriminator != BUY_DISCRIMINATOR:
                            logger.info(f"  Found non-buy instruction: {discriminator}")
                            logger.info(f"  Full data: {data}")
                            logger.info(f"  Transaction: {tx_data.get('transaction', {}).get('signatures', ['unknown'])[0]}")
                            
                    except Exception as e:
                        logger.error(f"Failed to decode instruction data: {e}")
                    
    except Exception as e:
        logger.error(f"Error analyzing instructions: {e}")

async def main():
    """Main function to analyze pump.fun instructions"""
    logger.info("🚀 Starting analysis of pump.fun instructions")
    logger.info("=" * 60)
    
    try:
        # Analyze instructions
        discriminator_counts = await analyze_pump_instructions()
        
        logger.info(f"\n📊 DISCRIMINATOR ANALYSIS RESULTS")
        logger.info("=" * 40)
        
        # Sort by count
        sorted_discriminators = sorted(discriminator_counts.items(), key=lambda x: x[1], reverse=True)
        
        for discriminator, count in sorted_discriminators:
            if discriminator == BUY_DISCRIMINATOR:
                instruction_type = "BUY (known)"
            else:
                instruction_type = "UNKNOWN"
                
            logger.info(f"{discriminator}: {count:3d} occurrences - {instruction_type}")
        
        logger.info("\n✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
