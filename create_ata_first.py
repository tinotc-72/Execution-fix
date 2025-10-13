#!/usr/bin/env python3

import asyncio
import httpx
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
import base64
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def create_ata_first():
    """Create ATA in a separate transaction first"""
    
    # Setup
    private_key = os.getenv('PRIVATE_KEY')
    private_key_bytes = base64.b64decode(private_key)
    keypair = Keypair.from_bytes(private_key_bytes)
    
    user_pubkey = keypair.pubkey()
    mint = Pubkey.from_string("8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump")
    TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
    RENT_PROGRAM_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
    
    # Derive ATA address
    user_token_account, _ = Pubkey.find_program_address(
        [
            bytes(user_pubkey),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )
    
    print(f"Creating ATA: {user_token_account}")
    
    # Create ATA instruction
    create_ata_accounts = [
        AccountMeta(pubkey=user_pubkey, is_signer=True, is_writable=True),
        AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=user_pubkey, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    
    create_ata_ix = Instruction(
        program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
        accounts=create_ata_accounts,
        data=bytes()
    )
    
    # Build transaction
    instructions = [
        set_compute_unit_limit(200_000),
        set_compute_unit_price(2_000_000),
        create_ata_ix
    ]
    
    # Get recent blockhash
    helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    resp = httpx.post(helius_url, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getLatestBlockhash"
    })
    
    blockhash_data = resp.json()
    recent_blockhash = blockhash_data["result"]["value"]["blockhash"]
    
    # Create message and transaction
    message = MessageV0.try_compile(
        payer=user_pubkey,
        instructions=instructions,
        address_lookup_table_accounts=[],
        recent_blockhash=recent_blockhash
    )
    
    transaction = VersionedTransaction(message, [keypair])
    
    # Send transaction
    print("Sending ATA creation transaction...")
    serialized = bytes(transaction)
    
    resp = httpx.post(helius_url, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendTransaction",
        "params": [base64.b64encode(serialized).decode(), {"encoding": "base64"}]
    })
    
    result = resp.json()
    if "result" in result:
        signature = result["result"]
        print(f"✅ ATA creation sent: {signature}")
        
        # Wait for confirmation
        print("Waiting for confirmation...")
        await asyncio.sleep(3)
        
        # Check status
        status_resp = httpx.post(helius_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
        })
        
        status_result = status_resp.json()
        if "result" in status_result and status_result["result"]:
            meta = status_result["result"].get("meta", {})
            if meta.get("err"):
                print(f"❌ ATA creation failed: {meta['err']}")
                return False
            else:
                print(f"✅ ATA creation successful!")
                return True
        else:
            print("⏳ Transaction still pending...")
            return False
    else:
        print(f"❌ Failed to send ATA creation: {result}")
        return False

if __name__ == "__main__":
    asyncio.run(create_ata_first())