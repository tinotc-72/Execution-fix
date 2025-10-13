import asyncio
import logging
from main import CopyTradingBot
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_bot_startup():
    """Test the complete bot startup sequence"""
    bot = None
    try:
        print("\n🧪 Testing Bot Startup")
        print("====================")
        
        # 1. Initialize bot
        print("\n1️⃣ Testing Bot Initialization")
        bot = CopyTradingBot()
        print("✅ Bot instance created")
        
        # 2. Test wallet loading
        print(f"\n2️⃣ Testing Wallet Configuration")
        print(f"Wallet public key: {bot.keypair.pubkey()}")
        
        # 3. Test RPC connection
        print("\n3️⃣ Testing RPC Connection")
        balance = await bot.executor.get_sol_balance()
        print(f"Wallet balance: {balance} SOL")
        
        # 4. Test WebSocket connection
        print("\n4️⃣ Testing WebSocket Connection")
        ws = await bot.connect_websocket()
        if ws:
            print("✅ WebSocket connection successful")
            await ws.close()
        else:
            print("❌ WebSocket connection failed")
            return
        
        print("\n✅ All startup tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Startup test failed: {str(e)}")
        print(traceback.format_exc())
        return False
    finally:
        if bot and hasattr(bot, 'executor'):
            await bot.executor.cleanup()

if __name__ == "__main__":
    asyncio.run(test_bot_startup())
