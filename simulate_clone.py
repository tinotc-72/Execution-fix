# simulate_clone.py

import base64
import inspect
import json
import aiohttp
from typing import Optional, List, Any
from solders.instruction import Instruction as SoldersInstruction, AccountMeta as SoldersAccountMeta
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.hash import Hash
from solders.signature import Signature
from solders.address_lookup_table_account import AddressLookupTableAccount
from spl.token.instructions import get_associated_token_address, create_associated_token_account
import base58
from utils import (
    fetch_json_rpc,
    get_latest_blockhash,
    rewrite_pda_if_wallet_a,
    get_account_info
)
from config import (
    WALLET_A_ADDRESS,
    RPC_URL,
    WALLET_A,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE
)
from tx_builder import get_jito_fee_instructions, create_jito_tip_instruction

# Use these aliases consistently
Instruction = SoldersInstruction
AccountMeta = SoldersAccountMeta

# Debug prints
print(f"🔬 Confirmed AccountMeta class: {AccountMeta}")
print(f"🔬 AccountMeta repr: {repr(AccountMeta)}")
print("💥 create_jito_tip_instruction loaded from:", inspect.getfile(create_jito_tip_instruction))

# Define WALLET_A once
WALLET_A = Pubkey.from_string(WALLET_A_ADDRESS)

# Known PDA seeds
KNOWN_PDA_SEEDS = {
    b"associated-user",
    b"user",
    b"referral",
    b"stake",
    b"vault",
}

def decode_instruction_data(data_raw: Any) -> bytes:
    """
    Safely decode instruction data from various formats
    """
    try:
        if isinstance(data_raw, str):
            # Handle base64 strings
            try:
                # Add padding if needed
                padding_needed = len(data_raw) % 4
                if padding_needed:
                    data_raw += '=' * (4 - padding_needed)
                return base64.b64decode(data_raw)
            except Exception as e:
                print(f"⚠️ Base64 decode failed: {e}")
                return b''
        elif isinstance(data_raw, list):
            # Handle array of integers
            try:
                return bytes(int(x) for x in data_raw)
            except Exception as e:
                print(f"⚠️ List to bytes conversion failed: {e}")
                return b''
        elif isinstance(data_raw, (bytes, bytearray)):
            # Handle raw bytes
            return bytes(data_raw)
        else:
            print(f"⚠️ Unknown data format: {type(data_raw)}")
            return b''
    except Exception as e:
        print(f"⚠️ Data decode failed: {e}")
        return b''
    

def rewrite_pda_if_wallet_a(pda: Pubkey, program_id: Pubkey, old_pubkey: Pubkey, new_pubkey: Pubkey) -> Pubkey:
    for seed in KNOWN_PDA_SEEDS:
        try:
            old_target, _ = Pubkey.find_program_address([seed, bytes(old_pubkey)], program_id)
            if pda == old_target:
                new_target, _ = Pubkey.find_program_address([seed, bytes(new_pubkey)], program_id)
                print(f"🔁 PDA swapped: {old_target} → {new_target}")
                return new_target
        except Exception:
            continue
    return pda

def debug_print_tx_data(raw_tx: dict):
    """Helper function to print transaction data for debugging"""
    print("\n🔍 Transaction Debug Info:")
    if isinstance(raw_tx.get("transaction"), list):
        print("Transaction format: [data, encoding]")
    else:
        print("Transaction format: dict")
    
    print(f"Keys found: {list(raw_tx.keys())}")
    print(f"Transaction type: {type(raw_tx.get('transaction'))}")

async def fetch_json_rpc(method: str, params: list) -> dict:
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        async with session.post(RPC_URL, json=payload) as resp:
            return await resp.json()

async def clone_transaction_from_wallet_a(raw_tx: dict, your_wallet: Keypair) -> Optional[VersionedTransaction]:
    print("🧪 clone_transaction_from_wallet_a STARTED")
    debug_print_tx_data(raw_tx)

    try:
        # Extract transaction data
        tx = raw_tx.get("transaction")
        if isinstance(tx, list) and len(tx) == 2:
            tx_data, encoding = tx
            if encoding == "base64":
                decoded = base64.b64decode(tx_data)
                orig_tx = VersionedTransaction.from_bytes(decoded)
                msg = orig_tx.message
                print("✅ Decoded base64 transaction")
            else:
                print(f"❌ Unsupported encoding: {encoding}")
                return None
        else:
            print("❌ Unexpected transaction format")
            return None

        # Get payer
        payer = your_wallet.pubkey()
        print(f"💰 Using payer: {payer}")

        # Get recent blockhash
        blockhash_resp = await get_latest_blockhash()
        if "error" in blockhash_resp:
            print("❌ Failed to get blockhash")
            return None
        
        blockhash = Hash.from_string(blockhash_resp["result"]["value"]["blockhash"])
        print(f"📦 Using blockhash: {blockhash}")

        # Create Jito fee instructions
        jito_instructions = get_jito_fee_instructions(payer)
        print(f"💰 Added {len(jito_instructions)} Jito fee instructions")

        # Initialize new instructions list with Jito fee instructions
        new_instructions = list(jito_instructions)
        compute_budget_data = []  # Store ComputeBudget instructions data
        compute_budget_processed = False

        print(f"📝 Original instructions count: {len(msg.instructions)}")
        print(f"🔑 Account keys count: {len(msg.account_keys)}")

        # Create mapping of lookup table indexes to accounts
        lookup_table_accounts = {}
        if hasattr(msg, 'address_table_lookups') and msg.address_table_lookups:
            base_index = len(msg.account_keys)  # Start after static keys
            for lookup in msg.address_table_lookups:
                table_key = lookup.account_key
                
                # Map writable indexes
                for i, idx in enumerate(lookup.writable_indexes):
                    adjusted_idx = base_index + i
                    lookup_table_accounts[adjusted_idx] = {
                        'key': lookup.account_key,
                        'is_writable': True,
                        'is_signer': False,
                        'original_idx': int(idx)
                    }
                
                # Map readonly indexes
                readonly_base = base_index + len(lookup.writable_indexes)
                for i, idx in enumerate(lookup.readonly_indexes):
                    adjusted_idx = readonly_base + i
                    lookup_table_accounts[adjusted_idx] = {
                        'key': lookup.account_key,
                        'is_writable': False,
                        'is_signer': False,
                        'original_idx': int(idx)
                    }
                
                print(f"📚 Lookup table {table_key}:")
                print(f"  Writable indexes mapped: {base_index} -> {base_index + len(lookup.writable_indexes) - 1}")
                print(f"  Readonly indexes mapped: {readonly_base} -> {readonly_base + len(lookup.readonly_indexes) - 1}")
                
                base_index = readonly_base + len(lookup.readonly_indexes)
            
            print(f"📚 Found {len(msg.address_table_lookups)} lookup tables with {len(lookup_table_accounts)} total mapped accounts")

        # First pass: collect ComputeBudget instructions
        for i, ix in enumerate(msg.instructions):
            try:
                program_id = msg.account_keys[ix.program_id_index]
                if str(program_id) == "ComputeBudget111111111111111111111111111111" and not compute_budget_processed:
                    compute_budget_data.append(ix.data)
                    print(f"📝 Saved ComputeBudget instruction data {len(compute_budget_data)}/2")
                    if len(compute_budget_data) == 2:
                        compute_budget_processed = True

            except Exception as e:
                print(f"⚠️ Failed to process instruction {i}: {e}")
                continue

        # Add ComputeBudget instructions if we found any
        compute_budget_program = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
        for i, data in enumerate(compute_budget_data[:2]):  # Only use first two
            new_ix = Instruction(
                program_id=compute_budget_program,
                accounts=[],
                data=data
            )
            new_instructions.append(new_ix)
            print(f"✅ Added ComputeBudget instruction {i+1}/2")

        # Process regular instructions
        for i, ix in enumerate(msg.instructions):
            try:
                program_id = msg.account_keys[ix.program_id_index]
                print(f"\n🔍 Processing instruction {i}:")
                print(f"  Program ID: {program_id}")
                print(f"  Account indexes: {ix.accounts}")

                # Skip ComputeBudget instructions as we've already handled them
                if str(program_id) == "ComputeBudget111111111111111111111111111111":
                    print(f"⏭️ Skipping ComputeBudget instruction {i} (already processed)")
                    continue

                # Process accounts
                accounts = []
                for acc_idx in ix.accounts:
                    print(f"    Processing account index {acc_idx}:")
                    account_key = None
                    is_signer = False
                    is_writable = False

                    # First try static keys
                    if acc_idx < len(msg.account_keys):
                        account_key = msg.account_keys[acc_idx]
                        is_signer = acc_idx < msg.header.num_required_signatures
                        is_writable = (
                            acc_idx < (msg.header.num_required_signatures - msg.header.num_readonly_signed_accounts)
                            or (
                                acc_idx >= msg.header.num_required_signatures
                                and acc_idx < (len(msg.account_keys) - msg.header.num_readonly_unsigned_accounts)
                            )
                        )
                        print(f"      Found in static keys: {account_key} (signer: {is_signer}, writable: {is_writable})")
                    
                    # Then try lookup tables with correct index mapping
                    elif acc_idx in lookup_table_accounts:
                        account_info = lookup_table_accounts[acc_idx]
                        account_key = account_info['key']
                        is_writable = account_info['is_writable']
                        is_signer = account_info['is_signer']
                        print(f"      Found in lookup table: {account_key} (writable: {is_writable}, original_idx: {account_info['original_idx']})")
                    else:
                        print(f"      ⚠️ Account index {acc_idx} not found in static keys or lookup tables")
                        continue

                    if account_key:
                        # Replace Wallet A's pubkey with your wallet's pubkey
                        new_key = payer if account_key == WALLET_A else account_key
                        accounts.append(AccountMeta(
                            pubkey=new_key,
                            is_signer=is_signer,
                            is_writable=is_writable
                        ))

                if accounts:
                    new_ix = Instruction(
                        program_id=program_id,
                        accounts=accounts,
                        data=ix.data
                    )
                    new_instructions.append(new_ix)
                    print(f"✅ Processed instruction {i}: program={program_id}, accounts={len(accounts)}")
                else:
                    print(f"⚠️ No valid accounts for instruction {i}")

            except Exception as e:
                print(f"⚠️ Failed to process instruction {i}: {e}")
                continue

        print(f"\n📋 Total instructions: {len(new_instructions)}")

        # Create new message
        new_msg = MessageV0.try_compile(
            payer=payer,
            instructions=new_instructions,
            recent_blockhash=blockhash,
            address_lookup_table_accounts=[]
        )

        # Create transaction first with default signature
        tx = VersionedTransaction.populate(
            message=new_msg,
            signatures=[Signature.default()]  # Start with a default signature
        )

        # Sign the transaction
        signed_msg = your_wallet.sign_message(bytes(new_msg))
        tx.signatures[0] = signed_msg  # Replace default signature with real one

        print("\n✅ Transaction cloned successfully!")
        try:
            serialized = bytes(tx)
            print(f"📏 Size: {len(serialized)} bytes")
        except Exception as e:
            print(f"⚠️ Size calculation failed: {e}")
        
        print(f"🔑 Signature: {tx.signatures[0]}")

        return tx

    except Exception as e:
        print(f"❌ Clone failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("🔍 Starting test...")
    sig = "4KgimS8mUVwbY1uC8Suev96ZyCnP1ULnEybFxFT6rkDkisA4mi3ePmovY94QneWvuA9SeLCGCSEEjbwfZPzaS9kD"
    tx_resp = await fetch_json_rpc("getTransaction", [sig, {"encoding": "base64", "maxSupportedTransactionVersion": 0}])
    tx_data = tx_resp.get("result")
    if not tx_data:
        print("❌ No transaction found.")
        return

    tx = await clone_transaction_from_wallet_a(tx_data, WALLET)
    if tx:
        print("✅ Cloned transaction:")
        print(tx.to_json())
    else:
        print("❌ Transaction cloning failed.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
