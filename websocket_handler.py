#!/usr/bin/env python3
"""
WebSocket Handler - Dedicated WebSocket monitoring for copy trading
Extracted from main.py for better modularity and reliability
Combines the simplicity of listener.py with the advanced features needed for main.py
"""

import asyncio
import json
import logging
import time
import traceback
import websockets
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass

# Setup logging
logger = logging.getLogger(__name__)


async def backfill_latest_tx(helius_rpc_url: str, wallet_str: str, limit: int = 1) -> Optional[Dict[str, Any]]:
    """
    🔁 Backfill helper: Fetch the latest transaction signature and full transaction data
    
    This helper is used when an account/logs event doesn't include a signature.
    It fetches the latest signature via getSignaturesForAddress and loads the full 
    transaction via getTransaction (jsonParsed, max_supported_transaction_version=0).
    
    Args:
        helius_rpc_url: The Helius RPC URL to use for fetching data
        wallet_str: The wallet address to fetch transactions for
        limit: Number of signatures to fetch (default: 1)
    
    Returns:
        Dict containing signature, logs, and transaction, or None if fetch fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Get latest signature(s) via getSignaturesForAddress
            sig_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [wallet_str, {"limit": limit}]
            }
            
            async with session.post(helius_rpc_url, json=sig_payload, timeout=aiohttp.ClientTimeout(total=10)) as sig_response:
                sig_data = await sig_response.json()
                sigs = sig_data.get("result") or []
            
            if not sigs:
                logger.warning(f"🧵 [BACKFILL] No signatures found for wallet {wallet_str[:8]}...")
                return None
            
            sig = sigs[0].get("signature")
            if not sig:
                logger.warning(f"🧵 [BACKFILL] No signature in result for wallet {wallet_str[:8]}...")
                return None
            
            # Step 2: Get full transaction via getTransaction
            tx_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    sig,
                    {
                        "encoding": "jsonParsed",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            async with session.post(helius_rpc_url, json=tx_payload, timeout=aiohttp.ClientTimeout(total=10)) as tx_response:
                tx_data = await tx_response.json()
                tx = tx_data.get("result")
            
            if not tx:
                logger.warning(f"🧵 [BACKFILL] No transaction data for signature {sig[:8]}...")
                return None
            
            meta = tx.get("meta") or {}
            logs = meta.get("logMessages") or []
            transaction = tx.get("transaction")
            
            return {
                "signature": sig,
                "logs": logs,
                "transaction": transaction,
                "meta": meta
            }
    
    except Exception as e:
        logger.warning(f"🧵 [BACKFILL] Failed to backfill latest tx: {e}")
        return None


@dataclass
class WebSocketConfig:
    """Configuration for WebSocket monitoring"""
    target_wallets: List[str]
    helius_ws_url: str
    helius_rpc_url: str
    max_retries: int = 10
    reconnect_delay: float = 2.0
    max_reconnect_delay: float = 30.0
    subscription_timeout: float = 10.0
    message_timeout: float = 5.0

class WebSocketHandler:
    """
    🚀 PRODUCTION WebSocket Handler - Reliable, fast, and modular
    Handles all WebSocket connections and delegates trade processing to callbacks
    """
    
    def __init__(self, config: WebSocketConfig, trade_callback: Callable):
        """
        Initialize WebSocket handler
        
        Args:
            config: WebSocket configuration
            trade_callback: Async function to call when trades are detected
                           Should accept: (trade_info: Dict[str, Any]) -> None
        """
        self.config = config
        self.trade_callback = trade_callback
        self.is_running = False
        self.websocket = None
        self.subscriptions = {}  # Track subscription IDs
        self.processed_signatures: Set[str] = set()
        self.connection_start_time = None
        self.messages_received = 0
        self.trades_detected = 0
        
        logger.info(f"🚀 WebSocket Handler initialized")
        logger.info(f"   🎯 Target wallets: {len(self.config.target_wallets)}")
        logger.info(f"   📡 WebSocket URL: {self.config.helius_ws_url[:50]}...")
        
    async def start_monitoring(self):
        """🚀 Start WebSocket monitoring with auto-reconnection"""
        logger.info("📡 Starting WebSocket monitoring...")
        self.is_running = True
        retry_count = 0
        
        while self.is_running and retry_count < self.config.max_retries:
            try:
                logger.info(f"📡 WebSocket connection attempt {retry_count + 1}/{self.config.max_retries}")
                
                # Connect to WebSocket
                await self._connect_and_monitor()
                
                # If we get here, connection was lost
                logger.warning("⚠️ WebSocket connection lost")
                retry_count += 1
                
                if retry_count < self.config.max_retries and self.is_running:
                    # Calculate backoff delay
                    delay = min(
                        self.config.reconnect_delay * (retry_count ** 0.5),  # Square root backoff
                        self.config.max_reconnect_delay
                    )
                    
                    logger.info(f"🔄 Reconnecting in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
                
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ WebSocket error (attempt {retry_count}): {e}")
                
                if retry_count < self.config.max_retries and self.is_running:
                    delay = min(
                        self.config.reconnect_delay * retry_count,
                        self.config.max_reconnect_delay
                    )
                    logger.info(f"🔄 Retrying in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("❌ Max WebSocket retries reached")
                    self.is_running = False
                    break
        
        logger.info("📡 WebSocket monitoring stopped")
    
    async def _connect_and_monitor(self):
        """🔗 Establish WebSocket connection and monitor"""
        try:
            logger.info(f"🔗 Connecting to WebSocket...")
            self.connection_start_time = time.time()
            
            async with websockets.connect(
                self.config.helius_ws_url,
                ping_interval=20,  # Ping every 20 seconds
                ping_timeout=10,   # Wait 10 seconds for pong
                close_timeout=10   # Wait 10 seconds for close
            ) as websocket:
                self.websocket = websocket
                logger.info("✅ WebSocket connected successfully")
                
                # Subscribe to wallet activities
                await self._setup_subscriptions()
                
                # Start monitoring messages
                await self._monitor_messages()
                
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"🔌 WebSocket connection closed: {e}")
        except Exception as e:
            logger.error(f"❌ WebSocket connection error: {e}")
            raise
        finally:
            self.websocket = None
    
    async def _setup_subscriptions(self):
        """📡 Setup subscriptions for all target wallets and enhanced transaction stream"""
        logger.info(f"📡 Setting up subscriptions for {len(self.config.target_wallets)} wallets...")
        successful_subscriptions = 0
        # Subscribe to logs/account for each wallet
        for i, wallet in enumerate(self.config.target_wallets):
            try:
                logger.info(f"📡 [{i+1}/{len(self.config.target_wallets)}] Processing wallet: {wallet[:8]}...")
                await self._subscribe_to_wallet(wallet, i)
                successful_subscriptions += 1
                if i < len(self.config.target_wallets) - 1:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"❌ [{i+1}] Failed to subscribe to {wallet[:8]}...: {e}")
                continue
        logger.info(f"✅ Subscriptions setup: {successful_subscriptions}/{len(self.config.target_wallets)} successful")
        # --- Helius Enhanced Transaction Stream ---
        try:
            logger.info("📡 Subscribing to Helius enhanced transaction stream (transactionSubscribe)...")
            enhanced_subscription = {
                "jsonrpc": "2.0",
                "id": f"enhanced_tx_{int(time.time())}",
                "method": "transactionSubscribe",
                "params": [
                    {
                        "mentions": self.config.target_wallets,
                        "commitment": "confirmed"
                    },
                    {
                        "encoding": "json"
                    }
                ]
            }
            await self.websocket.send(json.dumps(enhanced_subscription))
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            sub_response = json.loads(response)
            if 'result' in sub_response:
                sub_id = sub_response['result']
                self.subscriptions["enhanced_transaction"] = sub_id
                logger.info(f"✅ Enhanced transaction stream subscription successful: {sub_id}")
            else:
                logger.warning(f"⚠️ Enhanced transaction stream subscription failed: {sub_response}")
        except Exception as e:
            logger.warning(f"⚠️ Enhanced transaction stream unavailable: {e} — continuing with logs/account + backfill")
    
    async def _subscribe_to_wallet(self, wallet: str, index: int):
        """📡 ENHANCED: Subscribe to ALL wallet activities for comprehensive copying - SEQUENTIAL VERSION"""
        try:
            logger.info(f"📡 [{index+1}] Subscribing to ALL activities for: {wallet[:8]}...")
            
            # 🚀 SUBSCRIPTION 1: Logs (primary method - most reliable)
            logs_subscription = {
                "jsonrpc": "2.0",
                "id": f"logs_{index}_{int(time.time())}",  # Unique ID with timestamp
                "method": "logsSubscribe",
                "params": [
                    {"mentions": [wallet]},
                    {"commitment": "confirmed"}  # Use confirmed for speed vs finalized for reliability
                ]
            }
            
            await self.websocket.send(json.dumps(logs_subscription))
            
            # Wait for subscription confirmation - SEQUENTIAL
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            sub_response = json.loads(response)
            if 'result' in sub_response:
                sub_id = sub_response['result']
                self.subscriptions[f"logs_{wallet}"] = sub_id
                logger.info(f"✅ [{index+1}] Logs subscription successful: {sub_id}")
            else:
                logger.error(f"❌ [{index+1}] Logs subscription failed: {sub_response}")
                return  # Don't proceed if logs subscription fails
            
            # Small delay between subscription types
            await asyncio.sleep(0.05)
            
            # 🚀 SUBSCRIPTION 2: Account changes (balance monitoring)
            account_subscription = {
                "jsonrpc": "2.0",
                "id": f"account_{index}_{int(time.time())}",  # Unique ID with timestamp
                "method": "accountSubscribe",
                "params": [
                    wallet,
                    {"commitment": "confirmed", "encoding": "base64"}
                ]
            }
            
            await self.websocket.send(json.dumps(account_subscription))
            
            # Wait for confirmation - SEQUENTIAL
            response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            sub_response = json.loads(response)
            if 'result' in sub_response:
                sub_id = sub_response['result']
                self.subscriptions[f"account_{wallet}"] = sub_id
                logger.info(f"✅ [{index+1}] Account subscription successful: {sub_id}")
            else:
                logger.warning(f"⚠️ [{index+1}] Account subscription failed: {sub_response}")
            
            # 🎯 OPTIMIZED: Skip program subscriptions to reduce complexity and potential conflicts
            # The logs and account subscriptions are sufficient for comprehensive trade detection
            logger.info(f"✅ [{index+1}] Wallet {wallet[:8]}... fully subscribed (logs + account)")
            
        except Exception as e:
            logger.error(f"❌ [{index+1}] Subscription error for {wallet[:8]}...: {e}")
            raise
    
    async def _monitor_messages(self):
        """👂 Monitor incoming WebSocket messages"""
        logger.info("👂 Starting message monitoring...")
        
        try:
            while self.is_running:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=self.config.message_timeout
                    )
                    
                    self.messages_received += 1
                    
                    # Parse and handle message
                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError as e:
                        logger.debug(f"❌ JSON decode error: {e}")
                    except Exception as e:
                        logger.error(f"❌ Message handling error: {e}")
                        logger.debug(traceback.format_exc())
                
                except asyncio.TimeoutError:
                    # This is normal - just means no messages in timeout period
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("🔌 WebSocket connection closed during monitoring")
                    break
                except Exception as e:
                    logger.error(f"❌ Message monitoring error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"❌ Monitor loop error: {e}")
        
        logger.info("👂 Message monitoring stopped")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """📨 Handle incoming WebSocket message, including enhanced transaction stream"""
        try:
            method = data.get("method")
            if method == "logsNotification":
                await self._handle_logs_notification(data)
            elif method == "accountNotification":
                await self._handle_account_notification(data)
            elif method == "signatureNotification":
                await self._handle_signature_notification(data)
            elif method == "transactionNotification":
                await self._handle_enhanced_transaction_notification(data)
            else:
                if 'result' in data and 'id' in data:
                    logger.debug(f"📡 Subscription response: {data['id']} -> {data['result']}")
                else:
                    logger.debug(f"📨 Other message: {method}")
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")

    async def _handle_enhanced_transaction_notification(self, data: Dict[str, Any]):
        """Handle Helius enhanced transaction stream notification"""
        try:
            params = data.get("params", {})
            result = params.get("result", {})
            signature = result.get("transaction", {}).get("signatures", [None])[0]
            transaction = result.get("transaction")
            meta = result.get("meta")
            if not signature or not transaction:
                return
            if signature in self.processed_signatures:
                return
            self.processed_signatures.add(signature)
            # You can add more advanced trade detection here if needed
            trade_info = {
                'signature': signature,
                'detection_method': 'enhanced_transaction_stream',
                'timestamp': datetime.now(timezone.utc),
                'requires_analysis': True,
                'meta': meta,
                'transaction': transaction
            }
            # Pattern B: Properly await async pipeline with explicit logging
            logger.info(f"🧩 [CALLBACK] SCHEDULED pipeline for enhanced_tx {signature[:8]}...")
            try:
                logger.info(f"🧩 [CALLBACK] START pipeline (async) for {signature[:8]}...")
                await self.trade_callback(trade_info)
                logger.info(f"🧩 [CALLBACK] END pipeline finished successfully for {signature[:8]}")
            except Exception as e:
                logger.error(f"❌ [CALLBACK] ERROR pipeline crashed for {signature[:8]}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"❌ Error handling enhanced transaction notification: {e}")
    
    async def _handle_logs_notification(self, data: Dict[str, Any]):
        """📋 Handle logs notification (primary trade detection method, best-practice)"""
        try:
            params = data.get("params", {})
            result = params.get("result", {})
            if result.get("value", {}).get("err"):
                logger.debug("❌ Transaction failed - skipping")
                return
            signature = result.get("value", {}).get("signature")
            logs = result.get("value", {}).get("logs", [])
            
            # Track backfill data to avoid redundant RPC calls
            backfill_data = None
            
            # If we have logs but no signature, try backfill
            if not signature and logs:
                logger.info("🔍 [BACKFILL] Logs event without signature - attempting backfill")
                # Try to backfill from target wallets
                for wallet_str in self.config.target_wallets[:1]:  # Try first wallet
                    backfill_data = await backfill_latest_tx(self.config.helius_rpc_url, wallet_str)
                    if backfill_data:
                        signature = backfill_data["signature"]
                        # Merge logs if we got some from backfill
                        if backfill_data.get("logs"):
                            logs = backfill_data["logs"]
                        logger.info(f"🔁 [BACKFILL] Retrieved signature via backfill: {signature[:8]}...")
                        break
            
            if not signature or not logs:
                return
            if signature in self.processed_signatures:
                return
            self.processed_signatures.add(signature)
            if self._looks_like_trade(logs):
                logger.info(f"🎯 Trade detected: {signature[:8]}... with {len(logs)} logs")
                target_wallet = self._find_target_wallet_for_signature(signature, logs)
                # Always fetch full transaction/meta from RPC for every trade event
                meta = None
                transaction = None
                
                # If we already have backfill data, use it to avoid redundant RPC call
                if backfill_data:
                    meta = backfill_data.get("meta")
                    transaction = backfill_data.get("transaction")
                    logger.info("🔁 [BACKFILL] Reusing backfilled transaction/meta data")
                else:
                    try:
                        payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getTransaction",
                            "params": [
                                signature,
                                {
                                    "encoding": "json",
                                    "commitment": "confirmed",
                                    "maxSupportedTransactionVersion": 0
                                }
                            ]
                        }
                        async with aiohttp.ClientSession() as session:
                            async with session.post(self.config.helius_rpc_url, json=payload) as response:
                                data_rpc = await response.json()
                                result_rpc = data_rpc.get('result')
                                if result_rpc:
                                    meta = result_rpc.get('meta')
                                    transaction = result_rpc.get('transaction')
                    except Exception as rpc_error:
                        logger.warning(f"⚠️ Could not fetch transaction metadata for {signature[:8]}: {rpc_error}")
                # Pass only enriched trade info to callback, no legacy/partial analysis
                trade_info = {
                    'signature': signature,
                    'wallet_address': target_wallet,
                    'logs': logs,
                    'timestamp': datetime.now(timezone.utc),
                    'detection_method': 'websocket_logs',
                    'meta': meta,
                    'transaction': transaction
                }
                # Pattern B: Properly await async pipeline with explicit logging
                logger.info(f"🧩 [CALLBACK] SCHEDULED pipeline for logs_trade {signature[:8]}...")
                try:
                    logger.info(f"🧩 [CALLBACK] START pipeline (async) for {signature[:8]}...")
                    await self.trade_callback(trade_info)
                    logger.info(f"🧩 [CALLBACK] END pipeline finished successfully for {signature[:8]}")
                except Exception as e:
                    logger.error(f"❌ [CALLBACK] ERROR pipeline crashed for {signature[:8]}: {e}", exc_info=True)
            else:
                logger.debug(f"ℹ️ Non-trade transaction: {signature[:8]}...")
        except Exception as e:
            logger.error(f"❌ Error handling logs notification: {e}")
            logger.debug(traceback.format_exc())
    
    async def _handle_account_notification(self, data: Dict[str, Any]):
        """👤 Handle account notification (balance changes)"""
        try:
            logger.info("⚡ Account change detected - triggering analysis")
            
            # For account notifications, we need to fetch recent transactions
            # This is handled by the main trade callback
            
            # Create a generic trade info for account changes
            trade_info = {
                'detection_method': 'websocket_account_change',
                'timestamp': datetime.now(timezone.utc),
                'requires_full_analysis': True
            }
            
            # If signature is missing, try backfill for each target wallet
            if not trade_info.get("signature"):
                # Try to find which wallet had the account change
                # Since we don't have the wallet in the notification, try the first target wallet
                # The callback will determine the correct wallet using balance changes
                for wallet_str in self.config.target_wallets[:1]:  # Try first wallet as representative
                    backfill = await backfill_latest_tx(self.config.helius_rpc_url, wallet_str)
                    if backfill:
                        trade_info["signature"] = backfill["signature"]
                        trade_info["logs"] = backfill["logs"]
                        trade_info["transaction"] = backfill["transaction"]
                        trade_info["meta"] = backfill.get("meta")
                        logger.info("🔁 [BACKFILL] Attached signature/logs/tx via RPC backfill")
                        break
                else:
                    logger.warning("⚠️ [BACKFILL] No signature available and backfill returned nothing")
            
            # Let the callback handle the full analysis
            # Pattern B: Properly await async pipeline with explicit logging
            logger.info(f"🧩 [CALLBACK] SCHEDULED pipeline for account_change...")
            try:
                logger.info(f"🧩 [CALLBACK] START pipeline (async) for account_change...")
                await self.trade_callback(trade_info)
                logger.info(f"🧩 [CALLBACK] END pipeline finished successfully for account_change")
            except Exception as e:
                logger.error(f"❌ [CALLBACK] ERROR pipeline crashed for account_change: {e}", exc_info=True)
            
        except Exception as e:
            logger.error(f"❌ Error handling account notification: {e}")
    
    async def _handle_signature_notification(self, data: Dict[str, Any]):
        """✍️ Handle signature notification (new transactions)"""
        try:
            params = data.get("params", {})
            result = params.get("result", {})
            signature = result.get("value", {}).get("signature")
            if signature and signature not in self.processed_signatures:
                logger.info(f"⚡ New signature detected: {signature[:8]}...")
                self.processed_signatures.add(signature)
                meta = None
                transaction = None
                try:
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            signature,
                            {
                                "encoding": "json",
                                "commitment": "confirmed",
                                "maxSupportedTransactionVersion": 0
                            }
                        ]
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(self.config.helius_rpc_url, json=payload) as response:
                            data_rpc = await response.json()
                            result_rpc = data_rpc.get('result')
                            if result_rpc:
                                meta = result_rpc.get('meta')
                                transaction = result_rpc.get('transaction')
                except Exception as rpc_error:
                    logger.warning(f"⚠️ Could not fetch transaction metadata for {signature[:8]}: {rpc_error}")
                trade_info = {
                    'signature': signature,
                    'detection_method': 'websocket_signature',
                    'timestamp': datetime.now(timezone.utc),
                    'requires_analysis': True,
                    'meta': meta,
                    'transaction': transaction
                }
                # Pattern B: Properly await async pipeline with explicit logging
                logger.info(f"🧩 [CALLBACK] SCHEDULED pipeline for signature {signature[:8]}...")
                try:
                    logger.info(f"🧩 [CALLBACK] START pipeline (async) for {signature[:8]}...")
                    await self.trade_callback(trade_info)
                    logger.info(f"🧩 [CALLBACK] END pipeline finished successfully for {signature[:8]}")
                except Exception as e:
                    logger.error(f"❌ [CALLBACK] ERROR pipeline crashed for {signature[:8]}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"❌ Error handling signature notification: {e}")
    
    def _looks_like_trade(self, logs: List[str]) -> bool:
        """
        Only return True if logs indicate a token trade, not just account creation.
        """
        log_text = ' '.join(logs).lower()
        # Only match actual trade patterns
        trade_patterns = ['swap', 'buy', 'sell', 'trade', 'exchange']
        # Exclude account creation/init patterns
        account_init_patterns = ['initialize the associated token account', 'instruction: initializeaccount', 'instruction: create']
        if any(p in log_text for p in trade_patterns):
            if not any(p in log_text for p in account_init_patterns):
                return True
        return False
    
    def _basic_trade_analysis(self, logs: List[str], meta: Optional[dict] = None, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """ENHANCED: Use token balance changes for accurate buy/sell detection for the target wallet."""
        try:
            log_text = ' '.join(logs).lower()
            likely_action = 'unknown'
            confidence = 'low'
            reasoning = 'No clear indicators'
            detected_dex = 'unknown'
            detection_confidence = 'low'
            detection_method = 'text_pattern'

            # --- CRITICAL FIX: DEX detection using program IDs from logs ---
            # Check for Jupiter aggregator (HIGHEST PRIORITY - routes to multiple DEXs)
            if 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4' in log_text:
                detected_dex = 'jupiter'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for Raydium CPMM program
            elif 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C' in log_text:
                detected_dex = 'raydium_cpmm'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for Raydium CLMM program
            elif 'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK' in log_text:
                detected_dex = 'raydium_clmm'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for Meteora
            elif 'LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo' in log_text:
                detected_dex = 'meteora'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for Lifinity
            elif 'cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG' in log_text:
                detected_dex = 'lifinity'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for Whirlpool
            elif 'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc' in log_text:
                detected_dex = 'whirlpool'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for Meteora DAMM v2 (legacy detection)
            elif 'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN' in log_text:
                detected_dex = 'meteora_damm_v2'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for Pump.fun programs (BOTH active program IDs)
            elif ('6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P' in log_text or 
                  'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA' in log_text):
                detected_dex = 'pumpfun'
                detection_confidence = 'high'
                detection_method = 'program_id_detection'
            
            # Check for the ACTUAL program ID found in your trades
            elif 'LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj' in log_text:
                detected_dex = 'advanced_routing'  # This routes to Advanced MEV
                detection_confidence = 'high'
                detection_method = 'program_id_detection'

            # --- Token balance change analysis ---
            if meta and wallet_address:
                pre_balances = meta.get('preTokenBalances', [])
                post_balances = meta.get('postTokenBalances', [])
                # Map by account index
                pre_map = {b['accountIndex']: b for b in pre_balances if 'accountIndex' in b}
                post_map = {b['accountIndex']: b for b in post_balances if 'accountIndex' in b}
                # Find all account indices for the wallet
                changed = []
                for idx, post in post_map.items():
                    owner = post.get('owner')
                    if owner and owner == wallet_address:
                        pre_amt = int(pre_map.get(idx, {}).get('uiTokenAmount', {}).get('amount', '0'))
                        post_amt = int(post.get('uiTokenAmount', {}).get('amount', '0'))
                        if pre_amt != post_amt:
                            changed.append((pre_amt, post_amt, post.get('mint')))
                if changed:
                    # If any token decreased, it's a sell; if increased, it's a buy
                    for pre_amt, post_amt, mint in changed:
                        if pre_amt > post_amt:
                            likely_action = 'sell'
                            confidence = 'high'
                            reasoning = f'Token {mint} balance decreased for wallet.'
                            break
                        elif post_amt > pre_amt:
                            likely_action = 'buy'
                            confidence = 'high'
                            reasoning = f'Token {mint} balance increased for wallet.'
                            break

            # Fallback to log pattern matching if balance change is inconclusive
            if likely_action == 'unknown':
                buy_indicators = [
                    'instruction: buy', 'program log: buy', 'buy instruction',
                    'swapbasetoquote', 'exactinwithslippage', 'soltospl', 'wsoltotoken',
                    'purchasing', 'acquiring', 'input sol', 'spend sol'
                ]
                sell_indicators = [
                    'instruction: sell', 'program log: sell', 'sell instruction', 
                    'swapquotetobase', 'exactoutwithslippage', 'splittosol', 'tokentowsol',
                    'liquidating', 'divesting', 'output sol', 'receive sol'
                ]
                for indicator in buy_indicators:
                    if indicator in log_text:
                        likely_action = 'buy'
                        confidence = 'high'
                        reasoning = f'Found buy indicator: {indicator}'
                        break
                if likely_action == 'unknown':
                    for indicator in sell_indicators:
                        if indicator in log_text:
                            likely_action = 'sell'
                            confidence = 'high'
                            reasoning = f'Found sell indicator: {indicator}'
                            break

            # Don't assume action without evidence
            if likely_action == 'unknown' and detected_dex != 'unknown':
                confidence = 'low'
                reasoning = f'Detected {detected_dex} activity but no clear buy/sell evidence'

            return {
                'likely_action': likely_action,
                'confidence': confidence,
                'reasoning': reasoning,
                'method': 'token_balance_analysis',
                'detected_dex': detected_dex,
                'detection_confidence': detection_confidence,
                'detection_method': detection_method,
                'copy_immediately': True if confidence in ['high', 'medium'] else False
            }
        except Exception as e:
            return {
                'likely_action': 'buy',
                'confidence': 'fallback',
                'reasoning': f'Analysis error, copying defensively: {str(e)}',
                'method': 'token_balance_analysis',
                'detected_dex': 'unknown',
                'detection_confidence': 'low',
                'detection_method': 'fallback',
                'copy_immediately': True
            }
    
    def _find_target_wallet_for_signature(self, signature: str, logs: List[str]) -> Optional[str]:
        """🎯 ENHANCED: Find which target wallet this transaction is for"""
        try:
            # First check if any target wallet is mentioned in logs
            log_text = ' '.join(logs)
            
            for wallet in self.config.target_wallets:
                if wallet in log_text:
                    logger.info(f"✅ Wallet {wallet[:8]}... found in logs for {signature[:8]}...")
                    return wallet
            
            # 🔧 FIX: If wallet not in logs, but transaction was detected via "mentions" filter,
            # it means one of our target wallets IS involved. Check which subscription triggered this.
            # Since WebSocket "mentions" filter only triggers when wallet is in account keys,
            # we know this transaction involves one of our target wallets.
            
            logger.info(f"🔍 Wallet not in logs but detected via mentions filter - analyzing signature {signature[:8]}...")
            
            # Return the first target wallet for now, but mark for deep analysis
            # The trade processor will determine the correct wallet using balance changes
            if self.config.target_wallets:
                return self.config.target_wallets[0]  # Will be corrected by analysis
            
            return None
            
        except Exception:
            return None
    
    async def stop(self):
        """🛑 Stop WebSocket monitoring"""
        logger.info("🛑 Stopping WebSocket monitoring...")
        self.is_running = False
        
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.debug(f"Error closing WebSocket: {e}")
        
        logger.info("✅ WebSocket monitoring stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Get WebSocket statistics"""
        uptime = time.time() - self.connection_start_time if self.connection_start_time else 0
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'messages_received': self.messages_received,
            'trades_detected': self.trades_detected,
            'processed_signatures': len(self.processed_signatures),
            'subscriptions': len(self.subscriptions)
        }


async def create_websocket_handler(
    target_wallets: List[str],
    helius_ws_url: str,
    helius_rpc_url: str,
    trade_callback: Callable,
    **config_kwargs
) -> WebSocketHandler:
    """
    🏭 Factory function to create WebSocket handler
    
    Args:
        target_wallets: List of wallet addresses to monitor
        helius_ws_url: Helius WebSocket URL
        helius_rpc_url: Helius RPC URL  
        trade_callback: Async function to call when trades detected
        **config_kwargs: Additional configuration options
    
    Returns:
        Configured WebSocketHandler instance
    """
    config = WebSocketConfig(
        target_wallets=target_wallets,
        helius_ws_url=helius_ws_url,
        helius_rpc_url=helius_rpc_url,
        **config_kwargs
    )
    
    return WebSocketHandler(config, trade_callback)


# Example usage and testing
if __name__ == "__main__":
    async def example_trade_callback(trade_info: Dict[str, Any]):
        """Example trade callback for testing"""
        print(f"🎯 Trade detected: {trade_info}")
    
    async def main():
        """Example main function for testing"""
        # Example configuration
        target_wallets = ["suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"]
        helius_ws_url = "wss://mainnet.helius-rpc.com/?api-key=YOUR_KEY"
        helius_rpc_url = "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY"
        
        # Create handler
        handler = await create_websocket_handler(
            target_wallets=target_wallets,
            helius_ws_url=helius_ws_url,
            helius_rpc_url=helius_rpc_url,
            trade_callback=example_trade_callback
        )
        
        # Start monitoring
        try:
            await handler.start_monitoring()
        except KeyboardInterrupt:
            await handler.stop()
    
    # Run example
    asyncio.run(main())
