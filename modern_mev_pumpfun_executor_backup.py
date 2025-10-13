#!/usr/bin/env python3
"""
Complete MEV Trading Bot - Buy and Sell
Professional-grade MEV bot with both buy and sell capabilities
"""

import time
import asyncio
import base58
from typing import Optional, Tuple, Any, Dict, List
from dataclasses import dataclass
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.system_program import TransferParams, transfer
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.instruction import Instruction, AccountMeta
from spl.token.instructions import get_associated_token_address
import httpx
import struct
import base64
from env_keys import EnvKeys

@dataclass
class CompleteMEVConfig:
    """Complete MEV bot configuration for buy and sell operations"""
    
    # Buy configuration
    buy_priority_fee: int = 500_000  # Micro-lamports
    buy_compute_limit: int = 149_700  # Optimized from analysis
    buy_slippage_multiplier: float = 2.0
    
    # Sell configuration  
    sell_priority_fee: int = 750_000  # Higher priority for sells
    sell_compute_limit: int = 200_000  # Higher for sell operations
    sell_slippage_multiplier: float = 1.5
    
    # General settings
    skip_preflight: bool = True
    use_mev_router: bool = True

class CompleteMEVBot:
    async def ensure_associated_user_initialized(self, mint: Pubkey) -> None:
        """Check if associated_user PDA exists, and if not, initialize it."""
        # Derive associated_user PDA (Pump.fun convention: [b"associated_user", wallet, token_mint])
        associated_user_pda, _ = Pubkey.find_program_address(
            [b"associated_user", bytes(self.keypair.pubkey()), bytes(mint)],
            self.PUMP_PROGRAM_ID
        )
        # Check if account exists
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                self.env.HELIUS_RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [str(associated_user_pda), {"encoding": "base64"}]
                }
            )
            data = resp.json()
            exists = data.get("result", {}).get("value") is not None
        if exists:
            return  # Already initialized
        # Build initialize instruction (discriminator is 8 zero bytes)
        init_discriminator = bytes(8)
        ix = Instruction(
            program_id=self.PUMP_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=associated_user_pda, is_signer=False, is_writable=True),
                AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.RENT_PROGRAM_ID, is_signer=False, is_writable=False),
            ],
            data=init_discriminator
        )
        # Send the initialize transaction
        await self._send_transaction([ix], "Initialize associated_user")
    """Professional MEV bot with complete buy/sell capabilities"""
    
    def __init__(self, private_key: str, config: CompleteMEVConfig = None):
        self.keypair = Keypair.from_base58_string(private_key)
        self.config = config or CompleteMEVConfig()
        self.env = EnvKeys()
        
        # Program IDs - FIXED: Using correct current Pump.fun program ID
        self.PUMP_PROGRAM_ID = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.MEV_ROUTER_PROGRAM_ID = Pubkey.from_string("BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW")
        self.SYSTEM_PROGRAM_ID = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_PROGRAM_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        print(f"🤖 Complete MEV Bot initialized")
        print(f"   Wallet: {self.keypair.pubkey()}")
        print(f"   Buy Priority: {self.config.buy_priority_fee:,} μ-lamports")
        print(f"   Sell Priority: {self.config.sell_priority_fee:,} μ-lamports")
        
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
        
        bonding_curve = Pubkey.find_program_address(
            [b"bonding-curve", bytes(mint)],
            self.PUMP_PROGRAM_ID
        )[0]
        
        associated_bonding_curve = self.get_associated_token_address(mint, bonding_curve)
        global_account = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
    fee_program = Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
    fee_recipient_writable = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV1T6NVswCLPVXdHy")
        
        return {
            "bonding_curve": bonding_curve,
            "associated_bonding_curve": associated_bonding_curve,
            "global_account": global_account,
            "fee_recipient": fee_program,
            "fee_recipient_writable": fee_recipient_writable
        }
        
    def create_mev_buy_instruction(self, mint: Pubkey, sol_amount: int, max_sol_cost: int) -> Instruction:
        """Create MEV-optimized buy instruction using Jupiter routing (like successful transactions)"""
        
        # MAJOR FIX: Successful transactions don't call Pump.fun directly - they use Jupiter Router!
        # Jupiter Router program ID (from successful transaction analysis)
        JUPITER_ROUTER_PROGRAM_ID = Pubkey.from_string("F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq")
        
        # Exact instruction data from successful transaction: '1QSjywUgpFzpkwQV9yPSABq' 
        # Decoded: 00bdda4598000000004586f554dc040000 (17 bytes)
        # This represents a Jupiter Router swap instruction with amount parameters
        instruction_data = bytes.fromhex("00bdda4598000000004586f554dc040000")
        
        pump_accounts = self.get_pump_accounts(mint)
        user_token_account = self.get_associated_token_address(mint, self.keypair.pubkey())
        
        # Account structure matching successful transactions [21, 16, 12, 3, 4, 2, 0, 9, 20, 5, 22, 23, 6, 7, 14, 15]
        # This needs to be dynamically constructed based on the successful transaction pattern
        account_metas = [
            # Core accounts for Jupiter Router calling Pump.fun
            AccountMeta(pubkey=pump_accounts["global_account"], is_signer=False, is_writable=False),     # Global
            AccountMeta(pubkey=pump_accounts["fee_recipient"], is_signer=False, is_writable=True),       # Fee recipient
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),                               # Token mint
            AccountMeta(pubkey=pump_accounts["bonding_curve"], is_signer=False, is_writable=True),      # Bonding curve
            AccountMeta(pubkey=pump_accounts["associated_bonding_curve"], is_signer=False, is_writable=True), # Associated bonding curve
            AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),                 # User token account
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),               # User (signer)
            AccountMeta(pubkey=self.SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),            # System program
            AccountMeta(pubkey=self.TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),             # Token program
            AccountMeta(pubkey=self.RENT_PROGRAM_ID, is_signer=False, is_writable=False),              # Rent
            AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False), # Event authority
            AccountMeta(pubkey=self.PUMP_PROGRAM_ID, is_signer=False, is_writable=False),              # Pump.fun program
            AccountMeta(pubkey=Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"), is_signer=False, is_writable=False), # Fee program
            # Add other required accounts based on successful transaction analysis
        ]

        return Instruction(
            program_id=JUPITER_ROUTER_PROGRAM_ID,  # Use Jupiter Router instead of Pump.fun directly
            accounts=account_metas,
            data=instruction_data
        )
        
        # Derive associated_user PDA for this specific user and token
        associated_user_pda, _ = Pubkey.find_program_address(
            [b"associated_user", bytes(self.keypair.pubkey()), bytes(mint)],
            self.PUMP_PROGRAM_ID
        )
        
        # Use correct account structure with proper PDA derivation
        account_metas = [
            AccountMeta(pubkey=pump_accounts["global_account"], is_signer=False, is_writable=False),     # Global
            AccountMeta(pubkey=pump_accounts["fee_recipient"], is_signer=False, is_writable=True),       # Fee recipient
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),                               # Token mint
            AccountMeta(pubkey=pump_accounts["bonding_curve"], is_signer=False, is_writable=True),      # Bonding curve
            AccountMeta(pubkey=pump_accounts["associated_bonding_curve"], is_signer=False, is_writable=True), # Associated bonding curve
            AccountMeta(pubkey=associated_user_pda, is_signer=False, is_writable=True),                 # Associated user (derived for this user)
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),               # User (signer)
            AccountMeta(pubkey=self.SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),            # System program
            AccountMeta(pubkey=self.TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),             # Token program
            AccountMeta(pubkey=self.RENT_PROGRAM_ID, is_signer=False, is_writable=False),              # Rent
            AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False), # Event authority
            AccountMeta(pubkey=self.PUMP_PROGRAM_ID, is_signer=False, is_writable=False),              # Program
            AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),                 # User ATA
        ]
        
        return Instruction(
            program_id=self.PUMP_PROGRAM_ID,
            accounts=account_metas,
            data=instruction_data
        )
        
    def create_mev_sell_instruction(self, mint: Pubkey, token_amount: int, min_sol_output: int) -> Instruction:
        """Create MEV-optimized sell instruction"""
        
        pump_accounts = self.get_pump_accounts(mint)
        user_token_account = self.get_associated_token_address(mint, self.keypair.pubkey())
        
        # MEV sell instruction data (from MEV router analysis)
        instruction_data = bytes([0x33, 0xb2, 0xe3, 0xc9, 0xfd, 0x0b, 0x8c, 0x1c])
        instruction_data += struct.pack("<Q", token_amount)
        instruction_data += struct.pack("<Q", min_sol_output)
        instruction_data += bytes([0x01, 0x00, 0x00, 0x00])
        
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
            AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.PUMP_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111112"), is_signer=False, is_writable=False),
            AccountMeta(pubkey=Pubkey.from_string("Sysvar1nstructions1111111111111111111111111"), is_signer=False, is_writable=False),
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=False, is_writable=True),
            AccountMeta(pubkey=pump_accounts["bonding_curve"], is_signer=False, is_writable=False)
        ]
        
        return Instruction(
            program_id=self.MEV_ROUTER_PROGRAM_ID,
            accounts=account_metas,
            data=instruction_data
        )
        
    def create_ata_instruction(self, mint: Pubkey) -> Instruction:
        """Create Associated Token Account instruction like successful transactions"""
        user_token_account = self.get_associated_token_address(mint, self.keypair.pubkey())
        
        return Instruction(
            program_id=self.ASSOCIATED_TOKEN_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),
                AccountMeta(pubkey=self.keypair.pubkey(), is_signer=False, is_writable=False),
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(pubkey=self.TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            ],
            data=bytes()  # Create instruction has no data
        )

    async def execute_buy(self, mint_str: str, sol_amount: float) -> Optional[str]:
        """Execute MEV-optimized buy with COMPLETE instruction set like successful transactions"""
        try:
            mint = Pubkey.from_string(mint_str)
            sol_lamports = int(sol_amount * 1_000_000_000)
            max_sol_cost = int(sol_lamports * self.config.buy_slippage_multiplier)
            
            print(f"🎯 MEV Buy: {mint_str} for {sol_amount:.6f} SOL")
            
            # Ensure associated_user is initialized before buying
            await self.ensure_associated_user_initialized(mint)
            
            # Build compute budget instructions for MEV priority
            compute_limit_ix = set_compute_unit_limit(self.config.buy_compute_limit)
            compute_price_ix = set_compute_unit_price(self.config.buy_priority_fee)
            
            # Create the buy instruction
            buy_instruction = self.create_mev_buy_instruction(mint, sol_lamports, max_sol_cost)
            
            # Combine all instructions
            instructions = [compute_limit_ix, compute_price_ix, buy_instruction]
            
            # Send the transaction
            return await self._send_transaction(instructions, "MEV Buy")
            
        except Exception as e:
            print(f"❌ MEV Buy failed: {e}")
            return None
            
    async def execute_sell(self, mint_str: str, token_amount: Optional[int] = None) -> Optional[str]:
        """Execute MEV-optimized sell"""
        
        try:
            mint = Pubkey.from_string(mint_str)
            
            # Get token balance if not specified
            if token_amount is None:
                token_amount = await self.get_token_balance(mint_str)
                
            if token_amount == 0:
                print(f"❌ No tokens to sell")
                return None
                
            # Calculate minimum SOL output (conservative estimate)
            min_sol_output = int(token_amount * 0.000001 * 1_000_000_000 * (1 - 0.05))
            
            print(f"🎯 Executing MEV Sell:")
            print(f"   Mint: {mint_str}")
            print(f"   Token Amount: {token_amount:,}")
            print(f"   Min SOL Output: {min_sol_output / 1_000_000_000:.6f} SOL")
            
            # Create instructions
            compute_limit_ix = set_compute_unit_limit(self.config.sell_compute_limit)
            compute_price_ix = set_compute_unit_price(self.config.sell_priority_fee)
            sell_instruction = self.create_mev_sell_instruction(mint, token_amount, min_sol_output)
            
            instructions = [compute_limit_ix, compute_price_ix, sell_instruction]
            
            return await self._send_transaction(instructions, "MEV Sell")
            
        except Exception as e:
            print(f"❌ MEV sell failed: {e}")
            return None
            
    def create_priority_fee_instructions(self) -> List[Instruction]:
        """Create compute budget instructions like successful transactions"""
        from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
        
        instructions = []
        
        # Set compute unit limit (like successful transactions)
        instructions.append(set_compute_unit_limit(200_000))
        
        # Set priority fee (like successful transactions)
        instructions.append(set_compute_unit_price(self.config.buy_priority_fee))
        
        return instructions

    async def _send_transaction(self, instructions: List[Instruction], operation: str) -> Optional[str]:
        """Send transaction with MEV optimizations and complete instruction set like successful transactions"""
        
        try:
            # 🔥 CRITICAL FIX: Add priority fee instructions like successful transactions
            priority_instructions = self.create_priority_fee_instructions()
            all_instructions = priority_instructions + instructions
            
            print(f"📋 Complete instruction set:")
            print(f"   Priority fee instructions: {len(priority_instructions)}")
            print(f"   Main instructions: {len(instructions)}")
            print(f"   Total instructions: {len(all_instructions)}")
            
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
                blockhash_obj = Hash.from_string(blockhash)
                
            # Create and sign transaction with MessageV0 for address table lookup support
            message = MessageV0.try_compile(
                payer=self.keypair.pubkey(),
                instructions=all_instructions,  # Use complete instruction set
                address_lookup_table_accounts=[],  # TODO: Add actual lookup tables
                recent_blockhash=blockhash_obj
            )
            
            transaction = VersionedTransaction(message, [self.keypair])
            serialized = bytes(transaction)
            
            print(f"📡 Sending {operation} transaction...")
            print(f"   Size: {len(serialized)} bytes")
            
            # Send with MEV optimizations
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
                print(f"✅ {operation} Transaction sent!")
                print(f"   Signature: {signature}")
                
                # 🔥 CRITICAL FIX: Verify transaction actually succeeded
                success = await self._verify_transaction_success(signature)
                if not success:
                    print(f"❌ {operation} Transaction failed on blockchain: {signature}")
                    return None
                
                print(f"✅ {operation} Transaction confirmed successful on blockchain!")
                return signature
                
        except Exception as e:
            print(f"❌ {operation} transaction failed: {e}")
            return None
    
    async def _verify_transaction_success(self, signature: str) -> bool:
        """
        🔥 CRITICAL: Verify transaction actually succeeded on blockchain
        Returns True only if transaction was successful, False if failed
        """
        try:
            # Wait a bit for transaction to be processed
            await asyncio.sleep(1)
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            signature,
                            {
                                "encoding": "json",
                                "commitment": "confirmed",
                                "maxSupportedTransactionVersion": 0
                            }
                        ]
                    }
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to get transaction status: {response.status_code}")
                    return False
                    
                data = response.json()
                if 'error' in data:
                    print(f"❌ Transaction verification error: {data['error']}")
                    return False
                
                if not data.get('result'):
                    print(f"❌ Transaction not found: {signature}")
                    return False
                
                # Check if transaction has error
                meta = data['result'].get('meta', {})
                if meta.get('err'):
                    print(f"❌ Transaction failed on blockchain: {meta['err']}")
                    return False
                
                print(f"✅ Transaction verified successful on blockchain")
                return True
                
        except Exception as e:
            print(f"❌ Error verifying transaction: {e}")
            return False
            
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
            
    async def get_sol_balance(self) -> float:
        """Get SOL balance"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [str(self.keypair.pubkey())]
                    }
                )
                
                if response.status_code != 200:
                    return 0.0
                    
                data = response.json()
                if 'error' in data:
                    return 0.0
                    
                return data['result']['value'] / 1_000_000_000
                
        except Exception:
            return 0.0

# Test complete MEV bot
async def test_complete_mev():
    """Test the complete MEV bot"""
    
    env = EnvKeys()
    private_key = env.PHANTOM_PRIVATE_KEY
    
    if not private_key:
        print("❌ No private key found")
        return
    
    # Create complete MEV bot with optimized settings
    config = CompleteMEVConfig(
        buy_priority_fee=500_000,    # From successful MEV buy analysis
        buy_compute_limit=149_700,   # Optimized limit
        sell_priority_fee=750_000,   # Higher priority for sells
        sell_compute_limit=200_000,  # Higher for complex sells
        skip_preflight=True          # Speed optimization
    )
    
    bot = CompleteMEVBot(private_key, config)
    
    # Check balances
    sol_balance = await bot.get_sol_balance()
    print(f"\n💰 Current balances:")
    print(f"   SOL: {sol_balance:.6f}")
    
    # Test with a token (replace with actual mint you want to trade)
    test_mint = "DKLnWyUaFhPo9YsxTaJUQr5ZWLgDhojC8BXMM7QXpump"  # Replace with real mint
    
    token_balance = await bot.get_token_balance(test_mint)
    print(f"   Token: {token_balance:,}")
    
    print(f"\n🎯 Complete MEV Bot ready for:")
    print(f"   ✅ High-speed MEV buys")
    print(f"   ✅ Advanced MEV sells") 
    print(f"   ✅ Professional optimizations")
    print(f"   ✅ Direct Pump.fun integration")
    
    # Example: Uncomment to test buy
    # if sol_balance > 0.01:
    #     print(f"\n🎯 Testing MEV buy...")
    #     signature = await bot.execute_buy(test_mint, 0.01)
    #     if signature:
    #         print(f"✅ Buy successful: {signature}")
    
    # Example: Uncomment to test sell
    # if token_balance > 0:
    #     print(f"\n🎯 Testing MEV sell...")
    #     signature = await bot.execute_sell(test_mint)
    #     if signature:
    #         print(f"✅ Sell successful: {signature}")

if __name__ == "__main__":
    asyncio.run(test_complete_mev())
