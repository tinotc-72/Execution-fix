# meteora_copy_executor.py

import asyncio
import base64
import base58
import logging

# Defensive logger setup
class DummyLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    def warning(self, msg):
        print(f"[WARNING] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}")
    def debug(self, msg):
        print(f"[DEBUG] {msg}")

def get_safe_logger(logger_candidate):
    if isinstance(logger_candidate, logging.Logger):
        return logger_candidate
    if hasattr(logger_candidate, 'info') and hasattr(logger_candidate, 'warning') and hasattr(logger_candidate, 'error'):
        return logger_candidate
    return DummyLogger()

logger = get_safe_logger(globals().get('logger', None))
from typing import Optional, List, Dict, Any
import requests
import json
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.instruction import Instruction, AccountMeta
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.address_lookup_table_account import AddressLookupTableAccount
from solders.system_program import transfer, TransferParams

from config import WALLET, HELIUS_RPC_URL
from fast_executor import FastExecutor

logger = logging.getLogger(__name__)
if not (hasattr(logger, 'info') and hasattr(logger, 'warning') and hasattr(logger, 'error')) or not isinstance(logger, logging.Logger):
    class DummyLogger:
        def info(self, msg):
            print(msg)
        def warning(self, msg):
            print("[WARN]", msg)
        def error(self, msg):
            print("[ERROR]", msg)
        def debug(self, msg):
            print("[DEBUG]", msg)
    logger = DummyLogger()

class MeteoraExecutor:
    """
    Meteora DEX executor for copy trading
    
    Reverse engineered from successful Meteora transactions using program ID:
    dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN
    """
    
    def __init__(self, wallet_keypair: Keypair, fast_executor: FastExecutor = None):
        self.wallet_keypair = wallet_keypair
        self.wallet_pubkey = wallet_keypair.pubkey()
        self.rpc_url = HELIUS_RPC_URL
        self.fast_executor = fast_executor
        
        # Meteora program constants
        self.METEORA_PROGRAM = Pubkey.from_string("dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN")
        self.TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
        
        # Swap instruction discriminator (from reverse engineering)
        self.SWAP_DISCRIMINATOR = bytes.fromhex("f8c69e91e17587c8")
        
        logger.info(f"🌊 Meteora Executor initialized for wallet: {self.wallet_pubkey}")

    async def copy_buy_from_transaction(
        self,
        original_signature: str,
        target_token_mint: str,
        amount_sol: float,
        source_wallet: str = None,
        pool_info: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Copy a buy trade from a Meteora transaction
        
        Args:
            original_signature: The original transaction signature to copy
            target_token_mint: The token mint address to buy
            amount_sol: Amount of SOL to spend
            source_wallet: Source wallet that made the original trade
            pool_info: Pool information (can be extracted from original tx)
        
        Returns:
            Transaction signature if successful, None otherwise
        """
        try:
            logger.info(f"🌊 Meteora Buy: {amount_sol} SOL → {target_token_mint[:8]}...")
            logger.info(f"   📋 Original tx: {original_signature}")
            
            # Step 1: Analyze the original transaction to extract pool info
            pool_data = await self._analyze_meteora_transaction(original_signature)
            if not pool_data:
                logger.error("❌ Failed to extract pool data from original transaction")
                return None
            
            # Step 2: Get pool state and calculate swap amounts
            swap_params = await self._calculate_swap_amounts(
                pool_data, 
                target_token_mint, 
                amount_sol, 
                is_buy=True
            )
            if not swap_params:
                logger.error("❌ Failed to calculate swap parameters")
                return None
            
            # Step 3: Build the swap transaction
            transaction = await self._build_meteora_swap_transaction(
                swap_params,
                target_token_mint,
                amount_sol,
                is_buy=True
            )
            if not transaction:
                logger.error("❌ Failed to build Meteora swap transaction")
                return None
            
            # Step 4: Execute via FastExecutor
            logger.info(f"🚀 Executing Meteora buy via FastExecutor...")
            signature = await self.fast_executor.submit_transaction(transaction)
            
            if signature:
                logger.info(f"✅ Meteora buy executed: {signature}")
                return signature
            else:
                logger.error("❌ FastExecutor returned no signature")
                return None
                
        except Exception as e:
            logger.error(f"❌ Meteora buy failed: {str(e)}")
            return None

    async def _analyze_meteora_transaction(self, signature: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a Meteora transaction to extract pool and swap information with ALT support
        """
        try:
            payload = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'getTransaction',
                'params': [
                    signature,
                    {
                        'encoding': 'json',
                        'maxSupportedTransactionVersion': 0
                    }
                ]
            }
            
            response = requests.post(self.rpc_url, json=payload, timeout=10)
            data = response.json()
            
            if 'result' not in data or not data['result']:
                logger.error(f"Failed to fetch transaction: {signature}")
                return None
                
            tx = data['result']
            account_keys = tx['transaction']['message']['accountKeys']
            loaded_addresses = tx.get('meta', {}).get('loadedAddresses', {})
            
            # Find Meteora swap instruction
            meteora_instruction = None
            for instruction in tx['transaction']['message']['instructions']:
                program_index = instruction['programIdIndex']
                if program_index < len(account_keys) and account_keys[program_index] == str(self.METEORA_PROGRAM):
                    meteora_instruction = instruction
                    break
            
            if not meteora_instruction:
                logger.error("No Meteora instruction found in transaction")
                return None
            
            # Extract and resolve all accounts (including ALT)
            accounts = []
            readonly_alts = loaded_addresses.get('readonly', [])
            writable_alts = loaded_addresses.get('writable', [])
            
            logger.info(f"🔍 Account resolution:")
            logger.info(f"   📋 Static accounts: {len(account_keys)}")
            logger.info(f"   📖 Readonly ALTs: {len(readonly_alts)}")
            logger.info(f"   ✏️ Writable ALTs: {len(writable_alts)}")
            
            for i, acc_index in enumerate(meteora_instruction['accounts']):
                if acc_index < len(account_keys):
                    # Static account
                    account_addr = account_keys[acc_index]
                    accounts.append(account_addr)
                    logger.info(f"   [{i}] Static: {account_addr}")
                else:
                    # Address lookup table account
                    alt_index = acc_index - len(account_keys)
                    
                    if alt_index < len(readonly_alts):
                        account_addr = readonly_alts[alt_index]
                        accounts.append(account_addr)
                        logger.info(f"   [{i}] Readonly ALT: {account_addr}")
                    elif alt_index - len(readonly_alts) < len(writable_alts):
                        writable_index = alt_index - len(readonly_alts)
                        account_addr = writable_alts[writable_index]
                        accounts.append(account_addr)
                        logger.info(f"   [{i}] Writable ALT: {account_addr}")
                    else:
                        logger.error(f"❌ Could not resolve account index {acc_index}")
                        return None
            
            # Extract instruction data and verify discriminator
            try:
                import base58
                instruction_data = base58.b58decode(meteora_instruction['data'])
                if instruction_data[:8] == self.SWAP_DISCRIMINATOR:
                    logger.info(f"✅ Confirmed Meteora swap instruction (discriminator match)")
                else:
                    logger.warning(f"⚠️ Discriminator mismatch - might be different Meteora instruction")
            except Exception as e:
                logger.warning(f"⚠️ Could not decode instruction data: {e}")
                instruction_data = meteora_instruction['data']
            
            # Extract token changes to understand the swap
            pre_balances = tx.get('meta', {}).get('preTokenBalances', [])
            post_balances = tx.get('meta', {}).get('postTokenBalances', [])
            
            token_changes = []
            for post in post_balances:
                pre = next((p for p in pre_balances if p['accountIndex'] == post['accountIndex']), None)
                if pre:
                    pre_amount = float(pre['uiTokenAmount']['uiAmount'] or 0)
                    post_amount = float(post['uiTokenAmount']['uiAmount'] or 0)
                    change = post_amount - pre_amount
                    if abs(change) > 0.0001:  # Ignore dust changes
                        token_changes.append({
                            'mint': post['mint'],
                            'change': change,
                            'account_index': post['accountIndex'],
                            'decimals': post['uiTokenAmount']['decimals']
                        })
            
            pool_data = {
                'instruction_data': meteora_instruction['data'],
                'instruction_data_bytes': instruction_data,
                'accounts': accounts,
                'token_changes': token_changes,
                'program_id': str(self.METEORA_PROGRAM),
                'loaded_addresses': loaded_addresses
            }
            
            logger.info(f"🔍 Extracted Meteora pool data:")
            logger.info(f"   🏦 Accounts: {len(accounts)}")
            logger.info(f"   💱 Token changes: {len(token_changes)}")
            
            for change in token_changes:
                direction = "+" if change['change'] > 0 else ""
                logger.info(f"     {direction}{change['change']:,.4f} {change['mint'][:8]}...")
            
            return pool_data
            
        except Exception as e:
            logger.error(f"❌ Error analyzing Meteora transaction: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _calculate_swap_amounts(
        self,
        pool_data: Dict[str, Any],
        target_token: str,
        amount: float,
        is_buy: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate swap amounts and parameters for Meteora pool (buy or sell)
        """
        try:
            if is_buy:
                # BUY: amount is in SOL
                amount_lamports = int(amount * 1_000_000_000)  # Convert SOL to lamports
                logger.info(f"💰 Buy params: {amount} SOL ({amount_lamports} lamports)")
            else:
                # SELL: amount is in tokens
                # For selling, we need to determine token decimals and convert properly
                # For now, assume standard token amount (will need token metadata for precision)
                token_changes = pool_data.get('token_changes', [])
                
                # Find the token being sold in the original transaction
                token_decimals = 6  # Default, but should be fetched from token metadata
                for change in token_changes:
                    if change['mint'] == target_token:
                        token_decimals = change.get('decimals', 6)
                        break
                
                # Convert token amount to smallest unit
                amount_lamports = int(amount * (10 ** token_decimals))
                logger.info(f"💰 Sell params: {amount} tokens ({amount_lamports} smallest units, {token_decimals} decimals)")
            
            # Minimum amount out (with high slippage tolerance for copy trading)
            minimum_amount_out = 0  # Accept any amount (high slippage tolerance)
            
            swap_params = {
                'amount_in': amount_lamports,
                'minimum_amount_out': minimum_amount_out,
                'pool_accounts': pool_data['accounts'],
                'instruction_data_template': pool_data['instruction_data'],
                'is_buy': is_buy,
                'token_decimals': token_decimals if not is_buy else 9  # SOL has 9 decimals
            }
            
            return swap_params
            
        except Exception as e:
            logger.error(f"Error calculating swap amounts: {e}")
            return None

    async def _build_meteora_swap_transaction(
        self,
        swap_params: Dict[str, Any],
        target_token: str,
        amount: float,
        is_buy: bool
    ) -> Optional[VersionedTransaction]:
        """
        Build a Meteora swap transaction using reverse-engineered instruction pattern
        """
        try:
            action = "buy" if is_buy else "sell"
            logger.info(f"🔨 Building Meteora {action} transaction...")
            
            # Get recent blockhash
            blockhash_response = requests.post(
                self.rpc_url,
                json={
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'getLatestBlockhash'
                },
                timeout=10
            )
            
            blockhash_data = blockhash_response.json()
            if 'result' not in blockhash_data:
                logger.error("Failed to get recent blockhash")
                return None
                
            recent_blockhash = blockhash_data['result']['value']['blockhash']
            
            # Build account metas based on reverse-engineered pattern
            account_metas = []
            pool_accounts = swap_params['pool_accounts']
            
            for i, account_str in enumerate(pool_accounts):
                if account_str is None:
                    logger.error(f"❌ Unresolved account at index {i}")
                    return None
                
                # Replace the source wallet with our wallet (index 9 from analysis)
                if i == 9 or account_str == "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK":
                    account_pubkey = self.wallet_pubkey
                    is_signer = True
                    is_writable = True
                    logger.info(f"🔄 Wallet substitution at index {i}: {account_str[:8]}... → {str(self.wallet_pubkey)[:8]}...")
                else:
                    account_pubkey = Pubkey.from_string(account_str)
                    is_signer = False
                    # Most Meteora accounts need to be writable for pool operations
                    is_writable = True
                
                account_metas.append(AccountMeta(
                    pubkey=account_pubkey,
                    is_signer=is_signer,
                    is_writable=is_writable
                ))
            
            # Build instruction data - start with discriminator + swap parameters
            instruction_data = bytearray(self.SWAP_DISCRIMINATOR)
            
            # Add amount parameters (reverse-engineered from transaction analysis)
            amount_in = swap_params['amount_in']
            minimum_out = swap_params['minimum_amount_out']
            
            # Encode amounts as little-endian 64-bit integers
            instruction_data.extend(amount_in.to_bytes(8, 'little'))
            instruction_data.extend(minimum_out.to_bytes(8, 'little'))
            
            # Create the Meteora swap instruction
            meteora_swap_ix = Instruction(
                program_id=self.METEORA_PROGRAM,
                accounts=account_metas,
                data=bytes(instruction_data)
            )
            
            # Create compute budget instructions for better execution
            compute_limit_ix = set_compute_unit_limit(400_000)  # Higher limit for Meteora
            compute_price_ix = set_compute_unit_price(2_000_000)  # 2000 micro-lamports for priority
            
            instructions = [
                compute_limit_ix,
                compute_price_ix,
                meteora_swap_ix
            ]
            
            # Create the transaction message
            try:
                message = MessageV0.try_compile(
                    payer=self.wallet_pubkey,
                    instructions=instructions,
                    address_lookup_table_accounts=[],  # Handle ALTs if needed
                    recent_blockhash=recent_blockhash
                )
            except Exception as e:
                logger.error(f"❌ Failed to compile message: {e}")
                return None
            
            # Create and sign the transaction
            transaction = VersionedTransaction(message, [self.wallet_keypair])
            
            logger.info(f"✅ Meteora {action} transaction built successfully")
            if is_buy:
                logger.info(f"   💰 Amount: {amount} SOL ({amount_in} lamports)")
            else:
                logger.info(f"   💰 Amount: {amount} tokens ({amount_in} smallest units)")
            logger.info(f"   🏦 Accounts: {len(account_metas)}")
            logger.info(f"   📦 Instruction data: {len(instruction_data)} bytes")
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error building Meteora transaction: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_meteora_pools_for_token(self, token_mint: str) -> List[Dict[str, Any]]:
        """
        Get Meteora pools that trade the specified token
        """
        try:
            # This would query Meteora's API or on-chain data to find pools
            # For now, return empty list
            logger.warning("⚠️ Meteora pool discovery not yet implemented")
            return []
            
        except Exception as e:
            logger.error(f"Error getting Meteora pools: {e}")
            return []

    async def copy_sell_from_transaction(
        self,
        original_signature: str,
        target_token_mint: str,
        amount_tokens: float,
        source_wallet: str = None,
        pool_info: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Copy a sell trade from a Meteora transaction with proportional selling support
        """
        try:
            logger.info(f"🌊 Meteora Sell: {amount_tokens:.6f} {target_token_mint[:8]}... → SOL")
            logger.info(f"   📋 Original tx: {original_signature}")
            logger.info(f"   👤 Source wallet: {source_wallet}")
            
            # Step 1: Analyze the original transaction to extract pool info
            pool_data = await self._analyze_meteora_transaction(original_signature)
            if not pool_data:
                logger.error("❌ Failed to extract pool data from original sell transaction")
                return None
            
            # Step 2: Get pool state and calculate swap amounts for sell
            swap_params = await self._calculate_swap_amounts(
                pool_data, 
                target_token_mint, 
                amount_tokens, 
                is_buy=False  # This is a sell
            )
            if not swap_params:
                logger.error("❌ Failed to calculate sell swap parameters")
                return None
            
            # Step 3: Build the sell swap transaction
            transaction = await self._build_meteora_swap_transaction(
                swap_params,
                target_token_mint,
                amount_tokens,
                is_buy=False  # This is a sell
            )
            if not transaction:
                logger.error("❌ Failed to build Meteora sell swap transaction")
                return None
            
            # Step 4: Execute via FastExecutor
            logger.info(f"🚀 Executing Meteora sell via FastExecutor...")
            signature = await self.fast_executor.submit_transaction(transaction)
            
            if signature:
                logger.info(f"✅ Meteora sell executed: {signature}")
                return signature
            else:
                logger.error("❌ FastExecutor returned no signature for sell")
                return None
                
        except Exception as e:
            logger.error(f"❌ Meteora sell failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

# Wrapper function for integration with execution_coordinator.py
async def meteora_copy_trade(
    wallet_keypair: Keypair,
    fast_executor: FastExecutor,
    source_tx_signature: str,
    source_wallet: str,
    token_mint: str,
    amount_sol: float,
    original_signature: str = "",
    detected_action: str = "buy"
) -> Optional[str]:
    """
    Wrapper function for Meteora copy trading - compatible with execution_coordinator.py
    """
    try:
        logger.info(f"🌊 METEORA COPY TRADE: {amount_sol} SOL → {token_mint[:8]}...")
        logger.info(f"🚀 ULTRA-AGGRESSIVE MODE: Target wallet approved this token!")
        logger.info(f"💎 Direct Meteora DEX - Reverse engineered execution!")
        
        executor = MeteoraExecutor(wallet_keypair, fast_executor)
        
        if detected_action.lower() == "buy":
            result = await executor.copy_buy_from_transaction(
                original_signature=source_tx_signature,
                target_token_mint=token_mint,
                amount_sol=amount_sol,
                source_wallet=source_wallet
            )
        else:
            # Handle sell transactions
            result = await executor.copy_sell_from_transaction(
                original_signature=source_tx_signature,
                target_token_mint=token_mint,
                amount_tokens=amount_sol,  # For sells, this would be token amount
                source_wallet=source_wallet
            )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Meteora wrapper error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# Helper function for quick testing
async def test_meteora_analysis():
    """Test the Meteora transaction analysis"""
    from config import WALLET
    
    executor = MeteoraExecutor(WALLET)
    
    # Test with the transaction we analyzed
    test_signature = "5EnkXbke64aiEdk43kNRZAZE8wPGHUMs9roJ6DAAK4Z3KChXWwa8DzetTXAD9Zd2z4WgwrmFfJfy8uH7Ybp6UWA8"
    
    result = await executor._analyze_meteora_transaction(test_signature)
    if result:
        print("✅ Meteora analysis successful!")
        print(f"   Accounts: {len(result['accounts'])}")
        print(f"   Token changes: {len(result['token_changes'])}")
        
        # Show account layout
        print("\n🏦 Account Layout:")
        for i, account in enumerate(result['accounts']):
            print(f"   [{i:2d}] {account}")
            
        # Show token changes
        print("\n💱 Token Changes:")
        for change in result['token_changes']:
            direction = "+" if change['change'] > 0 else ""
            print(f"   {direction}{change['change']:,.4f} {change['mint'][:8]}...")
    else:
        print("❌ Meteora analysis failed")


if __name__ == "__main__":
    asyncio.run(test_meteora_analysis())
