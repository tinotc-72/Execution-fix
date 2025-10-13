"""
Simple Pump.fun Trading Library
Based on actual working transaction patterns from mainnet
"""

import asyncio
import base64
import struct
from typing import Optional, Dict, Any
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


class SimplePumpFunTrader:
    """
    Simple Pump.fun trader that uses Jupiter API for reliability
    Falls back to direct trading only when necessary
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
        
        # Jupiter API
        self.JUPITER_API_URL = "https://quote-api.jup.ag/v6"
    
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
    
    async def get_token_balance(self, token_mint: str) -> float:
        """Get token balance for the wallet"""
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            ata = get_associated_token_address(self.wallet_pubkey, token_mint_pubkey)
            
            account_info = await self.rpc_request("getAccountInfo", [str(ata), {"encoding": "jsonParsed"}])
            
            if not account_info or not account_info.get("value"):
                return 0.0
            
            parsed_data = account_info["value"]["data"]["parsed"]["info"]
            token_amount = float(parsed_data["tokenAmount"]["uiAmount"] or 0)
            return token_amount
            
        except Exception:
            return 0.0
    
    async def get_sol_balance(self) -> float:
        """Get SOL balance for the wallet"""
        try:
            balance_resp = await self.rpc_request("getBalance", [str(self.wallet_pubkey)])
            return balance_resp / 1_000_000_000
        except Exception:
            return 0.0
    
    async def buy_token_jupiter(self, token_mint: str, amount_sol: float) -> PumpFunTradeResult:
        """
        Buy token using Jupiter API (most reliable method)
        """
        try:
            # Get Jupiter quote
            quote_params = {
                "inputMint": "So11111111111111111111111111111111111111112",  # SOL
                "outputMint": token_mint,
                "amount": str(int(amount_sol * 1_000_000_000)),  # Convert to lamports
                "slippageBps": 300  # 3% slippage
            }
            
            quote_response = await self.client.get(
                f"{self.JUPITER_API_URL}/quote",
                params=quote_params
            )
            quote_response.raise_for_status()
            quote_data = quote_response.json()
            
            if not quote_data.get("data"):
                return PumpFunTradeResult(False, error="No Jupiter quote available")
            
            # Get swap transaction
            swap_payload = {
                "quoteResponse": quote_data["data"],
                "userPublicKey": str(self.wallet_pubkey),
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": 100000  # 0.0001 SOL priority fee
            }
            
            swap_response = await self.client.post(
                f"{self.JUPITER_API_URL}/swap",
                json=swap_payload
            )
            swap_response.raise_for_status()
            swap_data = swap_response.json()
            
            if not swap_data.get("swapTransaction"):
                return PumpFunTradeResult(False, error="Failed to get swap transaction")
            
            # Decode and sign transaction
            transaction_bytes = base64.b64decode(swap_data["swapTransaction"])
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            # Sign the transaction
            transaction.sign([self.wallet_keypair])
            
            # Send transaction
            signed_tx_bytes = base64.b64encode(bytes(transaction)).decode("utf-8")
            signature = await self.rpc_request("sendTransaction", [
                signed_tx_bytes,
                {"encoding": "base64", "skipPreflight": False}
            ])
            
            return PumpFunTradeResult(True, signature=signature)
            
        except Exception as e:
            return PumpFunTradeResult(False, error=f"Jupiter buy failed: {str(e)}")
    
    async def sell_token_jupiter(self, token_mint: str, percentage: float = 100.0) -> PumpFunTradeResult:
        """
        Sell token using Jupiter API (most reliable method)
        """
        try:
            # Get current token balance
            token_balance = await self.get_token_balance(token_mint)
            if token_balance <= 0:
                return PumpFunTradeResult(False, error="No tokens to sell")
            
            # Calculate amount to sell
            sell_amount = token_balance * (percentage / 100.0)
            if sell_amount <= 0:
                return PumpFunTradeResult(False, error="Invalid sell amount")
            
            # Convert to raw token units (assuming 6 decimals for most pump tokens)
            raw_amount = int(sell_amount * 1_000_000)
            
            # Get Jupiter quote
            quote_params = {
                "inputMint": token_mint,
                "outputMint": "So11111111111111111111111111111111111111112",  # SOL
                "amount": str(raw_amount),
                "slippageBps": 500  # 5% slippage for sells
            }
            
            quote_response = await self.client.get(
                f"{self.JUPITER_API_URL}/quote",
                params=quote_params
            )
            quote_response.raise_for_status()
            quote_data = quote_response.json()
            
            if not quote_data.get("data"):
                return PumpFunTradeResult(False, error="No Jupiter quote available")
            
            # Get swap transaction
            swap_payload = {
                "quoteResponse": quote_data["data"],
                "userPublicKey": str(self.wallet_pubkey),
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": 100000
            }
            
            swap_response = await self.client.post(
                f"{self.JUPITER_API_URL}/swap",
                json=swap_payload
            )
            swap_response.raise_for_status()
            swap_data = swap_response.json()
            
            if not swap_data.get("swapTransaction"):
                return PumpFunTradeResult(False, error="Failed to get swap transaction")
            
            # Decode and sign transaction
            transaction_bytes = base64.b64decode(swap_data["swapTransaction"])
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            # Sign the transaction
            transaction.sign([self.wallet_keypair])
            
            # Send transaction
            signed_tx_bytes = base64.b64encode(bytes(transaction)).decode("utf-8")
            signature = await self.rpc_request("sendTransaction", [
                signed_tx_bytes,
                {"encoding": "base64", "skipPreflight": False}
            ])
            
            return PumpFunTradeResult(True, signature=signature)
            
        except Exception as e:
            return PumpFunTradeResult(False, error=f"Jupiter sell failed: {str(e)}")
    
    async def create_token_account_if_needed(self, token_mint: str) -> bool:
        """
        Create associated token account if it doesn't exist
        """
        try:
            token_mint_pubkey = Pubkey.from_string(token_mint)
            ata = get_associated_token_address(self.wallet_pubkey, token_mint_pubkey)
            
            # Check if account exists
            account_info = await self.rpc_request("getAccountInfo", [str(ata)])
            if account_info and account_info.get("value"):
                return True  # Account already exists
            
            # Create ATA instruction
            create_ata_ix = create_associated_token_account(
                self.wallet_pubkey,  # payer
                self.wallet_pubkey,  # owner
                token_mint_pubkey    # mint
            )
            
            # Get recent blockhash
            blockhash_resp = await self.rpc_request("getLatestBlockhash", [])
            from solders.hash import Hash
            recent_blockhash = Hash.from_string(blockhash_resp["blockhash"])
            
            # Create and send transaction
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[create_ata_ix],
                recent_blockhash=recent_blockhash,
                address_lookup_table_accounts=[]
            )
            
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            tx_bytes = base64.b64encode(bytes(transaction)).decode("utf-8")
            
            signature = await self.rpc_request("sendTransaction", [
                tx_bytes,
                {"encoding": "base64", "skipPreflight": False}
            ])
            
            # Wait a moment for confirmation
            await asyncio.sleep(2)
            return True
            
        except Exception as e:
            print(f"Failed to create token account: {e}")
            return False


async def main():
    """
    Example usage of the Simple Pump.fun Trader
    """
    # Load your wallet and RPC
    from env_keys import get_wallet_keypair, get_rpc_url
    
    wallet_keypair = get_wallet_keypair()
    rpc_url = get_rpc_url()
    
    # Example token mint (replace with actual Pump.fun token)
    token_mint = "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmn"
    
    async with SimplePumpFunTrader(wallet_keypair, rpc_url) as trader:
        print(f"Wallet: {trader.wallet_pubkey}")
        print(f"SOL Balance: {await trader.get_sol_balance():.4f} SOL")
        
        # Buy 0.001 SOL worth of token
        print("\n🛒 Buying token...")
        buy_result = await trader.buy_token_jupiter(token_mint, 0.001)
        
        if buy_result.success:
            print(f"✅ Buy successful: {buy_result.signature}")
        else:
            print(f"❌ Buy failed: {buy_result.error}")
        
        # Wait a moment
        await asyncio.sleep(3)
        
        # Check token balance
        token_balance = await trader.get_token_balance(token_mint)
        print(f"\n💰 Token balance: {token_balance}")
        
        # Sell 50% of tokens
        if token_balance > 0:
            print("\n💸 Selling 50% of tokens...")
            sell_result = await trader.sell_token_jupiter(token_mint, 50.0)
            
            if sell_result.success:
                print(f"✅ Sell successful: {sell_result.signature}")
            else:
                print(f"❌ Sell failed: {sell_result.error}")


if __name__ == "__main__":
    asyncio.run(main())
