#!/usr/bin/env python3
"""
Analyze specific CLMM transaction to extract correct instruction format
"""

import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.signature import Signature
import json
import base64
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLMMTransactionAnalyzer:
    def __init__(self):
        self.client = AsyncClient("https://mainnet.helius-rpc.com//v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315")
        self.clmm_program = Pubkey.from_string("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK")
        
    async def analyze_transaction(self, signature_str: str):
        """Analyze a specific CLMM transaction"""
        try:
            logger.info(f"📊 Analyzing CLMM transaction: {signature_str}")
            
            # Get transaction details
            signature = Signature.from_string(signature_str)
            response = await self.client.get_transaction(
                signature,
                max_supported_transaction_version=0
            )
            
            if not response.value:
                logger.error(f"Transaction not found: {signature_str}")
                return None
            
            tx = response.value
            
            logger.info(f"✅ Transaction found!")
            logger.info(f"   Slot: {tx.slot}")
            logger.info(f"   Block Time: {tx.block_time}")
            logger.info(f"   Success: {tx.meta.err is None}")
            
            if tx.meta.err:
                logger.error(f"   Error: {tx.meta.err}")
                return None
            
            # Find CLMM instructions
            clmm_instructions = []
            
            if tx.transaction.message.instructions:
                for i, instruction in enumerate(tx.transaction.message.instructions):
                    # Check if this instruction is for CLMM program
                    program_key = tx.transaction.message.account_keys[instruction.program_id_index]
                    
                    if str(program_key) == str(self.clmm_program):
                        logger.info(f"🎯 Found CLMM instruction at index {i}")
                        
                        # Get all account addresses for this instruction
                        instruction_accounts = []
                        for account_index in instruction.accounts:
                            account_key = tx.transaction.message.account_keys[account_index]
                            instruction_accounts.append({
                                'index': account_index,
                                'address': str(account_key),
                                'is_signer': tx.transaction.message.is_signer(account_index),
                                'is_writable': tx.transaction.message.is_writable(account_index)
                            })
                        
                        # Decode instruction data
                        instruction_data = instruction.data
                        
                        clmm_instruction = {
                            'instruction_index': i,
                            'program_id': str(program_key),
                            'data': instruction_data,
                            'data_hex': instruction_data.hex() if instruction_data else None,
                            'data_base64': base64.b64encode(instruction_data).decode() if instruction_data else None,
                            'accounts': instruction_accounts,
                            'account_count': len(instruction_accounts)
                        }
                        
                        clmm_instructions.append(clmm_instruction)
                        
                        # Log detailed instruction info
                        logger.info(f"   Instruction Data (hex): {instruction_data.hex()}")
                        logger.info(f"   Instruction Data (base64): {base64.b64encode(instruction_data).decode()}")
                        logger.info(f"   Account Count: {len(instruction_accounts)}")
                        
                        # Log each account with its role
                        for j, account in enumerate(instruction_accounts):
                            signer_str = "✓" if account['is_signer'] else "✗"
                            writable_str = "✓" if account['is_writable'] else "✗"
                            logger.info(f"   Account {j:2d}: {account['address']} (S:{signer_str} W:{writable_str})")
            
            # Check for other relevant instructions (like compute budget)
            other_instructions = []
            for i, instruction in enumerate(tx.transaction.message.instructions):
                program_key = tx.transaction.message.account_keys[instruction.program_id_index]
                if str(program_key) != str(self.clmm_program):
                    other_instructions.append({
                        'index': i,
                        'program_id': str(program_key),
                        'data_hex': instruction.data.hex(),
                        'account_count': len(instruction.accounts)
                    })
            
            # Extract token information from pre/post balances
            token_info = self.extract_token_info(tx)
            
            analysis_result = {
                'signature': signature_str,
                'slot': tx.slot,
                'block_time': tx.block_time,
                'success': tx.meta.err is None,
                'clmm_instructions': clmm_instructions,
                'other_instructions': other_instructions,
                'token_info': token_info,
                'all_accounts': [str(key) for key in tx.transaction.message.account_keys]
            }
            
            # Save detailed analysis
            with open(f'clmm_transaction_analysis_{signature_str[:16]}.json', 'w') as f:
                json.dump(analysis_result, f, indent=2)
            
            logger.info(f"💾 Analysis saved to: clmm_transaction_analysis_{signature_str[:16]}.json")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing transaction: {e}")
            return None
    
    def extract_token_info(self, tx):
        """Extract token information from transaction"""
        try:
            token_info = {
                'pre_balances': [],
                'post_balances': [],
                'token_balances': []
            }
            
            if hasattr(tx.meta, 'pre_balances') and tx.meta.pre_balances:
                token_info['pre_balances'] = tx.meta.pre_balances
            
            if hasattr(tx.meta, 'post_balances') and tx.meta.post_balances:
                token_info['post_balances'] = tx.meta.post_balances
            
            if hasattr(tx.meta, 'pre_token_balances') and tx.meta.pre_token_balances:
                token_info['pre_token_balances'] = [
                    {
                        'account_index': balance.account_index,
                        'mint': str(balance.mint),
                        'amount': balance.ui_token_amount.amount,
                        'decimals': balance.ui_token_amount.decimals
                    }
                    for balance in tx.meta.pre_token_balances
                ]
            
            if hasattr(tx.meta, 'post_token_balances') and tx.meta.post_token_balances:
                token_info['post_token_balances'] = [
                    {
                        'account_index': balance.account_index,
                        'mint': str(balance.mint),
                        'amount': balance.ui_token_amount.amount,
                        'decimals': balance.ui_token_amount.decimals
                    }
                    for balance in tx.meta.post_token_balances
                ]
            
            return token_info
            
        except Exception as e:
            logger.error(f"Error extracting token info: {e}")
            return {}
    
    async def create_working_template(self, analysis_result):
        """Create a working template based on the analysis"""
        if not analysis_result or not analysis_result['clmm_instructions']:
            logger.error("No CLMM instructions found to create template")
            return None
        
        # Get the first (main) CLMM instruction
        main_instruction = analysis_result['clmm_instructions'][0]
        
        logger.info("📝 Creating working template...")
        
        # Extract key information
        template = {
            'signature': analysis_result['signature'],
            'instruction_data': main_instruction['data_hex'],
            'instruction_data_base64': main_instruction['data_base64'],
            'account_structure': main_instruction['accounts'],
            'total_accounts': main_instruction['account_count'],
            'token_info': analysis_result['token_info']
        }
        
        # Try to identify account roles based on patterns
        accounts = main_instruction['accounts']
        
        # Common patterns for CLMM accounts:
        # 0: User/Payer (signer, writable)
        # 1: AMM Config (not signer, not writable)
        # 2: Pool State (not signer, writable)
        # 3-4: User token accounts (not signer, writable)
        # 5-6: Pool vaults (not signer, writable)
        # 7: Observation state (not signer, writable)
        # 8+: Various program accounts
        
        identified_accounts = {}
        
        for i, account in enumerate(accounts):
            if i == 0 and account['is_signer'] and account['is_writable']:
                identified_accounts['user_payer'] = account['address']
            elif i == 1 and not account['is_signer'] and not account['is_writable']:
                identified_accounts['amm_config'] = account['address']
            elif i == 2 and not account['is_signer'] and account['is_writable']:
                identified_accounts['pool_state'] = account['address']
            elif i in [3, 4] and not account['is_signer'] and account['is_writable']:
                identified_accounts[f'user_token_account_{i-2}'] = account['address']
            elif i in [5, 6] and not account['is_signer'] and account['is_writable']:
                identified_accounts[f'pool_vault_{i-4}'] = account['address']
            elif i == 7 and not account['is_signer'] and account['is_writable']:
                identified_accounts['observation_state'] = account['address']
        
        template['identified_accounts'] = identified_accounts
        
        # Save the template
        with open(f'clmm_working_template_{analysis_result["signature"][:16]}.json', 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"💾 Working template saved: clmm_working_template_{analysis_result['signature'][:16]}.json")
        
        # Print summary
        logger.info("📋 WORKING TEMPLATE SUMMARY:")
        logger.info(f"   Transaction: {analysis_result['signature']}")
        logger.info(f"   Instruction Data: {main_instruction['data_hex']}")
        logger.info(f"   Total Accounts: {main_instruction['account_count']}")
        logger.info(f"   Identified Accounts: {len(identified_accounts)}")
        
        for role, address in identified_accounts.items():
            logger.info(f"     {role}: {address}")
        
        return template
    
    async def run_analysis(self, signature_str: str):
        """Run complete analysis"""
        analysis_result = await self.analyze_transaction(signature_str)
        
        if analysis_result:
            template = await self.create_working_template(analysis_result)
            
            if template:
                logger.info("🎉 Analysis complete! Ready to create working trader.")
                return template
        
        logger.error("❌ Analysis failed")
        return None

async def main():
    analyzer = CLMMTransactionAnalyzer()
    
    # Analyze the provided transaction
    signature = "4ogN4KqA2hpJBNDxqDeBuQkKBeovs17cqb6MqsVQa3dQ88nfMbUSNn7DRQBXDfqh6rQtaaSetECAdf1Xk3nokuJX"
    
    template = await analyzer.run_analysis(signature)
    
    await analyzer.client.close()
    
    return template

if __name__ == "__main__":
    result = asyncio.run(main())
