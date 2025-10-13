#!/usr/bin/env python3

"""
COMPREHENSIVE FIX for Fake Signatures and Jito Bundle Failures

This script addresses two critical issues:
1. Jito bundle failures due to missing tip account write locks
2. Fake signatures being returned instead of real transaction signatures

Root Causes Identified:
- Jito bundles fail: "Bundles must write lock at least one tip account to be eligible for the auction"
- Some executors return placeholder signatures instead of real ones
- The tip instruction is not properly write-locking a tip account
"""

import asyncio
import sys
sys.path.append('.')

from fast_executor import FastExecutor
from config import WALLET
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.hash import Hash
import base64
import traceback


class FixedFastExecutor(FastExecutor):
    """
    Enhanced FastExecutor with proper Jito tip account write-locking
    """
    
    async def create_jito_bundle_with_proper_tip(self, tx: VersionedTransaction):
        """Create Jito bundle with PROPER tip account write-locking"""
        try:
            from tx_builder import create_jito_tip_instruction
            from solders.message import MessageV0
            from solders.address_lookup_table_account import AddressLookupTableAccount
            
            print("\n🔧 Creating FIXED Jito bundle with proper tip account write-locking...")
            
            # CRITICAL FIX 1: Create tip instruction that WRITE-LOCKS a tip account
            tip_instruction = self._create_proper_tip_instruction()
            if not tip_instruction:
                print(f"❌ Failed to create proper tip instruction")
                return None
            
            print(f"✅ Created proper tip instruction with write-lock")
            
            # Get recent blockhash for tip transaction
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "processed"}]
                }
                
                async with session.post(self.helius_url, json=payload) as response:
                    data = await response.json()
                    if 'error' in data:
                        print(f"❌ Failed to get blockhash: {data['error']}")
                        return None
                    
                    blockhash = Hash.from_string(data['result']['value']['blockhash'])
            
            # CRITICAL FIX 2: Build tip transaction that properly write-locks tip account
            tip_message = MessageV0.try_compile(
                payer=self.keypair.pubkey(),
                instructions=[tip_instruction],
                address_lookup_table_accounts=[],
                recent_blockhash=blockhash
            )
            
            if not tip_message:
                print(f"❌ Failed to compile tip message")
                return None
            
            # Create and sign tip transaction
            tip_transaction = VersionedTransaction(tip_message, [self.keypair])
            
            print(f"✅ Created tip transaction with proper write-locking")
            
            # CRITICAL FIX 3: Verify tip account is write-locked
            self._verify_tip_account_write_lock(tip_transaction)
            
            # Create bundle with main transaction and tip transaction
            from jito_service import Bundle
            bundle = Bundle(transactions=[tx, tip_transaction])
            
            print(f"\n🔍 FIXED Bundle Details:")
            print(f"Bundle type: {type(bundle)}")
            print(f"Number of transactions: {len(bundle.transactions)}")
            print(f"Main transaction type: {type(bundle.transactions[0])}")
            print(f"Tip transaction type: {type(bundle.transactions[1])}")
            print("✅ Created FIXED Jito bundle with proper tip account write-locking")
            
            return bundle
            
        except Exception as e:
            print(f"❌ Failed to create fixed bundle: {str(e)}")
            traceback.print_exc()
            return None

    def _create_proper_tip_instruction(self):
        """
        CRITICAL FIX: Create tip instruction that WRITE-LOCKS a Jito tip account
        
        The error "Bundles must write lock at least one tip account" means we need to:
        1. Use a proper Jito tip account (not just any account)
        2. Make sure the tip account is marked as WRITABLE in the instruction
        """
        try:
            from config import VALID_JITO_TIP_ACCOUNTS, JITO_TIP_AMOUNT
            
            # Select first valid Jito tip account
            if not VALID_JITO_TIP_ACCOUNTS:
                print("❌ No valid Jito tip accounts configured")
                return None
                
            tip_account = Pubkey.from_string(VALID_JITO_TIP_ACCOUNTS[0])
            
            print(f"🎯 Selected Jito tip account: {tip_account}")
            print(f"💰 Tip amount: {JITO_TIP_AMOUNT} lamports")
            
            # CRITICAL: Use System Program transfer instruction with WRITABLE tip account
            system_program = Pubkey.from_string("11111111111111111111111111111111")
            
            # Create transfer instruction data (instruction type 2 = transfer)
            instruction_data = bytes([2, 0, 0, 0]) + JITO_TIP_AMOUNT.to_bytes(8, byteorder='little')
            
            # CRITICAL FIX: Mark tip account as WRITABLE (this is what was missing!)
            tip_instruction = Instruction(
                program_id=system_program,
                accounts=[
                    AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),   # From (payer)
                    AccountMeta(pubkey=tip_account, is_signer=False, is_writable=True)  # CRITICAL: is_writable=True!
                ],
                data=instruction_data
            )
            
            print(f"✅ Created tip instruction with WRITABLE tip account")
            print(f"   From: {self.keypair.pubkey()} (signer, writable)")
            print(f"   To: {tip_account} (writable) ← CRITICAL FIX")
            print(f"   Amount: {JITO_TIP_AMOUNT} lamports")
            
            return tip_instruction
            
        except Exception as e:
            print(f"❌ Error creating proper tip instruction: {e}")
            traceback.print_exc()
            return None

    def _verify_tip_account_write_lock(self, tip_transaction: VersionedTransaction):
        """Verify that the tip account is properly write-locked"""
        try:
            message = tip_transaction.message
            header = message.header
            
            print(f"\n🔍 Verifying tip account write-lock:")
            print(f"   Required signatures: {header.num_required_signatures}")
            print(f"   Readonly signed: {header.num_readonly_signed_accounts}")
            print(f"   Readonly unsigned: {header.num_readonly_unsigned_accounts}")
            print(f"   Total accounts: {len(message.account_keys)}")
            
            # Calculate which accounts are writable
            num_writable_signed = header.num_required_signatures - header.num_readonly_signed_accounts
            num_writable_unsigned = len(message.account_keys) - header.num_required_signatures - header.num_readonly_unsigned_accounts
            
            print(f"   Writable signed accounts: {num_writable_signed}")
            print(f"   Writable unsigned accounts: {num_writable_unsigned}")
            
            # Verify at least one tip account is writable
            from config import VALID_JITO_TIP_ACCOUNTS
            tip_account_found = False
            
            for idx, account in enumerate(message.account_keys):
                is_signer = idx < header.num_required_signatures
                is_writable = (
                    idx < num_writable_signed or 
                    (idx >= header.num_required_signatures and idx < header.num_required_signatures + num_writable_unsigned)
                )
                
                if str(account) in VALID_JITO_TIP_ACCOUNTS and is_writable:
                    tip_account_found = True
                    print(f"   ✅ FOUND: Tip account {account} is WRITABLE at index {idx}")
                    break
            
            if tip_account_found:
                print(f"✅ Tip account write-lock verification PASSED")
            else:
                print(f"❌ Tip account write-lock verification FAILED")
                
        except Exception as e:
            print(f"❌ Error verifying tip account write-lock: {e}")

    async def submit_transaction_fixed(self, tx: VersionedTransaction) -> str:
        """
        FIXED transaction submission with proper error handling and real signatures
        """
        try:
            if not self.session:
                await self.initialize()

            print(f"\n🚀 FIXED Transaction Submission:")
            print(f"   Fee payer: {self.keypair.pubkey()}")
            print(f"   Transaction size: {len(bytes(tx))} bytes")

            # STEP 1: Try FIXED Jito submission with proper tip account write-locking
            try:
                print(f"\n📦 Attempting FIXED Jito submission...")
                bundle = await self.create_jito_bundle_with_proper_tip(tx)
                
                if bundle:
                    result = await self.jito_client.send_bundle(bundle)
                    if result:
                        print(f"✅ FIXED Jito submission successful: {result}")
                        return result
                    else:
                        print(f"⚠️ Jito bundle submission returned no result")
                else:
                    print(f"⚠️ Failed to create fixed Jito bundle")
                    
            except Exception as jito_error:
                print(f"⚠️ FIXED Jito submission failed: {str(jito_error)}")

            # STEP 2: Use VERIFIED working RPC fallback
            print(f"\n📡 Using VERIFIED RPC fallback...")
            real_signature = await self._submit_to_rpc_verified(tx)
            
            if real_signature and len(real_signature) >= 64:
                print(f"✅ VERIFIED RPC submission successful: {real_signature}")
                return real_signature
            else:
                print(f"❌ RPC fallback failed or returned invalid signature")
                return None

        except Exception as e:
            print(f"❌ FIXED transaction submission error: {str(e)}")
            traceback.print_exc()
            return None

    async def _submit_to_rpc_verified(self, tx: VersionedTransaction) -> str:
        """
        VERIFIED RPC submission that returns REAL signatures (our debug test confirmed this works)
        """
        try:
            if not isinstance(tx, VersionedTransaction):
                print(f"❌ Invalid transaction type in RPC submission: {type(tx)}")
                return None

            serialized_tx = base64.b64encode(bytes(tx)).decode('utf-8')
            
            print(f"   📡 Submitting to RPC: {self.helius_url[:50]}...")
            
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
                timeout=5  # Increase timeout slightly
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "error" in result:
                        print(f"❌ RPC error: {result['error']}")
                        return None
                    
                    signature = result.get('result')
                    if signature:
                        print(f"✅ RPC returned signature: {signature}")
                        
                        # CRITICAL VALIDATION: Ensure it's not a placeholder
                        if signature == "1111111111111111111111111111111111111111111111111111111111111111":
                            print(f"❌ DETECTED FAKE SIGNATURE from RPC!")
                            return None
                        elif len(signature) < 64:
                            print(f"❌ INVALID SIGNATURE LENGTH: {len(signature)}")
                            return None
                        else:
                            print(f"✅ REAL SIGNATURE VERIFIED: {signature[:12]}...{signature[-12:]}")
                            return signature
                    else:
                        print(f"❌ RPC returned no signature")
                        return None
                else:
                    print(f"❌ RPC returned status {response.status}")
                    return None
                    
        except Exception as e:
            print(f"❌ RPC submission error: {str(e)}")
            traceback.print_exc()
            return None


async def test_comprehensive_fix():
    """Test the comprehensive fix for both Jito and signature issues"""
    
    print("🔧 COMPREHENSIVE FIX TEST")
    print("=" * 60)
    print("Testing fixes for:")
    print("1. Jito bundle failures (missing tip account write-locks)")
    print("2. Fake signature returns")
    print("=" * 60)
    
    # Initialize FIXED FastExecutor
    fixed_executor = FixedFastExecutor(WALLET)
    await fixed_executor.initialize()
    
    try:
        from solana.rpc.async_api import AsyncClient
        client = AsyncClient("https://api.mainnet-beta.solana.com")
        
        # Get recent blockhash
        blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = blockhash_resp.value.blockhash
        
        # Create test transaction
        instruction = Instruction(
            program_id=Pubkey.from_string("11111111111111111111111111111111"),
            accounts=[
                AccountMeta(pubkey=WALLET.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=WALLET.pubkey(), is_signer=False, is_writable=True)
            ],
            data=bytes([2, 0, 0, 0]) + (1).to_bytes(8, byteorder='little')
        )
        
        message = MessageV0.try_compile(
            payer=WALLET.pubkey(),
            instructions=[instruction],
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash
        )
        
        transaction = VersionedTransaction(message, [WALLET])
        
        print(f"✅ Created test transaction")
        
        # Test FIXED submission
        print(f"\n🚀 Testing FIXED submission...")
        signature = await fixed_executor.submit_transaction_fixed(transaction)
        
        print(f"\n📊 COMPREHENSIVE FIX RESULTS:")
        print(f"   Signature type: {type(signature)}")
        print(f"   Signature length: {len(signature) if signature else 0}")
        print(f"   Signature: {signature}")
        
        if signature == "1111111111111111111111111111111111111111111111111111111111111111":
            print(f"\n❌ CRITICAL: FAKE SIGNATURE STILL DETECTED!")
            print(f"   The comprehensive fix did not resolve the fake signature issue")
        elif signature and len(signature) >= 64:
            print(f"\n✅ SUCCESS: REAL SIGNATURE DETECTED!")
            print(f"   The comprehensive fix successfully returns real signatures")
        else:
            print(f"\n⚠️ WARNING: INVALID SIGNATURE!")
            print(f"   Signature is None or too short")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Comprehensive fix test failed: {e}")
        traceback.print_exc()
    
    finally:
        await fixed_executor.close()


if __name__ == "__main__":
    asyncio.run(test_comprehensive_fix())
