#!/usr/bin/env python3
"""
Complete Fresh Buy-Hold-Sell Test
First sells any existing tokens, then does a fresh buy-hold-sell cycle
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

class PumpFunCompleteTrader:
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
        
        # Working addresses for this specific token
        self.token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
        self.bonding_curve = Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb")
        self.bonding_curve_ata = Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz")
        self.our_token_account = get_associated_token_address(self.wallet_pubkey, self.token_mint)
        
        logger.info(f"🤖 Complete PumpFun Trader initialized for wallet: {self.wallet_pubkey}")

    async def get_sol_balance(self) -> float:
        """Get SOL balance of our wallet"""
        try:
            balance = await self.client.get_balance(self.wallet_pubkey)
            return balance.value / 1_000_000_000 if balance.value else 0.0
        except Exception as e:
            logger.error(f"Error getting SOL balance: {e}")
            return 0.0

    async def get_token_balance(self) -> int:
        """Get our token balance"""
        try:
            balance_result = await self.client.get_token_account_balance(self.our_token_account)
            if balance_result.value:
                return int(balance_result.value.amount)
            return 0
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0

    async def sell_all_tokens(self) -> tuple[bool, str]:
        """Sell all tokens we currently have"""
        token_balance = await self.get_token_balance()
        
        if token_balance == 0:
            logger.info("✅ No tokens to sell")
            return True, "No tokens to sell"
        
        logger.info(f"💸 SELLING ALL TOKENS: {token_balance:,}")
        
        try:
            # Build sell instruction accounts
            accounts = [
                AccountMeta(self.global_account, is_signer=False, is_writable=True),
                AccountMeta(self.fee_recipient, is_signer=False, is_writable=True),
                AccountMeta(self.token_mint, is_signer=False, is_writable=False),
                AccountMeta(self.bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(self.bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(self.our_token_account, is_signer=False, is_writable=True),
                AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),
                AccountMeta(self.system_program, is_signer=False, is_writable=False),
                AccountMeta(self.creator_vault, is_signer=False, is_writable=True),
                AccountMeta(self.token_program, is_signer=False, is_writable=False),
                AccountMeta(self.event_authority, is_signer=False, is_writable=False),
                AccountMeta(self.pump_program, is_signer=False, is_writable=False),
            ]
            
            # Create sell instruction data
            discriminator = bytes.fromhex("33e685a4017f83ad")
            min_sol_out = 0
            
            instruction_data = discriminator + struct.pack("<QQ", token_balance, min_sol_out)
            
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
                logger.info(f"✅ Sell all transaction sent: {result.value}")
                await asyncio.sleep(5)  # Wait for confirmation
                
                # Check if tokens were sold
                remaining_balance = await self.get_token_balance()
                tokens_sold = token_balance - remaining_balance
                
                if tokens_sold > 0:
                    logger.info(f"🎉 SELL ALL SUCCESS! Sold {tokens_sold:,} tokens")
                    return True, str(result.value)
                else:
                    logger.error("❌ Sell all failed - no tokens sold")
                    return False, str(result.value)
            else:
                logger.error(f"❌ Sell all transaction failed: {result}")
                return False, "Transaction failed"
                
        except Exception as e:
            logger.error(f"❌ Sell all error: {e}")
            return False, str(e)

    async def buy_tokens(self, sol_amount: float) -> tuple[bool, str]:
        """Buy tokens with specified SOL amount"""
        logger.info(f"💰 BUYING TOKENS with {sol_amount} SOL")
        
        try:
            # Build buy instruction accounts
            accounts = [
                AccountMeta(self.global_account, is_signer=False, is_writable=True),
                AccountMeta(self.fee_recipient, is_signer=False, is_writable=True),
                AccountMeta(self.token_mint, is_signer=False, is_writable=False),
                AccountMeta(self.bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(self.bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(self.our_token_account, is_signer=False, is_writable=True),
                AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),
                AccountMeta(self.system_program, is_signer=False, is_writable=False),
                AccountMeta(self.token_program, is_signer=False, is_writable=False),
                AccountMeta(self.creator_vault, is_signer=False, is_writable=True),
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
                await asyncio.sleep(5)  # Wait for confirmation
                
                # Check if we got tokens
                token_balance = await self.get_token_balance()
                if token_balance > 0:
                    logger.info(f"🎉 BUY SUCCESS! Now have {token_balance:,} tokens")
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

    async def sell_tokens(self, token_amount: int) -> tuple[bool, str]:
        """Sell specific amount of tokens"""
        logger.info(f"💸 SELLING {token_amount:,} TOKENS")
        
        try:
            # Build sell instruction accounts
            accounts = [
                AccountMeta(self.global_account, is_signer=False, is_writable=True),
                AccountMeta(self.fee_recipient, is_signer=False, is_writable=True),
                AccountMeta(self.token_mint, is_signer=False, is_writable=False),
                AccountMeta(self.bonding_curve, is_signer=False, is_writable=True),
                AccountMeta(self.bonding_curve_ata, is_signer=False, is_writable=True),
                AccountMeta(self.our_token_account, is_signer=False, is_writable=True),
                AccountMeta(self.wallet_pubkey, is_signer=True, is_writable=True),
                AccountMeta(self.system_program, is_signer=False, is_writable=False),
                AccountMeta(self.creator_vault, is_signer=False, is_writable=True),
                AccountMeta(self.token_program, is_signer=False, is_writable=False),
                AccountMeta(self.event_authority, is_signer=False, is_writable=False),
                AccountMeta(self.pump_program, is_signer=False, is_writable=False),
            ]
            
            # Create sell instruction data
            discriminator = bytes.fromhex("33e685a4017f83ad")
            min_sol_out = 0
            
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
                await asyncio.sleep(5)  # Wait for confirmation
                
                # Check if tokens were sold
                remaining_balance = await self.get_token_balance()
                tokens_sold = token_amount - remaining_balance if remaining_balance < token_amount else token_amount
                
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

async def test_complete_fresh_cycle():
    """Test a completely fresh buy-hold-sell cycle"""
    
    print("🚀 PUMP.FUN COMPLETE FRESH TRADING CYCLE TEST")
    print("="*80)
    
    sol_amount_to_spend = 0.005  # 0.005 SOL
    hold_duration = 5  # seconds
    
    trader = PumpFunCompleteTrader()
    
    try:
        # === STEP 0: CLEAR ANY EXISTING TOKENS ===
        print("\n🧹 STEP 0: CLEARING ANY EXISTING TOKENS")
        print("-" * 40)
        
        initial_sol = await trader.get_sol_balance()
        initial_tokens = await trader.get_token_balance()
        
        print(f"💰 Initial SOL balance: {initial_sol:.6f} SOL")
        print(f"🪙 Initial token balance: {initial_tokens:,} tokens")
        
        if initial_tokens > 0:
            sell_all_success, sell_all_tx = await trader.sell_all_tokens()
            
            if sell_all_success:
                after_clear_sol = await trader.get_sol_balance()
                after_clear_tokens = await trader.get_token_balance()
                
                print(f"✅ Cleared existing tokens!")
                print(f"💰 SOL balance: {initial_sol:.6f} → {after_clear_sol:.6f} (+{after_clear_sol - initial_sol:.6f})")
                print(f"🪙 Token balance: {initial_tokens:,} → {after_clear_tokens:,} (-{initial_tokens - after_clear_tokens:,})")
                print(f"📝 Clear transaction: {sell_all_tx}")
                
                initial_sol = after_clear_sol
                initial_tokens = after_clear_tokens
            else:
                print(f"❌ Failed to clear existing tokens: {sell_all_tx}")
        else:
            print("✅ No existing tokens to clear")
        
        # === STEP 1: BUY TOKENS ===
        print(f"\n🛒 STEP 1: BUYING {sol_amount_to_spend} SOL worth of tokens")
        print("-" * 40)
        
        buy_success, buy_tx = await trader.buy_tokens(sol_amount_to_spend)
        
        if not buy_success:
            print(f"❌ Buy failed: {buy_tx}")
            return
        
        # Check balances after buy
        after_buy_sol = await trader.get_sol_balance()
        after_buy_tokens = await trader.get_token_balance()
        
        print(f"✅ Buy completed!")
        print(f"💰 SOL balance: {initial_sol:.6f} → {after_buy_sol:.6f} (-{initial_sol - after_buy_sol:.6f})")
        print(f"🪙 Token balance: {initial_tokens:,} → {after_buy_tokens:,} (+{after_buy_tokens - initial_tokens:,})")
        print(f"📝 Buy transaction: {buy_tx}")
        
        if after_buy_tokens <= initial_tokens:
            print("❌ No new tokens were received from buy!")
            return
        
        # === STEP 2: HOLD ===
        print(f"\n⏳ STEP 2: HOLDING tokens for {hold_duration} seconds")
        print("-" * 40)
        
        for i in range(hold_duration):
            print(f"⏰ Holding... {i+1}/{hold_duration} seconds")
            await asyncio.sleep(1)
        
        print("✅ Hold period completed!")
        
        # === STEP 3: SELL ALL TOKENS ===
        print(f"\n💸 STEP 3: SELLING all {after_buy_tokens:,} tokens")
        print("-" * 40)
        
        sell_success, sell_tx = await trader.sell_tokens(after_buy_tokens)
        
        if not sell_success:
            print(f"❌ Sell failed: {sell_tx}")
            return
        
        # Check final balances
        final_sol = await trader.get_sol_balance()
        final_tokens = await trader.get_token_balance()
        
        print(f"✅ Sell completed!")
        print(f"💰 SOL balance: {after_buy_sol:.6f} → {final_sol:.6f} (+{final_sol - after_buy_sol:.6f})")
        print(f"🪙 Token balance: {after_buy_tokens:,} → {final_tokens:,} (-{after_buy_tokens - final_tokens:,})")
        print(f"📝 Sell transaction: {sell_tx}")
        
        # === FINAL SUMMARY ===
        print(f"\n🎯 COMPLETE TRADING CYCLE SUMMARY")
        print("="*80)
        
        total_net_sol_change = final_sol - initial_sol
        total_net_token_change = final_tokens - initial_tokens
        
        print(f"📈 Total net SOL change: {total_net_sol_change:+.6f} SOL")
        print(f"📈 Total net token change: {total_net_token_change:+,} tokens")
        
        if buy_success and sell_success:
            if final_tokens <= initial_tokens:  # All tokens sold
                print("\n🎉🎉🎉 COMPLETE TRADING CYCLE SUCCESS! 🎉🎉🎉")
                print("✅ Clear: SUCCESS")
                print("✅ Buy: SUCCESS")
                print("✅ Hold: SUCCESS") 
                print("✅ Sell: SUCCESS")
                print("🔥🔥 PUMP.FUN DIRECT TRADING BOT IS FULLY FUNCTIONAL! 🔥🔥")
                print("🚀🚀 BUY-HOLD-SELL CYCLE COMPLETED SUCCESSFULLY! 🚀🚀")
            else:
                print("⚠️ PARTIAL SUCCESS - Some tokens remain")
        else:
            print("❌ CYCLE INCOMPLETE")
        
        print(f"\n📊 Transaction Summary:")
        if 'sell_all_tx' in locals() and sell_all_success:
            print(f"🧹 Clear TX: https://solscan.io/tx/{sell_all_tx}")
        print(f"🛒 Buy TX: https://solscan.io/tx/{buy_tx}")
        print(f"💸 Sell TX: https://solscan.io/tx/{sell_tx}")
        
    except Exception as e:
        logger.error(f"❌ Trading cycle error: {e}")
        
    finally:
        await trader.close()

async def main():
    """Main function"""
    await test_complete_fresh_cycle()

if __name__ == "__main__":
    asyncio.run(main())
