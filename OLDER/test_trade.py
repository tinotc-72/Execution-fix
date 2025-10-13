import asyncio
import time
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from solders.instruction import Instruction
from config import kz
import base58
from fast_executor import FastExecutor
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_transaction(executor: FastExecutor, signature: str, max_retries: int = 10) -> bool:
    """Verify that a transaction was confirmed on-chain"""
    for _ in range(max_retries):
        try:
            resp = await executor.get_transaction(signature)
            if resp and resp.value:
                if resp.value.slot > 0:  # Transaction found and processed
                    return True
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error checking transaction: {e}")
        
    return False

async def test_trade():
    try:
        # Use mnemonic-based wallet from config
        from config import WALLET
        keypair = WALLET  # Already properly derived from mnemonic
        logger.info(f"Loaded wallet: {keypair.pubkey()}")
        
        # Initialize executor
        executor = FastExecutor(keypair)
        
        # Get initial balance
        balance = await executor.get_balance(keypair.pubkey())
        logger.info(f"Initial balance: {balance / 1e9:.4f} SOL")
        
        # Get recent blockhash
        blockhash_resp = await executor.get_latest_blockhash()
        if not blockhash_resp:
            raise Exception("Failed to get blockhash")
        logger.info(f"Got recent blockhash: {blockhash_resp}")
        
        # Create a test destination (just using a fixed public key for testing)
        test_destination = Pubkey.from_string("DG7XVutWPdEuC8UJqhy9UyGnQWUVDhzpqn4UoPTiv3Ce")
        
        # Test amounts in lamports
        test_amounts = [1_000_000, 10_000_000, 100_000_000]  # 0.001, 0.01, 0.1 SOL
        
        for amount in test_amounts:
            logger.info(f"\n📊 Testing {amount/1e9:.3f} SOL transfer...")
            
            # Get balance before trade
            balance_before = await executor.get_balance(keypair.pubkey())
            logger.info(f"Balance before {amount/1e9:.3f} SOL transfer: {balance_before/1e9:.4f} SOL")
            
            # Create compute budget instructions
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
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=keypair.pubkey(),
                    to_pubkey=test_destination,
                    lamports=amount
                )
            )
            
            # Create versioned transaction with compute budget
            message = MessageV0.try_compile(
                payer=keypair.pubkey(),
                instructions=[set_compute_unit_limit, set_compute_unit_price, transfer_ix],
                address_lookup_table_accounts=[],
                recent_blockhash=Hash.from_string(str(blockhash_resp))
            )
            if not message:
                raise Exception("Failed to compile message")
                
            tx = VersionedTransaction(message, [keypair])
            
            # Execute trade
            logger.info(f"Executing {amount/1e9:.3f} SOL transfer...")
            
            sig = await executor.execute_trade(tx)
            if not sig:
                logger.error("Failed to get transaction signature")
                continue
                
            # Verify the transaction was confirmed
            logger.info(f"Verifying transaction {sig[:8]}...")
            confirmed = await verify_transaction(executor, sig)
            
            if confirmed:
                logger.info(f"✅ Transaction confirmed on-chain: {sig}")
                
                # Get new balance and calculate actual fee
                balance_after = await executor.get_balance(keypair.pubkey())
                actual_fee = balance_before - balance_after - amount
                
                logger.info(f"Balance after: {balance_after/1e9:.4f} SOL")
                logger.info(f"Transaction fee: {actual_fee} lamports")
            else:
                logger.error(f"❌ Transaction not confirmed: {sig}")
                
        logger.info("\n📝 Test complete")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_trade())
