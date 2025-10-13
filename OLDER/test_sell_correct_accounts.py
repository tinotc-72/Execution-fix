#!/usr/bin/env python3
"""
Test sell transaction with correctly derived accounts
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

async def test_sell_with_correct_accounts():
    """Test sell with the correct account structure for our wallet"""
    
    print("🧪 TESTING SELL WITH CORRECT ACCOUNTS")
    print("="*80)
    
    # Load our wallet
    wallet_keypair = WALLET
    wallet_pubkey = wallet_keypair.pubkey()
    
    print(f"Our wallet: {wallet_pubkey}")
    
    # Correct addresses for our transaction
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    our_token_account = Pubkey.from_string("21g4V3k7T3C95PXNvTMvvbm33dj7tsZPKAQzw4mVZ9eG")
    bonding_curve = Pubkey.from_string("EAgio9owovfTwneWhv3SZrbEaPCj23QJ5C8JDN5XdyyV")
    bonding_curve_ata = Pubkey.from_string("AQPLuT1nZPFXsJ47JSk7LFVLYopnmC1FPh5fgzKaXFUZ")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    pump_fee_recipient = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
    system_program = Pubkey.from_string("11111111111111111111111111111111")
    token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    event_authority = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
    program_data = Pubkey.from_string("8WHNZ5pwqy6ZgS8jJUjtT3MKoSNWoAp4LCpm8hNHaWfN")
    
    # Build the sell instruction with correct accounts
    accounts = [
        AccountMeta(pump_fee_recipient, is_signer=False, is_writable=True),    # Global
        AccountMeta(pump_fee_recipient, is_signer=False, is_writable=True),    # Fee recipient  
        AccountMeta(token_mint, is_signer=False, is_writable=False),           # Token mint
        AccountMeta(bonding_curve, is_signer=False, is_writable=True),         # Bonding curve
        AccountMeta(bonding_curve_ata, is_signer=False, is_writable=True),     # Bonding curve token account
        AccountMeta(our_token_account, is_signer=False, is_writable=True),     # User token account (OUR ATA!)
        AccountMeta(wallet_pubkey, is_signer=True, is_writable=True),          # User wallet (signer)
        AccountMeta(system_program, is_signer=False, is_writable=False),       # System program
        AccountMeta(token_program, is_signer=False, is_writable=False),        # Token program
        AccountMeta(event_authority, is_signer=False, is_writable=False),      # Event authority
        AccountMeta(pump_program, is_signer=False, is_writable=False),         # Pump program
        AccountMeta(program_data, is_signer=False, is_writable=False),         # Program data
    ]
    
    # Create instruction data for selling our tokens
    discriminator = bytes.fromhex("33e685a4017f83ad")
    token_amount = 20_000_000  # Our current balance
    min_sol_out = 0  # Minimum SOL we want (0 for testing)
    
    instruction_data = discriminator + struct.pack("<QQ", token_amount, min_sol_out)
    
    print(f"Instruction data: {instruction_data.hex()}")
    print(f"Token amount: {token_amount:,}")
    print(f"Min SOL out: {min_sol_out}")
    
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
        print("📤 Sending sell transaction...")
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
                    else:
                        print("✅ Transaction succeeded!")
                        
                        # Check compute units used
                        compute_units = getattr(meta, 'compute_units_consumed', 0)
                        print(f"Compute units consumed: {compute_units:,}")
                        
                        if compute_units > 0:
                            print("🎉 PUMP.FUN PROGRAM WAS INVOKED!")
                        else:
                            print("⚠️ No compute units - program not invoked")
                        
                        # Check logs
                        if hasattr(meta, 'log_messages') and meta.log_messages:
                            print("\nProgram logs:")
                            for log in meta.log_messages:
                                if "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P" in log:
                                    print(f"  PUMP: {log}")
                                else:
                                    print(f"  {log}")
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

async def main():
    """Main function"""
    await test_sell_with_correct_accounts()

if __name__ == "__main__":
    asyncio.run(main())
