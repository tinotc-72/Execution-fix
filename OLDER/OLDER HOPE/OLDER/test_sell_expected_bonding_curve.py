#!/usr/bin/env python3
"""
Test sell with the expected bonding curve address that the program wants
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

async def test_sell_with_expected_bonding_curve():
    """Test sell with the bonding curve address that the program expects"""
    
    print("🧪 TESTING SELL WITH EXPECTED BONDING CURVE")
    print("="*80)
    
    # Load our wallet
    wallet_keypair = WALLET
    wallet_pubkey = wallet_keypair.pubkey()
    
    print(f"Our wallet: {wallet_pubkey}")
    
    # Use the bonding curve address that the program expects
    global_account = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
    fee_recipient = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    bonding_curve = Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb")  # The expected one!
    our_token_account = Pubkey.from_string("21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG")
    system_program = Pubkey.from_string("11111111111111111111111111111111")
    rent_sysvar = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
    token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    event_authority = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    
    print(f"✅ Using EXPECTED bonding curve: {bonding_curve}")
    
    # We need to derive the associated token account for this bonding curve
    from spl.token.instructions import get_associated_token_address
    bonding_curve_ata = get_associated_token_address(bonding_curve, token_mint)
    
    print(f"✅ Derived bonding curve ATA: {bonding_curve_ata}")
    
    # Check if the bonding curve and its ATA exist
    import aiohttp
    helius_url = f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}"
    
    async with aiohttp.ClientSession() as session:
        # Check bonding curve
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [str(bonding_curve), {"encoding": "base64"}]
        }
        
        async with session.post(helius_url, json=payload) as response:
            data = await response.json()
            if 'result' in data and data['result']['value']:
                owner = data['result']['value']['owner']
                print(f"✅ Bonding curve exists, owner: {owner}")
            else:
                print(f"❌ Bonding curve does not exist!")
                return
        
        # Check bonding curve ATA
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [str(bonding_curve_ata), {"encoding": "base64"}]
        }
        
        async with session.post(helius_url, json=payload) as response:
            data = await response.json()
            if 'result' in data and data['result']['value']:
                owner = data['result']['value']['owner']
                print(f"✅ Bonding curve ATA exists, owner: {owner}")
            else:
                print(f"❌ Bonding curve ATA does not exist - creating it should be automatic")
    
    print()
    print("Account order:")
    print(f"0: Global: {global_account}")
    print(f"1: Fee recipient: {fee_recipient}")
    print(f"2: Token mint: {token_mint}")
    print(f"3: Bonding curve: {bonding_curve}")
    print(f"4: Bonding curve ATA: {bonding_curve_ata}")
    print(f"5: Our token account: {our_token_account}")
    print(f"6: Our wallet: {wallet_pubkey}")
    print(f"7: System program: {system_program}")
    print(f"8: Rent sysvar: {rent_sysvar}")
    print(f"9: Token program: {token_program}")
    print(f"10: Event authority: {event_authority}")
    print(f"11: Pump program: {pump_program}")
    print()
    
    # Build the sell instruction with corrected bonding curve
    accounts = [
        AccountMeta(global_account, is_signer=False, is_writable=True),        # 0: Global
        AccountMeta(fee_recipient, is_signer=False, is_writable=True),         # 1: Fee recipient
        AccountMeta(token_mint, is_signer=False, is_writable=False),           # 2: Token mint
        AccountMeta(bonding_curve, is_signer=False, is_writable=True),         # 3: Bonding curve (CORRECTED!)
        AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),     # 4: Bonding curve ATA (CORRECTED!)
        AccountMeta(our_token_account, is_signer=False, is_writable=True),     # 5: Our token account
        AccountMeta(wallet_pubkey, is_signer=True, is_writable=True),          # 6: Our wallet (signer)
        AccountMeta(system_program, is_signer=False, is_writable=False),       # 7: System program
        AccountMeta(rent_sysvar, is_signer=False, is_writable=False),          # 8: Rent sysvar
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
        print("📤 Sending sell transaction with expected bonding curve...")
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
                        print("🎉🎉 TRANSACTION SUCCEEDED! 🎉🎉")
                        print("🔥🔥 PUMP.FUN SELL WORKING! 🔥🔥")
                        
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
                                    if change > 0:
                                        print(f"    💰 Received {change/1_000_000_000:.6f} SOL")
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

async def check_token_balance():
    """Check our token balance"""
    
    print("\n🔍 CHECKING TOKEN BALANCE AFTER TRANSACTION")
    print("="*80)
    
    client = AsyncClient(EnvKeys().HELIUS_RPC_URL)
    
    try:
        our_token_account = Pubkey.from_string("21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG")
        
        # Get current balance
        balance_result = await client.get_token_account_balance(our_token_account)
        
        if balance_result.value:
            amount = balance_result.value.amount
            ui_amount = balance_result.value.ui_amount
            print(f"Current token balance: {amount} raw ({ui_amount} adjusted)")
            
            if amount == "0":
                print("🎉🎉 TOKENS SOLD SUCCESSFULLY! Balance is now 0! 🎉🎉")
            elif int(amount) < 20_000_000:
                sold = 20_000_000 - int(amount)
                print(f"🎉 PARTIAL SELL SUCCESS! Sold {sold:,} tokens!")
            else:
                print(f"Still have {ui_amount} tokens remaining")
        else:
            print("Could not get token balance")
            
    except Exception as e:
        print(f"Error checking balance: {e}")
        
    finally:
        await client.close()

async def main():
    """Main function"""
    await test_sell_with_expected_bonding_curve()
    await check_token_balance()

if __name__ == "__main__":
    asyncio.run(main())
