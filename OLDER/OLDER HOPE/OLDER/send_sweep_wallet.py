# send_sol_clean.py

import base58
import asyncio
import base64
import logging
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from privatekeyz import private_key
from rpc_health import RPCHealthChecker

# === CONFIG ===
TO_ADDRESS = "4UskbEc8Gqj9t3GRtc3zcwtCDBHsAEX89dod9R5vSEwN"
LAMPORTS_BUFFER = 5000  # Leave ~5000 lamports for rent exemption (safety)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Load keypair from base58 string
    raw = base58.b58decode(private_key)
    keypair = Keypair.from_bytes(raw)
    wallet = keypair.pubkey()
    recipient = Pubkey.from_string(TO_ADDRESS)

    logger.info(f"👛 Sweeping SOL from wallet: {wallet}")

    # Initialize RPC
    http = RPCHealthChecker()
    await http.initialize()
    endpoints = await http.check_all_endpoints()
    if not endpoints:
        logger.error("❌ No healthy RPC endpoints found")
        return
    endpoint = endpoints[0]
    logger.info("✅ Using RPC: %s", endpoint.name)

    # Get balance
    async with http.session.post(
        endpoint.url,
        json={"jsonrpc": "2.0", "id": 1, "method": "getBalance", "params": [str(wallet)]}
    ) as resp:
        result = await resp.json()
        lamports = result["result"]["value"]
        if lamports <= LAMPORTS_BUFFER:
            logger.warning(f"⚠️ Not enough SOL to transfer: {lamports} lamports")
            return
        to_send = lamports - LAMPORTS_BUFFER
        logger.info(f"💸 Transferring {to_send} lamports")

    # Get blockhash
    async with http.session.post(
        endpoint.url,
        json={"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}
    ) as resp:
        res = await resp.json()
        blockhash = Hash.from_string(res["result"]["value"]["blockhash"])

    # Create message
    transfer_ix = transfer(TransferParams(from_pubkey=wallet, to_pubkey=recipient, lamports=to_send))
    message = MessageV0.try_compile(
        payer=wallet,
        instructions=[transfer_ix],
        recent_blockhash=blockhash,
        address_lookup_table_accounts=[]
    )
    tx = VersionedTransaction(message, [keypair])
    tx_bytes = base64.b64encode(bytes(tx)).decode()

    # Send transaction
    async with http.session.post(
        endpoint.url,
        json={"jsonrpc": "2.0", "id": 1, "method": "sendTransaction",
              "params": [tx_bytes, {"encoding": "base64"}]}
    ) as resp:
        tx_result = await resp.json()
        if "error" in tx_result:
            logger.error(f"❌ TX Error: {tx_result['error']}")
            await http.close()
            return
        sig = tx_result["result"]
        logger.info(f"✅ Sent! Signature: {sig}")
        print(f"https://solscan.io/tx/{sig}")

    await http.close()

if __name__ == "__main__":
    asyncio.run(main())
