#!/usr/bin/env python3
"""
Script to analyze Solana transactions using a provided transaction signature.
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transaction_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def analyze_transaction(signature: str):
    """Analyze a Solana transaction using its signature."""
    client = AsyncClient(EnvKeys().HELIUS_RPC_URL)

    try:
        logger.info(f"🔍 Analyzing transaction: {signature}")

        # Fetch transaction details using solders Signature
        from solders.signature import Signature
        try:
            sig = Signature.from_string(signature)
            transaction_details = await client.get_transaction(sig)
        except ValueError as e:
            logger.error(f"❌ Invalid signature format: {e}")
            return None

        if not transaction_details.value:
            logger.error(f"❌ Transaction not found: {signature}")
            return None

        logger.info("✅ Transaction details fetched successfully")

        # Extract relevant information
        if not transaction_details.value:
            logger.error(f"❌ Transaction not found: {signature}")
            return None

        transaction_info = transaction_details.value
        meta = transaction_info.meta if transaction_info.meta else {}
        
        # Get balances and convert lamports to SOL
        pre_balances = [bal / 1_000_000_000 for bal in meta.pre_balances] if meta.pre_balances else []
        post_balances = [bal / 1_000_000_000 for bal in meta.post_balances] if meta.post_balances else []
        
        # Get token balances
        pre_token_balances = meta.pre_token_balances if meta.pre_token_balances else []
        post_token_balances = meta.post_token_balances if meta.post_token_balances else []
        
        # Get instructions
        instructions = []
        if transaction_info.transaction and transaction_info.transaction.message:
            for ix in transaction_info.transaction.message.instructions:
                instructions.append({
                    'program_id': str(ix.program_id),
                    'accounts': [str(acc) for acc in ix.accounts],
                    'data': ix.data.hex() if ix.data else None
                })

        logger.info(f"Pre-balances: {pre_balances}")
        logger.info(f"Post-balances: {post_balances}")
        logger.info(f"Token balances: {token_balances}")

        # Calculate SOL transfers
        sol_transfers = []
        if len(pre_balances) == len(post_balances):
            for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
                if pre != post:
                    sol_transfers.append({
                        'index': i,
                        'pre_balance': pre,
                        'post_balance': post,
                        'change': post - pre
                    })

        # Calculate token transfers
        token_transfers = []
        for post_token in post_token_balances:
            pre_token = next(
                (t for t in pre_token_balances if t.mint == post_token.mint 
                 and t.owner == post_token.owner), None)
            
            if pre_token:
                pre_amount = float(pre_token.ui_token_amount.amount)
                post_amount = float(post_token.ui_token_amount.amount)
                if pre_amount != post_amount:
                    token_transfers.append({
                        'mint': str(post_token.mint),
                        'owner': str(post_token.owner),
                        'pre_amount': pre_amount,
                        'post_amount': post_amount,
                        'change': post_amount - pre_amount,
                        'decimals': post_token.ui_token_amount.decimals
                    })

        # Print analysis
        print("\n" + "="*80)
        print(f"Transaction Analysis: {signature}")
        print("="*80)
        print(f"\n💰 SOL Transfers:")
        for transfer in sol_transfers:
            print(f"  Account {transfer['index']}: {transfer['change']:+.6f} SOL")
        
        print(f"\n🔄 Token Transfers:")
        for transfer in token_transfers:
            print(f"  Token {transfer['mint'][:8]}...")
            print(f"  Change: {transfer['change']:+.6f}")
        
        print(f"\n📝 Instructions:")
        for i, ix in enumerate(instructions):
            print(f"\n  {i+1}. Program: {ix['program_id']}")
            print(f"     Accounts: {len(ix['accounts'])}")
        
        # Return structured analysis
        return {
            'signature': signature,
            'timestamp': transaction_info.block_time,
            'status': 'Success' if not meta.err else f'Failed: {meta.err}',
            'fee': meta.fee / 1_000_000_000 if meta.fee else 0,
            'sol_transfers': sol_transfers,
            'token_transfers': token_transfers,
            'instructions': instructions,
            'raw': {
                'pre_balances': pre_balances,
                'post_balances': post_balances,
                'pre_token_balances': pre_token_balances,
                'post_token_balances': post_token_balances
            }
        }

    except Exception as e:
        logger.error(f"❌ Error analyzing transaction: {e}")
        return None

    finally:
        await client.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python analyze_transaction.py <transaction_signature>")
        sys.exit(1)

    signature = sys.argv[1]

    asyncio.run(analyze_transaction(signature))
