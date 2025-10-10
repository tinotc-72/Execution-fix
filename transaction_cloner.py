"""
transaction_cloner.py

A universal transaction cloner for Solana MEV/copy trading bots.
Extracts and replicates any transaction's program ID, accounts, and instruction data.
"""

from solders.rpc.responses import GetTransactionResp
from solders.pubkey import Pubkey
from solders.instruction import CompiledInstruction
from solders.transaction import VersionedTransaction
from solders.message import Message
from solders.keypair import Keypair
from solders.signature import Signature
from typing import List, Dict, Any, Optional
import base64
import logging
import aiohttp
import asyncio
import json

logger = logging.getLogger(__name__)

class TransactionCloner:
    async def initialize(self):
        """Stub for initialization logic (if needed)."""
        import logging
        logging.getLogger(__name__).info("TransactionCloner initialized (stub method)")
        return True

    async def cleanup(self):
        """Stub for cleanup logic (if needed)."""
        import logging
        logging.getLogger(__name__).info("TransactionCloner cleaned up (stub method)")
        return True
    def __init__(self, rpc_url: str, payer: Keypair):
        self.rpc_url = rpc_url
        self.payer = payer

    async def fetch_transaction(self, signature: str) -> Optional[Dict[str, Any]]:
        """Fetch a transaction using aiohttp instead of solders Client"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "jsonParsed",
                        "maxSupportedTransactionVersion": 0,
                        "commitment": "confirmed"
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=payload) as response:
                    data = await response.json()
                    if "result" in data and data["result"]:
                        return data["result"]
                    else:
                        logger.error(f"Failed to fetch transaction: {data}")
                        return None
        except Exception as e:
            logger.error(f"Failed to fetch transaction: {e}")
            return None

    def extract_instructions(self, tx_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all instructions from the transaction data"""
        try:
            transaction = tx_data.get("transaction", {})
            message = transaction.get("message", {})
            instructions = message.get("instructions", [])
            account_keys = message.get("accountKeys", [])
            
            extracted_instructions = []
            for ix in instructions:
                program_id_index = ix.get("programIdIndex")
                if program_id_index is not None and program_id_index < len(account_keys):
                    program_id = account_keys[program_id_index]
                    accounts = [account_keys[i] for i in ix.get("accounts", []) if i < len(account_keys)]
                    data = ix.get("data", "")
                    
                    extracted_instructions.append({
                        "program_id": program_id,
                        "accounts": accounts,
                        "data": data
                    })
            return extracted_instructions
        except Exception as e:
            logger.error(f"Failed to extract instructions: {e}")
            return []

    async def get_recent_blockhash(self) -> Optional[str]:
        """Fetch the most recent blockhash from the network"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getLatestBlockhash",
                "params": [{"commitment": "confirmed"}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_url, json=payload) as response:
                    data = await response.json()
                    if "result" in data and "value" in data["result"]:
                        return data["result"]["value"]["blockhash"]
                    else:
                        logger.error(f"Failed to get blockhash: {data}")
                        return None
        except Exception as e:
            logger.error(f"Failed to fetch recent blockhash: {e}")
            return None

    async def clone_transaction(self, signature: str, override_accounts: Dict[int, Pubkey] = None) -> Optional[VersionedTransaction]:
        """
        Given a transaction signature, fetch and reconstruct the transaction for replay.
        Explicitly reconstructs AccountMeta for each account in every instruction.
        Optionally override certain accounts (e.g., payer, user wallet).
        """
        from solders.instruction import AccountMeta
        tx_data = await self.fetch_transaction(signature)
        if not tx_data:
            logger.error("Transaction not found or invalid response.")
            return None
        try:
            transaction = tx_data.get("transaction", {})
            message = transaction.get("message", {})
            account_keys_raw = message.get("accountKeys", [])
            
            # Convert string account keys to Pubkey objects
            account_keys = []
            for key in account_keys_raw:
                if isinstance(key, str):
                    account_keys.append(Pubkey.from_string(key))
                elif isinstance(key, dict) and "pubkey" in key:
                    account_keys.append(Pubkey.from_string(key["pubkey"]))
                else:
                    account_keys.append(key)
            
            # Always replace the first account (payer) with our own keypair
            if account_keys:
                account_keys[0] = self.payer.pubkey()
            
            # Optionally override additional accounts
            if override_accounts:
                for idx, new_key in override_accounts.items():
                    if idx < len(account_keys):
                        account_keys[idx] = new_key

            # Build a lookup for is_signer and is_writable for each account
            header = message.get("header", {})
            num_signers = header.get("numRequiredSignatures", 0)
            num_readonly_signed = header.get("numReadonlySignedAccounts", 0)
            num_readonly_unsigned = header.get("numReadonlyUnsignedAccounts", 0)
            total_keys = len(account_keys)
            
            signer_indices = set(range(num_signers))
            writable_signer_indices = set(range(num_signers - num_readonly_signed))
            writable_unsigned_indices = set(range(num_signers, total_keys - num_readonly_unsigned))

            def get_account_meta(idx):
                pubkey = account_keys[idx]
                is_signer = idx in signer_indices
                is_writable = (
                    (is_signer and idx in writable_signer_indices) or
                    (not is_signer and idx in writable_unsigned_indices)
                )
                return AccountMeta(pubkey, is_signer, is_writable)

            # Rebuild instructions with proper Instruction objects
            new_instructions = []
            for ix in message.get("instructions", []):
                program_id_index = ix.get("programIdIndex")
                if program_id_index is None or program_id_index >= len(account_keys):
                    continue
                    
                account_indices = ix.get("accounts", [])
                account_metas = [get_account_meta(i) for i in account_indices if i < len(account_keys)]
                data_str = ix.get("data", "")
                
                # Decode base64 data
                try:
                    data = base64.b64decode(data_str) if data_str else b""
                except Exception as decode_error:
                    logger.warning(f"Failed to decode instruction data: {decode_error}")
                    data = b""
                
                # Create Instruction object instead of CompiledInstruction
                from solders.instruction import Instruction
                program_id = account_keys[program_id_index]
                new_ix = Instruction(
                    program_id=program_id,
                    accounts=account_metas,
                    data=data
                )
                new_instructions.append(new_ix)

            # Get fresh recent blockhash from network
            blockhash_str = await self.get_recent_blockhash()
            if not blockhash_str:
                logger.error("Failed to get recent blockhash")
                return None
                
            from solders.hash import Hash
            try:
                recent_blockhash = Hash.from_string(blockhash_str)
            except Exception as hash_error:
                logger.error(f"Failed to parse blockhash '{blockhash_str}': {hash_error}")
                return None

            # Rebuild message using the correct Message constructor
            try:
                # Message.new_with_blockhash expects: instructions, payer, recent_blockhash
                new_message = Message.new_with_blockhash(
                    new_instructions,
                    self.payer.pubkey(),
                    recent_blockhash
                )
            except Exception as msg_error:
                logger.error(f"Failed to create message: {msg_error}")
                return None
            
            # Build transaction with proper signature
            try:
                # Use the correct VersionedTransaction API
                # Create VersionedTransaction directly with message and keypairs
                # Extract raw keypair from WalletWithSign wrapper
                signed_tx = VersionedTransaction(
                    message=new_message,
                    keypairs=[self.payer.keypair]
                )
                return signed_tx
            except Exception as tx_error:
                logger.error(f"Failed to create or sign transaction: {tx_error}")
                return None
        except Exception as e:
            logger.error(f"Failed to clone transaction: {e}")
            return None

    async def send_cloned_transaction(self, tx: VersionedTransaction, priority_fee: Optional[int] = None, max_retries: int = 3) -> Optional[str]:
        """
        Send the cloned transaction to the network with priority fee and retry logic.
        If transaction fails due to blockhash, retry with a fresh blockhash.
        """
        attempt = 0
        # Set the default priority fee to 3000000 lamports if not provided
        if priority_fee is None:
            priority_fee = 3000000  # 0.003 SOL, as requested
        from solders.transaction import VersionedTransaction
        from solders.message import Message
        from solders.hash import Hash
        while attempt < max_retries:
            try:
                # Always get a fresh blockhash for each attempt
                blockhash_str = await self.get_recent_blockhash()
                if not blockhash_str:
                    logger.error("Failed to get fresh blockhash for send attempt.")
                    return None
                try:
                    recent_blockhash = Hash.from_string(blockhash_str)
                except Exception as hash_error:
                    logger.error(f"Failed to parse blockhash '{blockhash_str}': {hash_error}")
                    return None
                # Rebuild message and transaction with new blockhash
                try:
                    new_message = Message.new_with_blockhash(
                        tx.message.instructions,
                        self.payer.pubkey(),
                        recent_blockhash
                    )
                    new_tx = VersionedTransaction(
                        message=new_message,
                        keypairs=[self.payer.keypair]
                    )
                    tx_bytes = bytes(new_tx)
                    tx_b64 = base64.b64encode(tx_bytes).decode()
                except Exception as rebuild_error:
                    logger.error(f"Failed to rebuild transaction for send: {rebuild_error}")
                    return None
                params = {"encoding": "base64"}
                params["preflightCommitment"] = "confirmed"
                params["maxRetries"] = max_retries
                params["minContextSlot"] = None
                params["skipPreflight"] = False
                params["feePayer"] = str(self.payer.pubkey())
                params["prioritizationFee"] = priority_fee
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "sendTransaction",
                    "params": [tx_b64, params]
                }
                logger.debug(f"Attempt {attempt+1}: Sending transaction with blockhash: {blockhash_str}")
                logger.debug(f"Transaction base64: {tx_b64}")
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.rpc_url, json=payload) as response:
                        data = await response.json()
                        if "result" in data:
                            logger.info(f"Transaction sent successfully. Signature: {data['result']}")
                            return data["result"]
                        elif "error" in data and "Blockhash not found" in str(data["error"]):
                            logger.warning(f"Blockhash not found, retrying with fresh blockhash... Last blockhash: {blockhash_str}")
                            logger.error(f"Full error response: {data}")
                            attempt += 1
                            continue
                        else:
                            logger.error(f"Failed to send transaction: {data}")
                            logger.error(f"Full error response: {data}")
                            logger.debug(f"Transaction base64: {tx_b64}")
                            logger.debug(f"Blockhash used: {blockhash_str}")
                            return None
            except Exception as e:
                logger.error(f"Exception sending transaction: {e}")
                attempt += 1
        return None
    async def clone_transaction_fast(self, signature: str, override_accounts: Dict[int, Pubkey] = None) -> Optional[VersionedTransaction]:
        """
        Fast clone method for universal cloner compatibility. Delegates to clone_transaction.
        """
        return await self.clone_transaction(signature, override_accounts)

    async def process_copy_trades_parallel(self, signatures: List[str], override_accounts: Dict[int, Pubkey] = None, priority_fee: Optional[int] = None):
        """
        Process multiple copy trades in parallel using asyncio tasks.
        Each transaction is constructed, signed, and sent independently.
        """
        async def process_one(signature):
            tx = await self.clone_transaction(signature, override_accounts)
            if tx:
                tx_sig = await self.send_cloned_transaction(tx, priority_fee=priority_fee)
                if tx_sig:
                    logger.info(f"✅ Copy trade sent for {signature}: {tx_sig}")
                else:
                    logger.error(f"❌ Failed to send copy trade for {signature}")
            else:
                logger.error(f"❌ Failed to clone transaction for {signature}")
        tasks = [process_one(sig) for sig in signatures]
        await asyncio.gather(*tasks)

# Example usage (to be integrated with the main copy bot):
# cloner = TransactionCloner(rpc_url, payer_keypair)
# tx = cloner.clone_transaction(target_signature, override_accounts={0: my_pubkey})
# if tx:
#     tx_sig = cloner.send_cloned_transaction(tx)
#     print(f"Cloned transaction sent: {tx_sig}")
