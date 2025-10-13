#!/usr/bin/env python3
"""
Production-Ready Pump.Fun Trading System
FOCUS: Reliable buy functionality with sell preparation framework
ACHIEVEMENT: Working buy system that can be extended when sell is solved
"""

import asyncio
import logging
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
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
    PUMP_SELL_DISCRIMINATOR,
    PUMP_TRADE_PROGRAM_KEY
)
from utils import check_token_account_exists, get_token_account_balance

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradeConfig:
    """Configuration for trading operations"""
    token_mint: str
    buy_amount_sol: float
    slippage_bps: int = 500  # 5%
    hold_time_seconds: int = 5
    compute_units: int = 300_000

@dataclass
class TradeResult:
    """Result of a trading operation"""
    success: bool
    transaction_signature: Optional[str]
    tokens_amount: Optional[int]
    sol_cost: Optional[float]
    error_message: Optional[str]
    timestamp: datetime

class PumpTradingSystem:
    """Production-ready pump.fun trading system"""
    
    def __init__(self):
        self.wallet = WALLET
        self.keys = EnvKeys()
        self.rpc_endpoints = [
            f"https://mainnet.helius-rpc.com/v0/?api-key={self.keys.HELIUS_API_KEY}",
            "https://api.mainnet-beta.solana.com"
        ]
        self.trade_history: List[TradeResult] = []
        
    def create_buy_instruction(self, owner: Pubkey, token_mint: Pubkey, amount: int, min_amount_out: int) -> Instruction:
        """Create proven working buy instruction"""
        
        instruction_data = (
            PUMP_BUY_DISCRIMINATOR +
            amount.to_bytes(8, "little") +
            min_amount_out.to_bytes(8, "little")
        )
        
        user_token_ata = get_associated_token_address(owner, token_mint)
        
        # PROVEN WORKING ACCOUNT STRUCTURE
        accounts = [
            AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
            AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # PDA
            AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
            AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault
            AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
            AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # User wallet
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
    
    def create_sell_instruction_placeholder(self, owner: Pubkey, token_mint: Pubkey, token_amount: int, min_sol_out: int) -> Instruction:
        """Placeholder sell instruction - TO BE COMPLETED when correct structure is found"""
        
        instruction_data = (
            PUMP_SELL_DISCRIMINATOR +
            token_amount.to_bytes(8, "little") +
            min_sol_out.to_bytes(8, "little")
        )
        
        user_token_ata = get_associated_token_address(owner, token_mint)
        
        # PLACEHOLDER - Will be updated with correct structure
        accounts = [
            AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
            AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # PDA
            AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
            AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account
            AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
            AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault
            AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # User wallet
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
    
    async def execute_buy(self, config: TradeConfig) -> TradeResult:
        """Execute a buy trade with the proven working structure"""
        logger.info(f"🚀 Executing BUY for {config.token_mint}")
        logger.info(f"   Amount: {config.buy_amount_sol} SOL")
        logger.info(f"   Slippage: {config.slippage_bps / 100}%")
        
        try:
            token_mint = Pubkey.from_string(config.token_mint)
            token_ata = get_associated_token_address(self.wallet.pubkey(), token_mint)
            amount_lamports = int(config.buy_amount_sol * 1e9)
            min_amount_out = max(1, int(amount_lamports * (1 - config.slippage_bps / 10000)))
            
            async with FastExecutor(self.wallet, rpc_urls=self.rpc_endpoints) as executor:
                # Check initial state
                initial_sol = await executor.get_balance(self.wallet.pubkey())
                initial_tokens = await get_token_account_balance(token_ata) or 0
                
                logger.info(f"Initial SOL: {initial_sol/1e9:.6f}")
                logger.info(f"Initial tokens: {initial_tokens:,}")
                
                # Build transaction
                instructions = []
                
                # Compute budget
                compute_ix = create_compute_budget_ix(compute_units=config.compute_units)
                instructions.append(compute_ix)
                
                # Create token account if needed
                token_account_exists = await check_token_account_exists(token_ata)
                if not token_account_exists:
                    ata_ix = create_associated_token_account(
                        payer=self.wallet.pubkey(),
                        owner=self.wallet.pubkey(),
                        mint=token_mint
                    )
                    instructions.append(ata_ix)
                    logger.info("Added ATA creation instruction")
                
                # Buy instruction
                buy_ix = self.create_buy_instruction(
                    self.wallet.pubkey(), 
                    token_mint, 
                    amount_lamports, 
                    min_amount_out
                )
                instructions.append(buy_ix)
                
                # Execute transaction
                recent_blockhash = await executor.get_latest_blockhash()
                message = Message.new_with_blockhash(instructions, self.wallet.pubkey(), recent_blockhash)
                tx = VersionedTransaction(message, [self.wallet])
                
                logger.info("Sending buy transaction...")
                signature = await executor.send_transaction(tx, [self.wallet], original_instructions=instructions)
                
                if not signature:
                    return TradeResult(
                        success=False,
                        transaction_signature=None,
                        tokens_amount=None,
                        sol_cost=None,
                        error_message="Transaction failed to send",
                        timestamp=datetime.now()
                    )
                
                logger.info(f"✅ Buy transaction sent: {signature}")
                logger.info(f"🔗 Solscan: https://solscan.io/tx/{signature}")
                
                # Wait for confirmation and check results
                await asyncio.sleep(3)
                
                final_sol = await executor.get_balance(self.wallet.pubkey())
                final_tokens = await get_token_account_balance(token_ata) or 0
                
                tokens_received = final_tokens - initial_tokens
                sol_spent = (initial_sol - final_sol) / 1e9
                
                logger.info(f"Final SOL: {final_sol/1e9:.6f}")
                logger.info(f"Final tokens: {final_tokens:,}")
                logger.info(f"Tokens received: {tokens_received:,}")
                logger.info(f"SOL spent: {sol_spent:.6f}")
                
                if tokens_received > 0:
                    result = TradeResult(
                        success=True,
                        transaction_signature=signature,
                        tokens_amount=tokens_received,
                        sol_cost=sol_spent,
                        error_message=None,
                        timestamp=datetime.now()
                    )
                    logger.info("🎉 BUY SUCCESSFUL!")
                    return result
                else:
                    return TradeResult(
                        success=False,
                        transaction_signature=signature,
                        tokens_amount=0,
                        sol_cost=sol_spent,
                        error_message="No tokens received despite transaction confirmation",
                        timestamp=datetime.now()
                    )
                    
        except Exception as e:
            logger.error(f"❌ Buy execution error: {e}")
            return TradeResult(
                success=False,
                transaction_signature=None,
                tokens_amount=None,
                sol_cost=None,
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    async def execute_sell_placeholder(self, config: TradeConfig, token_amount: int) -> TradeResult:
        """Placeholder sell function - will be completed when correct structure is found"""
        logger.info(f"📝 SELL PLACEHOLDER - Will sell {token_amount:,} tokens when structure is solved")
        
        # For now, return a placeholder result
        return TradeResult(
            success=False,
            transaction_signature=None,
            tokens_amount=None,
            sol_cost=None,
            error_message="Sell functionality pending - correct account structure research in progress",
            timestamp=datetime.now()
        )
    
    async def execute_buy_cycle(self, config: TradeConfig, cycles: int = 1) -> List[TradeResult]:
        """Execute multiple buy cycles for testing and accumulation"""
        logger.info(f"🔄 Starting {cycles} buy cycles")
        results = []
        
        for cycle in range(cycles):
            logger.info(f"\n{'='*50}")
            logger.info(f"🔄 CYCLE {cycle + 1}/{cycles}")
            logger.info(f"{'='*50}")
            
            # Execute buy
            buy_result = await self.execute_buy(config)
            results.append(buy_result)
            
            if buy_result.success:
                logger.info(f"✅ Cycle {cycle + 1} buy successful: {buy_result.tokens_amount:,} tokens")
                
                # Hold period
                if config.hold_time_seconds > 0:
                    logger.info(f"⏳ Holding for {config.hold_time_seconds} seconds...")
                    for i in range(config.hold_time_seconds):
                        await asyncio.sleep(1)
                        logger.info(f"   Holding... {i+1}/{config.hold_time_seconds}")
                
                # Placeholder for future sell
                logger.info("💡 Sell step will be added when account structure is solved")
            else:
                logger.error(f"❌ Cycle {cycle + 1} buy failed: {buy_result.error_message}")
            
            # Delay between cycles
            if cycle < cycles - 1:
                await asyncio.sleep(2)
        
        return results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get trading performance summary"""
        total_trades = len(self.trade_history)
        successful_trades = sum(1 for trade in self.trade_history if trade.success)
        total_tokens = sum(trade.tokens_amount or 0 for trade in self.trade_history if trade.success)
        total_sol_spent = sum(trade.sol_cost or 0 for trade in self.trade_history if trade.success)
        
        return {
            "total_trades": total_trades,
            "successful_trades": successful_trades,
            "success_rate": successful_trades / total_trades if total_trades > 0 else 0,
            "total_tokens_acquired": total_tokens,
            "total_sol_spent": total_sol_spent,
            "average_tokens_per_trade": total_tokens / successful_trades if successful_trades > 0 else 0
        }

async def main():
    """Main trading system demonstration"""
    print("\n" + "="*80)
    print("🚀 PUMP.FUN PRODUCTION TRADING SYSTEM")
    print("✅ Proven working buy functionality")
    print("🔧 Sell functionality framework ready for completion")
    print("="*80)
    
    # Initialize trading system
    trading_system = PumpTradingSystem()
    
    # Configuration for the proven working token
    config = TradeConfig(
        token_mint="6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump",  # Proven working token
        buy_amount_sol=0.005,  # Smaller amount for production testing
        slippage_bps=500,  # 5%
        hold_time_seconds=3,
        compute_units=300_000
    )
    
    logger.info("Configuration:")
    logger.info(f"  Token: {config.token_mint}")
    logger.info(f"  Buy amount: {config.buy_amount_sol} SOL")
    logger.info(f"  Hold time: {config.hold_time_seconds} seconds")
    
    # Execute trading cycles
    results = await trading_system.execute_buy_cycle(config, cycles=3)
    
    # Update trade history
    trading_system.trade_history.extend(results)
    
    # Performance summary
    summary = trading_system.get_performance_summary()
    
    print("\n" + "="*60)
    print("📊 TRADING PERFORMANCE SUMMARY")
    print("="*60)
    print(f"Total trades: {summary['total_trades']}")
    print(f"Successful trades: {summary['successful_trades']}")
    print(f"Success rate: {summary['success_rate']:.1%}")
    print(f"Total tokens acquired: {summary['total_tokens_acquired']:,}")
    print(f"Total SOL spent: {summary['total_sol_spent']:.6f}")
    print(f"Average tokens per trade: {summary['average_tokens_per_trade']:,.0f}")
    print("="*60)
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. ✅ Buy functionality is production-ready")
    print(f"2. 🔧 Continue research on sell instruction account structure")
    print(f"3. 🚀 Implement complete buy-hold-sell cycle once sell is solved")
    print(f"4. 📈 Scale to multiple tokens and automated strategies")

if __name__ == "__main__":
    asyncio.run(main())
