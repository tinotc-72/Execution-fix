import asyncio
from utils import RPCClient, get_associated_token_address, create_associated_token_account

# Stub for Jito tip instruction (replace with actual implementation if available)
def create_jito_tip_instruction(pubkey, amount):
    # Return None or a dummy Instruction for now
    return None
class MEVDirectCopyConfig:
    @property
    def sell_priority_fee(self):
        return self.pumpfun_priority_fee
    @property
    def buy_priority_fee(self):
        return self.pumpfun_priority_fee
    def __init__(self,
                 jupiter_priority_fee=2_000_000,
                 pumpfun_priority_fee=2_000_000,
                 compute_limit=1_400_000,
                 use_jito_bundles=False,
                 jito_tip_amount=0,
                 max_copy_time_ms=500.0,
                 skip_preflight=False):
        self.jupiter_priority_fee = jupiter_priority_fee
        self.pumpfun_priority_fee = pumpfun_priority_fee
        self.compute_limit = compute_limit
        self.skip_preflight = skip_preflight
        self.use_jito_bundles = use_jito_bundles
        self.jito_tip_amount = jito_tip_amount
        self.max_copy_time_ms = max_copy_time_ms
import logging
import base58
import httpx
from typing import Optional, Dict, Any, List
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from complete_mev_bot import CompleteMEVBot, CompleteMEVConfig
from env_keys import EnvKeys
from executor_utils import exec_ok, exec_err

# Import JitoClient for MEV protection
try:
    from jito_service import JitoClient
    JITO_AVAILABLE = True
except ImportError:
    JITO_AVAILABLE = False
    JitoClient = None

import logging

logger = logging.getLogger(__name__)

def jito_is_configured(jito_service) -> bool:
    """Check if Jito is properly configured and available"""
    return jito_service is not None and hasattr(jito_service, 'send_transaction')


async def submit_cloned_tx(final_vtx, fast_executor):
    """
    Helper function to submit a cloned transaction via FastExecutor.
    Supports both Jito (if available) and RPC fallback.
    
    Args:
        final_vtx: VersionedTransaction to submit
        fast_executor: FastExecutor instance with send_and_confirm method
        
    Returns:
        Signature string on success, None on failure
    """
    try:
        if fast_executor is None:
            logger.error("[SUBMIT_CLONED_TX] ❌ FastExecutor is None")
            return None
        
        if not hasattr(fast_executor, 'send_and_confirm'):
            logger.error("[SUBMIT_CLONED_TX] ❌ FastExecutor missing send_and_confirm method")
            return None
        
        logger.info("[SUBMIT_CLONED_TX] 🚀 Submitting via FastExecutor.send_and_confirm...")
        signature = await fast_executor.send_and_confirm(final_vtx)
        
        if signature:
            logger.info(f"[SUBMIT_CLONED_TX] ✅ Submission successful: {signature}")
        else:
            logger.error("[SUBMIT_CLONED_TX] ❌ Submission failed - no signature returned")
        
        return signature
        
    except Exception as e:
        logger.error(f"[SUBMIT_CLONED_TX] ❌ Exception during submission: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


class MEVDirectCopyExecutor:
    async def _submit_mev_transaction(self, instructions):
        """Submit MEV transaction with comprehensive logging"""
        import traceback
        
        try:
            logger.info("[DIRECT_COPY] 🚀 Starting MEV transaction submission...")
            logger.debug(f"[DIRECT_COPY] Input instructions count: {len(instructions)}")
            
            # Filter out duplicate ComputeBudget instructions
            filtered = [ix for ix in instructions if str(ix.program_id) != "ComputeBudget111111111111111111111111111111"]
            logger.debug(f"[DIRECT_COPY] After filtering ComputeBudget: {len(filtered)} instructions")
            
            # Prepend only the bot's ComputeBudget instructions
            bot_limit_ix = set_compute_unit_limit(self.config.compute_limit)
            bot_price_ix = set_compute_unit_price(self.config.pumpfun_priority_fee // 1000)
            final_instructions = [bot_limit_ix, bot_price_ix] + filtered
            logger.info(f"[DIRECT_COPY] Final instruction count: {len(final_instructions)}")
            logger.debug(f"[DIRECT_COPY] Compute limit: {self.config.compute_limit}")
            logger.debug(f"[DIRECT_COPY] Priority fee: {self.config.pumpfun_priority_fee} lamports")
            
            # Dual-path execution: Jito first, RPC fallback
            if jito_is_configured(self.jito_service):
                try:
                    logger.info("[DIRECT_COPY] 🔄 Attempting Jito submission for MEV protection...")
                    logger.debug(f"[DIRECT_COPY] Building signed transaction...")
                    
                    signed_tx = await self.mev_bot._build_signed_transaction(final_instructions)
                    if signed_tx:
                        logger.debug(f"[DIRECT_COPY] Signed transaction built successfully")
                        logger.info(f"[DIRECT_COPY] Sending transaction via Jito...")
                        
                        result = await self.jito_service.send_transaction(signed_tx)
                        logger.debug(f"[DIRECT_COPY] Jito response: {result}")
                        
                        signature = result.get("signature")
                        if signature:
                            logger.info(f"[DIRECT_COPY] ✅ EXECUTED via Jito — signature: {signature}")
                            return signature
                        else:
                            logger.warning(f"[DIRECT_COPY] ⏭️ Jito submission returned no signature: {result}")
                    else:
                        logger.warning(f"[DIRECT_COPY] ⏭️ Failed to build signed transaction for Jito")
                        
                except Exception as jito_error:
                    logger.error(f"[DIRECT_COPY] ❌ Jito submission failed: {jito_error}")
                    logger.debug(traceback.format_exc())
            else:
                logger.info(f"[DIRECT_COPY] ℹ️  Jito not configured, using RPC directly")
            
            # RPC fallback (must exist)
            logger.info(f"[DIRECT_COPY] 🔄 Attempting RPC submission...")
            result_signature = await self.mev_bot._send_transaction(
                final_instructions, 
                "MEV Direct Copy", 
                skip_priority_instructions=True
            )
            
            if result_signature:
                logger.info(f"[DIRECT_COPY] ✅ EXECUTED via RPC — signature: {result_signature}")
                return result_signature
            else:
                logger.error("[DIRECT_COPY] ❌ RPC submission failed - no signature returned")
                return None
                
        except Exception as e:
            logger.error(f"[DIRECT_COPY] ❌ MEV transaction submission failed: {e}")
            logger.error(traceback.format_exc())
            return None
    def __init__(self, private_key: str, config=None, jito_service=None, env_keys=None, fast_executor=None):
        """Initialize Direct Copy Executor with comprehensive error logging"""
        import traceback
        
        logger.info(f"[DIRECT_COPY] 🚀 Initializing MEV Direct Copy Executor...")
        logger.debug(f"[DIRECT_COPY] Config type: {type(config)}")
        logger.debug(f"[DIRECT_COPY] Jito service available: {jito_service is not None}")
        logger.debug(f"[DIRECT_COPY] FastExecutor provided: {fast_executor is not None}")
        
        try:
            # Validate and set config
            if config is None:
                self.config = MEVDirectCopyConfig()
                logger.debug(f"[DIRECT_COPY] Using default MEVDirectCopyConfig")
            elif isinstance(config, MEVDirectCopyConfig):
                self.config = config
                logger.debug(f"[DIRECT_COPY] Using provided MEVDirectCopyConfig")
            else:
                error_msg = f"config must be MEVDirectCopyConfig object or None, got {type(config).__name__}"
                logger.error(f"[DIRECT_COPY] ❌ Config type error: {error_msg}")
                raise TypeError(error_msg)
            
            logger.debug(f"[DIRECT_COPY] Config attributes: {vars(self.config)}")
            logger.info(f"[DIRECT_COPY] ✅ Config validated successfully")
            
            # Validate private key type
            if not isinstance(private_key, str):
                error_msg = f"PHANTOM_PRIVATE_KEY must be string, got {type(private_key)}"
                logger.error(f"[DIRECT_COPY] ❌ Type error: {error_msg}")
                raise TypeError(error_msg)
            
            logger.debug(f"[DIRECT_COPY] Private key length: {len(private_key)} chars")
            
            # Create keypair
            logger.info(f"[DIRECT_COPY] Creating keypair from private key...")
            self.keypair = Keypair.from_base58_string(private_key)
            logger.info(f"[DIRECT_COPY] ✅ Keypair created: {self.keypair.pubkey()}")
            
            # Initialize MEV bot - needs EnvKeys object, not private_key string
            logger.info(f"[DIRECT_COPY] Initializing CompleteMEVBot...")
            # If env_keys not provided, create one
            if env_keys is None:
                from env_keys import EnvKeys
                env_keys = EnvKeys()
                logger.debug(f"[DIRECT_COPY] Created new EnvKeys instance")
            # Create CompleteMEVConfig from MEVDirectCopyConfig
            from complete_mev_bot import CompleteMEVConfig
            mev_bot_config = CompleteMEVConfig(
                priority_fee=self.config.pumpfun_priority_fee,
                compute_limit=self.config.compute_limit,
                max_slippage=0.06,  # Default from CompleteMEVConfig
                timeout=30.0,  # Default from CompleteMEVConfig
                verify_transactions=True  # Default from CompleteMEVConfig
            )
            self.mev_bot = CompleteMEVBot(env_keys, mev_bot_config)
            logger.info(f"[DIRECT_COPY] ✅ CompleteMEVBot initialized")
            
            # Set Jito service
            self.jito_service = jito_service
            if jito_service:
                logger.info(f"[DIRECT_COPY] ✅ Jito service configured for MEV protection")
            else:
                logger.info(f"[DIRECT_COPY] ℹ️  No Jito service - using RPC only")
            
            # Set FastExecutor
            self.fast_executor = fast_executor
            if fast_executor:
                logger.info(f"[DIRECT_COPY] ✅ FastExecutor configured for transaction submission")
            else:
                logger.info(f"[DIRECT_COPY] ℹ️  No FastExecutor - will use internal _submit_mev_transaction")
                
            logger.info(f"[DIRECT_COPY] 🎉 Executor initialization complete")
            
        except TypeError as te:
            logger.error(f"[DIRECT_COPY] ❌ Type error during initialization: {te}")
            logger.error(traceback.format_exc())
            raise
        except Exception as e:
            logger.error(f"[DIRECT_COPY] ❌ Unexpected error during initialization: {e}")
            logger.error(traceback.format_exc())
            raise
    async def _copy_and_modify_instructions(self, original_instructions, account_keys, original_wallet):
        """
        Detect router program for Pump.fun and rebuild router instruction with user's wallet and derived ATA.
        Only create ATA if it doesn't already exist.
        """
        from solders.pubkey import Pubkey
        from solders.instruction import AccountMeta, Instruction
        import base58
        import httpx
        ATA_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        PUMPFUN_ROUTER_PROGRAMS = [
            "F5tfvbLog9VdGUPqBDTT8rgXvTTcq7e5UiGnupL1zvBq",  # router
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # direct
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",   # AMM
            "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95"   # Real router from transaction
        ]
        copied = []
        derived_ata_map = {}
        user_wallet = self.keypair.pubkey()
        router_ix_idx = None
        router_ix_data = None
        router_program_id = None
        # First pass: find all ATA creation instructions and build mapping from original ATA to derived ATA (for user's wallet)
        for ix_idx, ix_data in enumerate(original_instructions):
            program_id_index = ix_data.get('programIdIndex', 0)
            if program_id_index >= len(account_keys):
                logger.warning(f"[COPY EXECUTOR] Skipping instruction {ix_idx}: programIdIndex {program_id_index} out of bounds for account_keys (len={len(account_keys)})")
                continue
            program_id_str = account_keys[program_id_index]
            accounts_list = ix_data.get('accounts', [])
            logger.info(f"[ORIG IX {ix_idx}] Program: {program_id_str}")
            for i, account_index in enumerate(accounts_list):
                logger.info(f"[ORIG IX {ix_idx}]   idx {i}: {account_keys[account_index]}")
            if program_id_str == str(ATA_PROGRAM_ID):
                # Add bounds checks for ATA instruction accounts
                if len(accounts_list) > 1 and accounts_list[1] < len(account_keys):
                    mint_pubkey = Pubkey.from_string(account_keys[accounts_list[1]])
                else:
                    logger.warning(f"[COPY EXECUTOR] Skipping ATA instruction {ix_idx}: insufficient accounts or out of bounds")
                    continue
                
                if accounts_list[0] >= len(account_keys):
                    logger.warning(f"[COPY EXECUTOR] Skipping ATA instruction {ix_idx}: account[0] index out of bounds")
                    continue
                
                if True:  # Continue with ATA processing
                    ata_address, _ = Pubkey.find_program_address(
                        [bytes(user_wallet), bytes(TOKEN_PROGRAM_ID), bytes(mint_pubkey)],
                        ATA_PROGRAM_ID
                    )
                    original_ata = account_keys[accounts_list[0]]
                    derived_ata_map[original_ata] = ata_address
                    logger.info(f"[DEBUG:ATA MAP] For original ATA {account_keys[accounts_list[0]]}: derived ATA = {ata_address}")
                    logger.info(f"[DEBUG:ATA MAP] Mint pubkey: {mint_pubkey}")
                    logger.info(f"[DEBUG:ATA MAP] User wallet: {user_wallet}")
            # Detect router program for Pump.fun
            if program_id_str in PUMPFUN_ROUTER_PROGRAMS and router_ix_idx is None:
                router_ix_idx = ix_idx
                router_ix_data = ix_data
                router_program_id = program_id_str
        # Second pass: patch all instructions
        for ix_idx, ix_data in enumerate(original_instructions):
            try:
                program_id_index = ix_data.get('programIdIndex', 0)
                if program_id_index >= len(account_keys):
                    continue
                program_id_str = account_keys[program_id_index]
                accounts_list = ix_data.get('accounts', [])
                logger.info(f"[PATCH IX {ix_idx}] Program: {program_id_str}")
                for i, account_index in enumerate(accounts_list):
                    # Add bounds check for account_index
                    if account_index >= len(account_keys):
                        logger.warning(f"[PATCH IX {ix_idx}] Skipping account {i}: index {account_index} out of bounds (len={len(account_keys)})")
                        continue
                    logger.info(f"[PATCH IX {ix_idx}]   idx {i}: {account_keys[account_index]}")
                # Check ATA creation: only create if ATA doesn't already exist
                if program_id_str == str(ATA_PROGRAM_ID):
                    mint_pubkey = Pubkey.from_string(account_keys[accounts_list[1]])
                    ata_address, _ = Pubkey.find_program_address(
                        [bytes(user_wallet), bytes(TOKEN_PROGRAM_ID), bytes(mint_pubkey)],
                        ATA_PROGRAM_ID
                    )
                    
                    # Check if ATA already exists
                    try:
                        from env_keys import EnvKeys
                        env = EnvKeys()
                        
                        check_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getAccountInfo",
                            "params": [str(ata_address), {"encoding": "base64"}]
                        }
                        
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            resp = await client.post(env.HELIUS_RPC_URL, json=check_payload)
                            ata_data = resp.json()
                            
                        ata_exists = ata_data.get('result', {}).get('value') is not None
                        
                        if ata_exists:
                            logger.info(f"[ATA CHECK] ATA {str(ata_address)[:8]}... already exists, skipping creation")
                            continue  # Skip ATA creation - it already exists
                        else:
                            logger.info(f"[ATA CHECK] ATA {str(ata_address)[:8]}... doesn't exist, creating it")
                            
                    except Exception as e:
                        logger.warning(f"[ATA CHECK] Failed to check ATA existence: {e}, assuming it needs creation")
                    
                    # Create ATA instruction only if it doesn't exist
                    patched_accounts = []
                    for i, account_index in enumerate(accounts_list):
                        if i == 0:
                            account_key = ata_address
                            is_signer = False
                        elif i == 1:
                            account_key = mint_pubkey
                            is_signer = False
                        elif i == 2:
                            account_key = user_wallet
                            is_signer = False
                        elif i == 3:
                            account_key = user_wallet
                            is_signer = True
                        else:
                            key_str = account_keys[account_index]
                            account_key = Pubkey.from_string(key_str)
                            is_signer = False
                        is_writable = True
                        patched_accounts.append(AccountMeta(
                            pubkey=account_key,
                            is_signer=is_signer,
                            is_writable=is_writable
                        ))
                        logger.info(f"[PATCH IX {ix_idx}]   PATCHED idx {i}: {account_key} signer={is_signer}")
                    data_bytes = b''
                    if ix_data.get('data'):
                        data_bytes = base58.b58decode(ix_data['data'])
                    copied.append(Instruction(
                        program_id=ATA_PROGRAM_ID,
                        accounts=patched_accounts,
                        data=data_bytes
                    ))
                    continue
                # Patch router instruction for Pump.fun: always use user's wallet and derived ATA
                if router_ix_idx is not None and ix_idx == router_ix_idx and router_program_id in PUMPFUN_ROUTER_PROGRAMS:
                    patched_accounts = []
                    print("\n[DEBUG] Patching router instruction accounts:")
                    # Extract token mint from router instruction (index 5 in Pump.fun router)
                    mint_index = 5 if len(accounts_list) > 5 else None
                    token_mint = account_keys[accounts_list[mint_index]] if mint_index is not None else None
                    orig_ata = str(get_associated_token_address(Pubkey.from_string(original_wallet), Pubkey.from_string(token_mint))) if token_mint else None
                    patched_pubkeys = []
                    for i, account_index in enumerate(accounts_list):
                        key_str = account_keys[account_index]
                        # Replace original wallet with user wallet
                        if key_str == original_wallet:
                            account_key = user_wallet
                            is_signer = True
                        # Replace original user's ATA with our ATA
                        elif orig_ata and key_str == orig_ata:
                            account_key = derived_ata_map.get(orig_ata, orig_ata)
                            is_signer = False
                        elif key_str in derived_ata_map:
                            account_key = derived_ata_map[key_str]
                            is_signer = False
                        else:
                            account_key = Pubkey.from_string(key_str)
                            is_signer = False
                        is_writable = True if i < 10 else False
                        patched_accounts.append(AccountMeta(
                            pubkey=account_key,
                            is_signer=is_signer,
                            is_writable=is_writable
                        ))
                        patched_pubkeys.append(str(account_key))
                        print(f"  [DEBUG] idx {i}: {account_key} signer={is_signer} writable={is_writable} (orig: {key_str})")
                    print("\n[DEBUG] FINAL PATCHED ROUTER ACCOUNTS (ORDERED):")
                    for idx, pubkey in enumerate(patched_pubkeys):
                        print(f"    [{idx}] {pubkey}")
                    data_bytes = b''
                    if ix_data.get('data'):
                        data_bytes = base58.b58decode(ix_data['data'])
                    copied.append(Instruction(
                        program_id=Pubkey.from_string(router_program_id),
                        accounts=patched_accounts,
                        data=data_bytes
                    ))
                    continue
                # Patch all other instructions: replace any account that matches original ATA, original owner, or original payer with user's wallet/ATA
                program_id = Pubkey.from_string(program_id_str)
                account_metas = []
                for i, account_index in enumerate(accounts_list):
                    if account_index >= len(account_keys):
                        continue
                    key_str = account_keys[account_index]
                    if key_str == original_wallet:
                        account_key = user_wallet
                        is_signer = True
                    elif key_str in derived_ata_map:
                        account_key = derived_ata_map[key_str]
                        is_signer = False
                    elif key_str == str(user_wallet):
                        account_key = user_wallet
                        is_signer = False
                    else:
                        account_key = Pubkey.from_string(key_str)
                        is_signer = False
                    is_writable = True if i < 10 else False
                    account_metas.append(AccountMeta(
                        pubkey=account_key,
                        is_signer=is_signer,
                        is_writable=is_writable
                    ))
                    logger.info(f"[PATCH IX {ix_idx}]   PATCHED idx {i}: {account_key} signer={is_signer}")
                data_bytes = b''
                if ix_data.get('data'):
                    data_bytes = base58.b58decode(ix_data['data'])
                copied.append(Instruction(
                    program_id=program_id,
                    accounts=account_metas,
                    data=data_bytes
                ))
            except Exception as e:
                logger.warning(f"⚠️ Skipping instruction: {e}")
                continue
        return copied
        """
        Clean, robust implementation for atomic ATA/owner patching with debug logging.
        """
        from solders.pubkey import Pubkey
        from solders.instruction import AccountMeta, Instruction
        import base58
        ATA_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
        TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        copied = []
        derived_ata_map = {}
        # First pass: find all ATA creation instructions and build mapping from original ATA to derived ATA (for user's wallet)
        user_wallet = self.keypair.pubkey()
        for ix_data in original_instructions:
            program_id_index = ix_data.get('programIdIndex', 0)
            if program_id_index >= len(account_keys):
                continue
            program_id_str = account_keys[program_id_index]
            if program_id_str == str(ATA_PROGRAM_ID):
                accounts_list = ix_data.get('accounts', [])
                if len(accounts_list) > 1:
                    mint_pubkey = Pubkey.from_string(account_keys[accounts_list[1]])
                    ata_address, _ = Pubkey.find_program_address(
                        [bytes(user_wallet), bytes(TOKEN_PROGRAM_ID), bytes(mint_pubkey)],
                        ATA_PROGRAM_ID
                    )
                    logger.info(f"[DEBUG:ATA MAP] For original ATA {account_keys[accountsList[0]]}: derived ATA = {ata_address}")
                    logger.info(f"[DEBUG:ATA MAP] Mint pubkey: {mint_pubkey}")
                    logger.info(f"[DEBUG:ATA MAP] User wallet: {user_wallet}")
                    original_ata = account_keys[accounts_list[0]]
                    derived_ata_map[original_ata] = ata_address
        # Second pass: patch all instructions
        for ix_idx, ix_data in enumerate(original_instructions):
            try:
                program_id_index = ix_data.get('programIdIndex', 0)
                if program_id_index >= len(account_keys):
                    continue
                program_id_str = account_keys[program_id_index]
                accounts_list = ix_data.get('accounts', [])
                # Log all original instruction accounts
                logger.info(f"[ORIG IX {ix_idx}] Program: {program_id_str}")
                for i, account_index in enumerate(accounts_list):
                    # Add bounds check for account_index
                    if account_index >= len(account_keys):
                        logger.warning(f"[ORIG IX {ix_idx}] Skipping account {i}: index {account_index} out of bounds (len={len(account_keys)})")
                        continue
                    logger.info(f"[ORIG IX {ix_idx}]   idx {i}: {account_keys[account_index]}")
                logger.info(f"[DEBUG:IX] User wallet: {user_wallet}")
                logger.info(f"[DEBUG:IX] Derived ATA map: {derived_ata_map}")
                # Patch ATA creation: always use user's wallet as owner and payer
                if program_id_str == str(ATA_PROGRAM_ID):
                    patched_accounts = []
                    patched_account_keys = []
                    mint_pubkey = Pubkey.from_string(account_keys[accounts_list[1]])
                    ata_address, _ = Pubkey.find_program_address(
                        [bytes(user_wallet), bytes(TOKEN_PROGRAM_ID), bytes(mint_pubkey)],
                        ATA_PROGRAM_ID
                    )
                    logger.info(f"[ATA PATCH] idx 0 (ATA): {ata_address}")
                    logger.info(f"[ATA VERIFY] Owner pubkey (for seed): {str(user_wallet)}")
                    logger.info(f"[ATA VERIFY] Mint pubkey: {str(mint_pubkey)}")
                    logger.info(f"[ATA VERIFY] Solana CLI: spl-token account-info --owner {str(user_wallet)} {str(mint_pubkey)}")
                    logger.info(f"[ATA VERIFY] Derived ATA address (should match CLI): {str(ata_address)}")
                    for i, account_index in enumerate(accounts_list):
                        if i == 0:
                            # ATA address
                            account_key = ata_address
                            is_signer = False
                        elif i == 1:
                            # Mint
                            account_key = mint_pubkey
                            is_signer = False
                        elif i == 2:
                            # Owner (replace with user's wallet)
                            account_key = user_wallet
                            is_signer = False
                        elif i == 3:
                            # Payer (replace with user's wallet)
                            account_key = user_wallet
                            is_signer = True
                        else:
                            key_str = account_keys[account_index]
                            account_key = Pubkey.from_string(key_str)
                            is_signer = False
                        is_writable = True
                        patched_accounts.append(AccountMeta(
                            pubkey=account_key,
                            is_signer=is_signer,
                            is_writable=is_writable
                        ))
                        patched_account_keys.append(str(account_key))
                    logger.info(f"[PATCHED IX {ix_idx}] Patched ATA ix accounts:")
                    for i, key in enumerate(patched_account_keys):
                        logger.info(f"[PATCHED IX {ix_idx}]   idx {i}: {key}")
                    data_bytes = b''
                    if ix_data.get('data'):
                        data_bytes = base58.b58decode(ix_data['data'])
                    copied.append(Instruction(
                        program_id=ATA_PROGRAM_ID,
                        accounts=patched_accounts,
                        data=data_bytes
                    ))
                    continue
                # Patch all other instructions: replace any account that matches original ATA, original owner, or original payer with user's wallet/ATA
                program_id = Pubkey.from_string(program_id_str)
                account_metas = []
                patched_account_keys = []
                # Log and decode instruction data for Pump.fun buy instruction
                if program_id_str == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    if ix_data.get('data'):
                        try:
                            raw_data = base58.b58decode(ix_data['data'])
                            logger.info(f"[PUMPFUN BUY IX {ix_idx}] Raw data (base58): {ix_data['data']}")
                            logger.info(f"[PUMPFUN BUY IX {ix_idx}] Raw data (hex): {raw_data.hex()}")
                            logger.info(f"[DEBUG:PUMPFUN BUY] User wallet: {user_wallet}")
                            logger.info(f"[DEBUG:PUMPFUN BUY] Derived ATA map: {derived_ata_map}")
                            # Attempt to patch owner/ATA in instruction data
                            # WARNING: This is a placeholder. You must update offsets if Anchor layout changes.
                            patched_data = bytearray(raw_data)
                            # Example: If owner pubkey is at offset 8, replace with user's wallet pubkey
                            # (Pump.fun Anchor layout may differ; update as needed)
                            # Replace 32 bytes at offset 8 with user's wallet pubkey
                            # owner_offset = 8
                            # patched_data[owner_offset:owner_offset+32] = bytes(user_wallet)
                            # logger.info(f"[PUMPFUN PATCH] Patched owner at offset {owner_offset} with {str(user_wallet)}")
                            # If ATA is also encoded, patch similarly (update offset as needed)
                            # ata_offset = ...
                            # patched_data[ata_offset:ata_offset+32] = bytes(derived_ata_map.get(original_ata, b''))
                            # logger.info(f"[PUMPFUN PATCH] Patched ATA at offset {ata_offset}")
                            # Use patched_data as instruction data
                            data_bytes = bytes(patched_data)
                        except Exception as e:
                            logger.warning(f"[PUMPFUN BUY IX {ix_idx}] Failed to decode/patch data: {e}")
                            data_bytes = base58.b58decode(ix_data['data'])
                    else:
                        data_bytes = b''
                else:
                    data_bytes = b''
                for i, account_index in enumerate(accounts_list):
                    if account_index >= len(account_keys):
                        continue
                    key_str = account_keys[account_index]
                    # Replace original signer, original owner, original payer, and original ATA with user's wallet/ATA
                    if key_str == original_wallet:
                        account_key = user_wallet
                        is_signer = True
                    elif key_str in derived_ata_map:
                        account_key = derived_ata_map[key_str]
                        is_signer = False
                    elif key_str == str(user_wallet):
                        account_key = user_wallet
                        is_signer = False
                    else:
                        account_key = Pubkey.from_string(key_str)
                        is_signer = False
                    is_writable = True if i < 10 else False
                    logger.info(f"[DEBUG:ACCT META] idx {i}: key_str={key_str}, account_key={account_key}, is_signer={is_signer}, is_writable={is_writable}")
                    account_metas.append(AccountMeta(
                        pubkey=account_key,
                        is_signer=is_signer,
                        is_writable=is_writable
                    ))
                    patched_account_keys.append(str(account_key))
                logger.info(f"[PATCHED IX {ix_idx}] Patched ix accounts:")
                for i, key in enumerate(patched_account_keys):
                    logger.info(f"[PATCHED IX {ix_idx}]   idx {i}: {key}")
                # Use patched data_bytes if this is Pump.fun buy, else decode as before
                if program_id_str == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                    copied.append(Instruction(
                        program_id=program_id,
                        accounts=account_metas,
                        data=data_bytes
                    ))
                else:
                    data_bytes = b''
                    if ix_data.get('data'):
                        data_bytes = base58.b58decode(ix_data['data'])
                    copied.append(Instruction(
                        program_id=program_id,
                        accounts=account_metas,
                        data=data_bytes
                    ))
            except Exception as e:
                logger.warning(f"⚠️ Skipping instruction: {e}")
                continue
        return copied



    async def copy_transaction_from_signature(
        self, 
        transaction_signature: str, 
        original_wallet: str,
        detected_trade: Dict
    ) -> Dict[str, Any]:
        """
        Fetch original transaction data from signature and copy it directly
        This replaces API-based copying with pure instruction copying
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"🚀 Fetching original transaction: {transaction_signature[:8]}...")
            
            # Fetch the original transaction from RPC
            env_keys = EnvKeys()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                rpc_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        transaction_signature,
                        {
                            "encoding": "json",
                            "commitment": "confirmed",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                }
                
                response = await client.post(env_keys.HELIUS_RPC_URL, json=rpc_payload)
                if response.status_code != 200:
                    return {"success": False, "error": f"RPC request failed: {response.status_code}"}
                
                rpc_result = response.json()
                if 'error' in rpc_result:
                    return {"success": False, "error": f"RPC error: {rpc_result['error']}"}
                
                if not rpc_result.get('result'):
                    return {"success": False, "error": "Transaction not found"}
                
                original_tx_data = rpc_result['result']
            
            # Determine DEX type and route appropriately
            logger.info(f"[DEBUG] About to access detected_trade.get(), type: {type(detected_trade)}, value: {detected_trade}")
            
            try:
                dex_router = detected_trade.get('router', '').lower()
            except Exception as e:
                logger.error(f"[DEBUG] Error accessing detected_trade: {e}")
                raise e
            
            logger.info(f"[DEBUG] original_tx_data type: {type(original_tx_data)}")
            logger.info(f"[DEBUG] dex_router: {dex_router}")
            logger.info(f"[DEBUG] detected_trade: {detected_trade}")
            
            if 'jupiter' in dex_router or 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4' in str(original_tx_data):
                return await self.copy_jupiter_transaction_direct(
                    original_tx_data, 
                    original_wallet, 
                    detected_trade
                )
            elif 'pump' in dex_router or '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P' in str(original_tx_data):
                # Pass the fetched transaction data directly to avoid recursion
                return await self.copy_pumpfun_transaction_direct(
                    {'transaction': original_tx_data}, 
                    original_wallet, 
                    detected_trade
                )
            else:
                # Generic direct copy for other DEXes
                return await self.copy_generic_transaction_direct(
                    original_tx_data, 
                    original_wallet, 
                    detected_trade
                )
                
        except Exception as e:
            elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"❌ Failed to fetch and copy transaction in {elapsed_time:.1f}ms: {e}")
            return {"success": False, "error": str(e), "execution_time_ms": elapsed_time}

    async def copy_generic_transaction_direct(
        self, 
        original_tx_data: Dict, 
        original_wallet: str,
        detected_trade: Dict
    ) -> Dict[str, Any]:
        """
        Generic direct copy for any DEX transaction
        
        Implements comprehensive transaction validation:
        - Validates transaction structure before processing
        - Adds bounds checks for all list/array accesses
        - Logs and skips trades with insufficient instruction/account data
        - Prevents list index out of range runtime errors
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("🚀 MEV Direct Copy: Generic transaction")
            
            # Validate transaction structure before processing
            if not original_tx_data:
                logger.error("[DIRECT_COPY] ❌ Invalid transaction: original_tx_data is None or empty")
                return {"success": False, "error": "Invalid transaction data"}
            
            # Extract the original transaction data
            if 'transaction' in original_tx_data:
                tx_data = original_tx_data['transaction']
            else:
                tx_data = original_tx_data
            
            if not tx_data:
                logger.error("[DIRECT_COPY] ❌ Invalid transaction: tx_data is None or empty")
                return {"success": False, "error": "Invalid transaction data structure"}
                
            # Get the original message and instructions with validation
            message = tx_data.get('message', {})
            if not message:
                logger.error("[DIRECT_COPY] ❌ Invalid transaction: message is None or empty")
                return {"success": False, "error": "No message found in transaction"}
            
            original_instructions = message.get('instructions', [])
            account_keys = message.get('accountKeys', [])
            
            # Validate instructions exist
            if not original_instructions:
                logger.error("[DIRECT_COPY] ❌ Skipping trade: No instructions found in original transaction")
                return {"success": False, "error": "No instructions found in original transaction"}
            
            # Validate account keys exist
            if not account_keys:
                logger.error("[DIRECT_COPY] ❌ Skipping trade: No account keys found in transaction")
                return {"success": False, "error": "No account keys found in transaction"}
            
            logger.info(f"[DIRECT_COPY] ✅ Transaction validation passed: {len(original_instructions)} instructions, {len(account_keys)} account keys")
            
            # Build MEV-optimized instruction list
            all_instructions = []
            
            # 1. Add MEV compute budget instructions FIRST
            mev_compute_instructions = [
                set_compute_unit_limit(self.config.compute_limit),
                set_compute_unit_price(self.config.jupiter_priority_fee // 1000)  # Convert to micro-lamports per CU
            ]
            all_instructions.extend(mev_compute_instructions)
            
            # 2. Add Jito tip instruction for MEV bundling
            if self.config.use_jito_bundles:
                tip_ix = create_jito_tip_instruction(
                    self.keypair.pubkey(), 
                    self.config.jito_tip_amount
                )
                if tip_ix:
                    all_instructions.append(tip_ix)
            
            # 3. Process and copy original instructions with wallet replacement
            copied_instructions = await self._copy_and_modify_instructions(
                original_instructions, 
                account_keys, 
                original_wallet
            )
            all_instructions.extend(copied_instructions)
            
            # 4. Build and submit the transaction
            # If FastExecutor is available, use it; otherwise use internal method
            if self.fast_executor:
                # Build the VersionedTransaction first
                from solders.transaction import VersionedTransaction
                from solders.message import MessageV0
                
                signed_tx = await self.mev_bot._build_signed_transaction(all_instructions)
                if not signed_tx:
                    elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    return exec_err("direct_copy", "Failed to build transaction", {
                        "execution_time_ms": elapsed_time,
                        "dex": "generic"
                    })
                
                # Submit via FastExecutor
                signature = await submit_cloned_tx(signed_tx, self.fast_executor)
            else:
                # Fallback to internal _submit_mev_transaction
                signature = await self._submit_mev_transaction(all_instructions)
            
            elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if signature:
                logger.info(f"✅ MEV Direct Copy SUCCESS! {elapsed_time:.1f}ms - {signature}")
                return exec_ok("direct_copy", signature, {
                    "execution_time_ms": elapsed_time,
                    "method": "mev_direct_copy",
                    "dex": "generic"
                })
            else:
                return exec_err("direct_copy", "Transaction submission failed", {
                    "execution_time_ms": elapsed_time,
                    "dex": "generic"
                })
                
        except Exception as e:
            elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"❌ MEV Direct Copy failed in {elapsed_time:.1f}ms: {e}")
            return exec_err("direct_copy", str(e), {
                "execution_time_ms": elapsed_time,
                "dex": "generic"
            })

    async def copy_jupiter_transaction_direct(
        self, 
        original_tx_data: Dict, 
        original_wallet: str,
        detected_trade: Dict
    ) -> Dict[str, Any]:
        """
        Copy Jupiter transaction using direct instruction copying with MEV optimizations
        This is the FAST method - no API calls
        
        Implements comprehensive transaction validation:
        - Validates transaction structure before processing
        - Adds bounds checks for all list/array accesses
        - Logs and skips trades with insufficient instruction/account data
        - Prevents list index out of range runtime errors
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("🚀 MEV Direct Copy: Jupiter transaction")
            
            # Validate transaction structure before processing
            if not original_tx_data:
                logger.error("[DIRECT_COPY] ❌ Invalid transaction: original_tx_data is None or empty")
                return {"success": False, "error": "Invalid transaction data"}
            
            # Extract the original transaction data
            if 'transaction' in original_tx_data:
                tx_data = original_tx_data['transaction']
            else:
                tx_data = original_tx_data
            
            if not tx_data:
                logger.error("[DIRECT_COPY] ❌ Invalid transaction: tx_data is None or empty")
                return {"success": False, "error": "Invalid transaction data structure"}
                
            # Get the original message and instructions with validation
            message = tx_data.get('message', {})
            if not message:
                logger.error("[DIRECT_COPY] ❌ Invalid transaction: message is None or empty")
                return {"success": False, "error": "No message found in transaction"}
            
            original_instructions = message.get('instructions', [])
            account_keys = message.get('accountKeys', [])
            
            # Validate instructions exist
            if not original_instructions:
                logger.error("[DIRECT_COPY] ❌ Skipping trade: No instructions found in original transaction")
                return {"success": False, "error": "No instructions found in original transaction"}
            
            # Validate account keys exist
            if not account_keys:
                logger.error("[DIRECT_COPY] ❌ Skipping trade: No account keys found in transaction")
                return {"success": False, "error": "No account keys found in transaction"}
            
            logger.info(f"[DIRECT_COPY] ✅ Transaction validation passed: {len(original_instructions)} instructions, {len(account_keys)} account keys")
            
            # Build MEV-optimized instruction list
            all_instructions = []
            
            # 1. Add MEV compute budget instructions FIRST
            mev_compute_instructions = [
                set_compute_unit_limit(self.config.compute_limit),
                set_compute_unit_price(self.config.jupiter_priority_fee // 1000)  # Convert to micro-lamports per CU
            ]
            all_instructions.extend(mev_compute_instructions)
            
            # 2. Add Jito tip instruction for MEV bundling
            if self.config.use_jito_bundles:
                tip_ix = create_jito_tip_instruction(
                    self.keypair.pubkey(), 
                    self.config.jito_tip_amount
                )
                if tip_ix:
                    all_instructions.append(tip_ix)
            
            # 3. Process and copy original instructions with wallet replacement
            copied_instructions = await self._copy_and_modify_instructions(
                original_instructions, 
                account_keys, 
                original_wallet
            )
            all_instructions.extend(copied_instructions)
            
            # 4. Build and submit the transaction
            # If FastExecutor is available, use it; otherwise use internal method
            if self.fast_executor:
                # Build the VersionedTransaction first
                from solders.transaction import VersionedTransaction
                from solders.message import MessageV0
                
                signed_tx = await self.mev_bot._build_signed_transaction(all_instructions)
                if not signed_tx:
                    elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    return exec_err("direct_copy", "Failed to build transaction", {
                        "execution_time_ms": elapsed_time,
                        "dex": "jupiter"
                    })
                
                # Submit via FastExecutor
                signature = await submit_cloned_tx(signed_tx, self.fast_executor)
            else:
                # Fallback to internal _submit_mev_transaction
                signature = await self._submit_mev_transaction(all_instructions)
            
            elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if signature:
                logger.info(f"✅ MEV Direct Copy SUCCESS! {elapsed_time:.1f}ms - {signature}")
                return exec_ok("direct_copy", signature, {
                    "execution_time_ms": elapsed_time,
                    "method": "mev_direct_copy",
                    "dex": "jupiter"
                })
            else:
                return exec_err("direct_copy", "Transaction submission failed", {
                    "execution_time_ms": elapsed_time,
                    "dex": "jupiter"
                })
                
        except Exception as e:
            elapsed_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"❌ MEV Direct Copy failed in {elapsed_time:.1f}ms: {e}")
            return exec_err("direct_copy", str(e), {
                "execution_time_ms": elapsed_time,
                "dex": "jupiter"
            })

    async def copy_pumpfun_transaction_direct(
        self, 
        original_tx_data: Dict, 
        original_wallet: str,
        detected_trade: Dict
    ) -> Dict[str, Any]:
        """
        Copy Pump.fun transaction using direct instruction copying with MEV optimizations
        """
        start_time = asyncio.get_event_loop().time()
        try:
            logger.info("🚀 MEV Direct Copy: Pump.fun transaction")
            
            # If we only have signature, fetch the full transaction data
            if 'signature' in original_tx_data and 'transaction' not in original_tx_data:
                signature = original_tx_data['signature']
                return await self.copy_transaction_from_signature(
                    signature, 
                    original_wallet,
                    detected_trade
                )
            
            # Similar to Jupiter but with Pump.fun specific optimizations
            if 'transaction' in original_tx_data:
                tx_data = original_tx_data['transaction']
            else:
                tx_data = original_tx_data
            message = tx_data.get('message', {})
            original_instructions = message.get('instructions', [])
            account_keys = message.get('accountKeys', [])

            # Copy and modify instructions
            copied_instructions = await self._copy_and_modify_instructions(
                original_instructions, account_keys, original_wallet
            )

            # Remove all ComputeBudget instructions from copied_instructions
            filtered = [ix for ix in copied_instructions if str(ix.program_id) != "ComputeBudget111111111111111111111111111111"]

            # Prepare final instructions: only one SetComputeUnitLimit and one SetComputeUnitPrice
            final_instructions = []
            # Add bot's ComputeBudget instructions first
            final_instructions.append(set_compute_unit_limit(self.config.compute_limit))
            final_instructions.append(set_compute_unit_price(self.config.pumpfun_priority_fee // 1000))
            # Add Jito tip if needed
            if self.config.use_jito_bundles:
                tip_ix = create_jito_tip_instruction(self.keypair.pubkey(), self.config.jito_tip_amount)
                if tip_ix:
                    final_instructions.append(tip_ix)
            # Add all other instructions
            final_instructions.extend(filtered)

            # Build and submit the transaction
            # If FastExecutor is available, use it; otherwise use internal method
            if self.fast_executor:
                # Build the VersionedTransaction first
                from solders.transaction import VersionedTransaction
                from solders.message import MessageV0
                
                signed_tx = await self.mev_bot._build_signed_transaction(final_instructions)
                if not signed_tx:
                    elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
                    return exec_err("direct_copy", "Failed to build transaction", {
                        "execution_time_ms": elapsed,
                        "dex": "pumpfun"
                    })
                
                # Submit via FastExecutor
                signature = await submit_cloned_tx(signed_tx, self.fast_executor)
            else:
                # Fallback to internal _submit_mev_transaction
                signature = await self._submit_mev_transaction(final_instructions)
            
            elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
            if signature:
                return exec_ok("direct_copy", signature, {
                    "execution_time_ms": elapsed,
                    "method": "mev_direct_copy",
                    "dex": "pumpfun"
                })
            return exec_err("direct_copy", "Transaction submission failed", {
                "execution_time_ms": elapsed,
                "dex": "pumpfun"
            })
        except Exception as e:
            elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"❌ MEV Direct Copy failed in {elapsed:.1f}ms: {e}")
            return exec_err("direct_copy", str(e), {
                "execution_time_ms": elapsed,
                "dex": "pumpfun"
            })


# Convenience functions for integration with existing execution coordinator
async def try_mev_direct_copy_buy(
    wallet_keypair: Keypair, 
    token_mint: str, 
    amount_sol: float, 
    detected_trade: Dict = None,
    original_tx_data: Dict = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for MEV direct copy integration
    """
    try:
        private_key = base58.b58encode(wallet_keypair.secret()).decode('ascii')
        
        # Create MEV direct copy executor
        config = MEVDirectCopyConfig(
            jupiter_priority_fee=kwargs.get('priority_fee', 2_000_000),
            use_jito_bundles=kwargs.get('jito_service') is not None,
            max_copy_time_ms=kwargs.get('max_copy_time_ms', 500.0)
        )
        
        executor = MEVDirectCopyExecutor(private_key, config)
        
        # If we have the original transaction data, use direct copying
        if original_tx_data and detected_trade:
            result = await executor.execute_copy_trade(
                detected_trade,
                original_tx_data,
                **kwargs
            )
        else:
            # Fallback to MEV bot for new transaction building
            logger.info("📢 No original transaction data - using MEV bot fallback")
            signature = await executor.mev_bot.buy_token(token_mint, amount_sol)
            if signature:
                result = {
                    "success": True,
                    "signature": signature,
                    "method": "mev_fallback",
                    "dex": "mev_bot"
                }
            else:
                result = {"success": False, "error": "MEV bot execution failed"}
        
        return result
        
    except Exception as e:
        logger.error(f"❌ MEV direct copy buy failed: {e}")