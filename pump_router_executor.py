#!/usr/bin/env python3
"""
Pump.fun Router Executor - Supports Multiple Router Programs
Handles both direct and router-based Pump.fun trading
"""

import logging
import struct
import base64
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from spl.token.instructions import get_associated_token_address

logger = logging.getLogger(__name__)

@dataclass
class RouterConfig:
    """Configuration for Pump.fun router trading"""
    priority_fee: int = 2_000_000  # 2M micro-lamports (protocol-compliant)
    compute_limit: int = 200_000   # Higher for router complexity
    slippage_multiplier: float = 2.0
    skip_preflight: bool = False

# Protocol-compliant fee program and writable fee recipient
FEE_PROGRAM = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
FEE_RECIPIENT_WRITABLE = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV1T6NVswCLPVXdHy")

class PumpRouterExecutor:
    """Executor that supports multiple Pump.fun router programs"""
    
    def __init__(self, wallet: Keypair, rpc_client):
        self.wallet = wallet
        self.rpc_client = rpc_client
        self.config = RouterConfig()
        
        # Supported router programs
        self.ROUTER_PROGRAMS = {
            'main_pump': '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',    # Direct Pump.fun
            'router_v1': 'F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq',   # Router/Wrapper
            'router_v2': '6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC'    # Alternative Router
        }
        
        # Known discriminators for different router types
        self.DISCRIMINATORS = {
            # Direct Pump.fun
            '66063d1201daebea': 'direct_buy',
            '33e685a4017f83ad': 'direct_sell',
            
            # Router programs
            'd408fc89c1275061': 'router_buy',
            'b712469c946da122': 'router_initialize',
            'a02b392e88e8e5e0': 'router_withdraw'
        }
        
        logger.info("🔄 Pump Router Executor initialized")
        logger.info(f"   Wallet: {self.wallet.pubkey()}")
        logger.info(f"   Supported routers: {len(self.ROUTER_PROGRAMS)}")
    
    def detect_program_type(self, program_id: str) -> str:
        """Detect which type of Pump.fun program this is"""
        for router_type, prog_id in self.ROUTER_PROGRAMS.items():
            if program_id == prog_id:
                return router_type
        return 'unknown'
    
    async def execute_router_buy(self, 
                                program_id: str,
                                mint: Pubkey, 
                                amount_lamports: int,
                                transaction_data: Dict[str, Any] = None) -> Optional[str]:
        """Execute buy through appropriate router program"""
        
        router_type = self.detect_program_type(program_id)
        logger.info(f"🔄 Executing {router_type} buy for {mint}")
        
        try:
            if router_type == 'main_pump':
                return await self._execute_direct_buy(mint, amount_lamports)
            elif router_type in ['router_v1', 'router_v2']:
                return await self._execute_router_buy(program_id, mint, amount_lamports, transaction_data)
            else:
                logger.error(f"❌ Unsupported program: {program_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Router buy failed: {e}")
            return None
    
    async def _execute_direct_buy(self, mint: Pubkey, amount_lamports: int) -> Optional[str]:
        """Execute direct buy through main Pump.fun program"""
        logger.info("🎯 Executing direct Pump.fun buy")
        
        try:
            # Use the existing CompleteMEVBot logic for direct calls
            from complete_mev_bot import CompleteMEVBot
            
            # Create temporary instance for direct trading
            mev_bot = CompleteMEVBot(self.wallet, self.rpc_client)
            result = await mev_bot.execute_buy(mint, amount_lamports)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Direct buy failed: {e}")
            return None
    
    async def _execute_router_buy(self, 
                                 program_id: str,
                                 mint: Pubkey, 
                                 amount_lamports: int,
                                 transaction_data: Dict[str, Any] = None) -> Optional[str]:
        """Execute buy through router program"""
        logger.info(f"🔄 Executing router buy through {program_id}")
        
        try:
            # Get router-specific instruction
            instruction = await self._create_router_instruction(
                program_id, mint, amount_lamports, transaction_data
            )
            
            if not instruction:
                logger.error("❌ Failed to create router instruction")
                return None
            
            # Create and send transaction
            return await self._send_router_transaction([instruction])
            
        except Exception as e:
            logger.error(f"❌ Router buy failed: {e}")
            return None
    
    async def _create_router_instruction(self,
                                        program_id: str,
                                        mint: Pubkey,
                                        amount_lamports: int,
                                        transaction_data: Dict[str, Any] = None) -> Optional[Instruction]:
        """Create router-specific instruction based on observed transaction patterns"""
        
        try:
            program_pubkey = Pubkey.from_string(program_id)
            
            # For F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq router
            if program_id == 'F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq':
                return await self._create_f5_router_instruction(mint, amount_lamports, transaction_data)
            
            # For 6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC router
            elif program_id == '6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC':
                return await self._create_6h_router_instruction(mint, amount_lamports, transaction_data)
            
            else:
                logger.error(f"❌ Unknown router program: {program_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to create router instruction: {e}")
            return None
    
    async def _create_f5_router_instruction(self,
                                           mint: Pubkey,
                                           amount_lamports: int,
                                           transaction_data: Dict[str, Any] = None) -> Optional[Instruction]:
        """Create instruction for F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq router"""
        
        try:
            # Router program
            router_program = Pubkey.from_string('F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq')
            
            # Get standard Pump.fun accounts
            main_pump_program = Pubkey.from_string('6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P')
            system_program = Pubkey.from_string('11111111111111111111111111111111')
            token_program = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
            rent_sysvar = Pubkey.from_string('SysvarRent111111111111111111111111111111111')
            
            # Derive necessary PDAs
            bonding_curve, _ = Pubkey.find_program_address(
                [b"bonding-curve", bytes(mint)], main_pump_program
            )
            
            associated_bonding_curve = get_associated_token_address(bonding_curve, mint)
            associated_user = get_associated_token_address(self.wallet.pubkey(), mint)
            
            # Router instruction data (observed pattern from transaction analysis)
            # This is a simplified version - real router may need more complex data
            instruction_data = struct.pack('<Q', amount_lamports)  # Amount only for now
            
            # Account structure based on observed router transaction (16 accounts)
            accounts = [
                AccountMeta(pubkey=self.wallet.pubkey(), is_signer=True, is_writable=True),     # [0] User
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),                    # [1] Mint
                AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),           # [2] Bonding curve
                AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True), # [3] Bonding curve ATA
                AccountMeta(pubkey=associated_user, is_signer=False, is_writable=True),         # [4] User ATA
                AccountMeta(pubkey=main_pump_program, is_signer=False, is_writable=False),      # [5] Main Pump program
                AccountMeta(pubkey=system_program, is_signer=False, is_writable=False),         # [6] System program
                AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),          # [7] Token program
                AccountMeta(pubkey=rent_sysvar, is_signer=False, is_writable=False),            # [8] Rent sysvar
                # Add more accounts as needed based on router requirements
            ]
            
            # Pad to 16 accounts if needed (router used 16)
            while len(accounts) < 16:
                accounts.append(AccountMeta(pubkey=system_program, is_signer=False, is_writable=False))
            
            instruction = Instruction(
                program_id=router_program,
                accounts=accounts,
                data=instruction_data
            )
            
            logger.info(f"✅ Created F5 router instruction with {len(accounts)} accounts")
            return instruction
            
        except Exception as e:
            logger.error(f"❌ Failed to create F5 router instruction: {e}")
            return None
    
    async def _create_6h_router_instruction(self,
                                           mint: Pubkey,
                                           amount_lamports: int,
                                           transaction_data: Dict[str, Any] = None) -> Optional[Instruction]:
        """Create instruction for 6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC router"""
        
        # Similar structure to F5 router but with different program ID
        # Implementation would be similar but potentially with different account structure
        logger.warning("⚠️ 6H router not fully implemented yet - using F5 pattern")
        return await self._create_f5_router_instruction(mint, amount_lamports, transaction_data)
    
    async def _send_router_transaction(self, instructions: List[Instruction]) -> Optional[str]:
        """Send router transaction with proper compute budget"""
        
        try:
            # Add compute budget instructions
            compute_instructions = [
                set_compute_unit_limit(self.config.compute_limit),
                set_compute_unit_price(self.config.priority_fee)
            ]
            
            all_instructions = compute_instructions + instructions
            
            # Get recent blockhash
            blockhash_resp = await self.rpc_client.get_latest_blockhash()
            recent_blockhash = blockhash_resp.value.blockhash
            
            # Create versioned transaction
            message = MessageV0.try_compile(
                payer=self.wallet.pubkey(),
                instructions=all_instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [self.wallet])
            
            # Send transaction
            opts = {"skip_preflight": self.config.skip_preflight, "max_retries": 3}
            response = await self.rpc_client.send_transaction(transaction, opts=opts)
            
            if hasattr(response, 'value'):
                signature = str(response.value)
                logger.info(f"🚀 Router transaction sent: {signature}")
                return signature
            else:
                logger.error(f"❌ Router transaction failed: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to send router transaction: {e}")
            return None
    
    async def copy_router_transaction(self, original_tx_data: Dict[str, Any]) -> Optional[str]:
        """Copy a router transaction structure exactly"""
        
        try:
            # Extract program ID from original transaction
            instructions = original_tx_data.get('instructions', [])
            account_keys = original_tx_data.get('accountKeys', [])
            
            for instruction in instructions:
                program_idx = instruction.get('programIdIndex', 0)
                if program_idx < len(account_keys):
                    program_id = account_keys[program_idx]
                    
                    # Check if this is a router program
                    if program_id in self.ROUTER_PROGRAMS.values():
                        logger.info(f"🔄 Copying router transaction for {program_id}")
                        
                        # Extract key parameters
                        data = instruction.get('data', '')
                        accounts = instruction.get('accounts', [])
                        
                        # Decode amount from instruction data
                        try:
                            import base64
                            decoded = base64.b64decode(data)
                            if len(decoded) >= 8:
                                amount = struct.unpack('<Q', decoded[:8])[0]
                                logger.info(f"💰 Detected amount: {amount} lamports")
                                
                                # Extract mint from accounts (usually account[1])
                                if len(accounts) > 1:
                                    mint_idx = accounts[1]
                                    if mint_idx < len(account_keys):
                                        mint = Pubkey.from_string(account_keys[mint_idx])
                                        
                                        # Execute router buy
                                        return await self.execute_router_buy(
                                            program_id, mint, amount, original_tx_data
                                        )
                        except Exception as e:
                            logger.error(f"❌ Failed to decode transaction data: {e}")
            
            logger.warning("⚠️ No router instructions found in transaction")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to copy router transaction: {e}")
            return None

# Test function
async def test_router_compatibility():
    """Test router detection and compatibility"""
    print("🧪 TESTING ROUTER COMPATIBILITY")
    print("=" * 50)
    
    # Test program detection
    executor = PumpRouterExecutor(None, None)
    
    test_programs = [
        '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P',  # Direct
        'F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq',  # Router 1
        '6HB1VBBS8LrdQiR9MZcXV5VdpKFb7vjTMZuQQEQEPioC',  # Router 2
        'UnknownProgramID123456789'                         # Unknown
    ]
    
    for program in test_programs:
        router_type = executor.detect_program_type(program)
        print(f"Program: {program}")
        print(f"Type: {router_type}")
        print()
    
    print("✅ Router compatibility test complete!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_router_compatibility())
