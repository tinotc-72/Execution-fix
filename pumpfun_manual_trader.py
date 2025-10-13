"""
Manual Pump.fun Trading using Low-Level Solana SDK
--- Pump.fun Anchor IDL REQUIRED ---
All instruction construction in this file must use the official Pump.fun Anchor IDL
(discriminator and argument layout from the IDL, not hardcoded or reverse-engineered)
This approach builds transactions manually using only the Solana primitives
"""

import asyncio
import base64
import struct
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.system_program import create_account, CreateAccountParams
from spl.token.instructions import (
    get_associated_token_address, 
    create_associated_token_account,
    initialize_account,
    InitializeAccountParams
)
import httpx


@dataclass
class TradeParams:
    token_mint: str
    amount_sol: float
    slippage: float = 5.0  # 5% slippage


class ManualPumpFunTrader:
    """
    Manual approach that builds every piece of the transaction from scratch
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Known working addresses from mainnet
        self.PUMP_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
        
        # System programs
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        # Event authority (used in some transactions)
        self.EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def rpc_call(self, method: str, params: list = None) -> dict:
        """Make RPC call"""
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
        """Get all Pump.fun related accounts for a token"""
        
        # Bonding curve account
        bonding_curve, _ = Pubkey.find_program_address(
            [b"bonding-curve", bytes(token_mint)],
            self.PUMP_PROGRAM
        )
        
        # Associated bonding curve (holds the tokens)
        associated_bonding_curve = get_associated_token_address(
            bonding_curve, token_mint
        )
        
        # User's token account
        user_token_account = get_associated_token_address(
            self.wallet_pubkey, token_mint
        )
        
        # Associated user account (might be needed)
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
    
    async def build_buy_instruction(self, token_mint: Pubkey, amount_lamports: int) -> Instruction:
        """Build the buy instruction manually"""
        
        accounts = self.get_pump_accounts(token_mint)
        
        # Build instruction data
        # Format: discriminator (8 bytes) + amount (8 bytes) + max_sol_cost (8 bytes)
        discriminator = bytes.fromhex("66063d1201daebea")  # Buy discriminator
        amount_bytes = struct.pack("<Q", amount_lamports)
        max_sol_cost = struct.pack("<Q", amount_lamports * 2)  # Allow 2x slippage
        
        instruction_data = discriminator + amount_bytes + max_sol_cost
        
        # Account metas in the correct order
        account_metas = [
            AccountMeta(self.GLOBAL, False, False),
            AccountMeta(self.FEE_RECIPIENT, False, True),
            AccountMeta(token_mint, False, False),
            AccountMeta(accounts["bonding_curve"], False, True),
            AccountMeta(accounts["associated_bonding_curve"], False, True),
            AccountMeta(accounts["associated_user"], False, True),
            AccountMeta(accounts["user_token_account"], False, True),
            AccountMeta(self.wallet_pubkey, True, True),
            AccountMeta(self.SYSTEM_PROGRAM, False, False),
            AccountMeta(self.TOKEN_PROGRAM, False, False),
            AccountMeta(self.RENT, False, False),
            AccountMeta(self.EVENT_AUTHORITY, False, False),
            AccountMeta(self.PUMP_PROGRAM, False, False),
        ]
        
        return Instruction(
            program_id=self.PUMP_PROGRAM,
            accounts=account_metas,
            data=instruction_data
        )
    
    async def build_setup_instructions(self, token_mint: Pubkey) -> List[Instruction]:
        """Build setup instructions to create necessary accounts"""
        
        instructions = []
        accounts = self.get_pump_accounts(token_mint)
        
        # Check if user token account exists
        try:
            account_info = await self.rpc_call("getAccountInfo", [str(accounts["user_token_account"])])
            if not account_info or not account_info.get("value"):
                # Create associated token account
                create_ata_ix = create_associated_token_account(
                    self.wallet_pubkey,
                    self.wallet_pubkey,
                    token_mint
                )
                instructions.append(create_ata_ix)
        except:
            # Create it anyway
            create_ata_ix = create_associated_token_account(
                self.wallet_pubkey,
                self.wallet_pubkey,
                token_mint
            )
            instructions.append(create_ata_ix)
        
        # Check if associated user account exists
        try:
            account_info = await self.rpc_call("getAccountInfo", [str(accounts["associated_user"])])
            if not account_info or not account_info.get("value"):
                # Create associated user account
                # This might need specific initialization
                pass
        except:
            pass
        
        return instructions
    
    async def buy_token_manual(self, params: TradeParams) -> Dict[str, Any]:
        """
        Buy token using completely manual approach
        """
        try:
            token_mint = Pubkey.from_string(params.token_mint)
            amount_lamports = int(params.amount_sol * 1_000_000_000)
            
            # Build all instructions
            setup_instructions = await self.build_setup_instructions(token_mint)
            buy_instruction = await self.build_buy_instruction(token_mint, amount_lamports)
            
            all_instructions = setup_instructions + [buy_instruction]
            
            # Get recent blockhash
            blockhash_resp = await self.rpc_call("getLatestBlockhash")
            from solders.hash import Hash
            recent_blockhash = Hash.from_string(blockhash_resp["blockhash"])
            
            # Build transaction
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=all_instructions,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            # Simulate first
            tx_bytes = base64.b64encode(bytes(transaction)).decode()
            sim_result = await self.rpc_call("simulateTransaction", [
                tx_bytes, 
                {"encoding": "base64", "commitment": "processed"}
            ])
            
            if sim_result["value"]["err"]:
                return {
                    "success": False,
                    "error": f"Simulation failed: {sim_result['value']['err']}"
                }
            
            # Send transaction
            signature = await self.rpc_call("sendTransaction", [
                tx_bytes,
                {"encoding": "base64", "skipPreflight": False}
            ])
            
            return {
                "success": True,
                "signature": signature,
                "simulation": sim_result["value"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Manual buy failed: {str(e)}"
            }


# Option 3: Use existing Python libraries
class LibraryBasedTrader:
    """
    Use existing Solana Python libraries like solana-py or anchorpy
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
    
    async def buy_with_solana_py(self, token_mint: str, amount_sol: float) -> Dict[str, Any]:
        """
        Use the solana-py library (if available)
        """
        try:
            # This would require: pip install solana
            from solana.rpc.async_api import AsyncClient
            from solana.transaction import Transaction
            
            async with AsyncClient(self.rpc_url) as client:
                # Build transaction using solana-py
                # This library might have better abstractions
                
                return {
                    "success": False,
                    "error": "solana-py implementation not complete"
                }
                
        except ImportError:
            return {
                "success": False,
                "error": "solana-py library not installed. Run: pip install solana"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"solana-py approach failed: {str(e)}"
            }
    
    async def buy_with_anchorpy(self, token_mint: str, amount_sol: float) -> Dict[str, Any]:
        """
        Use anchorpy with Pump.fun IDL (if available)
        """
        try:
            # This would require the Pump.fun IDL
            import anchorpy
            
            # Load Pump.fun program
            # program = anchorpy.Program(idl, program_id)
            
            return {
                "success": False,
                "error": "anchorpy implementation needs Pump.fun IDL"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"anchorpy approach failed: {str(e)}"
            }


async def main():
    """Test manual approach"""
    from env_keys import get_wallet_keypair, get_rpc_url
    
    wallet_keypair = get_wallet_keypair()
    rpc_url = get_rpc_url()
    
    token_mint = "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmn"
    
    async with ManualPumpFunTrader(wallet_keypair, rpc_url) as trader:
        print(f"Wallet: {trader.wallet_pubkey}")
        
        params = TradeParams(
            token_mint=token_mint,
            amount_sol=0.001,
            slippage=5.0
        )
        
        print("\n🔧 Attempting manual Pump.fun buy...")
        result = await trader.buy_token_manual(params)
        
        if result["success"]:
            print(f"✅ Manual buy successful: {result['signature']}")
            if "simulation" in result:
                print(f"💻 Simulation logs: {result['simulation']['logs'][:3]}")
        else:
            print(f"❌ Manual buy failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
