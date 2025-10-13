from typing import Dict, Optional, Tuple
import asyncio
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solders.system_program import ID as SYS_PROGRAM_ID
from solana.rpc.commitment import Confirmed

async def validate_token_account(
    rpc_client: AsyncClient,
    token_account: Pubkey,
    mint: Pubkey
) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validates a token account's existence and balance
    Returns: (is_valid, error_message, balance)
    """
    try:
        # Check if account exists
        account_info = await rpc_client.get_account_info(token_account, commitment=Confirmed)
        if not account_info.value:
            return False, "Token account does not exist", None

        # Get token balance
        balance_response = await rpc_client.get_token_account_balance(token_account)
        if balance_response.value is None:
            return False, "Could not fetch token balance", None

        balance = int(balance_response.value.amount)
        return True, None, balance

    except Exception as e:
        return False, f"Error validating token account: {str(e)}", None

async def validate_trade_prerequisites(
    rpc_client: AsyncClient,
    wallet_pubkey: Pubkey,
    token_account: Pubkey,
    mint: Pubkey,
    required_sol_balance: float = 0.05  # 0.05 SOL minimum
) -> Tuple[bool, str]:
    """
    Comprehensive validation before attempting a trade
    Returns: (is_valid, error_message)
    """
    try:
        # 1. Check SOL balance
        sol_balance_response = await rpc_client.get_balance(wallet_pubkey)
        sol_balance = sol_balance_response.value / 1e9  # Convert lamports to SOL
        
        if sol_balance < required_sol_balance:
            return False, f"Insufficient SOL balance: {sol_balance:.4f} SOL (need {required_sol_balance} SOL)"

        # 2. Validate token account
        is_valid, error_msg, token_balance = await validate_token_account(
            rpc_client, token_account, mint
        )
        
        if not is_valid:
            return False, error_msg or "Token account validation failed"

        # 3. Check recent blockhash
        try:
            blockhash_resp = await rpc_client.get_latest_blockhash()
            if not blockhash_resp:
                return False, "Failed to get recent blockhash"
        except Exception as e:
            return False, f"Blockhash error: {str(e)}"

        return True, "All prerequisites met"

    except Exception as e:
        return False, f"Validation error: {str(e)}"

async def log_account_state(
    rpc_client: AsyncClient,
    wallet: Pubkey,
    token_account: Optional[Pubkey] = None,
    mint: Optional[Pubkey] = None
) -> None:
    """
    Logs detailed account state information for debugging
    """
    try:
        print("\n🔍 Account State Check:")
        
        # SOL balance
        sol_balance = await rpc_client.get_balance(wallet)
        print(f"💰 SOL Balance: {sol_balance.value / 1e9:.4f} SOL")

        if token_account and mint:
            # Token account state
            is_valid, error_msg, balance = await validate_token_account(
                rpc_client, token_account, mint
            )
            
            if is_valid:
                print(f"✅ Token Account: Valid")
                print(f"💎 Token Balance: {balance}")
            else:
                print(f"❌ Token Account: {error_msg}")

        # Recent blockhash
        blockhash_resp = await rpc_client.get_latest_blockhash()
        if blockhash_resp:
            print(f"🎯 Recent Blockhash: Available")
        else:
            print(f"❌ Recent Blockhash: Not available")

    except Exception as e:
        print(f"❌ Error logging account state: {str(e)}")
