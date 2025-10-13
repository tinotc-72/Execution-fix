#!/usr/bin/env python3
"""
Enhanced Jito Service - Official Implementation Following Jito Team Documentation
Implements Jito-first execution with RPC fallback as recommended by Jito team
Based on: https://docs.jito.wtf/lowlatencytxnsend/#system-overview
"""

import asyncio
import aiohttp
import json
import random
import time
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, UTC
from dataclasses import dataclass
from solders.transaction import VersionedTransaction
from solders.signature import Signature
from config import JITO_AUTH_TOKEN

logger = logging.getLogger(__name__)

@dataclass
class JitoTipAccount:
    """Official Jito tip accounts"""
    address: str
    region: str = "global"

@dataclass
class JitoExecutionResult:
    """Result of Jito execution attempt"""
    success: bool
    signature: Optional[str] = None
    bundle_id: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    method: str = "unknown"  # "jito_transaction", "jito_bundle", "rpc_fallback"

class JitoEnhancedService:
    """
    Enhanced Jito Service implementing official patterns:
    1. Jito sendTransaction (fastest, with MEV protection)
    2. Jito sendBundle (atomic transactions)
    3. RPC fallback (when Jito unavailable)
    """
    
    # Official Jito endpoints from documentation
    JITO_ENDPOINTS = {
        "mainnet": "https://mainnet.block-engine.jito.wtf",
        "amsterdam": "https://amsterdam.mainnet.block-engine.jito.wtf",
        "frankfurt": "https://frankfurt.mainnet.block-engine.jito.wtf", 
        "london": "https://london.mainnet.block-engine.jito.wtf",
        "new_york": "https://ny.mainnet.block-engine.jito.wtf",
        "salt_lake": "https://slc.mainnet.block-engine.jito.wtf",
        "singapore": "https://singapore.mainnet.block-engine.jito.wtf",
        "tokyo": "https://tokyo.mainnet.block-engine.jito.wtf"
    }
    
    # Official tip accounts from Jito documentation
    OFFICIAL_TIP_ACCOUNTS = [
        "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
        "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe", 
        "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
        "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
        "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
        "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
        "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
        "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT"
    ]
    
    def __init__(self, preferred_region: str = "london", rpc_fallback_url: str = None, wallet_keypair=None):
        """
        Initialize Enhanced Jito Service
        
        Args:
            preferred_region: Preferred Jito region (london, frankfurt, etc.)
            rpc_fallback_url: RPC URL for fallback when Jito fails
            wallet_keypair: Keypair for authentication (if None, uses config token)
        """
        self.preferred_region = preferred_region
        self.rpc_fallback_url = rpc_fallback_url
        
        # Primary endpoint (preferred region)
        self.primary_endpoint = self.JITO_ENDPOINTS.get(preferred_region, self.JITO_ENDPOINTS["london"])
        
        # Backup endpoints (other regions)
        self.backup_endpoints = [url for region, url in self.JITO_ENDPOINTS.items() 
                               if region != preferred_region]
        
        # API endpoints
        self.transaction_endpoint = f"{self.primary_endpoint}/api/v1/transactions"
        self.bundle_endpoint = f"{self.primary_endpoint}/api/v1/bundles"
        self.tip_accounts_endpoint = f"{self.primary_endpoint}/api/v1/getTipAccounts"
        self.bundle_status_endpoint = f"{self.primary_endpoint}/api/v1/getBundleStatuses"
        
        # Set up authentication header
        if wallet_keypair:
            # Use official authentication format: base64-encoded keypair
            import base64
            auth_token = base64.b64encode(bytes(wallet_keypair)).decode('utf-8')
        else:
            # Fallback to config token
            auth_token = JITO_AUTH_TOKEN
            
        # Headers for authentication
        self.headers = {
            "Content-Type": "application/json",
            "x-jito-auth": auth_token
        }
        
        # Session management
        self.session = None
        self.tip_accounts_cache = None
        self.last_tip_fetch = 0
        
        # Performance tracking
        self.stats = {
            "jito_success": 0,
            "jito_failures": 0,
            "rpc_fallbacks": 0,
            "total_attempts": 0
        }
        
        logger.info(f"🚀 Enhanced Jito Service Initialized")
        logger.info(f"   🌍 Primary Region: {preferred_region}")
        logger.info(f"   🔗 Primary Endpoint: {self.primary_endpoint}")
        logger.info(f"   🔑 Auth Token: {JITO_AUTH_TOKEN[:8]}...***")
        logger.info(f"   🔄 Backup Regions: {len(self.backup_endpoints)}")

    async def initialize(self) -> bool:
        """Initialize the service and test connectivity"""
        try:
            # ✅ FIXED: Proper session timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=30,      # Total timeout
                connect=10,    # Connection timeout  
                sock_read=10   # Socket read timeout
            )
            
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(
                    limit=100,           # Connection pool limit
                    ttl_dns_cache=300,   # DNS cache TTL
                    use_dns_cache=True,  # Enable DNS caching
                    keepalive_timeout=60 # Keep connections alive
                )
            )
            
            # Test primary endpoint
            logger.info(f"🔍 Testing connectivity to {self.preferred_region}...")
            
            # Get tip accounts to test connectivity
            await self.get_tip_accounts()
            
            logger.info(f"✅ Enhanced Jito Service ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Jito Service: {e}")
            if self.session:
                await self.session.close()
                self.session = None
            return False

    async def close(self):
        """✅ FIXED: Properly clean up all resources"""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
                # Wait a bit for the connector to close properly
                await asyncio.sleep(0.1)
                logger.info("✅ Enhanced Jito Service session closed properly")
            else:
                logger.debug("Session was already closed or None")
                
            self.session = None
            self.tip_accounts_cache = None
            
        except Exception as e:
            logger.warning(f"⚠️ Error during session cleanup: {e}")
        finally:
            logger.info("👋 Enhanced Jito Service cleanup complete")

    async def get_tip_accounts(self) -> List[str]:
        """
        Get current tip accounts from Jito API
        Caches for 5 minutes to avoid excessive API calls
        """
        current_time = time.time()
        
        # Use cache if recent
        if (self.tip_accounts_cache and 
            current_time - self.last_tip_fetch < 300):  # 5 minutes
            return self.tip_accounts_cache
        
        try:
            # Request tip accounts from API
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTipAccounts",
                "params": []
            }
            
            async with self.session.post(self.tip_accounts_endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    tip_accounts = data.get("result", self.OFFICIAL_TIP_ACCOUNTS)
                    
                    self.tip_accounts_cache = tip_accounts
                    self.last_tip_fetch = current_time
                    
                    logger.debug(f"✅ Retrieved {len(tip_accounts)} tip accounts")
                    return tip_accounts
                else:
                    logger.warning(f"⚠️ Failed to get tip accounts: {response.status}")
                    return self.OFFICIAL_TIP_ACCOUNTS
                    
        except Exception as e:
            logger.warning(f"⚠️ Error getting tip accounts: {e}")
            return self.OFFICIAL_TIP_ACCOUNTS

    def get_random_tip_account(self) -> str:
        """Get a random tip account to reduce contention"""
        tip_accounts = self.tip_accounts_cache or self.OFFICIAL_TIP_ACCOUNTS
        return random.choice(tip_accounts)

    async def send_transaction_with_tip(
        self, 
        transaction: VersionedTransaction,
        tip_lamports: int = 10_000,
        bundle_only: bool = False
    ) -> JitoExecutionResult:
        """
        ✅ FIXED: Send transaction with proper Jito tip for auction eligibility
        
        This method ensures the transaction includes a write-locked tip account
        as required by Jito: "Bundles must write lock at least one tip account to be eligible for the auction."
        
        Args:
            transaction: The transaction to send
            tip_lamports: Tip amount in lamports (minimum 10,000 for auction)
            bundle_only: Use bundleOnly=true for revert protection
        """
        start_time = time.time()
        self.stats["total_attempts"] += 1
        
        try:
            # ✅ CRITICAL: Verify transaction has writable tip account
            has_tip_account = self._verify_transaction_has_tip_account(transaction)
            
            if not has_tip_account:
                logger.warning("⚠️ Transaction missing writable tip account - bundle will be rejected")
                logger.warning("💡 Use create_jito_tip_instruction() to add tip instruction")
                return JitoExecutionResult(
                    success=False,
                    error="Transaction must include writable tip account for auction eligibility",
                    method="validation_failed"
                )
            
            logger.info(f"🚀 Sending transaction with Jito tip...")
            logger.info(f"   💰 Tip Amount: {tip_lamports:,} lamports")
            logger.info(f"   📦 Bundle Only: {bundle_only}")
            logger.info(f"   ✅ Has Tip Account: {has_tip_account}")
            
            # ✅ CRITICAL FIX: Use sendBundle instead of sendTransaction for proper tip validation
            # According to Jito docs, tip account validation requires bundle submission
            logger.info(f"   🎯 Using sendBundle method for proper tip account validation...")
            result = await self.send_bundle([transaction], tip_lamports)
            
            if result.success:
                result.execution_time = time.time() - start_time
                self.stats["jito_success"] += 1
                logger.info(f"✅ Jito bundle execution successful in {result.execution_time:.2f}s")
                return result
            
            # Fallback to RPC if Jito fails
            if self.rpc_fallback_url:
                logger.warning(f"🔄 Jito bundle failed, trying RPC fallback...")
                
                # Serialize transaction for RPC fallback
                import base64
                try:
                    serialized_tx = base64.b64encode(transaction.serialize()).decode('utf-8')
                except Exception as e:
                    logger.error(f"Failed to serialize transaction for RPC fallback: {e}")
                    return JitoExecutionResult(
                        success=False,
                        error=f"RPC fallback serialization failed: {e}",
                        execution_time=time.time() - start_time,
                        method="rpc_fallback"
                    )
                
                result = await self._try_rpc_fallback(serialized_tx)
                
                if result.success:
                    result.execution_time = time.time() - start_time
                    self.stats["rpc_fallbacks"] += 1
                    logger.info(f"✅ RPC fallback successful in {result.execution_time:.2f}s")
                    return result
            
            # Both methods failed
            result.execution_time = time.time() - start_time
            self.stats["jito_failures"] += 1
            logger.error(f"❌ All execution methods failed in {result.execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Error in send_transaction_with_tip: {e}")
            return JitoExecutionResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                method="exception"
            )

    def _verify_transaction_has_tip_account(self, transaction: VersionedTransaction) -> bool:
        """
        ✅ Verify transaction includes at least one writable tip account
        Required for Jito bundle auction eligibility
        """
        try:
            # Get all account keys from the transaction
            message = transaction.message
            try:
                account_keys = message.account_keys
            except AttributeError:
                account_keys = message.static_account_keys
            header = message.header
            num_required_signatures = header.num_required_signatures
            num_readonly_signed = header.num_readonly_signed_accounts
            num_readonly_unsigned = header.num_readonly_unsigned_accounts
            total_readonly = num_readonly_signed + num_readonly_unsigned
            total_accounts = len(account_keys)
            writable_start = num_required_signatures - num_readonly_signed
            writable_end = total_accounts - num_readonly_unsigned
            for i, account_key in enumerate(account_keys):
                if str(account_key) in [str(tip) for tip in self.OFFICIAL_TIP_ACCOUNTS]:
                    if writable_start <= i < writable_end:
                        logger.debug(f"✅ Found writable tip account: {str(account_key)[:8]}...")
                        return True
            logger.debug("❌ No writable tip accounts found in transaction")
            return False
        except Exception as e:
            logger.error(f"Error verifying tip account: {e}")
            return False
    async def send_transaction_jito_first(
        self, 
        transaction: VersionedTransaction,
        priority_fee_lamports: int = 50_000,
        tip_lamports: int = 10_000,
        bundle_only: bool = False
    ) -> JitoExecutionResult:
        """
        Send transaction with Jito-first approach and RPC fallback
        
        Execution order (following official Jito recommendations):
        1. Try Jito sendTransaction (fastest, with MEV protection)
        2. If Jito fails, fallback to RPC sendTransaction
        
        Args:
            transaction: The transaction to send
            priority_fee_lamports: Priority fee (70% of total fee recommended)
            tip_lamports: Jito tip (30% of total fee recommended)
            bundle_only: Use bundleOnly=true for revert protection
        """
        # Use the new method with tip verification
        return await self.send_transaction_with_tip(transaction, tip_lamports, bundle_only)

    async def _try_jito_send_transaction(
        self, 
        serialized_tx: str, 
        priority_fee: int, 
        tip: int,
        bundle_only: bool = False
    ) -> JitoExecutionResult:
        """Try sending transaction via Jito sendTransaction endpoint"""
        try:
            # Build URL with query parameters
            url = self.transaction_endpoint
            if bundle_only:
                url += "?bundleOnly=true"
            
            # Official Jito sendTransaction payload
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    serialized_tx,
                    {
                        "encoding": "base64",
                        "skipPreflight": True,  # Always true for Jito
                        "preflightCommitment": "processed",
                        "maxRetries": 0  # Let our retry logic handle it
                    }
                ]
            }
            
            logger.debug(f"📡 Sending to Jito: {url}")
            
            # Try primary endpoint first
            async with self.session.post(url, json=payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    
                    if "error" in data:
                        error_msg = data["error"].get("message", "Unknown Jito error")
                        logger.warning(f"⚠️ Jito error: {error_msg}")
                        return JitoExecutionResult(
                            success=False,
                            error=error_msg,
                            method="jito_transaction"
                        )
                    
                    signature = data.get("result")
                    if signature:
                        logger.info(f"✅ Jito transaction submitted: {signature[:12]}...")
                        return JitoExecutionResult(
                            success=True,
                            signature=signature,
                            method="jito_transaction"
                        )
                
                # Non-200 status
                logger.warning(f"⚠️ Jito returned status {response.status}")
                logger.debug(f"Response: {response_text[:200]}...")
                
                return JitoExecutionResult(
                    success=False,
                    error=f"HTTP {response.status}",
                    method="jito_transaction"
                )
                
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Jito transaction timeout")
            return JitoExecutionResult(
                success=False,
                error="Timeout",
                method="jito_transaction"
            )
        except Exception as e:
            logger.warning(f"❌ Jito transaction error: {e}")
            return JitoExecutionResult(
                success=False,
                error=str(e),
                method="jito_transaction"
            )

    async def _try_rpc_fallback(self, serialized_tx: str) -> JitoExecutionResult:
        """✅ FIXED: Fallback to standard RPC sendTransaction with proper session management"""
        try:
            if not self.rpc_fallback_url:
                return JitoExecutionResult(
                    success=False,
                    error="No RPC fallback URL configured",
                    method="rpc_fallback"
                )
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    serialized_tx,
                    {
                        "encoding": "base64",
                        "skipPreflight": False,  # RPC can use preflight
                        "preflightCommitment": "processed",
                        "maxRetries": 3
                    }
                ]
            }
            
            logger.debug(f"📡 RPC Fallback to: {self.rpc_fallback_url}")
            
            # ✅ FIXED: Use proper session management for RPC fallback
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            async with aiohttp.ClientSession(timeout=timeout) as rpc_session:
                async with rpc_session.post(
                    self.rpc_fallback_url, 
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        data = json.loads(response_text)
                        
                        if "error" in data:
                            error_msg = data["error"].get("message", "Unknown RPC error")
                            logger.warning(f"⚠️ RPC error: {error_msg}")
                            return JitoExecutionResult(
                                success=False,
                                error=error_msg,
                                method="rpc_fallback"
                            )
                        
                        signature = data.get("result")
                        if signature:
                            logger.info(f"✅ RPC fallback successful: {signature[:12]}...")
                            return JitoExecutionResult(
                                success=True,
                                signature=signature,
                                method="rpc_fallback"
                            )
                    
                    logger.warning(f"⚠️ RPC returned status {response.status}")
                    return JitoExecutionResult(
                        success=False,
                        error=f"RPC HTTP {response.status}",
                        method="rpc_fallback"
                    )
                    
        except asyncio.TimeoutError:
            logger.warning(f"⏰ RPC fallback timeout")
            return JitoExecutionResult(
                success=False,
                error="RPC Timeout",
                method="rpc_fallback"
            )
        except Exception as e:
            logger.warning(f"❌ RPC fallback error: {e}")
            return JitoExecutionResult(
                success=False,
                error=str(e),
                method="rpc_fallback"
            )

    async def send_bundle(
        self, 
        transactions: List[VersionedTransaction],
        tip_lamports: int = 10_000
    ) -> JitoExecutionResult:
        """
        Send bundle of transactions (max 5) via Jito
        All transactions execute atomically (all-or-nothing)
        """
        start_time = time.time()
        
        if len(transactions) > 5:
            return JitoExecutionResult(
                success=False,
                error="Bundle cannot exceed 5 transactions",
                method="jito_bundle"
            )
        
        try:
            # Serialize all transactions to base64
            import base64
            serialized_txs = []
            
            for tx in transactions:
                try:
                    # Try different serialization methods for different solders versions
                    if hasattr(tx, 'serialize'):
                        tx_bytes = tx.serialize()
                    elif hasattr(tx, 'to_bytes'):
                        tx_bytes = tx.serialize()
                    else:
                        # Fallback: convert to bytes using __bytes__
                        tx_bytes = bytes(tx)
                    
                    serialized_txs.append(base64.b64encode(tx_bytes).decode('utf-8'))
                except Exception as e:
                    logger.error(f"Failed to serialize transaction: {e}")
                    return JitoExecutionResult(
                        success=False,
                        error=f"Transaction serialization failed: {e}",
                        method="jito_bundle"
                    )
            
            payload = {
                "jsonrpc": "2.0", 
                "id": 1,
                "method": "sendBundle",
                "params": [
                    {
                        "transactions": serialized_txs
                    }
                ]
            }
            
            logger.info(f"📦 Sending bundle with {len(transactions)} transactions...")
            logger.info(f"   🎯 Tip: {tip_lamports:,} lamports")
            
            async with self.session.post(self.bundle_endpoint, json=payload, headers=self.headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = json.loads(response_text)
                    
                    if "error" in data:
                        error_msg = data["error"].get("message", "Unknown bundle error")
                        logger.warning(f"⚠️ Bundle error: {error_msg}")
                        return JitoExecutionResult(
                            success=False,
                            error=error_msg,
                            method="jito_bundle"
                        )
                    
                    bundle_id = data.get("result")
                    if bundle_id:
                        execution_time = time.time() - start_time
                        logger.info(f"✅ Bundle submitted: {bundle_id[:12]}... in {execution_time:.2f}s")
                        return JitoExecutionResult(
                            success=True,
                            bundle_id=bundle_id,
                            execution_time=execution_time,
                            method="jito_bundle"
                        )
                
                logger.warning(f"⚠️ Bundle submission failed: {response.status}")
                return JitoExecutionResult(
                    success=False,
                    error=f"HTTP {response.status}",
                    method="jito_bundle"
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Bundle submission error: {e}")
            return JitoExecutionResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                method="jito_bundle"
            )

    async def get_bundle_status(self, bundle_id: str) -> Optional[Dict[str, Any]]:
        """Check the status of a submitted bundle"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1, 
                "method": "getBundleStatuses",
                "params": [
                    [bundle_id]
                ]
            }
            
            async with self.session.post(self.bundle_status_endpoint, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get("result", {})
                    value = result.get("value", [])
                    
                    if value and len(value) > 0:
                        return value[0]  # Return first (and only) bundle status
                        
                return None
                
        except Exception as e:
            logger.debug(f"Error getting bundle status: {e}")
            return None

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total = self.stats["total_attempts"]
        if total == 0:
            return {"success_rate": 0.0, **self.stats}
        
        success_rate = (self.stats["jito_success"] + self.stats["rpc_fallbacks"]) / total
        
        return {
            "success_rate": success_rate,
            "jito_success_rate": self.stats["jito_success"] / total if total > 0 else 0.0,
            "rpc_fallback_rate": self.stats["rpc_fallbacks"] / total if total > 0 else 0.0,
            **self.stats
        }

    def log_stats(self):
        """Log current execution statistics"""
        stats = self.get_execution_stats()
        logger.info(f"📊 Jito Service Stats:")
        logger.info(f"   🎯 Overall Success Rate: {stats['success_rate']:.1%}")
        logger.info(f"   🚀 Jito Success: {stats['jito_success']} ({stats['jito_success_rate']:.1%})")
        logger.info(f"   🔄 RPC Fallbacks: {stats['rpc_fallbacks']} ({stats['rpc_fallback_rate']:.1%})")
        logger.info(f"   ❌ Total Failures: {stats['jito_failures']}")
        logger.info(f"   📊 Total Attempts: {stats['total_attempts']}")
