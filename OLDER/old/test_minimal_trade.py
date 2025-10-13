import asyncio
import logging
from solana.rpc.async_api import AsyncClient
import base58
from env_keys import kz
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction
from solders.message import Message
from solders.transaction import VersionedTransaction, Transaction
from solders.system_program import ID as SYS_PROGRAM_ID

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
TEST_AMOUNT = 0.01  # SOL in lamports
LAMPORTS_PER_SOL = 1_000_000_000

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / LAMPORTS_PER_SOL
    return 0.0

def create_transfer_instruction(from_pubkey: Pubkey, to_pubkey: Pubkey, amount_lamports: int) -> Instruction:
    """Create a transfer instruction"""
    keys = [
        AccountMeta(pubkey=from_pubkey, is_signer=True, is_writable=True),
        AccountMeta(pubkey=to_pubkey, is_signer=False, is_writable=True),
    ]
    
    # System program transfer instruction: 0x02 followed by the 64-bit little-endian amount
    data = bytes([2, 0, 0, 0]) + amount_lamports.to_bytes(8, 'little')
    
    return Instruction(
        program_id=SYS_PROGRAM_ID,
        accounts=keys,
        data=data
    )

async def send_test_transaction(client: AsyncClient, keypair: Keypair) -> bool:
    """Execute a test self-transfer transaction"""
    try:
        amount_lamports = int(TEST_AMOUNT * LAMPORTS_PER_SOL)
        
        # Get recent blockhash
        recent_blockhash = await client.get_latest_blockhash()
        if not recent_blockhash.value:
            raise Exception("Failed to get recent blockhash")
            
        # Create transfer instruction
        transfer_ix = create_transfer_instruction(
            keypair.pubkey(),
            keypair.pubkey(),
            amount_lamports
        )
        
        # Create message
        message = Message.new_with_blockhash(
            [transfer_ix],
            keypair.pubkey(),
            recent_blockhash.value.blockhash
        )
        
        # Create and sign transaction
        transaction = Transaction.new_signed_with_payer(
            [transfer_ix],
            keypair.pubkey(),
            [keypair],
            recent_blockhash.value.blockhash
        )
        
        # Send transaction
        logging.info("Sending test transaction...")
        response = await client.send_transaction(transaction)
        
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
