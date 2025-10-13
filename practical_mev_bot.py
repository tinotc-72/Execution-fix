"""
Practical MEV-Style Pump.fun Bot
Implements the key optimizations from MEV bots that we can actually use
"""

import asyncio
import base64
import struct
import httpx
from typing import Dict, Any, Optional
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from spl.token.instructions import get_associated_token_address, create_associated_token_account

from env_keys import EnvKeys, load_wallet_from_private_key, validate_env_vars


@dataclass
class MEVStyleConfig:
    """Configuration for MEV-style trading"""
    priority_fee_lamports: int = 500000  # High priority like MEV bots
    compute_units: int = 149700  # Sufficient compute units
    skip_preflight: bool = True  # Speed optimization
    max_retries: int = 3
    slippage_multiplier: float = 2.0  # Aggressive slippage like MEV bots


class PracticalMEVBot:
    """
    Practical MEV-style bot that implements the key optimizations
    without trying to copy complex proprietary programs
    """
    
    def __init__(self, wallet_keypair: Keypair, config: MEVStyleConfig = None):
        env = EnvKeys()
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = env.HELIUS_RPC_URL
        self.config = config or MEVStyleConfig()
        
        # Pump.fun program addresses
        self.PUMP_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
        self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
        
        # System programs
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        # Instruction discriminators
        self.BUY_DISCRIMINATOR = bytes.fromhex("66063d1201daebea")
        self.SELL_DISCRIMINATOR = bytes.fromhex("33e685a4017f83ad")
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def rpc_call(self, method: str, params: list = None) -> dict:
        """Make RPC call with error handling"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }
        
        response = await self.client.post(self.rpc_url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            raise Exception(f"RPC error: {data['error']}")
        
        return data["result"]
    
    def get_pump_accounts(self, token_mint: Pubkey) -> Dict[str, Pubkey]:
        """Get all required Pump.fun accounts"""
        
        # Bonding curve PDA
        bonding_curve, _ = Pubkey.find_program_address(
            [b"bonding-curve", bytes(token_mint)],
            self.PUMP_PROGRAM
        )
        
        # Associated bonding curve (holds tokens)
        associated_bonding_curve = get_associated_token_address(
            bonding_curve, token_mint
        )
        
        # User's token account
        user_token_account = get_associated_token_address(
            self.wallet_pubkey, token_mint
        )
        
        # Associated user PDA (if needed)
        associated_user, _ = Pubkey.find_program_address(
            [b"associated-user", bytes(self.wallet_pubkey)],
            self.PUMP_PROGRAM
        )
        
        return {
            "bonding_curve": bonding_curve,
            "associated_bonding_curve": associated_bonding_curve,
            "user_token_account": user_token_account,
            "associated_user": associated_user
        }
    
    def build_mev_style_buy_instruction(self, token_mint: Pubkey, amount_lamports: int) -> Instruction:
        """
        Build buy instruction with MEV-style optimizations
        """
        
        accounts = self.get_pump_accounts(token_mint)
        
        # Aggressive slippage like MEV bots
        max_sol_cost = int(amount_lamports * self.config.slippage_multiplier)
        
        # Build instruction data
        instruction_data = self.BUY_DISCRIMINATOR + struct.pack("<QQ", amount_lamports, max_sol_cost)
        
        # Account metas in correct order
        account_metas = [
            AccountMeta(self.GLOBAL_ACCOUNT, False, False),
            AccountMeta(self.FEE_RECIPIENT, False, True),
            AccountMeta(token_mint, False, False),
            AccountMeta(accounts["bonding_curve"], False, True),
            AccountMeta(accounts["associated_bonding_curve"], False, True),
            AccountMeta(accounts["user_token_account"], False, True),
            AccountMeta(self.wallet_pubkey, True, True),
            AccountMeta(self.SYSTEM_PROGRAM, False, False),
            AccountMeta(self.TOKEN_PROGRAM, False, False),
            AccountMeta(self.ASSOCIATED_TOKEN_PROGRAM, False, False),
            AccountMeta(self.RENT_SYSVAR, False, False),
            AccountMeta(self.EVENT_AUTHORITY, False, False),
            AccountMeta(self.PUMP_PROGRAM, False, False),
        ]
        
        return Instruction(
            program_id=self.PUMP_PROGRAM,
            accounts=account_metas,
            data=instruction_data
        )
    
    async def execute_mev_style_buy(self, token_mint: str, amount_sol: float) -> Dict[str, Any]:
        """
        Execute buy with MEV-style optimizations
        """
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            amount_lamports = int(amount_sol * 1_000_000_000)
            
            print(f"🤖 Executing MEV-style buy...")
            print(f"   Token: {token_mint}")
            print(f"   Amount: {amount_sol} SOL")
            print(f"   Priority fee: {self.config.priority_fee_lamports} micro-lamports")
            print(f"   Compute units: {self.config.compute_units}")
            
            # Build instructions
            instructions = []
            
            # 1. Set high priority fee (MEV optimization)
            priority_fee_ix = set_compute_unit_price(self.config.priority_fee_lamports)
            instructions.append(priority_fee_ix)
            
            # 2. Set compute unit limit
            compute_limit_ix = set_compute_unit_limit(self.config.compute_units)
            instructions.append(compute_limit_ix)
            
            # 3. Create token account if needed
            accounts = self.get_pump_accounts(token_mint_pubkey)
            
            # Check if token account exists
            try:
                account_info = await self.rpc_call("getAccountInfo", [str(accounts["user_token_account"])])
                if not account_info or not account_info.get("value"):
                    create_ata_ix = create_associated_token_account(
                        self.wallet_pubkey,
                        self.wallet_pubkey,
                        token_mint_pubkey
                    )
                    instructions.append(create_ata_ix)
                    print("   📝 Creating token account...")
            except:
                # Create it anyway to be safe
                create_ata_ix = create_associated_token_account(
                    self.wallet_pubkey,
                    self.wallet_pubkey,
                    token_mint_pubkey
                )
                instructions.append(create_ata_ix)
                print("   📝 Creating token account...")
            
            # 4. Main buy instruction
            buy_instruction = self.build_mev_style_buy_instruction(token_mint_pubkey, amount_lamports)
            instructions.append(buy_instruction)
            
            # Get recent blockhash
            blockhash_resp = await self.rpc_call("getLatestBlockhash", [{"commitment": "finalized"}])
            from solders.hash import Hash
            recent_blockhash = Hash.from_string(blockhash_resp["value"]["blockhash"])
            
            # Build transaction
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=instructions,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            tx_bytes = base64.b64encode(bytes(transaction)).decode()
            
            # Simulate first (optional for MEV bots, but good for debugging)
            if not self.config.skip_preflight:
                print("   🔍 Simulating transaction...")
                sim_result = await self.rpc_call("simulateTransaction", [
                    tx_bytes,
                    {"encoding": "base64", "commitment": "processed"}
                ])
                
                if sim_result["value"]["err"]:
                    return {
                        "success": False,
                        "error": f"Simulation failed: {sim_result['value']['err']}",
                        "logs": sim_result["value"].get("logs", [])
                    }
                
                print("   ✅ Simulation successful")
            
            # Send transaction with MEV settings
            print("   🚀 Sending transaction...")
            
            send_params = {
                "encoding": "base64",
                "skipPreflight": self.config.skip_preflight,
                "preflightCommitment": "processed",
                "maxRetries": self.config.max_retries
            }
            
            signature = await self.rpc_call("sendTransaction", [tx_bytes, send_params])
            
            # Calculate estimated fee
            estimated_fee = (self.config.compute_units * self.config.priority_fee_lamports) / 1_000_000_000
            
            return {
                "success": True,
                "signature": signature,
                "method": "MEV-Style Direct Pump.fun",
                "priority_fee_sol": estimated_fee,
                "compute_units": self.config.compute_units,
                "slippage_multiplier": self.config.slippage_multiplier,
                "config": {
                    "skip_preflight": self.config.skip_preflight,
                    "max_retries": self.config.max_retries
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"MEV-style buy failed: {str(e)}"
            }
    
    async def execute_mev_style_sell(self, token_mint: str, percentage: float = 100.0) -> Dict[str, Any]:
        """
        Execute sell with MEV-style optimizations
        """
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            
            # Get current token balance
            accounts = self.get_pump_accounts(token_mint_pubkey)
            
            account_info = await self.rpc_call("getAccountInfo", [
                str(accounts["user_token_account"]),
                {"encoding": "jsonParsed"}
            ])
            
            if not account_info or not account_info.get("value"):
                return {"success": False, "error": "No token account found"}
            
            token_amount = int(account_info["value"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
            if token_amount <= 0:
                return {"success": False, "error": "No tokens to sell"}
            
            sell_amount = int(token_amount * (percentage / 100.0))
            
            print(f"🤖 Executing MEV-style sell...")
            print(f"   Token: {token_mint}")
            print(f"   Amount: {sell_amount} tokens ({percentage}%)")
            
            # Build sell instruction
            instructions = []
            
            # Priority fee and compute limit
            instructions.append(set_compute_unit_price(self.config.priority_fee_lamports))
            instructions.append(set_compute_unit_limit(self.config.compute_units))
            
            # Sell instruction
            min_sol_out = 0  # Accept any amount (MEV style)
            instruction_data = self.SELL_DISCRIMINATOR + struct.pack("<QQ", sell_amount, min_sol_out)
            
            account_metas = [
                AccountMeta(self.GLOBAL_ACCOUNT, False, False),
                AccountMeta(self.FEE_RECIPIENT, False, True),
                AccountMeta(token_mint_pubkey, False, False),
                AccountMeta(accounts["bonding_curve"], False, True),
                AccountMeta(accounts["associated_bonding_curve"], False, True),
                AccountMeta(accounts["user_token_account"], False, True),
                AccountMeta(self.wallet_pubkey, True, True),
                AccountMeta(self.SYSTEM_PROGRAM, False, False),
                AccountMeta(self.TOKEN_PROGRAM, False, False),
                AccountMeta(self.ASSOCIATED_TOKEN_PROGRAM, False, False),
                AccountMeta(self.RENT_SYSVAR, False, False),
                AccountMeta(self.EVENT_AUTHORITY, False, False),
                AccountMeta(self.PUMP_PROGRAM, False, False),
            ]
            
            sell_instruction = Instruction(
                program_id=self.PUMP_PROGRAM,
                accounts=account_metas,
                data=instruction_data
            )
            
            instructions.append(sell_instruction)
            
            # Execute transaction
            blockhash_resp = await self.rpc_call("getLatestBlockhash")
            from solders.hash import Hash
            recent_blockhash = Hash.from_string(blockhash_resp["value"]["blockhash"])
            
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=instructions,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            tx_bytes = base64.b64encode(bytes(transaction)).decode()
            
            signature = await self.rpc_call("sendTransaction", [
                tx_bytes,
                {
                    "encoding": "base64",
                    "skipPreflight": self.config.skip_preflight,
                    "maxRetries": self.config.max_retries
                }
            ])
            
            return {
                "success": True,
                "signature": signature,
                "method": "MEV-Style Sell",
                "tokens_sold": sell_amount,
                "percentage": percentage
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"MEV-style sell failed: {str(e)}"
            }


async def main():
    """Test the practical MEV bot"""
    
    # Load wallet
    env_vars = validate_env_vars()
    wallet_keypair = load_wallet_from_private_key(env_vars["PHANTOM_PRIVATE_KEY"])
    
    # Configure MEV-style settings
    mev_config = MEVStyleConfig(
        priority_fee_lamports=500000,  # High priority like the MEV bot we analyzed
        compute_units=149700,          # Same compute units
        skip_preflight=True,           # Speed optimization
        max_retries=3,
        slippage_multiplier=2.0        # Aggressive slippage
    )
    
    token_mint = "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmn"  # Example token
    
    async with PracticalMEVBot(wallet_keypair, mev_config) as bot:
        print("🤖 Practical MEV-Style Pump.fun Bot")
        print("=" * 50)
        print(f"Wallet: {bot.wallet_pubkey}")
        print(f"RPC: {bot.rpc_url[:50]}...")
        print()
        
        # Test buy
        result = await bot.execute_mev_style_buy(token_mint, 0.001)
        
        if result["success"]:
            print("✅ MEV-style buy successful!")
            print(f"   Signature: {result['signature']}")
            print(f"   Method: {result['method']}")
            print(f"   Priority fee: {result['priority_fee_sol']:.9f} SOL")
            print(f"   Compute units: {result['compute_units']}")
            print(f"   Slippage multiplier: {result['slippage_multiplier']}x")
            print(f"   Skip preflight: {result['config']['skip_preflight']}")
        else:
            print("❌ MEV-style buy failed!")
            print(f"   Error: {result['error']}")
            if "logs" in result:
                print("   Logs:")
                for log in result["logs"][:5]:
                    print(f"     {log}")


if __name__ == "__main__":
    asyncio.run(main())
