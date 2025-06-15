# test_bundle.py

import os
import asyncio
import traceback
import json
from base58 import b58encode
from datetime import datetime, UTC
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import VersionedTransaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solana.rpc.async_api import AsyncClient
from models import Bundle
from config import (
    DECODED_PRIVATE_KEY,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE,
    JITO_TIP_AMOUNT,
    WALLET_A,
    VALID_JITO_TIP_ACCOUNTS,
    COMPUTE_BUDGET_PROGRAM_ID,
    SYS_PROGRAM_ID,
    JITO_TIP_PROGRAM_ID,
    JITO_HEADERS,
    JITO_BLOCK_ENGINE,
    BUNDLE_CONFIG
)
from tx_builder import create_and_sign_transaction, create_jito_bundle, submit_to_jito_block_engine

async def simulate_wallet_a_trade():
    """Simulate a trade from wallet A that we want to copy"""
    instructions = []
    
    # Add compute budget instructions
    instructions.append(
        set_compute_unit_limit(COMPUTE_UNIT_LIMIT)
    )
    instructions.append(
        set_compute_unit_price(COMPUTE_UNIT_PRICE)
    )
    
    # Add Jito tip instruction (using first tip account)
    tip_ix = transfer(
        TransferParams(
            from_pubkey=WALLET_A,
            to_pubkey=VALID_JITO_TIP_ACCOUNTS[0],
            lamports=JITO_TIP_AMOUNT
        )
    )
    instructions.append(tip_ix)
    
    # Add main trade instruction (simulated)
    trade_ix = transfer(
        TransferParams(
            from_pubkey=WALLET_A,
            to_pubkey=Pubkey.new_unique(),
            lamports=100_000_000  # 0.1 SOL
        )
    )
    instructions.append(trade_ix)
    
    return instructions

async def test_bundle_creation():
    client = None
    try:
        print("\nStarting Bundle Tests at", datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 47)
        
        print(f"\nCurrent Date and Time (UTC): {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Current User's Login: tinotc-72\n")
        
        # 1. Load test wallet
        print("\n1️⃣ Testing Keypair Loading")
        print("-" * 27)
        keypair = Keypair.from_bytes(DECODED_PRIVATE_KEY)
        print(f"✅ Test wallet loaded: {keypair.pubkey()}")
        
        # 2. Create test instructions
        print("\n2️⃣ Simulating Wallet A Trade")
        print("-" * 27)
        instructions = await simulate_wallet_a_trade()
        print(f"✅ Created {len(instructions)} instructions")
        for i, ix in enumerate(instructions, 1):
            print(f"   Instruction {i}: {ix.program_id}")
            
        # 3. Get recent blockhash
        print("\n3️⃣ Getting Recent Blockhash")
        print("-" * 27)
        client = AsyncClient("https://api.mainnet-beta.solana.com")
        blockhash_resp = await client.get_latest_blockhash()
        blockhash = blockhash_resp.value.blockhash
        blockhash_str = str(blockhash)
        print(f"✅ Got blockhash: {blockhash_str[:8]}...")
        
        # 4. Create versioned transaction
        print("\n4️⃣ Creating Versioned Transaction")
        print("-" * 27)
        # Remove await since create_and_sign_transaction is not async
        versioned_tx = create_and_sign_transaction(
            keypair=keypair,
            instructions=instructions,
            recent_blockhash=blockhash_str
        )
        if not versioned_tx:
            raise Exception("Failed to create transaction")
        print("✅ Transaction created successfully")
        
        # 5. Create bundle
        print("\n5️⃣ Creating Jito Bundle")
        print("-" * 27)
        bundle = create_jito_bundle(versioned_tx)
        if not bundle:
            raise Exception("Failed to create bundle")
        print("✅ Bundle created successfully")
        
        # Debug print bundle contents
        print("\n🔍 Bundle Contents:")
        print(f"Bundle type: {type(bundle)}")
        print("Bundle structure:")
        for key, value in bundle.items():
            print(f"  {key}: {type(value)}")
        
        # 6. Test submission
        print("\n6️⃣ Testing Jito Submission")
        print("-" * 27)
        
        print("\n🔧 Initializing Jito London Client:")
        print("🌍 Region: London (🇬🇧)")
        print(f"🔗 Block Engine: {JITO_BLOCK_ENGINE}")
        print("📡 Relayer: http://london.mainnet.relayer.jito.wtf:8100")
        print("⏰ NTP Server: ntp.london.jito.wtf")
        print("📦 Shred Receiver: 142.91.127.175:1002")
        
        success = await submit_to_jito_block_engine(
            bundle=bundle,
            auth_token=JITO_HEADERS["x-jito-auth"]
        )
        
        if success:
            print("\n✅ Bundle test completed successfully")
        else:
            print("\n❌ Bundle submission failed")
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        traceback.print_exc()
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    print(f"Current Date and Time (UTC): {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current User's Login: tinotc-72")
    asyncio.run(test_bundle_creation())

