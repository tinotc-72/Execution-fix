import asyncio
import logging
from datetime import datetime
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.system_program import TransferParams, transfer_with_seed, ID as SYS_PROGRAM_ID
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
import base58
from env_keys import kz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_trade.log'),
        logging.StreamHandler()
    ]
)

# Constants
COMPUTE_UNITS = 200_000
PRIORITY_FEE = 1_000_000  # 0.001 SOL
TEST_AMOUNT = 0.01  # SOL

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def send_test_transaction(client: AsyncClient, keypair: Keypair) -> bool:
    """Execute a test self-transfer transaction"""
    try:
        amount_lamports = int(TEST_AMOUNT * 1e9)
        
        # Create transfer instruction (sending to self for testing)
        transfer_params = TransferParams(
            from_pubkey=keypair.pubkey(),
            to_pubkey=keypair.pubkey(),
            lamports=amount_lamports
        )
        transfer_ix = transfer_with_seed(transfer_params)
        
        # Add compute budget instructions
        instructions = [
            set_compute_unit_limit(COMPUTE_UNITS),
            set_compute_unit_price(PRIORITY_FEE),
            transfer_ix
        ]

        # Get latest blockhash
        latest_blockhash = await client.get_latest_blockhash()
        if not latest_blockhash.value:
            raise Exception("Failed to get recent blockhash")

        # Create and sign transaction
        message = MessageV0.new_with_blockhash(
            instructions,
            keypair.pubkey(),
            latest_blockhash.value.blockhash
        )
        tx = VersionedTransaction(message, [keypair])

        # Send transaction
        logging.info("Sending test transaction...")
        result = await client.send_transaction(tx)
        if not result.value:
            raise Exception("Failed to send transaction")
        
        signature = result.value
        logging.info(f"Transaction sent: {signature}")
        
        # Wait for confirmation
        for _ in range(60):  # 60 second timeout
            resp = await client.confirm_transaction(signature)
            if resp.value:
                tx_response = await client.get_transaction(signature)
                if tx_response.value and tx_response.value.meta and not tx_response.value.meta.err:
                    logging.info("Transaction confirmed successfully!")
                    return True
                elif tx_response.value and tx_response.value.meta and tx_response.value.meta.err:
                    logging.error(f"Transaction failed: {tx_response.value.meta.err}")
                    return False
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        logging.error("Transaction confirmation timed out")
        return False
        
    except Exception as e:
        logging.error(f"Error executing test transaction: {str(e)}")
        return False

async def main():
    print("\n🚀 Executing Test Trade")
    print("======================")
    
    # Use mnemonic-based wallet from config
    try:
        from config import WALLET
        keypair = WALLET  # Already properly derived from mnemonic
        logging.info(f"Loaded wallet A: {keypair.pubkey()}")
    except Exception as e:
        logging.error(f"Failed to load wallet: {str(e)}")
        return False

    # Connect to mainnet
    client = AsyncClient(kz.HELIUS_RPC_URL)
    try:
        # Check initial balance
        initial_balance = await get_balance(client, keypair.pubkey())
        logging.info(f"Initial balance: {initial_balance:.4f} SOL")
        
        if initial_balance < (TEST_AMOUNT + 0.002):  # Amount + fees
            logging.error("Insufficient balance for test trade")
            return False
            
        # Execute test transaction
        success = await send_test_transaction(client, keypair)
        
        if success:
            # Verify final balance
            final_balance = await get_balance(client, keypair.pubkey())
            logging.info(f"Final balance: {final_balance:.4f} SOL")
            logging.info(f"Transaction fee: {(initial_balance - final_balance):.6f} SOL")
            
            print("\n✅ Test trade successful!")
            print("Check test_trade.log for detailed information")
        else:
            print("\n❌ Test trade failed!")
            print("Check test_trade.log for error details")
            
    except Exception as e:
        logging.error(f"Error during test trade: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
