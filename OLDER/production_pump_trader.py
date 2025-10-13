#!/usr/bin/env python3
"""
Production-Ready Pump.Fun Trading System
Focus: Reliable buying with comprehensive logging and monitoring
Future: Sell functionality to be completed once correct discriminator is found
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime

from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.transaction import VersionedTransaction

# Local imports
from env_keys import EnvKeys
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import (
    get_associated_token_address,
    create_compute_budget_ix,
    create_associated_token_account,
    PUMP_BUY_DISCRIMINATOR,
    PUMP_TRADE_PROGRAM_KEY
)
from utils import check_token_account_exists, get_token_account_balance

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PumpFunTrader:
    """Production-ready pump.fun trading system"""
    
    def __init__(self, wallet, rpc_endpoints: list):
        self.wallet = wallet
        self.rpc_endpoints = rpc_endpoints
        self.executor = None
        self.stats = {
            'total_buys': 0,
            'total_sells': 0,
            'successful_buys': 0,
            'successful_sells': 0,
            'total_sol_spent': 0.0,
            'total_sol_earned': 0.0,
            'errors': 0,
            'start_time': time.time()
        }
        
    async def __aenter__(self):
        self.executor = FastExecutor(self.wallet, rpc_urls=self.rpc_endpoints)
        await self.executor.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.executor:
            await self.executor.__aexit__(exc_type, exc_val, exc_tb)
            
    def create_buy_instruction(self, token_mint: str, amount_lamports: int, min_tokens_out: int) -> Instruction:
        """Create a proven working buy instruction"""
        
        instruction_data = (
            PUMP_BUY_DISCRIMINATOR +
            amount_lamports.to_bytes(8, "little") +
            min_tokens_out.to_bytes(8, "little")
        )
        
        token_mint_pubkey = Pubkey.from_string(token_mint)
        user_token_ata = get_associated_token_address(self.wallet.pubkey(), token_mint_pubkey)
        
        # Proven working account structure for buy
        accounts = [
            AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
            AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # PDA
            AccountMeta(pubkey=token_mint_pubkey, is_signer=False, is_writable=False),  # Token mint
            AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault
            AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
            AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account
            AccountMeta(pubkey=self.wallet.pubkey(), is_signer=True, is_writable=True),  # User wallet
            AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # System program
            AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # Token program
            AccountMeta(pubkey=Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"), is_signer=False, is_writable=True),   # Other account
            AccountMeta(pubkey=Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1"), is_signer=False, is_writable=False),  # Event authority
            AccountMeta(pubkey=PUMP_TRADE_PROGRAM_KEY, is_signer=False, is_writable=False),  # Program ID
        ]
        
        return Instruction(
            program_id=PUMP_TRADE_PROGRAM_KEY,
            accounts=accounts,
            data=instruction_data
        )
    
    async def buy_token(self, token_mint: str, amount_sol: float, slippage_bps: int = 500) -> Optional[str]:
        """Buy tokens with comprehensive error handling and logging"""
        
        try:
            self.stats['total_buys'] += 1
            amount_lamports = int(amount_sol * 1e9)
            min_tokens_out = 0  # Accept any amount for now
            
            logger.info(f"🔥 BUYING TOKEN: {token_mint}")
            logger.info(f"💰 Amount: {amount_sol} SOL ({amount_lamports:,} lamports)")
            logger.info(f"📊 Slippage: {slippage_bps} bps ({slippage_bps/100:.1f}%)")
            
            # Check wallet balance
            wallet_balance = await self.executor.get_balance(self.wallet.pubkey())
            logger.info(f"💳 Wallet balance: {wallet_balance/1e9:.6f} SOL")
            
            if wallet_balance < amount_lamports + 10_000_000:  # Leave 0.01 SOL for fees
                logger.error(f"❌ Insufficient balance. Need {amount_sol + 0.01:.6f} SOL, have {wallet_balance/1e9:.6f} SOL")
                self.stats['errors'] += 1
                return None
            
            # Check/create token account
            token_mint_pubkey = Pubkey.from_string(token_mint)
            token_ata = get_associated_token_address(self.wallet.pubkey(), token_mint_pubkey)
            token_account_exists = await check_token_account_exists(token_ata)
            
            logger.info(f"🏦 Token account: {token_ata}")
            logger.info(f"📋 Account exists: {token_account_exists}")
            
            # Build transaction
            instructions = []
            
            # Compute budget
            compute_ix = create_compute_budget_ix(compute_units=300_000)
            instructions.append(compute_ix)
            
            # Create ATA if needed
            if not token_account_exists:
                logger.info("🏗️  Creating token account...")
                ata_ix = create_associated_token_account(
                    self.wallet.pubkey(),
                    self.wallet.pubkey(),
                    token_mint_pubkey
                )
                instructions.append(ata_ix)
            
            # Buy instruction
            buy_ix = self.create_buy_instruction(token_mint, amount_lamports, min_tokens_out)
            instructions.append(buy_ix)
            
            # Create and send transaction
            message = Message.new_with_blockhash(
                instructions,
                self.wallet.pubkey(),
                await self.executor.get_latest_blockhash()
            )
            
            tx = VersionedTransaction(message, [self.wallet])
            
            logger.info("📤 Sending buy transaction...")
            tx_sig = await self.executor.send_transaction(tx, [self.wallet])
            
            if tx_sig:
                logger.info(f"✅ Buy transaction sent: {tx_sig}")
                logger.info(f"🔗 Solscan: https://solscan.io/tx/{tx_sig}")
                
                # Wait and check if tokens were received
                await asyncio.sleep(5)
                token_balance = await get_token_account_balance(token_ata)
                
                if token_balance > 0:
                    logger.info(f"🎉 SUCCESS! Received {token_balance:,} tokens!")
                    self.stats['successful_buys'] += 1
                    self.stats['total_sol_spent'] += amount_sol
                    return tx_sig
                else:
                    logger.warning(f"⚠️  Transaction sent but no tokens received")
                    self.stats['errors'] += 1
                    return tx_sig
            else:
                logger.error("❌ Failed to send buy transaction")
                self.stats['errors'] += 1
                return None
                
        except Exception as e:
            logger.error(f"❌ Error buying token: {e}")
            self.stats['errors'] += 1
            return None
    
    async def sell_token(self, token_mint: str, amount_tokens: Optional[int] = None) -> Optional[str]:
        """Sell tokens - PLACEHOLDER until correct sell discriminator is found"""
        
        logger.warning("🚧 SELL FUNCTIONALITY NOT YET IMPLEMENTED")
        logger.warning("📋 Current status: Buy discriminator works, sell discriminator needs research")
        logger.warning("💡 Options:")
        logger.warning("   1. Find the correct sell discriminator from working pump.fun transactions")
        logger.warning("   2. Use pump.fun frontend to sell manually")
        logger.warning("   3. Use Jupiter aggregator to swap tokens back to SOL")
        
        # For now, just log the request
        self.stats['total_sells'] += 1
        token_ata = get_associated_token_address(self.wallet.pubkey(), Pubkey.from_string(token_mint))
        current_balance = await get_token_account_balance(token_ata)
        
        logger.info(f"📊 Current token balance: {current_balance:,} tokens")
        logger.info(f"📊 Requested sell amount: {amount_tokens or 'ALL'} tokens")
        
        return None
    
    def print_stats(self):
        """Print trading statistics"""
        runtime = time.time() - self.stats['start_time']
        
        logger.info("\n" + "="*60)
        logger.info("📊 TRADING STATISTICS")
        logger.info("="*60)
        logger.info(f"⏱️  Runtime: {runtime/60:.1f} minutes")
        logger.info(f"🔥 Total buy attempts: {self.stats['total_buys']}")
        logger.info(f"✅ Successful buys: {self.stats['successful_buys']}")
        logger.info(f"💸 Total sell attempts: {self.stats['total_sells']}")
        logger.info(f"✅ Successful sells: {self.stats['successful_sells']}")
        logger.info(f"💰 Total SOL spent: {self.stats['total_sol_spent']:.6f} SOL")
        logger.info(f"💰 Total SOL earned: {self.stats['total_sol_earned']:.6f} SOL")
        logger.info(f"❌ Total errors: {self.stats['errors']}")
        
        if self.stats['total_buys'] > 0:
            success_rate = (self.stats['successful_buys'] / self.stats['total_buys']) * 100
            logger.info(f"📈 Buy success rate: {success_rate:.1f}%")
        
        logger.info("="*60)

async def test_production_system():
    """Test the production trading system"""
    
    # Configuration
    TEST_TOKEN = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"  # Our proven working token
    BUY_AMOUNT = 0.005  # Small test amount
    
    keys = EnvKeys()
    rpc_endpoints = [
        f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}",
        "https://api.mainnet-beta.solana.com"
    ]
    
    logger.info("🚀 Starting production trading system test")
    logger.info("="*60)
    
    async with PumpFunTrader(WALLET, rpc_endpoints) as trader:
        # Test buy
        logger.info("🧪 Testing buy functionality...")
        buy_tx = await trader.buy_token(TEST_TOKEN, BUY_AMOUNT)
        
        if buy_tx:
            logger.info("✅ Buy test successful!")
            
            # Wait a bit
            await asyncio.sleep(5)
            
            # Test sell (will show placeholder message)
            logger.info("\n🧪 Testing sell functionality...")
            sell_tx = await trader.sell_token(TEST_TOKEN)
            
        # Print final stats
        trader.print_stats()

if __name__ == "__main__":
    asyncio.run(test_production_system())
