import asyncio
import logging
import base64
import traceback
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from solders.instruction import Instruction
from config import kz
import base58
import aiohttp
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_rpc_transfer():
    try:
        # Load wallet
        key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        decoded_key = base58.b58decode(key)
        keypair = Keypair.from_bytes(decoded_key[:64])
        logger.info(f"Loaded wallet: {keypair.pubkey()}")
        
        logger.info(f"\n📡 Connecting to RPC: {kz.HELIUS_RPC_URL}")
        
        # Set up RPC session
        try:
            async with aiohttp.ClientSession() as session:
                # Test connection
                logger.info("Testing RPC connection...")
                async with session.post(
                    kz.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getHealth",
                        "params": []
                    }
                ) as response:
                    result = await response.json()
                    if "result" not in result or result["result"] != "ok":
                        raise Exception(f"RPC health check failed: {result}")
                    logger.info("✅ RPC connection successful")
                
                # Get recent blockhash
                logger.info("\n🔄 Getting recent blockhash...")
                async with session.post(
                    kz.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getLatestBlockhash",
                        "params": []
                    }
                ) as response:
                    result = await response.json()
                    if "error" in result:
                        raise Exception(f"Failed to get blockhash: {result['error']}")
                    blockhash = result["result"]["value"]["blockhash"]
                    logger.info(f"Got blockhash: {blockhash}")
                
                # Get initial balance
                logger.info("\n💰 Getting initial balance...")
                async with session.post(
                    kz.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [str(keypair.pubkey())]
                    }
                ) as response:
                    result = await response.json()
                    if "error" in result:
                        raise Exception(f"Failed to get balance: {result['error']}")
                    balance = result["result"]["value"]
                    logger.info(f"Initial balance: {balance/1e9:.4f} SOL")
                
                # Create test transaction
                amount = 1_000_000  # 0.001 SOL
                
                # Set up compute budget
                logger.info("\n🔧 Creating transaction...")
                compute_budget_id = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
                set_compute_unit_limit = Instruction(
                    program_id=compute_budget_id,
                    accounts=[],
                    data=bytes([0] + list((200_000).to_bytes(4, 'little')))  # 200k CU
                )
                set_compute_unit_price = Instruction(
                    program_id=compute_budget_id,
                    accounts=[],
                    data=bytes([1] + list((1_000).to_bytes(4, 'little')))    # 1000 micro-lamports/CU
                )
                
                # Create transfer to self (for testing)
                transfer_ix = transfer(
                    TransferParams(
                        from_pubkey=keypair.pubkey(),
                        to_pubkey=keypair.pubkey(),  # Transfer to self
                        lamports=amount
                    )
                )
                
                logger.info("Instructions:")
                logger.info(f"1. Set compute unit limit: {200_000} units")
                logger.info(f"2. Set compute unit price: {1_000} micro-lamports")
                logger.info(f"3. Transfer {amount/1e9:.9f} SOL to self")
                
                # Create transaction
                message = MessageV0.try_compile(
                    payer=keypair.pubkey(),
                    instructions=[set_compute_unit_limit, set_compute_unit_price, transfer_ix],
                    address_lookup_table_accounts=[],
                    recent_blockhash=Hash.from_string(blockhash)
                )
                if not message:
                    raise Exception("Failed to compile message")
                    
                logger.info("\n✅ Message compiled successfully")
                logger.info(f"Header: {message.header}")
                
                tx = VersionedTransaction(message, [keypair])
                
                # Convert to wire format
                wire_tx = bytes(tx)
                encoded_tx = base64.b64encode(wire_tx).decode('utf-8')
                
                logger.info("\n🔍 Transaction Details:")
                logger.info(f"Instructions: {len(tx.message.instructions)}")
                logger.info(f"Account keys: {len(tx.message.account_keys)}")
                logger.info("Accounts:")
                for i, key in enumerate(tx.message.account_keys):
                    is_signer = i < tx.message.header.num_required_signatures
                    logger.info(f"  {i}: {key} (signer: {is_signer})")
                logger.info(f"Wire format size: {len(wire_tx)} bytes")
                
                # Submit transaction
                logger.info("\n📡 Submitting transaction via RPC...")
                async with session.post(
                    kz.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            encoded_tx,
                            {"skipPreflight": True, "maxRetries": 0}
                        ]
                    }
                ) as response:
                    result = await response.json()
                    logger.info(f"Response: {json.dumps(result, indent=2)}")
                    
                    if "error" in result:
                        logger.error(f"❌ Transaction failed: {result['error']}")
                    else:
                        sig = result["result"]
                        logger.info(f"✅ Transaction submitted! Signature: {sig}")
                        
                        # Wait for confirmation
                        logger.info("\n⏳ Waiting for confirmation...")
                        for _ in range(10):
                            async with session.post(
                                kz.HELIUS_RPC_URL,
                                json={
                                    "jsonrpc": "2.0",
                                    "id": 1,
                                    "method": "getTransaction",
                                    "params": [
                                        sig,
                                        {"maxSupportedTransactionVersion": 0}
                                    ]
                                }
                            ) as response:
                                confirm_result = await response.json()
                                if "result" in confirm_result and confirm_result["result"]:
                                    logger.info(f"✅ Transaction confirmed!")
                                    logger.info(f"Details: {json.dumps(confirm_result['result'], indent=2)}")
                                    break
                                await asyncio.sleep(1)
                        
                        # Get final balance
                        async with session.post(
                            kz.HELIUS_RPC_URL,
                            json={
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "getBalance",
                                "params": [str(keypair.pubkey())]
                            }
                        ) as response:
                            result = await response.json()
                            if "error" in result:
                                raise Exception(f"Failed to get final balance: {result['error']}")
                            final_balance = result["result"]["value"]
                            logger.info(f"\nFinal balance: {final_balance/1e9:.4f} SOL")
                            logger.info(f"Change: {(final_balance - balance)/1e9:.9f} SOL")
                    
        except aiohttp.ClientError as e:
            logger.error(f"RPC connection error: {str(e)}")
            raise
                    
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        traceback.print_exc()

async def main():
    try:
        await test_rpc_transfer()
    except Exception as e:
        logger.error(f"Main error: {str(e)}")
        traceback.print_exc()
    finally:
        # Force close any remaining connections
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
