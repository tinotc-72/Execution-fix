#!/usr/bin/env python3
"""
Integrated Trade Monitor - Thin wrapper combining WebSocket detection and analysis
This provides a single interface while keeping the underlying components modular
"""

import asyncio
import logging
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime, timezone

from websocket_handler import create_websocket_handler, WebSocketHandler
from official_wallet_perspective_analyzer import OfficialWalletPerspectiveAnalyzer

logger = logging.getLogger(__name__)

class IntegratedTradeMonitor:
    """
    🚀 Integrated Trade Monitor - Single interface for WebSocket detection + analysis
    
    Combines WebSocket handler and official analyzer while keeping them modular.
    This gives you the convenience of a single script with the benefits of separation.
    """
    
    def __init__(
        self,
        target_wallets: List[str],
        helius_ws_url: str,
        helius_rpc_url: str,
        rpc_client,
        trade_callback: Callable,
        **websocket_config
    ):
        """
        Initialize integrated monitor
        
        Args:
            target_wallets: List of wallet addresses to monitor
            helius_ws_url: Helius WebSocket URL
            helius_rpc_url: Helius RPC URL
            rpc_client: Solana RPC client for analysis
            trade_callback: Final callback for confirmed trades
            **websocket_config: Additional WebSocket configuration
        """
        self.target_wallets = target_wallets
        self.trade_callback = trade_callback
        self.rpc_client = rpc_client
        
        # Create the official analyzer
        self.analyzer = OfficialWalletPerspectiveAnalyzer(rpc_client)
        
        # WebSocket handler will be created in start_monitoring
        self.ws_handler: Optional[WebSocketHandler] = None
        
        # Store config for WebSocket creation
        self.helius_ws_url = helius_ws_url
        self.helius_rpc_url = helius_rpc_url
        self.websocket_config = websocket_config
        
        # Statistics
        self.detections = 0
        self.confirmed_trades = 0
        self.false_positives = 0
        
        logger.info(f"🚀 Integrated Trade Monitor initialized")
        logger.info(f"   🎯 Target wallets: {len(target_wallets)}")
    
    async def start_monitoring(self):
        """🚀 Start integrated monitoring with detection + analysis"""
        try:
            logger.info("🚀 Starting integrated trade monitoring...")
            
            # Create WebSocket handler with our internal callback
            self.ws_handler = await create_websocket_handler(
                target_wallets=self.target_wallets,
                helius_ws_url=self.helius_ws_url,
                helius_rpc_url=self.helius_rpc_url,
                trade_callback=self._handle_detected_transaction,
                **self.websocket_config
            )
            
            # Start monitoring (this will block until stopped)
            await self.ws_handler.start_monitoring()
            
        except Exception as e:
            logger.error(f"❌ Error in integrated monitoring: {e}")
            raise
    
    async def _handle_detected_transaction(self, trade_info: Dict[str, Any]):
        """🔍 Handle transaction detected by WebSocket - perform analysis"""
        try:
            self.detections += 1
            
            logger.info(f"🔍 Transaction detected, performing analysis...")
            
            # Extract signature and wallet from detection
            signature = trade_info.get('signature')
            wallet_address = trade_info.get('wallet_address')
            
            if not signature or not wallet_address:
                logger.warning(f"⚠️ Missing signature or wallet in detection")
                return
            
            # Perform official analysis
            analysis_result = await self.analyzer.analyze_wallet_action(signature, wallet_address)
            
            if analysis_result and analysis_result.get('action') not in ['none', 'error']:
                # Confirmed trade - call the final callback
                self.confirmed_trades += 1
                
                confirmed_trade_info = {
                    'signature': signature,
                    'wallet_address': wallet_address,
                    'action': analysis_result['action'],
                    'token_mint': analysis_result['token_mint'],
                    'amount_change': analysis_result.get('amount_change', 0),
                    'confidence': analysis_result.get('confidence', 10),
                    'timestamp': datetime.now(timezone.utc),
                    'detection_method': 'integrated_websocket_analysis',
                    'original_detection': trade_info
                }
                
                logger.info(f"✅ Confirmed trade: {analysis_result['action'].upper()} {analysis_result['token_mint'][:8]}...")
                
                # Call the final trade callback
                await self.trade_callback(confirmed_trade_info)
                
            else:
                # False positive
                self.false_positives += 1
                logger.debug(f"❌ False positive: No confirmed trade action")
                
        except Exception as e:
            logger.error(f"❌ Error analyzing detected transaction: {e}")
    
    async def stop(self):
        """🛑 Stop integrated monitoring"""
        if self.ws_handler:
            await self.ws_handler.stop()
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Get monitoring statistics"""
        ws_stats = self.ws_handler.get_stats() if self.ws_handler else {}
        
        return {
            'integrated_stats': {
                'detections': self.detections,
                'confirmed_trades': self.confirmed_trades,
                'false_positives': self.false_positives,
                'accuracy': (self.confirmed_trades / max(self.detections, 1)) * 100
            },
            'websocket_stats': ws_stats
        }


async def create_integrated_monitor(
    target_wallets: List[str],
    helius_ws_url: str,
    helius_rpc_url: str,
    rpc_client,
    trade_callback: Callable,
    **websocket_config
) -> IntegratedTradeMonitor:
    """
    🏭 Factory function to create integrated trade monitor
    
    This gives you a single interface that combines WebSocket detection and analysis
    while keeping the underlying components modular and reusable.
    """
    return IntegratedTradeMonitor(
        target_wallets=target_wallets,
        helius_ws_url=helius_ws_url,
        helius_rpc_url=helius_rpc_url,
        rpc_client=rpc_client,
        trade_callback=trade_callback,
        **websocket_config
    )


# Example usage
if __name__ == "__main__":
    async def example_trade_callback(trade_info: Dict[str, Any]):
        """Example final trade callback"""
        print(f"🎯 CONFIRMED TRADE:")
        print(f"   Action: {trade_info['action'].upper()}")
        print(f"   Token: {trade_info['token_mint'][:8]}...")
        print(f"   Amount: {trade_info['amount_change']}")
        print(f"   Confidence: {trade_info['confidence']}/10")
    
    async def test_integrated_monitor():
        """Test the integrated monitor"""
        from solana.rpc.async_api import AsyncClient
        
        # Configuration
        target_wallets = ["suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"]
        helius_ws_url = "wss://mainnet.helius-rpc.com/?api-key=YOUR_KEY"
        helius_rpc_url = "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY"
        rpc_client = AsyncClient(helius_rpc_url)
        
        # Create integrated monitor
        monitor = await create_integrated_monitor(
            target_wallets=target_wallets,
            helius_ws_url=helius_ws_url,
            helius_rpc_url=helius_rpc_url,
            rpc_client=rpc_client,
            trade_callback=example_trade_callback,
            max_retries=3
        )
        
        try:
            # Monitor for 30 seconds
            await asyncio.wait_for(monitor.start_monitoring(), timeout=30.0)
        except asyncio.TimeoutError:
            print("Test timeout")
        finally:
            await monitor.stop()
            stats = monitor.get_stats()
            print(f"📊 Final Stats: {stats}")
    
    # Run test
    print("🧪 Testing Integrated Trade Monitor")
    asyncio.run(test_integrated_monitor())
