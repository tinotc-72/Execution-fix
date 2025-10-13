"""
Direct Raydium CPMM Executor - No Jupiter dependency
Executes trades directly on Raydium's Constant Product Market Maker pools
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.instruction import Instruction, AccountMeta
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Confirmed
import struct

logger = logging.getLogger(__name__)

# Raydium Program IDs
RAYDIUM_AMM_PROGRAM = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
RENT_PROGRAM_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

# SOL mint
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

class DirectRaydiumExecutor:
    """Direct Raydium CPMM executor without Jupiter dependency"""
    
    def __init__(self, rpc_url: str):
        self.rpc_client = AsyncClient(rpc_url, commitment=Processed)
        
    async def buy_token(self, wallet: Keypair, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """Buy token directly via Raydium CPMM"""
        try:
            logger.info(f"🟣 Direct Raydium BUY: {amount_sol} SOL → {token_mint}")
            
            token_pubkey = Pubkey.from_string(token_mint)
            
            # Find Raydium pool for this token pair
            pool_info = await self.find_raydium_pool(SOL_MINT, token_pubkey)
            if not pool_info:
                logger.error("❌ No Raydium pool found for this token pair")
                return {"success": False, "signature": "", "error": "No Raydium pool found"}
            
            logger.info(f"✅ Found Raydium pool: {pool_info['amm_id']}")
            
            # Calculate swap amount
            lamports = int(amount_sol * 1e9)
            
            # Build swap instruction
            swap_instruction = await self.build_swap_instruction(
                wallet.pubkey(),
                pool_info,
                lamports,
                True,  # SOL -> Token
                kwargs.get('slippage_tolerance', 0.05)
            )
            
            if not swap_instruction:
                return {"success": False, "signature": "", "error": "Failed to build swap instruction"}
            
            # Create and send transaction
            signature = await self.send_transaction(wallet, [swap_instruction])
            
            if signature:
                logger.info(f"✅ Direct Raydium buy successful: {signature}")
                return {"success": True, "signature": signature, "dex": "Raydium-Direct"}
            else:
                return {"success": False, "signature": "", "error": "Transaction failed"}
                
        except Exception as e:
            logger.error(f"❌ Direct Raydium buy error: {e}")
            return {"success": False, "signature": "", "error": str(e)}
    
    async def sell_token(self, wallet: Keypair, token_mint: str, **kwargs) -> Dict[str, Any]:
        """Sell all tokens directly via Raydium CPMM"""
        try:
            logger.info(f"🟣 Direct Raydium SELL: {token_mint} → SOL")
            
            token_pubkey = Pubkey.from_string(token_mint)
            
            # Get token balance first
            token_balance = await self.get_token_balance(wallet.pubkey(), token_pubkey)
            if token_balance <= 0:
                logger.warning("⚠️ No tokens to sell")
                return {"success": False, "signature": "", "error": "No tokens to sell"}
            
            # Find Raydium pool
            pool_info = await self.find_raydium_pool(token_pubkey, SOL_MINT)
            if not pool_info:
                logger.error("❌ No Raydium pool found for this token pair")
                return {"success": False, "signature": "", "error": "No Raydium pool found"}
            
            # Build swap instruction
            swap_instruction = await self.build_swap_instruction(
                wallet.pubkey(),
                pool_info,
                token_balance,
                False,  # Token -> SOL
                kwargs.get('slippage_tolerance', 0.05)
            )
            
            if not swap_instruction:
                return {"success": False, "signature": "", "error": "Failed to build swap instruction"}
            
            # Send transaction
            signature = await self.send_transaction(wallet, [swap_instruction])
            
            if signature:
                logger.info(f"✅ Direct Raydium sell successful: {signature}")
                return {"success": True, "signature": signature, "dex": "Raydium-Direct"}
            else:
                return {"success": False, "signature": "", "error": "Transaction failed"}
                
        except Exception as e:
            logger.error(f"❌ Direct Raydium sell error: {e}")
            return {"success": False, "signature": "", "error": str(e)}
    
    async def find_raydium_pool(self, mint_a: Pubkey, mint_b: Pubkey) -> Optional[Dict[str, Any]]:
        """Find Raydium pool for token pair"""
        try:
            # Search for existing AMM pools
            # This is a simplified version - in production you'd use proper pool discovery
            
            # Get all Raydium AMM accounts
            amm_accounts = await self.rpc_client.get_program_accounts(
                RAYDIUM_AMM_PROGRAM,
                commitment=Processed
            )
            
            if not amm_accounts.value:
                return None
            
            # Parse AMM accounts to find matching pool
            for account in amm_accounts.value:
                try:
                    # Parse AMM account data (simplified)
                    data = account.account.data
                    if len(data) < 200:  # AMM accounts should be larger
                        continue
                    
                    # Extract mint addresses from AMM data
                    # This is a simplified parsing - real implementation would need proper struct parsing
                    coin_mint_offset = 40
                    pc_mint_offset = 72
                    
                    coin_mint_bytes = data[coin_mint_offset:coin_mint_offset + 32]
                    pc_mint_bytes = data[pc_mint_offset:pc_mint_offset + 32]
                    
                    coin_mint = Pubkey(coin_mint_bytes)
                    pc_mint = Pubkey(pc_mint_bytes)
                    
                    # Check if this pool matches our token pair
                    if ((coin_mint == mint_a and pc_mint == mint_b) or 
                        (coin_mint == mint_b and pc_mint == mint_a)):
                        
                        return {
                            'amm_id': account.pubkey,
                            'coin_mint': coin_mint,
                            'pc_mint': pc_mint,
                            'coin_vault_key': None,  # Would need to parse from data
                            'pc_vault_key': None,    # Would need to parse from data
                        }
                        
                except Exception as parse_error:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding Raydium pool: {e}")
            return None
    
    async def build_swap_instruction(self, user_wallet: Pubkey, pool_info: Dict[str, Any], 
                                   amount: int, is_buy: bool, slippage: float) -> Optional[Instruction]:
        """Build Raydium swap instruction"""
        try:
            # This is a simplified version - real implementation needs:
            # 1. Proper AMM data parsing
            # 2. Price calculation
            # 3. Slippage protection
            # 4. Associated Token Account creation if needed
            
            logger.warning("⚠️ Direct Raydium swap instruction building not fully implemented")
            logger.info("💡 This would require detailed AMM data parsing and instruction building")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error building swap instruction: {e}")
            return None
    
    async def get_token_balance(self, wallet: Pubkey, token_mint: Pubkey) -> int:
        """Get token balance"""
        try:
            from spl.token.instructions import get_associated_token_address
            
            token_account = get_associated_token_address(wallet, token_mint)
            account_info = await self.rpc_client.get_account_info(token_account)
            
            if not account_info.value:
                return 0
            
            # Parse token account data to get balance
            data = account_info.value.data
            balance = struct.unpack('<Q', data[64:72])[0]  # Balance is at offset 64
            
            return balance
            
        except Exception as e:
            logger.error(f"❌ Error getting token balance: {e}")
            return 0
    
    async def send_transaction(self, wallet: Keypair, instructions: list) -> Optional[str]:
        """Send transaction with instructions"""
        try:
            # Build transaction (simplified)
            # Real implementation would need proper transaction building
            logger.warning("⚠️ Direct transaction sending not fully implemented")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error sending transaction: {e}")
            return None
    
    async def close(self):
        """Close RPC client"""
        try:
            await self.rpc_client.close()
        except:
            pass
