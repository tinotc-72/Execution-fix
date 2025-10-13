#!/usr/bin/env python3
"""
Advanced Solana Transaction Analyzer
Extracts detailed information from any Solana transaction, with special focus on DEX activities
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solders.transaction import Transaction
from base58 import b58decode

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

# Known DEX Program IDs
KNOWN_DEXES = {
    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter",
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium",
    "srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX": "Serum",
    "M2mx93ekt1fmXSVkTrUL9xVFHkmME8HTUi5Cyc5aF7K": "Magic Eden",
}

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

class TransactionAnalyzer:
    """Analyzes Solana transactions with focus on DEX activities"""
    
    def __init__(self):
        self.client = AsyncClient(EnvKeys().HELIUS_RPC_URL)

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

    async def analyze_token_transfers(self, tx_data: Dict[str, Any]) -> List[TokenTransfer]:
        """Extract all token transfers from the transaction"""
        token_transfers = []
        
        if not tx_data.get('meta'):
            return token_transfers

        pre_token_balances = tx_data['meta'].get('preTokenBalances', [])
        post_token_balances = tx_data['meta'].get('postTokenBalances', [])

        # Create lookup tables for pre and post balances
        pre_balances = {(b['mint'], b['owner']): b['uiTokenAmount']['amount'] 
                       for b in pre_token_balances}
        post_balances = {(b['mint'], b['owner']): b['uiTokenAmount']['amount'] 
                        for b in post_token_balances}

        # Find transfers by comparing pre and post balances
        all_mints = set(k[0] for k in pre_balances.keys() | post_balances.keys())
        all_owners = set(k[1] for k in pre_balances.keys() | post_balances.keys())

        for mint in all_mints:
            for owner in all_owners:
                pre_amount = int(pre_balances.get((mint, owner), 0))
                post_amount = int(post_balances.get((mint, owner), 0))
                
                if pre_amount != post_amount:
                    # Get token metadata
                    metadata = await self.get_token_metadata(mint)
                    
                    if pre_amount < post_amount:
                        # This owner received tokens
                        transfer = TokenTransfer(
                            token_mint=mint,
                            from_address="unknown",  # We might be able to determine this from logs
                            to_address=owner,
                            amount=post_amount - pre_amount,
                            decimals=metadata.get('decimals')
                        )
                        token_transfers.append(transfer)
                    else:
                        # This owner sent tokens
                        transfer = TokenTransfer(
                            token_mint=mint,
                            from_address=owner,
                            to_address="unknown",  # We might be able to determine this from logs
                            amount=pre_amount - post_amount,
                            decimals=metadata.get('decimals')
                        )
                        token_transfers.append(transfer)

        return token_transfers

    async def analyze_dex_swaps(self, tx_data: Dict[str, Any], token_transfers: List[TokenTransfer]) -> List[DEXSwap]:
        """Identify and analyze DEX swap operations"""
        dex_swaps = []
        
        if not tx_data.get('transaction') or not tx_data.get('meta'):
            return dex_swaps

        # Get program IDs from instructions
        program_ids = [str(ix['programId']) for ix in tx_data['transaction']['message']['instructions']]
        
        # Look for known DEX program IDs
        for program_id in program_ids:
            if program_id in KNOWN_DEXES:
                dex_name = KNOWN_DEXES[program_id]
                
                # Find input and output tokens by analyzing token transfers
                # Typically, the sender's token decrease is the input
                # and the receiver's token increase is the output
                inputs = [t for t in token_transfers if t.from_address != "unknown"]
                outputs = [t for t in token_transfers if t.to_address != "unknown"]
                
                if inputs and outputs:
                    swap = DEXSwap(
                        dex_name=dex_name,
                        program_id=program_id,
                        input_token=inputs[0],
                        output_token=outputs[0]
                    )
                    dex_swaps.append(swap)
        
        return dex_swaps

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

            # Fetch transaction details
            tx_response = await self.client.get_transaction(sig)
            if not tx_response.value:
                logger.error(f"Transaction not found: {signature}")
                return None

            tx_data = tx_response.value

            # Extract basic information
            timestamp = datetime.fromtimestamp(tx_data['blockTime']) if 'blockTime' in tx_data else None
            status = "Success" if not tx_data['meta'].get('err') else f"Failed: {tx_data['meta']['err']}"
            fee = tx_data['meta'].get('fee', 0)

            # Analyze different aspects of the transaction
            token_transfers = await self.analyze_token_transfers(tx_data)
            dex_swaps = await self.analyze_dex_swaps(tx_data, token_transfers)
            sol_transfers = await self.analyze_sol_transfers(tx_data)

            # Get program IDs and log messages
            program_ids = [str(ix['programId']) for ix in tx_data['transaction']['message']['instructions']]
            log_messages = tx_data['meta'].get('logMessages', []) if tx_data.get('meta') else []

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

    async def print_analysis(self, summary: TransactionSummary):
        """Print transaction analysis in a readable format"""
        print("\n" + "="*80)
        print(f"Transaction Analysis: {summary.signature}")
        print("="*80)
        
        print(f"\n⏰ Timestamp: {summary.timestamp}")
        print(f"📊 Status: {summary.status}")
        print(f"💰 Fee: {summary.fee / 1_000_000_000:.6f} SOL")
        
        if summary.dex_swaps:
            print("\n🔄 DEX Swaps:")
            for swap in summary.dex_swaps:
                print(f"\n  DEX: {swap.dex_name}")
                print(f"  Input: {swap.input_token.formatted_amount} {swap.input_token.token_mint}")
                print(f"  Output: {swap.output_token.formatted_amount} {swap.output_token.token_mint}")
        
        if summary.token_transfers:
            print("\n💎 Token Transfers:")
            for transfer in summary.token_transfers:
                print(f"\n  Token: {transfer.token_mint}")
                print(f"  Amount: {transfer.formatted_amount}")
                print(f"  From: {transfer.from_address}")
                print(f"  To: {transfer.to_address}")
        
        if summary.sol_transfers:
            print("\n📈 SOL Transfers:")
            for transfer in summary.sol_transfers:
                print(f"\n  Address: {transfer['address']}")
                print(f"  Change: {transfer['change']:+.6f} SOL")
        
        print("\n🔧 Programs Used:")
        for program_id in summary.program_ids:
            dex_name = KNOWN_DEXES.get(program_id, "Unknown Program")
            print(f"  • {dex_name} ({program_id})")
        
        print("\n📝 Log Messages:")
        for msg in summary.log_messages:
            if "error" in msg.lower() or "failed" in msg.lower():
                print(f"  ❌ {msg}")
            elif "success" in msg.lower():
                print(f"  ✅ {msg}")
            else:
                print(f"  • {msg}")

    async def close(self):
        """Close the client connection"""
        await self.client.close()

async def analyze_interactive():
    """Interactive mode for analyzing multiple transactions"""
    analyzer = TransactionAnalyzer()
    try:
        print("\n🔍 Solana Transaction Analyzer - Interactive Mode")
        print("="*80)
        print("• Enter a transaction signature to analyze it")
        print("• Press Ctrl+C or type 'exit' to quit")
        print("="*80)

        while True:
            try:
                print("\nPaste transaction signature (or type 'exit' to quit):")
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
                                f.write(f"  Input: {swap.input_token.formatted_amount} {swap.input_token.token_mint}\n")
                                f.write(f"  Output: {swap.output_token.formatted_amount} {swap.output_token.token_mint}\n")
                        f.write("\nLog Messages:\n")
                        for msg in summary.log_messages:
                            f.write(f"  {msg}\n")
                    print(f"\n✅ Analysis saved to {filename}")
                else:
                    print("❌ Could not analyze transaction")
                
            except KeyboardInterrupt:
                print("\nExiting analyzer...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
                
    finally:
        await analyzer.close()

async def main(signature: str = None):
    """Main entry point"""
    if signature:
        # Single transaction mode
        analyzer = TransactionAnalyzer()
        try:
            summary = await analyzer.analyze_transaction(signature)
            if summary:
                await analyzer.print_analysis(summary)
            else:
                logger.error("Could not analyze transaction")
        finally:
            await analyzer.close()
    else:
        # Interactive mode
        await analyze_interactive()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        print("Usage: python transaction_analyzer.py [transaction_signature]")
        print("       If no signature is provided, enters interactive mode")
        sys.exit(1)
    
    signature = sys.argv[1] if len(sys.argv) == 2 else None
    asyncio.run(main(signature))
