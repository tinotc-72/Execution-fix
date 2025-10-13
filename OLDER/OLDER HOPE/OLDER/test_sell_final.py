#!/usr/bin/env python3
"""
Final sell test with the correct creator_vault account
"""

import asyncio
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solana.rpc.async_api import AsyncClient
from config import WALLET
from env_keys import EnvKeys
import struct

async def test_sell_with_creator_vault():
    """Test sell with the correct creator_vault account"""
    
    print("🧪 TESTING SELL WITH CREATOR VAULT")
    print("="*80)
    
    # Load our wallet
    wallet_keypair = WALLET
    wallet_pubkey = wallet_keypair.pubkey()
    
    print(f"Our wallet: {wallet_pubkey}")
    
    # All the correct addresses
    global_account = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
    fee_recipient = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    bonding_curve = Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb")
    bonding_curve_ata = Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz")
    our_token_account = Pubkey.from_string("21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG")
    system_program = Pubkey.from_string("11111111111111111111111111111111")
    creator_vault = Pubkey.from_string("Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD")  # The expected creator vault!
    token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    event_authority = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    
    print(f"✅ Using correct creator vault: {creator_vault}")
    
    # Check if creator vault exists
    import aiohttp
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [str(creator_vault), {"encoding": "base64"}]
        }
        
        async with session.post(helius_url, json=payload) as response:
            data = await response.json()
            if 'result' in data and data['result']['value']:
                owner = data['result']['value']['owner']
                print(f"✅ Creator vault exists, owner: {owner}")
            else:
                print(f"❌ Creator vault does not exist!")
    
    print()
    print("Final account order:")
    print(f"0: Global: {global_account}")
    print(f"1: Fee recipient: {fee_recipient}")
    print(f"2: Token mint: {token_mint}")
    print(f"3: Bonding curve: {bonding_curve}")
    print(f"4: Bonding curve ATA: {bonding_curve_ata}")
    print(f"5: Our token account: {our_token_account}")
    print(f"6: Our wallet: {wallet_pubkey}")
    print(f"7: System program: {system_program}")
    print(f"8: Creator vault: {creator_vault}")
    print(f"9: Token program: {token_program}")
    print(f"10: Event authority: {event_authority}")
    print(f"11: Pump program: {pump_program}")
    print()
    
    # Build the sell instruction with ALL correct accounts
    accounts = [
        AccountMeta(global_account, is_signer=False, is_writable=True),        # 0: Global
        AccountMeta(fee_recipient, is_signer=False, is_writable=True),         # 1: Fee recipient
        AccountMeta(token_mint, is_signer=False, is_writable=False),           # 2: Token mint
        AccountMeta(bonding_curve, is_signer=False, is_writable=True),         # 3: Bonding curve
        AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),     # 4: Bonding curve ATA
        AccountMeta(our_token_account, is_signer=False, is_writable=True),     # 5: Our token account
        AccountMeta(wallet_pubkey, is_signer=True, is_writable=True),          # 6: Our wallet (signer)
        AccountMeta(system_program, is_signer=False, is_writable=False),       # 7: System program
        AccountMeta(creator_vault, is_signer=False, is_writable=True),         # 8: Creator vault (CORRECTED!)
        AccountMeta(token_program, is_signer=False, is_writable=False),        # 9: Token program
        AccountMeta(event_authority, is_signer=False, is_writable=False),      # 10: Event authority
        AccountMeta(pump_program, is_signer=False, is_writable=False),         # 11: Pump program
    ]
    
    # Create instruction data for selling our tokens
    discriminator = bytes.fromhex("33e685a4017f83ad")
    token_amount = 20_000_000  # Our current balance
    min_sol_out = 0  # Minimum SOL we want (0 for testing)
    
    instruction_data = discriminator + struct.pack("<QQ", token_amount, min_sol_out)
    
    print(f"Instruction data: {instruction_data.hex()}")
    print(f"Token amount: {token_amount:,}")
    print(f"Min SOL out: {min_sol_out}")
    print()
    
    # Create the instruction
    sell_instruction = Instruction(
        program_id=pump_program,
        accounts=accounts,
        data=instruction_data
    )
    
    # Create and send transaction
    client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
    
    try:
        # Get recent blockhash
        response = await client.get_latest_blockhash()
        recent_blockhash = response.value.blockhash
        
        # Create transaction
        message = Message.new_with_blockhash(
            [sell_instruction],
            wallet_pubkey,
            recent_blockhash
        )
        
        transaction = Transaction.new_unsigned(message)
        transaction.sign([wallet_keypair], recent_blockhash)
        
        print(f"Transaction signature (before sending): {transaction.signatures[0]}")
        
        # Send transaction
        print("📤 Sending FINAL sell transaction...")
        result = await client.send_transaction(transaction)
        
        if result.value:
            print(f"✅ Transaction sent successfully!")
            print(f"Signature: {result.value}")
            
            # Wait a bit and check the result
            await asyncio.sleep(3)
            
            # Get transaction status
            tx_result = await client.get_transaction(result.value, encoding="jsonParsed")
            
            if tx_result.value:
                meta = tx_result.value.transaction.meta
                if meta:
                    if meta.err:
                        print(f"❌ Transaction failed: {meta.err}")
                        
                        # Show logs for debugging
                        if hasattr(meta, 'log_messages') and meta.log_messages:
                            print("\nError logs:")
                            for log in meta.log_messages:
                                print(f"  {log}")
                    else:
                        print("🎉🎉🎉 TRANSACTION SUCCEEDED! 🎉🎉🎉")
                        print("🔥🔥🔥 PUMP.FUN SELL WORKING! 🔥🔥🔥")
                        print("🚀🚀🚀 DIRECT SELL SOLUTION FOUND! 🚀🚀🚀")
                        
                        # Check compute units used
                        compute_units = getattr(meta, 'compute_units_consumed', 0)
                        print(f"Compute units consumed: {compute_units:,}")
                        
                        # Check logs
                        if hasattr(meta, 'log_messages') and meta.log_messages:
                            print("\nSuccess logs:")
                            for log in meta.log_messages:
                                print(f"  {log}")
                        
                        # Check balance changes
                        if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                            print("\nSOL balance changes:")
                            for i, (pre, post) in enumerate(zip(meta.pre_balances, meta.post_balances)):
                                if pre != post:
                                    change = post - pre
                                    print(f"  Account {i}: {pre:,} -> {post:,} ({change:+,} lamports)")
                                    if change > 0 and i == 6:  # Our wallet account
                                        print(f"    💰💰 WE RECEIVED {change/1_000_000_000:.6f} SOL! 💰💰")
                else:
                    print("No transaction metadata available")
            else:
                print("Could not retrieve transaction result")
                
        else:
            print(f"❌ Failed to send transaction: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        await client.close()

async def check_final_balances():
    """Check our final token and SOL balances"""
    
    print("\n🔍 FINAL BALANCE CHECK")
    print("="*80)
    
    client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
    
    try:
        our_token_account = Pubkey.from_string("21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG")
        our_wallet = Pubkey.from_string("A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
        
        # Get token balance
        balance_result = await client.get_token_account_balance(our_token_account)
        
        if balance_result.value:
            amount = balance_result.value.amount
            ui_amount = balance_result.value.ui_amount
            print(f"🪙 Token balance: {amount} raw ({ui_amount} adjusted)")
            
            if amount == "0":
                print("🎉🎉🎉 ALL TOKENS SOLD SUCCESSFULLY! 🎉🎉🎉")
            elif int(amount) < 20_000_000:
                sold = 20_000_000 - int(amount)
                print(f"🎉 PARTIAL SELL SUCCESS! Sold {sold:,} tokens!")
            else:
                print(f"Still have {ui_amount} tokens remaining")
        
        # Get SOL balance
        sol_balance = await client.get_balance(our_wallet)
        if sol_balance.value:
            sol_amount = sol_balance.value / 1_000_000_000
            print(f"💰 SOL balance: {sol_amount:.6f} SOL")
            
    except Exception as e:
        print(f"Error checking balances: {e}")
        
    finally:
        await client.close()

async def main():
    """Main function"""
    await test_sell_with_creator_vault()
    await check_final_balances()
    
    print("\n" + "="*80)
    print("🎊 CONGRATULATIONS! 🎊")
    print("If this worked, we have successfully cracked the pump.fun direct sell!")
    print("This means we can now build a complete buy-hold-sell trading bot!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
