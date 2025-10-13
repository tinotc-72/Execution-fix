import logging
import base58
import base64
import requests
import time

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.hash import Hash
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
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
PRIORITY_FEE = 1000  # micro-lamports per CU

def get_balance(pubkey: Pubkey) -> float:
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [str(pubkey)]
        }
        response = requests.post(kz.HELIUS_RPC_URL, json=payload)
        result = response.json()
        return result["result"]["value"] / 1e9
    except Exception as e:
        logging.error(f"Error getting balance: {e}")
        return 0.0

def get_latest_blockhash() -> Hash:
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getLatestBlockhash",
            "params": []
        }
        response = requests.post(kz.HELIUS_RPC_URL, json=payload)
        result = response.json()
        return Hash.from_string(result["result"]["value"]["blockhash"])
    except Exception as e:
        logging.error(f"Error getting blockhash: {e}")
        raise

def confirm_transaction(signature: str) -> bool:
    for _ in range(15):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignatureStatuses",
            "params": [[signature]]
        }
        response = requests.post(kz.HELIUS_RPC_URL, json=payload)
        result = response.json()
        status = result.get("result", {}).get("value", [None])[0]

        if status:
            if status["err"]:
                logging.error(f"Transaction failed: {status['err']}")
                return False
            if status["confirmationStatus"] == "finalized":
                logging.info("Transaction confirmed ✅")
                return True

        time.sleep(1)
        print(".", end="", flush=True)

    logging.error("Transaction confirmation timed out ❌")
    return False

def main():
    print("\n🚀 Executing Test Trade")
    print("======================")

    try:
        # Load wallet
        private_key = base58.b58decode(kz.BULLX_NEO_PRIVATE_KEY_QM.strip())
        keypair = Keypair.from_bytes(private_key)
        pubkey = keypair.pubkey()
        logging.info(f"Loaded wallet: {pubkey}")

        # Check balance
        balance = get_balance(pubkey)
        logging.info(f"Current balance: {balance:.4f} SOL")

        if balance < TEST_AMOUNT + 0.01:
            logging.error("Insufficient balance")
            return

        # Get blockhash
        blockhash = get_latest_blockhash()
        logging.info(f"Got blockhash: {blockhash}")

        # Build instructions
        priority_ix = set_compute_unit_price(PRIORITY_FEE)
        compute_ix = set_compute_unit_limit(COMPUTE_UNITS)
        transfer_ix = transfer(TransferParams(from_pubkey=pubkey, to_pubkey=pubkey, lamports=int(TEST_AMOUNT * 1e9)))

        instructions = [priority_ix, compute_ix, transfer_ix]

        # Create MessageV0 and VersionedTransaction
        message = MessageV0.try_compile(
            payer=pubkey,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=blockhash
        )

        tx = VersionedTransaction(message, [keypair])

        # Serialize transaction
        raw_bytes = bytes(tx)
        b64_tx = base64.b64encode(raw_bytes).decode("utf-8")

        # Send transaction
        logging.info("Sending transaction...")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [
                b64_tx,
                {"encoding": "base64", "preflightCommitment": "confirmed", "maxSupportedTransactionVersion": 0}
            ]
        }

        response = requests.post(kz.HELIUS_RPC_URL, json=payload)
        result = response.json()

        if "error" in result:
            logging.error(f"❌ Failed to send transaction: {result['error']}")
            return

        signature = result["result"]
        logging.info(f"Transaction sent: {signature}")

        # Wait for confirmation
        if confirm_transaction(signature):
            new_balance = get_balance(pubkey)
            logging.info(f"New balance: {new_balance:.4f} SOL")
            print("\n✅ Test transaction successful!")
        else:
            print("\n❌ Test transaction failed!")

    except Exception as e:
        logging.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
