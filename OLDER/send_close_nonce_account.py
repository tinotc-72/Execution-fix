import asyncio
import base58
import base64
import logging
import aiohttp

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash

import privatekeyz as kk

# === CONFIG ===
DESTINATION = Pubkey.from_string("4UskbEc8Gqj9t3GRtc3zcwtCDBHsAEX89dod9R5vSEwN")
NONCE_ACCOUNT = Pubkey.from_string("9heeb6JBHFB48jz7pV7umHpG3aKD6KibV4fVq2vJHPsq")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
RPC_URL = "https://api.mainnet-beta.solana.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_withdraw_instruction(nonce_acc, dest, authority, lamports: int = 0) -> Instruction:
    # Instruction layout: https://docs.solana.com/developing/runtime-facilities/sysvars#recent-blockhashes
    # Index 4 = withdraw_nonce_account (source: solana/system_program/src/system_instruction.rs)
    # Layout: u32 (4) for withdraw, then u64 (lamports) in little-endian
    ix_data = (4).to_bytes(4, "little") + lamports.to_bytes(8, "little")
    accounts = [
        AccountMeta(pubkey=nonce_acc, is_signer=False, is_writable=True),
        AccountMeta(pubkey=dest, is_signer=False, is_writable=True),
        AccountMeta(pubkey=authority, is_signer=True, is_writable=False),
    ]
    return Instruction(program_id=SYSTEM_PROGRAM_ID, accounts=accounts, data=ix_data)

async def get_recent_blockhash(session):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getLatestBlockhash",
        "params": []
    }
    async with session.post(RPC_URL, json=payload) as resp:
        res = await resp.json()
        return Hash.from_string(res["result"]["value"]["blockhash"])

async def get_nonce_authority(session):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [str(NONCE_ACCOUNT), {"encoding": "jsonParsed"}]
    }
    async with session.post(RPC_URL, json=payload) as resp:
        res = await resp.json()
        info = res["result"]["value"]["data"]["parsed"]["info"]
        return Pubkey.from_string(info["authority"])

async def main():
    raw_bytes = base58.b58decode(kk.private_key)
    if len(raw_bytes) != 64:
        raise ValueError("❌ Invalid private key length")
    authority_keypair = Keypair.from_bytes(raw_bytes)

    logger.info("👛 Closing nonce account: %s", NONCE_ACCOUNT)

    async with aiohttp.ClientSession() as session:
        authority_on_chain = await get_nonce_authority(session)
        if authority_on_chain != authority_keypair.pubkey():
            raise ValueError("❌ This wallet is not the authority of the nonce account")

        withdraw_ix = build_withdraw_instruction(NONCE_ACCOUNT, DESTINATION, authority_keypair.pubkey(), 0)
        blockhash = await get_recent_blockhash(session)

        msg = MessageV0.try_compile(
            payer=authority_keypair.pubkey(),
            instructions=[withdraw_ix],
            recent_blockhash=blockhash,
            address_lookup_table_accounts=[]
        )
        tx = VersionedTransaction(msg, [authority_keypair])
        tx_b64 = base64.b64encode(bytes(tx)).decode()

        logger.info("📤 Sending withdrawal TX...")
        async with session.post(RPC_URL, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [tx_b64, {"encoding": "base64"}]
        }) as resp:
            res = await resp.json()
            if "error" in res:
                logger.error("❌ TX Failed: %s", res["error"])
            else:
                logger.info("✅ Sent! Signature: %s", res["result"])

if __name__ == "__main__":
    asyncio.run(main())
