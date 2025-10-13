"""
🚀 SOCKET TRADE DETECTOR - Separate modular trade detection using WebSockets
This module handles all trade detection logic and sends signals to main.py
"""

import asyncio
import json
import logging
import traceback
import time
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timezone
import websockets
import aiohttp

# Import your existing WebSocket infrastructure
try:
    from wallet_tx_parser import WebSocketWalletMonitor, create_websocket_monitor
    WEBSOCKET_AVAILABLE = True
    print("✅ Socket Trade Detector: WebSocket infrastructure available")
except ImportError:
    print("❌ Socket Trade Detector: WebSocket infrastructure not available")
    WEBSOCKET_AVAILABLE = False

try:
    from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer
    ANALYZER_AVAILABLE = True
    print("✅ Socket Trade Detector: Official analyzer available")
except ImportError:
    print("❌ Socket Trade Detector: Official analyzer not available")
    ANALYZER_AVAILABLE = False

logger = logging.getLogger(__name__)

class SocketTradeDetector:
    """
    🚀 MODULAR SOCKET TRADE DETECTOR
    - Handles all WebSocket connections and trade detection
    - Sends clean trade signals to main.py via callback
    - No execution logic - pure detection only
    """
    
    def __init__(self, target_wallets: List[str], trade_callback: Callable, rpc_client=None):
        """
        Initialize socket trade detector
        
        Args:
            target_wallets: List of wallet addresses to monitor
            trade_callback: Function to call when trade is detected
            rpc_client: RPC client for transaction analysis
        """
        self.target_wallets = target_wallets
        self.trade_callback = trade_callback
        self.rpc_client = rpc_client
        self.is_monitoring = False
        self.ws_monitor = None
        self.processed_signatures = set()
        
        # Initialize analyzer if available
        self.analyzer = None
        if ANALYZER_AVAILABLE and rpc_client:
            self.analyzer = OfficialWalletPerspectiveAnalyzer(rpc_client)
            
        logger.info(f"🚀 Socket Trade Detector initialized for {len(target_wallets)} wallets")
        
    async def start_monitoring(self):
        """Start WebSocket monitoring for trade detection"""
        if not WEBSOCKET_AVAILABLE:
            logger.error("❌ WebSocket infrastructure not available")
            return False
            
        try:
            logger.info("🚀 Starting socket trade detection...")
            self.is_monitoring = True
            
            # Create WebSocket monitor using your existing infrastructure
            self.ws_monitor = await create_websocket_monitor(
                self.target_wallets,
                self._handle_detected_trade
            )
            
            if self.ws_monitor:
                logger.info("✅ Socket trade detector started successfully")
                
                # Start monitoring (this will run indefinitely)
                await self.ws_monitor.start_monitoring()
                
            else:
                logger.error("❌ Failed to create WebSocket monitor")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting socket trade detector: {e}")
            logger.error(traceback.format_exc())
            return False
            
    async def stop_monitoring(self):
        """Stop WebSocket monitoring"""
        try:
            logger.info("⏹️ Stopping socket trade detection...")
            self.is_monitoring = False
            
            if self.ws_monitor:
                await self.ws_monitor.stop()
                self.ws_monitor = None
                
            logger.info("✅ Socket trade detector stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping socket trade detector: {e}")
            
    async def _handle_detected_trade(self, trade_info: Dict[str, Any]):
        """
        Handle trades detected via WebSocket
        This is the bridge between detection and execution
        """
        try:
            logger.info(f"🎯 TRADE DETECTED via Socket: {trade_info.get('signature', 'unknown')[:8]}...")
            
            # Skip test trades
            if trade_info.get('signature') == 'test123':
                logger.debug("🧪 Skipping test trade")
                return
                
            # Validate trade info
            if not self._validate_trade_info(trade_info):
                logger.warning("⚠️ Invalid trade info - skipping")
                return
                
            # Skip already processed transactions
            signature = trade_info.get('signature', '')
            if signature in self.processed_signatures:
                logger.debug(f"⏭️ Already processed: {signature[:8]}...")
                return
                
            # Mark as processed
            self.processed_signatures.add(signature)
            
            # Enhance trade info with additional analysis if needed
            enhanced_trade_info = await self._enhance_trade_info(trade_info)
            
            if enhanced_trade_info:
                # Send to main.py via callback (NON-BLOCKING)
                logger.info(f"📡 Sending trade signal to main.py...")
                
                # Create task to avoid blocking the detector
                asyncio.create_task(self.trade_callback(enhanced_trade_info))
                
            else:
                logger.warning("⚠️ Failed to enhance trade info - skipping")
                
        except Exception as e:
            logger.error(f"❌ Error handling detected trade: {e}")
            logger.error(traceback.format_exc())
            
    def _validate_trade_info(self, trade_info: Dict[str, Any]) -> bool:
        """Validate that trade info is complete and valid"""
        required_fields = ['action', 'wallet_address', 'signature']
        
        for field in required_fields:
            if not trade_info.get(field):
                logger.warning(f"⚠️ Missing required field: {field}")
                return False
                
        # Validate wallet is in target list
        wallet_address = trade_info.get('wallet_address', '')
        if wallet_address not in self.target_wallets:
            logger.warning(f"⚠️ Wallet not in target list: {wallet_address[:8]}...")
            return False
            
        # Validate token mint if provided
        token_mint = trade_info.get('token_mint')
        if token_mint:
            # Filter out known problematic tokens
            problematic_patterns = [
                'AGGRESSIVE_TARGET_WALLET_',
                'FALLBACK_BUY_TOKEN_',
                'ERROR_FALLBACK_BUY_',
                'EMERGENCY_TOKEN_DETECTION_FAILED',
                'BALANCE_ANALYSIS_REQUIRED'
            ]
            
            for pattern in problematic_patterns:
                if pattern in token_mint:
                    logger.warning(f"⚠️ Problematic token pattern detected: {pattern}")
                    return False
                    
            # Validate token mint length (Solana addresses are 43-44 chars)
            if len(token_mint) < 43 or len(token_mint) > 44:
                logger.warning(f"⚠️ Invalid token mint length: {len(token_mint)}")
                return False
                
        logger.debug("✅ Trade info validation passed")
        return True
        
    async def _enhance_trade_info(self, trade_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhance trade info with additional analysis if needed
        This can include balance analysis, token extraction, etc.
        """
        try:
            enhanced_info = trade_info.copy()
            
            # Add timestamp if not present
            if 'timestamp' not in enhanced_info:
                enhanced_info['timestamp'] = datetime.now(timezone.utc)
                
            # Add detection source
            enhanced_info['detection_source'] = 'socket_trade_detector'
            
            # Perform additional analysis if analyzer is available
            if self.analyzer and not enhanced_info.get('token_mint'):
                logger.info("🔍 Performing additional token analysis...")
                
                signature = enhanced_info.get('signature')
                wallet_address = enhanced_info.get('wallet_address')
                
                if signature and wallet_address:
                    analysis_result = await self.analyzer.analyze_wallet_action(
                        signature, wallet_address
                    )
                    
                    if analysis_result and analysis_result.get('action') != 'none':
                        logger.info("✅ Enhanced trade info with analyzer results")
                        enhanced_info.update({
                            'token_mint': analysis_result.get('token_mint'),
                            'amount_change': analysis_result.get('amount_change'),
                            'confidence': analysis_result.get('confidence'),
                            'analysis_method': 'official_wallet_perspective'
                        })
                    else:
                        logger.warning("⚠️ Analyzer found no valid action")
                        return None
                        
            return enhanced_info
            
        except Exception as e:
            logger.error(f"❌ Error enhancing trade info: {e}")
            return trade_info  # Return original if enhancement fails
            
    async def emergency_rescan(self, wallet: str, max_transactions: int = 100):
        """
        Emergency rescan for missed trades
        This can be called from main.py when needed
        """
        try:
            logger.warning(f"🚨 Emergency rescan for {wallet[:8]}... (last {max_transactions} txs)")
            
            if not self.rpc_client:
                logger.error("❌ No RPC client available for emergency rescan")
                return
                
            from solders.pubkey import Pubkey
            
            # Get recent transactions
            response = await self.rpc_client.get_signatures_for_address(
                Pubkey.from_string(wallet),
                limit=max_transactions
            )
            
            if not response.value:
                logger.warning("⚠️ No transactions found in emergency rescan")
                return
                
            logger.info(f"🔍 Emergency scanning {len(response.value)} transactions...")
            
            # Process transactions that weren't already processed
            for tx_info in response.value:
                signature = str(tx_info.signature)
                
                if signature not in self.processed_signatures:
                    logger.info(f"🆕 Processing missed transaction: {signature[:8]}...")
                    
                    # Create trade info for missed transaction
                    trade_info = {
                        'signature': signature,
                        'wallet_address': wallet,
                        'action': 'buy',  # Assume buy for emergency rescan
                        'timestamp': datetime.now(timezone.utc),
                        'detection_source': 'emergency_rescan'
                    }
                    
                    # Process through normal flow
                    await self._handle_detected_trade(trade_info)
                    
        except Exception as e:
            logger.error(f"❌ Error in emergency rescan: {e}")


class SocketTradeDetectorManager:
    """
    🎯 MANAGER CLASS - Simple interface for main.py integration
    This is what main.py will import and use
    """
    
    def __init__(self):
        self.detector = None
        self.is_active = False
        
    async def initialize(self, target_wallets: List[str], trade_callback: Callable, rpc_client=None):
        """Initialize the detector with configuration"""
        try:
            self.detector = SocketTradeDetector(target_wallets, trade_callback, rpc_client)
            logger.info("✅ Socket Trade Detector Manager initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing detector manager: {e}")
            return False
            
    async def start(self):
        """Start trade detection"""
        if not self.detector:
            logger.error("❌ Detector not initialized")
            return False
            
        try:
            self.is_active = True
            await self.detector.start_monitoring()
            return True
        except Exception as e:
            logger.error(f"❌ Error starting detector: {e}")
            self.is_active = False
            return False
            
    async def stop(self):
        """Stop trade detection"""
        if not self.detector:
            return
            
        try:
            self.is_active = False
            await self.detector.stop_monitoring()
            logger.info("✅ Socket Trade Detector Manager stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping detector: {e}")
            
    async def emergency_rescan(self, wallet: str, max_transactions: int = 100):
        """Trigger emergency rescan"""
        if self.detector:
            await self.detector.emergency_rescan(wallet, max_transactions)


# Factory function for easy import
async def create_socket_trade_detector(target_wallets: List[str], trade_callback: Callable, rpc_client=None):
    """
    Factory function to create and initialize a socket trade detector
    
    Usage in main.py:
        detector = await create_socket_trade_detector(wallets, callback, rpc_client)
        await detector.start()
    """
    manager = SocketTradeDetectorManager()
    
    if await manager.initialize(target_wallets, trade_callback, rpc_client):
        return manager
    else:
        return None
