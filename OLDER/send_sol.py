import asyncio
import base64
import logging
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams
from config import WALLET  # Import the mnemonic-based wallet
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from rpc_health import RPCHealthChecker
from config import kz  # Optional fallback

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TO_ADDRESS = "4UskbEc8Gqj9t3GRtc3zcwtCDBHsAEX89dod9R5vSEwN"
LAMPORTS_TO_SEND = 480_000_000  # 0.48 SOL

async def main():
    # Use mnemonic-based wallet from config
    keypair = WALLET  # This is already properly derived from the mnemonic
    payer = keypair.pubkey()
    recipient = Pubkey.from_string(TO_ADDRESS)

    # Instructions
    compute_ixs = [
        set_compute_unit_limit(200_000),
        set_compute_unit_price(1_000)
    ]
    transfer_ix = transfer(TransferParams(from_pubkey=payer, to_pubkey=recipient, lamports=LAMPORTS_TO_SEND))
    instructions = compute_ixs + [transfer_ix]

    # RPC setup
    http = RPCHealthChecker()
    await http.initialize()

    try:
        healthy_endpoints = await http.check_all_endpoints()
        if not healthy_endpoints:
            logger.error("❌ No healthy RPC endpoints available")
            return

        endpoint = healthy_endpoints[0]
        logger.info("✅ Using healthy RPC: %s", endpoint.name)

        # Get latest blockhash
        async with http.session.post(
            endpoint.url,
            json={"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}
        ) as resp:
            res = await resp.json()
            if "error" in res:
                logger.error("❌ Failed to get blockhash: %s", res["error"])
                return
            blockhash = Hash.from_string(res["result"]["value"]["blockhash"])

        # Build and send transaction
        message = MessageV0.try_compile(
            payer=payer,
            instructions=instructions,
            recent_blockhash=blockhash,
            address_lookup_table_accounts=[]
        )
        tx = VersionedTransaction(message, [keypair])

        async with http.session.post(
            endpoint.url,
            json={
                "jsonrpc": "2.0", "id": 1, "method": "sendTransaction",
                "params": [base64.b64encode(bytes(tx)).decode(), {"encoding": "base64"}]
            }
        ) as resp:
            res = await resp.json()
            if "error" in res:
                logger.error("❌ Send failed: %s", res["error"])
                return

            sig = res["result"]
            logger.info("✅ Sent! Signature: %s", sig)

            # Confirm transaction
            for _ in range(30):
                await asyncio.sleep(1)
                async with http.session.post(
                    endpoint.url,
                    json={
                        "jsonrpc": "2.0", "id": 1, "method": "getSignatureStatuses", "params": [[sig]]
                    }
                ) as resp2:
                    status = await resp2.json()
                    if "error" in status:
                        logger.warning("Status check error: %s", status["error"])
                        continue
                    info = status["result"]["value"][0]
                    if info:
                        logger.info("🟢 Confirmed: %s", info)
                        return

        logger.warning("⚠️ Timeout waiting for confirmation")

    except Exception as e:
        logger.error("❌ Transaction failed: %s", str(e))
    finally:
        await http.close()

if __name__ == "__main__":
    asyncio.run(main())
