"""
Check transaction details and logs for the latest failed trade.
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from fast_executor import FastExecutor
from env_keys import EnvKeys
from config import WALLET

# Load environment keys
keys = EnvKeys()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RPC endpoints
RPC_ENDPOINTS = [keys.HELIUS_RPC_URL, keys.PUBLIC_RPC_URL]

async def check_transaction_details():
    """Check transaction details and logs."""
    # Latest transaction signature
    tx_sig = "3AKwniSH3XAvAiM5HJm266VNxfJSd1RHLeFfaHZErt88pqfvEtnSHi81LwFV5i9p4EBYfTiT1nUDt3hMrnxbQB4P"
    
    try:
        async with FastExecutor(WALLET, rpc_urls=RPC_ENDPOINTS) as executor:
            logger.info(f"🔍 Checking transaction: {tx_sig}")
            
            # Get transaction details
            for rpc_url in RPC_ENDPOINTS:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        payload = {
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
                        
                        async with session.post(rpc_url, json=payload) as response:
                            result = await response.json()
                            
                            if "result" in result and result["result"]:
                                tx_data = result["result"]
                                
                                logger.info(f"✅ Transaction found on {rpc_url}")
                                logger.info(f"Slot: {tx_data.get('slot', 'N/A')}")
                                logger.info(f"Block time: {tx_data.get('blockTime', 'N/A')}")
                                
                                meta = tx_data.get("meta", {})
                                logger.info(f"Status: {'Success' if meta.get('err') is None else 'Failed'}")
                                
                                if meta.get("err"):
                                    logger.error(f"❌ Transaction error: {meta['err']}")
                                
                                # Check program logs
                                logs = meta.get("logMessages", [])
                                logger.info(f"\n📝 Program Logs ({len(logs)} total):")
                                if logs:
                                    for i, log in enumerate(logs):
                                        logger.info(f"  {i}: {log}")
                                else:
                                    logger.warning("  No program logs found")
                                
                                # Check instructions
                                instructions = tx_data.get("transaction", {}).get("message", {}).get("instructions", [])
                                logger.info(f"\n🛠️ Instructions ({len(instructions)} total):")
                                for i, instruction in enumerate(instructions):
                                    program_id_index = instruction.get("programIdIndex", "N/A")
                                    accounts = instruction.get("accounts", [])
                                    data = instruction.get("data", "")
                                    logger.info(f"  Instruction {i}: Program index {program_id_index}, Accounts: {len(accounts)}, Data: {data[:20]}...")
                                
                                # Check account keys
                                account_keys = tx_data.get("transaction", {}).get("message", {}).get("accountKeys", [])
                                logger.info(f"\n🔑 Account Keys ({len(account_keys)} total):")
                                for i, key in enumerate(account_keys):
                                    logger.info(f"  {i}: {key}")
                                
                                # Check pre/post token balances
                                pre_balances = meta.get("preTokenBalances", [])
                                post_balances = meta.get("postTokenBalances", [])
                                
                                if pre_balances or post_balances:
                                    logger.info("\n💰 Token Balance Changes:")
                                    logger.info(f"Pre-balances: {len(pre_balances)} accounts")
                                    for balance in pre_balances:
                                        logger.info(f"  Account {balance.get('accountIndex')}: {balance.get('uiTokenAmount', {}).get('uiAmount', 0)}")
                                    
                                    logger.info(f"Post-balances: {len(post_balances)} accounts")
                                    for balance in post_balances:
                                        logger.info(f"  Account {balance.get('accountIndex')}: {balance.get('uiTokenAmount', {}).get('uiAmount', 0)}")
                                
                                # Check account changes
                                pre_sol_balances = meta.get("preBalances", [])
                                post_sol_balances = meta.get("postBalances", [])
                                
                                if pre_sol_balances and post_sol_balances:
                                    logger.info("\n💳 SOL Balance Changes:")
                                    for i, (pre, post) in enumerate(zip(pre_sol_balances, post_sol_balances)):
                                        change = post - pre
                                        if change != 0:
                                            logger.info(f"  Account {i}: {pre/1e9:.6f} → {post/1e9:.6f} SOL (change: {change/1e9:.6f})")
                                
                                return  # Found it, exit
                            else:
                                logger.warning(f"❌ Transaction not found on {rpc_url}")
                                
                except Exception as e:
                    logger.error(f"❌ Error checking {rpc_url}: {str(e)}")
                    continue
                    
    except Exception as e:
        logger.error(f"❌ Error checking transaction: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(check_transaction_details())
