"""
Pump.fun Token Validator
Validates that a token is actually a pump.fun token before attempting execution

This prevents the exact error we encountered with WSOL and other non-pump.fun tokens
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

logger = logging.getLogger(__name__)

# Pump.fun program ID (verified correct)
PUMP_FUN_PROGRAM_ID = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")

class PumpFunTokenValidator:
    """Validates tokens specifically for pump.fun trading"""
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
        
    async def is_pump_fun_token(self, token_mint: str) -> bool:
        """
        Check if a token is actually a pump.fun token by validating its bonding curve exists
        
        Args:
            token_mint: Token mint address as string
            
        Returns:
            True if token has valid pump.fun bonding curve, False otherwise
        """
        try:
            # Convert to Pubkey
            token_mint_pubkey = Pubkey.from_string(token_mint) if not isinstance(token_mint, Pubkey) else token_mint
            
            # WSOL and other system tokens are never pump.fun tokens
            if token_mint == "So11111111111111111111111111111111111111112":
                logger.info(f"❌ WSOL is not a pump.fun token - skipping")
                return False
                
            # Check if this looks like a valid mint address (32 bytes, valid base58)
            if len(token_mint) != 44:  # Base58 encoded pubkey should be 44 chars
                logger.warning(f"❌ Invalid token mint format: {token_mint}")
                return False
            
            # Derive the bonding curve PDA for this token
            bonding_curve_pda, _ = Pubkey.find_program_address(
                [b"bonding-curve", bytes(token_mint_pubkey)],
                PUMP_FUN_PROGRAM_ID
            )
            # Always use string for JSON/API
            bonding_curve_pda_str = str(bonding_curve_pda)
            # Check if the bonding curve account exists and is owned by pump.fun
            account_info = await self.rpc_client.get_account_info(bonding_curve_pda_str)
            value = account_info.get('result', {}).get('value') if isinstance(account_info, dict) else getattr(account_info, 'value', None)
            if value is None:
                logger.info(f"❌ No bonding curve found for {token_mint[:8]}... - not a pump.fun token")
                return False
            # Verify the account is owned by the pump.fun program
            owner = value.get('owner') if isinstance(value, dict) else getattr(value, 'owner', None)
            if str(owner) != str(PUMP_FUN_PROGRAM_ID):
                logger.warning(f"❌ Bonding curve not owned by pump.fun program for {token_mint[:8]}...")
                return False
            # Additional validation: check if the account has data
            data = value.get('data') if isinstance(value, dict) else getattr(value, 'data', None)
            if not data or len(data) == 0:
                logger.warning(f"❌ Empty bonding curve data for {token_mint[:8]}...")
                return False
            logger.info(f"✅ Valid pump.fun token confirmed: {token_mint[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating pump.fun token {token_mint[:8]}...: {e}")
            return False
    
    async def get_pump_fun_token_info(self, token_mint: str) -> Optional[Dict[str, Any]]:
        """
        Get pump.fun specific token information
        
        Args:
            token_mint: Token mint address
            
        Returns:
            Dictionary with token info or None if invalid
        """
        try:
            if not await self.is_pump_fun_token(token_mint):
                return None
                
            token_mint_pubkey = Pubkey.from_string(token_mint) if not isinstance(token_mint, Pubkey) else token_mint
            # Get bonding curve info
            bonding_curve_pda, bump = Pubkey.find_program_address(
                [b"bonding-curve", bytes(token_mint_pubkey)],
                PUMP_FUN_PROGRAM_ID
            )
            bonding_curve_pda_str = str(bonding_curve_pda)
            account_info = await self.rpc_client.get_account_info(bonding_curve_pda_str)
            value = account_info.get('result', {}).get('value') if isinstance(account_info, dict) else getattr(account_info, 'value', None)
            if value and (value.get('data') if isinstance(value, dict) else getattr(value, 'data', None)):
                data = value.get('data') if isinstance(value, dict) else getattr(value, 'data', None)
                owner = value.get('owner') if isinstance(value, dict) else getattr(value, 'owner', None)
                return {
                    "is_pump_fun_token": True,
                    "bonding_curve": bonding_curve_pda_str,
                    "bonding_curve_bump": bump,
                    "data_length": len(data),
                    "owner": str(owner)
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error getting pump.fun token info: {e}")
            return None


async def validate_pump_fun_token(rpc_client: AsyncClient, token_mint: str) -> bool:
    """
    Convenience function to validate a pump.fun token
    
    Args:
        rpc_client: Solana RPC client
        token_mint: Token mint address
        
    Returns:
        True if valid pump.fun token, False otherwise
    """
    validator = PumpFunTokenValidator(rpc_client)
    return await validator.is_pump_fun_token(token_mint)


# Test function
async def test_pump_fun_validation():
    """Test the pump.fun validator with known tokens"""
    from env_keys import EnvKeys
    
    env_keys = EnvKeys()
    client = AsyncClient(env_keys.HELIUS_RPC_URL)
    validator = PumpFunTokenValidator(client)
    
    # Test cases
    test_tokens = [
        ("So11111111111111111111111111111111111111112", "WSOL - should fail"),
        ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "USDC - should fail"),
        ("85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmn", "Test token - unknown"),
    ]
    
    print("🧪 Testing Pump.fun Token Validator")
    print("=" * 50)
    
    for token_mint, description in test_tokens:
        print(f"\n🔍 Testing: {description}")
        print(f"   Token: {token_mint}")
        
        is_valid = await validator.is_pump_fun_token(token_mint)
        result = "✅ VALID PUMP.FUN TOKEN" if is_valid else "❌ NOT A PUMP.FUN TOKEN"
        print(f"   Result: {result}")
        
        if is_valid:
            info = await validator.get_pump_fun_token_info(token_mint)
            if info:
                print(f"   Bonding Curve: {info['bonding_curve']}")
                print(f"   Data Length: {info['data_length']} bytes")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_pump_fun_validation())
