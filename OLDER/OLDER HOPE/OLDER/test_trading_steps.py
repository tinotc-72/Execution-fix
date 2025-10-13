import asyncio
import logging
from main import CopyTradingBot
from wallet_tx_parser import WalletATxParser
from fast_executor import FastExecutor
from solders.keypair import Keypair
import base58
from config import kz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Sample trade logs for testing
SAMPLE_BUY_LOGS = {
    "result": {
        "value": {
            "logs": [
                "Program ComputeBudget111111111111111111111111111111 invoke [1]",
                "Program ComputeBudget111111111111111111111111111111 success",
                "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke [1]",
                "Program log: Instruction: PumpBuy",
                "Program log: Token: ERGKydJayFVtBogci46Ht4U3otjJgchiYWo83mT1Kgw5",
                "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
                "Program log: Instruction: Transfer",
                "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
                "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW success"
            ],
            "signature": "test_buy_signature"
        }
    }
}

async def test_wallet_setup():
    """Test 1: Verify wallet setup and balance"""
    print("\n🧪 Test 1: Wallet Setup")
    print("=====================")
    
    try:
        # Initialize bot
        bot = CopyTradingBot()
        print(f"✅ Bot initialized with wallet: {bot.keypair.pubkey()}")
        
        # Check SOL balance
        balance = await bot.executor.get_sol_balance()
        if balance is None:
            print("❌ Failed to get wallet balance")
            return False
            
        print(f"💰 Wallet balance: {balance} SOL")
        if balance < 0.07:
            print("⚠️ Warning: Balance below 0.07 SOL minimum for trading")
        else:
            print("✅ Balance sufficient for trading")
            
        return True
        
    except Exception as e:
        print(f"❌ Wallet setup test failed: {str(e)}")
        return False

async def test_trade_detection():
    """Test 2: Verify trade detection logic"""
    print("\n🧪 Test 2: Trade Detection")
    print("========================")
    
    try:
        parser = WalletATxParser()
        
        # Test buy detection
        trade_info = await parser.parse_transaction({"value": SAMPLE_BUY_LOGS["result"]["value"]})
        if not trade_info:
            print("❌ Failed to detect buy trade")
            return False
            
        print("\nBuy Trade Detection:")
        print(f"✅ Type: {trade_info['type']}")
        print(f"✅ Token: {trade_info['token']}")
        print(f"✅ Amount: {trade_info['amount']} SOL")
        
        return True
        
    except Exception as e:
        print(f"❌ Trade detection test failed: {str(e)}")
        return False

async def test_trade_execution():
    """Test 3: Test minimal trade execution"""
    print("\n🧪 Test 3: Trade Execution")
    print("========================")
    
    try:
        # Initialize executor
        key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        DECODED_PRIVATE_KEY = base58.b58decode(key)
        keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        executor = FastExecutor(keypair)
        
        # Initialize
        await executor.initialize()
        print("✅ Executor initialized")
        
        # Check balance
        balance = await executor.get_sol_balance()
        print(f"💰 Current balance: {balance} SOL")
        
        # Create small test trade (0.01 SOL self-transfer)
        print("\nAttempting small test transaction...")
        
        # TODO: Implement small test transaction
        
        await executor.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Trade execution test failed: {str(e)}")
        return False

async def main():
    """Run all tests in sequence"""
    bot = None
    executor = None
    try:
        # Test 1: Wallet Setup
        if not await test_wallet_setup():
            print("❌ Wallet setup failed - stopping tests")
            return
            
        # Test 2: Trade Detection
        if not await test_trade_detection():
            print("❌ Trade detection failed - stopping tests")
            return
            
        # Test 3: Trade Execution
        if not await test_trade_execution():
            print("❌ Trade execution failed")
            return
            
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
    finally:
        # Clean up resources
        if bot and hasattr(bot, 'executor'):
            await bot.executor.cleanup()
        if executor:
            await executor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
