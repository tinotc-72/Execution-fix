"""
Test script for pumpfun_CC_copy_executor.py
- Loads wallet and RPC from .env using env_keys.py
- Instantiates PumpFunCCCopyExecutor
- Buys and sells 0.001 SOL of a Pump.fun meme coin
- Prints transaction signature and Solscan link for confirmation
"""


import os
import asyncio
from solders.keypair import Keypair
from pumpfun_CC_copy_executor import try_pumpfun_buy, try_pumpfun_sell_all

# Minimal wallet loader (base58 string from env)
def load_wallet_from_private_key(private_key: str = None):
    import base58
    if private_key is None:
        private_key = os.getenv("PHANTOM_PRIVATE_KEY")
        if not private_key:
            raise ValueError("PHANTOM_PRIVATE_KEY not found in environment variables")
    private_key = private_key.strip().replace('"', '').replace("'", '')
    private_key_bytes = base58.b58decode(private_key)
    return Keypair.from_bytes(private_key_bytes)

async def main():
    # Load wallet and RPC from environment
    keypair = load_wallet_from_private_key()
    rpc_url = os.getenv("HELIUS_RPC_URL")
    TOKEN_MINT = os.getenv("PUMPFUN_TEST_TOKEN", "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmn")
    AMOUNT_SOL = 0.001

    print(f"Loaded wallet: {keypair.pubkey()}")
    print(f"Using RPC: {rpc_url}")
    print(f"Testing buy of {AMOUNT_SOL} SOL for token: {TOKEN_MINT}")


    # Use real addresses from a live Pump.fun meme coin transaction (from Solscan)
    # Transaction: 4xeMWYebXdThgAmZqSTPcbgHFodz4cujsp323pfJ5dsjuegD2oPYxT7Zp37qqtSACLK9nzC4ByisYr5vi5gq9iYQ
    # Mapping:
    #  0: User wallet (signer): your wallet
    #  1: Protocol Fee Account: 7hTckgnGnLQR6sdH7YkqFTAA7VwTfYFaZ6EhEsU3saCX
    #  2: Meme coin mint: 3QRh4yQY5NHH7TK2dxzbFbUANSQRyn8P11ZDSqUSpump
    #  3: Bonding Curve: JBACT6XejRKHt6TVuZLtsen53s39kSYMGbJUVFTN3qHz
    #  4: Vault: AeYQKmNEVAwT4PDjTidycYmLmWtApu67hEUiTork9783
    #  5: Event Authority/Global: HapyT99AvwPNMcJQWH33hiyBPKhsi5dfETQuJ1EbejTT
    #  6: Your ATA for the meme coin mint (replace with your ATA if needed)
    #  7: System Program: 11111111111111111111111111111111
    #  8: SPL Token Program: TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
    #  9: Possibly global volume accumulator: GoNKTRUxW71LWMpvXLzKGjGGF7k9DQa9SndHmDchCrLS
    # 10: Possibly event authority/global: Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1
    # 11: Pump.fun Program: 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P
    # 12-15: Other accounts (not always needed for buy/sell)

    # Dynamically compute your ATA for the meme coin mint
    from spl.token.instructions import get_associated_token_address
    from solders.pubkey import Pubkey
    user_ata = str(get_associated_token_address(keypair.pubkey(), Pubkey.from_string("3QRh4yQY5NHH7TK2dxzbFbUANSQRyn8P11ZDSqUSpump")))
    real_accounts = [
        str(keypair.pubkey()),  # 0: user (your wallet)
        "7hTckgnGnLQR6sdH7YkqFTAA7VwTfYFaZ6EhEsU3saCX",  # 1: protocol fee
        "3QRh4yQY5NHH7TK2dxzbFbUANSQRyn8P11ZDSqUSpump",  # 2: meme coin mint
        "JBACT6XejRKHt6TVuZLtsen53s39kSYMGbJUVFTN3qHz",  # 3: bonding curve
        "AeYQKmNEVAwT4PDjTidycYmLmWtApu67hEUiTork9783",  # 4: vault
        "HapyT99AvwPNMcJQWH33hiyBPKhsi5dfETQuJ1EbejTT",  # 5: event authority/global
        user_ata,  # 6: your ATA for the meme coin mint
        "11111111111111111111111111111111",  # 7: system program
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # 8: SPL token program
        "GoNKTRUxW71LWMpvXLzKGjGGF7k9DQa9SndHmDchCrLS",  # 9: possibly global volume accumulator
        "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1",  # 10: possibly event authority/global
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # 11: Pump.fun program
        # Add more if needed
    ]
    real_instruction = {
        "program_id": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Pump.fun program
        "accounts": real_accounts,
        "data": {"amount": AMOUNT_SOL}
    }
    real_transaction = {
        "instructions": [real_instruction],
        "signature": "DUMMY_SIGNATURE_123",
        "signer": str(keypair.pubkey())
    }

    try:
        buy_result = await try_pumpfun_buy(keypair, "3QRh4yQY5NHH7TK2dxzbFbUANSQRyn8P11ZDSqUSpump", AMOUNT_SOL, rpc_url=rpc_url, transaction_data=real_transaction)
        print(f"Buy result: {buy_result}")
        if buy_result.get('signature'):
            print(f"🔗 View on Solscan: https://solscan.io/tx/{buy_result['signature']}")
    except Exception as e:
        print(f"Buy failed: {e}")
    await asyncio.sleep(2)
    print(f"Testing sell all for token: 3QRh4yQY5NHH7TK2dxzbFbUANSQRyn8P11ZDSqUSpump")
    try:
        sell_result = await try_pumpfun_sell_all(keypair, "3QRh4yQY5NHH7TK2dxzbFbUANSQRyn8P11ZDSqUSpump", rpc_url=rpc_url, transaction_data=real_transaction)
        print(f"Sell result: {sell_result}")
        if sell_result.get('signature'):
            print(f"🔗 View on Solscan: https://solscan.io/tx/{sell_result['signature']}")
    except Exception as e:
        print(f"Sell failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
