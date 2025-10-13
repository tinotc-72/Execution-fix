import asyncio
import logging
import traceback
from datetime import datetime
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from env_keys import kz
from fast_executor import FastExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_trade.log'),
        logging.StreamHandler()
    ]
)

# Test configurations
TEST_AMOUNTS = [0.001, 0.01, 0.1]  # Test different SOL amounts
MIN_BALANCE = 0.2  # Minimum SOL needed for tests

async def get_balance(executor: FastExecutor, pubkey: Pubkey) -> float:
    """Get wallet balance in SOL with commitment level."""
    try:
        # Check balance with finalized commitment for accuracy
        result = await executor._rpc_request(
            "getBalance",
            [
                str(pubkey),
                {"commitment": "finalized"}
            ],
            endpoint="https://api.mainnet-beta.solana.com"  # Use public RPC for reliable balance checks
        )
        if "result" in result and "value" in result["result"]:
            return result["result"]["value"] / 1e9
        return 0.0
    except Exception as e:
        logging.error(f"Error getting balance: {e}")
        return 0.0

async def execute_test_trade(executor: FastExecutor, amount: float) -> tuple[bool, str]:
    """Execute a test trade with enhanced verification."""
    try:
        # Get initial balance with retries
        retry_count = 0
        initial_balance = None
        while retry_count < 3 and initial_balance is None:
            initial_balance = await get_balance(executor, executor.keypair.pubkey())
            if initial_balance > 0:
                break
            retry_count += 1
            await asyncio.sleep(1)
        
        if initial_balance is None:
            return False, "Failed to get initial balance"
        
        logging.info(f"\n💰 Starting Test Trade")
        logging.info(f"Initial Balance: {initial_balance:.6f} SOL")
        logging.info(f"Trade Amount: {amount:.6f} SOL")

        # Create transfer instruction
        amount_lamports = int(amount * 1e9)
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=executor.keypair.pubkey(),
                to_pubkey=executor.keypair.pubkey(),
                lamports=amount_lamports
            )
        )

        # Execute transaction
        signature = await executor.build_and_execute(
            instructions=[transfer_ix],
            use_jito=True,
            jito_retries=2,
            jito_timeout=1.0
        )
        
        if not signature:
            return False, "Transaction submission failed"
            
        logging.info(f"🔑 Transaction submitted: {signature}")
        
        # Verify transaction status with detailed info
        success, tx_info = await executor.verify_transaction_status(signature)
        
        if not success:
            return False, f"Transaction verification failed: {tx_info.get('error', 'Unknown error')}"
            
        # Get final balance with retries
        retry_count = 0
        max_retries = 5
        final_balance = None
        
        while retry_count < max_retries:
            await asyncio.sleep(1.5 ** retry_count)  # Exponential backoff
            final_balance = await get_balance(executor, executor.keypair.pubkey())
            
            if final_balance is not None:
                fee = tx_info.get("fee", 0) / 1e9  # Convert lamports to SOL
                balance_change = abs(final_balance - initial_balance)
                
                logging.info(f"\n📊 Trade Summary:")
                logging.info(f"Final Balance: {final_balance:.6f} SOL")
                logging.info(f"Fee Paid: {fee:.6f} SOL")
                logging.info(f"Total Balance Change: {balance_change:.6f} SOL")
                
                # Verify fee was deducted
                if fee > 0:
                    return True, f"Trade successful - Fee paid: {fee:.6f} SOL"
                else:
                    logging.warning("⚠️ No fee detected - checking transaction info...")
                    compute_units = tx_info.get("compute_units", 0)
                    if compute_units > 0:
                        logging.info(f"Compute units used: {compute_units:,}")
                        return True, "Trade executed (verified by compute units)"
            
            retry_count += 1
        
        return False, "Could not verify balance change"
            
    except Exception as e:
        logging.error(f"Test trade error: {str(e)}")
        traceback.print_exc()
        return False, str(e)

async def main():
    print("\n🚀 FastExecutor Trade Testing")
    print("============================")
    
    try:
        # Load wallet
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        logging.info(f"Loaded wallet: {keypair.pubkey()}")

        # Initialize FastExecutor
        async with FastExecutor(keypair) as executor:
            # Verify sufficient balance for all tests
            initial_balance = await get_balance(executor, keypair.pubkey())
            logging.info(f"Initial wallet balance: {initial_balance:.4f} SOL")

            if initial_balance < MIN_BALANCE:
                logging.error(f"Insufficient balance. Need at least {MIN_BALANCE:.4f} SOL")
                return False

            # Run test trades with different amounts
            results = []
            for amount in TEST_AMOUNTS:
                print(f"\n📊 Testing {amount} SOL trade...")
                success, result = await execute_test_trade(executor, amount)
                results.append((amount, success, result))
                # Small delay between trades
                await asyncio.sleep(1)

            # Print summary
            print("\n📝 Test Results Summary:")
            print("------------------------")
            all_passed = True
            for amount, success, result in results:
                status = "✅ Passed" if success else "❌ Failed"
                print(f"{status} - {amount} SOL trade: {result}")
                all_passed = all_passed and success

            # Final balance check
            final_balance = await get_balance(executor, keypair.pubkey())
            total_fees = (initial_balance - final_balance) * 1e9  # lamports
            
            print("\n💰 Balance Summary:")
            print(f"Initial balance: {initial_balance:.4f} SOL")
            print(f"Final balance: {final_balance:.4f} SOL")
            print(f"Total fees: {total_fees:.0f} lamports")
            
            if all_passed:
                print("\n✅ All trade tests passed successfully!")
                return True
            else:
                print("\n⚠️ Some trade tests failed. Check logs for details.")
                return False

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(main())
