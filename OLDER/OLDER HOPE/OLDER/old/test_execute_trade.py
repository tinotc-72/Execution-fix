import asyncio
import logging
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.system_program import transfer, TransferParams
import base58
from solders.hash import Hash
from solders.message.v0 import MessageHeader, Message, LoadedAddresses
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
TEST_AMOUNT = 0.01  # SOL
COMPUTE_UNITS = 200_000
PRIORITY_FEE = 1_000_000  # 0.001 SOL

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def execute_test_trade(client: AsyncClient, keypair: Keypair) -> bool:
    """Execute a test trade (self-transfer) with the prepared wallet"""
    try:
        # Convert amount to lamports
        amount_lamports = int(TEST_AMOUNT * 1e9)
        
        # Get recent blockhash
        recent = await client.get_latest_blockhash()
        if not recent.value:
            raise Exception("Failed to get recent blockhash")
        
        # Create instructions
        compute_limit_ix = set_compute_unit_limit(COMPUTE_UNITS)
        compute_price_ix = set_compute_unit_price(PRIORITY_FEE)
        
        # Create transfer instruction (self-transfer for testing)
        transfer_params = TransferParams(
            from_pubkey=keypair.pubkey(),
            to_pubkey=keypair.pubkey(),
            lamports=amount_lamports
        )
        transfer_ix = transfer(transfer_params)
        
        # Combine all instructions
        instructions = [
            compute_limit_ix,
            compute_price_ix,
            transfer_ix
        ]
        
        # Create message
        message = Message(
            header=MessageHeader(
                num_required_signatures=1,
                num_readonly_signed_accounts=0,
                num_readonly_unsigned_accounts=1
            ),
            account_keys=[keypair.pubkey()],  # Replace with full unique account list if needed
            recent_blockhash=Hash.from_string(str(recent.value.blockhash)),
            instructions=instructions,
            address_table_lookups=[]
        )
        
        # Create and sign transaction
        tx = VersionedTransaction(message, [keypair])
        
        # Send and confirm transaction
        logging.info(f"Sending test trade ({TEST_AMOUNT} SOL)...")
        result = await client.send_transaction(tx)
        
        if not result.value:
            raise Exception("Failed to send transaction")
            
        signature = result.value
        logging.info(f"Transaction sent: {signature}")
        
        # Wait for confirmation
        for _ in range(30):
            resp = await client.confirm_transaction(signature)
            if resp.value:
                tx_details = await client.get_transaction(signature)
                if tx_details.value and tx_details.value.meta and not tx_details.value.meta.err:
                    logging.info("Transaction confirmed successfully!")
                    return True
                elif tx_details.value and tx_details.value.meta:
                    logging.error(f"Transaction failed: {tx_details.value.meta.err}")
                    return False
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
        logging.error("Transaction confirmation timed out")
        return False
            
    except Exception as e:
        logging.error(f"Error executing test trade: {str(e)}")
        return False

async def main():
    print("\n🚀 Executing Test Trade")
    print("======================")
    
    # Load wallet
    try:
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
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
            
        # Execute the test trade
        success = await execute_test_trade(client, keypair)
        
        if success:
            # Verify final balance
            final_balance = await get_balance(client, keypair.pubkey())
            logging.info(f"Final balance: {final_balance:.4f} SOL")
            logging.info(f"Transaction fee: {(initial_balance - final_balance):.6f} SOL")
            
            print("\n✅ Test trade successful!")
            print("Check test_trade.log for detailed information")
            print("\nNext steps:")
            print("1. Verify transaction in your Solana explorer")
            print("2. Monitor wallet balance")
            print("3. Ready to proceed with real trading setup")
        else:
            print("\n❌ Test trade failed!")
            print("Check test_trade.log for error details")
            
    except Exception as e:
        logging.error(f"Error during test: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
