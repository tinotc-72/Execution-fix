import asyncio
import aiohttp
import base64
import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from config import kz
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def simple_test():
    try:
        # Load wallet
        key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        decoded_key = base58.b58decode(key)
        keypair = Keypair.from_bytes(decoded_key[:64])
        logger.info(f"Loaded wallet: {keypair.pubkey()}")
        
        # Set up session
        async with aiohttp.ClientSession() as session:
            logger.info("Testing RPC connection...")
            
            rpc_url = kz.HELIUS_RPC_URL  # Use Helius RPC for better reliability
            logger.info(f"Using RPC URL: {rpc_url}")
            
            # Get initial balance
            logger.info("\nChecking initial balance...")
            async with session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [str(keypair.pubkey())]
                }
            ) as response:
                result = await response.json()
                if "result" in result:
                    initial_balance = result["result"]["value"]
                    logger.info(f"Initial balance: {initial_balance/1e9:.4f} SOL")
                else:
                    logger.error(f"Error getting balance: {result}")
                    return

            # Send a minimal test transaction (0.000001 SOL to self)
            logger.info("\n🔄 Testing minimal transaction...")
            recent_blockhash_resp = await session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "finalized"}]
                }
            )
            blockhash_result = await recent_blockhash_resp.json()
            if "result" not in blockhash_result:
                logger.error(f"Failed to get blockhash: {blockhash_result}")
                return
                
            recent_blockhash = blockhash_result["result"]["value"]["blockhash"]
            logger.info(f"Got blockhash: {recent_blockhash}")

            # Create self-transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=keypair.pubkey(),
                    to_pubkey=keypair.pubkey(),  # Send to self
                    lamports=1_000  # 0.000001 SOL
                )
            )

            # Create transaction
            message = MessageV0.try_compile(
                payer=keypair.pubkey(),
                instructions=[transfer_ix],
                address_lookup_table_accounts=[],
                recent_blockhash=Hash.from_string(recent_blockhash)
            )

            tx = VersionedTransaction(message, [keypair])
            logger.info("Transaction created and signed")

            # Convert to wire format and encode properly
            wire_tx = base64.b64encode(bytes(tx)).decode('utf-8')
            logger.info("Transaction encoded for submission")

            # Submit transaction with proper options
            logger.info("\n📡 Submitting transaction...")
            submit_response = await session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "sendTransaction",
                    "params": [
                        wire_tx,
                        {
                            "encoding": "base64",
                            "skipPreflight": False,
                            "preflightCommitment": "confirmed",
                            "maxRetries": 3
                        }
                    ]
                }
            )
            submit_result = await submit_response.json()
            
            if "error" in submit_result:
                logger.error(f"❌ Transaction failed: {submit_result['error']}")
                return
                
            signature = submit_result["result"]
            logger.info(f"✅ Transaction submitted! Signature: {signature}")

            # Wait for confirmation
            logger.info("\n⏳ Waiting for confirmation...")
            confirmed = False
            for _ in range(30):  # Wait up to 30 seconds
                confirm_response = await session.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            signature,
                            {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
                        ]
                    }
                )
                confirm_result = await confirm_response.json()
                
                if confirm_result.get("result"):
                    meta = confirm_result["result"].get("meta", {})
                    if meta.get("err"):
                        logger.error(f"❌ Transaction failed on-chain: {meta['err']}")
                        return
                    else:
                        logger.info("✅ Transaction executed successfully!")
                        confirmed = True
                    
                    # Show detailed execution info
                    logger.info("\n🔍 Transaction details:")
                    logger.info(f"Slot: {confirm_result['result'].get('slot')}")
                    logger.info(f"Confirmations: {meta.get('confirmations')}")
                    logger.info(f"Fee: {meta.get('fee')} lamports")
                    
                    # Show balance changes
                    pre_token_balances = meta.get("preTokenBalances", [])
                    post_token_balances = meta.get("postTokenBalances", [])
                    
                    if pre_token_balances != post_token_balances:
                        logger.info("\nToken balance changes detected:")
                        logger.info(f"Pre: {pre_token_balances}")
                        logger.info(f"Post: {post_token_balances}")
                    break
                    
                logger.info("Still waiting for confirmation...")
                await asyncio.sleep(1)

            if not confirmed:
                logger.error("❌ Transaction was not confirmed after 30 seconds")

            # Get final balance
            logger.info("\nChecking final balance...")
            async with session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [str(keypair.pubkey())]
                }
            ) as response:
                result = await response.json()
                if "result" in result:
                    final_balance = result["result"]["value"]
                    logger.info(f"Final balance: {final_balance/1e9:.4f} SOL")
                    change = (final_balance - initial_balance)
                    logger.info(f"Balance change: {change/1e9:.9f} SOL")
                    
                    if change < 0:
                        logger.info("✅ Transaction fee was deducted - confirmed on-chain execution!")
                    else:
                        logger.warning("⚠️ No balance change detected - transaction may not have executed")
                else:
                    logger.error(f"Error getting final balance: {result}")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    try:
        await simple_test()
    except Exception as e:
        logger.error(f"Main error: {str(e)}")
    finally:
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
