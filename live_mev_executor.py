"""
Fixed MEV Executor for Live Testing - Using Working Account Structure
Based on our successful tests, removing problematic accounts
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
from solders.hash import Hash
import httpx
from base58 import b58encode
import struct

from env_keys import EnvKeys

logger = logging.getLogger(__name__)

class LiveMEVExecutor:
    """
    Live MEV executor using the working account structure from our tests
    """
    
    def __init__(self, env_keys: EnvKeys):
        self.env = env_keys
        try:
            self.keypair = Keypair.from_base58_string(env_keys.PHANTOM_PRIVATE_KEY)
            self.wallet_address = self.keypair.pubkey()
            logger.info(f"✅ Wallet loaded: {self.wallet_address}")
        except Exception as e:
            logger.error(f"❌ Failed to load keypair: {e}")
            raise
        
        # Core programs - FIXED: Use Jupiter Router instead of direct Pump.fun
        try:
            self.JUPITER_ROUTER_PROGRAM = Pubkey.from_string("F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq")
            self.PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")  # Reference only
            self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
            self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
            self.RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
            logger.info("✅ Core programs loaded with Jupiter Router")
        except Exception as e:
            logger.error(f"❌ Failed to load core programs: {e}")
            raise
        
        # Protocol constants
        try:
            self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
            self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
            self.FEE_RECIPIENT = Pubkey.from_string("CebN5XLdTukHvfFhA7s8BPg2SB9JMLvjDFYUkLKJGQhU")
            logger.info("✅ Protocol accounts loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load protocol accounts: {e}")
            raise
        
        # MEV priority fees
        self.BUY_PRIORITY_FEE = 500_000
        self.SELL_PRIORITY_FEE = 750_000
        
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
    
    def derive_pump_accounts(self, mint_address) -> Dict[str, Pubkey]:
        """Derive Pump.fun accounts dynamically"""
        if isinstance(mint_address, str):
            mint_pubkey = Pubkey.from_string(mint_address)
        else:
            mint_pubkey = mint_address
            
        # Bonding curve
        bonding_curve = Pubkey.find_program_address(
            [b"bonding-curve", bytes(mint_pubkey)],
            self.PUMP_FUN_PROGRAM
        )[0]
        
        # Associated bonding curve 
        associated_bonding_curve = self.derive_associated_token_address(
            bonding_curve, mint_pubkey
        )
        
        # User's associated token account
        user_token_account = self.derive_associated_token_address(
            self.wallet_address, mint_pubkey
        )
        
        return {
            'mint': mint_pubkey,
            'bonding_curve': bonding_curve,
            'associated_bonding_curve': associated_bonding_curve,
            'user_token_account': user_token_account,
            'user': self.wallet_address
        }
    
    async def get_token_balance(self, token_account: Pubkey) -> int:
        """Get token balance for account"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTokenAccountBalance",
                        "params": [str(token_account)]
                    }
                )
                
                data = response.json()
                if 'result' in data and data['result']['value']:
                    return int(data['result']['value']['amount'])
                return 0
        except:
            return 0
    
    def create_buy_instruction(self, accounts: Dict[str, Pubkey], sol_amount_lamports: int) -> Instruction:
        """Create buy instruction using Jupiter Router (FIXED)"""
        
        # Jupiter Router instruction data for Pump.fun routing
        instruction_data = bytes.fromhex("00bdda4598000000004586f554dc040000")
        
        # Account metas for Jupiter Router -> Pump.fun routing
        account_metas = [
            AccountMeta(pubkey=self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.FEE_RECIPIENT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts['mint'], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts['bonding_curve'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['associated_bonding_curve'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['user_token_account'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['user'], is_signer=True, is_writable=True),
            AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.RENT_SYSVAR, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.EVENT_AUTHORITY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),
        ]
        
        return Instruction(
            program_id=self.JUPITER_ROUTER_PROGRAM,  # FIXED: Use Jupiter Router
            accounts=account_metas,
            data=instruction_data
        )
    
    def create_sell_instruction(self, accounts: Dict[str, Pubkey], token_amount: int) -> Instruction:
        """Create sell instruction with simplified account structure"""
        
        # Sell discriminator
        discriminator = bytes.fromhex("33e685a4017f83ad")
        min_sol_output = int(token_amount * 0.94)
        instruction_data = discriminator + struct.pack('<QQ', token_amount, min_sol_output)
        
        # Same account structure as buy
        account_metas = [
            AccountMeta(pubkey=self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts['mint'], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts['bonding_curve'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['associated_bonding_curve'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['user_token_account'], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts['user'], is_signer=True, is_writable=True),
            AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.RENT_SYSVAR, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.EVENT_AUTHORITY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.FEE_RECIPIENT, is_signer=False, is_writable=True),
        ]
        
        return Instruction(
            program_id=self.PUMP_FUN_PROGRAM,
            accounts=account_metas,
            data=instruction_data
        )
    
    async def execute_buy(self, mint_address: str, sol_amount: float) -> Optional[str]:
        """Execute live buy"""
        try:
            logger.info(f"🚀 LIVE BUY: {sol_amount} SOL for {mint_address}")
            
            sol_lamports = int(sol_amount * 1_000_000_000)
            accounts = self.derive_pump_accounts(mint_address)
            
            recent_blockhash = await self.get_recent_blockhash()
            
            instructions = [
                set_compute_unit_price(self.BUY_PRIORITY_FEE),
                set_compute_unit_limit(400_000),
                self.create_buy_instruction(accounts, sol_lamports)
            ]
            
            message = MessageV0.try_compile(
                payer=self.wallet_address,
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            
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
                                "skipPreflight": False,
                                "preflightCommitment": "confirmed"
                            }
                        ]
                    }
                )
                
                result = response.json()
                
                if 'result' in result:
                    signature = result['result']
                    logger.info(f"✅ BUY submitted: {signature}")
                    return signature
                else:
                    error = result.get('error', {})
                    logger.error(f"❌ BUY failed: {error}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ BUY error: {e}")
            return None
    
    async def execute_sell(self, mint_address: str, percentage: float = 100.0) -> Optional[str]:
        """Execute live sell"""
        try:
            logger.info(f"🚀 LIVE SELL: {percentage}% of {mint_address}")
            
            accounts = self.derive_pump_accounts(mint_address)
            
            # Get token balance
            token_balance = await self.get_token_balance(accounts['user_token_account'])
            if token_balance == 0:
                logger.warning("❌ No tokens to sell")
                return None
            
            sell_amount = int(token_balance * (percentage / 100.0))
            
            recent_blockhash = await self.get_recent_blockhash()
            
            instructions = [
                set_compute_unit_price(self.SELL_PRIORITY_FEE),
                set_compute_unit_limit(400_000),
                self.create_sell_instruction(accounts, sell_amount)
            ]
            
            message = MessageV0.try_compile(
                payer=self.wallet_address,
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            
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
                                "skipPreflight": False,
                                "preflightCommitment": "confirmed"
                            }
                        ]
                    }
                )
                
                result = response.json()
                
                if 'result' in result:
                    signature = result['result']
                    logger.info(f"✅ SELL submitted: {signature}")
                    return signature
                else:
                    error = result.get('error', {})
                    logger.error(f"❌ SELL failed: {error}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ SELL error: {e}")
            return None
