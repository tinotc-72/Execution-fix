#!/usr/bin/env python3
"""
Test the most likely sell discriminators based on Solana program patterns
Focus on finding the working sell instruction
"""

import asyncio
import logging
import hashlib
from typing import List, Optional

from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.transaction import VersionedTransaction

# Local imports
from config import WALLET
from fast_executor import FastExecutor
from minimal_tx_builder import (
    get_associated_token_address,
    create_compute_budget_ix,
    PUMP_TRADE_PROGRAM_KEY
)
from utils import get_token_account_balance
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
RPC_ENDPOINTS = [
    f"https://mainnet.helius-rpc.com/v0/?api-key={EnvKeys().HELIUS_API_KEY}",
    "https://api.mainnet-beta.solana.com"
]

# Calculate discriminators using different methods that are commonly used
def generate_discriminators() -> List[tuple]:
    """Generate potential discriminators using various methods"""
    discriminators = []
    
    # Method 1: Standard Anchor patterns
    anchor_patterns = [
        "global:sell",
        "global:swap", 
        "global:trade",
        "global:exit",
        "global:redeem"
    ]
    
    for pattern in anchor_patterns:
        disc = hashlib.sha256(pattern.encode()).digest()[:8].hex()
        discriminators.append((pattern, disc))
    
    # Method 2: No namespace patterns
    simple_patterns = [
        "sell",
        "swap", 
        "trade",
        "exit",
        "redeem",
        "withdraw"
    ]
    
    for pattern in simple_patterns:
        disc = hashlib.sha256(pattern.encode()).digest()[:8].hex()
        discriminators.append((f"simple:{pattern}", disc))
    
    # Method 3: Pump-specific patterns
    pump_patterns = [
        "pump:sell",
        "pump:swap",
        "pump:trade",
        "token:sell",
        "market:sell"
    ]
    
    for pattern in pump_patterns:
        disc = hashlib.sha256(pattern.encode()).digest()[:8].hex()
        discriminators.append((pattern, disc))
    
    # Method 4: Common hex patterns found in other programs
    known_patterns = [
        ("raydium_sell", "f8c69e91e17587c8"),  # Common Raydium pattern
        ("jupiter_swap", "e445a52e51cb9a1d"),  # Common Jupiter pattern  
        ("orca_swap", "2bb96458047b3b3b"),     # Common Orca pattern
        ("pump_sell_v1", "33e685a4017f83ad"),  # Our previous attempt
        ("pump_sell_v2", "b712469c946da122"),  # Alternative attempt
    ]
    
    discriminators.extend(known_patterns)
    
    return discriminators

def create_sell_instruction_test(owner: Pubkey, token_amount: int, min_sol_out: int, discriminator: str) -> Instruction:
    """Create sell instruction for testing"""
    
    instruction_data = (
        bytes.fromhex(discriminator) +
        token_amount.to_bytes(8, "little") +
        min_sol_out.to_bytes(8, "little")
    )
    
    token_mint = Pubkey.from_string(TOKEN_MINT)
    user_token_ata = get_associated_token_address(owner, token_mint)
    
    # Use the same account structure as buy but with user_ata and token_vault swapped
    accounts = [
        AccountMeta(pubkey=Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf"), is_signer=False, is_writable=False),  # Config
        AccountMeta(pubkey=Pubkey.from_string("G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP"), is_signer=False, is_writable=True),   # PDA
        AccountMeta(pubkey=token_mint, is_signer=False, is_writable=False),  # Token mint
        AccountMeta(pubkey=user_token_ata, is_signer=False, is_writable=True),  # User token account (swapped from buy)
        AccountMeta(pubkey=Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"), is_signer=False, is_writable=True),   # Route state
        AccountMeta(pubkey=Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"), is_signer=False, is_writable=True),   # Token vault (swapped from buy)
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

async def test_discriminators():
    """Test each discriminator to find the working one"""
    logger.info("🧪 Testing discriminators to find working sell instruction")
    logger.info("=" * 60)
    
    discriminators = generate_discriminators()
    logger.info(f"📊 Testing {len(discriminators)} discriminators")
    
    try:
        wallet = WALLET
        token_mint = Pubkey.from_string(TOKEN_MINT)
        token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
        
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # Check current token balance
            initial_balance = await get_token_account_balance(token_ata)
            logger.info(f"💰 Current token balance: {initial_balance:,} tokens")
            
            if initial_balance == 0:
                logger.warning("❌ No tokens to sell! Need to buy some first.")
                return None
            
            # Test with a small amount
            test_amount = min(1000, initial_balance)  # Sell max 1000 tokens
            min_sol_out = 0  # Accept any amount of SOL
            
            logger.info(f"🧪 Testing sell of {test_amount:,} tokens")
            
            # Test each discriminator
            for i, (pattern, discriminator) in enumerate(discriminators):
                logger.info(f"\n🔍 Test {i+1}/{len(discriminators)}: {pattern}")
                logger.info(f"   Discriminator: {discriminator}")
                
                try:
                    # Build transaction
                    instructions = []
                    
                    # Compute budget
                    compute_ix = create_compute_budget_ix(compute_units=300_000)
                    instructions.append(compute_ix)
                    
                    # Sell instruction
                    sell_ix = create_sell_instruction_test(
                        wallet.pubkey(),
                        test_amount,
                        min_sol_out, 
                        discriminator
                    )
                    instructions.append(sell_ix)
                    
                    # Create transaction
                    message = Message.new_with_blockhash(
                        instructions,
                        wallet.pubkey(),
                        await executor.get_latest_blockhash()
                    )
                    
                    tx = VersionedTransaction(message, [wallet])
                    
                    # Send transaction
                    tx_sig = await executor.send_transaction(tx, [wallet])
                    
                    if tx_sig:
                        logger.info(f"   ✅ Transaction sent: {tx_sig}")
                        logger.info(f"   🔗 Solscan: https://solscan.io/tx/{tx_sig}")
                        
                        # Wait and check if tokens were sold
                        await asyncio.sleep(3)
                        new_balance = await get_token_account_balance(token_ata)
                        
                        if new_balance < initial_balance:
                            tokens_sold = initial_balance - new_balance
                            logger.info(f"   🎉 SUCCESS! FOUND WORKING DISCRIMINATOR!")
                            logger.info(f"   🏆 Pattern: {pattern}")
                            logger.info(f"   🔑 Discriminator: {discriminator}")
                            logger.info(f"   💰 Tokens sold: {tokens_sold:,}")
                            logger.info(f"   💰 Remaining: {new_balance:,}")
                            
                            return {
                                "pattern": pattern,
                                "discriminator": discriminator,
                                "tx_signature": tx_sig,
                                "tokens_sold": tokens_sold
                            }
                        else:
                            logger.info(f"   ⚠️  No tokens sold (balance: {new_balance:,})")
                    else:
                        logger.info(f"   ❌ Transaction failed to send")
                        
                except Exception as e:
                    logger.info(f"   ❌ Error: {e}")
                    
                # Small delay between tests
                await asyncio.sleep(1)
            
            logger.warning("\n❌ No working discriminator found")
            return None
        
    except Exception as e:
        logger.error(f"❌ Error in testing: {e}")
        raise

async def main():
    """Main function"""
    logger.info("🚀 Starting discriminator testing for pump.fun sell")
    
    try:
        result = await test_discriminators()
        
        if result:
            logger.info(f"\n🎉 SUCCESS! Found working sell discriminator:")
            logger.info(f"🏷️  Pattern: {result['pattern']}")
            logger.info(f"🔑 Discriminator: {result['discriminator']}")
            logger.info(f"📝 Transaction: {result['tx_signature']}")
            logger.info(f"💰 Tokens sold: {result['tokens_sold']:,}")
        else:
            logger.info(f"\n❌ No working discriminator found")
            logger.info(f"💡 Next steps:")
            logger.info(f"   1. Try manual sell on pump.fun website")
            logger.info(f"   2. Analyze that transaction signature")
            logger.info(f"   3. Extract exact discriminator and accounts")
        
        logger.info("\n✅ Testing complete!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
