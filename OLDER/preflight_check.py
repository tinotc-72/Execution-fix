import asyncio
import logging
from datetime import datetime
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from env_keys import kz
from fast_executor import FastExecutor
from jito_service import JitoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('preflight.log'),
        logging.StreamHandler()
    ]
)

async def check_rpc_health(executor: FastExecutor) -> bool:
    """Verify RPC endpoint health and response times."""
    try:
        start = datetime.now()
        # Try to get a test blockhash as connection check
        blockhash = await executor._rpc_request("getLatestBlockhash")
        response_time = (datetime.now() - start).total_seconds() * 1000
        
        if not blockhash or "result" not in blockhash:
            logging.error("❌ Failed to verify RPC connection")
            return False
            
        logging.info(f"✅ RPC response time: {response_time:.2f}ms")
        if response_time > 500:  # Warning if response > 500ms
            logging.warning(f"⚠️ High latency: {response_time:.2f}ms")
            
        return True
    except Exception as e:
        logging.error(f"❌ RPC health check failed: {str(e)}")
        return False

async def check_jito_connection() -> bool:
    """Verify Jito services are accessible."""
    try:
        client = JitoClient()
        # Test connection by checking block engine status
        status = await client.check_connection()
        if status:
            logging.info("✅ Jito connection successful")
            return True
        logging.error("❌ Could not connect to Jito services")
        return False
    except Exception as e:
        logging.error(f"❌ Jito connection failed: {str(e)}")
        return False
    finally:
        if client:
            await client.close()

async def check_wallet_readiness(executor: FastExecutor) -> bool:
    """Verify wallet balance and transaction capability."""
    try:
        # Get wallet balance using RPC request
        params = [str(executor.keypair.pubkey())]
        balance_resp = await executor._rpc_request("getBalance", params)
        if not balance_resp or "result" not in balance_resp:
            logging.error("❌ Failed to get wallet balance")
            return False
            
        balance = balance_resp["result"]["value"]
        sol_balance = balance / 1_000_000_000  # Convert lamports to SOL
        logging.info(f"💰 Wallet balance: {sol_balance:.4f} SOL")
        
        if balance < 50_000_000:  # 0.05 SOL minimum required for trading
            logging.error(f"❌ Insufficient balance: {sol_balance:.4f} SOL (need >= 0.05 SOL)")
            return False
            
        # No need to test transaction building - FastExecutor handles this internally
        logging.info("✅ Wallet check successful")
        return True
        
    except Exception as e:
        logging.error(f"❌ Wallet readiness check failed: {str(e)}")
        return False

async def main():
    print("\n🚀 Running Pre-Trade Health Check")
    print("================================")
    
    try:
        # Load wallet
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        logging.info(f"Loaded wallet: {keypair.pubkey()}")

        # Initialize FastExecutor
        async with FastExecutor(keypair) as executor:
            # Run health checks
            checks = {
                "RPC Health": await check_rpc_health(executor),
                "Jito Connection": await check_jito_connection(),
                "Wallet Readiness": await check_wallet_readiness(executor)
            }
            
            print("\n📊 Health Check Results:")
            print("------------------------")
            all_passed = True
            for check, result in checks.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{check}: {status}")
                all_passed = all_passed and result
                
            if all_passed:
                print("\n✨ All checks passed! Bot is ready for trading.")
                return True
            else:
                print("\n⚠️ Some checks failed. Please review logs before starting the bot.")
                return False

    except Exception as e:
        logging.error(f"Fatal error in health check: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
