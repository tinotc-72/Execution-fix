# fast_executor.py

import aiohttp
import base64
import asyncio
import json
import traceback
from typing import Union, Optional, List
from solders.keypair import Keypair
from solders.transaction import Transaction, VersionedTransaction
from solders.message import MessageV0
from solders.instruction import CompiledInstruction, Instruction
from solders.hash import Hash
from jito_service import JitoClient, Bundle  # Import Bundle directly from jito_client
from config import (
    HELIUS_RPC_URL,
    JITO_AUTH_TOKEN,
    JITO_BLOCK_ENGINE,
    JITO_HEADERS,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE,
    JITO_TIP_AMOUNT,
    VALID_JITO_TIP_ACCOUNTS
)

class FastExecutor:
    def __init__(self, keypair: Keypair):
        self.keypair = keypair
        self.session = None
        self.helius_url = HELIUS_RPC_URL
        self.jito_client = JitoClient()
        print(f"🔐 Initializing FastExecutor with wallet: {keypair.pubkey()}")
        print(f"🔑 Using Jito Auth: {JITO_AUTH_TOKEN[:8]}...")
        print("💫 MEV Protection: Enabled (using Jito London Block Engine)")

    async def initialize(self):
        """Initialize sessions"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            await self.jito_client.initialize()
            print("✅ FastExecutor session initialized")

    async def create_jito_bundle(self, tx: VersionedTransaction) -> Optional[Bundle]:
        try:
            if not isinstance(tx, VersionedTransaction):
                print(f"❌ Invalid transaction type: {type(tx)}")
                return None
                
            bundle = Bundle(transactions=[tx])
            
            # Add debug information
            print("\n🔍 Bundle Creation Debug:")
            print(f"Bundle type: {type(bundle)}")
            print(f"Bundle module: {type(bundle).__module__}")
            print(f"Transaction type in bundle: {type(bundle.transactions[0])}")
            print("✅ Created Jito bundle")
            
            return bundle
        except Exception as e:
            print(f"❌ Failed to create bundle: {str(e)}")
            traceback.print_exc()
            return None

    def verify_transaction(self, tx: Union[VersionedTransaction, Bundle]) -> bool:
        """Verify transaction structure before submission"""
        try:
            print("\n📝 Transaction Structure Analysis:")
            
            # Enhanced type checking and Bundle handling
            print(f"Input type: {type(tx)}")
            print(f"Input module: {type(tx).__module__}")
            
            # Handle Bundle input with explicit type checking
            if isinstance(tx, Bundle):
                print(f"Input is Bundle from module: {type(tx).__module__}")
                if not tx.transactions:
                    print("❌ Empty bundle")
                    return False
                print(f"Bundle transaction count: {len(tx.transactions)}")
                tx = tx.transactions[0]
                print(f"Extracted transaction type: {type(tx)}")
                print(f"Extracted transaction module: {type(tx).__module__}")
            
            # Verify VersionedTransaction
            if not isinstance(tx, VersionedTransaction):
                print(f"❌ Invalid transaction type: {type(tx)}")
                print(f"Expected: {VersionedTransaction}")
                print(f"Got: {type(tx)}")
                return False

            if not hasattr(tx, 'message'):
                print("❌ Transaction missing message")
                return False

            message = tx.message
            if not message:
                print("❌ Empty transaction message")
                return False

            # Print header info
            print("\n📑 Header Information:")
            header = message.header
            print(f"Required signatures: {header.num_required_signatures}")
            print(f"Readonly signed accounts: {header.num_readonly_signed_accounts}")
            print(f"Readonly unsigned accounts: {header.num_readonly_unsigned_accounts}")

            # Verify account keys
            if not message.account_keys:
                print("❌ No account keys found")
                return False

            print("\n🔑 Account Keys Analysis:")
            for idx, key in enumerate(message.account_keys):
                is_signer = idx < header.num_required_signatures
                is_writable = (
                    idx < (header.num_required_signatures - header.num_readonly_signed_accounts) or
                    (idx >= header.num_required_signatures and 
                    idx < (len(message.account_keys) - header.num_readonly_unsigned_accounts))
                )
                account_type = "Signer" if is_signer else "Readonly"
                if is_writable:
                    account_type += " (Writable)"
                print(f"[{idx}] {key} - {account_type}")

            # Verify instructions
            if not message.instructions:
                print("❌ No instructions found")
                return False

            print("\n📋 Instructions Analysis:")
            for idx, ix in enumerate(message.instructions):
                print(f"\nInstruction {idx + 1}:")
                
                if ix.program_id_index >= len(message.account_keys):
                    print(f"❌ Invalid program ID index: {ix.program_id_index}")
                    return False
                    
                program_id = message.account_keys[ix.program_id_index]
                print(f"Program ID: {program_id}")

                print("Account References:")
                for acc_idx in ix.accounts:
                    if acc_idx >= len(message.account_keys):
                        print(f"❌ Invalid account index: {acc_idx}")
                        return False
                    account = message.account_keys[acc_idx]
                    is_signer = acc_idx < header.num_required_signatures
                    is_writable = (
                        acc_idx < (header.num_required_signatures - 
                                header.num_readonly_signed_accounts) or
                        (acc_idx >= header.num_required_signatures and 
                        acc_idx < (len(message.account_keys) - 
                                header.num_readonly_unsigned_accounts))
                    )
                    print(f"  [{acc_idx}] {account} (signer: {is_signer}, writable: {is_writable})")

                print(f"Data length: {len(ix.data)} bytes")

            print("\n✅ Transaction verification passed")
            return True

        except Exception as e:
            print(f"❌ Transaction verification failed: {str(e)}")
            traceback.print_exc()
            return False
    
    async def submit_transaction(self, bundle_or_tx: Union[Bundle, VersionedTransaction]) -> Optional[str]:
        """Submit transaction via Jito block engine or fallback to RPC"""
        try:
            if not self.session:
                await self.initialize()

            print("\n🔍 Debug Bundle Processing:")
            print(f"Input type: {type(bundle_or_tx)}")
            print(f"Input module: {type(bundle_or_tx).__module__}")

            # Get transaction from bundle or direct input
            tx = None
            bundle = None

            if isinstance(bundle_or_tx, Bundle):
                print("✅ Input is Bundle")
                if not bundle_or_tx.transactions:
                    print("❌ Empty bundle")
                    return None
                
                tx = bundle_or_tx.transactions[0]
                print(f"Extracted transaction type: {type(tx)}")
                print(f"Extracted transaction module: {type(tx).__module__}")
                
                bundle = bundle_or_tx
            elif isinstance(bundle_or_tx, VersionedTransaction):
                print("✅ Input is VersionedTransaction")
                tx = bundle_or_tx
                bundle = Bundle(transactions=[tx])
            else:
                print(f"❌ Invalid input type: {type(bundle_or_tx)}")
                return None

            # Verify transaction type
            if not isinstance(tx, VersionedTransaction):
                print(f"❌ Invalid transaction type: {type(tx)}")
                print(f"Expected: VersionedTransaction")
                print(f"Got: {type(tx)}")
                return None

            print("\n🚀 Submitting transaction...")
            print(f"💰 Fee payer: {self.keypair.pubkey()}")
            print(f"📝 Transaction size: {len(bytes(tx))} bytes")

            # Try Jito submission first
            try:
                print("\n📦 Submitting to Jito Transaction API...")
                print(f"Bundle type: {type(bundle)}")
                print(f"Bundle module: {type(bundle).__module__}")
                
                result = await self.jito_client.send_bundle(bundle)
                if result:
                    print(f"✅ Transaction submitted via Jito: {result}")
                    return result
            except Exception as e:
                print(f"⚠️ Jito submission failed: {str(e)}")
                traceback.print_exc()

            # Fallback to RPC
            print("\n📡 Falling back to regular RPC submission...")
            return await self._submit_to_rpc(tx)

        except Exception as e:
            print(f"❌ Transaction submission error: {str(e)}")
            traceback.print_exc()
            return None
    
    async def _submit_to_rpc(self, tx: VersionedTransaction) -> Optional[str]:
        """Helper method for RPC submission"""
        try:
            if not isinstance(tx, VersionedTransaction):
                print(f"❌ Invalid transaction type in RPC submission: {type(tx)}")
                return None

            serialized_tx = base64.b64encode(bytes(tx)).decode('utf-8')
            
            async with self.session.post(
                self.helius_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "sendTransaction",
                    "params": [
                        serialized_tx,
                        {
                            "encoding": "base64",
                            "skipPreflight": True,
                            "maxRetries": 0
                        }
                    ]
                },
                timeout=aiohttp.ClientTimeout(total=2)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "error" in result:
                        print(f"❌ RPC error: {result['error']}")
                        return None
                    signature = result.get('result')
                    print(f"✅ Transaction submitted via RPC: {signature}")
                    return signature
                else:
                    print(f"❌ RPC returned status {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ RPC submission error: {str(e)}")
            traceback.print_exc()
            return None

    async def close(self):
        """Close the sessions"""
        if self.session:
            await self.session.close()
            await self.jito_client.close()
            self.session = None
            print("👋 FastExecutor session closed")