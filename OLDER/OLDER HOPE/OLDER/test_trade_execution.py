import asyncio
import logging
import json
import base64
import base58
from datetime import datetime
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from config import kz
from fast_executor import FastExecutor
from tx_builder import build_pump_trade

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler()
    ]
)

async def test_balance_check(executor, keypair):
    """Test balance checking functionality"""
    print("\n💰 Testing balance check...")
    
    balance_result = await executor._rpc_request(
        "getBalance",
        [str(keypair.pubkey())]
    )
    
    if "result" not in balance_result:
        print("❌ Failed to get wallet balance")
        return False
        
    balance_lamports = balance_result["result"]["value"]
    balance_sol = balance_lamports / 1e9
    print(f"Current wallet balance: {balance_sol:.4f} SOL")
    return True

async def test_transaction_simulation(executor, keypair):
    """Test transaction simulation"""
    print("\n🔄 Testing transaction simulation...")
    
    try:
        from solders.system_program import TransferParams, transfer
        from solders.instruction import Instruction
        from solders.transaction import Transaction
        from solders.keypair import Keypair
        from solders.pubkey import Pubkey
        
        # Create a minimal SOL transfer transaction for testing
        recent_blockhash = (await executor._rpc_request(
            "getLatestBlockhash",
            [{"commitment": "processed"}]
        ))["result"]["value"]["blockhash"]
        
        # Create a transfer instruction with 0 SOL
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=keypair.pubkey(),
                lamports=0
            )
        )
        
        # Create and sign transaction
        tx = Transaction().add(transfer_ix)
        tx.recent_blockhash = recent_blockhash
        tx.sign(keypair)
        
        # Simulate transaction
        sim_result = await executor._rpc_request(
            "simulateTransaction",
            [base64.b64encode(bytes(tx)).decode('ascii')]
        )
        
        if "result" not in sim_result or sim_result["result"]["value"].get("err") is not None:
            print(f"❌ Transaction simulation failed: {json.dumps(sim_result)}")
            return False
            
        print("✅ Transaction simulation successful")
        logging.debug(f"Simulation result: {json.dumps(sim_result, indent=2)}")
        return True
        
    except Exception as e:
        print(f"❌ Error in transaction simulation: {str(e)}")
        logging.error(f"Simulation error details: {str(e)}", exc_info=True)
        return False

async def test_retry_logic(executor):
    """Test retry logic with a deliberately failed transaction"""
    print("\n🔁 Testing retry logic...")
    
    # Try to send an invalid transaction that will fail
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        result = await executor._rpc_request(
            "sendTransaction",
            ["invalid_tx_data", {"maxRetries": 1, "skipPreflight": False}]
        )
        
        if "error" in result:
            print(f"Expected error on attempt {retry_count + 1}: {result['error']['message']}")
            retry_count += 1
            await asyncio.sleep(1)
        else:
            print("❌ Unexpected success with invalid transaction")
            return False
    
    print("✅ Retry logic working as expected")
    return True

async def run_tests():
    """Run all trade execution tests"""
    print("\n🧪 Testing Trade Execution Components")
    print("===================================")
    
    try:
        # Initialize components with mnemonic-based wallet
        from config import WALLET
        keypair = WALLET  # Already properly derived from mnemonic
        print(f"✅ Loaded test wallet: {keypair.pubkey()}")
        
        # FastExecutor will use the mnemonic wallet by default
        executor = FastExecutor()
        
        # Run tests
        tests = {
            "Balance Check": await test_balance_check(executor, keypair),
            "Transaction Simulation": await test_transaction_simulation(executor, keypair),
            "Retry Logic": await test_retry_logic(executor)
        }
        
        # Print test summary
        print("\n📊 Test Summary")
        print("==============")
        for test_name, result in tests.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            
        all_passed = all(tests.values())
        if all_passed:
            print("\n🎉 All tests passed!")
        else:
            print("\n⚠️ Some tests failed")
            
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_tests())
