"""
🚀 TRADE PROCESSOR - Pure trade analysis and routing logic
Handles validation, analysis, and routing decisions without execution
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TradeProcessor:
    """
    Pure trade processor - analyzes trades and provides routing decisions
    NO EXECUTION - only analysis and routing instructions
    """
    
    def __init__(self, target_wallets: List[str], rpc_client=None):
        self.target_wallets = target_wallets
        self.rpc_client = rpc_client
        
        # 🧠 INTELLIGENT EXECUTOR MAPPING based on program IDs
        self.dex_executor_mapping = {
            'pumpfun': ['direct_pumpfun'],
            'raydium_cpmm': ['cpmm'],
            'raydium_clmm': ['clmm'], 
            'raydium_amm': ['raydium'],
            'jupiter': ['jupiter'],
            'orca': ['orca'],
            'phoenix': ['phoenix'],
            'unknown': ['jupiter', 'raydium']  # Safe defaults
        }
    
    async def validate_trade_info(self, trade_info: Dict[str, Any]) -> bool:
        """Validate trade info structure"""
        if not trade_info:
            return False
        
        # Check for minimum required fields
        required_fields = ['signature', 'wallet_address']
        for field in required_fields:
            if field not in trade_info:
                return False
        
        return True
    
    async def analyze_and_route_trade(self, trade_info: Dict[str, Any], source_wallet: str) -> Dict[str, Any]:
        """
        Analyze trade and return routing instructions (NO EXECUTION)
        
        Returns:
            Dict with routing instructions for the execution coordinator
        """
        try:
            # Extract action from trade info
            action = self._extract_action(trade_info)
            token_mint = trade_info.get('token_mint', 'UNKNOWN')
            
            logger.info(f"🔍 ANALYZING {action.upper()} from {source_wallet[:8]}...")
            
            # Determine execution strategy
            execution_strategy = await self._determine_execution_strategy(trade_info, action)
            
            # Build routing instructions
            routing_instructions = {
                'action': action,
                'token_mint': token_mint,
                'source_wallet': source_wallet,
                'execution_strategy': execution_strategy,
                'trade_info': trade_info,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'requires_execution': True
            }
            
            logger.info(f"✅ Trade analyzed - Strategy: {execution_strategy['type']}")
            return routing_instructions
            
        except Exception as e:
            logger.error(f"❌ Trade analysis failed: {e}")
            return {
                'action': 'error',
                'error': str(e),
                'requires_execution': False
            }
    
    def _extract_action(self, trade_info: Dict[str, Any]) -> str:
        """Extract trade action from trade info"""
        # Try direct action field first
        action = trade_info.get('action')
        
        # Try basic_analysis field
        if not action and 'basic_analysis' in trade_info:
            action = trade_info['basic_analysis'].get('likely_action', 'unknown')
        
        # Default to unknown
        if not action:
            action = 'unknown'
        
        return action.lower()
    
    async def _determine_execution_strategy(self, trade_info: Dict[str, Any], action: str) -> Dict[str, Any]:
        """
        Determine the best execution strategy based on trade analysis
        Returns strategy instructions, not execution
        """
        try:
            # Detect DEX type from trade info
            dex_type = self._detect_dex_type(trade_info)
            
            # Get confidence score
            confidence = self._calculate_confidence(trade_info, dex_type)
            
            # Determine strategy based on action and confidence
            if action in ['buy', 'swap_in']:
                return self._get_buy_strategy(dex_type, confidence, trade_info)
            elif action in ['sell', 'swap_out']:
                return self._get_sell_strategy(dex_type, confidence, trade_info)
            else:
                return self._get_fallback_strategy(trade_info)
                
        except Exception as e:
            logger.warning(f"Strategy determination failed: {e}")
            return self._get_fallback_strategy(trade_info)
    
    def _detect_dex_type(self, trade_info: Dict[str, Any]) -> str:
        """Detect which DEX was used based on trade info"""
        # Check for program IDs or other indicators
        program_id = trade_info.get('program_id', '')
        
        # Known program ID mappings
        if '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P' in program_id:
            return 'pumpfun'
        elif 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C' in program_id:
            return 'raydium_cpmm'
        elif 'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK' in program_id:
            return 'raydium_clmm'
        elif '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8' in program_id:
            return 'raydium_amm'
        else:
            return 'unknown'
    
    def _calculate_confidence(self, trade_info: Dict[str, Any], dex_type: str) -> float:
        """Calculate confidence score for trade detection"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on available data
        if trade_info.get('token_mint'):
            confidence += 0.2
        if trade_info.get('amount_change'):
            confidence += 0.2
        if dex_type != 'unknown':
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _get_buy_strategy(self, dex_type: str, confidence: float, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get buy execution strategy"""
        # High confidence - use specific DEX
        if confidence >= 0.8 and dex_type in self.dex_executor_mapping:
            return {
                'type': 'focused',
                'executors': self.dex_executor_mapping[dex_type],
                'confidence': confidence,
                'parallel': False
            }
        
        # Medium confidence - try focused then fallback
        elif confidence >= 0.6:
            primary = self.dex_executor_mapping.get(dex_type, ['jupiter'])
            fallback = ['jupiter', 'raydium'] if dex_type != 'unknown' else ['jupiter']
            
            return {
                'type': 'tiered',
                'primary_executors': primary,
                'fallback_executors': fallback,
                'confidence': confidence,
                'parallel': False
            }
        
        # Low confidence - safe parallel approach
        else:
            return {
                'type': 'parallel_safe',
                'executors': ['jupiter', 'raydium'],
                'confidence': confidence,
                'parallel': True
            }
    
    def _get_sell_strategy(self, dex_type: str, confidence: float, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get sell execution strategy"""
        # For sells, always try the detected DEX first
        if dex_type in self.dex_executor_mapping:
            return {
                'type': 'focused_sell',
                'executors': self.dex_executor_mapping[dex_type],
                'confidence': confidence,
                'parallel': False,
                'sell_percentage': trade_info.get('sell_percentage', 100)  # Default full sell
            }
        else:
            return {
                'type': 'fallback_sell',
                'executors': ['jupiter'],
                'confidence': confidence,
                'parallel': False,
                'sell_percentage': trade_info.get('sell_percentage', 100)
            }
    
    def _get_fallback_strategy(self, trade_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback strategy for unknown trades"""
        return {
            'type': 'fallback',
            'executors': ['jupiter'],
            'confidence': 0.3,
            'parallel': False,
            'note': 'Using fallback strategy due to analysis failure'
        }
    
    async def extract_token_info_fast(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Fast token extraction from transaction
        Pure analysis - no execution
        """
        try:
            logger.debug(f"🔍 Fast token extraction for {signature[:8]}...")
            
            # This would use utils to analyze the transaction
            # Placeholder for actual implementation
            from utils import get_transaction_with_logs
            
            transaction = await get_transaction_with_logs(signature, self.rpc_client)
            if not transaction:
                return None
            
            # Extract token info from transaction
            # Implementation would go here
            
            return {
                'token_mint': 'EXTRACTED_TOKEN_MINT',
                'action': 'extracted_action',
                'amount_change': 0,
                'method': 'fast_extraction'
            }
            
        except Exception as e:
            logger.warning(f"Fast extraction failed: {e}")
            return None
    
    async def analyze_trade_simple(self, signature: str, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Simple trade analysis
        Pure analysis - no execution
        """
        try:
            logger.debug(f"🔍 Simple trade analysis for {signature[:8]}...")
            
            # This would perform deeper analysis
            # Placeholder for actual implementation
            
            return {
                'confidence': 0.7,
                'dex_type': 'detected_dex',
                'trade_type': 'detected_type',
                'analysis_method': 'simple'
            }
            
        except Exception as e:
            logger.warning(f"Simple analysis failed: {e}")
            return None

    def get_target_wallets(self) -> List[str]:
        """Get list of target wallets being monitored"""
        return self.target_wallets.copy()
    
    def is_target_wallet(self, wallet_address: str) -> bool:
        """Check if wallet is in target list"""
        return wallet_address in self.target_wallets
