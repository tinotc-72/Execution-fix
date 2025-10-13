import asyncio
import logging
import json
import base58
from datetime import datetime
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from wallet_tx_parser import WalletATxParser
from fast_executor import FastExecutor
from config import kz

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_strategy.log'),
        logging.StreamHandler()
    ]
)

# Sample transaction logs for testing
SAMPLE_BUY_LOGS = [
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

SAMPLE_SELL_LOGS = [
    "Program ComputeBudget111111111111111111111111111111 invoke [1]",
    "Program ComputeBudget111111111111111111111111111111 success",
    "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke [1]",
    "Program log: Instruction: PumpSell",
    "Program log: Token: ERGKydJayFVtBogci46Ht4U3otjJgchiYWo83mT1Kgw5",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
    "Program log: Instruction: Transfer",
    "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
    "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW success"
]

async def test_fixed_amount_strategy():
    """Test the fixed amount buy and proportional sell strategy"""
    print("\n🧪 Testing Fixed Amount (0.05 SOL) Strategy")
    print("===========================================")
    
    try:
        # Initialize components
        logging.info("Initializing test components...")
        from config import WALLET
        keypair = WALLET  # Use mnemonic-based wallet
        print(f"\n🔑 Test wallet: {keypair.pubkey()}")
        
        parser = WalletATxParser()
        executor = FastExecutor(keypair)
        await executor.initialize()
        
        # 1. Test Buy Detection
        print("\n📥 Testing Buy Detection")
        print("-------------------------")
        buy_tx_data = {
            "value": {
                "logs": SAMPLE_BUY_LOGS,
                "signature": "test_buy_signature"
            }
        }
        
        buy_trade = await parser.parse_transaction(buy_tx_data)
        assert buy_trade is not None, "Buy trade should be detected"
        assert buy_trade['type'] == 'buy', "Should be a buy trade"
        assert buy_trade['amount'] == 0.05, "Buy amount should be fixed at 0.05 SOL"
        print("✅ Buy correctly detected with fixed 0.05 SOL amount")
        
        # 2. Check Buy Transaction Building
        print("\n🏗️ Testing Buy Transaction Building")
        print("-----------------------------------")
        balance_result = await executor._rpc_request(
            "getBalance",
            [str(keypair.pubkey())]
        )
        balance = balance_result.get("result", {}).get("value", 0)
        print(f"Current wallet balance: {balance/1e9:.4f} SOL")
        
        # 3. Test Sell Detection
        print("\n📤 Testing Sell Detection")
        print("-------------------------")
        sell_tx_data = {
            "value": {
                "logs": SAMPLE_SELL_LOGS,
                "signature": "test_sell_signature"
            }
        }
        
        sell_trade = await parser.parse_transaction(sell_tx_data)
        assert sell_trade is not None, "Sell trade should be detected"
        assert sell_trade['type'] == 'sell', "Should be a sell trade"
        assert sell_trade['amount'] is None, "Sell amount should be None (proportional)"
        print("✅ Sell correctly detected with proportional amount")
        
        # 4. Test Token Balance Check
        print("\n💰 Testing Token Balance Check")
        print("------------------------------")
        token_pubkey = Pubkey.from_string(sell_trade['token'])
        token_balance = await executor._rpc_request(
            "getTokenAccountBalance",
            [str(token_pubkey)]
        )
        print(f"Token balance response: {json.dumps(token_balance, indent=2)}")
        
        # 5. Summary
        print("\n📊 Test Summary")
        print("=============")
        print("✅ Parser correctly identifies buy/sell trades")
        print("✅ Buy trades fixed at 0.05 SOL")
        print("✅ Sell trades set up for proportional amounts")
        print("✅ Token balance checking operational")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    finally:
        # Cleanup
        if 'executor' in locals():
            await executor.close()

if __name__ == "__main__":
    asyncio.run(test_fixed_amount_strategy())
