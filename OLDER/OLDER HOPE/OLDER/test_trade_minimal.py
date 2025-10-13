"""
Test script for executing a minimal buy/sell trade sequence.
Uses 0.01 SOL for testing trade execution.
"""

import asyncio
import logging
import traceback
from datetime import datetime
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address

# Import core components
from fast_executor import FastExecutor
from minimal_tx_builder import (
    build_buy_tx,
    build_sell_tx,
    PUMP_ROUTER,
    TOKEN_PROGRAM_ID,
    ATA_PROGRAM_ID
)
from config import kz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
TEST_TOKEN_MINT = "63Uxys56GcQDWh93YTtgCmD4qfLW6VPrUeB1JjT8CNEe"
TEST_AMOUNT_SOL = 0.01  # Small amount for testing
MIN_SOL_BALANCE = 0.02  # Minimum SOL needed (including fees)

# Trading parameters - same as main.py will use
SLIPPAGE_BPS = 3000  # 30% slippage
FIXED_BUY_AMOUNT = 0.01  # Test with smaller amount

async def execute_test_trades():
    """Execute a test buy and sell sequence"""
    try:
        print("\n🧪 Starting Test Trade Sequence")
        print("==============================")
        
        # Use mnemonic-based wallet from config
        from config import WALLET
        keypair = WALLET  # Already properly derived from mnemonic
        print(f"🔑 Wallet loaded: {keypair.pubkey()}")
        
        # Initialize FastExecutor (it will use the mnemonic wallet by default)
        executor = FastExecutor()
        await executor.initialize()
        print("✅ FastExecutor initialized")
        
        # Check SOL balance
        balance = await executor.get_balance(keypair.pubkey())
        if balance is None or balance < MIN_SOL_BALANCE:
            print(f"❌ Insufficient balance: {balance} SOL")
            print(f"Need at least {MIN_SOL_BALANCE} SOL for test")
            return
        print(f"💰 Current balance: {balance} SOL")
        
        # Convert token mint string to Pubkey
        token_pubkey = Pubkey.from_string(TEST_TOKEN_MINT)
        
        # Get token ATA
        token_ata = get_associated_token_address(keypair.pubkey(), token_pubkey)
        print(f"📝 Token ATA: {token_ata}")
        
        # Check initial token balance
        initial_token_balance = await executor.get_token_balance(
            keypair.pubkey(),
            token_pubkey
        )
        print(f"📊 Initial token balance: {initial_token_balance or 0}")
        
        # Execute buy
        print("\n🛒 Executing test buy...")
        amount_lamports = int(TEST_AMOUNT_SOL * 1_000_000_000)
        buy_tx = await build_buy_tx(
            executor=executor,
            token=token_pubkey,
            amount=amount_lamports,
            keypair=keypair,
            slippage_bps=SLIPPAGE_BPS  # 30% slippage
        )
        
        if not buy_tx:
            print("❌ Failed to build buy transaction")
            return
            
        buy_result = await executor.execute_transaction(buy_tx)
        if not buy_result:
            print("❌ Buy transaction failed")
            return
        print("✅ Buy transaction successful!")
        
        # Wait a moment and check new balance
        print("\n⏳ Waiting for token balance update...")
        await asyncio.sleep(2)
        
        new_token_balance = await executor.get_token_balance(
            keypair.pubkey(),
            token_pubkey
        )
        print(f"📊 New token balance: {new_token_balance or 0}")
        
        if not new_token_balance:
            print("❌ No tokens received from buy")
            return
            
        # Execute sell
        print("\n💰 Executing test sell...")
        sell_tx = await build_sell_tx(
            executor=executor,
            token=token_pubkey,
            amount=new_token_balance,
            keypair=keypair,
            slippage_bps=SLIPPAGE_BPS  # 30% slippage
        )
        
        if not sell_tx:
            print("❌ Failed to build sell transaction")
            return
            
        sell_result = await executor.execute_transaction(sell_tx)
        if not sell_result:
            print("❌ Sell transaction failed")
            return
        print("✅ Sell transaction successful!")
        
        # Final balance check
        await asyncio.sleep(2)
        final_token_balance = await executor.get_token_balance(
            keypair.pubkey(),
            token_pubkey
        )
        final_sol_balance = await executor.get_balance(keypair.pubkey())
        
        print("\n📊 Final Results")
        print("===============")
        print(f"Final token balance: {final_token_balance or 0}")
        print(f"Final SOL balance: {final_sol_balance} SOL")
        print(f"SOL change: {final_sol_balance - balance} SOL")
        
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        traceback.print_exc()
    finally:
        # Cleanup
        await executor.cleanup()
        print("\n🧹 Cleaned up FastExecutor")

if __name__ == "__main__":
    try:
        asyncio.run(execute_test_trades())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        traceback.print_exc()
