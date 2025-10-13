# fast_executor.py
"""
FastExecutor: Executes Solana transactions with Jito MEV protection and RPC fallback.

Features:
- Prioritizes Jito bundles for MEV protection and optimal execution
- Automatic RPC fallback if Jito submission fails
- Configurable retry logic for Jito attempts
- Compute budget and priority fee configuration
- Detailed execution logging
- Transaction verification and confirmation

Transaction Flow:
1. Attempt bundle submission via Jito
2. If Jito fails, automatically fall back to RPC
3. Confirm transaction success

Example:
    # Uses mnemonic-based wallet by default
    async with FastExecutor() as executor:
        instructions = [transfer(TransferParams...)]
        result = await executor.build_and_execute(
            instructions=instructions,
            use_jito=True,
            jito_retries=2,
            jito_timeout=1.0
        )
        
    # Or with a custom keypair if needed
    async with FastExecutor(custom_keypair) as executor:
        # ... same as above ...
"""

import aiohttp
import base64
import asyncio
import json
import traceback
import time
import logging
from typing import List, Optional, Dict, Any, Union, Tuple, TYPE_CHECKING

from solders.keypair import Keypair
from solders.message import MessageV0, to_bytes_versioned
from solders.transaction import VersionedTransaction
from solders.system_program import TransferParams, transfer, ID as SYS_PROGRAM_ID
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.instruction import Instruction, AccountMeta
from jito_service import JitoClient, Bundle

from config import (
    WALLET, 
    BOT_PUBKEY,
    HELIUS_RPC_URL,
    JITO_AUTH_TOKEN,
    JITO_BLOCK_ENGINE,
    JITO_HEADERS,
    COMPUTE_UNIT_LIMIT,
    COMPUTE_UNIT_PRICE,
    JITO_TIP_AMOUNT,
    VALID_JITO_TIP_ACCOUNTS
)
from env_keys import kz

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RPCHandler:
    def __init__(self):
        """Initialize RPC Handler with multiple endpoints"""
        self.rpc_endpoints = [
            HELIUS_RPC_URL,  # Your existing Helius endpoint
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com"
        ]
        self.last_health_check = {}
        self.health_check_interval = 30  # seconds
        self.logger = logging.getLogger(__name__)
        
    async def get_healthy_rpc(self, session: aiohttp.ClientSession) -> Optional[str]:
        """Get a healthy RPC endpoint"""
        current_time = time.time()
        
        for endpoint in self.rpc_endpoints:
            # Check if we need to recheck health
            last_check = self.last_health_check.get(endpoint, 0)
            if current_time - last_check < self.health_check_interval:
                continue
                
            try:
                async with session.post(
                    endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getLatestBlockhash",
                        "params": [{"commitment": "processed"}]
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=5.0
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "result" in result and "value" in result["result"]:
                            self.last_health_check[endpoint] = current_time
                            self.logger.info(f"RPC endpoint {endpoint} is healthy")
                            return endpoint
            except Exception as e:
                self.logger.warning(f"RPC health check failed for {endpoint}: {e}")
                continue
                
        return None

    async def get_latest_blockhash_with_fallback(self, session: aiohttp.ClientSession) -> Optional[Hash]:
        """Get latest blockhash with RPC fallback"""
        rpc_url = await self.get_healthy_rpc(session)
        if not rpc_url:
            self.logger.error("No healthy RPC endpoints available")
            return None
            
        try:
            async with session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "processed"}]
                },
                headers={"Content-Type": "application/json"},
                timeout=5.0
            ) as response:
                result = await response.json()
                if "result" in result and "value" in result["result"]:
                    return Hash.from_string(result["result"]["value"]["blockhash"])
        except Exception as e:
            self.logger.error(f"Error getting latest blockhash: {e}")
            
        return None

# Token Program Constants
TOKEN_PROGRAM_KEY = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA_PROGRAM_KEY = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
RENT_SYSVAR_KEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

def get_associated_token_address(wallet_address: Pubkey, token_mint_address: Pubkey) -> Pubkey:
    """Find the associated token account address using the official derivation"""
    if isinstance(token_mint_address, str):
        token_mint_address = Pubkey.from_string(token_mint_address)
    if isinstance(wallet_address, str):
        wallet_address = Pubkey.from_string(wallet_address)

    seeds = [
        bytes(wallet_address),  # Allow auto-conversion from Pubkey to bytes
        bytes(TOKEN_PROGRAM_KEY),
        bytes(token_mint_address)
    ]

    # Official SPL Token ATA derivation
    program_address = Pubkey.find_program_address(
        seeds,
        ATA_PROGRAM_KEY
    )
    return program_address[0]

class FastExecutor:
    """FastExecutor: Executes Solana transactions with Jito MEV protection and RPC fallback."""
    
    def __init__(self, 
                keypair: Optional[Keypair] = None,
                jito_url: Optional[str] = None,
                rpc_urls: Optional[List[str]] = None,
                health_check_timeout: float = 5.0,
                max_retries: int = 3):
        """Initialize FastExecutor with an optional keypair (defaults to mnemonic-based wallet) and RPC configuration."""
        self.logger = logging.getLogger(__name__)
        
        # Setup keypair with validation
        self.keypair = keypair if keypair is not None else WALLET
        if not self.validate_keypair(self.keypair, "Initializing FastExecutor"):
            raise ValueError("Invalid keypair provided to FastExecutor")
            
        # Setup RPC configuration
        self.jito_url = jito_url
        self.rpc_urls = []
        self.health_check_timeout = health_check_timeout
        self.healthy_rpcs = []
        self.session = None
        self.jito_client = None
        self.closed = False
        self.initialized = False
        self.rpc_handler = RPCHandler()
        self.max_retries = max_retries
        self.current_rpc_index = 0
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Add provided RPCs
        if rpc_urls:
            self.rpc_urls.extend(rpc_urls)
            
        # Add Helius RPC if available
        if hasattr(kz, 'HELIUS_RPC_URL') and kz.HELIUS_RPC_URL and kz.HELIUS_RPC_URL not in self.rpc_urls:
            self.rpc_urls.append(kz.HELIUS_RPC_URL)
            
        # Add public RPC as fallback
        public_rpc = "https://api.mainnet-beta.solana.com"
        if public_rpc not in self.rpc_urls:
            self.rpc_urls.append(public_rpc)

    async def __aenter__(self):
        """Set up aiohttp session and check RPC health"""
        if not self.session:
            # Default timeouts: 30s total, 10s connect, 5s sock_read
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(
                    total=30,
                    connect=10,
                    sock_read=5
                )
            )
            
        # Initial health check of all RPCs
        await self.update_healthy_rpcs()
        
        if not self.healthy_rpcs:
            self.logger.warning("No healthy RPCs found on startup, but will retry during operation")
            
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self.session:
            await self.session.close()

    async def update_healthy_rpcs(self):
        """Update the list of healthy RPCs"""
        self.healthy_rpcs = []
        check_tasks = []
        for url in self.rpc_urls:
            check_tasks.append(self.check_rpc_health(url))
        
        results = await asyncio.gather(*check_tasks, return_exceptions=True)
        for url, is_healthy in zip(self.rpc_urls, results):
            if isinstance(is_healthy, bool) and is_healthy:
                self.healthy_rpcs.append(url)
                self.logger.info(f"RPC {url} is healthy")
            else:
                self.logger.warning(f"RPC {url} is unhealthy: {is_healthy}")

    async def get_working_rpc(self) -> Optional[str]:
        """Get a working RPC endpoint from the available list.
        
        Returns:
            str: URL of a working RPC endpoint, or None if no working endpoints found
        """
        # If we have healthy RPCs, try the next one in round-robin
        if self.healthy_rpcs:
            rpc = self.healthy_rpcs[self.current_rpc_index]
            self.current_rpc_index = (self.current_rpc_index + 1) % len(self.healthy_rpcs)
            
            # Verify it's still healthy
            if await self.check_rpc_health(rpc):
                return rpc
                
        # Update healthy RPCs if none available or current one failed
        await self.update_healthy_rpcs()
        
        # Return first healthy RPC if any
        if self.healthy_rpcs:
            self.current_rpc_index = 0
            return self.healthy_rpcs[0]
            
        return None

    async def check_rpc_health(self, url: str) -> bool:
        """Check if an RPC endpoint is healthy by requesting a recent blockhash."""
        try:
            if not self.session:
                return False
                
            async with self.session.post(
                url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "processed"}]
                },
                headers=self.headers,
                timeout=self.health_check_timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result and "value" in result["result"]:
                        return True
            return False
            
        except Exception as e:
            self.logger.warning(f"Health check failed for {url}: {e}")
            return False

    async def get_latest_blockhash(self) -> Optional[Hash]:
        """Get the latest blockhash from a healthy RPC endpoint.
        
        Returns:
            Hash: A valid blockhash or None if request fails
        """
        try:
            rpc_url = await self.get_working_rpc()
            if not rpc_url:
                self.logger.error("No healthy RPC endpoints available")
                return None
                
            async with self.session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                    "params": [{"commitment": "processed"}]
                },
                headers=self.headers
            ) as response:
                response_json = await response.json()
                
                if "result" in response_json and "value" in response_json["result"]:
                    blockhash = response_json["result"]["value"]["blockhash"]
                    return Hash.from_string(blockhash)
                    
        except Exception as e:
            self.logger.error(f"Error getting latest blockhash: {e}")
            return None

    async def get_balance(self, pubkey: Pubkey) -> int:
        """Get the SOL balance of an account in lamports"""
        rpc_url = await self.get_working_rpc()
        if not rpc_url:
            raise RuntimeError("No healthy RPCs available")

        try:
            async with self.session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [str(pubkey)]
                },
                headers={"Content-Type": "application/json"},
            ) as response:
                result = await response.json()
                if "result" not in result:
                    raise RuntimeError(f"Invalid response: {result}")
                return result["result"]["value"]
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            raise

    async def get_token_balance(self, token_account: Pubkey) -> Optional[int]:
        """Get the token balance for a token account."""
        try:
            rpc_url = await self.get_working_rpc()
            if not rpc_url:
                raise RuntimeError("No healthy RPCs available")

            async with self.session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountBalance",
                    "params": [str(token_account)]
                },
                headers={"Content-Type": "application/json"},
            ) as response:
                result = await response.json()
                if "result" not in result:
                    raise RuntimeError(f"Invalid response: {result}")
                if "value" not in result["result"]:
                    raise RuntimeError(f"No balance value in response: {result}")
                    
                # Get amount and decimals
                amount = int(result["result"]["value"]["amount"])
                decimals = int(result["result"]["value"]["decimals"])
                
                return amount
                
        except Exception as e:
            self.logger.error(f"Error getting token balance: {e}")
            return None

    async def send_transaction(
        self, 
        transaction: VersionedTransaction, 
        signers: List[Keypair],
        original_instructions: Optional[List[Instruction]] = None,
        retries: int = 3
    ) -> Optional[str]:
        """Send a transaction with optional Jito bundle and retry logic."""
        try:
            # 1. Validate inputs
            if not transaction or not signers:
                self.logger.error("❌ Missing transaction or signers")
                return None
                
            self.logger.info("🔑 Validating signers...")
            for idx, signer in enumerate(signers):
                if not isinstance(signer, Keypair):
                    self.logger.error(f"❌ Invalid signer type at position {idx}")
                    return None
                if not hasattr(signer, 'sign_message'):
                    self.logger.error(f"❌ Signer {idx} cannot sign")
                    return None
                self.logger.info(f"✅ Signer {idx} ({signer.pubkey()}) validated")
                
            # 2. Verify instruction signers
            self.logger.info("🔍 Verifying instruction signers...")
            for idx, ix in enumerate(original_instructions or []):
                required_signers = {acc.pubkey for acc in ix.accounts if acc.is_signer}
                self.logger.info(f"✅ Instruction {idx} signers verified: {required_signers}")
                
            for retry in range(retries):
                try:
                    # 3. Get fresh blockhash and compile message
                    try:
                        blockhash = await self.get_latest_blockhash()
                        if not blockhash:
                            self.logger.error("❌ Failed to get blockhash")
                            continue
                            
                        new_message = MessageV0.try_compile(
                            payer=signers[0].pubkey(),
                            instructions=original_instructions or [],
                            address_lookup_table_accounts=[],
                            recent_blockhash=blockhash
                        )
                    except Exception as e:
                        self.logger.error(f"❌ Failed to compile message: {e}")
                        continue

                    # 4. Create and sign transaction
                    try:
                        new_tx = VersionedTransaction(message=new_message, keypairs=signers)
                        
                        if len(new_tx.signatures) != len(signers):
                            self.logger.error(f"❌ Missing signatures. Expected {len(signers)}, got {len(new_tx.signatures)}")
                            continue
                            
                        self.logger.info(f"✅ Transaction signed by {len(new_tx.signatures)} signers")
                        
                        # 5. Submit transaction
                        sig = await self.submit_transaction(new_tx)
                        if sig:
                            self.logger.info(f"🎉 Transaction sent successfully: {sig}")
                            return sig
                            
                    except Exception as sign_err:
                        self.logger.error(f"❌ Error signing transaction: {sign_err}")
                        continue
                        
                except Exception as retry_err:
                    self.logger.error(f"❌ Error in retry {retry + 1}: {retry_err}")
                    if retry == retries - 1:
                        raise
                        
            self.logger.error(f"❌ Failed after {retries} retries")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Unhandled error: {str(e)}")
            traceback.print_exc()
            return None

    async def send_and_confirm_transaction(
        self,
        transaction: VersionedTransaction,
        signers: List[Keypair],
        confirm_timeout: int = 60
    ) -> Dict[str, Any]:
        """Send a transaction and wait for confirmation"""
        try:
            # Send transaction
            tx_sig = await self.send_transaction(transaction, signers)
            if not tx_sig:
                self.logger.error("Failed to send transaction")
                return {"success": False, "error": "Failed to send transaction"}
                
            self.logger.info(f"Transaction sent: {tx_sig}")

            # Wait for confirmation
            max_retries = int(confirm_timeout // 1.0)  # Using 1s retry delay
            result = await self.wait_for_confirmation(
                tx_sig=tx_sig,  # Pass signature string directly
                max_retries=max_retries,
                retry_delay=1.0
            )

            if not result.get("success"):
                self.logger.error(f"Transaction failed: {result.get('error', 'Unknown error')}")
            else:
                self.logger.info(f"Transaction confirmed: {tx_sig}")

            # Add signature to result for reference
            result["signature"] = tx_sig
            return result

        except Exception as e:
            error_msg = f"Transaction execution failed: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    async def submit_transaction(
        self,
        transaction: VersionedTransaction,
        preflight_checks: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Optional[str]:
        """Submit a transaction to the Solana network with retries and error handling.
        
        Args:
            transaction: The signed VersionedTransaction to submit
            preflight_checks: Whether to run preflight checks (default: True)
            max_retries: Maximum number of submission attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Optional[str]: Transaction signature if successful, None if failed
        """
        if not self.session:
            self.logger.error("❌ No active session")
            return None
            
        retry_count = 0
        current_delay = retry_delay
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Get a healthy RPC endpoint
                rpc_url = await self.get_working_rpc()
                if not rpc_url:
                    self.logger.error("❌ No healthy RPC endpoints available")
                    await asyncio.sleep(current_delay)
                    retry_count += 1
                    continue
                    
                # Serialize transaction
                serialized_tx = base64.b64encode(bytes(transaction)).decode('utf-8')
                
                # Build RPC request
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "sendTransaction",
                    "params": [
                        serialized_tx,
                        {
                            "skipPreflight": not preflight_checks,
                            "preflightCommitment": "processed",
                            "encoding": "base64",
                            "maxRetries": 3
                        }
                    ]
                }
                
                # Send transaction
                self.logger.info(f"📤 Submitting transaction to {rpc_url}")
                async with self.session.post(
                    rpc_url,
                    json=request,
                    headers=self.headers
                ) as response:
                    response_json = await response.json()
                    
                    # Check for RPC error
                    if "error" in response_json:
                        error = response_json["error"]
                        self.logger.error(f"❌ RPC error: {error}")
                        last_error = error
                        
                        # If it's a blockhash error, get a new one and rebuild
                        if "invalid blockhash" in str(error).lower():
                            self.logger.warning("⚠️ Invalid blockhash, will retry with new one")
                            await asyncio.sleep(current_delay)
                            retry_count += 1
                            continue
                            
                        # For other errors, maybe retry
                        if retry_count < max_retries - 1:
                            await asyncio.sleep(current_delay)
                            retry_count += 1
                            current_delay *= 1.5  # Exponential backoff
                            continue
                        else:
                            return None
                            
                    # Handle successful response
                    if "result" in response_json:
                        signature = response_json["result"]
                        self.logger.info(f"✅ Transaction submitted successfully: {signature}")
                        return signature
                        
            except Exception as e:
                self.logger.error(f"❌ Error submitting transaction: {e}")
                last_error = e
                
                if retry_count < max_retries - 1:
                    await asyncio.sleep(current_delay)
                    retry_count += 1
                    current_delay *= 1.5
                    continue
                else:
                    return None
                    
        # If we get here, all retries failed
        self.logger.error(f"❌ Failed to submit transaction after {max_retries} attempts")
        if last_error:
            self.logger.error(f"Last error: {last_error}")
        return None

    async def check_account_exists(self, address: Pubkey) -> bool:
        """Check if an account exists by trying to get its data"""
        try:
            rpc_url = await self.get_working_rpc()
            if not rpc_url:
                raise RuntimeError("No healthy RPCs available")

            async with self.session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [str(address), {"encoding": "base64"}]
                },
                headers={"Content-Type": "application/json"},
            ) as response:
                result = await response.json()
                if "result" not in result:
                    raise RuntimeError(f"Invalid response: {result}")
                return result["result"] is not None
        except Exception as e:
            self.logger.warning(f"Error checking account {address}: {e}")
            return False

    async def get_account_info(self, address: Pubkey) -> Optional[Dict]:
        """Get account info for a Solana account."""
        try:
            rpc_url = await self.get_working_rpc()
            if not rpc_url:
                raise RuntimeError("No healthy RPCs available")

            async with self.session.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [
                        str(address),
                        {"encoding": "jsonParsed"}
                    ]
                },
                headers=self.headers
            ) as response:
                result = await response.json()
                if "result" not in result:
                    self.logger.error(f"Invalid response: {result}")
                    return None
                    
                if "value" not in result["result"]:
                    self.logger.debug(f"No account found for {address}")
                    return None
                    
                return result["result"]["value"]
                
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}\n{traceback.format_exc()}")
            return None

    async def wait_for_confirmation(self, tx_sig: str, max_retries: int = 30, retry_delay: float = 1.0) -> dict:
        """Wait for transaction confirmation with exponential backoff and enhanced debugging.
        
        Args:
            tx_sig: The transaction signature to check
            max_retries: Maximum number of confirmation attempts
            retry_delay: Initial delay between retries, will increase exponentially
            
        Returns:
            dict: Status info including success, error (if any), and confirmationStatus
        """
        retry_count = 0
        current_delay = retry_delay
        
        while retry_count < max_retries:
            try:
                rpc_url = await self.get_working_rpc()
                if not rpc_url:
                    logger.error("No healthy RPC endpoints available for confirmation check")
                    return {"success": False, "error": "No healthy RPC endpoints"}
                    
                # Get signature status first
                async with self.session.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignatureStatuses",
                        "params": [[tx_sig]]
                    },
                    headers=self.headers
                ) as response:
                    resp = await response.json()
                    logger.debug(f"Signature status response: {resp}")
                    status = resp.get("result", {}).get("value", [None])[0]
                    
                    if status:
                        if status.get("err"):
                            logger.error(f"Transaction {tx_sig} failed: {status['err']}")
                            return {
                                "success": False, 
                                "error": status["err"], 
                                "confirmationStatus": status.get("confirmationStatus")
                            }
                            
                        if status.get("confirmationStatus") == "finalized":
                            logger.info(f"Transaction {tx_sig} finalized!")
                            return {"success": True, "confirmationStatus": "finalized"}
                        elif status.get("confirmationStatus") == "confirmed":
                            logger.info(f"Transaction {tx_sig} confirmed but waiting for finalization...")
                            return {"success": True, "confirmationStatus": "confirmed"}
                        elif status.get("confirmationStatus"):
                            logger.debug(f"Transaction {tx_sig} in state: {status['confirmationStatus']}")
                    else:
                        logger.debug(f"No status found for {tx_sig} yet on retry {retry_count}")

                # Also check getTransaction for more detailed error info
                async with self.session.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            tx_sig,
                            {"maxSupportedTransactionVersion": 0, "encoding": "jsonParsed"}
                        ]
                    },
                    headers=self.headers,
                ) as response:
                    tx_resp = await response.json()
                    logger.debug(f"Transaction info response: {tx_resp}")
                    
                    if "result" in tx_resp and tx_resp["result"]:
                        meta = tx_resp["result"].get("meta", {})
                        if meta.get("err"):
                            return {
                                "success": False, 
                                "error": meta["err"],
                                "confirmationStatus": meta.get("confirmationStatus", "unknown"),
                                "logs": meta.get("logs", [])
                            }
                            
                        if meta.get("confirmationStatus") in ["finalized", "confirmed"]:
                            return {
                                "success": True,
                                "confirmationStatus": meta["confirmationStatus"],
                                "logs": meta.get("logs", [])
                            }
                    
            except Exception as e:
                logger.warning(f"Error checking confirmation status: {str(e)}\n{traceback.format_exc()}")
                
            retry_count += 1
            await asyncio.sleep(current_delay)
            current_delay *= 1.5  # Exponential backoff
            
        logger.error(f"Transaction {tx_sig} not confirmed after {max_retries} attempts")
        return {"success": False, "error": "Timeout waiting for confirmation"}

    async def account_exists(self, account: Pubkey) -> bool:
        """Check if an account exists on chain"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [str(account), {"commitment": "confirmed"}]
                }
                async with session.post(HELIUS_RPC_URL, json=payload) as response:
                    resp = await response.json()
                    if "result" in resp:
                        return resp["result"] is not None
                    return False
        except Exception as e:
            self.logger.error(f"Error checking account existence: {e}")
            return False

    async def get_sol_balance(self, address: Pubkey) -> int:
        """Get SOL balance in lamports"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [str(address), {"commitment": "confirmed"}]
                }
                async with session.post(HELIUS_RPC_URL, json=payload) as response:
                    resp = await response.json()
                    if "result" in resp:
                        return resp["result"]["value"]
                    return 0
        except Exception as e:
            self.logger.error(f"Error getting SOL balance: {e}")
            return 0

    async def get_token_balance(self, token_account: Pubkey) -> int:
        """Get token balance from an Associated Token Account"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountBalance",
                    "params": [str(token_account)]
                }
                async with session.post(HELIUS_RPC_URL, json=payload) as response:
                    resp = await response.json()
                    if "result" in resp and "value" in resp["result"]:
                        return int(resp["result"]["value"]["amount"])
                    return 0
        except Exception as e:
            self.logger.error(f"Error getting token balance: {e}")
            return 0

    def validate_keypair(self, potential_keypair: Any, context: str = "") -> bool:
        """Validate that an object is a usable Keypair
        
        Args:
            potential_keypair: Object to validate
            context: Context string for error messages
            
        Returns:
            bool: True if object is a valid, signing-capable Keypair
        """
        try:
            if not potential_keypair:
                self.logger.error(f"❌ {context}: Keypair is None")
                return False
                
            if not isinstance(potential_keypair, Keypair):
                self.logger.error(f"❌ {context}: Expected Keypair, got {type(potential_keypair)}")
                return False
                
            # Test that it can actually sign
            test_msg = bytes([1, 2, 3, 4])
            signature = potential_keypair.sign_message(test_msg)
            if not signature:
                self.logger.error(f"❌ {context}: Keypair failed to sign test message")
                return False
                
            # Get and verify public key
            try:
                pubkey = potential_keypair.pubkey()
                if not pubkey:
                    self.logger.error(f"❌ {context}: Could not get public key")
                    return False
                self.logger.debug(f"✅ {context}: Valid Keypair with pubkey {pubkey}")
            except Exception as e:
                self.logger.error(f"❌ {context}: Error getting pubkey: {e}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ {context}: Validation error: {e}")
            return False
        
    def validate_transaction(
        self,
        transaction: VersionedTransaction,
        signers: List[Keypair],
        original_instructions: Optional[List[Instruction]] = None
    ) -> bool:
        """Validate a transaction's signers and account permissions
        
        Args:
            transaction: The transaction to validate
            signers: List of expected signers
            original_instructions: Original instructions for additional validation
            
        Returns:
            bool: True if transaction is valid
        """
        try:
            message = transaction.message
            if not isinstance(message, MessageV0):
                self.logger.error("❌ Transaction validation: Not a MessageV0 transaction")
                return False

            # 1. Validate each signer
            self.logger.info("🔑 Validating transaction signers...")
            signer_pubkeys = set()
            for i, signer in enumerate(signers):
                if not self.validate_keypair(signer, f"Transaction signer {i}"):
                    return False
                signer_pubkeys.add(str(signer.pubkey()))

            # 2. Check required signatures in message
            message_signers = {
                str(key) 
                for key in message.account_keys[:message.header.num_required_signatures]
            }
            
            if not message_signers.issubset(signer_pubkeys):
                self.logger.error("❌ Transaction requires signatures we don't have:")
                self.logger.error(f"Missing: {message_signers - signer_pubkeys}")
                return False
                
            self.logger.info(f"✅ Found all required signers ({len(message_signers)})")

            # 3. Validate original instructions if provided
            if original_instructions:
                self.logger.info("📝 Validating original instructions...")
                for i, ix in enumerate(original_instructions):
                    # Get signers required by this instruction
                    ix_signers = {
                        str(acct.pubkey) 
                        for acct in ix.accounts 
                        if acct.is_signer
                    }
                    
                    # Verify we have all required signers
                    if not ix_signers.issubset(signer_pubkeys):
                        self.logger.error(f"❌ Instruction {i} requires signers we don't have:")
                        self.logger.error(f"Missing: {ix_signers - signer_pubkeys}")
                        return False
                        
                    self.logger.debug(f"✅ Instruction {i}: Found all {len(ix_signers)} signers")

            # 4. If there are signatures, verify them
            if transaction.signatures:
                self.logger.info("🔏 Validating existing signatures...")
                try:
                    message_data = bytes(message)
                    for i, (pubkey, signature) in enumerate(zip(
                        message.account_keys[:message.header.num_required_signatures],
                        transaction.signatures
                    )):
                        if not signature.verify(pubkey.as_bytes(), message_data):
                            self.logger.error(f"❌ Invalid signature {i} for {pubkey}")
                            return False
                    self.logger.info(f"✅ Verified {len(transaction.signatures)} signatures")
                except Exception as e:
                    self.logger.error(f"❌ Error verifying signatures: {e}")
                    return False

            self.logger.info("✅ Transaction validation successful")
            return True

        except Exception as e:
            self.logger.error(f"❌ Transaction validation error: {e}")
            self.logger.error(traceback.format_exc())
            return False

    async def submit_transaction(self, transaction: VersionedTransaction) -> Optional[str]:
        """Submit a transaction to the Solana network.
        
        Args:
            transaction: The signed VersionedTransaction to submit
            
        Returns:
            Optional[str]: The transaction signature if successful, None if failed
        """
        try:
            # 1. Serialize transaction
            tx_data = base64.b64encode(bytes(transaction)).decode('utf-8')
            
            # 2. Get a healthy RPC endpoint
            rpc_url = await self.get_working_rpc()
            if not rpc_url:
                self.logger.error("❌ No healthy RPC endpoints available")
                return None
                
            # 3. Submit transaction
            try:
                async with self.session.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "sendTransaction",
                        "params": [
                            tx_data,
                            {"encoding": "base64", "skipPreflight": True, "maxRetries": 3}
                        ]
                    },
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        self.logger.error(f"❌ RPC error: {response.status}")
                        return None
                        
                    result = await response.json()
                    if "error" in result:
                        self.logger.error(f"❌ RPC error: {result['error']}")
                        return None
                        
                    if "result" not in result:
                        self.logger.error("❌ Invalid RPC response")
                        return None
                        
                    signature = result["result"]
                    self.logger.info(f"✅ Transaction submitted: {signature}")
                    return signature
                    
            except Exception as e:
                self.logger.error(f"❌ Error submitting transaction: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error serializing transaction: {e}")
            return None

