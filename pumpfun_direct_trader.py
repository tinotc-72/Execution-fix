"""
Direct Pump.fun Trading Library
--- Pump.fun Anchor IDL REQUIRED ---
All instruction construction in this file must use the official Pump.fun Anchor IDL
(discriminator and argument layout from the IDL, not hardcoded or reverse-engineered)
Based on reverse-engineered protocol from successful transactions
"""

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction

import asyncio
import base64
import struct
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.system_program import TransferParams, transfer
from spl.token.instructions import get_associated_token_address, create_associated_token_account
import httpx


@dataclass
class PumpFunTradeResult:
    success: bool
    signature: Optional[str] = None
    error: Optional[str] = None


class DirectPumpFunTrader:
    """
    Direct Pump.fun trader using the actual protocol
    Based on successful mainnet transactions
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Program IDs
        self.PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.ASSOCIATED_TOKEN_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        self.RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        # Hardcoded addresses from successful transactions
        self.GLOBAL_ACCOUNT = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
        
        # Discriminators
        self.BUY_DISCRIMINATOR = bytes.fromhex("66063d1201daebea")
        self.SELL_DISCRIMINATOR = bytes.fromhex("33e685a4017f83ad")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def rpc_request(self, method: str, params: list = None) -> dict:
        """Make RPC request to Solana"""
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        response = await self.client.post(self.rpc_url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            raise Exception(f"RPC error: {data['error']}")
        
        return data["result"]
    
    def derive_pump_pdas(self, token_mint: Pubkey) -> Tuple[Pubkey, Pubkey]:
        """Derive Pump.fun PDAs for a token"""
        # Bonding curve PDA
        bonding_curve, _ = Pubkey.find_program_address(
            [b"bonding-curve", bytes(token_mint)],
            self.PUMP_FUN_PROGRAM
        )
        
        # Associated bonding curve (token account)
        associated_bonding_curve = get_associated_token_address(
            bonding_curve, token_mint
        )
        
        return bonding_curve, associated_bonding_curve
    
    async def buy_token_direct(self, token_mint: str, amount_sol: float) -> BuildResult:
        """
        Buy token using direct Pump.fun protocol
        This approach creates all necessary accounts in a single transaction
        """
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            
            # Derive PDAs
            bonding_curve, associated_bonding_curve = self.derive_pump_pdas(token_mint_pubkey)
            
            # Get user's token account
            user_token_account = get_associated_token_address(
                self.wallet_pubkey, token_mint_pubkey
            )
            
            # Check if user token account exists
            account_info = await self.rpc_request("getAccountInfo", [str(user_token_account)])
            
            instructions = []
            
            # Create token account if it doesn't exist
            if not account_info or not account_info.get("value"):
                create_ata_ix = create_associated_token_account(
                    self.wallet_pubkey,
                    self.wallet_pubkey,
                    token_mint_pubkey
                )
                instructions.append(create_ata_ix)
            
            # Build buy instruction
            amount_lamports = int(amount_sol * 1_000_000_000)
            min_tokens_out = 0  # Accept any amount of tokens
            
            instruction_data = self.BUY_DISCRIMINATOR + struct.pack("<QQ", amount_lamports, min_tokens_out)
            
            # Account list based on successful transactions
            accounts = [
                AccountMeta(self.GLOBAL_ACCOUNT, False, False),
                AccountMeta(self.FEE_RECIPIENT, False, True),
                AccountMeta(token_mint_pubkey, False, False),
                AccountMeta(bonding_curve, False, True),
                AccountMeta(associated_bonding_curve, False, True),
                AccountMeta(user_token_account, False, True),
                AccountMeta(self.wallet_pubkey, True, True),
                AccountMeta(self.SYSTEM_PROGRAM, False, False),
                AccountMeta(self.TOKEN_PROGRAM, False, False),
                AccountMeta(self.ASSOCIATED_TOKEN_PROGRAM, False, False),
                AccountMeta(self.RENT_SYSVAR, False, False),
                AccountMeta(self.PUMP_FUN_PROGRAM, False, False),
            ]
            
            buy_instruction = Instruction(
                program_id=self.PUMP_FUN_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            
            instructions.append(buy_instruction)
            
            # PR-02: Apply compute budget and ATA enforcement
            ixs = with_compute_budget(instructions)
            ixs = ensure_ata_ixs(ixs, self.wallet_pubkey, [token_mint_pubkey])
            
            # PR-02: Build ALTs and recent blockhash
            alts = build_alts_from_tables(ixs)
            recent_blockhash = await get_recent_blockhash()
            
            # PR-02: Compile with ALTs
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=ixs,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=alts
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            # PR-02: Submit with logging
            result = await send_and_confirm_v0_tx(transaction)
            log_submit_result(result, "pumpfun_direct_buy")
            
            return BuildResult(
                ok=result.success,
                tx=result.signature if result.success else None,
                dex="pumpfun",
                action="buy",
                reason=result.error if not result.success else "Direct buy completed"
            )
            
        except Exception as e:
            return BuildResult(
                ok=False,
                tx=None,
                dex="pumpfun",
                action="buy",
                reason=f"Direct buy failed: {str(e)}"
            )
    
    async def sell_token_direct(self, token_mint: str, percentage: float = 100.0) -> BuildResult:
        """
        Sell token using direct Pump.fun protocol
        """
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            
            # Get current token balance
            user_token_account = get_associated_token_address(
                self.wallet_pubkey, token_mint_pubkey
            )
            
            account_info = await self.rpc_request("getAccountInfo", [
                str(user_token_account), {"encoding": "jsonParsed"}
            ])
            
            if not account_info or not account_info.get("value"):
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="pumpfun", 
                    action="sell",
                    reason="No token account found"
                )
            
            token_amount = int(account_info["value"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
            if token_amount <= 0:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="pumpfun",
                    action="sell", 
                    reason="No tokens to sell"
                )
            
            # Calculate amount to sell
            sell_amount = int(token_amount * (percentage / 100.0))
            if sell_amount <= 0:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="pumpfun",
                    action="sell",
                    reason="Invalid sell amount"
                )
            
            # Derive PDAs
            bonding_curve, associated_bonding_curve = self.derive_pump_pdas(token_mint_pubkey)
            
            # Build sell instruction
            min_sol_out = 0  # Accept any amount of SOL
            
            instruction_data = self.SELL_DISCRIMINATOR + struct.pack("<QQ", sell_amount, min_sol_out)
            
            # Account list for sell (similar to buy but different order)
            accounts = [
                AccountMeta(self.GLOBAL_ACCOUNT, False, False),
                AccountMeta(self.FEE_RECIPIENT, False, True),
                AccountMeta(token_mint_pubkey, False, False),
                AccountMeta(bonding_curve, False, True),
                AccountMeta(associated_bonding_curve, False, True),
                AccountMeta(user_token_account, False, True),
                AccountMeta(self.wallet_pubkey, True, True),
                AccountMeta(self.SYSTEM_PROGRAM, False, False),
                AccountMeta(self.TOKEN_PROGRAM, False, False),
                AccountMeta(self.ASSOCIATED_TOKEN_PROGRAM, False, False),
                AccountMeta(self.RENT_SYSVAR, False, False),
                AccountMeta(self.PUMP_FUN_PROGRAM, False, False),
            ]
            
            sell_instruction = Instruction(
                program_id=self.PUMP_FUN_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )
            
            # PR-02: Apply compute budget and ATA enforcement  
            ixs = with_compute_budget([sell_instruction])
            ixs = ensure_ata_ixs(ixs, self.wallet_pubkey, [token_mint_pubkey])
            
            # PR-02: Build ALTs and recent blockhash
            alts = build_alts_from_tables(ixs)
            recent_blockhash = await get_recent_blockhash()
            
            # PR-02: Compile with ALTs
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=ixs,
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=alts
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            # PR-02: Submit with logging
            result = await send_and_confirm_v0_tx(transaction)
            log_submit_result(result, "pumpfun_direct_sell")
            
            return BuildResult(
                ok=result.success,
                tx=result.signature if result.success else None,
                dex="pumpfun",
                action="sell",
                reason=result.error if not result.success else "Direct sell completed"
            )
            
        except Exception as e:
            return BuildResult(
                ok=False,
                tx=None,
                dex="pumpfun",
                action="sell",
                reason=f"Direct sell failed: {str(e)}"
            )


# Option 2: Use a wrapper around existing tools
class PumpFunWrapper:
    """
    Alternative approach: Use command-line tools or existing libraries
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
    
    async def buy_with_solana_cli(self, token_mint: str, amount_sol: float) -> PumpFunTradeResult:
        """
        Use Solana CLI tools (if available)
        This would require the Solana CLI to be installed
        """
        try:
            import subprocess
            
            # This is pseudo-code - you'd need the actual CLI command
            cmd = [
                "solana", "transfer",
                "--from", str(self.wallet_pubkey),
                "--url", self.rpc_url,
                token_mint,
                str(amount_sol)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse signature from output
                signature = result.stdout.strip().split()[-1]
                return PumpFunTradeResult(True, signature=signature)
            else:
                return PumpFunTradeResult(False, error=result.stderr)
                
        except Exception as e:
            return PumpFunTradeResult(False, error=f"CLI approach failed: {str(e)}")


# Option 3: Simplified version that focuses on working patterns
class MinimalPumpFunTrader:
    """
    Minimal implementation focusing only on what we know works
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = rpc_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def copy_successful_transaction(self, original_signature: str, new_amount: float) -> PumpFunTradeResult:
        """
        Copy a successful transaction with a new amount
        This is the most reliable approach - find a working transaction and replicate it
        """
        try:
            # Get the original transaction
            tx_response = await self.client.post(self.rpc_url, json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [original_signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
            })
            
            tx_data = tx_response.json()["result"]
            
            if not tx_data:
                return PumpFunTradeResult(False, error="Could not fetch original transaction")
            
            # Extract the instruction data and modify the amount
            # This would require parsing the transaction and rebuilding it
            # with your wallet and new amount
            
            return PumpFunTradeResult(False, error="Transaction copying not implemented yet")
            
        except Exception as e:
            return PumpFunTradeResult(False, error=f"Copy transaction failed: {str(e)}")


async def main():
    """Test the direct approach"""
    from env_keys import get_wallet_keypair, get_rpc_url
    
    wallet_keypair = get_wallet_keypair()
    rpc_url = get_rpc_url()
    
    token_mint = "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmn"
    
    async with DirectPumpFunTrader(wallet_keypair, rpc_url) as trader:
        print(f"Wallet: {trader.wallet_pubkey}")
        
        # Try direct buy
        print("\n🛒 Attempting direct Pump.fun buy...")
        buy_result = await trader.buy_token_direct(token_mint, 0.001)
        
        if buy_result.success:
            print(f"✅ Direct buy successful: {buy_result.signature}")
        else:
            print(f"❌ Direct buy failed: {buy_result.error}")


if __name__ == "__main__":
    asyncio.run(main())
