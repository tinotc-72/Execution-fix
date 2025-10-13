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

# Import official base executor
from base_solana_executor import BaseSolanaExecutor, SolanaExecutorConfig
from env_keys import EnvKeys

# Import JitoClient for MEV protection
try:
    from jito_service import JitoClient
    JITO_AVAILABLE = True
except ImportError:
    JITO_AVAILABLE = False
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
            return None
            
        return data
        
    except requests.exceptions.Timeout:
        logger.warning(f"⏰ Jupiter quote timeout")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Jupiter quote request error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Jupiter quote unexpected error: {e}")
        return None

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
            return None
            
        return data.get("swapTransaction")
        
    except requests.exceptions.Timeout:
        logger.warning(f"⏰ Jupiter swap timeout")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Jupiter swap request error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Jupiter swap unexpected error: {e}")
        return None
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
            return None
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"Jupiter API HTTP error: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Jupiter swap transaction error: {e}")
        return None


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


class MEVJupiterExecutor(BaseSolanaExecutor):
    """
    Jupiter aggregator executor implementing official Solana best practices
    Inherits from BaseSolanaExecutor for consistent transaction handling
    """
    
    def __init__(self, wallet_keypair: Keypair, rpc_url: str, config: SolanaExecutorConfig = None, jito_service=None):
        # Initialize base executor with official patterns
        super().__init__(wallet_keypair, rpc_url, config)
        self.jito_service = jito_service  # Add JitoClient support
        
        logger.info(f"✅ Jupiter executor initialized with official Solana best practices")
        if jito_service:
            logger.info(f"🚀 Jupiter executor configured with Jito MEV protection")
    
    async def execute_buy(self, token_mint: str, amount_sol: float, **kwargs) -> Dict[str, Any]:
        """
        Execute buy trade using official Solana best practices
        Implements the base class abstract method
        """
        try:
            logger.info(f"🚀 OFFICIAL Jupiter BUY: {amount_sol} SOL → {token_mint[:8]}...")
            
            # Official: Validate inputs
            if amount_sol < self.config.min_sol_amount:
                return {
                    'success': False,
                    'error': f'Amount too small: {amount_sol} SOL (min: {self.config.min_sol_amount})',
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
                kwargs.get('slippage_tolerance', self.config.default_slippage) * 10000,  # Convert to BPS
                self.config.max_slippage * 10000  # Max slippage as fallback
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
                        logger.warning(f"   ❌ Sell transaction error: {tx_error}")
                        continue
                        
                except Exception as route_error:
                    logger.warning(f"   ❌ Sell route error: {route_error}")
                    continue
            
            return {
                'success': False,
                'error': 'All Jupiter sell attempts failed',
                'signature': None
            }
            
        except Exception as e:
            logger.error(f"❌ Jupiter sell error: {e}")
            return {
                'success': False,
                'error': str(e),
                'signature': None
            }
        
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
                
            return None
            
        except Exception as e:
            logger.error(f"Error ensuring token account: {e}")
            return None

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
                    
                    # Try Jito first for MEV protection
                    if hasattr(self, 'jito_service') and self.jito_service:
                        try:
                            logger.info("🚀 Using Jito for Jupiter MEV protection...")
                            # Convert VersionedTransaction to bytes for Jito
                            signed_tx_bytes = bytes(tx)
                            result = await self.jito_service.send_transaction(signed_tx_bytes)
                            signature = result.get("signature")
                            if signature:
                                logger.info(f"   🎉 JITO JUPITER BUY SUCCESS: {signature}")
                                return signature
                            else:
                                logger.warning(f"   ⚠️ Jito failed, falling back to RPC: {result}")
                        except Exception as jito_error:
                            logger.warning(f"   ⚠️ Jito error, falling back to RPC: {jito_error}")
                    
                    # Fallback to standard RPC
                    sig = await self.client.send_transaction(tx, opts=opts)
                    
                    if sig.value:
                        logger.info(f"   🎉 JUPITER BUY SUCCESS: {str(sig.value)}")
                        return str(sig.value)
                    else:
                        logger.warning(f"   ❌ No signature returned for {slippage_bps/100}%")
                        continue
                        
                except Exception as slippage_error:
                    logger.warning(f"   ❌ Error with {slippage_bps/100}% slippage: {slippage_error}")
                    continue
            
            # If all slippage levels failed
            logger.error(f"❌ All Jupiter slippage levels failed")
            return None

        except Exception as e:
            logger.error(f"❌ Critical Jupiter buy error: {e}")
            return None
