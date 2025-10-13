#!/usr/bin/env python3
"""
Find active pump.fun wallets to monitor
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from env_keys import EnvKeys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_recent_pump_transactions():
    """Get recent pump.fun transactions to find active wallets"""
    logger.info("🔍 Finding active pump.fun wallets...")
    
    env_keys = EnvKeys()
    
    # Use the standard RPC to get recent pump.fun program transactions
    rpc_url = env_keys.HELIUS_RPC_URL
    
    # Pump.fun program ID
    pump_program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            pump_program_id,
            {
                "limit": 20,  # Get last 20 transactions
                "commitment": "finalized"
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    signatures = data.get('result', [])
                    
                    logger.info(f"✅ Found {len(signatures)} recent pump.fun transactions")
                    
                    active_wallets = set()
                    
                    # Analyze each transaction to find the traders
                    for sig_info in signatures[:10]:  # Check first 10
                        signature = sig_info['signature']
                        logger.info(f"Analyzing transaction: {signature[:8]}...")
                        
                        # Get full transaction details
                        tx_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getTransaction",
                            "params": [
                                signature,
                                {
                                    "encoding": "json",
                                    "maxSupportedTransactionVersion": 0,
                                    "commitment": "finalized"
                                }
                            ]
                        }
                        
                        async with session.post(rpc_url, json=tx_payload) as tx_response:
                            if tx_response.status == 200:
                                tx_data = await tx_response.json()
                                tx_result = tx_data.get('result')
                                
                                if tx_result and tx_result.get('meta', {}).get('err') is None:
                                    # Extract account keys (potential wallets)
                                    account_keys = tx_result.get('transaction', {}).get('message', {}).get('accountKeys', [])
                                    
                                    # Filter out program accounts and system accounts
                                    potential_wallets = []
                                    for account in account_keys:
                                        if (account != pump_program_id and 
                                            not account.startswith('11111111') and  # System program
                                            not account.startswith('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA') and  # Token program
                                            not account.startswith('ComputeBudget') and
                                            len(account) > 40):  # Valid base58 address length
                                            potential_wallets.append(account)
                                    
                                    if potential_wallets:
                                        # Usually the first account is the fee payer/trader
                                        trader_wallet = potential_wallets[0]
                                        active_wallets.add(trader_wallet)
                                        logger.info(f"  📱 Found trader: {trader_wallet[:8]}...")
                    
                    logger.info(f"\n📊 ACTIVE PUMP.FUN WALLETS FOUND:")
                    for i, wallet in enumerate(list(active_wallets)[:5]):  # Show top 5
                        logger.info(f"   {i+1}. {wallet}")
                    
                    return list(active_wallets)[:5]  # Return top 5 active wallets
                    
                else:
                    logger.error(f"Failed to get pump transactions: {response.status}")
                    return []
    
    except Exception as e:
        logger.error(f"Error finding active wallets: {e}")
        return []

async def test_wallet_for_recent_activity(wallet: str) -> bool:
    """Test if a wallet has recent pump.fun activity"""
    logger.info(f"🧪 Testing wallet activity: {wallet[:8]}...")
    
    env_keys = EnvKeys()
    rpc_url = env_keys.HELIUS_RPC_URL
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet,
            {
                "limit": 10,
                "commitment": "finalized"
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(rpc_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    signatures = data.get('result', [])
                    
                    recent_count = 0
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    
                    for sig_info in signatures:
                        block_time = sig_info.get('blockTime')
                        if block_time:
                            tx_time = datetime.fromtimestamp(block_time)
                            if tx_time > cutoff_time:
                                recent_count += 1
                    
                    logger.info(f"   📊 {recent_count} transactions in last 24h")
                    return recent_count > 0
                
    except Exception as e:
        logger.error(f"Error testing wallet: {e}")
        return False

async def main():
    print("🔍 FINDING ACTIVE PUMP.FUN WALLETS")
    print("=" * 50)
    
    # Find currently active wallets
    active_wallets = await get_recent_pump_transactions()
    
    if active_wallets:
        print(f"\n✅ Found {len(active_wallets)} active wallets")
        print("🧪 Testing each wallet for recent activity...")
        
        verified_wallets = []
        for wallet in active_wallets:
            is_active = await test_wallet_for_recent_activity(wallet)
            if is_active:
                verified_wallets.append(wallet)
        
        print(f"\n🎯 RECOMMENDED WALLETS TO MONITOR:")
        print("Add these to your config.py MONITORED_WALLETS:")
        print("MONITORED_WALLETS = [")
        for wallet in verified_wallets:
            print(f"    '{wallet}',")
        print("]")
    
    else:
        print("❌ No active wallets found")

if __name__ == "__main__":
    asyncio.run(main())
