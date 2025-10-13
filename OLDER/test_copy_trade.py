"""
Test script for executing a copy trade of a specific token,
with improved error handling and PDA verification.
"""

import asyncio
import logging
import traceback
import json
from datetime import datetime, timezone, UTC
from typing import Tuple, Optional, List, Dict, Any, Union

from solders.pubkey import Pubkey
from solders.keypair import Keypair 
import aiohttp
import json
import base64

# Local imports
from env_keys import EnvKeys
from config import WALLET, BOT_PUBKEY, kz
from utils import (
    get_token_account_balance,
    check_token_account_exists,
    wait_for_token_balance,
    get_formatted_datetime,
    get_current_user
)

# Import after basics to avoid circular imports
from fast_executor import FastExecutor
from tx_translator import clone_monitored_transaction
from listener import (
    fetch_transaction,
    identify_dex_and_instruction,
    extract_trade_data
)
# Import tx_builder last to avoid circular imports
from minimal_tx_builder import (
    build_buy_tx,
    build_sell_tx,
    PUMP_ROUTER,
    TOKEN_PROGRAM_ID,
    ATA_PROGRAM_ID,
    get_associated_token_address,
    verify_user_pda_needs_init
)

# Load environment keys
keys = EnvKeys()

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('test_copy_trade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants for buy strategy
TARGET_TOKEN_DECIMALS = 9  # Most SPL tokens use 9 decimals
MIN_SOL_BALANCE = 0.15     # Minimum SOL needed (including fees)
SLIPPAGE_BPS = 1000        # 10% slippage tolerance for pump.fun

# Buy amounts (try larger amounts to avoid minimum thresholds)
AMOUNT_IN_LAMPORTS = 20_000_000   # 0.02 SOL worth of tokens - substantial amount
MAX_SOL_COST = 50_000_000         # Max 0.05 SOL (including slippage)
SLIPPAGE_BPS = 1000               # 10% slippage for pump.fun tokens

# Target meme coin to purchase - using an active pump.fun token with liquidity
TARGET_TOKEN_MINT = "9Gnf5oG7QiK4uZWgMmc55Ui2uZnJcf8YVZTH52ctpump"  # From successful transaction example
SOURCE_WALLET = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"

# Collect all available RPC URLs
RPC_ENDPOINTS = [
    keys.HELIUS_RPC_URL,
    keys.PUBLIC_RPC_URL,
]
if keys.QUICKNODE_RPC_URL:
    RPC_ENDPOINTS.append(keys.QUICKNODE_RPC_URL)
    
async def fetch_last_traded_token(wallet_address: str) -> str:
    """Fetch the most recently traded token by the monitored wallet"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{kz.HELIUS_RPC_URL}"
            payload = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "getSignaturesForAddress",
                "params": [
                    wallet_address,
                    {
                        "limit": 100,
                        "commitment": "confirmed"
                    }
                ]
            }
            async with session.post(url, json=payload) as response:
                data = await response.json()
                for tx in data.get("result", []):
                    tx_data = await fetch_transaction(tx["signature"])
                    if not tx_data:
                        continue
                    dex_info = identify_dex_and_instruction(tx_data)
                    if not dex_info:
                        continue
                    trade_data = extract_trade_data(tx_data, dex_info)
                    if trade_data and trade_data.get("token_mint"):
                        logger.info(f"Found trade: {json.dumps(trade_data, indent=2)}")
                        return trade_data["token_mint"]
        return None
    except Exception as e:
        logger.error(f"Error fetching last traded token: {str(e)}")
        return None

async def verify_transaction_status(executor: FastExecutor, signature: str) -> Tuple[bool, str]:
    """Verify the status of a transaction and decode any errors.
    
    Args:
        executor: The executor instance
        signature: The transaction signature
        
    Returns:
        Tuple[bool, str]: Success status and error message if any
    """
    try:
        # Add small delay to ensure transaction is confirmed
        await asyncio.sleep(2)
        
        # Try to get transaction status
        confirmation = await executor.wait_for_confirmation(
            tx_sig=signature,
            max_retries=30,
            retry_delay=1.0
        )
        
        if not confirmation:
            return False, "Transaction not found"
            
        # Check for errors
        if not confirmation.get("success", False):
            error = confirmation.get("error", {})
            if not error:
                return False, "Transaction failed (no error details)"
                
            # Parse instruction errors
            if isinstance(error, list) and len(error) >= 2:
                ix_index = error[0]
                ix_error = error[1]
                
                if isinstance(ix_error, dict):
                    # Handle custom program errors
                    if "Custom" in str(ix_error):
                        code = ix_error.get("Custom", 0)
                        # Known custom error codes
                        if code == 101 or "0x65" in str(code):
                            return False, f"Custom error 101 in instruction {ix_index}: PDA already initialized or slippage exceeded"
                        return False, f"Custom program error {code} in instruction {ix_index}"
                        
                    return False, f"Instruction {ix_index} failed: {json.dumps(ix_error)}"
                    
                return False, f"Instruction {ix_index} failed: {str(ix_error)}"
            
            return False, f"Transaction failed: {str(error)}"
            
        # Get program logs
        logs = confirmation.get("logs", [])
        if logs:
            # Check logs for errors
            error_logs = [log for log in logs if any(err in log.lower() for err in ["error", "failed", "invalid"])]
            if error_logs:
                return False, f"Found errors in program logs: {'; '.join(error_logs)}"
                
        # Check confirmation status
        status = confirmation.get("confirmationStatus")
        if status in ["confirmed", "finalized"]:
            return True, f"Transaction {status}"
            
        return False, f"Unexpected status: {status}"
        
    except Exception as e:
        logger.error(f"Error verifying transaction: {str(e)}")
        logger.error(traceback.format_exc())
        return False, f"Error verifying transaction: {str(e)}"
        
async def verify_user_pda(executor: FastExecutor, wallet: Pubkey) -> bool:
    """Verify that the user's PDA is properly initialized.
    
    Args:
        executor: The executor instance
        wallet: The user's wallet
        
    Returns:
        bool: True if PDA exists and is properly initialized
    """
    from minimal_tx_builder import get_user_pda_with_bump, PUMP_ROUTER
    
    try:
        # Get the PDA
        user_pda, _bump = get_user_pda_with_bump(wallet)
        logger.info(f"\n🔍 Checking User PDA: {user_pda}")
        
        # Get account info
        account = await executor.get_account_info(user_pda)
        if not account:
            logger.info("PDA account does not exist")
            return False
            
        # Verify owner is PUMP_ROUTER
        owner = account.get("owner")
        if str(owner) != str(PUMP_ROUTER):
            logger.info(f"Wrong owner: {owner} (expected {PUMP_ROUTER})")
            return False
            
        # Verify data exists
        data = account.get("data", [])
        if not data or not isinstance(data, list) or not data[0]:
            logger.info("No account data found")
            return False
            
        # Check discriminator
        raw_data = base64.b64decode(data[0])
        discriminator = raw_data[:8]
        expected = bytes.fromhex("b5f9b1e8179d8e84")  # initialize_user
        
        if discriminator != expected:
            logger.info(f"Wrong discriminator: {discriminator.hex()}")
            return False
            
        logger.info("✅ PDA properly initialized")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying PDA: {str(e)}")
        return False

async def execute_test_copy_trade():
    """Execute a test buy and sell sequence on a specific token.
    Handles PUMP.fun router errors and validates all steps."""
    try:
        # Initial setup and logging
        current_time = get_formatted_datetime()
        current_user = get_current_user()
        
        logger.info(f"\n🕒 Starting test at: {current_time}")
        logger.info(f"👤 User: {current_user}")
        logger.info("\n🧪 Starting Test Copy Trade Sequence")
        logger.info("===================================")

        # Initialize and validate wallet
        wallet = WALLET
        logger.info("\n=== Wallet Validation ===")
        logger.info(f"Type: {type(wallet)}")
        logger.info(f"Module: {wallet.__class__.__module__}")
        
        # Strict wallet validation
        if not isinstance(wallet, Keypair):
            raise ValueError(f"Invalid wallet type: {type(wallet)}. Must be solders.keypair.Keypair")
            
        # Verify signing capability
        test_message = bytes([1, 2, 3, 4])
        try:
            test_sig = wallet.sign_message(test_message)
            if not test_sig:
                raise ValueError("Wallet signing test failed")
            logger.info("✅ Wallet signing verified")
        except Exception as e:
            raise ValueError(f"Wallet signing test failed: {e}")

        # Setup transaction parameters
        token_mint = Pubkey.from_string(TARGET_TOKEN_MINT)
        amount_in = AMOUNT_IN_LAMPORTS
        max_cost = MAX_SOL_COST
        slippage_bps = SLIPPAGE_BPS
        
        logger.info(f"\n🎯 Target Parameters:")
        logger.info(f"Token: {token_mint}")
        logger.info(f"Amount: {amount_in/1e9:.6f} SOL")
        logger.info(f"Max cost: {max_cost/1e9:.6f} SOL")
        logger.info(f"Slippage: {slippage_bps/100:.1f}%")

        # Initialize FastExecutor with error handling
        async with FastExecutor(wallet, rpc_urls=RPC_ENDPOINTS) as executor:
            # Get and verify wallet balance
            balance = await executor.get_balance(wallet.pubkey())
            logger.info("\n💰 Wallet State:")
            logger.info(f"Balance: {balance/1e9:.6f} SOL")
            
            if balance < MIN_SOL_BALANCE * 1e9:
                raise ValueError(f"Insufficient balance: {balance/1e9:.6f} SOL (need {MIN_SOL_BALANCE} SOL)")
                
            # Check PDA state BEFORE transaction build
            logger.info("\n🔍 Verifying PDA state")
            is_pda_ready = await verify_user_pda(executor, wallet.pubkey())
            logger.info(f"PDA initialized: {is_pda_ready}")

            # Build the buy transaction using simple buy instead of initialize_and_buy
            logger.info("\n🏗️ Building buy transaction")
            
            # Get token ATA
            token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
            
            # Check if token account exists
            logger.info("\n🔍 Checking if token account needs to be created")
            account_exists = await check_token_account_exists(token_ata)
            logger.info(f"Token account exists: {account_exists}")
            
            # Create buy instruction using the simpler approach
            from minimal_tx_builder import create_buy_instruction
            
            buy_ix = await create_buy_instruction(
                token_mint=token_mint,
                owner=wallet.pubkey(),
                amount=amount_in,
                slippage_bps=slippage_bps,
                token_ata=token_ata
            )
            
            instructions = []
            
            # Add compute budget
            from minimal_tx_builder import create_compute_budget_ix
            compute_ix = create_compute_budget_ix(compute_units=200_000)
            instructions.append(compute_ix)
            
            # Add user PDA initialization if needed (might be required for pump.fun)
            # Temporarily disable PDA init to test if buy works without it
            # if not is_pda_ready:
            #     logger.info("Initializing user PDA...")
            #     from minimal_tx_builder import create_user_init_instruction
            #     try:
            #         init_ix = create_user_init_instruction(wallet.pubkey())
            #         instructions.append(init_ix)
            #         logger.info("✅ User PDA initialization instruction added")
            #     except Exception as e:
            #         logger.warning(f"⚠️ Could not create PDA init instruction: {e}")
            
            # Add token account creation if needed
            if not account_exists:
                logger.info("Creating token account...")
                from minimal_tx_builder import create_associated_token_account
                ata_ix = create_associated_token_account(
                    payer=wallet.pubkey(),
                    owner=wallet.pubkey(),
                    mint=token_mint
                )
                instructions.append(ata_ix)
            
            # Add the buy instruction
            instructions.append(buy_ix)
            
            # Build transaction
            from solders.transaction import VersionedTransaction
            from solders.message import Message
            from solders.hash import Hash as SolanaHash
            
            # Get recent blockhash
            recent_blockhash = await executor.get_latest_blockhash()
            if not recent_blockhash:
                raise ValueError("Failed to get recent blockhash")
                
            # Build message
            message = Message.new_with_blockhash(instructions, wallet.pubkey(), recent_blockhash)
            
            # Create and sign transaction
            tx = VersionedTransaction(message, [wallet])
            
            if not tx or not instructions:
                raise ValueError("Failed to build transaction")

            # Detailed instruction debugging
            logger.info("\n🔍 Transaction Instruction Details:")
            for i, ix in enumerate(instructions):
                logger.info(f"\nInstruction {i}:")
                logger.info(f"  Program: {ix.program_id}")
                logger.info(f"  Data (hex): {ix.data.hex() if ix.data else 'None'}")
                logger.info(f"  Accounts ({len(ix.accounts)}): {[str(a.pubkey) for a in ix.accounts]}")
                
            # Original transaction logging
            logger.info("\n📝 Transaction Details:")
            logger.info(f"Instruction count: {len(instructions)}")
            for i, ix in enumerate(instructions):
                logger.info(f"\nInstruction {i}:")
                logger.info(f"  Program: {ix.program_id}")
                logger.info(f"  Accounts: {len(ix.accounts)}")
                
            # Get token ATA for verification
            token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
            
            # Execute the transaction
            logger.info("\n🚀 Sending transaction")
            sig = await executor.send_transaction(tx, [wallet], original_instructions=instructions)
            if not sig:
                raise ValueError("Transaction submission failed")
                
            logger.info(f"Transaction sent: {sig}")
            logger.info(f"Explorer URL: https://solscan.io/tx/{sig}")
            
            # Log detailed transaction result with improved logging
            await log_transaction_result(executor, sig)
            
            # Wait for confirmation and check logs
            confirmation = await executor.wait_for_confirmation(sig)
            
            # Log any errors
            if confirmation.get("error"):
                logger.error("\n❌ Transaction had errors:")
                logger.error(json.dumps(confirmation["error"], indent=2))
                raise ValueError(f"Transaction failed: {confirmation['error']}")
            
            # Check if transaction was successful
            if not confirmation.get("success", True):
                logger.error("❌ Transaction not marked as successful")
                if confirmation.get("logs"):
                    logger.error("Program logs:")
                    for log in confirmation["logs"]:
                        logger.error(f"  {log}")
                raise ValueError("Transaction not successful")
            
            # Verify transaction status
            success, status = await verify_transaction_status(executor, sig)
            if not success:
                # Log the failed transaction details
                logger.error("\n❌ Transaction Failed:")
                logger.error(f"Status: {status}")
                logger.error(f"Explorer URL: https://solscan.io/tx/{sig}")
                raise ValueError(f"Transaction failed: {status}")
            
            # Verify trade success by checking token balance using direct method
            logger.info("\n⏳ Checking token balance directly...")
            token_balance = await get_token_account_balance_direct(executor, token_ata)
            
            if token_balance == 0:
                # Wait a bit more and try again
                logger.info("No tokens found, waiting 3 seconds and checking again...")
                await asyncio.sleep(3)
                token_balance = await get_token_account_balance_direct(executor, token_ata)
            
            if token_balance == 0:
                logger.error("❌ Trade failed - no tokens received")
                raise ValueError("Trade failed - no tokens received")
                
            logger.info(f"\n✅ Buy trade succeeded! Received {token_balance} tokens")
            
            # Hold for 5 seconds
            logger.info("\n⏳ Holding tokens for 5 seconds...")
            await asyncio.sleep(5)
            
            # Now sell all tokens
            logger.info("\n💰 Starting sell sequence...")
            sell_sig = await execute_sell_trade(executor, wallet, token_mint, token_balance)
            
            if not sell_sig:
                logger.error("❌ Sell trade failed")
                raise ValueError("Sell trade failed")
            
            logger.info("\n✅ Sell trade succeeded!")
            
            # Verify final state
            logger.info("\n� Final State:")
            
            # Check PDA state
            is_pda_ready = await verify_user_pda(executor, wallet.pubkey())
            logger.info(f"PDA initialized: {'yes' if is_pda_ready else 'no'}")
            
            # Check final balances
            final_balance = await executor.get_balance(wallet.pubkey())
            balance_change = (final_balance - balance) / 1e9
            final_token_balance = await get_token_account_balance_direct(executor, token_ata)
            
            logger.info("\n💰 Final Balance Changes:")
            logger.info(f"SOL change: {balance_change:.6f} SOL")
            logger.info(f"Final token balance: {final_token_balance}")
            logger.info(f"Buy transaction: {sig}")
            logger.info(f"Sell transaction: {sell_sig}")
            
            return {"buy_sig": sig, "sell_sig": sell_sig}
            
    except Exception as e:
        logger.error(f"\n❌ Error in test_copy_trade: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def log_transaction_result(executor: FastExecutor, signature: str):
    """Log detailed transaction result information.
    
    Args:
        executor: The executor instance
        signature: The transaction signature
    """
    try:
        # Add small delay to ensure transaction is fully confirmed
        await asyncio.sleep(2)
        
        confirmation = await executor.wait_for_confirmation(signature)
        
        logger.info("\n📊 Transaction Result:")
        logger.info(f"Signature: {signature}")
        logger.info(f"Status: {confirmation.get('confirmationStatus', 'unknown')}")
        logger.info(f"Explorer URL: https://solscan.io/tx/{signature}")
        
        if confirmation.get("error"):
            logger.error("\n❌ Transaction Error:")
            error = confirmation["error"]
            if isinstance(error, dict):
                logger.error(json.dumps(error, indent=2))
            else:
                logger.error(str(error))
                
            # Check instruction errors
            if "InstructionError" in str(error):
                instruction_idx = None
                error_details = None
                
                # Parse error details
                if isinstance(error, list) and len(error) >= 2:
                    instruction_idx = error[0]
                    error_details = error[1]
                    
                if instruction_idx is not None:
                    logger.error(f"\nInstruction {instruction_idx} failed:")
                    if isinstance(error_details, dict):
                        logger.error(json.dumps(error_details, indent=2))
                    else:
                        logger.error(str(error_details))
            return
            
        if confirmation.get("logs"):
            logger.info("\n📝 Program Logs:")
            for log in confirmation["logs"]:
                # Format program logs nicely
                if "Program log:" in log:
                    log = log.replace("Program log:", "  →")
                elif "Program data:" in log:
                    log = log.replace("Program data:", "  📊")
                logger.info(log)
                
                # Check for specific error indicators
                if any(err in log.lower() for err in ["error", "failed", "invalid", "insufficient"]):
                    logger.error(f"\n❗ Found error in program log: {log}")
                    
                # Look for transfer events
                if "Transfer" in log:
                    logger.info(f"\n💸 Found transfer event: {log}")
                    
                # Look for token mint events
                if "Mint" in log or "mint" in log:
                    logger.info(f"\n🪙 Found mint event: {log}")
                    
                # Look for swap events
                if "swap" in log.lower() or "Swap" in log:
                    logger.info(f"\n🔄 Found swap event: {log}")
                    
            # Additional analysis of transaction effects
            if "meta" in confirmation and "postTokenBalances" in confirmation["meta"]:
                logger.info("\n💰 Post-transaction token balances:")
                for balance in confirmation["meta"]["postTokenBalances"]:
                    logger.info(f"  Account: {balance.get('owner', 'unknown')}")
                    logger.info(f"  Mint: {balance.get('mint', 'unknown')}")
                    logger.info(f"  Amount: {balance.get('uiTokenAmount', {}).get('amount', '0')}")
                    
            if "meta" in confirmation and "preTokenBalances" in confirmation["meta"]:
                logger.info("\n💰 Pre-transaction token balances:")
                for balance in confirmation["meta"]["preTokenBalances"]:
                    logger.info(f"  Account: {balance.get('owner', 'unknown')}")
                    logger.info(f"  Mint: {balance.get('mint', 'unknown')}")
                    logger.info(f"  Amount: {balance.get('uiTokenAmount', {}).get('amount', '0')}")
                
    except Exception as e:
        logger.error(f"\n❌ Error getting transaction result: {str(e)}")
        logger.error(traceback.format_exc())
        
async def verify_trade_success(executor: FastExecutor, signature: str, token_ata: Pubkey) -> bool:
    """Verify that a trade was successful by checking token balance.
    
    Args:
        executor: The executor instance
        signature: The transaction signature
        token_ata: The token account to check
        
    Returns:
        bool: True if trade succeeded, False otherwise
    """
    try:
        # Wait for confirmation and check logs
        confirmation = await executor.wait_for_confirmation(signature)
        if not confirmation.get("success"):
            logger.error("\n❌ Transaction failed:")
            if confirmation.get("error"):
                logger.error(json.dumps(confirmation["error"], indent=2))
            if confirmation.get("logs"):
                logger.error("\nProgram logs:")
                for log in confirmation["logs"]:
                    logger.error(f"  {log}")
            return False
            
        # Check logs for program errors
        if confirmation.get("logs"):
            logs = confirmation["logs"]
            logger.info("\n📝 Program logs:")
            for log in logs:
                logger.info(f"  {log}")
                if "Error:" in log:
                    logger.error(f"Found error in logs: {log}")
                    return False
            
        # Wait for transaction to finalize
        logger.info("\n⏳ Waiting for finalization...")
        finalized = False
        retries = 10  # Increased retries for finalization
        while retries > 0 and not finalized:
            confirmation = await executor.wait_for_confirmation(signature)
            if confirmation.get("confirmationStatus") == "finalized":
                finalized = True
                logger.info("✅ Transaction finalized")
                break
            logger.info(f"Waiting for finalization... (retries left: {retries})")
            await asyncio.sleep(2)  # Longer wait between checks
            retries -= 1
            
        if not finalized:
            logger.error("❌ Transaction never reached finalized state")
            return False

        # Wait for token balance to update
        logger.info("\n⏳ Checking token balance...")
        token_balance = 0
        retries = 10  # Increased retries for balance check
        while retries > 0:
            try:
                token_balance = await get_token_account_balance(token_ata)
                if token_balance > 0:
                    logger.info(f"✅ Token balance: {token_balance}")
                    return True
            except ValueError as e:
                logger.warning(f"Retrying balance check: {e}")
            
            logger.info(f"Waiting... (retries left: {retries})")
            await asyncio.sleep(2)  # Longer wait between checks
            retries -= 1
            
        if token_balance == 0:
            logger.error("❌ Token balance is still 0 after waiting")
            return False
            
        return token_balance > 0
        
    except Exception as e:
        logger.error(f"Error verifying trade: {str(e)}")
        logger.error(traceback.format_exc())
        return False

async def get_token_account_balance_direct(executor: FastExecutor, token_account: Pubkey) -> int:
    """Get token balance directly using the executor with better error handling.
    
    Args:
        executor: FastExecutor instance
        token_account: The token account to check
        
    Returns:
        int: The token balance amount (0 if account doesn't exist)
    """
    try:
        logger.info(f"🔍 Checking token account: {token_account}")
        
        # First check if the account exists
        account_info = await executor.get_account_info(token_account)
        if not account_info:
            logger.info(f"❌ Token account {token_account} does not exist")
            return 0
            
        logger.info(f"✅ Token account exists, checking data...")
        logger.info(f"Account info keys: {list(account_info.keys()) if account_info else 'None'}")
        
        # Parse the account data for token balance
        if account_info.get("data") and len(account_info["data"]) > 0:
            logger.info(f"Data found, length: {len(account_info['data'])}")
            
            # For jsonParsed encoding
            if isinstance(account_info["data"], dict) and "parsed" in account_info["data"]:
                parsed = account_info["data"]["parsed"]
                if "info" in parsed and "tokenAmount" in parsed["info"]:
                    amount = int(parsed["info"]["tokenAmount"]["amount"])
                    logger.info(f"✅ Token balance from parsed data: {amount}")
                    return amount
            
            # For base64 encoding
            elif isinstance(account_info["data"], list) and len(account_info["data"]) > 0:
                import base64
                raw_data = base64.b64decode(account_info["data"][0])
                logger.info(f"Raw data length: {len(raw_data)}")
                
                if len(raw_data) >= 8:
                    # Parse the amount (first 8 bytes, little endian)
                    amount = int.from_bytes(raw_data[:8], byteorder='little')
                    logger.info(f"✅ Token balance from raw data: {amount}")
                    return amount
                else:
                    logger.info(f"Raw data too short: {len(raw_data)} bytes")
        else:
            logger.info("No data field found in account")
        
        logger.info("No balance data found in account")
        return 0
        
    except Exception as e:
        logger.error(f"Error checking token balance: {str(e)}")
        logger.error(traceback.format_exc())
        return 0

async def execute_sell_trade(executor: FastExecutor, wallet: Keypair, token_mint: Pubkey, token_balance: int) -> Optional[str]:
    """Execute a sell trade for all tokens.
    
    Args:
        executor: FastExecutor instance
        wallet: The wallet keypair
        token_mint: The token to sell
        token_balance: Current token balance to sell
        
    Returns:
        str: Transaction signature if successful, None if failed
    """
    try:
        logger.info(f"\n💰 Selling {token_balance} tokens of {token_mint}")
        
        # Build sell transaction
        # Note: For sell, amount_in is the token amount we want to sell
        # min_out is the minimum SOL we want to receive
        min_sol_out = 5_000_000  # Minimum 0.005 SOL (adjust based on your needs)
        
        sell_tx, sell_instructions = await build_sell_tx(
            token_mint=token_mint,
            amount_in=token_balance,  # Sell all tokens
            min_out=min_sol_out,
            owner=wallet.pubkey(),
            signer=wallet,
            executor=executor,
            slippage_bps=500  # 5% slippage for sell (higher than buy)
        )
        
        if not sell_tx or not sell_instructions:
            raise ValueError("Failed to build sell transaction")
            
        logger.info("\n🚀 Sending sell transaction")
        sell_sig = await executor.send_transaction(sell_tx, [wallet], original_instructions=sell_instructions)
        if not sell_sig:
            raise ValueError("Sell transaction submission failed")
            
        logger.info(f"Sell transaction sent: {sell_sig}")
        logger.info(f"Explorer URL: https://solscan.io/tx/{sell_sig}")
        
        # Wait for confirmation
        success, status = await verify_transaction_status(executor, sell_sig)
        if not success:
            logger.error(f"❌ Sell transaction failed: {status}")
            return None
            
        logger.info("✅ Sell transaction confirmed!")
        return sell_sig
        
    except Exception as e:
        logger.error(f"❌ Error executing sell trade: {str(e)}")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    try:
        print(f"\n🕒 Test started at: {get_formatted_datetime()}")
        print(f"👤 Running as user: {get_current_user()}")
        asyncio.run(execute_test_copy_trade())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        traceback.print_exc()
