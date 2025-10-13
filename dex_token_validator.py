"""
Enhanced Executor Validation System
Validates tokens according to official documentation for each DEX type

This ensures proper routing and prevents execution failures by validating
token compatibility with each specific DEX before attempting trades.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import requests

logger = logging.getLogger(__name__)

# Official program IDs from documentation
DEX_PROGRAM_IDS = {
    # Pump.fun (verified correct program ID)
    "pumpfun": "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",
    
    # Jupiter (aggregator - works with most tokens)
    "jupiter": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
    
    # Raydium programs
    "raydium_v4": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "raydium_cpmm": "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK",
    "raydium_clmm": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
    
    # Orca programs
    "orca_whirlpool": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    "orca_v1": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
    
    # Phoenix
    "phoenix": "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY",
    
    # Meteora
    "meteora": "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi",
    
    # Standard token programs
    "spl_token": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "token_2022": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
}

# System tokens that should be rejected by specific DEXs
SYSTEM_TOKENS = {
    "So11111111111111111111111111111111111111112": "WSOL",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC", 
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT"
}

class DEXTokenValidator:
    """Validates tokens for specific DEX compatibility according to official docs"""
    
    def __init__(self, rpc_client: AsyncClient):
        self.rpc_client = rpc_client
    
    async def validate_pump_fun_token(self, token_mint: str) -> Dict[str, Any]:
        """
        Validate pump.fun token according to official pump.fun documentation
        
        Returns: {valid: bool, error: str, bonding_curve: str}
        """
        try:
            # Immediately reject system tokens
            if token_mint in SYSTEM_TOKENS:
                return {
                    "valid": False,
                    "error": f"{SYSTEM_TOKENS[token_mint]} is not a pump.fun token",
                    "reason": "system_token"
                }
            
            # Check bonding curve exists (official pump.fun pattern)
            pump_program = Pubkey.from_string(DEX_PROGRAM_IDS["pumpfun"])
            token_pubkey = Pubkey.from_string(token_mint)
            
            bonding_curve_pda, _ = Pubkey.find_program_address(
                [b"bonding-curve", bytes(token_pubkey)],
                pump_program
            )
            
            # Check if bonding curve account exists
            account_info = await self.rpc_client.get_account_info(bonding_curve_pda)
            
            if account_info.value is None:
                return {
                    "valid": False,
                    "error": f"No pump.fun bonding curve found for token",
                    "reason": "no_bonding_curve"
                }
            
            # Verify account is owned by pump.fun program
            if account_info.value.owner != pump_program:
                return {
                    "valid": False,
                    "error": f"Bonding curve not owned by pump.fun program",
                    "reason": "wrong_program_owner"
                }
            
            return {
                "valid": True,
                "bonding_curve": str(bonding_curve_pda),
                "reason": "valid_pumpfun_token"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Pump.fun validation error: {e}",
                "reason": "validation_error"
            }
    
    async def validate_jupiter_token(self, token_mint: str) -> Dict[str, Any]:
        """
        Validate token for Jupiter compatibility
        Jupiter works with most SPL tokens, so validation is less restrictive
        """
        try:
            # Jupiter can handle most tokens, but validate basic format
            token_pubkey = Pubkey.from_string(token_mint)
            
            # Check if token account exists
            account_info = await self.rpc_client.get_account_info(token_pubkey)
            
            if account_info.value is None:
                # For Jupiter, even if mint doesn't exist, it might be very new
                # Jupiter API will determine if routes exist
                return {
                    "valid": True,  # Let Jupiter API decide
                    "warning": "Token mint not found, Jupiter will validate routes",
                    "reason": "jupiter_api_validation"
                }
            
            # Check token program compatibility
            spl_token_program = Pubkey.from_string(DEX_PROGRAM_IDS["spl_token"])
            token_2022_program = Pubkey.from_string(DEX_PROGRAM_IDS["token_2022"])
            
            if account_info.value.owner == spl_token_program:
                return {
                    "valid": True,
                    "token_program": "spl-token",
                    "reason": "standard_spl_token"
                }
            elif account_info.value.owner == token_2022_program:
                return {
                    "valid": True,
                    "token_program": "token-2022",
                    "warning": "Token-2022 detected - limited DEX support",
                    "reason": "token_2022_format"
                }
            else:
                return {
                    "valid": True,  # Jupiter can often handle non-standard tokens
                    "warning": f"Unknown token program: {account_info.value.owner}",
                    "reason": "unknown_program_jupiter_fallback"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Jupiter validation error: {e}",
                "reason": "validation_error"
            }
    
    async def validate_raydium_token(self, token_mint: str) -> Dict[str, Any]:
        """
        Validate token for Raydium compatibility
        Requires SPL token with existing pools
        """
        try:
            # System tokens should go through Jupiter instead
            if token_mint in SYSTEM_TOKENS:
                return {
                    "valid": False,
                    "error": f"{SYSTEM_TOKENS[token_mint]} should use Jupiter, not Raydium",
                    "reason": "system_token_jupiter_preferred"
                }
            
            token_pubkey = Pubkey.from_string(token_mint)
            account_info = await self.rpc_client.get_account_info(token_pubkey)
            
            if account_info.value is None:
                return {
                    "valid": False,
                    "error": "Token mint not found",
                    "reason": "token_not_found"
                }
            
            # Raydium requires SPL tokens
            spl_token_program = Pubkey.from_string(DEX_PROGRAM_IDS["spl_token"])
            
            if account_info.value.owner != spl_token_program:
                return {
                    "valid": False,
                    "error": "Raydium requires SPL token format",
                    "reason": "not_spl_token"
                }
            
            return {
                "valid": True,
                "token_program": "spl-token", 
                "reason": "valid_spl_token"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Raydium validation error: {e}",
                "reason": "validation_error"
            }
    
    async def validate_orca_token(self, token_mint: str) -> Dict[str, Any]:
        """
        Validate token for Orca compatibility
        Similar to Raydium - requires SPL tokens
        """
        # Orca has similar requirements to Raydium
        return await self.validate_raydium_token(token_mint)
    
    async def validate_phoenix_token(self, token_mint: str) -> Dict[str, Any]:
        """
        Validate token for Phoenix (CLOB) compatibility
        Phoenix is more selective about tokens
        """
        try:
            # Phoenix CLOB is more restrictive
            if token_mint in SYSTEM_TOKENS:
                return {
                    "valid": True,  # Phoenix can handle major tokens
                    "token_type": SYSTEM_TOKENS[token_mint],
                    "reason": "major_token_supported"
                }
            
            token_pubkey = Pubkey.from_string(token_mint)
            account_info = await self.rpc_client.get_account_info(token_pubkey)
            
            if account_info.value is None:
                return {
                    "valid": False,
                    "error": "Phoenix requires established tokens",
                    "reason": "token_not_established"
                }
            
            # Phoenix works best with established SPL tokens
            spl_token_program = Pubkey.from_string(DEX_PROGRAM_IDS["spl_token"])
            
            if account_info.value.owner == spl_token_program:
                return {
                    "valid": True,
                    "token_program": "spl-token",
                    "reason": "established_spl_token"
                }
            else:
                return {
                    "valid": False,
                    "error": "Phoenix prefers established SPL tokens",
                    "reason": "not_established_spl"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": f"Phoenix validation error: {e}",
                "reason": "validation_error"
            }
    
    async def get_compatible_dexes(self, token_mint: str) -> List[str]:
        """
        Get list of compatible DEXes for a token
        
        Returns list of DEX names that can handle this token
        """
        compatible = []
        
        # Test each DEX
        validators = {
            "pumpfun": self.validate_pump_fun_token,
            "jupiter": self.validate_jupiter_token,
            "raydium": self.validate_raydium_token,
            "orca": self.validate_orca_token,
            "phoenix": self.validate_phoenix_token
        }
        
        for dex_name, validator in validators.items():
            try:
                result = await validator(token_mint)
                if result.get("valid", False):
                    compatible.append(dex_name)
            except Exception as e:
                logger.debug(f"Error validating {dex_name} for {token_mint[:8]}...: {e}")
        
        return compatible


# Integration functions for the wrapper system
async def validate_token_for_dex(rpc_client: AsyncClient, token_mint: str, dex_name: str) -> Dict[str, Any]:
    """
    Validate a token for a specific DEX
    
    Args:
        rpc_client: Solana RPC client
        token_mint: Token mint address
        dex_name: DEX name to validate for
        
    Returns:
        Validation result dictionary
    """
    validator = DEXTokenValidator(rpc_client)
    
    validation_map = {
        "pumpfun": validator.validate_pump_fun_token,
        "jupiter": validator.validate_jupiter_token,
        "raydium": validator.validate_raydium_token,
        "cpmm": validator.validate_raydium_token,  # CPMM uses Raydium validation
        "clmm": validator.validate_raydium_token,  # CLMM uses Raydium validation
        "orca": validator.validate_orca_token,
        "phoenix": validator.validate_phoenix_token
    }
    
    validator_func = validation_map.get(dex_name)
    if not validator_func:
        return {
            "valid": False,
            "error": f"Unknown DEX: {dex_name}",
            "reason": "unknown_dex"
        }
    
    return await validator_func(token_mint)


async def get_recommended_dexes_for_token(rpc_client: AsyncClient, token_mint: str) -> List[str]:
    """
    Get recommended DEXes for a token based on validation
    
    Returns list of DEX names in order of preference
    """
    validator = DEXTokenValidator(rpc_client)
    compatible = await validator.get_compatible_dexes(token_mint)
    
    # Prioritize based on token type
    if "pumpfun" in compatible:
        # Pump.fun tokens should prioritize pump.fun
        return ["pumpfun"] + [dex for dex in compatible if dex != "pumpfun"]
    else:
        # Non-pump.fun tokens prioritize Jupiter for universal routing
        if "jupiter" in compatible:
            return ["jupiter"] + [dex for dex in compatible if dex != "jupiter"]
        else:
            return compatible


# Test function
async def test_all_validations():
    """Test validation for all DEX types"""
    from env_keys import EnvKeys
    
    env_keys = EnvKeys()
    client = AsyncClient(env_keys.HELIUS_RPC_URL)
    validator = DEXTokenValidator(client)
    
    test_tokens = [
        ("So11111111111111111111111111111111111111112", "WSOL"),
        ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "USDC"),
        ("85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmn", "Test Token")
    ]
    
    dex_types = ["pumpfun", "jupiter", "raydium", "orca", "phoenix"]
    
    print("🧪 Testing DEX Token Validation System")
    print("=" * 60)
    
    for token_mint, description in test_tokens:
        print(f"\n🔍 Testing: {description}")
        print(f"   Token: {token_mint[:8]}...")
        
        for dex in dex_types:
            result = await validate_token_for_dex(client, token_mint, dex)
            status = "✅ VALID" if result.get("valid") else "❌ INVALID"
            reason = result.get("reason", "unknown")
            print(f"   {dex:10}: {status:10} ({reason})")
        
        # Get recommendations
        recommended = await get_recommended_dexes_for_token(client, token_mint)
        print(f"   Recommended: {recommended}")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(test_all_validations())
