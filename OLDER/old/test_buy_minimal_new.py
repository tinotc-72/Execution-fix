"""
Test buying BONK using exact PUMP router instruction from mainnet.
"""

import asyncio
import logging
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Import core components
from fast_executor import FastExecutor
from minimal_tx_builder_final import (
    build_buy_tx,
    BONK_MINT,
    PUMP_ROUTER_STATE,
    PUMP_TOKEN_VAULT
)

# Import config and setup logging
from config import WALLET_PRIVATE_KEY, HELIUS_RPC_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_execution.log')
    ]
)
logger = logging.getLogger(__name__)
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.message import MessageV0
from solders.transaction import VersionedTransaction

# Import core components
from fast_executor import FastExecutor
from minimal_tx_builder import (
    build_buy_tx,
    build_sell_tx,
    PUMP_ROUTER,
    TOKEN_PROGRAM_ID,
    ATA_PROGRAM_ID,
    get_associated_token_address
)
from config import kz
from env_keys import kz as env_kz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
TEST_TOKEN_MINT = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"  # BONK token mint
TEST_AMOUNT_SOL = 0.1  # Amount for testing (maximum available)
MIN_SOL_BALANCE = 0.12  # Minimum SOL needed (including fees)
SLIPPAGE_BPS = 3000  # 30% slippage
CONFIRMATION_WAIT = 2  # Seconds to wait for confirmation
BONK_DECIMALS = 5  # BONK uses 5 decimal places

async def create_ata_instruction(
    owner: Pubkey,
    mint: Pubkey,
    ata: Pubkey
) -> Instruction:
    """Create an instruction to create an Associated Token Account"""
    
    accounts = [
        AccountMeta(pubkey=owner, is_signer=True, is_writable=True),  # Payer
        AccountMeta(pubkey=ata, is_signer=False, is_writable=True),  # ATA
        AccountMeta(pubkey=owner, is_signer=False, is_writable=False),  # Owner
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),  # Mint
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),  # System Program
        AccountMeta(pubkey=Pubkey.from_string(TOKEN_PROGRAM_ID), is_signer=False, is_writable=False),  # Token Program
        AccountMeta(pubkey=Pubkey.from_string(ATA_PROGRAM_ID), is_signer=False, is_writable=False),  # ATA Program
    ]
    
    return Instruction(
        program_id=Pubkey.from_string(ATA_PROGRAM_ID),
        accounts=accounts,
        data=bytes([])
    )

async def execute_test_trades():
    """Execute test buy and sell trades"""
    try:
        print("\n🧪 Starting Buy/Sell Test")
        print("========================")
        
        # Load wallet
        key = env_kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        decoded_key = base58.b58decode(key)
        keypair = Keypair.from_bytes(decoded_key)
        print(f"🔑 Wallet loaded: {keypair.pubkey()}")
        
        # Initialize FastExecutor
        executor = FastExecutor(keypair)
        await executor.initialize()
        print("✅ FastExecutor initialized")
        
        # Check initial SOL balance
        initial_balance = await executor.get_balance(keypair.pubkey())
        if initial_balance is None or initial_balance < MIN_SOL_BALANCE:
            print(f"❌ Insufficient balance: {initial_balance} SOL")
            print(f"Need at least {MIN_SOL_BALANCE} SOL for test")
            return
        print(f"💰 Initial SOL balance: {initial_balance} SOL")
        
        # Convert token mint string to Pubkey
        token_pubkey = Pubkey.from_string(TEST_TOKEN_MINT)
        print(f"🪙 Testing with token: {TEST_TOKEN_MINT} (BONK)")
        
        # Get token ATA and Router vaults
        token_ata = get_associated_token_address(keypair.pubkey(), token_pubkey)
        router_key = Pubkey.from_string(PUMP_ROUTER)
        router_wsol_vault = get_associated_token_address(router_key, Pubkey.from_string("So11111111111111111111111111111111111111112"))
        router_token_vault = get_associated_token_address(router_key, token_pubkey)
        print(f"📝 Token ATA: {token_ata}")
        print(f"🏦 Router WSOL Vault: {router_wsol_vault}")
        print(f"🏦 Router BONK Vault: {router_token_vault}")
        
        # Check if ATA exists and create if needed
        token_balance_before = await executor.get_token_balance(token_ata)
        if token_balance_before is None:
            print("\n🔧 Creating token account...")
            create_ata_ix = await create_ata_instruction(
                owner=keypair.pubkey(),
                mint=token_pubkey,
                ata=token_ata
            )
            
            # Get blockhash
            blockhash = await executor.get_latest_blockhash()
            if not blockhash:
                print("❌ Failed to get blockhash")
                return
                
            # Create ATA tx
            message = MessageV0.try_compile(
                payer=keypair.pubkey(),
                instructions=[create_ata_ix],
                recent_blockhash=blockhash,
                address_lookup_table_accounts=[]
            )
            
            tx = VersionedTransaction(message, [keypair])
            
            # Execute ATA creation
            ata_result = await executor.execute_transaction(tx)
            if not ata_result:
                print("❌ Failed to create token account")
                return
                
            print("✅ Token account created!")
            await asyncio.sleep(CONFIRMATION_WAIT)
        
        # Check router vault balances to ensure they exist
        router_wsol_balance = await executor.get_token_balance(router_wsol_vault)
        router_token_balance = await executor.get_token_balance(router_token_vault)
        
        print("\n🏦 Router Balances")
        print("================")
        print("WSOL: " + (f"{router_wsol_balance/1e9:.9f} SOL" if router_wsol_balance is not None else "Not found"))
        print("BONK: " + (f"{router_token_balance/(10**BONK_DECIMALS):.5f} BONK" if router_token_balance is not None else "Not found"))
        
        if router_wsol_balance is None or router_token_balance is None:
            print("❗ Router vaults not found - they will be created during the transaction")
        
        # Check initial token balance
        token_balance_before = await executor.get_token_balance(token_ata)
        formatted_balance_before = token_balance_before / (10 ** BONK_DECIMALS) if token_balance_before is not None else None
        print(f"💎 Initial token balance: {formatted_balance_before} BONK")
        
        # Execute buy
        print("\n🛒 Executing test buy...")
        amount_lamports = int(TEST_AMOUNT_SOL * 1_000_000_000)  # Convert SOL to lamports
        print(f"🔢 Amount: {TEST_AMOUNT_SOL} SOL ({amount_lamports} lamports)")
        print(f"↕️ Slippage: {SLIPPAGE_BPS/100}%")
        
        # Build and execute buy transaction
        buy_tx = await build_buy_tx(
            executor=executor,
            token=token_pubkey,
            amount=amount_lamports,
            keypair=keypair,
            slippage_bps=SLIPPAGE_BPS
        )
        
        if not buy_tx:
            print("❌ Failed to build buy transaction")
            return
            
        print("\n📝 Transaction Details:")
        print("====================")
        print(f"Instructions: {len(buy_tx.message.instructions)} total")
        for i, ix in enumerate(buy_tx.message.instructions):
            print(f"\nInstruction {i}:")
            print(f"Data (hex): {ix.data.hex()}")
            print(f"Program ID: {ix.program_id}")
            if hasattr(ix, 'accounts'):
                print("Accounts:")
                for j, meta in enumerate(ix.accounts):
                    print(f"  {j}: {meta}")
            
        buy_result = await executor.execute_transaction(buy_tx)
        if not buy_result:
            print("❌ Buy transaction failed")
            return
            
        print("✅ Buy transaction submitted!")
        print(f"🔖 Buy signature: {buy_result}")
        
        # Wait for confirmation and check balances
        print("\n⏳ Waiting for buy confirmation...")
        await asyncio.sleep(CONFIRMATION_WAIT)
        
        # Check balances after buy
        sol_after_buy = await executor.get_balance(keypair.pubkey())
        token_balance_after_buy = await executor.get_token_balance(token_ata)
        formatted_balance_after = token_balance_after_buy / (10 ** BONK_DECIMALS) if token_balance_after_buy is not None else None
        
        print("\n📊 Buy Results")
        print("============")
        print(f"SOL spent: {initial_balance - sol_after_buy} SOL")
        print(f"Token balance: {formatted_balance_after} BONK")
        print(f"Tokens received: {formatted_balance_after - (formatted_balance_before or 0)} BONK")
        
        if token_balance_after_buy <= 0:
            print("❌ No tokens received from buy")
            return
            
        # Execute sell
        print("\n💰 Executing test sell...")
        sell_tx = await build_sell_tx(
            executor=executor,
            token=token_pubkey,
            token_amount=token_balance_after_buy,  # Sell all tokens
            keypair=keypair,
            slippage_bps=SLIPPAGE_BPS
        )
        
        if not sell_tx:
            print("❌ Failed to build sell transaction")
            return
            
        sell_result = await executor.execute_transaction(sell_tx)
        if not sell_result:
            print("❌ Sell transaction failed")
            return
            
        print("✅ Sell transaction successful!")
        print(f"🔖 Sell signature: {sell_result}")
        
        # Wait for confirmation and check final balances
        print("\n⏳ Waiting for sell confirmation...")
        await asyncio.sleep(CONFIRMATION_WAIT)
        
        # Check final balances
        sol_final = await executor.get_balance(keypair.pubkey())
        token_balance_final = await executor.get_token_balance(token_ata)
        formatted_balance_final = token_balance_final / (10 ** BONK_DECIMALS) if token_balance_final is not None else None
        
        print("\n📊 Sell Results")
        print("============")
        print(f"SOL received: {sol_final - sol_after_buy} SOL")
        print(f"Net SOL change: {sol_final - initial_balance} SOL")
        print(f"Final token balance: {formatted_balance_final} BONK")
        
        print("\n✅ Test complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
    finally:
        await executor.cleanup()
        print("\n🧹 Cleaned up FastExecutor")

async def main():
    """Test buying using PUMP router with exact mainnet instruction"""
    print("\n🧪 Starting PUMP Buy Test")
    print("=" * 24)

    # Load wallet
    keypair = Keypair.from_bytes(WALLET_PRIVATE_KEY)
    logger.info(f"🔑 Wallet loaded: {keypair.pubkey()}")

    # Initialize executor
    async with FastExecutor(
        keypair=keypair,
        rpc_urls=[HELIUS_RPC_URL],
        health_check_timeout=10.0
    ) as executor:
        try:
            # Check SOL balance
            balance = await executor.get_balance(keypair.pubkey())
            logger.info(f"💰 SOL Balance: {balance / 1e9:.4f} SOL")

            if balance < 0.05 * 1e9:  # 0.05 SOL minimum
                raise ValueError("Insufficient SOL balance")

            # Amount to test with (0.01 SOL)
            amount = int(0.01 * 1e9)
            logger.info(f"🎯 Test amount: {amount / 1e9:.4f} SOL")

            # Build transaction with mainnet-exact accounts
            logger.info("🔧 Building transaction...")
            tx = await build_buy_tx(
                payer=keypair.pubkey(),
                amount=amount,
                slippage=0.30  # 30% slippage
            )

            if not tx:
                raise ValueError("Failed to build transaction")

            # Send and confirm
            logger.info("🚀 Sending transaction...")
            result = await executor.send_and_confirm_transaction(
                transaction=tx,
                signers=[keypair],
                confirm_timeout=60
            )

            if "error" in result:
                logger.error(f"❌ Transaction failed: {result['error']}")
                if "logs" in result:
                    logger.error("Transaction logs:")
                    for log in result["logs"]:
                        logger.error(f"  {log}")
            else:
                logger.info(f"✅ Transaction succeeded!")
                logger.info(f"📝 Signature: {result['signature']}")
                logger.info(f"🔍 Status: {result['confirmationStatus']}")
                if "logs" in result:
                    logger.info("Transaction logs:")
                    for log in result["logs"]:
                        logger.info(f"  {log}")

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        traceback.print_exc()
