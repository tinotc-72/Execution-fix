#!/usr/bin/env python3
"""
MEV-Style Sell Bot Implementation
Enhances the practical MEV bot with professional sell capabilities
"""

import time
import asyncio
from typing import Optional, Tuple, Any, Dict, List
from dataclasses import dataclass
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.instruction import Instruction, AccountMeta
import httpx
import struct
import base64
from env_keys import EnvKeys

@dataclass
class MEVSellConfig:
    """MEV-style sell configuration parameters"""
    
    # Sell-specific optimizations
    priority_fee_micro_lamports: int = 500_000  # High priority for MEV sells
    compute_unit_limit: int = 150_000  # Higher for sell operations
    slippage_multiplier: float = 1.5  # More conservative on sells
    skip_preflight: bool = True  # Speed optimization
    
    # MEV sell strategy
    min_profit_threshold: float = 0.001  # Minimum SOL profit to execute
    max_sell_percentage: float = 100.0  # Maximum percentage to sell
    use_mev_router: bool = True  # Use MEV router for advanced routing

class MEVSellBot:
    """Professional MEV-style sell bot for Pump.fun tokens"""
    
    def __init__(self, private_key: str, config: MEVSellConfig = None):
        self.keypair = Keypair.from_base58_string(private_key)
        self.config = config or MEVSellConfig()
        self.env = EnvKeys()
        
        # Program IDs
        self.PUMP_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.MEV_ROUTER_PROGRAM_ID = Pubkey.from_string("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW")
        self.SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_PROGRAM_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        print(f"🤖 MEV Sell Bot initialized")
        print(f"   Wallet: {self.keypair.pubkey()}")
        print(f"   Priority Fee: {self.config.priority_fee_micro_lamports:,} micro-lamports")
        print(f"   Compute Limit: {self.config.compute_unit_limit:,}")
        
    def get_associated_token_address(self, mint: Pubkey, owner: Pubkey) -> Pubkey:
        """Derive associated token account address"""
        return Pubkey.find_program_address(
            [
                bytes(owner),
                bytes(self.TOKEN_PROGRAM_ID),
                bytes(mint)
            ],
            self.ASSOCIATED_TOKEN_PROGRAM_ID
        )[0]
        
    def get_pump_accounts(self, mint: Pubkey) -> Dict[str, Pubkey]:
        """Get all necessary Pump.fun account addresses"""
        
        # Bonding curve account
        bonding_curve = Pubkey.find_program_address(
            [b"bonding-curve", bytes(mint)],
            self.PUMP_PROGRAM_ID
        )[0]
        
        # Associated bonding curve account
        associated_bonding_curve = self.get_associated_token_address(mint, bonding_curve)
        
        # Global account (standard Pump.fun global)
        global_account = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        
        # Fee recipient
        fee_recipient = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV1T6NVswCLPVXdHy")
        
        return {
            "bonding_curve": bonding_curve,
            "associated_bonding_curve": associated_bonding_curve,
            "global_account": global_account,
            "fee_recipient": fee_recipient
        }
        
    def create_mev_sell_instruction(
        self, 
        mint: Pubkey, 
        token_amount: int,
        min_sol_output: int
    ) -> Tuple[Instruction, List[AccountMeta]]:
        """Create MEV-style sell instruction using the advanced router"""
        
        pump_accounts = self.get_pump_accounts(mint)
        user_token_account = self.get_associated_token_address(mint, self.keypair.pubkey())
        
        # MEV router instruction data (based on analysis of successful MEV sell)
        # This mimics the pattern from the analyzed transaction
        mev_instruction_data = bytes([
            0x33, 0xb2, 0xe3, 0xc9, 0xfd, 0x0b, 0x8c, 0x1c,  # MEV router selector
        ]) + struct.pack("<Q", token_amount) + struct.pack("<Q", min_sol_output) + bytes([
            0x01, 0x00, 0x00, 0x00  # Additional MEV parameters
        ])
        
        # Account metas for MEV router (17 accounts based on analysis)
        account_metas = [
            AccountMeta(pubkey=pump_accounts["global_account"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=pump_accounts["fee_recipient"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=pump_accounts["bonding_curve"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=pump_accounts["associated_bonding_curve"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
            AccountMeta(pubkey=self.SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.RENT_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # Event authority
            AccountMeta(pubkey=self.PUMP_PROGRAM_ID, is_signer=False, is_writable=False),
            # Additional MEV-specific accounts
            AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111112"), is_signer=False, is_writable=False),  # Clock sysvar
            AccountMeta(pubkey=Pubkey.from_string("Sysvar1nstructions1111111111111111111111111"), is_signer=False, is_writable=False),  # Instructions sysvar
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=False, is_writable=True),  # Duplicate for MEV routing
            AccountMeta(pubkey=pump_accounts["bonding_curve"], is_signer=False, is_writable=False)  # Duplicate for validation
        ]
        
        instruction = Instruction(
            program_id=self.MEV_ROUTER_PROGRAM_ID,
            accounts=account_metas,
            data=mev_instruction_data
        )
        
        return instruction, account_metas
        
    async def execute_mev_sell(
        self, 
        mint_str: str, 
        token_amount: int,
        min_sol_output: Optional[int] = None
    ) -> Optional[str]:
        """Execute MEV-style sell with advanced optimizations"""
        
        try:
            mint = Pubkey.from_string(mint_str)
            
            # Calculate minimum SOL output if not provided
            if min_sol_output is None:
                # Conservative estimate - you'd typically get this from price calculation
                min_sol_output = int(token_amount * 0.000001 * 1_000_000_000 * (1 - 0.05))  # 5% slippage
                
            print(f"🎯 Executing MEV Sell:")
            print(f"   Mint: {mint_str}")
            print(f"   Token Amount: {token_amount:,}")
            print(f"   Min SOL Output: {min_sol_output / 1_000_000_000:.6f} SOL")
            
            # Create compute budget instructions
            compute_limit_ix = set_compute_unit_limit(self.config.compute_unit_limit)
            compute_price_ix = set_compute_unit_price(self.config.priority_fee_micro_lamports)
            
            # Create MEV sell instruction
            sell_instruction, _ = self.create_mev_sell_instruction(mint, token_amount, min_sol_output)
            
            # Build transaction
            instructions = [compute_limit_ix, compute_price_ix, sell_instruction]
            
            # Get recent blockhash
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getLatestBlockhash",
                        "params": [{"commitment": "finalized"}]
                    }
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to get blockhash: {response.status_code}")
                    return None
                    
                data = response.json()
                if 'error' in data:
                    print(f"❌ RPC Error: {data['error']}")
                    return None
                    
                blockhash = data['result']['value']['blockhash']
                
            # Create message and transaction
            message = MessageV0.try_compile(
                payer=self.keypair.pubkey(),
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=blockhash
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            
            # Serialize transaction
            serialized = bytes(transaction)
            
            print(f"📡 Sending MEV sell transaction...")
            print(f"   Size: {len(serialized)} bytes")
            
            # Send transaction with MEV optimizations
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            base64.b64encode(serialized).decode('utf-8'),
                            {
                                "skipPreflight": self.config.skip_preflight,
                                "preflightCommitment": "processed",
                                "encoding": "base64",
                                "maxRetries": 3
                            }
                        ]
                    }
                )
                
                if response.status_code != 200:
                    print(f"❌ Send failed: {response.status_code}")
                    return None
                    
                data = response.json()
                if 'error' in data:
                    print(f"❌ Transaction Error: {data['error']}")
                    return None
                    
                signature = data['result']
                print(f"✅ MEV Sell Transaction sent!")
                print(f"   Signature: {signature}")
                
                return signature
                
        except Exception as e:
            print(f"❌ MEV sell failed: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    async def get_token_balance(self, mint_str: str) -> int:
        """Get token balance for the wallet"""
        try:
            mint = Pubkey.from_string(mint_str)
            token_account = self.get_associated_token_address(mint, self.keypair.pubkey())
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTokenAccountBalance",
                        "params": [str(token_account)]
                    }
                )
                
                if response.status_code != 200:
                    return 0
                    
                data = response.json()
                if 'error' in data:
                    return 0
                    
                return int(data['result']['value']['amount'])
                
        except Exception:
            return 0
            
    async def sell_all_tokens(self, mint_str: str) -> Optional[str]:
        """Sell all tokens using MEV optimizations"""
        balance = await self.get_token_balance(mint_str)
        if balance == 0:
            print(f"❌ No tokens to sell for mint: {mint_str}")
            return None
            
        print(f"💰 Selling all {balance:,} tokens")
        return await self.execute_mev_sell(mint_str, balance)

# Test implementation
async def test_mev_sell():
    """Test the MEV sell bot with a real example"""
    
    # Load your private key from environment
    env = EnvKeys()
    private_key = env.PHANTOM_PRIVATE_KEY  # or whatever your key is named
    
    if not private_key:
        print("❌ No private key found in environment")
        return
    
    # Create MEV sell bot
    config = MEVSellConfig(
        priority_fee_micro_lamports=750_000,  # High priority for sells
        compute_unit_limit=200_000,  # Higher limit for complex sells
        slippage_multiplier=2.0  # More conservative on sells
    )
    
    bot = MEVSellBot(private_key, config)
    
    # Test with a token mint (replace with actual token you want to sell)
    test_mint = "Ew4teeKoEKn5EQeNtgfYS5y1gJriBcMXet7kCiTJpump"  # From analyzed transaction
    
    print(f"\n🎯 Testing MEV sell for mint: {test_mint}")
    
    # Check balance first
    balance = await bot.get_token_balance(test_mint)
    print(f"Current balance: {balance:,} tokens")
    
    if balance > 0:
        # Execute sell
        signature = await bot.sell_all_tokens(test_mint)
        if signature:
            print(f"🚀 MEV sell executed successfully: {signature}")
        else:
            print("❌ MEV sell failed")
    else:
        print("ℹ️ No tokens to sell - testing instruction creation only")
        
        # Test instruction creation with dummy values
        try:
            mint = Pubkey.from_string(test_mint)
            instruction, accounts = bot.create_mev_sell_instruction(mint, 1000000, 1000)
            print(f"✅ MEV sell instruction created successfully")
            print(f"   Program ID: {instruction.program_id}")
            print(f"   Accounts: {len(instruction.accounts)}")
            print(f"   Data length: {len(instruction.data)} bytes")
        except Exception as e:
            print(f"❌ Instruction creation failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mev_sell())
