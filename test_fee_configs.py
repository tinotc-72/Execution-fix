"""
Test Different Fee Config Accounts - Final Fix
"""

import asyncio
import logging
from typing import Optional
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

class FeeConfigTester:
    """
    Test different fee_config accounts to find the correct one
    """
    
    def __init__(self, env_keys: EnvKeys):
        self.env = env_keys
        self.keypair = Keypair.from_base58_string(env_keys.PHANTOM_PRIVATE_KEY)
        self.wallet_address = self.keypair.pubkey()
        
        # Core programs
        self.PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        # Protocol constants
        self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
        self.FEE_RECIPIENT = Pubkey.from_string("CebN5XLdTukHvfFhA7s8BPg2SB9JMLvjDFYUkLKJGQhU")
        
        # Different fee_config candidates
        self.fee_configs = {
            "PDA_fee": Pubkey.find_program_address([b"fee"], self.PUMP_FUN_PROGRAM)[0],
            "PDA_fee_config": Pubkey.find_program_address([b"fee_config"], self.PUMP_FUN_PROGRAM)[0], 
            "global_account": self.GLOBAL_ACCOUNT,
            "fee_recipient": self.FEE_RECIPIENT,
            "event_authority": self.EVENT_AUTHORITY
        }
        
        # MEV settings
        self.PRIORITY_FEE = 500_000
        
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
    
    def derive_bonding_curve(self, mint: Pubkey) -> Pubkey:
        """Derive bonding curve"""
        return Pubkey.find_program_address(
            [b"bonding-curve", bytes(mint)],
            self.PUMP_FUN_PROGRAM
        )[0]
    
    async def test_fee_config(self, config_name: str, fee_config: Pubkey, mint_address: str, sol_amount: float) -> bool:
        """
        Test a specific fee_config account
        """
        try:
            logger.info(f"🧪 Testing fee_config: {config_name} = {fee_config}")
            
            mint_pubkey = Pubkey.from_string(mint_address)
            sol_lamports = int(sol_amount * 1_000_000_000)
            
            # Derive all required accounts
            bonding_curve = self.derive_bonding_curve(mint_pubkey)
            associated_bonding_curve = self.derive_associated_token_address(bonding_curve, mint_pubkey)
            user_token_account = self.derive_associated_token_address(self.wallet_address, mint_pubkey)
            
            # Buy instruction data
            buy_discriminator = bytes.fromhex("66063d1201daebea")
            max_sol_cost = int(sol_lamports * 1.06)
            instruction_data = buy_discriminator + struct.pack('<QQ', sol_lamports, max_sol_cost)
            
            # Account structure with this specific fee_config
            account_metas = [
                AccountMeta(pubkey=self.GLOBAL_ACCOUNT, is_signer=False, is_writable=False),           # Global
                AccountMeta(pubkey=fee_config, is_signer=False, is_writable=False),                   # Fee config (TEST)
                AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),                  # Mint
                AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),                 # Bonding curve
                AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),      # Associated bonding curve
                AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),            # User token account
                AccountMeta(pubkey=self.wallet_address, is_signer=True, is_writable=True),            # User (signer)
                AccountMeta(pubkey=self.SYSTEM_PROGRAM, is_signer=False, is_writable=False),          # System program
                AccountMeta(pubkey=self.TOKEN_PROGRAM, is_signer=False, is_writable=False),           # Token program
                AccountMeta(pubkey=self.RENT_SYSVAR, is_signer=False, is_writable=False),             # Rent sysvar
                AccountMeta(pubkey=self.EVENT_AUTHORITY, is_signer=False, is_writable=False),         # Event authority
                AccountMeta(pubkey=self.PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),        # Pump.fun program
                AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM, is_signer=False, is_writable=False), # ATA program
                AccountMeta(pubkey=self.FEE_RECIPIENT, is_signer=False, is_writable=True),            # Fee recipient
            ]
            
            # Create instruction
            buy_instruction = Instruction(
                program_id=self.PUMP_FUN_PROGRAM,
                accounts=account_metas,
                data=instruction_data
            )
            
            # Get blockhash
            recent_blockhash = await self.get_recent_blockhash()
            
            # Create transaction with MEV priority
            instructions = [
                set_compute_unit_price(self.PRIORITY_FEE),
                set_compute_unit_limit(400_000),
                buy_instruction
            ]
            
            message = MessageV0.try_compile(
                payer=self.wallet_address,
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            
            # Submit transaction
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
                    logger.info(f"🎉 SUCCESS with {config_name}! Signature: {signature}")
                    return True
                else:
                    error = result.get('error', {})
                    error_msg = error.get('message', str(error))
                    
                    if "AccountNotEnoughKeys" in error_msg and "fee_config" in error_msg:
                        logger.warning(f"❌ {config_name}: Still missing fee_config account")
                    elif "custom program error" in error_msg:
                        logger.warning(f"❌ {config_name}: Program error - {error_msg}")
                    else:
                        logger.warning(f"❌ {config_name}: Other error - {error_msg}")
                    
                    return False
                    
        except Exception as e:
            logger.error(f"❌ {config_name} test error: {e}")
            return False
    
    async def test_all_configs(self, mint_address: str, sol_amount: float):
        """Test all fee_config candidates"""
        
        logger.info(f"🚀 TESTING ALL FEE CONFIG CANDIDATES")
        logger.info(f"   Mint: {mint_address}")
        logger.info(f"   Amount: {sol_amount} SOL")
        logger.info("=" * 60)
        
        for config_name, fee_config in self.fee_configs.items():
            success = await self.test_fee_config(config_name, fee_config, mint_address, sol_amount)
            
            if success:
                logger.info(f"🏆 WINNER: {config_name} = {fee_config}")
                return config_name, fee_config
            
            await asyncio.sleep(2)  # Small delay between tests
        
        logger.error("❌ No working fee_config found!")
        return None, None

async def run_fee_config_tests():
    """Run comprehensive fee_config tests"""
    
    env = EnvKeys()
    tester = FeeConfigTester(env)
    
    # Test parameters
    test_mint = "5rPVwsZ4KpPZ2Zt4FmYfMJuYe8PWRF2rXrBy2oG5pump"
    test_amount = 0.001
    
    # Test all configurations
    winner_name, winner_config = await tester.test_all_configs(test_mint, test_amount)
    
    if winner_config:
        print()
        print("🎯 FINAL RESULT:")
        print("=" * 60)
        print(f"✅ Working fee_config: {winner_name}")
        print(f"✅ Address: {winner_config}")
        print("🚀 MEV bot protocol fix COMPLETE!")
    else:
        print()
        print("❌ No working fee_config found. Need to investigate further.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_fee_config_tests())
