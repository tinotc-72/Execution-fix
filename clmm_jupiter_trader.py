#!/usr/bin/env python3
"""
CLMM Working Trader - Using Jupiter API to execute CLMM trades
Since direct CLMM instruction building is complex, we'll use Jupiter's API for routing
"""

import asyncio
import json
import aiohttp
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.signature import Signature
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Processed
from env_keys import EnvKeys
import base58
import os

# Load environment
env = EnvKeys()

class CLMMJupiterTrader:
    def __init__(self):
        self.client = AsyncClient(env.HELIUS_RPC_URL)
        
        # Load wallet from .env file
        private_key_b58 = os.getenv('PHANTOM_PRIVATE_KEY')
        if not private_key_b58:
            raise ValueError("PHANTOM_PRIVATE_KEY not found in .env file")
        
        decoded_key = base58.b58decode(private_key_b58)
        self.wallet_keypair = Keypair.from_bytes(decoded_key)
        self.wallet_pubkey = self.wallet_keypair.pubkey()
        
        # Token info from your analysis
        self.token_mint = "72jQFwjd14BEhyDfdQsH7D2hS5dN1H6bzsikjkyHyx2D"
        self.sol_mint = "So11111111111111111111111111111111111111112"
        
        print(f"🚀 CLMM Jupiter Trader initialized")
        print(f"   Wallet: {self.wallet_pubkey}")
        print(f"   Token: {self.token_mint}")
    
    async def get_balances(self):
        """Get current balances"""
        try:
            # SOL balance
            sol_balance = await self.client.get_balance(self.wallet_pubkey)
            sol_amount = sol_balance.value / 1_000_000_000 if sol_balance.value else 0.0
            
            # Token balance (if exists)
            try:
                from spl.token.instructions import get_associated_token_address
                token_mint = Pubkey.from_string(self.token_mint)
                token_ata = get_associated_token_address(self.wallet_pubkey, token_mint)
                token_balance = await self.client.get_token_account_balance(token_ata)
                token_amount = float(token_balance.value.ui_amount) if token_balance.value else 0.0
            except:
                token_amount = 0.0
            
            return sol_amount, token_amount
        except Exception as e:
            print(f"❌ Error getting balances: {e}")
            return 0.0, 0.0
    
    async def get_jupiter_quote(self, input_mint: str, output_mint: str, amount: int):
        """Get quote from Jupiter API"""
        try:
            url = "https://quote-api.jup.ag/v6/quote"
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": amount,
                "slippageBps": 500,  # 5% slippage
                "onlyDirectRoutes": False,
                "asLegacyTransaction": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"❌ Quote API error: {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Error getting Jupiter quote: {e}")
            return None
    
    async def get_jupiter_swap_transaction(self, quote_data):
        """Get swap transaction from Jupiter API"""
        try:
            url = "https://quote-api.jup.ag/v6/swap"
            payload = {
                "quoteResponse": quote_data,
                "userPublicKey": str(self.wallet_pubkey),
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": 1000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"❌ Swap API error: {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Error getting Jupiter swap: {e}")
            return None
    
    async def execute_jupiter_trade(self, input_mint: str, output_mint: str, amount: int):
        """Execute trade through Jupiter"""
        try:
            print(f"🔄 Getting Jupiter quote...")
            quote = await self.get_jupiter_quote(input_mint, output_mint, amount)
            
            if not quote:
                print("❌ Failed to get quote")
                return None
            
            print(f"✅ Quote received: {quote.get('outAmount', 'N/A')} output tokens")
            
            # Get swap transaction
            print(f"🔄 Getting swap transaction...")
            swap_data = await self.get_jupiter_swap_transaction(quote)
            
            if not swap_data:
                print("❌ Failed to get swap transaction")
                return None
            
            # Decode and sign transaction
            import base64
            tx_bytes = base64.b64decode(swap_data['swapTransaction'])
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            # Sign with our wallet
            transaction.sign([self.wallet_keypair])
            
            # Send transaction
            print(f"📡 Sending transaction...")
            response = await self.client.send_transaction(
                transaction,
                opts=TxOpts(
                    skip_preflight=True,
                    preflight_commitment=Processed,
                    max_retries=3
                )
            )
            
            if response.value:
                signature = str(response.value)
                print(f"✅ Transaction sent: {signature}")
                return signature
            else:
                print("❌ Failed to send transaction")
                return None
                
        except Exception as e:
            print(f"❌ Error executing Jupiter trade: {e}")
            return None
    
    async def run_buy_hold_sell_cycle(self):
        """Run buy-hold-sell cycle using Jupiter"""
        amount_sol = 0.0001
        amount_lamports = int(amount_sol * 1_000_000_000)
        
        print("🚀 CLMM Jupiter Buy-Hold-Sell Cycle")
        print("=" * 50)
        print(f"💰 Trading amount: {amount_sol} SOL")
        print("⏱️  Hold time: 5 seconds")
        
        # Check initial balances
        print("\n📊 Initial balances:")
        sol_initial, token_initial = await self.get_balances()
        print(f"   SOL: {sol_initial:.6f}")
        print(f"   Token: {token_initial:.6f}")
        
        if sol_initial < amount_sol + 0.01:
            print(f"❌ Insufficient SOL balance")
            return
        
        # STEP 1: BUY (SOL -> Token)
        print(f"\n🛒 STEP 1: BUYING tokens with {amount_sol} SOL...")
        buy_signature = await self.execute_jupiter_trade(
            self.sol_mint,
            self.token_mint,
            amount_lamports
        )
        
        if not buy_signature:
            print("❌ Buy trade failed")
            return
        
        print(f"✅ Buy executed: {buy_signature}")
        
        # Wait for confirmation
        print("⏳ Waiting for confirmation...")
        await asyncio.sleep(5)
        
        # Check balances after buy
        print("\n📊 Balances after buy:")
        sol_after_buy, token_after_buy = await self.get_balances()
        print(f"   SOL: {sol_after_buy:.6f}")
        print(f"   Token: {token_after_buy:.6f}")
        
        if token_after_buy <= token_initial:
            print("❌ No tokens received")
            return
        
        # STEP 2: HOLD
        print(f"\n⏱️  STEP 2: HOLDING for 5 seconds...")
        await asyncio.sleep(5)
        
        # STEP 3: SELL (Token -> SOL)
        print(f"\n💸 STEP 3: SELLING all tokens...")
        
        # Get current token balance for sell
        _, current_token_balance = await self.get_balances()
        if current_token_balance > 0:
            # Convert to raw token amount (assuming 6 decimals for most tokens)
            token_amount_raw = int(current_token_balance * 1_000_000)
            
            sell_signature = await self.execute_jupiter_trade(
                self.token_mint,
                self.sol_mint,
                token_amount_raw
            )
            
            if sell_signature:
                print(f"✅ Sell executed: {sell_signature}")
            else:
                print("❌ Sell trade failed")
        else:
            print("❌ No tokens to sell")
            sell_signature = None
        
        # Wait for final confirmation
        print("⏳ Waiting for final confirmation...")
        await asyncio.sleep(5)
        
        # Final balances
        print("\n📊 Final balances:")
        sol_final, token_final = await self.get_balances()
        print(f"   SOL: {sol_final:.6f}")
        print(f"   Token: {token_final:.6f}")
        
        # Summary
        print(f"\n📈 TRADE CYCLE SUMMARY:")
        print(f"   SOL change: {sol_final - sol_initial:.6f}")
        print(f"   Token change: {token_final - token_initial:.6f}")
        print(f"   Buy signature: {buy_signature}")
        print(f"   Sell signature: {sell_signature}")
        
        if sol_final > sol_initial:
            print("🎉 PROFIT!")
        elif sol_final < sol_initial:
            print("📉 Loss (including fees)")
        else:
            print("⚖️  Break even")
        
        await self.client.close()

async def main():
    trader = CLMMJupiterTrader()
    await trader.run_buy_hold_sell_cycle()

if __name__ == "__main__":
    asyncio.run(main())
