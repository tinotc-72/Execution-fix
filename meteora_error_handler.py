"""
Meteora Error Handler
Handles specific Meteora Dynamic Bonding Curve errors and provides solutions
"""

import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class MeteoraErrorHandler:
    """Handles Meteora-specific errors and provides appropriate fallback strategies"""
    
    # Meteora Dynamic Bonding Curve error codes
    METEORA_ERROR_CODES = {
        3007: {
            'name': 'BONDING_CURVE_COMPLETE',
            'description': 'The bonding curve has completed or no tokens available',
            'fallback': 'check_dex_trading'
        },
        3008: {
            'name': 'INSUFFICIENT_SUPPLY',
            'description': 'Not enough tokens available in the bonding curve',
            'fallback': 'retry_with_lower_amount'
        },
        3009: {
            'name': 'MINIMUM_PURCHASE_NOT_MET',
            'description': 'Purchase amount below minimum threshold',
            'fallback': 'increase_purchase_amount'
        },
        3010: {
            'name': 'SLIPPAGE_EXCEEDED',
            'description': 'Transaction would exceed maximum slippage',
            'fallback': 'increase_slippage_tolerance'
        },
        6000: {
            'name': 'POOL_NOT_INITIALIZED',
            'description': 'The bonding curve pool has not been initialized',
            'fallback': 'skip_token'
        }
    }
    
    def __init__(self):
        self.handled_errors = set()
    
    def parse_transaction_error(self, error_msg: str) -> Optional[Dict[str, Any]]:
        """Parse Solana transaction error to extract Meteora error code"""
        try:
            # Look for Custom error pattern: Custom(InstructionErrorCustom(3007))
            custom_error_pattern = r'Custom\(InstructionErrorCustom\((\d+)\)\)'
            match = re.search(custom_error_pattern, str(error_msg))
            
            if match:
                error_code = int(match.group(1))
                return {
                    'error_code': error_code,
                    'error_type': 'meteora_custom',
                    'raw_error': str(error_msg)
                }
            
            # Look for other error patterns
            if 'InstructionError' in str(error_msg):
                return {
                    'error_code': None,
                    'error_type': 'instruction_error',
                    'raw_error': str(error_msg)
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error parsing transaction error: {e}")
            return None
    
    def get_error_info(self, error_code: int) -> Optional[Dict[str, Any]]:
        """Get information about a Meteora error code"""
        return self.METEORA_ERROR_CODES.get(error_code)
    
    def should_fallback_to_dex(self, error_code: int) -> bool:
        """Check if we should try DEX trading instead of bonding curve"""
        fallback_to_dex_codes = [3007, 6000]  # Bonding curve complete or not initialized
        return error_code in fallback_to_dex_codes
    
    def should_retry_with_adjustments(self, error_code: int) -> bool:
        """Check if we should retry with different parameters"""
        retry_codes = [3008, 3009, 3010]  # Insufficient supply, min purchase, slippage
        return error_code in retry_codes
    
    def get_fallback_strategy(self, error_code: int, token_mint: str) -> Dict[str, Any]:
        """Get recommended fallback strategy for the error"""
        error_info = self.get_error_info(error_code)
        
        if not error_info:
            return {
                'strategy': 'skip',
                'reason': f'Unknown Meteora error code: {error_code}',
                'action': 'skip_token'
            }
        
        if error_code == 3007:  # Bonding curve complete
            return {
                'strategy': 'fallback_to_dex',
                'reason': 'Bonding curve has completed - token likely graduated to DEX',
                'action': 'try_jupiter_raydium',
                'token_mint': token_mint,
                'suggested_dexes': ['jupiter', 'raydium', 'orca']
            }
        
        elif error_code == 3008:  # Insufficient supply
            return {
                'strategy': 'retry_lower_amount',
                'reason': 'Not enough tokens available at current amount',
                'action': 'reduce_purchase_amount',
                'suggested_reduction': 0.5  # Try 50% of original amount
            }
        
        elif error_code == 3009:  # Minimum purchase not met
            return {
                'strategy': 'increase_amount',
                'reason': 'Purchase amount below minimum threshold',
                'action': 'increase_purchase_amount',
                'suggested_minimum': 0.001  # SOL minimum
            }
        
        elif error_code == 3010:  # Slippage exceeded
            return {
                'strategy': 'increase_slippage',
                'reason': 'Transaction would exceed slippage tolerance',
                'action': 'increase_slippage_tolerance',
                'suggested_slippage': 0.5  # 50% slippage for high volatility
            }
        
        else:
            return {
                'strategy': 'skip',
                'reason': f'Unhandleable Meteora error: {error_info["name"]}',
                'action': 'skip_token'
            }
    
    def log_error_analysis(self, error_code: int, token_mint: str, strategy: Dict[str, Any]):
        """Log detailed error analysis"""
        error_info = self.get_error_info(error_code)
        error_name = error_info['name'] if error_info else f'Unknown_{error_code}'
        
        logger.warning(f"🚨 METEORA ERROR ANALYSIS")
        logger.warning(f"   Token: {token_mint[:8]}...")
        logger.warning(f"   Error Code: {error_code} ({error_name})")
        logger.warning(f"   Description: {error_info['description'] if error_info else 'Unknown error'}")
        logger.warning(f"   Strategy: {strategy['strategy']}")
        logger.warning(f"   Action: {strategy['action']}")
        logger.warning(f"   Reason: {strategy['reason']}")

def handle_meteora_error(error_msg: str, token_mint: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to handle Meteora errors
    Returns fallback strategy or None if not a Meteora error
    """
    handler = MeteoraErrorHandler()
    
    # Parse the error
    parsed_error = handler.parse_transaction_error(error_msg)
    if not parsed_error or parsed_error['error_type'] != 'meteora_custom':
        return None
    
    error_code = parsed_error['error_code']
    if error_code is None:
        return None
    
    # Get fallback strategy
    strategy = handler.get_fallback_strategy(error_code, token_mint)
    
    # Log analysis
    handler.log_error_analysis(error_code, token_mint, strategy)
    
    return strategy

# Example usage for your specific error
if __name__ == "__main__":
    # Test with your specific error
    error_msg = "TransactionErrorInstructionError((2, Tagged(Custom(InstructionErrorCustom(3007)))))"
    token_mint = "2MyuH4bDzV7K3DEqY31FqGPB2rhgeBmFCYSyibsWbrwJbvNuycdXexHNDWv39DJK2CtmB9Wm9VYhYQwtjqeoAABX"
    
    strategy = handle_meteora_error(error_msg, token_mint)
    if strategy:
        print(f"✅ Fallback strategy: {strategy}")
    else:
        print("❌ Not a recognized Meteora error")
