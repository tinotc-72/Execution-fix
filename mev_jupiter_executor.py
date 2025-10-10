# jupiter_trade_executor.py - Official Solana Documentation Best Practices

import base64
import logging
import requests
import asyncio

from typing import Optional, Tuple, Dict, Any, List
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction, AccountMeta
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solana.rpc.types import TxOpts
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.compute_budget import ID as COMPUTE_BUDGET_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address, create_associated_token_account

from env_keys import EnvKeys

# Import JitoClient for MEV protection
try:
    from jito_service import JitoClient
    JITO_AVAILABLE = True
except ImportError:
    JITO_AVAILABLE = False

# Standardized result helpers
def exec_ok(executor_name: str, signature: str, data: dict = None) -> dict:
    """Create standardized success result"""
    result = {"success": True, "executor": executor_name, "signature": signature}
    if data:
        result.update(data)
    return result

def exec_err(executor_name: str, error_message: str) -> dict:
    """Create standardized error result"""
    return {"success": False, "executor": executor_name, "error": error_message}

def jito_is_configured(jito_service) -> bool:
    """Check if Jito is properly configured and available"""
    return JITO_AVAILABLE and jito_service is not None

JitoClient = None

# Load Jupiter credentials from environment
env_keys = EnvKeys()
JUPITER_QUOTE_URL = env_keys.JUPITER_QUOTE_URL
JUPITER_SWAP_URL = env_keys.JUPITER_SWAP_URL
JUPITER_API_KEY = env_keys.JUPITER_API_KEY
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")

# Jupiter Program and Accounts
JUPITER_PROGRAM = Pubkey.from_string("JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4")

logger = logging.getLogger(__name__)
RPC_URL = EnvKeys().HELIUS_RPC_URL


def get_best_route(input_mint: str, output_mint: str, amount: int, slippage_bps: int = 300) -> Optional[dict]:
    """Get best route with official error handling"""
    try:
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": str(slippage_bps),
            "onlyDirectRoutes": "false",
            "restrictIntermediateTokens": "false",
            "maxAccounts": "64",
        }
        
        # Add API key to headers if available
        headers = {}
        if JUPITER_API_KEY:
            headers['Authorization'] = f'Bearer {JUPITER_API_KEY}'
            headers['x-api-key'] = JUPITER_API_KEY
        
        response = requests.get(JUPITER_QUOTE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()  # Official: Raise for HTTP errors
        
        data = response.json()
        if 'error' in data:
            logger.error(f"❌ Jupiter quote error: {data['error']}")
            return exec_err("jupiter", f"quote error: {data['error']}")
            
        return data
        
    except requests.exceptions.Timeout:
        logger.warning(f"⏰ Jupiter quote timeout")
        return exec_err("jupiter", "quote timeout")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Jupiter quote request error: {e}")
        return exec_err("jupiter", f"quote request error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Jupiter quote unexpected error: {e}")
        return exec_err("jupiter", f"quote unexpected error: {str(e)}")

def get_swap_transaction(route: dict, user_pubkey: Pubkey) -> Optional[str]:
    """Get swap transaction with official error handling"""
    try:
        payload = {
            "quoteResponse": route,
            "userPublicKey": str(user_pubkey),
            "wrapAndUnwrapSol": True,
            "dynamicComputeUnitLimit": True,  # Official: Let Jupiter optimize compute
            "prioritizationFeeLamports": "auto"  # Official: Auto priority fees
        }
        
        # Add API key to headers if available
        headers = {'Content-Type': 'application/json'}
        if JUPITER_API_KEY:
            headers['Authorization'] = f'Bearer {JUPITER_API_KEY}'
            headers['x-api-key'] = JUPITER_API_KEY
        
        response = requests.post(JUPITER_SWAP_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()  # Official: Raise for HTTP errors
        
        data = response.json()
        if 'error' in data:
            logger.error(f"❌ Jupiter swap error: {data['error']}")
            return exec_err("jupiter", f"swap error: {data['error']}")
            
        return data.get("swapTransaction")
        
    except requests.exceptions.Timeout:
        logger.warning(f"⏰ Jupiter swap timeout")
        return exec_err("jupiter", "swap timeout")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Jupiter swap request error: {e}")
        return exec_err("jupiter", f"swap request error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Jupiter swap unexpected error: {e}")
        return exec_err("jupiter", f"swap unexpected error: {str(e)}")
    res.raise_for_status()
    route = res.json()
    if "inAmount" not in route or "outAmount" not in route:
        raise Exception(f"Invalid Jupiter quote response: {route}")
    return route


def get_swap_transaction(route: dict, wallet_pubkey: Pubkey) -> Optional[str]:
    """Get swap transaction with better error handling"""
    try:
        body = {
            "quoteResponse": route,
            "userPublicKey": str(wallet_pubkey),
            "wrapAndUnwrapSol": True,
            "useSharedAccounts": True,
            "asLegacyTransaction": False,
            "dynamicComputeUnitLimit": True,  # Auto-adjust compute units
            "prioritizationFeeLamports": 100000,  # 0.0001 SOL priority fee for speed
        }
        
        # Add API key to headers if available
        headers = {'Content-Type': 'application/json'}
        if JUPITER_API_KEY:
            headers['Authorization'] = f'Bearer {JUPITER_API_KEY}'
            headers['x-api-key'] = JUPITER_API_KEY
        
        res = requests.post(JUPITER_SWAP_URL, json=body, headers=headers, timeout=15)
        res.raise_for_status()
        tx_data = res.json()

        if "swapTransaction" in tx_data:
            return tx_data["swapTransaction"]
        elif "transaction" in tx_data:
            return tx_data["transaction"]
        elif "data" in tx_data:
            return tx_data["data"]
        else:
            logger.error(f"Invalid Jupiter swap response format: {list(tx_data.keys())}")
            return exec_err("jupiter", "invalid swap response format")
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"Jupiter API HTTP error: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response content: {e.response.text}")
        return exec_err("jupiter", f"API HTTP error: {str(e)}")
    except Exception as e:
        logger.error(f"Jupiter swap transaction error: {e}")
        return exec_err("jupiter", f"swap transaction error: {str(e)}")


def build_buy_tx(token_mint: str, amount_sol: float, wallet: Keypair, slippage: float = 3.0) -> VersionedTransaction:
    lamports = int(amount_sol * 1_000_000_000)
    route = get_best_route(SOL_MINT, token_mint, lamports, slippage_bps=int(slippage * 100))
    swap_tx_b64 = get_swap_transaction(route, wallet.pubkey())
    return VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))


def build_sell_tx(token_mint: str, wallet: Keypair, slippage: float = 3.0) -> VersionedTransaction:
    ata = get_associated_token_address(wallet.pubkey(), Pubkey.from_string(token_mint))
    
    # You must fetch token balance to determine sell amount
    res = requests.post(RPC_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountBalance",
        "params": [str(ata)],
    })
    balance_data = res.json()
    try:
        amount = int(balance_data["result"]["value"]["amount"])
    except Exception:
        raise Exception("Failed to fetch token balance for sell transaction")
    
    route = get_best_route(token_mint, SOL_MINT, amount, slippage_bps=int(slippage * 100))
    swap_tx_b64 = get_swap_transaction(route, wallet.pubkey())
    return VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))


class MEVJupiterExecutor:
    """
    Jupiter aggregator executor implementing official Solana best practices
    Standalone executor for consistent transaction handling
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config=None, jito_service=None):
        # Initialize executor with official patterns
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.client = AsyncClient(rpc_url)
        self.config = config or {}
        self.jito_service = jito_service  # Add JitoClient support
        
        # Set configuration defaults
        self.config.setdefault('min_sol_amount', 0.001)
        self.config.setdefault('default_slippage', 0.01)
        self.config.setdefault('max_slippage', 0.1)
        
        logger.info(f"✅ Jupiter executor initialized with official Solana best practices")
        if jito_service:
            logger.info(f"🚀 Jupiter executor configured with Jito MEV protection")
    
    async def validate_sol_balance(self, amount_sol: float) -> bool:
        """Validate sufficient SOL balance"""
        try:
            balance_resp = await self.client.get_balance(self.wallet_pubkey)
            balance_sol = balance_resp.value / 1e9
            return balance_sol >= amount_sol + 0.01  # Account for transaction fees
        except Exception as e:
            logger.error(f"Failed to check SOL balance: {e}")
            return False
    
    async def execute_buy(self, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """
        Execute buy trade using official Solana best practices
        Implements the base class abstract method
        """
        try:
            logger.info(f"🚀 OFFICIAL Jupiter BUY: {amount_sol} SOL → {token_mint[:8]}...")
            
            # Official: Validate inputs
            if amount_sol < self.config.get('min_sol_amount', 0.001):
                return {
                    'success': False,
                    'error': f'Amount too small: {amount_sol} SOL (min: {self.config.get("min_sol_amount", 0.001)})',
                    'signature': None
                }
            
            # Official: Validate SOL balance
            if not await self.validate_sol_balance(amount_sol):
                return {
                    'success': False,
                    'error': 'Insufficient SOL balance',
                    'signature': None
                }
            
            # Ensure token account exists
            try:
                token_mint_pubkey = Pubkey.from_string(token_mint)
                await self.ensure_token_account(token_mint_pubkey)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Token account setup failed: {e}',
                    'signature': None
                }
            
            # Try progressive slippage levels per official patterns
            slippage_levels = [
                kwargs.get('slippage_tolerance', self.config.get('default_slippage', 0.01)) * 10000,  # Convert to BPS
                self.config.get('max_slippage', 0.1) * 10000  # Max slippage as fallback
            ]
            
            for slippage_bps in slippage_levels:
                try:
                    logger.info(f"   📊 Trying Jupiter with {slippage_bps/100}% slippage...")
                    
                    # Get Jupiter route
                    lamports = int(amount_sol * 1e9)
                    route = get_best_route(str(SOL_MINT), token_mint, lamports, int(slippage_bps))
                    
                    if not route:
                        logger.warning(f"   ❌ No Jupiter route for {slippage_bps/100}% slippage")
                        continue
                    
                    # Get swap transaction
                    swap_tx_b64 = get_swap_transaction(route, self.wallet_pubkey)
                    if not swap_tx_b64:
                        logger.warning(f"   ❌ No Jupiter swap transaction")
                        continue
                    
                    # Decode and execute transaction
                    try:
                        transaction = VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))
                        
                        # Re-sign with our wallet (Jupiter returns unsigned tx)
                        transaction.sign([self.wallet_keypair])
                        
                        # Execute using official retry logic
                        signature = await self.send_transaction_with_retry(transaction)
                        
                        if signature:
                            return {
                                'success': True,
                                'signature': signature,
                                'error': None,
                                'dex': 'Jupiter',
                                'slippage_used': slippage_bps / 10000
                            }
                            
                    except Exception as tx_error:
                        logger.warning(f"   ❌ Transaction execution error: {tx_error}")
                        continue
                        
                except Exception as route_error:
                    logger.warning(f"   ❌ Route error at {slippage_bps/100}%: {route_error}")
                    continue
            
            return {
                'success': False,
                'error': 'All Jupiter slippage levels failed',
                'signature': None
            }
            
        except Exception as e:
            logger.error(f"❌ Jupiter buy error: {e}")
            return {
                'success': False,
                'error': str(e),
                'signature': None
            }
    
    async def execute_sell(self, token_mint: str, **kwargs) -> Dict[str, Any]:
        """
        Execute sell trade using official Solana best practices
        Implements the base class abstract method
        """
        try:
            logger.info(f"💸 OFFICIAL Jupiter SELL: {token_mint[:8]}...")
            
            # Get token balance
            try:
                token_mint_pubkey = Pubkey.from_string(token_mint)
                token_balance = await self.get_token_balance(token_mint_pubkey)
                
                if token_balance <= 0:
                    return {
                        'success': False,
                        'error': f'No tokens to sell: {token_balance}',
                        'signature': None
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Token balance check failed: {e}',
                    'signature': None
                }
            
            # Try progressive slippage levels
            slippage_levels = [
                kwargs.get('slippage_tolerance', self.config.default_slippage) * 10000,
                self.config.max_slippage * 10000
            ]
            
            for slippage_bps in slippage_levels:
                try:
                    logger.info(f"   📊 Trying Jupiter sell with {slippage_bps/100}% slippage...")
                    
                    # Get Jupiter route for sell
                    route = get_best_route(token_mint, str(SOL_MINT), token_balance, int(slippage_bps))
                    
                    if not route:
                        logger.warning(f"   ❌ No Jupiter sell route for {slippage_bps/100}% slippage")
                        continue
                    
                    # Get swap transaction
                    swap_tx_b64 = get_swap_transaction(route, self.wallet_pubkey)
                    if not swap_tx_b64:
                        logger.warning(f"   ❌ No Jupiter sell swap transaction")
                        continue
                    
                    # Execute transaction
                    try:
                        transaction = VersionedTransaction.from_bytes(base64.b64decode(swap_tx_b64))
                        transaction.sign([self.wallet_keypair])
                        
                        # Dual-path execution: Jito first, RPC fallback
                        signature = None
                        path_used = "rpc"
                        
                        if jito_is_configured(self.jito_service):
                            try:
                                logger.info("🚀 Using Jito for Jupiter sell MEV protection...")
                                signed_tx_bytes = bytes(transaction)
                                result = await self.jito_service.send_transaction(signed_tx_bytes)
                                signature = result.get("signature")
                                if signature:
                                    path_used = "jito"
                                    logger.info(f"✅ EXECUTED via jupiter (jito) — signature: {signature}")
                                    return exec_ok("jupiter", signature, {
                                        'dex': 'Jupiter',
                                        'slippage_used': slippage_bps / 10000,
                                        'path': 'jito'
                                    })
                                else:
                                    logger.warning(f"⏭️ Skipped jupiter (jito): {result}")
                            except Exception as jito_error:
                                logger.warning(f"⏭️ Skipped jupiter (jito): {jito_error}")
                        
                        # RPC fallback (must exist)
                        if not signature:
                            opts = TxOpts(
                                skip_preflight=True,
                                preflight_commitment=Processed,
                                max_retries=1
                            )
                            sig_result = await self.client.send_transaction(transaction, opts=opts)
                            signature = str(sig_result.value) if sig_result.value else None
                        
                        if signature:
                            logger.info(f"✅ EXECUTED via jupiter (rpc) — signature: {signature}")
                            return exec_ok("jupiter", signature, {
                                'dex': 'Jupiter',
                                'slippage_used': slippage_bps / 10000,
                                'path': 'rpc'
                            })
                            
                    except Exception as tx_error:
                        logger.warning(f"   ❌ Sell transaction error: {tx_error}")
                        continue
                        
                except Exception as route_error:
                    logger.warning(f"   ❌ Sell route error: {route_error}")
                    continue
            
            return exec_err("jupiter", "All Jupiter sell attempts failed")
            
        except Exception as e:
            logger.error(f"❌ Jupiter sell error: {e}")
            return exec_err("jupiter", str(e))
        
    async def ensure_token_account(self, token_mint: Pubkey) -> Optional[Pubkey]:
        """Ensure ATA exists for token mint"""
        try:
            ata = get_associated_token_address(self.wallet_pubkey, token_mint)
            
            # Check if ATA exists
            info = await self.client.get_account_info(ata)
            if info.value is not None:
                return ata
                
            # Create ATA instruction
            create_ata_ix = create_associated_token_account(
                payer=self.wallet_pubkey,
                owner=self.wallet_pubkey,
                mint=token_mint
            )
            
            # Get recent blockhash
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
            
            # Create and send transaction
            message = MessageV0.try_compile(
                payer=self.wallet_pubkey,
                instructions=[create_ata_ix],
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            tx = VersionedTransaction(message, [self.wallet_keypair])
            
            # Send and confirm
            sig = await self.client.send_transaction(tx)
            if sig.value:
                # Wait for confirmation
                await asyncio.sleep(1)
                return ata
                
            return exec_err("jupiter", "ATA creation transaction failed")
            
        except Exception as e:
            logger.error(f"Error ensuring token account: {e}")
            return exec_err("jupiter", f"ATA creation failed: {str(e)}")

    async def execute_buy_trade(self, token_mint: Pubkey, sol_amount: float) -> Optional[str]:
        """Execute a buy trade through Jupiter with AGGRESSIVE settings"""
        try:
            logger.info(f"🚀 AGGRESSIVE Jupiter BUY: {sol_amount} SOL → {str(token_mint)}")

            # Get Jupiter swap transaction with HIGH slippage tolerance
            lamports = int(sol_amount * 1e9)
            
            # AGGRESSIVE: Try multiple slippage levels
            slippage_levels = [500, 800, 1200, 2000]  # 5%, 8%, 12%, 20%
            
            for slippage_bps in slippage_levels:
                try:
                    logger.info(f"   📊 Trying slippage: {slippage_bps/100}%")
                    
                    route = get_best_route(str(SOL_MINT), str(token_mint), lamports, slippage_bps)
                    if not route:
                        logger.warning(f"   ❌ No route found for slippage {slippage_bps/100}%")
                        continue
                    
                    logger.info(f"   📊 Quote: {route['inAmount']} → {route['outAmount']}")
                    
                    # Get swap transaction
                    swap_tx_b64 = get_swap_transaction(route, self.wallet_pubkey)
                    if not swap_tx_b64:
                        logger.warning(f"   ❌ No swap transaction for slippage {slippage_bps/100}%")
                        continue
                    
                    # CRITICAL FIX: Properly construct and sign VersionedTransaction
                    tx_bytes = base64.b64decode(swap_tx_b64)
                    tx = VersionedTransaction.from_bytes(tx_bytes)
                    
                    # CRITICAL: Sign the transaction properly
                    tx.sign([self.wallet_keypair])
                    logger.info(f"   ✅ Transaction signed successfully")

                    # Simulate first with current slippage
                    logger.info(f"   🧪 Simulating transaction...")
                    sim_result = await self.client.simulate_transaction(tx)
                    
                    if sim_result.value.err:
                        logger.warning(f"   ❌ Simulation failed for {slippage_bps/100}%: {sim_result.value.err}")
                        if hasattr(sim_result.value, 'logs') and sim_result.value.logs:
                            for log in sim_result.value.logs[-3:]:  # Show last 3 logs
                                logger.warning(f"     {log}")
                        continue
                    
                    logger.info(f"   ✅ Simulation successful with {slippage_bps/100}% slippage!")

                    # AGGRESSIVE: Send transaction immediately with minimal retries
                    opts = TxOpts(
                        skip_preflight=True,  # Skip preflight for speed
                        preflight_commitment=Processed,
                        max_retries=1  # Reduced retries for speed
                    )
                    
                    logger.info(f"   📡 Sending Jupiter transaction with {slippage_bps/100}% slippage...")
                    
                    # Dual-path execution: Jito first, RPC fallback
                    if jito_is_configured(self.jito_service):
                        try:
                            logger.info("🚀 Using Jito for Jupiter MEV protection...")
                            signed_tx_bytes = bytes(tx)
                            result = await self.jito_service.send_transaction(signed_tx_bytes)
                            signature = result.get("signature")
                            if signature:
                                logger.info(f"✅ EXECUTED via jupiter (jito) — signature: {signature}")
                                return exec_ok("jupiter", signature, {"lamports": lamports, "cu": 300_000, "path": "jito"})
                            else:
                                logger.warning(f"⏭️ Skipped jupiter (jito): {result}")
                        except Exception as jito_error:
                            logger.warning(f"⏭️ Skipped jupiter (jito): {jito_error}")
                    
                    # RPC fallback (must exist)
                    sig = await self.client.send_transaction(tx, opts=opts)
                    
                    if sig.value:
                        logger.info(f"✅ EXECUTED via jupiter (rpc) — signature: {str(sig.value)}")
                        return exec_ok("jupiter", str(sig.value), {"lamports": lamports, "cu": 300_000, "path": "rpc"})
                    else:
                        logger.warning(f"   ❌ No signature returned for {slippage_bps/100}%")
                        continue
                        
                except Exception as slippage_error:
                    logger.warning(f"   ❌ Error with {slippage_bps/100}% slippage: {slippage_error}")
                    continue
            
            # If all slippage levels failed
            logger.error(f"❌ All Jupiter slippage levels failed")
            return exec_err("jupiter", "all slippage levels failed")

        except Exception as e:
            logger.error(f"❌ Critical Jupiter buy error: {e}")
            return exec_err("jupiter", f"critical buy error: {str(e)}")
