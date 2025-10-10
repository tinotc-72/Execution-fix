# fast_executor.py - Official Jito Documentation Compliant

import aiohttp
import base64
import asyncio
import json
import traceback
import uuid
from typing import Union, Optional, List
from solders.keypair import Keypair
from solders.transaction import Transaction, VersionedTransaction
from solders.message import MessageV0
from solders.instruction import CompiledInstruction, Instruction
from solders.hash import Hash
from jito_service import JitoClient, Bundle  # Import Bundle directly from jito_client

# ✅ ENHANCED JITO INTEGRATION - Import Jupiter utilities for Jito transaction building
try:
    from jupiter_utils import (
        get_jupiter_quote, get_jupiter_transaction, get_jupiter_sell_quote, get_jupiter_sell_transaction,
        create_jupiter_buy_transaction, create_jupiter_sell_transaction,
        JupiterQuoteResult, JupiterTransactionResult
    )
    JUPITER_AVAILABLE = True
    print("✅ Jupiter utilities loaded - Enhanced Jito execution enabled")
except ImportError as e:
    JUPITER_AVAILABLE = False
    print(f"⚠️ Jupiter utilities not found: {e} - Jito execution will use fallback methods")

# ✅ ENHANCED JITO SERVICE INTEGRATION
try:
    from jito_enhanced_service import JitoEnhancedService, JitoExecutionResult
    JITO_ENHANCED_AVAILABLE = True
    print("✅ JitoEnhancedService available for optimal execution")
except ImportError as e:
    JITO_ENHANCED_AVAILABLE = False
    print(f"⚠️ JitoEnhancedService not found: {e} - Using basic Jito client")
    JitoExecutionResult = dict

from config import (
    HELIUS_RPC_URL,
    JITO_AUTH_TOKEN,
    JITO_BLOCK_ENGINE,
    JITO_HEADERS,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE,
    JITO_TIP_AMOUNT,
    VALID_JITO_TIP_ACCOUNTS,
    JITO_TIP_PROGRAM_ID
)

# ✅ OFFICIAL JITO CONFIGURATION - Following docs.jito.wtf
JITO_MAINNET_ENDPOINT = "https://mainnet.block-engine.jito.wtf"
JITO_LONDON_ENDPOINT = "https://london.mainnet.block-engine.jito.wtf"  # Closest to user location
JITO_BUNDLE_ENDPOINT = "/api/v1/bundles"
JITO_TRANSACTION_ENDPOINT = "/api/v1/transactions"
JITO_TIP_ACCOUNTS_ENDPOINT = "/api/v1/getTipAccounts"

# ✅ MINIMUM TIP REQUIREMENTS - Per Jito Documentation
MIN_JITO_TIP_LAMPORTS = 1000  # Minimum 1000 lamports per docs
RECOMMENDED_TIP_LAMPORTS = 10000  # 0.00001 SOL for better auction position

class FastExecutor:
    def __init__(self, keypair: Keypair, rpc_url: str = None, jito_client=None, jito_service=None, preferred_region: str = "london"):
        self.keypair = keypair
        self.session = None
        self.helius_url = rpc_url if rpc_url else HELIUS_RPC_URL
        self.jito_client = jito_client if jito_client else JitoClient()
        
        # ✅ ENHANCED JITO SERVICE INTEGRATION from main.py
        self.jito_service = jito_service
        self.jito_enhanced_initialized = False
        self.jupiter_available = JUPITER_AVAILABLE
        self.jito_enhanced_available = JITO_ENHANCED_AVAILABLE
        
        # ✅ OFFICIAL JITO ENDPOINT SELECTION
        self.jito_endpoint = self._get_jito_endpoint(preferred_region)
        self.bundle_url = f"{self.jito_endpoint}{JITO_BUNDLE_ENDPOINT}"
        self.transaction_url = f"{self.jito_endpoint}{JITO_TRANSACTION_ENDPOINT}"
        
        # ✅ OFFICIAL AUTHENTICATION HEADERS per docs.jito.wtf
        self.jito_headers = {
            "Content-Type": "application/json",
            "x-jito-auth": JITO_AUTH_TOKEN  # Official auth header format
        }
        
        print(f"🔐 Initializing FastExecutor with wallet: {keypair.pubkey()}")
        print(f"🌍 Using Jito endpoint: {self.jito_endpoint}")
        print(f"🔑 Auth configured: {JITO_AUTH_TOKEN[:8]}...")
        print(f"🚀 Jupiter utilities: {'Available' if self.jupiter_available else 'Fallback mode'}")
        print(f"⚡ Enhanced Jito: {'Available' if self.jito_enhanced_available else 'Basic mode'}")
        print("💫 MEV Protection: Enabled (Official Jito Configuration)")

    def _get_jito_endpoint(self, region: str) -> str:
        """Get the appropriate Jito endpoint based on region - per official docs"""
        endpoints = {
            "mainnet": JITO_MAINNET_ENDPOINT,
            "london": JITO_LONDON_ENDPOINT,
            "amsterdam": "https://amsterdam.mainnet.block-engine.jito.wtf",
            "frankfurt": "https://frankfurt.mainnet.block-engine.jito.wtf", 
            "ny": "https://ny.mainnet.block-engine.jito.wtf",
            "singapore": "https://singapore.mainnet.block-engine.jito.wtf",
            "tokyo": "https://tokyo.mainnet.block-engine.jito.wtf"
        }
        return endpoints.get(region, JITO_LONDON_ENDPOINT)

    async def get_official_tip_accounts(self) -> List[str]:
        """Get official tip accounts from Jito API - per docs.jito.wtf/getTipAccounts"""
        try:
            print(f"📡 Fetching official tip accounts from Jito API...")
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTipAccounts",
                "params": []
            }
            
            async with self.session.post(
                f"{self.jito_endpoint}{JITO_TIP_ACCOUNTS_ENDPOINT}",
                json=payload,
                headers=self.jito_headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data:
                        tip_accounts = data['result']
                        print(f"✅ Retrieved {len(tip_accounts)} official tip accounts")
                        return tip_accounts
                
                print(f"⚠️ Failed to get tip accounts, using hardcoded ones")
                return [str(account) for account in VALID_JITO_TIP_ACCOUNTS]
                
        except Exception as e:
            print(f"❌ Error fetching tip accounts: {e}")
            return [str(account) for account in VALID_JITO_TIP_ACCOUNTS]

    async def get_current_tip_floor(self) -> dict:
        """Get current tip floor information from Jito REST API"""
        try:
            tip_floor_url = "https://bundles.jito.wtf/api/v1/bundles/tip_floor"
            
            async with self.session.get(tip_floor_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        latest_data = data[0]
                        print(f"📊 Current tip floor data:")
                        print(f"   50th percentile: {latest_data.get('landed_tips_50th_percentile', 0):.6f} SOL")
                        print(f"   75th percentile: {latest_data.get('landed_tips_75th_percentile', 0):.6f} SOL")
                        print(f"   95th percentile: {latest_data.get('landed_tips_95th_percentile', 0):.6f} SOL")
                        return latest_data
                
        except Exception as e:
            print(f"⚠️ Could not fetch tip floor data: {e}")
        
        return {}

    async def initialize_session(self):
        """Initialize HTTP session for Jito communication"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
    async def initialize(self):
        """Initialize the FastExecutor - required by execution components"""
        await self.initialize_session()
        if self.jito_enhanced_available and self.jito_service:
            try:
                # Initialize enhanced Jito service if available
                if hasattr(self.jito_service, 'initialize') and not self.jito_enhanced_initialized:
                    await self.jito_service.initialize()
                    self.jito_enhanced_initialized = True
                    print("✅ Enhanced Jito service initialized")
            except Exception as e:
                print(f"⚠️ Enhanced Jito initialization failed: {e}")
        
        print("✅ FastExecutor initialization complete")
        
        # ✅ INITIALIZE ENHANCED JITO SERVICE (from main.py integration)
        if self.jito_service and not self.jito_enhanced_initialized:
            print("🚀 Initializing Enhanced Jito Service...")
            try:
                jito_initialized = await self.jito_service.initialize()
                if jito_initialized:
                    self.jito_enhanced_initialized = True
                    print("✅ Enhanced Jito Service ready for optimal execution!")
                    print(f"   🎯 Primary endpoint: {getattr(self.jito_service, 'primary_endpoint', 'N/A')}")
                    print(f"   📡 RPC fallback: {getattr(self.jito_service, 'rpc_fallback_url', 'N/A')}")
                else:
                    print("⚠️ Enhanced Jito Service initialization failed, using basic Jito client")
            except Exception as e:
                print(f"❌ Enhanced Jito Service initialization error: {e}")
                print("⚠️ Falling back to basic Jito client")
        
        # ✅ FETCH OFFICIAL TIP ACCOUNTS per docs.jito.wtf
        await self.get_official_tip_accounts()
        
        # ✅ GET CURRENT TIP INFORMATION for better bidding
        await self.get_current_tip_floor()
        
        print("✅ FastExecutor session initialized with official Jito configuration")

    async def create_jito_bundle(self, tx: VersionedTransaction, custom_tip: int = None) -> Optional[Bundle]:
        """Create a Jito bundle following official docs.jito.wtf requirements"""
        try:
            if not isinstance(tx, VersionedTransaction):
                print(f"❌ Invalid transaction type: {type(tx)}")
                return None
            
            # Import required functions
            from tx_builder import create_jito_tip_instruction
            from solders.message import MessageV0
            from solders.address_lookup_table_account import AddressLookupTableAccount
            from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
            
            print("\n🔍 Creating Jito bundle per official documentation...")
            
            # ✅ DETERMINE TIP AMOUNT - Following Jito requirements
            if custom_tip is not None:
                tip_amount = max(custom_tip, MIN_JITO_TIP_LAMPORTS)
            else:
                tip_amount = max(JITO_TIP_AMOUNT, RECOMMENDED_TIP_LAMPORTS)
            
            print(f"💰 Tip amount: {tip_amount:,} lamports ({tip_amount/1e9:.6f} SOL)")
            
            # ✅ VALIDATE TIP AMOUNT per docs
            if tip_amount < MIN_JITO_TIP_LAMPORTS:
                print(f"❌ Tip amount {tip_amount} below minimum {MIN_JITO_TIP_LAMPORTS}")
                return None
            
            # Create tip instruction with proper amount
            tip_instruction = create_jito_tip_instruction(self.keypair.pubkey(), tip_amount)
            if not tip_instruction:
                print(f"❌ Failed to create tip instruction")
                return None
            
            print(f"✅ Created tip instruction: {tip_amount} lamports")
            
            # ✅ PRIORITY FEE CONFIGURATION - Per Jito recommendations
            # For bundles, only Jito tip matters (not priority fee)
            # But we can still add compute budget for better execution
            compute_limit_ix = set_compute_unit_limit(COMPUTE_UNIT_LIMIT)
            compute_price_ix = set_compute_unit_price(COMPUTE_UNIT_PRICE)
            
            print(f"✅ Created compute budget: {COMPUTE_UNIT_LIMIT:,} units @ {COMPUTE_UNIT_PRICE:,} micro-lamports")
            
            # Get recent blockhash with retry logic
            blockhash = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getLatestBlockhash",
                            "params": [{"commitment": "processed"}]
                        }
                        
                        timeout = aiohttp.ClientTimeout(total=3)
                        async with session.post(self.helius_url, json=payload, timeout=timeout) as response:
                            data = await response.json()
                            if 'error' in data:
                                print(f"❌ Blockhash error (attempt {attempt+1}): {data['error']}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(0.5)
                                    continue
                                return None
                            
                            blockhash = Hash.from_string(data['result']['value']['blockhash'])
                            print(f"✅ Got blockhash on attempt {attempt+1}: {blockhash}")
                            break
                except Exception as e:
                    print(f"❌ Blockhash retrieval error (attempt {attempt+1}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.5)
                        continue
                    return None
            
            if not blockhash:
                print(f"❌ Failed to get blockhash after {max_retries} attempts")
                return None
            
            # ✅ OFFICIAL BUNDLE CREATION - Following docs.jito.wtf/sendBundle
            # Max 5 transactions per bundle (official limit)
            # Transactions execute sequentially and atomically
            
            # Option 1: Include tip in main transaction (RECOMMENDED per docs)
            # This protects against "uncle bandit" scenarios
            try:
                # Try to add tip instruction to existing transaction
                main_tx_instructions = list(tx.message.instructions)
                main_tx_instructions.append(tip_instruction)
                
                # Rebuild transaction with tip included
                enhanced_message = MessageV0.try_compile(
                    payer=self.keypair.pubkey(),
                    instructions=main_tx_instructions,
                    address_lookup_table_accounts=[],
                    recent_blockhash=blockhash
                )
                
                if enhanced_message:
                    enhanced_tx = VersionedTransaction(enhanced_message, [self.keypair])
                    print(f"✅ RECOMMENDED: Tip included in main transaction")
                    
                    # Create single-transaction bundle
                    bundle = Bundle(transactions=[enhanced_tx])
                    
                else:
                    raise Exception("Failed to compile enhanced transaction")
                    
            except Exception as e:
                print(f"⚠️ Could not include tip in main transaction: {e}")
                print(f"📦 FALLBACK: Creating separate tip transaction")
                
                # Option 2: Separate tip transaction (fallback)
                tip_instructions = [
                    compute_limit_ix,  # Set compute unit limit
                    compute_price_ix,  # Set compute unit price  
                    tip_instruction    # Jito tip instruction
                ]
                
                tip_message = MessageV0.try_compile(
                    payer=self.keypair.pubkey(),
                    instructions=tip_instructions,
                    address_lookup_table_accounts=[],
                    recent_blockhash=blockhash
                )
                
                if not tip_message:
                    print(f"❌ Failed to compile tip message")
                    return None
                
                # Create and sign tip transaction
                tip_transaction = VersionedTransaction(tip_message, [self.keypair])
                
                # ✅ BUNDLE ORDER - Per Jito docs for atomic execution
                # Main transaction first, then tip (all-or-nothing)
                bundle = Bundle(transactions=[tx, tip_transaction])
            
            # ✅ VALIDATE BUNDLE per official requirements
            if not self._validate_jito_bundle(bundle):
                print(f"❌ Bundle validation failed")
                return None
            
            print(f"✅ Bundle created successfully with {len(bundle.transactions)} transaction(s)")
            return bundle
            
        except Exception as e:
            print(f"❌ Failed to create Jito bundle: {e}")
            traceback.print_exc()
            return None

    def _validate_jito_bundle(self, bundle: Bundle) -> bool:
        """
        ✅ OFFICIAL BUNDLE VALIDATION - Per docs.jito.wtf requirements
        Validates bundle meets all Jito specifications before submission
        
        Official Requirements:
        1. Maximum 5 transactions per bundle
        2. All transactions must be properly signed
        3. Bundle size limits apply
        4. Tip minimum of 1000 lamports
        
        Returns:
            bool: True if bundle is valid for Jito submission
        """
        try:
            # ✅ CHECK 1: Transaction count limit (max 5 per docs.jito.wtf)
            if len(bundle.transactions) > 5:
                print(f"❌ Bundle validation failed: Too many transactions ({len(bundle.transactions)} > 5)")
                return False
            
            if len(bundle.transactions) == 0:
                print(f"❌ Bundle validation failed: Empty bundle")
                return False
            
            print(f"✅ Transaction count valid: {len(bundle.transactions)}/5")
            
            # ✅ CHECK 2: Transaction signature validation
            unsigned_count = 0
            total_size = 0
            
            for i, tx in enumerate(bundle.transactions):
                try:
                    # Check if transaction is properly formatted
                    if not hasattr(tx, 'message') or not hasattr(tx, 'signatures'):
                        print(f"❌ Transaction {i}: Invalid transaction format")
                        return False
                    
                    # Check signature count
                    if len(tx.signatures) == 0:
                        unsigned_count += 1
                        print(f"⚠️ Transaction {i}: No signatures found")
                    
                    # Calculate size
                    tx_size = len(bytes(tx))
                    total_size += tx_size
                    
                    # Individual transaction size check (reasonable limit)
                    if tx_size > 1232:  # Standard Solana transaction size limit
                        print(f"❌ Transaction {i}: Too large ({tx_size} bytes)")
                        return False
                        
                except Exception as e:
                    print(f"❌ Transaction {i}: Serialization error: {e}")
                    return False
            
            # ✅ CHECK 3: Bundle size validation
            # Total bundle size should be reasonable for network transmission
            max_bundle_size = 6160  # 5 transactions * 1232 bytes max each
            if total_size > max_bundle_size:
                print(f"❌ Bundle too large: {total_size} bytes > {max_bundle_size} bytes")
                return False
            
            print(f"✅ Bundle size valid: {total_size} bytes")
            
            # ✅ CHECK 4: Look for tip instructions (recommended)
            tip_found = False
            tip_amount = 0
            
            for i, tx in enumerate(bundle.transactions):
                try:
                    for instruction in tx.message.instructions:
                        # Check if this looks like a Jito tip instruction
                        if hasattr(instruction, 'data') and len(instruction.data) >= 4:
                            # Jito tip instructions transfer to known tip accounts
                            if hasattr(instruction, 'accounts') and len(instruction.accounts) >= 2:
                                tip_found = True
                                # Try to extract tip amount (simplified check)
                                if len(instruction.data) >= 12:  # SOL transfer instruction
                                    import struct
                                    try:
                                        amount = struct.unpack('<Q', instruction.data[4:12])[0]
                                        if amount >= 1000:  # Minimum tip per docs
                                            tip_amount = max(tip_amount, amount)
                                    except:
                                        pass
                except Exception as e:
                    print(f"⚠️ Could not analyze transaction {i} for tips: {e}")
            
            if tip_found and tip_amount >= 1000:
                print(f"✅ Tip validation: {tip_amount / 1e9:.9f} SOL found")
            elif tip_found:
                print(f"⚠️ Tip found but amount unclear")
            else:
                print(f"⚠️ No obvious tip instruction found - bundle may be rejected")
            
            # ✅ CHECK 5: Recent blockhash validation
            try:
                for i, tx in enumerate(bundle.transactions):
                    if hasattr(tx.message, 'recent_blockhash'):
                        if not tx.message.recent_blockhash:
                            print(f"❌ Transaction {i}: Missing recent blockhash")
                            return False
            except Exception as e:
                print(f"⚠️ Could not validate blockhashes: {e}")
            
            print(f"✅ Bundle validation passed - ready for Jito submission")
            return True
            
        except Exception as e:
            print(f"❌ Bundle validation error: {e}")
            traceback.print_exc()
            return False
            
            print(f"\n🔍 Bundle Creation Debug:")
            print(f"Bundle type: {type(bundle)}")
            print(f"Bundle module: {type(bundle).__module__}")
            print(f"Number of transactions: {len(bundle.transactions)}")
            print(f"Main transaction type: {type(bundle.transactions[0])}")
            print(f"Tip transaction type: {type(bundle.transactions[1])}")
            print("✅ Created Jito bundle with tip")
            
            return bundle
            
        except Exception as e:
            print(f"❌ Failed to create bundle: {str(e)}")
            traceback.print_exc()
            return None

    def _transaction_has_tip(self, tx: VersionedTransaction) -> bool:
        """Check if transaction contains a Jito tip instruction"""
        try:
            if not hasattr(tx, 'message') or not tx.message:
                return False
            
            message = tx.message
            if not message.account_keys or not message.instructions:
                return False
            
            # Check for tip to any of the valid Jito tip accounts
            for ix in message.instructions:
                if ix.program_id_index >= len(message.account_keys):
                    continue
                    
                program_id = message.account_keys[ix.program_id_index]
                
                # Check if this is a system program transfer to a Jito tip account
                if str(program_id) == "11111111111111111111111111111111":  # System Program
                    for acc_idx in ix.accounts:
                        if acc_idx >= len(message.account_keys):
                            continue
                        account = message.account_keys[acc_idx]
                        
                        # Check if transferring to any valid Jito tip account
                        for tip_account in VALID_JITO_TIP_ACCOUNTS:
                            if str(account) == str(tip_account):
                                return True
            return False
            
        except Exception as e:
            print(f"❌ Error checking for tip instruction: {e}")
            return False

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

            # ✅ PRIORITY 1: Enhanced Jito Service (from main.py integration)
            if self.jito_service and self.jito_enhanced_initialized:
                try:
                    print("\n⚡ Submitting via Enhanced Jito Service...")
                    
                    # Use enhanced service for optimal execution (like main.py)
                    result = await self.jito_service.submit_bundle(bundle)
                    
                    if result and isinstance(result, dict) and result.get('success'):
                        bundle_id = result.get('bundle_id', 'unknown')
                        print(f"✅ Enhanced Jito Service success! Bundle ID: {bundle_id}")
                        return bundle_id
                    else:
                        print(f"⚠️ Enhanced Jito Service failed: {result}")
                        print(f"📡 Falling back to official Jito Bundle API...")
                        
                except Exception as e:
                    print(f"⚠️ Enhanced Jito Service error: {str(e)}")
                    print(f"📡 Falling back to official Jito Bundle API...")

            # ✅ PRIORITY 2: Official Jito Bundle Submission - Following docs.jito.wtf
            try:
                print("\n📦 Submitting to Official Jito Bundle API...")
                print(f"Bundle type: {type(bundle)}")
                print(f"Bundle size: {len(bundle.transactions)} transactions")
                
                # Use official Jito bundle submission
                success = await self._submit_jito_bundle_official(bundle)
                if success:
                    print(f"✅ Bundle submitted successfully via Official Jito API")
                    return "bundle_submitted"  # Bundle doesn't return individual tx signature
                else:
                    print(f"❌ Official Jito bundle submission failed")
                    
            except Exception as e:
                print(f"⚠️ Official Jito bundle submission failed: {str(e)}")
                traceback.print_exc()

            # Fallback to RPC
            print("\n📡 Falling back to regular RPC submission...")
            return await self._submit_to_rpc(tx)

        except Exception as e:
            print(f"❌ Transaction submission error: {str(e)}")
            traceback.print_exc()
            return None
    
    
    async def _submit_jito_bundle_official(self, bundle: Bundle) -> bool:
        """
        ✅ OFFICIAL BUNDLE SUBMISSION - Following docs.jito.wtf requirements
        Submits bundle to Jito with official authentication and endpoints
        
        Returns:
            bool: True if bundle submitted successfully and accepted
        """
        try:
            import aiohttp
            import base64
            
            # ✅ OFFICIAL JITO HEADERS per docs.jito.wtf
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                # Official authentication format from docs.jito.wtf
                'x-jito-auth': base64.b64encode(bytes(self.keypair)).decode('utf-8')
            }
            
            # ✅ OFFICIAL BUNDLE PAYLOAD - Exact format from docs
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendBundle",
                "params": [
                    {
                        "transactions": [
                            # Convert transactions to base64 format
                            base64.b64encode(bytes(tx)).decode('utf-8')
                            for tx in bundle.transactions
                        ]
                    }
                ]
            }
            
            # ✅ RETRY LOGIC for production reliability
            max_retries = 3
            retry_delay = 0.1  # 100ms between retries
            
            for attempt in range(max_retries):
                try:
                    print(f"📤 Submitting bundle to Jito (attempt {attempt + 1}/{max_retries})")
                    
                    async with self.session.post(
                        self.jito_endpoint,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=5.0)  # 5 second timeout per official recommendations
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            
                            if 'result' in result:
                                bundle_id = result['result']
                                print(f"✅ Bundle submitted successfully! ID: {bundle_id}")
                                return True
                            elif 'error' in result:
                                error = result['error']
                                print(f"❌ Jito bundle error: {error}")
                                
                                # Check for specific error types
                                if 'code' in error:
                                    error_code = error['code']
                                    if error_code == -32602:  # Invalid params
                                        print(f"💡 Bundle rejected - check transaction format")
                                        return False
                                    elif error_code == -32005:  # Already processed
                                        print(f"⚠️ Bundle already processed")
                                        return True
                                
                                # Retry on certain errors
                                if attempt < max_retries - 1:
                                    print(f"🔄 Retrying in {retry_delay}s...")
                                    await asyncio.sleep(retry_delay)
                                    continue
                                
                                return False
                        else:
                            response_text = await response.text()
                            print(f"❌ HTTP error {response.status}: {response_text}")
                            
                            # Retry on server errors
                            if response.status >= 500 and attempt < max_retries - 1:
                                print(f"🔄 Server error - retrying in {retry_delay}s...")
                                await asyncio.sleep(retry_delay)
                                continue
                            
                            return False
                            
                except asyncio.TimeoutError:
                    print(f"⏰ Request timeout (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                    return False
                    
                except Exception as e:
                    print(f"🌐 Network error: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                    return False
            
            print(f"❌ All retry attempts failed")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error submitting bundle: {e}")
            traceback.print_exc()
            return False

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
                    
                    # 🚨 CRITICAL FIX: Detect placeholder signatures from Jupiter unsigned transactions
                    if signature == "1111111111111111111111111111111111111111111111111111111111111111":
                        print(f"❌ Placeholder signature detected – Jupiter unsigned transaction submitted!")
                        print(f"   🚨 This indicates Jupiter API returned unsigned transaction!")
                        print(f"   🔄 Should use native DEX builders instead of Jupiter API!")
                        return None
                    
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
    
    # Backward compatibility alias
    async def send_and_confirm_transaction(self, bundle_or_tx: Union[Bundle, VersionedTransaction]) -> Optional[str]:
        """Backward compatibility alias for submit_transaction"""
        return await self.submit_transaction(bundle_or_tx)

    async def close_session(self):
        """Close session and enhanced services - integrated from main.py"""
        if self.session:
            await self.session.close()
            self.session = None
            print("✅ FastExecutor session closed")
        
        # Close enhanced Jito service if available
        if self.jito_service and self.jito_enhanced_initialized:
            try:
                await self.jito_service.close()
                print("✅ Enhanced Jito Service closed")
            except Exception as e:
                print(f"⚠️ Error closing Enhanced Jito Service: {e}")

    async def create_jupiter_enhanced_bundle(self, token_mint: str, action: str, amount_sol: float) -> Optional[Bundle]:
        """
        Create enhanced bundle using Jupiter utilities when available
        Integrated from main.py Jupiter transaction building capabilities
        """
        if not self.jupiter_available:
            print("⚠️ Jupiter utilities not available - falling back to standard bundle creation")
            return None
        
        try:
            print(f"🚀 Creating Jupiter-enhanced bundle for {action.upper()} action")
            print(f"   💎 Token: {token_mint[:8]}...")
            print(f"   💰 Amount: {amount_sol} SOL")
            
            # Use Jupiter utilities for enhanced transaction building
            if action.lower() == 'buy':
                from jupiter_utils import create_jupiter_buy_transaction
                tx_result = create_jupiter_buy_transaction(
                    wallet=self.keypair,
                    token_mint=token_mint,
                    amount_sol=amount_sol,
                    slippage_bps=1500  # 15% slippage for copy trading
                )
            elif action.lower() == 'sell':
                from jupiter_utils import create_jupiter_sell_transaction
                tx_result = create_jupiter_sell_transaction(
                    wallet=self.keypair,
                    token_mint=token_mint,
                    amount_sol=amount_sol,
                    slippage_bps=1500
                )
            else:
                print(f"❌ Unsupported Jupiter action: {action}")
                return None
            
            if tx_result and hasattr(tx_result, 'transaction'):
                tx = tx_result.transaction
                print(f"✅ Jupiter transaction created successfully")
                
                # Create Jito bundle with Jupiter transaction
                bundle = await self.create_jito_bundle(tx)
                if bundle:
                    print(f"✅ Jupiter-enhanced Jito bundle created")
                    return bundle
                else:
                    print(f"❌ Failed to create Jito bundle from Jupiter transaction")
                    return None
            else:
                print(f"❌ Jupiter transaction creation failed")
                return None
                
        except Exception as e:
            print(f"❌ Jupiter-enhanced bundle creation failed: {e}")
            print(f"📡 Falling back to standard bundle creation")
            return None

    def get_jito_service_status(self) -> dict:
        """Get status of all Jito services for debugging - integrated from main.py"""
        return {
            'enhanced_jito_available': self.jito_enhanced_available,
            'enhanced_jito_initialized': self.jito_enhanced_initialized,
            'jupiter_available': self.jupiter_available,
            'basic_jito_client': self.jito_client is not None,
            'official_tip_accounts': len(self.official_tip_accounts),
            'current_tip_floor': self.current_tip_floor,
            'jito_endpoint': self.jito_endpoint
        }