import asyncio
import logging
import base58
from solana.rpc.async_api import AsyncClient
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.message import MessageHeader
from solders.message.v0 import Message, LoadedAddresses
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
TEST_AMOUNT = int(0.01 * 1_000_000_000)  # 0.01 SOL in lamports
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")

async def send_test_transaction(client: AsyncClient, keypair: Keypair) -> bool:
    try:
        # Create transfer instruction data
        data = bytes([2, 0, 0, 0]) + TEST_AMOUNT.to_bytes(8, 'little')
        
        instruction = Instruction(
            program_id=SYSTEM_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=keypair.pubkey(), is_signer=False, is_writable=True)
            ],
            data=data
        )
        
        # Get blockhash
        recent = await client.get_latest_blockhash()
        if not recent.value:
            raise Exception("Failed to get blockhash")
        
        # Construct message manually
        message = Message(
            header=MessageHeader(1, 0, 1),
            account_keys=[keypair.pubkey()],
            recent_blockhash=Hash.from_string(str(recent.value.blockhash)),
            instructions=[instruction],
            address_table_lookups=LoadedAddresses([], [])
        )
        
        # Build transaction
        transaction = VersionedTransaction(message, [keypair])
        
        # Send transaction
        logging.info("Sending transaction...")
        signature = await client.send_transaction(transaction)
        
        if not signature.value:
            raise Exception("Failed to send transaction")
            
        logging.info(f"Transaction sent: {signature.value}")
        
        # Confirm transaction
        for _ in range(30):
            confirm = await client.confirm_transaction(signature.value)
            if confirm.value:
                tx = await client.get_transaction(signature.value, encoding="jsonParsed")
                if tx.value and tx.value.meta and not tx.value.meta.err:
                    logging.info("Transaction confirmed successfully!")
                    return True
                elif tx.value and tx.value.meta:
                    logging.error(f"Transaction failed: {tx.value.meta.err}")
                    return False
            await asyncio.sleep(1)
            print(".", end="", flush=True)
        
        logging.error("Transaction confirmation timed out")
        return False
        
    except Exception as e:
        logging.error(f"Error sending transaction: {str(e)}")
        return False

async def main():
    print("\n🚀 Testing Transaction")
    print("=====================")
    
    try:
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        logging.info(f"Loaded wallet: {keypair.pubkey()}")
    except Exception as e:
        logging.error(f"Failed to load wallet: {str(e)}")
        return
        
    client = AsyncClient(kz.HELIUS_RPC_URL)
    
    try:
        balance = await client.get_balance(keypair.pubkey())
        if balance.value:
            sol_balance = balance.value / 1_000_000_000
            logging.info(f"Initial balance: {sol_balance:.4f} SOL")
        
        success = await send_test_transaction(client, keypair)
        
        if success:
            balance = await client.get_balance(keypair.pubkey())
            if balance.value:
                sol_balance = balance.value / 1_000_000_000
                logging.info(f"Final balance: {sol_balance:.4f} SOL")
            
            print("\n✅ Test successful!")
            print("Check test_trade.log for transaction details")
        else:
            print("\n❌ Test failed!")
            print("Check test_trade.log for error details")
            
    except Exception as e:
        logging.error(f"Error: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
