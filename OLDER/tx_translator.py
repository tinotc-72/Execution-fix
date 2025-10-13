# tx_translator.py

import base64
from typing import Optional

from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.hash import Hash
from solana.rpc.async_api import AsyncClient

from config import RPC_URL, MONITORED_WALLETS, MONITORED_WALLET_PUBKEYS
from tx_builder import get_jito_fee_instructions
from spl.token.instructions import get_associated_token_address, create_associated_token_account

client = AsyncClient(RPC_URL)
# === PDA Rewrite Patterns ===
KNOWN_PDA_SEEDS = {
    b"associated-user",
    b"user",
    b"referral",
    b"stake",
    b"vault",
}


def rewrite_pda_if_monitored(
    pda: Pubkey,
    program_id: Pubkey,
    old_pubkey: Pubkey,
    new_pubkey: Pubkey
) -> Pubkey:
    """
    Rewrites a PDA if it's based on Wallet A’s pubkey using known seed patterns.
    """
    for seed in KNOWN_PDA_SEEDS:
        try:
            old_target, _ = Pubkey.find_program_address([seed, bytes(old_pubkey)], program_id)
            if pda == old_target:
                new_target, _ = Pubkey.find_program_address([seed, bytes(new_pubkey)], program_id)
                print(f"🔁 PDA swapped: {old_target} → {new_target}")
                return new_target
        except Exception:
            continue

    return pda  # unchanged


async def clone_monitored_transaction(raw_tx: dict, your_wallet: Keypair, source_wallet: Pubkey) -> Optional[VersionedTransaction]:
    try:
        # === 1. Decode Base64 TX ===
        message_b64 = raw_tx.get("transaction", {}).get("message")
        if not message_b64 or isinstance(message_b64, dict):
            raise ValueError("Missing or malformed base64 message")

        tx_bytes = base64.b64decode(message_b64)
        original_tx = VersionedTransaction.from_bytes(tx_bytes)
        original_msg: MessageV0 = original_tx.message
        keys = original_msg.account_keys
        payer = your_wallet.pubkey()

        cloned_ixs = []
        token_account_creates = []

        for ix in original_msg.instructions:
            program_id = keys[ix.program_id_index]
            new_accounts = []

            for i in ix.accounts:
                old_key = keys[i]

                # Replace source wallet with your wallet
                new_key = payer if old_key == source_wallet else old_key

                # Rewrite known PDAs if they depend on source wallet
                if old_key not in [payer, new_key] and old_key != program_id:
                    new_key = rewrite_pda_if_monitored(old_key, program_id, source_wallet, payer)

                new_accounts.append(AccountMeta(
                    pubkey=new_key,
                    is_signer=(i < original_msg.header.num_required_signatures),
                    is_writable=(i in original_msg.writable_indexes)
                ))

                # Auto-create ATA if needed (basic case)
                if "Tokenkeg" in str(program_id) and old_key == source_wallet:
                    mint = next((k for k in keys if k != old_key), None)
                    if mint:
                        ata = get_associated_token_address(payer, mint)
                        info = await client.get_account_info(str(ata))
                        if info["result"]["value"] is None:
                            token_account_creates.append(
                                create_associated_token_account(payer, payer, mint)
                            )

            cloned_ixs.append(Instruction(program_id, new_accounts, ix.data))

        # === 3. Build Final TX ===
        blockhash = client.get_latest_blockhash()["result"]["value"]["blockhash"]
        blockhash_obj = Hash.from_string(blockhash)

        final_ixs = (
            get_jito_fee_instructions(payer) +
            token_account_creates +
            cloned_ixs
        )

        msg = MessageV0.try_compile(
            payer=payer,
            instructions=final_ixs,
            recent_blockhash=blockhash_obj,
            address_lookup_table_accounts=[]
        )

        return VersionedTransaction(msg, [your_wallet])

    except Exception as e:
        print("❌ Clone TX failed:", e)
        return None