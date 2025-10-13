"""
GENERIC EXECUTOR: Attempts to copy any trade, regardless of DEX/program support.
Logs all unknown program IDs and tries to replay the original instruction with the user's wallet.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GenericExecutor:
    def __init__(self, rpc_client, user_wallet):
        self.rpc_client = rpc_client
        self.user_wallet = user_wallet

    async def execute(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        from utils import get_transaction_with_logs, get_latest_blockhash, get_account_info, create_ata_if_missing
        from solders.pubkey import Pubkey
        from solders.instruction import Instruction
        from solders.transaction import Transaction
        from solders.message import Message
        from solders.hash import Hash
        import base58
        
        program_id = trade_info.get('program_id', 'UNKNOWN')
        signature = trade_info.get('signature')
        logger.warning(f"[GENERIC EXECUTOR] Attempting to copy trade for unknown program_id: {program_id}")
        logger.info(f"[GENERIC EXECUTOR] Trade info: {trade_info}")
        if not signature:
            return {'confirmed': False, 'signature': None, 'error': 'No signature in trade_info'}
        # Fetch the original transaction
        tx_data = await get_transaction_with_logs(signature)
        if not tx_data:
            return {'confirmed': False, 'signature': None, 'error': 'Could not fetch original transaction'}
        try:
            # Extract message and instructions
            msg = tx_data['transaction']['message']
            account_keys = msg['accountKeys']
            instructions = msg['instructions']
            # Substitute user wallet for original trader in writable/signing accounts
            orig_wallet = trade_info.get('original_wallet') or account_keys[0]
            user_wallet_pk = str(self.user_wallet.pubkey())
            # Prepare new instructions
            new_instructions = []
            for ix in instructions:
                prog_id_idx = ix['programIdIndex']
                prog_id = Pubkey.from_string(account_keys[prog_id_idx])
                # Substitute user wallet in accounts
                accounts = []
                for i in ix['accounts']:
                    acc = account_keys[i]
                    if acc == orig_wallet:
                        accounts.append(self.user_wallet.pubkey())
                    else:
                        accounts.append(Pubkey.from_string(acc))
                data = base58.b58decode(ix['data'])
                new_instructions.append(Instruction(prog_id, data, accounts))
            # Check/create ATAs for all token mints for user wallet (improved logic)
            try:
                for ix in instructions:
                    prog_id_idx = ix['programIdIndex']
                    prog_id = account_keys[prog_id_idx]
                    if prog_id == 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA':
                        # Try to find mint and destination
                        for i in ix['accounts']:
                            acc = account_keys[i]
                            # If this is a token mint, ensure ATA exists for user wallet
                            if len(acc) == 44 and acc != user_wallet_pk:
                                try:
                                    await create_ata_if_missing(self.user_wallet, acc)
                                except Exception as e:
                                    logger.error(f"[GENERIC EXECUTOR] Error creating ATA for {acc}: {e}")
            except Exception as e:
                logger.error(f"[GENERIC EXECUTOR] ATA creation logic error: {e}")
            # Get latest blockhash
            blockhash_resp = await get_latest_blockhash()
            if 'result' not in blockhash_resp:
                return {'confirmed': False, 'signature': None, 'error': 'Failed to get blockhash'}
            blockhash = Hash.from_string(blockhash_resp['result']['value']['blockhash'])
            # Build transaction
            msg = Message(self.user_wallet.pubkey(), new_instructions, blockhash)
            tx = Transaction([self.user_wallet], msg, blockhash)
            # Simulate transaction before sending
            sim_result = await self.rpc_client.simulate_transaction(tx)
            if not sim_result['value']['err']:
                send_result = await self.rpc_client.send_transaction(tx)
                logger.info(f"[GENERIC EXECUTOR] Transaction sent: {send_result}")
                # Confirm transaction
                try:
                    sig = send_result.get('result') or send_result.get('signature')
                    if not sig:
                        return {'confirmed': False, 'signature': None, 'error': 'No signature returned'}
                    # Wait for confirmation (simple polling)
                    for _ in range(10):
                        conf = await self.rpc_client.get_confirmed_transaction(sig)
                        if conf and conf.get('result'):
                            logger.info(f"[GENERIC EXECUTOR] Transaction {sig} confirmed on-chain.")
                            return {'confirmed': True, 'signature': sig, 'error': None}
                        import asyncio
                        await asyncio.sleep(1)
                    logger.warning(f"[GENERIC EXECUTOR] Transaction {sig} not confirmed after polling.")
                    return {'confirmed': False, 'signature': sig, 'error': 'Not confirmed after polling'}
                except Exception as e:
                    logger.error(f"[GENERIC EXECUTOR] Error during confirmation: {e}")
                    return {'confirmed': False, 'signature': None, 'error': str(e)}
            else:
                logger.error(f"[GENERIC EXECUTOR] Simulation failed: {sim_result['value']['err']}")
                logger.debug(f"[DEBUG] Simulation error: {sim_result['value']['err']}")
                logger.error(f"[GENERIC EXECUTOR] Transaction: {tx}")
                logger.error(f"[GENERIC EXECUTOR] Instruction details: {instructions}")
                return {'confirmed': False, 'signature': None, 'error': sim_result['value']['err']}
        except Exception as e:
            logger.error(f"[GENERIC EXECUTOR] Exception: {e}")
            import traceback
            logger.error(f"[DEBUG] Exception details: {traceback.format_exc()}")
            return {'confirmed': False, 'signature': None, 'error': str(e)}
