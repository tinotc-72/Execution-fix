import asyncio
import logging
import json
from main import CopyTradingBot
import base58
from solders.keypair import Keypair
from config import kz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_main.log'),
        logging.StreamHandler()
    ]
)

# Sample Pump.fun transaction logs
SAMPLE_LOGS = {
    "jsonrpc": "2.0",
    "method": "logsNotification",
    "params": {
        "result": {
            "context": {"slot": 1234567},
            "value": {
                "signature": "test_signature",
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
                ]
            }
        }
    }
}

async def test_bot_initialization():
    """Test 1: Bot Initialization"""
    print("\n🧪 Test 1: Bot Initialization")
    print("============================")
    
    try:
        # Create bot instance
        bot = CopyTradingBot()
        print(f"✅ Bot created with wallet: {bot.keypair.pubkey()}")
        
        # Initialize components
        success = await bot.initialize()
        if not success:
            print("❌ Bot initialization failed")
            return False
            
        print("✅ Bot initialized successfully")
        
        # Check wallet balance
        balance = await bot.executor.get_sol_balance()
        if balance is None:
            print("❌ Failed to get wallet balance")
            return False
            
        print(f"💰 Wallet balance: {balance} SOL")
        if balance < 0.07:
            print("⚠️ Warning: Low balance, minimum 0.07 SOL recommended")
            
        await bot.executor.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Initialization test failed: {str(e)}")
        return False

async def test_trade_detection():
    """Test 2: Trade Detection"""
    print("\n🧪 Test 2: Trade Detection")
    print("=========================")
    
    try:
        bot = CopyTradingBot()
        await bot.initialize()
        
        # Test trade detection
        await bot.handle_transaction(SAMPLE_LOGS["params"])
        print("✅ Trade detection test completed")
        
        await bot.executor.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Trade detection test failed: {str(e)}")
        return False

async def test_full_trade_flow():
    """Test 3: Complete Trade Flow"""
    print("\n🧪 Test 3: Complete Trade Flow")
    print("============================")
    
    try:
        bot = CopyTradingBot()
        await bot.initialize()
        
        # 1. Parse trade
        trade_info = await bot.parser.parse_transaction({"value": SAMPLE_LOGS["params"]["result"]["value"]})
        if not trade_info:
            print("❌ Failed to parse trade")
            return False
            
        print(f"✅ Trade parsed successfully:")
        print(f"   Type: {trade_info['type']}")
        print(f"   Token: {trade_info['token']}")
        print(f"   Amount: {trade_info['amount'] if trade_info['amount'] else 'SELL ALL'}")
        
        # 2. Execute trade
        success = await bot.execute_trade(trade_info)
        print(f"{'✅' if success else '❌'} Trade execution: {'Success' if success else 'Failed'}")
        
        await bot.executor.cleanup()
        return success
        
    except Exception as e:
        print(f"❌ Full trade flow test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("\n🧪 Starting Main.py Tests")
    print("======================")
    
    results = {
        "Initialization": await test_bot_initialization(),
        "Trade Detection": await test_trade_detection(),
        "Full Trade Flow": await test_full_trade_flow()
    }
    
    print("\n📊 Test Results:")
    print("==============")
    for test, passed in results.items():
        print(f"{test}: {'✅ PASSED' if passed else '❌ FAILED'}")
    
    all_passed = all(results.values())
    print(f"\n🏁 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
