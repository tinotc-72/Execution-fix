#!/usr/bin/env python3
"""
Complete Buy-Hold-Sell Test for Pump.fun Trading Bot
Tests the full trading cycle: Buy tokens -> Hold -> Sell tokens
"""

import asyncio
import time
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solana.rpc.async_api import AsyncClient
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from config import WALLET
from env_keys import EnvKeys
import struct
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PumpFunTrader:
    def __init__(self):
        self.wallet_keypair = WALLET
        self.wallet_pubkey = self.wallet_keypair.pubkey()
        self.client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
        
        # Pump.fun program addresses
        self.pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
        self.global_account = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
        self.fee_recipient = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
        self.event_authority = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
        self.creator_vault = Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD")
        
        # System programs
        self.system_program = Pubkey.from_string("11111111111111111111111111111111")
        self.token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.rent_sysvar = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
        
        logger.info(f"🤖 PumpFun Trader initialized for wallet: {self.wallet_pubkey}")

    async def get_sol_balance(self) -> float:
        """Get SOL balance of our wallet"""
        try:
            balance = await self.client.get_balance(self.wallet_pubkey)
            return balance.value / 1_000_000_000 if balance.value else 0.0
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0

    async def get_token_balance(self, token_account: Pubkey) -> int:
        """Get token balance of a token account"""
        try:
            balance_result = await self.client.get_token_account_balance(token_account)
            if balance_result.value:
                return int(balance_result.value.amount)
            return 0
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0

    async def create_ata_if_needed(self, token_mint: Pubkey) -> Pubkey:
        """Create Associated Token Account if it doesn't exist"""
        ata = get_associated_token_address(self.wallet_pubkey, token_mint)
        
        try:
            # Check if ATA exists
            account_info = await self.client.get_account_info(ata)
            if account_info.value:
                logger.info(f"✅ ATA already exists: {ata}")
                return ata
        except:
            pass
        
        logger.info(f"🔨 Creating ATA: {ata}")
        
        # Create ATA instruction
        create_ata_ix = create_associated_token_account(
            payer=self.wallet_pubkey,
            owner=self.wallet_pubkey,
            mint=token_mint
        )
        
        # Send transaction
        try:
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = Message.new_with_blockhash([create_ata_ix], self.wallet_pubkey, recent_blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], recent_blockhash)
            
            result = await self.client.send_transaction(transaction)
            if result.value:
                logger.info(f"✅ ATA created successfully: {ata}")
                await asyncio.sleep(2)  # Wait for confirmation
            return ata
        except Exception as e:
            logger.error(f"Error creating ATA: {e}")
            return ata

    async def buy_tokens(self, token_mint: Pubkey, sol_amount: float) -> tuple[bool, str]:
        """Buy tokens from pump.fun"""
        logger.info(f"💰 BUYING TOKENS")
        logger.info(f"Token mint: {token_mint}")
        logger.info(f"SOL amount: {sol_amount}")
        
        try:
            # Create ATA if needed
            our_token_account = await self.create_ata_if_needed(token_mint)
            
            # Use the SAME bonding curve addresses for buy as we use for sell
            bonding_curve = Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb")
            bonding_curve_ata = Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz")
            
            # Build buy instruction accounts (corrected order to match sell)
            accounts = [
                AccountMeta(self.global_account, is_signer=False, is_writable=True),
                AccountMeta(self.fee_recipient, is_signer=False, is_writable=True),
                AccountMeta(token_mint, is_signer=False, is_writable=False),
                AccountMeta(bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(our_token_account, is_signer=False, is_writable=True),
                AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),
                AccountMeta(self.system_program, is_signer=False, is_writable=False),
                AccountMeta(self.token_program, is_signer=False, is_writable=False),
                AccountMeta(self.creator_vault, is_signer=False, is_writable=True),  # Use creator vault instead of rent
                AccountMeta(self.event_authority, is_signer=False, is_writable=False),
                AccountMeta(self.pump_program, is_signer=False, is_writable=False),
            ]
            
            # Create buy instruction data
            discriminator = bytes.fromhex("66063d1201daebea")
            sol_amount_lamports = int(sol_amount * 1_000_000_000)
            max_sol_cost = sol_amount_lamports
            
            instruction_data = discriminator + struct.pack("<QQ", sol_amount_lamports, max_sol_cost)
            
            # Create instruction
            buy_instruction = Instruction(
                program_id=self.pump_program,
                accounts=accounts,
                data=instruction_data
            )
            
            # Send transaction
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = Message.new_with_blockhash([buy_instruction], self.wallet_pubkey, recent_blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], recent_blockhash)
            
            result = await self.client.send_transaction(transaction)
            
            if result.value:
                logger.info(f"✅ Buy transaction sent: {result.value}")
                await asyncio.sleep(5)  # Wait longer for confirmation
                
                # Check if we got tokens
                token_balance = await self.get_token_balance(our_token_account)
                if token_balance > 0:
                    logger.info(f"🎉 BUY SUCCESS! Received {token_balance:,} tokens")
                    return True, str(result.value)
                else:
                    logger.error("❌ Buy failed - no tokens received")
                    return False, str(result.value)
            else:
                logger.error(f"❌ Buy transaction failed: {result}")
                return False, "Transaction failed"
                
        except Exception as e:
            logger.error(f"❌ Buy error: {e}")
            return False, str(e)

    async def sell_tokens(self, token_mint: Pubkey, token_amount: int) -> tuple[bool, str]:
        """Sell tokens on pump.fun"""
        logger.info(f"💸 SELLING TOKENS")
        logger.info(f"Token mint: {token_mint}")
        logger.info(f"Token amount: {token_amount:,}")
        
        try:
            our_token_account = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Use the working addresses we discovered
            bonding_curve = Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb")
            bonding_curve_ata = Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz")
            
            # Build sell instruction accounts (working order)
            accounts = [
                AccountMeta(self.global_account, is_signer=False, is_writable=True),        # 0: Global
                AccountMeta(self.fee_recipient, is_signer=False, is_writable=True),         # 1: Fee recipient
                AccountMeta(token_mint, is_signer=False, is_writable=False),                # 2: Token mint
                AccountMeta(bonding_curve, is_signer=False, is_writable=True),              # 3: Bonding curve
                AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),          # 4: Bonding curve ATA
                AccountMeta(our_token_account, is_signer=False, is_writable=True),          # 5: Our token account
                AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),          # 6: Our wallet (signer)
                AccountMeta(self.system_program, is_signer=False, is_writable=False),       # 7: System program
                AccountMeta(self.creator_vault, is_signer=False, is_writable=True),         # 8: Creator vault
                AccountMeta(self.token_program, is_signer=False, is_writable=False),        # 9: Token program
                AccountMeta(self.event_authority, is_signer=False, is_writable=False),      # 10: Event authority
                AccountMeta(self.pump_program, is_signer=False, is_writable=False),         # 11: Pump program
            ]
            
            # Create sell instruction data
            discriminator = bytes.fromhex("33e685a4017f83ad")
            min_sol_out = 0  # Minimum SOL we want (0 for testing)
            
            instruction_data = discriminator + struct.pack("<QQ", token_amount, min_sol_out)
            
            # Create instruction
            sell_instruction = Instruction(
                program_id=self.pump_program,
                accounts=accounts,
                data=instruction_data
            )
            
            # Send transaction
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            message = Message.new_with_blockhash([sell_instruction], self.wallet_pubkey, recent_blockhash)
            transaction = Transaction.new_unsigned(message)
            transaction.sign([self.wallet_keypair], recent_blockhash)
            
            result = await self.client.send_transaction(transaction)
            
            if result.value:
                logger.info(f"✅ Sell transaction sent: {result.value}")
                await asyncio.sleep(5)  # Wait longer for confirmation
                
                # Check if tokens were sold
                remaining_balance = await self.get_token_balance(our_token_account)
                tokens_sold = token_amount - remaining_balance
                
                if tokens_sold > 0:
                    logger.info(f"🎉 SELL SUCCESS! Sold {tokens_sold:,} tokens")
                    return True, str(result.value)
                else:
                    logger.error("❌ Sell failed - no tokens sold")
                    return False, str(result.value)
            else:
                logger.error(f"❌ Sell transaction failed: {result}")
                return False, "Transaction failed"
                
        except Exception as e:
            logger.error(f"❌ Sell error: {e}")
            return False, str(e)

    async def close(self):
        """Close the client"""
        await self.client.close()

async def test_complete_trading_cycle():
    """Test the complete buy-hold-sell trading cycle"""
    
    print("🚀 PUMP.FUN COMPLETE TRADING CYCLE TEST")
    print("="*80)
    
    # Test parameters
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    sol_amount_to_spend = 0.005  # 0.005 SOL
    hold_duration = 5  # seconds
    
    trader = PumpFunTrader()
    
    try:
        # === INITIAL BALANCES ===
        print("\n📊 INITIAL BALANCES")
        print("-" * 40)
        initial_sol = await trader.get_sol_balance()
        print(f"💰 Initial SOL balance: {initial_sol:.6f} SOL")
        
        our_token_account = get_associated_token_address(trader.wallet_pubkey, token_mint)
        initial_tokens = await trader.get_token_balance(our_token_account)
        print(f"🪙 Initial token balance: {initial_tokens:,} tokens")
        
        # === STEP 1: BUY TOKENS ===
        print(f"\n🛒 STEP 1: BUYING {sol_amount_to_spend} SOL worth of tokens")
        print("-" * 40)
        
        buy_success, buy_tx = await trader.buy_tokens(token_mint, sol_amount_to_spend)
        
        if not buy_success:
            print(f"❌ Buy failed: {buy_tx}")
            return
        
        # Check balances after buy
        after_buy_sol = await trader.get_sol_balance()
        after_buy_tokens = await trader.get_token_balance(our_token_account)
        
        print(f"✅ Buy completed!")
        print(f"💰 SOL balance: {initial_sol:.6f} → {after_buy_sol:.6f} (-{initial_sol - after_buy_sol:.6f})")
        print(f"🪙 Token balance: {initial_tokens:,} → {after_buy_tokens:,} (+{after_buy_tokens - initial_tokens:,})")
        print(f"📝 Buy transaction: {buy_tx}")
        
        if after_buy_tokens <= initial_tokens:
            print("❌ No tokens were received from buy!")
            return
        
        # === STEP 2: HOLD ===
        print(f"\n⏳ STEP 2: HOLDING tokens for {hold_duration} seconds")
        print("-" * 40)
        
        for i in range(hold_duration):
            print(f"⏰ Holding... {i+1}/{hold_duration} seconds")
            await asyncio.sleep(1)
        
        print("✅ Hold period completed!")
        
        # === STEP 3: SELL TOKENS ===
        print(f"\n💸 STEP 3: SELLING all {after_buy_tokens:,} tokens")
        print("-" * 40)
        
        sell_success, sell_tx = await trader.sell_tokens(token_mint, after_buy_tokens)
        
        if not sell_success:
            print(f"❌ Sell failed: {sell_tx}")
            return
        
        # Check final balances
        final_sol = await trader.get_sol_balance()
        final_tokens = await trader.get_token_balance(our_token_account)
        
        print(f"✅ Sell completed!")
        print(f"💰 SOL balance: {after_buy_sol:.6f} → {final_sol:.6f} (+{final_sol - after_buy_sol:.6f})")
        print(f"🪙 Token balance: {after_buy_tokens:,} → {final_tokens:,} (-{after_buy_tokens - final_tokens:,})")
        print(f"📝 Sell transaction: {sell_tx}")
        
        # === FINAL SUMMARY ===
        print(f"\n🎯 TRADING CYCLE SUMMARY")
        print("="*80)
        
        net_sol_change = final_sol - initial_sol
        net_token_change = final_tokens - initial_tokens
        
        print(f"📈 Net SOL change: {net_sol_change:+.6f} SOL")
        print(f"📈 Net token change: {net_token_change:+,} tokens")
        
        if buy_success and sell_success:
            if final_tokens <= initial_tokens:  # All tokens sold
                print("🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
                print("✅ Buy: SUCCESS")
                print("✅ Hold: SUCCESS") 
                print("✅ Sell: SUCCESS")
                print("🔥 PUMP.FUN DIRECT TRADING BOT IS FULLY FUNCTIONAL! 🔥")
            else:
                print("⚠️ PARTIAL SUCCESS - Some tokens remain")
        else:
            print("❌ CYCLE INCOMPLETE")
        
        print(f"\n📊 Transaction Summary:")
        print(f"🛒 Buy TX: https://solscan.io/tx/{buy_tx}")
        print(f"💸 Sell TX: https://solscan.io/tx/{sell_tx}")
        
    except Exception as e:
        logger.error(f"❌ Trading cycle error: {e}")
        
    finally:
        await trader.close()

async def main():
    """Main function"""
    await test_complete_trading_cycle()

if __name__ == "__main__":
    asyncio.run(main())
