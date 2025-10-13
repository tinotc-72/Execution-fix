import asyncio
import logging
from datetime import datetime
import json
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from wallet_tx_parser import WalletATxParser
from tx_builder import build_pump_trade
from fast_executor import FastExecutor
from config import kz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_pump_trade.log'),
        logging.StreamHandler()
    ]
)

# Sample Pump.fun trade from wallet A
SAMPLE_TRADE = {
    "value": {
        "signature": "3zz7xPiKSjud4224Jp7CSid9Qbf1QfREvWAfNdh3KEmvxdZu4F6W8YjHannMNqK9JCsNyBmYMkDbGk31vZLQWM4p",
        "err": None,
        "logs": [
            "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke [1]",
            "Program log: Instruction: PumpBuy",
            "Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P invoke [2]",
            "Program log: Instruction: Buy",
            "Program data: vdt/007mYe54baTH8YZAzX2YK7dmS6MzE76uVcW1yCCNjc1GM6SpP5PnRa8AAAAAv4YT+0JKAAABDQrJSOqMzHXMXQxQqrnfCaHHahKftcI3VjpunWx2xnqiuFZoAAAAAHpv90YIAAAAbjL0k4Y3AwB6w9NKAQAAAG6a4Uf1OAIAg4R0KS5nWpS0NuywqZiJQjKKg93GIzgClhJnxc1hF8tfAAAAAAAAAJxDqgEAAAAAASLoKwMOQcY6slkkLP6yfWzEKjSaGq2fX1KlaE+0MTkFAAAAAAAAAFpvFgAAAAAA",
        ]
    }
}

async def test_full_trade_flow():
    """Test the complete trade flow from parsing to execution"""
    print("\n🧪 Testing Complete Pump.fun Trade Flow")
    print("=====================================")
    
    # Initialize components
    parser = WalletATxParser()
    keypair = Keypair.from_bytes(base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip()))
    executor = FastExecutor(keypair)
    await executor.initialize()
    
    try:
        # 1. Parse the trade
        print("\n1️⃣ Parsing trade...")
        trade_info = await parser.parse_transaction(SAMPLE_TRADE)
        
        if not trade_info:
            print("❌ Failed to parse trade")
            return
            
        print(f"✅ Successfully parsed trade:")
        print(f"Type: {trade_info['type']}")
        print(f"Token: {trade_info['token']}")
        print(f"Amount: {trade_info['amount']} SOL")
        
        # 2. Build the transaction
        print("\n2️⃣ Building transaction...")
        tx = await build_pump_trade(
            executor=executor,
            token=trade_info['token'],
            amount=trade_info['amount'],
            trade_type=trade_info['type'],
            keypair=keypair
        )
        
        if not tx:
            print("❌ Failed to build transaction")
            return
            
        print("✅ Successfully built transaction")
        
        # 3. Simulate the transaction (optional)
        print("\n3️⃣ Simulating transaction...")
        sim_result = await executor.simulate_transaction(tx)
        
        if sim_result.get("err"):
            print(f"❌ Simulation failed: {sim_result['err']}")
            return
            
        print("✅ Transaction simulation successful")
        
        # 4. Execute the transaction (commented out for safety)
        """
        print("\n4️⃣ Executing transaction...")
        signature = await executor.execute_transaction(tx)
        
        if signature:
            print(f"✅ Transaction executed: {signature}")
        else:
            print("❌ Transaction execution failed")
        """
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        await executor.cleanup()

if __name__ == "__main__":
    asyncio.run(test_full_trade_flow())
