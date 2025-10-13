"""
LIVE MEV Test - Simplified Working Version
Real blockchain transactions with 0.001 SOL
"""

import asyncio
import logging
import time
from live_mev_executor import LiveMEVExecutor
from env_keys import EnvKeys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def confirm_transaction(env_keys: EnvKeys, signature: str, max_retries: int = 30) -> bool:
    """Wait for transaction confirmation"""
    import httpx
    
    logger.info(f"⏳ Confirming transaction: {signature}")
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    env_keys.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignatureStatuses",
                        "params": [[signature]]
                    }
                )
                
                data = response.json()
                if 'result' in data and data['result']['value']:
                    status = data['result']['value'][0]
                    if status:
                        if status.get('confirmationStatus') in ['confirmed', 'finalized']:
                            if status.get('err') is None:
                                logger.info(f"✅ Transaction confirmed: {signature}")
                                return True
                            else:
                                logger.error(f"❌ Transaction failed: {status['err']}")
                                return False
        except Exception as e:
            logger.warning(f"Confirmation check error (attempt {attempt + 1}): {e}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2)
    
    logger.warning(f"⏰ Transaction confirmation timeout: {signature}")
    return False

async def run_live_test():
    """Run live MEV test with real transactions"""
    print("🔥 LIVE MEV EXECUTOR TEST - REAL BLOCKCHAIN TRANSACTIONS 🔥")
    print("=" * 60)
    
    # Load environment
    env_keys = EnvKeys()
    
    # Initialize executor
    executor = LiveMEVExecutor(env_keys)
    
    # Test token (the token you provided)
    test_token = "CzR5f68ySPMtvLEkAM6mP85VPBhvkRybTCV2CHzpump"
    
    print(f"💰 Testing with: {test_token}")
    print(f"🔑 Wallet: {executor.wallet_address}")
    print(f"💵 Trade size: 0.001 SOL")
    print("⚠️  WARNING: This will use REAL SOL!")
    print()
    
    # Phase 1: BUY
    print("🚀 Phase 1: BUYING...")
    buy_signature = await executor.execute_buy(test_token, 0.001)
    
    if not buy_signature:
        print("❌ Buy failed - aborting test")
        return
    
    print(f"📝 Buy signature: {buy_signature}")
    print(f"🔗 Explorer: https://solscan.io/tx/{buy_signature}")
    
    # Wait for buy confirmation
    buy_confirmed = await confirm_transaction(env_keys, buy_signature)
    
    if not buy_confirmed:
        print("❌ Buy confirmation failed")
        return
    
    print("✅ Buy confirmed!")
    
    # Phase 2: Wait a bit
    print("\n⏳ Waiting 5 seconds before sell...")
    await asyncio.sleep(5)
    
    # Phase 3: SELL
    print("\n🚀 Phase 2: SELLING...")
    sell_signature = await executor.execute_sell(test_token, 100.0)
    
    if not sell_signature:
        print("❌ Sell failed")
        return
    
    print(f"📝 Sell signature: {sell_signature}")
    print(f"🔗 Explorer: https://solscan.io/tx/{sell_signature}")
    
    # Wait for sell confirmation
    sell_confirmed = await confirm_transaction(env_keys, sell_signature)
    
    if sell_confirmed:
        print("✅ Sell confirmed!")
        print("\n🎉 LIVE TEST COMPLETE - MEV EXECUTOR WORKS!")
        print("✅ Your MEV bot successfully bought and sold on the blockchain!")
    else:
        print("❌ Sell confirmation failed")
    
    print("\n" + "=" * 60)
    print("💡 Test Results:")
    print(f"   Buy: {'✅ SUCCESS' if buy_confirmed else '❌ FAILED'}")
    print(f"   Sell: {'✅ SUCCESS' if sell_confirmed else '❌ FAILED'}")
    
    if buy_confirmed and sell_confirmed:
        print("🏆 FULL SUCCESS - Your MEV executor is working perfectly!")

if __name__ == "__main__":
    asyncio.run(run_live_test())
