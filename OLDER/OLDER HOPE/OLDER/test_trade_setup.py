import asyncio
import logging
from datetime import datetime
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.system_program import transfer, TransferParams  # ✅ ADDED MISSING IMPORT
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
WRAPPED_SOL = Pubkey.from_string("So11111111111111111111111111111111111111112")
COMPUTE_UNITS = 200_000
PRIORITY_FEE = 1_000_000  # 0.001 SOL

async def get_balance(client: AsyncClient, pubkey: Pubkey) -> float:
    resp = await client.get_balance(pubkey)
    if resp.value is not None:
        return resp.value / 1e9
    return 0.0

async def build_optimized_transaction(client: AsyncClient, instructions, payer: Pubkey):
    """Build a transaction with compute budget and priority fee"""
    try:
        final_ix = [
            set_compute_unit_limit(COMPUTE_UNITS),
            set_compute_unit_price(PRIORITY_FEE),
            *instructions
        ]

        latest_blockhash = await client.get_latest_blockhash()
        if not latest_blockhash.value:
            raise Exception("Failed to get recent blockhash")

        message = MessageV0.new_with_blockhash(
            final_ix,
            payer,
            latest_blockhash.value.blockhash
        )

        return VersionedTransaction(message, [])
    except Exception as e:
        logging.error(f"Error building transaction: {str(e)}")
        raise

async def verify_transaction(client: AsyncClient, signature: str, max_retries: int = 60) -> bool:
    for i in range(max_retries):
        try:
            resp = await client.confirm_transaction(signature)
            if resp.value:
                tx = await client.get_transaction(signature)
                if tx.value and tx.value.meta and not tx.value.meta.err:
                    return True
                elif tx.value and tx.value.meta and tx.value.meta.err:
                    logging.error(f"Transaction failed: {tx.value.meta.err}")
                    return False
        except Exception as e:
            logging.warning(f"Verification attempt {i+1} failed: {str(e)}")
        await asyncio.sleep(1)
    return False

async def prepare_test_trade():
    logging.info("Starting test trade preparation")
    
    try:
        from config import WALLET
        keypair = WALLET  # Use mnemonic-based wallet
        logging.info(f"Loaded wallet: {keypair.pubkey()}")
    except Exception as e:
        logging.error(f"Failed to load wallet: {str(e)}")
        return False

    client = AsyncClient(kz.HELIUS_RPC_URL)
    try:
        balance = await get_balance(client, keypair.pubkey())
        logging.info(f"Current balance: {balance:.4f} SOL")
        
        if balance < 0.02:
            logging.error("Insufficient balance for test trade")
            return False

        amount_lamports = int(0.001 * 1e9)
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=keypair.pubkey(),
                lamports=amount_lamports
            )
        )

        versioned_tx = await build_optimized_transaction(client, [transfer_ix], keypair.pubkey())
        versioned_tx.sign([keypair])

        resp = await client.send_raw_transaction(versioned_tx.serialize())
        sig = resp.value
        logging.info(f"Transaction sent: {sig}")

        confirmed = await verify_transaction(client, sig)
        if confirmed:
            logging.info("✅ Transaction confirmed successfully")
            return True
        else:
            logging.error("❌ Transaction failed or not confirmed")
            return False

    except Exception as e:
        logging.error(f"Error during trade preparation: {str(e)}")
        return False
    finally:
        await client.close()

async def main():
    print("\n🚀 Test Trade Preparation")
    print("========================")
    
    success = await prepare_test_trade()
    
    if success:
        print("\n✅ Trade preparation successful!")
        print("Check test_trade.log for detailed information")
    else:
        print("\n❌ Trade preparation failed!")
        print("Check test_trade.log for error details")

if __name__ == "__main__":
    asyncio.run(main())
