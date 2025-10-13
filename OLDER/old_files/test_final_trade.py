import asyncio
import logging
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
import base58
from env_keys import kz
import struct

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
TEST_AMOUNT = 0.01  # SOL

async def get_balance(client: AsyncClient, pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def send_test_transaction(client: AsyncClient, wallet) -> bool:
    """Execute a test self-transfer transaction"""
    try:
        amount_lamports = int(TEST_AMOUNT * 1e9)
        
        # Create transaction
        transaction = Transaction()
        
        # Add transfer instruction
        transaction.add(
            transfer(
                TransferParams(
                    from_pubkey=wallet.public_key(),
                    to_pubkey=wallet.public_key(),
                    lamports=amount_lamports
                )
            )
        )
        
        # Send transaction
        logging.info("Sending test transaction...")
        response = await client.send_transaction(
            transaction,
            wallet
        )
        
        if not response.value:
            raise Exception("Failed to send transaction")
        
        signature = response.value
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
    
    # Load wallet
    try:
        from solana.keypair import Keypair
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_secret_key(private_key)
        logging.info(f"Loaded wallet A: {keypair.public_key()}")
    except Exception as e:
        logging.error(f"Failed to load wallet: {str(e)}")
        return False

    # Connect to mainnet
    client = AsyncClient(kz.HELIUS_RPC_URL)
    try:
        # Check initial balance
        initial_balance = await get_balance(client, keypair.public_key())
        logging.info(f"Initial balance: {initial_balance:.4f} SOL")
        
        if initial_balance < (TEST_AMOUNT + 0.002):  # Amount + fees
            logging.error("Insufficient balance for test trade")
            return False
            
        # Execute test transaction
        success = await send_test_transaction(client, keypair)
        
        if success:
            # Verify final balance
            final_balance = await get_balance(client, keypair.public_key())
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
