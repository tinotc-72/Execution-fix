"""
Modern MEV PumpFun Executor - FIXED with Jupiter Router
Based on complete_mev_bot.py architecture that uses Jupiter Router routing
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Tuple
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.system_program import create_account, CreateAccountParams
from solders.hash import Hash
import httpx
from base58 import b58decode, b58encode
import struct

from env_keys import EnvKeys

logger = logging.getLogger(__name__)

class ModernMEVPumpFunExecutor:

    async def execute_sell(
        self,
        mint_address: str,
        token_amount: int
    ) -> Optional[str]:
        """
        Execute MEV sell using Jupiter Router, always bundling ATA creation with sell if needed.
        """
        try:
            logger.info(f"🚀 Starting modern MEV sell: {token_amount} tokens for {mint_address}")
            mint_pubkey = Pubkey.from_string(mint_address)
            # Derive accounts dynamically
            accounts = self.derive_pump_accounts(mint_pubkey)
            # Get recent blockhash
            recent_blockhash = await self.get_recent_blockhash()
            # --- ATA check and bundle logic ---
            user_token_account = self.derive_associated_token_address(self.wallet_address, mint_pubkey)
            ata_exists = False
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getAccountInfo",
                        "params": [str(user_token_account), {"encoding": "base64"}]
                    }
                )
                data = resp.json()
                ata_exists = data.get("result", {}).get("value") is not None

            instructions = [
                *self.create_priority_fee_instructions(self.SELL_PRIORITY_FEE),
            ]
            if not ata_exists:
                logger.info(f"🟡 ATA does not exist, bundling ATA creation with sell.")
                instructions.append(self.create_ata_instruction(mint_pubkey))
            else:
                logger.info(f"🟢 ATA exists, no need to create.")
            instructions.append(self.create_modern_sell_instruction(accounts, token_amount))

            # Create transaction
            message = MessageV0.try_compile(
                payer=self.wallet_address,
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            transaction = VersionedTransaction(message, [self.keypair])
            # Send transaction
            async with httpx.AsyncClient(timeout=30.0) as client:
                serialized = b58encode(bytes(transaction)).decode()
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            serialized,
                            {
                                "encoding": "base58",
                                "skipPreflight": True,
                                "preflightCommitment": "confirmed"
                            }
                        ]
                    }
                )
                result = response.json()
                if 'result' in result:
                    signature = result['result']
                    logger.info(f"✅ SELL submitted via Jupiter Router: {signature}")
                    return signature
                else:
                    logger.error(f"❌ Sell failed: {result}")
                    return None
        except Exception as e:
            logger.error(f"❌ Sell error: {e}")
            return None

    def create_modern_sell_instruction(
        self,
        accounts: Dict[str, Pubkey],
        token_amount: int
    ) -> Instruction:
        """
        Create modern sell instruction using Jupiter Router (FIXED)
        """
        # Jupiter Router instruction data for Pump.fun routing (SELL)
        # NOTE: This is a placeholder. You must update this with the correct instruction data for a sell.
        instruction_data = bytes.fromhex("01bdda4598000000004586f554dc040000")
        account_metas = [
            AccountMeta(pubkey=self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.FEE_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts['mint'], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts['bonding_curve'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['associated_bonding_curve'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['user_token_account'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['user'], is_signer=True, is_writable=True),
            AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.RENT_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.EVENT_AUTHORITY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.FEE_RECIPIENT_WRITABLE, is_signer=False, is_writable=True),            # Fee recipient (as writable, fixes error 3005)
        ]
        return Instruction(
            program_id=self.JUPITER_ROUTER_PROGRAM,
            accounts=account_metas,
            data=instruction_data
        )
    """
    Modern MEV-optimized PumpFun executor using Jupiter Router routing (FIXED)
    """
    
    def __init__(self):
        """Initialize the modern MEV PumpFun executor"""
        self.env = EnvKeys()
        
        # Load keypair
        try:
            if hasattr(self.env, 'PHANTOM_PRIVATE_KEY') and self.env.PHANTOM_PRIVATE_KEY:
                secret_bytes = b58decode(self.env.PHANTOM_PRIVATE_KEY)
                self.keypair = Keypair.from_bytes(secret_bytes)
                self.wallet_address = self.keypair.pubkey()
                logger.info(f"✅ Loaded wallet: {self.wallet_address}")
            else:
                raise ValueError("PHANTOM_PRIVATE_KEY not found in environment")
        except Exception as e:
            logger.error(f"❌ Failed to load keypair: {e}")
            raise
        
        # Program IDs - FIXED: Use Jupiter Router instead of direct Pump.fun calls
        self.JUPITER_ROUTER_PROGRAM = Pubkey.from_string("F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq")
        self.PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")  # Reference only
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_PROGRAM = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        # Additional required accounts for modern protocol
        self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
    # Protocol compliance: fee_recipient is now the fee_program (for account[1])
    self.FEE_PROGRAM = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
    # If a writable fee recipient is still needed at the end, keep the old address as fee_recipient_writable
    self.FEE_RECIPIENT_WRITABLE = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV1T6NVswCLPVXdHy")
    self.FEE_RECIPIENT = Pubkey.from_string("CebN5XLdTukHvfFhA7s8BPg2SB9JMLvjDFYUkLKJGQhU")  # Legacy, do not use for protocol
        
        # Additional programs often used in Pump.fun transactions
        self.TOKEN_PROGRAM_2022 = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")
        self.MEMO_PROGRAM = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")
        
        # MEV priority fees (higher than standard)
        self.BUY_PRIORITY_FEE = 500_000  # 500k μ-lamports
        self.SELL_PRIORITY_FEE = 750_000  # 750k μ-lamports
        
    async def get_recent_blockhash(self) -> Hash:
        """Get recent blockhash"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.env.HELIUS_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "confirmed"}]
                }
            )
            
            data = response.json()
            if 'result' in data:
                blockhash_str = data['result']['value']['blockhash']
                return Hash.from_string(blockhash_str)
            
            raise Exception("Failed to get blockhash")
    
    def derive_associated_token_address(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
        """Derive associated token address"""
        seeds = [
            bytes(owner),
            bytes(self.TOKEN_PROGRAM),
            bytes(mint)
        ]
        
        return Pubkey.find_program_address(
            seeds,
            self.ASSOCIATED_TOKEN_PROGRAM
        )[0]
    
    def derive_pump_accounts(self, mint: Pubkey) -> Dict[str, Pubkey]:
        """Derive all Pump.fun accounts for a given mint"""
        
        # Bonding curve account
        bonding_curve_seeds = [b"bonding-curve", bytes(mint)]
        bonding_curve = Pubkey.find_program_address(
            bonding_curve_seeds,
            self.PUMP_FUN_PROGRAM
        )[0]
        
        # Associated bonding curve (token account for bonding curve)
        associated_bonding_curve = self.derive_associated_token_address(
            bonding_curve,
            mint
        )
        
        # User token account
        user_token_account = self.derive_associated_token_address(
            self.wallet_address,
            mint
        )
        
        return {
            'mint': mint,
            'bonding_curve': bonding_curve,
            'associated_bonding_curve': associated_bonding_curve,
            'user_token_account': user_token_account,
            'user': self.wallet_address
        }

    def create_ata_instruction(self, mint: Pubkey) -> Instruction:
        """Create Associated Token Account instruction"""
        return Instruction(
            program_id=self.ASSOCIATED_TOKEN_PROGRAM,
            accounts=[
                AccountMeta(pubkey=self.wallet_address, is_signer=True, is_writable=True),
                AccountMeta(pubkey=self.derive_associated_token_address(self.wallet_address, mint), is_signer=False, is_writable=True),
                AccountMeta(pubkey=self.wallet_address, is_signer=False, is_writable=False),
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
            ],
            data=bytes()
        )

    def create_priority_fee_instructions(self, priority_fee: int) -> List[Instruction]:
        """Create priority fee instructions"""
        return [
            set_compute_unit_limit(400_000),
            set_compute_unit_price(priority_fee)
        ]
    
    def create_modern_buy_instruction(
        self, 
        accounts: Dict[str, Pubkey], 
        sol_amount_lamports: int
    ) -> Instruction:
        """
        Create modern buy instruction using Jupiter Router (FIXED)
        """
        # Jupiter Router instruction data for Pump.fun routing
        instruction_data = bytes.fromhex("00bdda4598000000004586f554dc040000")
        
        # Account metas for Jupiter Router -> Pump.fun routing
        account_metas = [
            AccountMeta(pubkey=self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),                    # 0. Global
            AccountMeta(pubkey=self.FEE_PROGRAM, is_signer=False, is_writable=False),                      # 1. Fee program (Anchor IDL compliance)
            AccountMeta(pubkey=accounts['mint'], is_signer=False, is_writable=False),                      # 2. Mint
            AccountMeta(pubkey=accounts['bonding_curve'], is_signer=False, is_writable=True),              # 3. Bonding Curve
            AccountMeta(pubkey=accounts['associated_bonding_curve'], is_signer=False, is_writable=True),   # 4. Associated Bonding Curve
            AccountMeta(pubkey=accounts['user_token_account'], is_signer=False, is_writable=True),         # 5. User Token Account
            AccountMeta(pubkey=accounts['user'], is_signer=True, is_writable=True),                        # 6. User (signer)
            AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),                   # 7. System Program
            AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),                    # 8. Token Program
            AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM, is_signer=False, is_writable=False),         # 9. Associated Token Program
            AccountMeta(pubkey=self.RENT_PROGRAM, is_signer=False, is_writable=False),                     # 10. Rent Sysvar
            AccountMeta(pubkey=self.EVENT_AUTHORITY, is_signer=False, is_writable=False),                  # 11. Event Authority
            AccountMeta(pubkey=self.PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),                 # 12. Pump.fun Program
            AccountMeta(pubkey=self.FEE_RECIPIENT_WRITABLE, is_signer=False, is_writable=True),            # 13. Fee recipient (as writable, fixes error 3005)
        ]
        return Instruction(
            program_id=self.JUPITER_ROUTER_PROGRAM,  # FIXED: Use Jupiter Router
            accounts=account_metas,
            data=instruction_data
        )
    
    async def execute_buy(
        self, 
        mint_address: str, 
        sol_amount: float
    ) -> Optional[str]:
        """
        Execute MEV buy using Jupiter Router (FIXED)
        """
        try:
            logger.info(f"🚀 Starting modern MEV buy: {sol_amount} SOL for {mint_address}")
            
            mint_pubkey = Pubkey.from_string(mint_address)
            sol_lamports = int(sol_amount * 1_000_000_000)
            
            # Derive accounts dynamically
            accounts = self.derive_pump_accounts(mint_pubkey)
            
            # Get recent blockhash
            recent_blockhash = await self.get_recent_blockhash()
            
            # Create instructions with Jupiter Router routing
            # --- ATA check and bundle logic ---
            user_token_account = self.get_associated_token_address(mint_pubkey, self.wallet_address)
            ata_exists = False
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getAccountInfo",
                        "params": [str(user_token_account), {"encoding": "base64"}]
                    }
                )
                data = resp.json()
                ata_exists = data.get("result", {}).get("value") is not None

            instructions = [
                *self.create_priority_fee_instructions(self.BUY_PRIORITY_FEE),
            ]
            if not ata_exists:
                logger.info(f"🟡 ATA does not exist, bundling ATA creation with buy.")
                instructions.append(self.create_ata_instruction(mint_pubkey))
            else:
                logger.info(f"🟢 ATA exists, no need to create.")
            instructions.append(self.create_modern_buy_instruction(accounts, sol_lamports))
            
            # Create transaction
            message = MessageV0.try_compile(
                payer=self.wallet_address,
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            
            # Send transaction
            async with httpx.AsyncClient(timeout=30.0) as client:
                serialized = b58encode(bytes(transaction)).decode()
                
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            serialized,
                            {
                                "encoding": "base58",
                                "skipPreflight": True,
                                "preflightCommitment": "confirmed"
                            }
                        ]
                    }
                )
                
                result = response.json()
                
                if 'result' in result:
                    signature = result['result']
                    logger.info(f"✅ BUY submitted via Jupiter Router: {signature}")
                    return signature
                else:
                    logger.error(f"❌ Buy failed: {result}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Buy error: {e}")
            return None
    
    async def execute_copy_buy(self, detected_tx: Dict[str, Any]) -> Optional[str]:
        """Execute copy trade buy"""
        try:
            mint_address = detected_tx.get('mint_address')
            sol_amount = detected_tx.get('sol_amount', 0.1)  # Default 0.1 SOL
            
            if not mint_address:
                logger.error("❌ No mint address in detected transaction")
                return None
            
            return await self.execute_buy(mint_address, sol_amount)
            
        except Exception as e:
            logger.error(f"❌ Copy buy error: {e}")
            return None

# Factory function for easy usage
def create_modern_mev_executor() -> ModernMEVPumpFunExecutor:
    """Create and return a modern MEV executor instance"""
    return ModernMEVPumpFunExecutor()

# Test function
async def test_executor():
    """Test the modern MEV executor"""
    executor = create_modern_mev_executor()
    
    # Test with a known token (replace with actual test token)
    test_mint = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"  # Example mint
    
    signature = await executor.execute_buy(test_mint, 0.01)  # Test with 0.01 SOL
    
    if signature:
        logger.info(f"✅ Test successful: {signature}")
    else:
        logger.error("❌ Test failed")

if __name__ == "__main__":
    asyncio.run(test_executor())
