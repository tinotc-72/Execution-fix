#!/usr/bin/env python3 - This script is for getting details from a pasted transaction signature
"""
Advanced Solana Transaction Analyzer
Extracts detailed information from any Solana transaction, with special focus on DEX activities
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import base64

from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solders.transaction import Transaction
from base58 import b58decode, b58encode

from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transaction_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants for DEX program IDs
PUMP_PROGRAM_ID = "PUmpFMxQheCHicHJYqZBp9CqHhVEJXHEdSGKXxWqE3d"  # Pump.fun program ID
JUPITER_PROGRAM_ID = "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB"  # Jupiter
RAYDIUM_PROGRAM_ID = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"  # Raydium

# Constants for instruction discriminators
PUMP_SWAP_IX = bytes([9, 50, 133, 111, 27, 149, 102, 83])  # Updated discriminator for Pump.fun swap
JUPITER_SWAP_IX = bytes([62, 198, 214, 193, 213, 159, 108, 210])  # Updated discriminator for Jupiter v6 swap

# Account role constants
ROLE_TOKEN_ACCOUNT = "token_account"
ROLE_TOKEN_MINT = "token_mint"
ROLE_PROGRAM = "program"
ROLE_SIGNER = "signer"
ROLE_SYSTEM = "system"
ROLE_UNKNOWN = "unknown"

# Known DEX Program IDs
KNOWN_DEXES = {
    "JUP6LkbZbjS1jKKwapdHH3deZxw1biwkKBBPrZkYqGv": "Jupiter v6",
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium",
    "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX": "Serum",
    "M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K": "Magic Eden",
}

# Known program IDs
KNOWN_PROGRAMS = {
    'JUP6LkbZbjS1jKKwapdHH3deZxw1biwkKBBPrZkYqGv': 'Jupiter v6',
    '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun',
    'RAYZYMhp1QQfJy78m3HQrmhvGxs6FSydWdGGe6y8wxZ': 'Raydium AMM',
    'So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo': 'Solend Program',
    'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA': 'Token Program',
    'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL': 'Associated Token Program',
    '11111111111111111111111111111111': 'System Program',
}

# Account indices in swap instructions
class PumpSwapAccounts:
    AUTHORITY = 0
    USER_WALLET = 1
    TOKEN_ACCOUNT_IN = 2
    TOKEN_ACCOUNT_OUT = 3
    TOKEN_MINT_IN = 4
    TOKEN_MINT_OUT = 5
    POOL = 6
    PROGRAM = 7

class JupiterSwapAccounts:
    USER_WALLET = 0
    TOKEN_ACCOUNT_IN = 1
    TOKEN_ACCOUNT_OUT = 2
    TOKEN_MINT_IN = 3
    TOKEN_MINT_OUT = 4
    TOKEN_PROGRAM = 5
    POOL = 6

def decode_pump_swap_data(data: bytes) -> Optional[Dict[str, Any]]:
    """Decode Pump.fun swap instruction data"""
    try:
        if len(data) < 8:
            return None
            
        discriminator = data[:8]
        if discriminator != PUMP_SWAP_IX:
            return None
            
        # Pump.fun swap layout:
        # u64 (8 bytes): amount_in
        # u64 (8 bytes): min_amount_out
        # u16 (2 bytes): slippage_bps
        amount_in = int.from_bytes(data[8:16], 'little')
        min_amount_out = int.from_bytes(data[16:24], 'little')
        slippage_bps = int.from_bytes(data[24:26], 'little')
        
        return {
            'type': 'swap',
            'amount_in': amount_in,
            'min_amount_out': min_amount_out,
            'slippage_bps': slippage_bps
        }
    except Exception as e:
        logging.error(f"Error decoding Pump swap data: {e}")
        return None

def decode_jupiter_swap_data(data: bytes) -> Optional[Dict[str, Any]]:
    """Decode Jupiter swap instruction data"""
    try:
        if len(data) < 8:
            return None
            
        discriminator = data[:8]
        if discriminator != JUPITER_SWAP_IX:
            return None
            
        # Jupiter swap layout:
        # u64: amount_in
        # u64: min_amount_out
        # u16: slippage_bps
        # u8: number_of_routes
        # followed by route data
        amount_in = int.from_bytes(data[8:16], 'little')
        min_amount_out = int.from_bytes(data[16:24], 'little')
        slippage_bps = int.from_bytes(data[24:26], 'little')
        num_routes = data[26]
        
        return {
            'type': 'swap',
            'amount_in': amount_in,
            'min_amount_out': min_amount_out,
            'slippage_bps': slippage_bps,
            'num_routes': num_routes
        }
    except Exception as e:
        logging.error(f"Error decoding Jupiter swap data: {e}")
        return None

async def identify_token_account_info(pubkey: str, connection: AsyncClient) -> Optional[Dict[str, Any]]:
    """Get detailed information about a token account"""
    try:
        account_info = await connection.get_account_info(Pubkey.from_string(pubkey))
        if not account_info.value:
            return None
            
        # Parse SPL Token account data
        # Layout: https://github.com/solana-labs/solana-program-library/blob/master/token/js/src/state/account.ts
        data = account_info.value.data
        if len(data) != 165:  # SPL Token Account size
            return None
            
        mint = str(Pubkey.from_bytes(data[0:32]))
        owner = str(Pubkey.from_bytes(data[32:64]))
        amount = int.from_bytes(data[64:72], 'little')
        
        # Get mint info for decimals
        mint_info = await connection.get_account_info(Pubkey.from_string(mint))
        decimals = mint_info.value.data[44] if mint_info.value else 9
        
        return {
            'token_mint': mint,
            'owner': owner,
            'amount': amount,
            'decimals': decimals
        }
    except Exception as e:
        logging.error(f"Error getting token account info: {e}")
        return None

@dataclass
class TokenTransfer:
    """Represents a token transfer in the transaction"""
    token_mint: str
    from_address: str
    to_address: str
    amount: int
    decimals: Optional[int] = None

    @property
    def formatted_amount(self) -> float:
        """Return human-readable token amount"""
        if self.decimals is not None:
            return self.amount / (10 ** self.decimals)
        return self.amount

@dataclass
class DEXSwap:
    """Represents a DEX swap operation"""
    dex_name: str
    program_id: str
    input_token: TokenTransfer
    output_token: TokenTransfer
    fee_amount: Optional[float] = None
    slippage: Optional[float] = None
    price_impact: Optional[float] = None

@dataclass
class TransactionSummary:
    """Complete transaction analysis summary"""
    signature: str
    timestamp: datetime
    status: str
    fee: int
    token_transfers: List[TokenTransfer]
    dex_swaps: List[DEXSwap]
    sol_transfers: List[Dict[str, Any]]
    program_ids: List[str]
    log_messages: List[str]
    raw_data: Dict[str, Any]

@dataclass
class AccountInfo:
    """Detailed information about an account involved in a transaction"""
    pubkey: str
    is_signer: bool
    is_writable: bool
    role: Optional[str] = None  # e.g., 'token_account', 'mint', 'authority', 'program'
    token_info: Optional[Dict[str, Any]] = None  # For token accounts: mint, owner, amount

@dataclass
class InstructionData:
    """Decoded instruction data from a transaction"""
    program_id: str
    program_name: str  # e.g., 'Jupiter', 'Pump.fun', etc.
    accounts: List[AccountInfo]
    data: bytes
    decoded_data: Optional[Dict[str, Any]] = None  # Parsed instruction data if known format

@dataclass
class SwapParameters:
    """Detailed swap parameters extracted from instruction data"""
    input_mint: str
    output_mint: str
    amount_in: int
    min_amount_out: Optional[int] = None
    slippage_bps: Optional[int] = None
    route: Optional[List[str]] = None  # List of programs/AMMs in the swap route

class TransactionAnalyzer:
    """Analyzes Solana transactions with focus on DEX activities"""
    
    def __init__(self):
        env = EnvKeys()
        self.client = AsyncClient(env.HELIUS_RPC_URL)
        logger.info(f"Initialized with RPC URL: {env.HELIUS_RPC_URL}")

    async def get_token_metadata(self, mint_address: str) -> Dict[str, Any]:
        """Fetch token metadata including decimals"""
        try:
            account_info = await self.client.get_account_info(Pubkey.from_string(mint_address))
            if not account_info.value:
                return {}
            
            # Parse mint data to get decimals
            # TODO: Add proper SPL token mint data parsing
            return {
                "decimals": 9  # Default to 9 if we can't parse
            }
        except Exception as e:
            logger.error(f"Error fetching token metadata: {e}")
            return {}

    async def analyze_token_transfers(self, tx_data: Dict) -> List[TokenTransfer]:
        """Analyze token transfers in the transaction"""
        transfers = []
        try:
            pre_balances = {
                b.get('accountIndex'): b
                for b in tx_data['meta'].get('preTokenBalances', [])
            }
            post_balances = {
                b.get('accountIndex'): b
                for b in tx_data['meta'].get('postTokenBalances', [])
            }
            
            # Get all account indices that appear in either pre or post balances
            all_indices = set(pre_balances.keys()) | set(post_balances.keys())
            
            for idx in all_indices:
                pre = pre_balances.get(idx, {'uiTokenAmount': {'amount': '0', 'decimals': 0}})
                post = post_balances.get(idx, {'uiTokenAmount': {'amount': '0', 'decimals': 0}})
                
                pre_amount = int(pre.get('uiTokenAmount', {}).get('amount', '0'))
                post_amount = int(post.get('uiTokenAmount', {}).get('amount', '0'))
                
                if pre_amount != post_amount:
                    mint = pre.get('mint') or post.get('mint')
                    owner = pre.get('owner') or post.get('owner')
                    decimals = pre.get('uiTokenAmount', {}).get('decimals') or post.get('uiTokenAmount', {}).get('decimals')
                    
                    transfer = TokenTransfer(
                        token_mint=mint,
                        from_address=owner if pre_amount > post_amount else None,
                        to_address=owner if pre_amount < post_amount else None,
                        amount=abs(post_amount - pre_amount),
                        decimals=decimals
                    )
                    transfers.append(transfer)
            
            logger.info(f"Found {len(transfers)} token transfers")
            
        except Exception as e:
            logger.error(f"Error analyzing token transfers: {e}")
        
        return transfers

    async def analyze_dex_swaps(self, tx_data: Dict, token_transfers: List[TokenTransfer]) -> List[DEXSwap]:
        """Analyze DEX swap operations in the transaction"""
        swaps = []
        try:
            instructions = tx_data['transaction']['message']['instructions']
            account_keys = tx_data['transaction']['message']['accountKeys']
            log_messages = tx_data['meta'].get('logMessages', [])

            for idx, ix in enumerate(instructions):
                program_id = ix['programId']
                
                # Detect known DEX program IDs
                if program_id in [
                    PUMP_PROGRAM_ID,  # Pump.fun
                    JUPITER_PROGRAM_ID,  # Jupiter
                    RAYDIUM_PROGRAM_ID,  # Raydium
                    # Add other DEX program IDs here
                ]:
                    # Try to decode instruction data
                    try:
                        data_bytes = b58decode(ix['data'])
                        accounts = [account_keys[int(acc_idx)] for acc_idx in ix['accounts']]
                        
                        # Find relevant token transfers
                        relevant_transfers = [
                            t for t in token_transfers
                            if (t.from_address in accounts or t.to_address in accounts)
                        ]
                        
                        if program_id == PUMP_PROGRAM_ID:
                            params = self.decode_pump_instruction(data_bytes, accounts, relevant_transfers)
                        elif program_id == JUPITER_PROGRAM_ID:
                            params = self.decode_jupiter_instruction(data_bytes, accounts, relevant_transfers)
                        else:
                            # Generic parameter extraction
                            params = SwapParameters(
                                amount_in=sum(t.amount for t in relevant_transfers if t.from_address in accounts),
                                amount_out=sum(t.amount for t in relevant_transfers if t.to_address in accounts),
                                from_token=next((t.token_mint for t in relevant_transfers if t.from_address in accounts), None),
                                to_token=next((t.token_mint for t in relevant_transfers if t.to_address in accounts), None),
                                slippage=None,
                                route=None
                            )
                        
                        if params and (params.from_token or params.to_token):
                            swap = DEXSwap(
                                dex_name=self.get_dex_name(program_id),
                                program_id=program_id,
                                instruction_index=idx,
                                params=params,
                                accounts=accounts
                            )
                            swaps.append(swap)
                    except Exception as e:
                        logger.error(f"Error decoding swap instruction: {e}")
                        continue

            logger.info(f"Found {len(swaps)} DEX swaps")
            
        except Exception as e:
            logger.error(f"Error analyzing DEX swaps: {e}")
        
        return swaps

    def get_dex_name(self, program_id: str) -> str:
        """Get the DEX name from program ID"""
        dex_mapping = {
            PUMP_PROGRAM_ID: "Pump.fun",
            JUPITER_PROGRAM_ID: "Jupiter",
            RAYDIUM_PROGRAM_ID: "Raydium",
            # Add other mappings here
        }
        return dex_mapping.get(program_id, "Unknown DEX")

    async def analyze_sol_transfers(self, tx_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract SOL transfers from the transaction"""
        sol_transfers = []
        
        if not tx_data.get('meta'):
            return sol_transfers

        pre_balances = tx_data['meta'].get('preBalances', [])
        post_balances = tx_data['meta'].get('postBalances', [])
        
        if len(pre_balances) != len(post_balances):
            return sol_transfers

        accounts = tx_data['transaction']['message']['accountKeys']
        
        for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
            if pre != post:
                transfer = {
                    'address': str(accounts[i]),
                    'pre_balance': pre / 1_000_000_000,  # Convert lamports to SOL
                    'post_balance': post / 1_000_000_000,
                    'change': (post - pre) / 1_000_000_000
                }
                sol_transfers.append(transfer)
        
        return sol_transfers

    async def identify_account_role(self, pubkey: str, accounts_context: Dict[str, Any], connection: AsyncClient) -> Optional[str]:
        """Identify the role of an account in the transaction"""
        try:
            # Check if it's a known program
            if pubkey in KNOWN_PROGRAMS:
                return 'program'
                
            # Get token account info
            token_info = await identify_token_account_info(pubkey, connection)
            if token_info:
                return 'token_account'
                
            # Check if it's a signer
            if pubkey in accounts_context.get('signers', []):
                return 'signer'
                
            # Check if it's writable
            if pubkey in accounts_context.get('writable', []):
                return 'writable'
                
            return 'unknown'
        except Exception as e:
            logging.error(f"Error identifying account role: {e}")
            return 'unknown'

    async def identify_account_role(self, account: str, tx_data: Dict, connection: AsyncClient) -> str:
        """Identify the role of an account in the transaction"""
        try:
            # Check if it's a program ID
            if account in [ix['programId'] for ix in tx_data['transaction']['message']['instructions']]:
                return ROLE_PROGRAM
                
            # Check if it's a signer
            account_keys = tx_data['transaction']['message']['accountKeys']
            if account in account_keys[:tx_data['transaction']['message'].get('header', {}).get('numRequiredSignatures', 0)]:
                return ROLE_SIGNER
                
            # Check if it's a token account or mint
            try:
                account_info = await connection.get_account_info(Pubkey.from_string(account))
                if account_info.value:
                    # TODO: Add proper SPL token program checks
                    # For now, just return token_account as a placeholder
                    return ROLE_TOKEN_ACCOUNT
            except Exception:
                pass
                
            return ROLE_UNKNOWN
            
        except Exception as e:
            logger.error(f"Error identifying account role: {e}")
            return ROLE_UNKNOWN

    async def analyze_instruction(self, ix: Dict[str, Any], tx_data: Dict[str, Any]) -> InstructionData:
        """Analyze a single instruction, with DEX-specific decoding"""
        program_id = ix['programId']
        program_name = KNOWN_PROGRAMS.get(program_id, 'Unknown Program')
        
        # Get accounts with metadata
        accounts = []
        account_metas = tx_data['transaction']['message'].get('accountKeys', [])
        
        for idx, acc in enumerate(ix['accounts']):
            # Get token account info if relevant
            token_info = await self.identify_token_account_info(acc) if program_name in ['Jupiter v6', 'Pump.fun'] else None
            
            account_info = AccountInfo(
                pubkey=acc,
                is_signer=idx < tx_data['transaction']['message'].get('numRequiredSignatures', 0),
                is_writable=idx < tx_data['transaction']['message'].get('numRequiredSignatures', 0) + tx_data['transaction']['message'].get('numReadonlySignedAccounts', 0),
                role=await self.identify_account_role(acc, tx_data, self.client),
                token_info=token_info
            )
            accounts.append(account_info)
        
        # Decode instruction data
        data = b58decode(ix.get('data', ''))
        decoded_data = self.decode_instruction_data(program_id, data)
        
        # Identify if this is a buy or sell for DEX instructions
        if program_name in ['Jupiter v6', 'Pump.fun'] and decoded_data:
            decoded_data['is_buy'] = False  # Default to sell
            for acc in accounts:
                if acc.role == 'token_account' and acc.token_info:
                    if acc.token_info['token_mint'].startswith('So1111111111111111111111111111111111111111111'):
                        # If SOL is being sent out, it's a buy
                        decoded_data['is_buy'] = True
                        break
    
        return InstructionData(
            program_id=program_id,
            program_name=program_name,
            accounts=accounts,
            data=data,
            decoded_data=decoded_data
        )

    def extract_swap_parameters(self, instruction: InstructionData) -> Optional[SwapParameters]:
        """Extract swap parameters from a DEX instruction"""
        if not instruction.decoded_data or instruction.decoded_data.get('type') != 'swap':
            return None
            
        # Find input and output token accounts
        token_accounts = [acc for acc in instruction.accounts if acc.role == 'token_account' and acc.token_info]
        if len(token_accounts) < 2:
            return None
            
        input_account = token_accounts[0]
        output_account = token_accounts[1]
        
        return SwapParameters(
            input_mint=input_account.token_info['token_mint'],
            output_mint=output_account.token_info['token_mint'],
            amount_in=instruction.decoded_data['amount_in'],
            min_amount_out=instruction.decoded_data.get('min_amount_out'),
            slippage_bps=instruction.decoded_data.get('slippage_bps'),
            route=instruction.decoded_data.get('route')
        )

    async def analyze_instructions(self, tx_data: Dict[str, Any]) -> List[InstructionData]:
        """Analyze all instructions in a transaction"""
        instructions = []
        for ix in tx_data['transaction']['message']['instructions']:
            instruction_data = await self.analyze_instruction(ix, tx_data)
            instructions.append(instruction_data)
            
        return instructions

    async def analyze_transaction(self, signature: str) -> Optional[TransactionSummary]:
        """Analyze a transaction and return detailed information"""
        try:
            logger.info(f"🔍 Analyzing transaction: {signature}")

            # Convert signature string to Signature object
            try:
                sig = Signature.from_string(signature)
            except Exception as e:
                logger.error(f"Invalid signature format: {e}")
                return None

            # Fetch transaction details with proper parsing
            tx_response = await self.client.get_transaction(sig)
            if not tx_response or not tx_response.value:
                logger.error(f"Transaction not found: {signature}")
                return None

            # Parse the transaction data from the response
            tx_value = tx_response.value
            
            # Convert meta and transaction data to a dictionary structure
            tx_data = {
                'blockTime': getattr(tx_value, 'block_time', None),
                'meta': {
                    'err': None,
                    'fee': 0,
                    'preTokenBalances': [],
                    'postTokenBalances': [],
                    'preBalances': [],
                    'postBalances': [],
                    'logMessages': []
                },
                'transaction': {
                    'message': {
                        'instructions': [],
                        'accountKeys': []
                    }
                }
            }

            # Handle meta data
            if hasattr(tx_value, 'meta') and tx_value.meta:
                tx_data['meta'].update({
                    'err': tx_value.meta.err,
                    'fee': tx_value.meta.fee,
                    'preBalances': tx_value.meta.pre_balances,
                    'postBalances': tx_value.meta.post_balances,
                    'logMessages': tx_value.meta.log_messages if hasattr(tx_value.meta, 'log_messages') else []
                })

                if hasattr(tx_value.meta, 'pre_token_balances'):
                    tx_data['meta']['preTokenBalances'] = [
                        {
                            'accountIndex': b.account_index,
                            'mint': b.mint,
                            'owner': b.owner,
                            'uiTokenAmount': {
                                'amount': str(b.ui_token_amount.amount),
                                'decimals': b.ui_token_amount.decimals,
                                'uiAmount': b.ui_token_amount.ui_amount
                            }
                        } for b in tx_value.meta.pre_token_balances
                    ]
                
                if hasattr(tx_value.meta, 'post_token_balances'):
                    tx_data['meta']['postTokenBalances'] = [
                        {
                            'accountIndex': b.account_index,
                            'mint': b.mint,
                            'owner': b.owner,
                            'uiTokenAmount': {
                                'amount': str(b.ui_token_amount.amount),
                                'decimals': b.ui_token_amount.decimals,
                                'uiAmount': b.ui_token_amount.ui_amount
                            }
                        } for b in tx_value.meta.post_token_balances
                    ]

            # Handle instructions and account keys
            if hasattr(tx_value, 'transaction') and hasattr(tx_value.transaction, 'message'):
                message = tx_value.transaction.message
                tx_data['transaction']['message']['accountKeys'] = [str(key) for key in message.account_keys]
                tx_data['transaction']['message']['instructions'] = [
                    {
                        'programId': str(message.account_keys[ix.program_id_index]),
                        'accounts': [str(message.account_keys[idx]) for idx in ix.accounts],
                        'data': b58encode(ix.data).decode() if ix.data else ''
                    }
                    for ix in message.instructions
                ]

            logger.info("Transaction data extracted successfully")

            # Extract basic information
            timestamp = datetime.fromtimestamp(tx_data['blockTime']) if tx_data.get('blockTime') else None
            status = "Success" if not tx_data['meta'].get('err') else f"Failed: {tx_data['meta']['err']}"
            fee = tx_data['meta'].get('fee', 0)

            # Analyze different aspects of the transaction
            token_transfers = await self.analyze_token_transfers(tx_data)
            dex_swaps = await self.analyze_dex_swaps(tx_data, token_transfers)
            sol_transfers = await self.analyze_sol_transfers(tx_data)

            # Get program IDs and log messages
            program_ids = [ix['programId'] for ix in tx_data['transaction']['message']['instructions']]
            log_messages = tx_data['meta'].get('logMessages', [])

            # Create summary
            summary = TransactionSummary(
                signature=signature,
                timestamp=timestamp,
                status=status,
                fee=fee,
                token_transfers=token_transfers,
                dex_swaps=dex_swaps,
                sol_transfers=sol_transfers,
                program_ids=program_ids,
                log_messages=log_messages,
                raw_data=tx_data
            )

            return summary

        except Exception as e:
            logger.error(f"Error analyzing transaction: {e}")
            return None

async def analyze_interactive():
    """Interactive mode for analyzing multiple transactions"""
    analyzer = TransactionAnalyzer()
    try:
        while True:
            print("\nEnter a transaction signature (or type 'exit' to quit):")
            signature = input().strip()
            
            if signature.lower() == 'exit':
                print("\nExiting analyzer...")
                break
            
            if not signature:
                continue
            
            print(f"\nAnalyzing transaction: {signature}")
            summary = await analyzer.analyze_transaction(signature)
            
            if summary:
                await analyzer.print_analysis(summary)
                # Save analysis to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_{timestamp}.log"
                with open(filename, "w") as f:
                    f.write(f"Transaction Analysis: {signature}\n")
                    f.write("="*80 + "\n")
                    f.write(f"Timestamp: {summary.timestamp}\n")
                    f.write(f"Status: {summary.status}\n")
                    f.write(f"Fee: {summary.fee / 1_000_000_000:.6f} SOL\n\n")
                    if summary.dex_swaps:
                        f.write("DEX Swaps:\n")
                        for swap in summary.dex_swaps:
                            f.write(f"  DEX: {swap.dex_name}\n")
                            if isinstance(swap.input_token, TokenTransfer):
                                f.write(f"  Input: {swap.input_token.formatted_amount} {swap.input_token.token_mint[:8]}...\n")
                            if isinstance(swap.output_token, TokenTransfer):
                                f.write(f"  Output: {swap.output_token.formatted_amount} {swap.output_token.token_mint[:8]}...\n")
                    f.write("\nLog Messages:\n")
                    for msg in summary.log_messages:
                        f.write(f"  {msg}\n")
                print(f"\n✅ Analysis saved to {filename}")
            else:
                print("❌ Could not analyze transaction")
            
    except KeyboardInterrupt:
        print("\nExiting analyzer...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await analyzer.close()

if __name__ == '__main__':
    try:
        print("\n🔍 Solana Transaction Analyzer")
        print("="*80)
        print("• Enter transaction signatures to analyze them")
        print("• Press Ctrl+C or type 'exit' to quit")
        print("="*80 + "\n")
        
        asyncio.run(analyze_interactive())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        sys.exit(0)