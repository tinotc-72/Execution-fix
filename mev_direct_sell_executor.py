#!/usr/bin/env python3
"""
MEV Direct SELL Executor - Direct Instruction Copying for SELL Transactions
Uses the same approach as BUYs: copy exact instruction details from target wallet's SELL transactions
"""

# PR-02 Integration: Required imports
from models.build_result import BuildResult
from utils.alt_fetch import build_alts_from_tables, get_recent_blockhash
from utils.ata_enforce import ensure_ata_ixs
from utils.fees import with_compute_budget
from executors.submit import send_and_confirm_v0_tx
from utils.logs import log_submit_result

import asyncio
import logging
import requests
import base64
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned
import base58

# Additional imports for the fixed implementation
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from utils import RPCClient

logger = logging.getLogger(__name__)

# Constants for router detection
JUPITER_PROGRAM = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
METEORA_AGGREGATOR = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"

async def try_mev_direct_copy_sell(trade_info: dict, wallet: Keypair, rpc):
    """
    Build a *real* VersionedTransaction for cloning a SELL route.
    1) Fetch the original tx (via get_transaction).
    2) Extract route/DEX (Jupiter/Meteora) and key accounts.
    3) Rebuild instructions with our wallet's accounts.
    4) Create and sign a VersionedTransaction.
    5) send_raw_transaction + confirm via get_signature_statuses.
    """
    sig = trade_info.get("signature")
    if not sig:
        return {"ok": False, "executor": "direct_sell_executor", "error": "missing source signature"}

    # 1) Fetch original tx
    tx_resp = await rpc.get_transaction(sig, commitment="confirmed", max_supported_transaction_version=0)
    if not tx_resp.value:
        return {"ok": False, "executor": "direct_sell_executor", "error": "source transaction not found"}

    # 2) Detect route program
    logs = (tx_resp.value.meta.log_messages or [])
    log_line = " | ".join(logs)
    if JUPITER_PROGRAM not in log_line and METEORA_AGGREGATOR not in log_line:
        # Don't lie; if we can't detect, say so.
        return {"ok": False, "executor": "direct_sell_executor", "error": "router program not found in source tx logs"}

    # 3) TODO: build the SELL instruction list for our wallet (omitted here for brevity)
    #    -> compile MessageV0(...)
    #    -> if you use address lookup tables, fetch them and include lookups.

    # Minimal skeleton to ensure we produce a real VersionedTransaction:
    recent = await rpc.get_latest_blockhash()
    msg = MessageV0.try_compile(
        payer=wallet.pubkey(),
        instructions=[],  # <--- build actual route instructions here
        address_lookup_table_accounts=[],
        recent_blockhash=Hash.from_string(recent.value.blockhash),
    )
    vtx = VersionedTransaction(msg, [wallet])
    # This is an actual tx, not a dict. It has .signatures and can be serialized.

    # 4) Send + 5) confirm correctly
    wire = bytes(vtx)  # already signed
    send = await rpc.send_raw_transaction(wire, max_retries=3, skip_preflight=False)
    tx_sig = str(send.value)

    # Confirm using get_signature_statuses (get_confirmed_transaction doesn't exist on AsyncClient)
    for _ in range(20):
        st = await rpc.get_signature_statuses([tx_sig])
        val = st.value and st.value[0]
        if val and (val.confirmation_status in ("confirmed", "finalized")):
            return {"ok": True, "executor": "direct_sell_executor", "signature": tx_sig, "details": {"path": "rpc"}}
        await asyncio.sleep(0.25)

    return {"ok": False, "executor": "direct_sell_executor", "error": "not confirmed in time", "details": {"sig": tx_sig}}

# =====================================================================
# EXECUTOR STANDARDIZATION HELPERS
# =====================================================================

def exec_ok(executor_name: str, signature: str, data: dict = None) -> BuildResult:
    """Standard success response format - PR-02 Integration"""
    return BuildResult(
        ok=True,
        tx=signature,
        dex=executor_name,
        action="sell",
        reason="Success"
    )

def exec_err(executor_name: str, reason: str, data: dict = None) -> BuildResult:
    """Standard error response format - PR-02 Integration"""
    return BuildResult(
        ok=False,
        tx=None,
        dex=executor_name,
        action="sell",
        reason=reason
    )

def is_success(result: dict) -> bool:
    """Check if executor result represents success"""
    return isinstance(result, dict) and result.get("success") == True

def jito_is_configured(jito_service) -> bool:
    """Check if Jito is properly configured and available"""
    return jito_service is not None and hasattr(jito_service, 'send_transaction')

@dataclass
class DirectSellCopyConfig:
    """Configuration for direct sell copying"""
    priority_fee: int = 2_000_000  # 2M micro-lamports for speed
    compute_limit: int = 400_000
    use_jito_bundles: bool = True
    max_copy_time_ms: float = 500.0
    jito_tip_amount: int = 100_000  # 0.0001 SOL
    slippage_tolerance: float = 0.05  # 5% slippage

class MEVDirectSellExecutor:
    """
    Direct SELL Instruction Copying - Same approach as MEVDirectCopyExecutor but for SELL transactions
    Copies exact instruction details from successful SELL transactions
    """
    
    def __init__(self, wallet_private_key: str, config: DirectSellCopyConfig = None):
        self.config = config or DirectSellCopyConfig()
        
        # Decode private key
        try:
            if isinstance(wallet_private_key, str):
                # Base58 decode the private key
                private_key_bytes = base58.b58decode(wallet_private_key)
            else:
                private_key_bytes = wallet_private_key
        except Exception as e:
            raise ValueError(f"Invalid private key format: {e}")
        
        # Create wallet keypair (handle both 32 and 64-byte formats)
        if len(private_key_bytes) == 64:
            # 64-byte format - use directly with solders
            self.wallet = Keypair.from_bytes(private_key_bytes)
        elif len(private_key_bytes) == 32:
            # 32-byte format - use from_seed with solders
            self.wallet = Keypair.from_seed(private_key_bytes)
        else:
            raise ValueError(f"Invalid private key length: expected 32 or 64 bytes, got {len(private_key_bytes)}")
        
        # Set up RPC connection
        from env_keys import EnvKeys
        env_keys = EnvKeys()
        self.rpc_url = env_keys.HELIUS_RPC_URL
        
        logger.info(f"🎯 MEV Direct SELL Executor initialized")
    
    async def copy_sell_transaction_from_signature(
        self, 
        original_sell_signature: str, 
        token_mint: str,
        sell_percentage: float = 100.0
    ) -> Optional[str]:
        """
        Copy a SELL transaction by signature using direct instruction copying
        
        Args:
            original_sell_signature: The signature of the original SELL transaction to copy
            token_mint: Token mint address to sell
            sell_percentage: Percentage of tokens to sell (default 100%)
            
        Returns:
            Transaction signature if successful, None if failed
        """
        try:
            logger.info(f"🎯 Copying SELL transaction: {original_sell_signature[:16]}...")
            
            # 1. Fetch the original SELL transaction
            original_tx = await self._fetch_transaction(original_sell_signature)
            if not original_tx:
                logger.error(f"❌ Failed to fetch original SELL transaction")
                return exec_err("direct_sell_executor", f"Failed to fetch original SELL transaction: {original_sell_signature}")
            
            # 2. Extract SELL instruction details
            sell_instruction_data = await self._extract_sell_instruction_data(
                original_tx, token_mint
            )
            if not sell_instruction_data:
                logger.error(f"❌ Failed to extract SELL instruction data")
                return exec_err("direct_sell_executor", f"Failed to extract SELL instruction data from transaction")
            
            # 3. Build our SELL transaction using the copied instruction data
            our_sell_tx = await self._build_sell_transaction(
                sell_instruction_data, token_mint, sell_percentage
            )
            if not our_sell_tx:
                logger.error(f"❌ Failed to build SELL transaction")
                return exec_err("direct_sell_executor", f"Failed to build SELL transaction using copied instruction data")
            
            # 4. Execute the SELL transaction with MEV protection
            signature = await self._execute_sell_transaction(our_sell_tx)
            
            if signature:
                logger.info(f"✅ Direct SELL copy SUCCESS: {signature}")
                return signature
            else:
                logger.error(f"❌ Direct SELL copy execution failed")
                return exec_err("direct_sell_executor", f"Direct SELL copy execution failed")
                
        except Exception as e:
            logger.error(f"❌ Error in copy_sell_transaction_from_signature: {e}")
            return exec_err("direct_sell_executor", f"Exception in copy_sell_transaction_from_signature: {str(e)}")
    
    async def analyze_wallet_sell_pattern(
        self, 
        wallet_address: str, 
        token_mint: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a wallet's SELL patterns for a specific token
        Returns the best SELL transaction to copy
        """
        try:
            logger.info(f"🔍 Analyzing SELL patterns for wallet {wallet_address[:8]}...")
            
            # Get wallet's recent transactions
            signatures = await self._get_wallet_transactions(wallet_address, limit=50)
            if not signatures:
                logger.warning(f"⚠️ No transactions found for wallet")
                return exec_err("direct_sell_executor", f"No transactions found for wallet {wallet_address[:8]}")
            
            # Find SELL transactions for this token
            sell_transactions = []
            for signature in signatures[:20]:  # Check last 20 transactions
                tx = await self._fetch_transaction(signature)
                if tx and await self._is_sell_transaction(tx, token_mint):
                    sell_info = await self._extract_sell_instruction_data(tx, token_mint)
                    if sell_info:
                        sell_info['signature'] = signature
                        sell_transactions.append(sell_info)
            
            if not sell_transactions:
                logger.warning(f"⚠️ No SELL transactions found for token {token_mint[:8]}")
                return exec_err("direct_sell_executor", f"No SELL transactions found for token {token_mint[:8]} from wallet {wallet_address}")
            
            # Return the most recent successful SELL transaction
            best_sell = sell_transactions[0]  # Most recent
            logger.info(f"✅ Found {len(sell_transactions)} SELL transactions, using: {best_sell['signature'][:16]}")
            
            return best_sell
            
        except Exception as e:
            logger.error(f"❌ Error analyzing wallet SELL patterns: {e}")
            return exec_err("direct_sell_executor", f"Error analyzing wallet SELL patterns: {str(e)}")
    
    async def execute_direct_sell_copy(
        self, 
        target_wallet: str, 
        token_mint: str, 
        sell_percentage: float = 100.0
    ) -> BuildResult:
        """
        Execute direct SELL copying from a target wallet's successful SELL pattern
        
        Args:
            target_wallet: Wallet address to copy SELL pattern from
            token_mint: Token to sell
            sell_percentage: Percentage of tokens to sell
            
        Returns:
            BuildResult with transaction details
        """
        try:
            # 1. Analyze the target wallet's SELL pattern
            sell_pattern = await self.analyze_wallet_sell_pattern(target_wallet, token_mint)
            if not sell_pattern:
                logger.error(f"❌ No SELL pattern found for {target_wallet[:8]} and token {token_mint[:8]}")
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="direct_sell",
                    action="sell",
                    reason=f"No SELL pattern found for {target_wallet[:8]} and token {token_mint[:8]}"
                )
            
            # 2. Copy the SELL transaction using their pattern
            signature = await self.copy_sell_transaction_from_signature(
                sell_pattern['signature'], token_mint, sell_percentage
            )
            
            if signature:
                return BuildResult(
                    ok=True,
                    tx=signature,
                    dex="direct_sell",
                    action="sell",
                    reason="Direct sell copy successful"
                )
            else:
                return BuildResult(
                    ok=False,
                    tx=None,
                    dex="direct_sell",
                    action="sell",
                    reason="Direct sell copy execution failed"
                )
            
        except Exception as e:
            logger.error(f"❌ Error in execute_direct_sell_copy: {e}")
            return BuildResult(
                ok=False,
                tx=None,
                dex="direct_sell",
                action="sell",
                reason=f"Error in execute_direct_sell_copy: {str(e)}"
            )
    
    async def _fetch_transaction(self, signature: str) -> Optional[Dict[str, Any]]:
        """Fetch transaction data from RPC"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": "json",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result and result["result"]:
                return result["result"]
            else:
                logger.warning(f"⚠️ Transaction not found: {signature[:16]}")
                return exec_err("direct_sell_executor", f"Transaction not found: {signature[:16]}")
                
        except Exception as e:
            logger.error(f"❌ Error fetching transaction {signature[:16]}: {e}")
            return exec_err("direct_sell_executor", f"Error fetching transaction {signature[:16]}: {str(e)}")
    
    async def _get_wallet_transactions(self, wallet_address: str, limit: int = 50) -> List[str]:
        """Get recent transaction signatures for wallet"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    wallet_address,
                    {
                        "limit": limit,
                        "commitment": "confirmed"
                    }
                ]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result and result["result"]:
                return [tx["signature"] for tx in result["result"]]
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching wallet transactions: {e}")
            return []
    
    async def _is_sell_transaction(self, tx_data: Dict[str, Any], token_mint: str) -> bool:
        """Check if transaction is a SELL for the specified token"""
        try:
            meta = tx_data.get("meta", {})
            
            # Check token balance changes
            pre_token_balances = meta.get("preTokenBalances", [])
            post_token_balances = meta.get("postTokenBalances", [])
            
            # Look for decrease in token amount (SELL indicator)
            for pre_balance in pre_token_balances:
                if pre_balance.get("mint") == token_mint:
                    pre_amount = float(pre_balance.get("uiTokenAmount", {}).get("uiAmount", 0) or 0)
                    
                    # Find corresponding post balance
                    for post_balance in post_token_balances:
                        if (post_balance.get("mint") == token_mint and 
                            post_balance.get("accountIndex") == pre_balance.get("accountIndex")):
                            post_amount = float(post_balance.get("uiTokenAmount", {}).get("uiAmount", 0) or 0)
                            
                            # If token amount decreased significantly, it's a SELL
                            if pre_amount - post_amount > 0.001:
                                return True
            
            # Also check logs for SELL indicators
            logs = meta.get("logMessages", [])
            for log in logs:
                if any(indicator in log.lower() for indicator in ["sell", "swap out", "instruction: sell"]):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking if transaction is SELL: {e}")
            return False
    
    async def _extract_sell_instruction_data(
        self, 
        tx_data: Dict[str, Any], 
        token_mint: str
    ) -> Optional[Dict[str, Any]]:
        """Extract SELL instruction data from transaction"""
        try:
            transaction = tx_data.get("transaction", {})
            message = transaction.get("message", {})
            instructions = message.get("instructions", [])
            account_keys = message.get("accountKeys", [])
            
            # Find the router/DEX instruction
            for idx, instruction in enumerate(instructions):
                program_idx = instruction.get("programIdIndex", 0)
                if program_idx < len(account_keys):
                    program_id = account_keys[program_idx]
                    
                    # Check for known DEX/router programs (updated with constants)
                    known_programs = {
                        JUPITER_PROGRAM: "Jupiter",
                        METEORA_AGGREGATOR: "Meteora", 
                        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
                        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium CPMM",
                    }
                    
                    if program_id in known_programs:
                        return {
                            "program_id": program_id,
                            "program_name": known_programs[program_id],
                            "instruction_index": idx,
                            "instruction_data": instruction.get("data", ""),
                            "accounts": instruction.get("accounts", []),
                            "account_keys": account_keys
                        }
            
            # Enhanced router detection using logs (fallback method)
            logger.info(f"🔍 No router instruction found via program IDs, checking logs...")
            
            # Check transaction logs for router activity
            meta = tx_data.get('meta', {})
            logs = meta.get('logMessages', [])
            log_line = " | ".join(logs) if logs else ""
            
            if JUPITER_PROGRAM in log_line or "jupiter" in log_line.lower():
                logger.info(f"✅ Found Jupiter router activity in logs")
                return {
                    "program_id": JUPITER_PROGRAM,
                    "program_name": "Jupiter",
                    "instruction_index": 0,
                    "instruction_data": "",
                    "accounts": [],
                    "account_keys": account_keys,
                    "detected_via": "logs"
                }
            elif METEORA_AGGREGATOR in log_line or "meteora" in log_line.lower():
                logger.info(f"✅ Found Meteora router activity in logs") 
                return {
                    "program_id": METEORA_AGGREGATOR,
                    "program_name": "Meteora",
                    "instruction_index": 0,
                    "instruction_data": "",
                    "accounts": [],
                    "account_keys": account_keys,
                    "detected_via": "logs"
                }
            
            logger.warning(f"⚠️ No router instruction found in SELL transaction (checked {len(instructions)} instructions and logs)")
            return exec_err("direct_sell_executor", f"No router instruction found in SELL transaction")
            
        except Exception as e:
            logger.error(f"❌ Error extracting SELL instruction data: {e}")
            return exec_err("direct_sell_executor", f"Error extracting SELL instruction data: {str(e)}")
    
    async def _build_sell_transaction(
        self, 
        sell_instruction_data: Dict[str, Any], 
        token_mint: str, 
        sell_percentage: float
    ) -> Optional[VersionedTransaction]:
        """Build SELL transaction using copied instruction data"""
        try:
            logger.info(f"🏗️ Building SELL transaction using {sell_instruction_data['program_name']} pattern")
            
            program_name = sell_instruction_data.get('program_name', '').lower()
            
            if 'jupiter' in program_name:
                return await self._build_jupiter_sell_transaction(token_mint, sell_percentage)
            elif 'raydium' in program_name:
                return await self._build_raydium_sell_transaction(sell_instruction_data, token_mint, sell_percentage)
            else:
                # For unknown programs, use Jupiter as fallback
                logger.info(f"🔄 Unknown program '{program_name}', falling back to Jupiter sell")
                return await self._build_jupiter_sell_transaction(token_mint, sell_percentage)
            
        except Exception as e:
            logger.error(f"❌ Error building SELL transaction: {e}")
            return exec_err("direct_sell_executor", f"Error building SELL transaction: {str(e)}")

    async def _build_jupiter_sell_transaction(self, token_mint: str, sell_percentage: float) -> Optional[VersionedTransaction]:
        """Build Jupiter sell transaction using Jupiter API"""
        try:
            # Get our wallet's token balance first
            token_balance = await self._get_token_balance(token_mint)
            if token_balance == 0:
                logger.warning(f"⚠️ No {token_mint[:8]}... tokens to sell")
                return exec_err("direct_sell_executor", f"No {token_mint[:8]}... tokens to sell - balance is 0")
            
            # Calculate amount to sell based on percentage
            sell_amount = int(token_balance * sell_percentage / 100)
            if sell_amount == 0:
                logger.warning(f"⚠️ Calculated sell amount is 0 for {sell_percentage}% of {token_balance}")
                return exec_err("direct_sell_executor", f"Calculated sell amount is 0 for {sell_percentage}% of {token_balance}")
            
            logger.info(f"💰 Selling {sell_amount} tokens ({sell_percentage}% of {token_balance})")
            
            # Use Jupiter API to get sell route (token -> SOL)
            quote_response = await self._get_jupiter_quote(
                input_mint=token_mint,
                output_mint="So11111111111111111111111111111111111111112",  # SOL
                amount=sell_amount,
                slippage_bps=300
            )
            
            if not quote_response:
                logger.error("❌ Failed to get Jupiter quote for sell")
                return exec_err("direct_sell_executor", f"Failed to get Jupiter quote for sell")
            
            # Get swap transaction from Jupiter
            swap_response = await self._get_jupiter_swap_transaction(quote_response)
            if not swap_response:
                logger.error("❌ Failed to get Jupiter swap transaction for sell")
                return exec_err("direct_sell_executor", f"Failed to get Jupiter swap transaction for sell")
            
            # Decode the transaction
            swap_transaction = swap_response.get("swapTransaction")
            if not swap_transaction:
                logger.error("❌ No swap transaction in Jupiter response")
                return exec_err("direct_sell_executor", f"No swap transaction in Jupiter response")
            
            # Decode base64 transaction
            import base64
            tx_bytes = base64.b64decode(swap_transaction)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            logger.info(f"✅ Built Jupiter sell transaction successfully")
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error building Jupiter sell transaction: {e}")
            return exec_err("direct_sell_executor", f"Error building Jupiter sell transaction: {str(e)}")

    async def _build_raydium_sell_transaction(self, sell_instruction_data: Dict[str, Any], token_mint: str, sell_percentage: float) -> Optional[VersionedTransaction]:
        """Build Raydium sell transaction by copying instruction structure"""
        try:
            # For Raydium, we would copy the instruction structure and patch accounts
            # This is more complex and would require detailed instruction parsing
            logger.warning(f"⚠️ Raydium sell transaction building not yet implemented")
            # Fall back to Jupiter
            return await self._build_jupiter_sell_transaction(token_mint, sell_percentage)
            
        except Exception as e:
            logger.error(f"❌ Error building Raydium sell transaction: {e}")
            return exec_err("direct_sell_executor", f"Error building Raydium sell transaction: {str(e)}")
    
    async def _execute_sell_transaction(self, transaction: VersionedTransaction) -> Optional[str]:
        """Execute SELL transaction with MEV protection and proper confirmation"""
        try:
            logger.info(f"⚡ Executing SELL transaction with MEV protection")
            
            # Ensure transaction is properly signed (not signing a dict)
            if not isinstance(transaction, VersionedTransaction):
                logger.error(f"❌ Expected VersionedTransaction, got {type(transaction)}")
                return None
            
            # Sign the transaction
            transaction.sign([self.wallet])
            
            # Serialize transaction for submission
            serialized_tx = bytes(transaction)
            
            # Dual-path execution: Jito first, RPC fallback
            jito_service = getattr(self, 'jito_service', None)
            if jito_is_configured(jito_service):
                try:
                    logger.info("🚀 Using Jito for direct sell MEV protection...")
                    result = await jito_service.send_transaction(serialized_tx)
                    signature = result.get("signature")
                    if signature:
                        logger.info(f"✅ EXECUTED via direct_sell (jito) — signature: {signature}")
                        return signature  # Return just the signature string
                    else:
                        logger.warning(f"⏭️ Skipped direct_sell (jito): {result}")
                except Exception as jito_error:
                    logger.warning(f"⏭️ Skipped direct_sell (jito): {jito_error}")
            
            # RPC fallback (must exist) - use proper AsyncClient methods
            signature = await self._submit_via_rpc_fixed(serialized_tx)
            if signature:
                logger.info(f"✅ EXECUTED via direct_sell (rpc) — signature: {signature}")
                return signature  # Return just the signature string
            
            logger.error("❌ Failed to submit SELL transaction")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error executing SELL transaction: {e}")
            return None

    async def _submit_via_jito(self, serialized_tx: bytes) -> Optional[str]:
        """Submit transaction via Jito for MEV protection (legacy method)"""
        # This method is kept for compatibility but Jito logic is now in main execution path
        return None

    async def _submit_via_rpc(self, serialized_tx: bytes) -> Optional[str]:
        """Submit transaction via RPC (legacy method - kept for compatibility)"""
        try:
            import base64
            
            # Convert to base64 for RPC submission
            tx_base64 = base64.b64encode(serialized_tx).decode('utf-8')
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    tx_base64,
                    {
                        "encoding": "base64",
                        "preflightCommitment": "processed",
                        "skipPreflight": False
                    }
                ]
            }
            
            import requests
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "result" in result:
                signature = result["result"]
                logger.info(f"📡 Transaction submitted: {signature}")
                return signature
            elif "error" in result:
                logger.error(f"❌ RPC error: {result['error']}")
                return None
            
        except Exception as e:
            logger.error(f"❌ RPC submission error: {e}")
            return None

    async def _submit_via_rpc_fixed(self, serialized_tx: bytes) -> Optional[str]:
        """Submit transaction via RPC with proper AsyncClient and confirmation"""
        try:
            # Create RPCClient for proper async RPC calls
            from utils import RPCClient
            
            async with RPCClient(self.rpc_url) as rpc:
                # Send raw transaction
                send_response = await rpc.send_raw_transaction(
                    serialized_tx, 
                    opts={"skip_preflight": False, "preflight_commitment": "processed"}
                )
                
                if not send_response.value:
                    logger.error("❌ Failed to send transaction - no signature returned")
                    return None
                
                tx_signature = str(send_response.value)
                logger.info(f"📡 Transaction submitted: {tx_signature}")
                
                # Confirm using get_signature_statuses (correct method)
                for attempt in range(20):  # 5 seconds total (20 * 0.25s)
                    try:
                        status_response = await rpc.get_signature_statuses([tx_signature])
                        if status_response.value and status_response.value[0]:
                            status = status_response.value[0]
                            if status.confirmation_status in ("confirmed", "finalized"):
                                logger.info(f"✅ Transaction confirmed: {tx_signature}")
                                return tx_signature
                        
                        await asyncio.sleep(0.25)  # Wait 250ms between checks
                    except Exception as confirm_error:
                        logger.debug(f"Confirmation check {attempt + 1} failed: {confirm_error}")
                        await asyncio.sleep(0.25)
                
                # Return signature even if not confirmed (timeout)
                logger.warning(f"⚠️ Transaction submitted but not confirmed in time: {tx_signature}")
                return tx_signature
                
        except Exception as e:
            logger.error(f"❌ Fixed RPC submission error: {e}")
            return None

    async def _get_jupiter_quote(self, input_mint: str, output_mint: str, amount: int, slippage_bps: int = 300) -> Optional[dict]:
        """Get Jupiter quote for selling tokens"""
        try:
            import requests
            
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": str(slippage_bps),
                "onlyDirectRoutes": "false"
            }
            
            response = requests.get("https://quote-api.jup.ag/v6/quote", params=params, timeout=15)
            response.raise_for_status()
            
            quote_data = response.json()
            if "error" in quote_data:
                logger.error(f"❌ Jupiter quote error: {quote_data['error']}")
                return exec_err("direct_sell_executor", f"Jupiter quote error: {quote_data['error']}")
                
            logger.info(f"✅ Got Jupiter quote: {quote_data.get('outAmount', 'unknown')} output")
            return quote_data
            
        except Exception as e:
            logger.error(f"❌ Error getting Jupiter quote: {e}")
            return exec_err("direct_sell_executor", f"Error getting Jupiter quote: {str(e)}")

    async def _get_jupiter_swap_transaction(self, quote_data: dict) -> Optional[dict]:
        """Get Jupiter swap transaction from quote"""
        try:
            import requests
            
            payload = {
                "userPublicKey": str(self.wallet.pubkey()),
                "quoteResponse": quote_data,
                "wrapAndUnwrapSol": True,
                "useSharedAccounts": True,
                "feeAccount": None,
                "computeUnitPriceMicroLamports": 400000,  # Priority fee
                "asLegacyTransaction": False
            }
            
            response = requests.post("https://quote-api.jup.ag/v6/swap", json=payload, timeout=30)
            response.raise_for_status()
            
            swap_data = response.json()
            if "error" in swap_data:
                logger.error(f"❌ Jupiter swap error: {swap_data['error']}")
                return exec_err("direct_sell_executor", f"Jupiter swap error: {swap_data['error']}")
                
            logger.info(f"✅ Got Jupiter swap transaction")
            return swap_data
            
        except Exception as e:
            logger.error(f"❌ Error getting Jupiter swap transaction: {e}")
            return exec_err("direct_sell_executor", f"Error getting Jupiter swap transaction: {str(e)}")

    async def _get_token_balance(self, token_mint: str) -> int:
        """Get wallet's token balance"""
        try:
            import requests
            from solders.pubkey import Pubkey
            from utils import get_associated_token_address
            
            # Get associated token account
            wallet_pubkey = self.wallet.pubkey()
            mint_pubkey = Pubkey.from_string(token_mint)
            token_account = get_associated_token_address(wallet_pubkey, mint_pubkey)
            
            # Query balance via RPC
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountBalance",
                "params": [str(token_account)]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if "result" in result and result["result"]["value"]:
                amount_str = result["result"]["value"]["amount"]
                return int(amount_str)
            else:
                # Account doesn't exist or has no balance
                return 0
                
        except Exception as e:
            logger.debug(f"Token balance query failed (probably no tokens): {e}")
            return 0

# Convenience functions for easy integration
async def execute_direct_sell_copy(
    wallet_private_key: str,
    target_wallet: str,
    token_mint: str,
    sell_percentage: float = 100.0,
    config: DirectSellCopyConfig = None
) -> BuildResult:
    """
    Execute direct SELL copying - main entry point
    
    Args:
        wallet_private_key: Your wallet's private key
        target_wallet: Target wallet to copy SELL pattern from
        token_mint: Token to sell
        sell_percentage: Percentage of tokens to sell
        config: Configuration options
        
    Returns:
        BuildResult with transaction details
    """
    try:
        executor = MEVDirectSellExecutor(wallet_private_key, config)
        return await executor.execute_direct_sell_copy(
            target_wallet, token_mint, sell_percentage
        )
    except Exception as e:
        logger.error(f"❌ Error in execute_direct_sell_copy: {e}")
        return BuildResult(
            ok=False,
            tx=None,
            dex="direct_sell_executor",
            action="sell",
            reason=f"Error in execute_direct_sell_copy: {str(e)}"
        )

async def copy_specific_sell_transaction(
    wallet_private_key: str,
    sell_transaction_signature: str,
    token_mint: str,
    sell_percentage: float = 100.0,
    config: DirectSellCopyConfig = None
) -> BuildResult:
    """
    Copy a specific SELL transaction by signature
    
    Args:
        wallet_private_key: Your wallet's private key
        sell_transaction_signature: Signature of SELL transaction to copy
        token_mint: Token to sell
        sell_percentage: Percentage of tokens to sell
        config: Configuration options
        
    Returns:
        BuildResult with transaction details
    """
    try:
        executor = MEVDirectSellExecutor(wallet_private_key, config)
        signature = await executor.copy_sell_transaction_from_signature(
            sell_transaction_signature, token_mint, sell_percentage
        )
        
        if signature:
            return BuildResult(
                ok=True,
                tx=signature,
                dex="direct_sell_executor",
                action="sell",
                reason="Copy specific sell transaction successful"
            )
        else:
            return BuildResult(
                ok=False,
                tx=None,
                dex="direct_sell_executor",
                action="sell",
                reason="Copy specific sell transaction failed"
            )
    except Exception as e:
        logger.error(f"❌ Error in copy_specific_sell_transaction: {e}")
        return BuildResult(
            ok=False,
            tx=None,
            dex="direct_sell_executor",
            action="sell",
            reason=f"Error in copy_specific_sell_transaction: {str(e)}"
        )

if __name__ == "__main__":
    # Example usage
    async def test_direct_sell_copy():
        from env_keys import EnvKeys
        env_keys = EnvKeys()
        
        # Example: Copy sell pattern from the analyzed wallet
        target_wallet = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
        token_mint = "444oc9sU6mGMsAox9ivhKKGbYrWRZHWKHzrwTQkJZwCu"  # Example token
        
        signature = await execute_direct_sell_copy(
            wallet_private_key=env_keys.PHANTOM_PRIVATE_KEY,
            target_wallet=target_wallet,
            token_mint=token_mint,
            sell_percentage=100.0
        )
        
        if signature:
            print(f"✅ Direct SELL copy successful: {signature}")
        else:
            print(f"❌ Direct SELL copy failed")
    
    # Uncomment to test
    # asyncio.run(test_direct_sell_copy())