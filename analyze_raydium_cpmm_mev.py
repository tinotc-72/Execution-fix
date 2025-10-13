#!/usr/bin/env python3
"""
🔍 RAYDIUM CPMM MEV REVERSE ENGINEERING
=====================================

Deep analysis of Raydium CPMM transactions:
- Signature 1: 5jcK7HKWSeFjE3yTooNgLGk9gLFgCvbArijESXTyFSDR2PvduoNHkWjywmUdPmMDXxg3s5wxu9uY1xLCoXWA4qtF
- Signature 2: 2vp3rSv5CLUtwjfodi3CEysxDyD7H8hJQU8RUk5zK8dk4zFdbd2j9iHH2e3JdEmXBUYSH3h7PbV97y6Dkvrrseoh

Key Program: CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C (Raydium CPMM)
Instruction: SwapBaseInput

Goal: Reverse engineer the execution method and create Raydium MEV executor for copy bot integration
"""

import asyncio
import json
import logging
import base64
import struct
from datetime import datetime
from typing import Dict, Any, Optional, List
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RaydiumCPMMAnalyzer:
    """Reverse engineer Raydium CPMM execution patterns"""
    
    def __init__(self):
        self.env_keys = None
        
        # Target Raydium CPMM transactions
        self.signatures = [
            "5jcK7HKWSeFjE3yTooNgLGk9gLFgCvbArijESXTyFSDR2PvduoNHkWjywmUdPmMDXxg3s5wxu9uY1xLCoXWA4qtF",
            "2vp3rSv5CLUtwjfodi3CEysxDyD7H8hJQU8RUk5zK8dk4zFdbd2j9iHH2e3JdEmXBUYSH3h7PbV97y6Dkvrrseoh"
        ]
        
        # Key Raydium CPMM program
        self.raydium_cpmm_program = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
        
        # Initialize RPC
        try:
            from env_keys import EnvKeys
            self.env_keys = EnvKeys()
            logger.info("✅ RPC configuration loaded")
        except ImportError:
            logger.error("❌ env_keys not available")
            
    async def analyze_transaction_details(self, signature: str) -> Dict[str, Any]:
        """Get detailed transaction information"""
        logger.info(f"🔍 Analyzing transaction: {signature[:16]}...")
        
        if not self.env_keys:
            return {"error": "No RPC configuration"}
        
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
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.env_keys.HELIUS_RPC_URL, json=payload)
                data = response.json()
                
                if 'error' in data:
                    logger.error(f"❌ RPC Error: {data['error']}")
                    return {"error": data['error']}
                
                if not data.get('result'):
                    logger.error("❌ Transaction not found")
                    return {"error": "Transaction not found"}
                
                return data['result']
                
            except Exception as e:
                logger.error(f"❌ Error fetching transaction: {e}")
                return {"error": str(e)}
    
    def analyze_instruction_data(self, instruction: Dict, account_keys: List) -> Dict[str, Any]:
        """Analyze Raydium CPMM instruction data structure"""
        try:
            program_id_index = instruction.get('programIdIndex', 0)
            program_id = account_keys[program_id_index] if program_id_index < len(account_keys) else "unknown"
            
            if program_id != self.raydium_cpmm_program:
                return {"type": "non_raydium", "details": f"Not a Raydium CPMM instruction (program: {program_id})"}
            
            data = instruction.get('data', '')
            if not data:
                return {"type": "no_data", "details": "No instruction data"}
            
            # Decode base58 data
            try:
                decoded_data = base64.b64decode(data)
                logger.info(f"📊 Instruction data length: {len(decoded_data)} bytes")
                logger.info(f"📊 First 32 bytes (hex): {decoded_data[:32].hex()}")
                
                # Check for SwapBaseInput discriminator
                if len(decoded_data) >= 4:
                    discriminator = decoded_data[:4]
                    logger.info(f"🎯 Instruction discriminator: {discriminator.hex()}")
                    
                    # Analyze the rest of the data
                    if len(decoded_data) >= 8:
                        # Try to parse as SwapBaseInput parameters
                        try:
                            amount_in = struct.unpack('<Q', decoded_data[4:12])[0] if len(decoded_data) >= 12 else 0
                            min_amount_out = struct.unpack('<Q', decoded_data[12:20])[0] if len(decoded_data) >= 20 else 0
                            
                            return {
                                "type": "SwapBaseInput",
                                "discriminator": discriminator.hex(),
                                "amount_in": amount_in,
                                "min_amount_out": min_amount_out,
                                "total_data_length": len(decoded_data),
                                "details": f"Swap {amount_in} for minimum {min_amount_out}"
                            }
                        except struct.error as e:
                            logger.warning(f"⚠️ Error parsing swap parameters: {e}")
                
                return {
                    "type": "raydium_cpmm_unknown",
                    "discriminator": discriminator.hex() if len(decoded_data) >= 4 else "none",
                    "data_length": len(decoded_data),
                    "details": "Raydium CPMM instruction with unknown format"
                }
                
            except Exception as e:
                logger.error(f"❌ Error decoding instruction data: {e}")
                return {"type": "decode_error", "details": str(e)}
                
        except Exception as e:
            logger.error(f"❌ Error analyzing instruction: {e}")
            return {"type": "analysis_error", "details": str(e)}
    
    def extract_accounts_pattern(self, instruction: Dict) -> Dict[str, Any]:
        """Extract account pattern for Raydium CPMM instructions"""
        try:
            accounts = instruction.get('accounts', [])
            account_count = len(accounts)
            
            logger.info(f"📋 Account count: {account_count}")
            
            # Log account roles based on typical Raydium CPMM pattern
            account_roles = []
            for i, account_idx in enumerate(accounts):
                if i == 0:
                    account_roles.append(f"[{i}] User/Payer (index {account_idx})")
                elif i == 1:
                    account_roles.append(f"[{i}] User source token account (index {account_idx})")
                elif i == 2:
                    account_roles.append(f"[{i}] User destination token account (index {account_idx})")
                elif i == 3:
                    account_roles.append(f"[{i}] Pool state (index {account_idx})")
                elif i == 4:
                    account_roles.append(f"[{i}] AMM authority (index {account_idx})")
                elif i == 5:
                    account_roles.append(f"[{i}] Pool source token vault (index {account_idx})")
                elif i == 6:
                    account_roles.append(f"[{i}] Pool destination token vault (index {account_idx})")
                else:
                    account_roles.append(f"[{i}] Additional account (index {account_idx})")
            
            return {
                "account_count": account_count,
                "account_pattern": account_roles,
                "accounts": accounts
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting account pattern: {e}")
            return {"error": str(e)}
    
    async def reverse_engineer_execution_flow(self, signature: str) -> Dict[str, Any]:
        """Reverse engineer the complete execution flow"""
        logger.info(f"🔧 Reverse engineering execution flow for {signature[:16]}...")
        
        tx_data = await self.analyze_transaction_details(signature)
        if 'error' in tx_data:
            return tx_data
        
        # Extract key information
        transaction = tx_data.get('transaction', {})
        meta = tx_data.get('meta', {})
        
        # Analyze instructions
        instructions = transaction.get('message', {}).get('instructions', [])
        raydium_instructions = []
        
        execution_pattern = {
            "signature": signature,
            "slot": tx_data.get('slot'),
            "success": meta.get('err') is None,
            "fee": meta.get('fee', 0),
            "compute_units_consumed": meta.get('computeUnitsConsumed', 0),
            "total_instructions": len(instructions),
            "raydium_instructions": [],
            "instruction_flow": []
        }
        
        for i, instruction in enumerate(instructions):
            account_keys = transaction.get('message', {}).get('accountKeys', [])
            program_id_index = instruction.get('programIdIndex', 0)
            program_id = account_keys[program_id_index] if program_id_index < len(account_keys) else "unknown"
            
            if program_id == self.raydium_cpmm_program:
                # This is a Raydium CPMM instruction
                instruction_analysis = self.analyze_instruction_data(instruction, account_keys)
                account_pattern = self.extract_accounts_pattern(instruction)
                
                raydium_instruction = {
                    "instruction_index": i,
                    "program_id": program_id,
                    "instruction_data": instruction_analysis,
                    "account_pattern": account_pattern
                }
                
                execution_pattern["raydium_instructions"].append(raydium_instruction)
                execution_pattern["instruction_flow"].append(f"[{i}] Raydium CPMM: {instruction_analysis.get('type', 'unknown')}")
                
                logger.info(f"🎯 Raydium instruction [{i}]: {instruction_analysis.get('type', 'unknown')}")
                
            else:
                # Other instruction
                execution_pattern["instruction_flow"].append(f"[{i}] {program_id}")
        
        return execution_pattern
    
    async def analyze_all_transactions(self) -> Dict[str, Any]:
        """Analyze all target Raydium CPMM transactions"""
        logger.info("🚀 Starting comprehensive Raydium CPMM analysis...")
        
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "target_program": self.raydium_cpmm_program,
            "transactions_analyzed": len(self.signatures),
            "individual_analysis": [],
            "common_patterns": {},
            "mev_executor_blueprint": {}
        }
        
        for signature in self.signatures:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 ANALYZING: {signature}")
            logger.info(f"{'='*60}")
            
            execution_flow = await self.reverse_engineer_execution_flow(signature)
            analysis_results["individual_analysis"].append(execution_flow)
            
            # Print key findings
            if 'error' not in execution_flow:
                logger.info(f"✅ Transaction successful: {execution_flow['success']}")
                logger.info(f"💰 Fee: {execution_flow['fee'] / 1_000_000_000:.9f} SOL")
                logger.info(f"⚡ Compute units: {execution_flow['compute_units_consumed']:,}")
                logger.info(f"📋 Total instructions: {execution_flow['total_instructions']}")
                logger.info(f"🎯 Raydium instructions: {len(execution_flow['raydium_instructions'])}")
                
                for raydium_inst in execution_flow['raydium_instructions']:
                    data = raydium_inst['instruction_data']
                    accounts = raydium_inst['account_pattern']
                    logger.info(f"   • Type: {data.get('type', 'unknown')}")
                    logger.info(f"   • Accounts: {accounts.get('account_count', 0)}")
                    if 'amount_in' in data:
                        logger.info(f"   • Amount in: {data['amount_in']}")
                        logger.info(f"   • Min out: {data['min_amount_out']}")
        
        # Extract common patterns for MEV executor
        self.extract_mev_patterns(analysis_results)
        
        # Save results
        filename = f"raydium_cpmm_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        logger.info(f"\n📁 Analysis saved to: {filename}")
        return analysis_results
    
    def extract_mev_patterns(self, analysis_results: Dict[str, Any]):
        """Extract patterns for MEV executor implementation"""
        logger.info("🔧 Extracting MEV executor patterns...")
        
        successful_transactions = [
            tx for tx in analysis_results["individual_analysis"] 
            if 'error' not in tx and tx.get('success', False)
        ]
        
        if not successful_transactions:
            logger.warning("⚠️ No successful transactions to analyze")
            return
        
        # Extract common instruction patterns
        instruction_patterns = []
        compute_unit_usage = []
        fee_patterns = []
        
        for tx in successful_transactions:
            instruction_patterns.append(tx["instruction_flow"])
            compute_unit_usage.append(tx["compute_units_consumed"])
            fee_patterns.append(tx["fee"])
        
        # Calculate recommendations
        avg_compute_units = sum(compute_unit_usage) / len(compute_unit_usage)
        avg_fee = sum(fee_patterns) / len(fee_patterns)
        
        mev_blueprint = {
            "recommended_compute_limit": int(avg_compute_units * 1.5),  # 50% buffer
            "recommended_priority_fee": int(avg_fee * 2),  # 2x for MEV speed
            "instruction_pattern": instruction_patterns[0] if instruction_patterns else [],
            "account_structure": [],
            "implementation_notes": [
                "Use SwapBaseInput instruction for Raydium CPMM",
                f"Set compute limit to {int(avg_compute_units * 1.5):,} units",
                f"Use priority fee of {int(avg_fee * 2):,} micro-lamports for MEV",
                "Implement proper account ordering as per transaction analysis",
                "Handle slippage with min_amount_out parameter"
            ]
        }
        
        # Extract account patterns from first successful Raydium instruction
        for tx in successful_transactions:
            if tx["raydium_instructions"]:
                first_raydium = tx["raydium_instructions"][0]
                mev_blueprint["account_structure"] = first_raydium["account_pattern"]["account_pattern"]
                break
        
        analysis_results["mev_executor_blueprint"] = mev_blueprint
        
        logger.info("✅ MEV patterns extracted:")
        logger.info(f"   • Recommended compute limit: {mev_blueprint['recommended_compute_limit']:,}")
        logger.info(f"   • Recommended priority fee: {mev_blueprint['recommended_priority_fee']:,}")
        logger.info(f"   • Account pattern: {len(mev_blueprint['account_structure'])} accounts")

async def main():
    """Main analysis function"""
    print("🔍 RAYDIUM CPMM MEV REVERSE ENGINEERING")
    print("=" * 50)
    
    analyzer = RaydiumCPMMAnalyzer()
    
    try:
        results = await analyzer.analyze_all_transactions()
        
        print("\n🎉 ANALYSIS COMPLETE!")
        print(f"📊 Transactions analyzed: {results['transactions_analyzed']}")
        print(f"✅ Successful analyses: {len([tx for tx in results['individual_analysis'] if 'error' not in tx])}")
        
        blueprint = results.get("mev_executor_blueprint", {})
        if blueprint:
            print("\n🚀 MEV EXECUTOR RECOMMENDATIONS:")
            for note in blueprint.get("implementation_notes", []):
                print(f"   • {note}")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
