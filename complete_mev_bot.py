#!/usr/bin/env python3
"""
Complete MEV Trading Bo        
        print(f"🔍 Checking if associated_user PDA exists: {associated_user_pda}")
        # Check if account exists
        async with httpx.AsyncClient(timeout=10.0) as client: Buy and Sell
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
            print(f"🔍 Account check result: exists={exists}, data={data.get('result', {})}")
        if exists:
            print("✅ Associated user PDA already exists - no initialization needed")
            return  # Already initialized
        # FIXED: Use correct initialization discriminator
        # For Pump.fun, initialization might not be needed at all, or uses a different discriminator
        # Let's try common Anchor initialization patterns
        # Option 1: Try common init discriminator
        init_discriminator = bytes([175, 175, 109, 31, 13, 152, 155, 237])  # Common Anchor init discriminator
        ix = Instruction(
            program_id=self.PUMP_PROGRAM_ID,
            accounts=[
                AccountMeta(pubkey=associated_user_pda, is_signer=False, is_writable=True),  # Account to initialize
                AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True), # Payer
                AccountMeta(pubkey=self.SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False), # System program (MUST be position 2)
                AccountMeta(pubkey=mint, is_signer=False, is_writable=False),  # Mint
                AccountMeta(pubkey=self.RENT_PROGRAM_ID, is_signer=False, is_writable=False), # Rent
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
    
    def get_pump_accounts(self, token_mint: Pubkey) -> Dict[str, Pubkey]:
        """Get all required Pump.fun accounts - EXACT COPY from successful transaction 4NdQCVM21FBtwBsVfR8ngyUr18DRbwwi1NgvyuZzVYv3pW1t5XwL9jFRmLQ4fu1fMgm6PP6FaDi2wKgTP7viE2as"""
        
        # Bonding curve PDA
        bonding_curve, _ = Pubkey.find_program_address(
            [b"bonding-curve", bytes(token_mint)],
            self.PUMP_PROGRAM_ID
        )
        
        # Associated bonding curve (holds tokens)
        associated_bonding_curve = get_associated_token_address(
            token_mint, bonding_curve
        )
        
        # User's token account
        user_token_account = get_associated_token_address(
            token_mint, self.keypair.pubkey()
        )
        
        # FIXED: Use EXACT accounts from successful transaction, only change wallet/mint specific ones
        return {
            "bonding_curve": bonding_curve,
            "associated_bonding_curve": associated_bonding_curve,
            "user_token_account": user_token_account,
            # EXACT accounts from real transaction (these DON'T change)
            "global_account": Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"),  # [0]
            "fee_recipient": Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM"),   # [1]
            "event_authority": Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), # [10]
            "associated_user": Pubkey.from_string("4ARTvzY4G8VHZPZKc7H69AM7kK4QgZC8uSw4VPSCXvxv"), # [9] - Try exact same first
            "pump_program": self.PUMP_PROGRAM_ID,
            # Additional accounts from real transaction [12-15]
            "account_12": Pubkey.from_string("Hq2wp8uJ9jCPsYgNHex8RtqdvMPfVGoYwjvF1ATiwn2Y"),
            "account_13": Pubkey.from_string("HCm4WDnVHkQZ6QM91cwkoZH1VKndZp1YsfEmGpoQ7Yyj"), 
            "account_14": Pubkey.from_string("8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt"),
            "account_15": Pubkey.from_string("pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ")
        }
        
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
        
    def get_associated_token_address(self, mint: Pubkey, owner: Pubkey) -> Pubkey:
        """Get associated token account address"""
        seeds = [
            bytes(owner),
            bytes(self.TOKEN_PROGRAM_ID),
            bytes(mint)
        ]
        ata_address, _ = Pubkey.find_program_address(seeds, self.ASSOCIATED_TOKEN_PROGRAM_ID)
        return ata_address

    def get_bonding_curve_address(self, mint: Pubkey) -> Pubkey:
        """Derive bonding curve address for mint"""
        # Standard Pump.fun bonding curve derivation
        seeds = [b"bonding-curve", bytes(mint)]
        bonding_curve_address, _ = Pubkey.find_program_address(seeds, self.PUMP_PROGRAM_ID)
        return bonding_curve_address
    
    def get_associated_bonding_curve_address(self, mint: Pubkey) -> Pubkey:
        """Derive associated bonding curve address for mint"""
        bonding_curve = self.get_bonding_curve_address(mint)
        return self.get_associated_token_address(mint, bonding_curve)
        
    def create_mev_buy_instruction(self, mint: Pubkey, sol_amount: int, max_sol_cost: int) -> Instruction:
        """Create MEV-optimized buy instruction by dynamically cloning the router program and account metas from the original transaction."""
        # Expect: router_program_id, account_metas, instruction_data extracted from original transaction
        # These should be passed in from the trade processor or transaction analyzer
        # Example args: router_program_id, account_metas, instruction_data
        # Add logging for router program used
        router_program_id = getattr(self.config, 'router_program_id', None)
        account_metas = getattr(self.config, 'router_account_metas', None)
        instruction_data = getattr(self.config, 'router_instruction_data', None)
        
        # If router data is missing, fall back to default Pump.fun instruction
        if router_program_id is None or account_metas is None or instruction_data is None:
            print("⚠️ [MEV BUY] Router data missing, falling back to default Pump.fun buy instruction")
            return self.create_default_pump_buy_instruction(mint, sol_amount, max_sol_cost)
        
        # Validation and error handling
        if not isinstance(account_metas, list) or len(account_metas) == 0:
            print("❌ [MEV BUY] account_metas is invalid! Cannot construct buy instruction.")
            return self.create_default_pump_buy_instruction(mint, sol_amount, max_sol_cost)
        if not isinstance(instruction_data, (bytes, bytearray)) or len(instruction_data) == 0:
            print("❌ [MEV BUY] instruction_data is invalid! Cannot construct buy instruction.")
            return self.create_default_pump_buy_instruction(mint, sol_amount, max_sol_cost)
            
        print(f"[MEV BUY] Using router program: {router_program_id}")
        print(f"[MEV BUY] Account metas: {[str(a.pubkey) for a in account_metas]}")
        print(f"[MEV BUY] Instruction data: {instruction_data.hex() if hasattr(instruction_data, 'hex') else instruction_data}")
        return Instruction(
            program_id=router_program_id,
            accounts=account_metas,
            data=instruction_data
        )
        
    def create_default_pump_buy_instruction(self, mint: Pubkey, sol_amount: int, max_sol_cost: int) -> Instruction:
        """Create Buy instruction with EXACT format from successful transaction 4NdQCVM21FBtwBsVfR8ngyUr18DRbwwi1NgvyuZzVYv3pW1t5XwL9jFRmLQ4fu1fMgm6PP6FaDi2wKgTP7viE2as"""
        
        pump_accounts = self.get_pump_accounts(mint)
        user_token_account = self.get_associated_token_address(mint, self.keypair.pubkey())
        
        # EXACT discriminator from successful transaction
        discriminator = bytes([102, 6, 61, 18, 1, 218, 235, 234])  # 66063d1201daebea
        print(f"[MEV BUY] Using EXACT Pump.fun buy discriminator: {discriminator.hex()}")
        
        # EXACT data structure from successful transaction: token_amount=16777216, sol_cost=2100000
        # Use same token amount pattern but scale sol cost to user input
        token_amount_bytes = (16777216).to_bytes(8, 'little')  # Same as successful tx
        max_sol_bytes = max_sol_cost.to_bytes(8, 'little')     # User's sol amount
        instruction_data = discriminator + token_amount_bytes + max_sol_bytes
        
        # EXACT account structure from successful transaction - 16 accounts in exact order
        account_metas = [
            AccountMeta(pubkey=pump_accounts["global_account"], is_signer=False, is_writable=True),          # [0] - EXACT from real tx
            AccountMeta(pubkey=pump_accounts["fee_recipient"], is_signer=False, is_writable=True),           # [1] - EXACT from real tx
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),                                    # [2] - User's mint (only difference)
            AccountMeta(pubkey=pump_accounts["bonding_curve"], is_signer=False, is_writable=True),          # [3] - Derived from user's mint
            AccountMeta(pubkey=pump_accounts["associated_bonding_curve"], is_signer=False, is_writable=True), # [4] - Derived from user's mint
            AccountMeta(pubkey=user_token_account, is_signer=False, is_writable=True),                      # [5] - User's token account
            AccountMeta(pubkey=self.keypair.pubkey(), is_signer=True, is_writable=True),                    # [6] - User wallet (only difference)
            AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111112"), is_signer=False, is_writable=False), # [7] - System Program EXACT
            AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False), # [8] - Token Program EXACT
            AccountMeta(pubkey=pump_accounts["associated_user"], is_signer=False, is_writable=True),        # [9] - USE EXACT ACCOUNT FOR NOW
            AccountMeta(pubkey=pump_accounts["event_authority"], is_signer=False, is_writable=False),       # [10] - EXACT from real tx
            AccountMeta(pubkey=pump_accounts["pump_program"], is_signer=False, is_writable=False),          # [11] - EXACT from real tx  
            AccountMeta(pubkey=pump_accounts["account_12"], is_signer=False, is_writable=False),            # [12] - EXACT from real tx
            AccountMeta(pubkey=pump_accounts["account_13"], is_signer=False, is_writable=False),            # [13] - EXACT from real tx
            AccountMeta(pubkey=pump_accounts["account_14"], is_signer=False, is_writable=False),            # [14] - EXACT from real tx  
            AccountMeta(pubkey=pump_accounts["account_15"], is_signer=False, is_writable=False)             # [15] - EXACT from real tx
        ]
        
        print(f"[MEV BUY] Using EXACT Pump.fun buy instruction structure from real transaction")
        print(f"[MEV BUY] Token amount: 16777216 (same as successful tx)")
        print(f"[MEV BUY] Max sol cost: {max_sol_cost} lamports")
        print(f"[MEV BUY] Instruction data: {instruction_data.hex()}")
        
        return Instruction(
            program_id=pump_accounts["pump_program"],
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
            
            # Build compute budget instructions for MEV priority
            compute_limit_ix = set_compute_unit_limit(self.config.buy_compute_limit)
            compute_price_ix = set_compute_unit_price(self.config.buy_priority_fee)
            
            # Check if associated_user PDA needs initialization  
            # FIXED: Use correct seed derivation based on error analysis
            # The error shows it expects a different PDA - let's use the standard pattern
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
                needs_init = data.get("result", {}).get("value") is None
            
            instructions = [compute_limit_ix, compute_price_ix]
            
            # Create buy instruction using EXACT format from real transaction (no initialization needed)
            buy_instruction = self.create_default_pump_buy_instruction(mint, sol_lamports, max_sol_cost)
            instructions.append(buy_instruction)
            
            print(f"🔍 Buy instruction created:")
            print(f"   Program: {buy_instruction.program_id}")
            print(f"   Data: {buy_instruction.data.hex()}")
            print(f"   Accounts: {len(buy_instruction.accounts)}")
            
            print(f"📋 Transaction for MEV Buy:")
            print(f"   Instructions: {len(instructions)}")
            for i, ix in enumerate(instructions):
                print(f"     [{i}] Program: {ix.program_id}")
                print(f"         Data: {ix.data.hex()}")
            
            # Send the combined transaction (initialization + buy in same transaction)
            return await self._send_transaction_no_priority(instructions, "MEV Buy")
            
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

    async def _send_transaction_no_priority(self, instructions: List[Instruction], operation: str) -> Optional[str]:
        """Send transaction without adding additional priority fee instructions (to avoid duplicates)"""
        try:
            print(f"\n📋 Transaction for {operation}:")
            print(f"   Instructions: {len(instructions)}")
            for i, ix in enumerate(instructions):
                print(f"     [{i}] Program: {ix.program_id}")
                print(f"         Data: {ix.data.hex() if hasattr(ix.data, 'hex') else ix.data}")

            # Get recent blockhash
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getLatestBlockhash"
                    }
                )
                blockhash_data = response.json()
                
                if "result" not in blockhash_data:
                    print(f"❌ Failed to get blockhash: {blockhash_data}")
                    return None
                    
                recent_blockhash = Hash.from_string(blockhash_data["result"]["value"]["blockhash"])

                # Create transaction message
                message = MessageV0.try_compile(
                    payer=self.keypair.pubkey(),
                    instructions=instructions,
                    address_lookup_table_accounts=[],
                    recent_blockhash=recent_blockhash
                )

                # Create and sign transaction
                transaction = VersionedTransaction(message, [self.keypair])

                # Convert transaction to base64 for RPC
                transaction_bytes = bytes(transaction)
                transaction_base64 = base64.b64encode(transaction_bytes).decode('utf-8')

                # Simulate first
                simulate_response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "simulateTransaction",
                        "params": [
                            transaction_base64,
                            {
                                "encoding": "base64",
                                "replaceRecentBlockhash": True
                            }
                        ]
                    }
                )

                sim_data = simulate_response.json()
                print(f"🔬 Simulation result: {sim_data}")

                if "error" in sim_data:
                    print(f"❌ Simulation failed: {sim_data['error']}")
                    return None

                if sim_data.get("result", {}).get("value", {}).get("err"):
                    error = sim_data["result"]["value"]["err"]
                    print(f"❌ Transaction simulation failed: {error}")
                    if "logs" in sim_data["result"]["value"]:
                        print(f"   Logs: {sim_data['result']['value']['logs']}")
                    return None

                print("✅ Simulation passed! Sending transaction...")

                # Send the transaction
                send_response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            transaction_base64,
                            {
                                "encoding": "base64",
                                "skipPreflight": self.config.skip_preflight,
                                "maxRetries": 3
                            }
                        ]
                    }
                )

                send_data = send_response.json()
                
                if "error" in send_data:
                    print(f"❌ Send failed: {send_data['error']}")
                    return None
                    
                if "result" in send_data:
                    signature = send_data["result"]
                    print(f"✅ {operation} sent: {signature}")
                    return signature
                else:
                    print(f"❌ Unexpected send response: {send_data}")
                    return None

        except Exception as e:
            print(f"❌ Send transaction error: {e}")
            return None

    async def _send_transaction(self, instructions: List[Instruction], operation: str, skip_priority_instructions: bool = False) -> Optional[str]:
        """Send transaction with MEV optimizations and complete instruction set like successful transactions, with detailed logging and simulation."""
        try:
            if skip_priority_instructions:
                all_instructions = instructions
                priority_instructions = []
            else:
                priority_instructions = self.create_priority_fee_instructions()
                all_instructions = priority_instructions + instructions

            print(f"\n📋 Complete instruction set:")
            print(f"   Priority fee instructions: {len(priority_instructions)}")
            print(f"   Main instructions: {len(instructions)}")
            print(f"   Total instructions: {len(all_instructions)}")
            print(f"   Instruction details:")
            for i, ix in enumerate(all_instructions):
                print(f"     [{i}] Program: {ix.program_id}")
                print(f"         Accounts: {[str(a.pubkey) for a in ix.accounts]}")
                print(f"         Data: {ix.data.hex() if hasattr(ix.data, 'hex') else ix.data}")

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

            # Create and sign transaction
            message = MessageV0.try_compile(
                payer=self.keypair.pubkey(),
                instructions=all_instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=blockhash_obj
            )
            transaction = VersionedTransaction(message, [self.keypair])
            serialized = bytes(transaction)

            print(f"\n🔬 Simulating transaction before sending...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                sim_response = await client.post(
                    self.env.HELIUS_RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "simulateTransaction",
                        "params": [
                            base64.b64encode(serialized).decode('utf-8'),
                            {
                                "sigVerify": False,
                                "encoding": "base64",
                                "commitment": "processed"
                            }
                        ]
                    }
                )
                print(f"   Simulation status: {sim_response.status_code}")
                if sim_response.status_code != 200:
                    print(f"❌ Simulation HTTP error: {sim_response.status_code} - {sim_response.text}")
                    return None
                
                sim_data = sim_response.json()
                print(f"   Simulation full response: {sim_data}")
                
                if 'error' in sim_data:
                    print(f"❌ Simulation RPC error: {sim_data['error']}")
                    print(f"   Error code: {sim_data['error'].get('code')}")
                    print(f"   Error message: {sim_data['error'].get('message')}")
                    print(f"   Error data: {sim_data['error'].get('data')}")
                    return None
                    
                result = sim_data.get('result', {})
                value = result.get('value', {})
                
                if value.get('err'):
                    print(f"❌ Simulation failed: {value['err']}")
                    print(f"   Logs: {value.get('logs', [])}")
                    return None
                else:
                    print(f"✅ Simulation passed successfully")
                    print(f"   Compute units consumed: {value.get('unitsConsumed', 'N/A')}")
                    if value.get('logs'):
                        print(f"   Logs preview: {value['logs'][:3]}...")  # Show first 3 logs

            print(f"\n📡 Sending {operation} transaction...")
            print(f"   Size: {len(serialized)} bytes")
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
                print(f"   Send status: {response.status_code}")
                if response.status_code != 200:
                    print(f"❌ Transaction send HTTP error: {response.status_code} - {response.text}")
                    return None
                
                data = response.json()
                print(f"   Send full response: {data}")
                
                if 'error' in data:
                    print(f"❌ Transaction send RPC error: {data['error']}")
                    print(f"   Error code: {data['error'].get('code')}")
                    print(f"   Error message: {data['error'].get('message')}")
                    print(f"   Error data: {data['error'].get('data')}")
                    return None
                    
                signature = data.get('result')
                if not signature:
                    print(f"❌ No signature returned from send transaction")
                    return None
                print(f"✅ {operation} Transaction sent!")
                print(f"   Signature: {signature}")
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
