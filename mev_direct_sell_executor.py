#!/usr/bin/env python3
"""
MEV Direct SELL Executor - Direct Instruction Copying for SELL Transactions
Uses the same approach as BUYs: copy exact instruction details from target wallet's SELL transactions
"""

import asyncio
import logging
import requests
import base64
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned
import base58

logger = logging.getLogger(__name__)

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
                return None
            
            # 2. Extract SELL instruction details
            sell_instruction_data = await self._extract_sell_instruction_data(
                original_tx, token_mint
            )
            if not sell_instruction_data:
                logger.error(f"❌ Failed to extract SELL instruction data")
                return None
            
            # 3. Build our SELL transaction using the copied instruction data
            our_sell_tx = await self._build_sell_transaction(
                sell_instruction_data, token_mint, sell_percentage
            )
            if not our_sell_tx:
                logger.error(f"❌ Failed to build SELL transaction")
                return None
            
            # 4. Execute the SELL transaction with MEV protection
            signature = await self._execute_sell_transaction(our_sell_tx)
            
            if signature:
                logger.info(f"✅ Direct SELL copy SUCCESS: {signature}")
                return signature
            else:
                logger.error(f"❌ Direct SELL copy execution failed")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error in copy_sell_transaction_from_signature: {e}")
            return None
    
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
                return None
            
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
                return None
            
            # Return the most recent successful SELL transaction
            best_sell = sell_transactions[0]  # Most recent
            logger.info(f"✅ Found {len(sell_transactions)} SELL transactions, using: {best_sell['signature'][:16]}")
            
            return best_sell
            
        except Exception as e:
            logger.error(f"❌ Error analyzing wallet SELL patterns: {e}")
            return None
    
    async def execute_direct_sell_copy(
        self, 
        target_wallet: str, 
        token_mint: str, 
        sell_percentage: float = 100.0
    ) -> Optional[str]:
        """
        Execute direct SELL copying from a target wallet's successful SELL pattern
        
        Args:
            target_wallet: Wallet address to copy SELL pattern from
            token_mint: Token to sell
            sell_percentage: Percentage of tokens to sell
            
        Returns:
            Transaction signature if successful, None if failed
        """
        try:
            # 1. Analyze the target wallet's SELL pattern
            sell_pattern = await self.analyze_wallet_sell_pattern(target_wallet, token_mint)
            if not sell_pattern:
                logger.error(f"❌ No SELL pattern found for {target_wallet[:8]} and token {token_mint[:8]}")
                return None
            
            # 2. Copy the SELL transaction using their pattern
            signature = await self.copy_sell_transaction_from_signature(
                sell_pattern['signature'], token_mint, sell_percentage
            )
            
            return signature
            
        except Exception as e:
            logger.error(f"❌ Error in execute_direct_sell_copy: {e}")
            return None
    
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
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching transaction {signature[:16]}: {e}")
            return None
    
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
                    
                    # Check for known DEX/router programs
                    known_programs = {
                        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter",
                        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
                        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium CPMM",
                        "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN": "Custom Router"
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
            
            logger.warning(f"⚠️ No router instruction found in SELL transaction")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting SELL instruction data: {e}")
            return None
    
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
            return None

    async def _build_jupiter_sell_transaction(self, token_mint: str, sell_percentage: float) -> Optional[VersionedTransaction]:
        """Build Jupiter sell transaction using Jupiter API"""
        try:
            # Get our wallet's token balance first
            token_balance = await self._get_token_balance(token_mint)
            if token_balance == 0:
                logger.warning(f"⚠️ No {token_mint[:8]}... tokens to sell")
                return None
            
            # Calculate amount to sell based on percentage
            sell_amount = int(token_balance * sell_percentage / 100)
            if sell_amount == 0:
                logger.warning(f"⚠️ Calculated sell amount is 0 for {sell_percentage}% of {token_balance}")
                return None
            
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
                return None
            
            # Get swap transaction from Jupiter
            swap_response = await self._get_jupiter_swap_transaction(quote_response)
            if not swap_response:
                logger.error("❌ Failed to get Jupiter swap transaction for sell")
                return None
            
            # Decode the transaction
            swap_transaction = swap_response.get("swapTransaction")
            if not swap_transaction:
                logger.error("❌ No swap transaction in Jupiter response")
                return None
            
            # Decode base64 transaction
            import base64
            tx_bytes = base64.b64decode(swap_transaction)
            transaction = VersionedTransaction.from_bytes(tx_bytes)
            
            logger.info(f"✅ Built Jupiter sell transaction successfully")
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error building Jupiter sell transaction: {e}")
            return None

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
            return None
    
    async def _execute_sell_transaction(self, transaction: VersionedTransaction) -> Optional[str]:
        """Execute SELL transaction with MEV protection"""
        try:
            logger.info(f"⚡ Executing SELL transaction with MEV protection")
            
            # Sign the transaction
            transaction.sign([self.wallet])
            
            # Serialize transaction for submission
            serialized_tx = bytes(transaction)
            
            # Try to submit via Jito if configured
            if self.config and getattr(self.config, 'use_jito', False):
                signature = await self._submit_via_jito(serialized_tx)
                if signature:
                    logger.info(f"✅ SELL transaction submitted via Jito: {signature}")
                    return signature
            
            # Fallback to RPC submission
            signature = await self._submit_via_rpc(serialized_tx)
            if signature:
                logger.info(f"✅ SELL transaction submitted via RPC: {signature}")
                return signature
            
            logger.error("❌ Failed to submit SELL transaction")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error executing SELL transaction: {e}")
            return None

    async def _submit_via_jito(self, serialized_tx: bytes) -> Optional[str]:
        """Submit transaction via Jito for MEV protection"""
        try:
            # This would integrate with Jito service
            logger.warning("⚠️ Jito submission not yet implemented")
            return None
        except Exception as e:
            logger.error(f"❌ Jito submission error: {e}")
            return None

    async def _submit_via_rpc(self, serialized_tx: bytes) -> Optional[str]:
        """Submit transaction via RPC"""
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
                return None
                
            logger.info(f"✅ Got Jupiter quote: {quote_data.get('outAmount', 'unknown')} output")
            return quote_data
            
        except Exception as e:
            logger.error(f"❌ Error getting Jupiter quote: {e}")
            return None

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
                return None
                
            logger.info(f"✅ Got Jupiter swap transaction")
            return swap_data
            
        except Exception as e:
            logger.error(f"❌ Error getting Jupiter swap transaction: {e}")
            return None

    async def _get_token_balance(self, token_mint: str) -> int:
        """Get wallet's token balance"""
        try:
            import requests
            from solders.pubkey import Pubkey
            from spl.token.instructions import get_associated_token_address
            
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
) -> Optional[str]:
    """
    Execute direct SELL copying - main entry point
    
    Args:
        wallet_private_key: Your wallet's private key
        target_wallet: Target wallet to copy SELL pattern from
        token_mint: Token to sell
        sell_percentage: Percentage of tokens to sell
        config: Configuration options
        
    Returns:
        Transaction signature if successful, None if failed
    """
    try:
        executor = MEVDirectSellExecutor(wallet_private_key, config)
        return await executor.execute_direct_sell_copy(
            target_wallet, token_mint, sell_percentage
        )
    except Exception as e:
        logger.error(f"❌ Error in execute_direct_sell_copy: {e}")
        return None

async def copy_specific_sell_transaction(
    wallet_private_key: str,
    sell_transaction_signature: str,
    token_mint: str,
    sell_percentage: float = 100.0,
    config: DirectSellCopyConfig = None
) -> Optional[str]:
    """
    Copy a specific SELL transaction by signature
    
    Args:
        wallet_private_key: Your wallet's private key
        sell_transaction_signature: Signature of SELL transaction to copy
        token_mint: Token to sell
        sell_percentage: Percentage of tokens to sell
        config: Configuration options
        
    Returns:
        Transaction signature if successful, None if failed
    """
    try:
        executor = MEVDirectSellExecutor(wallet_private_key, config)
        return await executor.copy_sell_transaction_from_signature(
            sell_transaction_signature, token_mint, sell_percentage
        )
    except Exception as e:
        logger.error(f"❌ Error in copy_specific_sell_transaction: {e}")
        return None

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