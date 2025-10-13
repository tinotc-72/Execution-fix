#!/usr/bin/env python3
"""
Comprehensive Transaction Failure Analyzer
Analyzes why a Solana transaction failed given its signature
"""

import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import base64

class TransactionFailureAnalyzer:
    def __init__(self):
        # Load RPC URL from environment or use default
        try:
            from env_keys import get_env_value
            self.rpc_url = get_env_value('HELIUS_RPC_URL')
        except:
            self.rpc_url = "https://api.mainnet-beta.solana.com"
        
        print(f"🔗 Using RPC: {self.rpc_url[:50]}...")
    
    def analyze_transaction_failure(self, signature: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a failed transaction
        """
        print(f"🔍 ANALYZING TRANSACTION FAILURE")
        print(f"📋 Signature: {signature}")
        print("=" * 80)
        
        # Get transaction details with multiple encodings
        transaction_data = self._fetch_transaction_details(signature)
        
        if not transaction_data:
            return {"error": "Could not fetch transaction details"}
        
        analysis = {
            "signature": signature,
            "timestamp": datetime.now().isoformat(),
            "basic_info": self._extract_basic_info(transaction_data),
            "failure_analysis": self._analyze_failure_reasons(transaction_data),
            "program_analysis": self._analyze_programs(transaction_data),
            "account_analysis": self._analyze_accounts(transaction_data),
            "instruction_analysis": self._analyze_instructions(transaction_data),
            "compute_analysis": self._analyze_compute_usage(transaction_data),
            "recommendations": self._generate_recommendations(transaction_data)
        }
        
        self._print_analysis(analysis)
        return analysis
    
    def _fetch_transaction_details(self, signature: str) -> Optional[Dict[str, Any]]:
        """
        Fetch transaction details with multiple encoding attempts
        """
        encodings = ["jsonParsed", "json", "base64"]
        
        for encoding in encodings:
            try:
                print(f"📡 Fetching with {encoding} encoding...")
                
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTransaction",
                    "params": [
                        signature,
                        {
                            "encoding": encoding,
                            "commitment": "confirmed",
                            "maxSupportedTransactionVersion": 0
                        }
                    ]
                }
                
                response = requests.post(self.rpc_url, json=payload, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if "result" in data and data["result"]:
                    print(f"✅ Successfully fetched with {encoding} encoding")
                    return data["result"]
                else:
                    print(f"❌ No result with {encoding} encoding")
                    
            except Exception as e:
                print(f"❌ Error with {encoding} encoding: {str(e)}")
                continue
        
        return None
    
    def _extract_basic_info(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic transaction information"""
        meta = tx_data.get("meta", {})
        
        return {
            "slot": tx_data.get("slot"),
            "block_time": tx_data.get("blockTime"),
            "fee": meta.get("fee"),
            "compute_units_consumed": meta.get("computeUnitsConsumed"),
            "status": meta.get("status"),
            "error": meta.get("err"),
            "num_instructions": len(tx_data.get("transaction", {}).get("message", {}).get("instructions", [])),
            "num_accounts": len(tx_data.get("transaction", {}).get("message", {}).get("accountKeys", []))
        }
    
    def _analyze_failure_reasons(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the specific failure reasons"""
        meta = tx_data.get("meta", {})
        error = meta.get("err")
        
        analysis = {
            "failed": error is not None,
            "error_type": None,
            "error_details": None,
            "common_causes": [],
            "specific_analysis": None
        }
        
        if error:
            if isinstance(error, dict):
                if "InstructionError" in error:
                    instruction_error = error["InstructionError"]
                    analysis["error_type"] = "InstructionError"
                    analysis["error_details"] = instruction_error
                    analysis["specific_analysis"] = self._analyze_instruction_error(instruction_error)
                elif "InsufficientFundsForRent" in error:
                    analysis["error_type"] = "InsufficientFundsForRent"
                    analysis["common_causes"] = ["Not enough SOL for rent", "Account creation failed"]
                elif "AccountNotFound" in error:
                    analysis["error_type"] = "AccountNotFound"
                    analysis["common_causes"] = ["Account doesn't exist", "Wrong account address"]
                else:
                    analysis["error_type"] = str(error)
            else:
                analysis["error_type"] = str(error)
        
        return analysis
    
    def _analyze_instruction_error(self, instruction_error) -> Dict[str, Any]:
        """Analyze specific instruction errors"""
        if len(instruction_error) >= 2:
            instruction_index = instruction_error[0]
            error_detail = instruction_error[1]
            
            analysis = {
                "failed_instruction_index": instruction_index,
                "error_detail": error_detail
            }
            
            if isinstance(error_detail, dict):
                if "Custom" in error_detail:
                    analysis["custom_error_code"] = error_detail["Custom"]
                    analysis["interpretation"] = self._interpret_custom_error(error_detail["Custom"])
                elif "InsufficientFunds" in error_detail:
                    analysis["interpretation"] = "Insufficient funds for the operation"
                elif "InvalidAccountData" in error_detail:
                    analysis["interpretation"] = "Account data is invalid or corrupted"
                elif "AccountNotInitialized" in error_detail:
                    analysis["interpretation"] = "Account exists but is not properly initialized"
                elif "AccountAlreadyInitialized" in error_detail:
                    analysis["interpretation"] = "Trying to initialize an already initialized account"
            
            return analysis
        
        return {"error": "Could not parse instruction error"}
    
    def _interpret_custom_error(self, error_code: int) -> str:
        """Interpret common custom error codes"""
        common_errors = {
            0: "Generic error",
            1: "Invalid instruction",
            2: "Invalid account",
            3: "Invalid program id",
            6001: "Insufficient funds",
            6002: "Invalid mint",
            6003: "Invalid token account",
            6004: "Invalid authority",
            6005: "Invalid owner",
            6006: "Invalid delegate",
            6007: "Invalid state",
            6008: "Invalid instruction data",
            6009: "Invalid account data",
            6010: "Insufficient lamports",
            6011: "Insufficient tokens"
        }
        
        return common_errors.get(error_code, f"Custom error code {error_code}")
    
    def _analyze_programs(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze programs involved in the transaction"""
        message = tx_data.get("transaction", {}).get("message", {})
        instructions = message.get("instructions", [])
        account_keys = message.get("accountKeys", [])
        
        programs = set()
        
        for instruction in instructions:
            program_id_index = instruction.get("programIdIndex")
            if program_id_index is not None and program_id_index < len(account_keys):
                program_id = account_keys[program_id_index]
                programs.add(program_id)
        
        program_names = {}
        for program_id in programs:
            program_names[program_id] = self._identify_program(program_id)
        
        return {
            "programs_involved": list(programs),
            "program_names": program_names,
            "total_programs": len(programs)
        }
    
    def _identify_program(self, program_id: str) -> str:
        """Identify well-known program IDs"""
        known_programs = {
            "11111111111111111111111111111111": "System Program",
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program",
            "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program",
            "ComputeBudget111111111111111111111111111111": "Compute Budget Program",
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium AMM",
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Raydium CLMM",
            "cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG": "Raydium CPMM",
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
            "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump.fun",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
            "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin": "Serum DEX V3"
        }
        
        return known_programs.get(program_id, f"Unknown Program ({program_id[:8]}...)")
    
    def _analyze_accounts(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze accounts involved in the transaction"""
        meta = tx_data.get("meta", {})
        message = tx_data.get("transaction", {}).get("message", {})
        
        pre_balances = meta.get("preBalances", [])
        post_balances = meta.get("postBalances", [])
        account_keys = message.get("accountKeys", [])
        
        balance_changes = []
        for i, account in enumerate(account_keys):
            if i < len(pre_balances) and i < len(post_balances):
                change = post_balances[i] - pre_balances[i]
                if change != 0:
                    balance_changes.append({
                        "account": account,
                        "pre_balance": pre_balances[i],
                        "post_balance": post_balances[i],
                        "change": change,
                        "change_sol": change / 1e9
                    })
        
        return {
            "total_accounts": len(account_keys),
            "balance_changes": balance_changes,
            "accounts_with_changes": len(balance_changes)
        }
    
    def _analyze_instructions(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the instructions in the transaction"""
        message = tx_data.get("transaction", {}).get("message", {})
        instructions = message.get("instructions", [])
        
        instruction_analysis = []
        for i, instruction in enumerate(instructions):
            analysis = {
                "index": i,
                "program_id_index": instruction.get("programIdIndex"),
                "accounts": instruction.get("accounts", []),
                "data_length": len(instruction.get("data", "")),
                "num_accounts": len(instruction.get("accounts", []))
            }
            instruction_analysis.append(analysis)
        
        return {
            "total_instructions": len(instructions),
            "instruction_details": instruction_analysis
        }
    
    def _analyze_compute_usage(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compute unit usage"""
        meta = tx_data.get("meta", {})
        
        return {
            "compute_units_consumed": meta.get("computeUnitsConsumed"),
            "fee": meta.get("fee"),
            "fee_sol": meta.get("fee", 0) / 1e9 if meta.get("fee") else None
        }
    
    def _generate_recommendations(self, tx_data: Dict[str, Any]) -> list:
        """Generate recommendations based on the failure analysis"""
        recommendations = []
        meta = tx_data.get("meta", {})
        error = meta.get("err")
        
        if error:
            if isinstance(error, dict):
                if "InstructionError" in error:
                    recommendations.append("Check the specific instruction that failed")
                    recommendations.append("Verify all account addresses are correct")
                    recommendations.append("Ensure all accounts are properly initialized")
                    
                if "InsufficientFunds" in str(error):
                    recommendations.append("Add more SOL to your wallet")
                    recommendations.append("Check minimum balance requirements")
                    
                if "AccountNotInitialized" in str(error):
                    recommendations.append("Initialize the account before using it")
                    recommendations.append("Check if ATA needs to be created first")
                    
                if "InvalidAccountData" in str(error):
                    recommendations.append("Verify account data format")
                    recommendations.append("Check account ownership")
        
        # General recommendations
        recommendations.append("Test with smaller amounts first")
        recommendations.append("Check transaction simulation before sending")
        recommendations.append("Verify all program IDs are correct")
        
        return recommendations
    
    def _print_analysis(self, analysis: Dict[str, Any]):
        """Print formatted analysis results"""
        print("\n🔍 TRANSACTION FAILURE ANALYSIS RESULTS")
        print("=" * 80)
        
        # Basic Info
        basic = analysis["basic_info"]
        print(f"📊 BASIC INFORMATION:")
        print(f"   Slot: {basic.get('slot')}")
        print(f"   Fee: {basic.get('fee')} lamports ({basic.get('fee', 0) / 1e9:.6f} SOL)")
        print(f"   Compute Units: {basic.get('compute_units_consumed')}")
        print(f"   Instructions: {basic.get('num_instructions')}")
        print(f"   Accounts: {basic.get('num_accounts')}")
        print()
        
        # Failure Analysis
        failure = analysis["failure_analysis"]
        print(f"❌ FAILURE ANALYSIS:")
        print(f"   Failed: {failure.get('failed')}")
        print(f"   Error Type: {failure.get('error_type')}")
        if failure.get("error_details"):
            print(f"   Error Details: {failure.get('error_details')}")
        if failure.get("specific_analysis"):
            spec = failure["specific_analysis"]
            print(f"   Failed Instruction: #{spec.get('failed_instruction_index')}")
            print(f"   Interpretation: {spec.get('interpretation')}")
        print()
        
        # Programs
        programs = analysis["program_analysis"]
        print(f"🏛️ PROGRAMS INVOLVED:")
        for program_id, name in programs["program_names"].items():
            print(f"   {name}: {program_id}")
        print()
        
        # Recommendations
        print(f"💡 RECOMMENDATIONS:")
        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"   {i}. {rec}")
        print()

def main():
    analyzer = TransactionFailureAnalyzer()
    
    print("🔍 Transaction Failure Analyzer")
    print("=" * 50)
    print("Enter a transaction signature to analyze why it failed.")
    print("Press Ctrl+C to exit.")
    print()
    
    while True:
        try:
            signature = input("📋 Enter transaction signature: ").strip()
            
            if not signature:
                print("❌ Please enter a valid signature")
                continue
            
            if len(signature) < 80:
                print("❌ Signature seems too short")
                continue
            
            print(f"\n🔍 Analyzing transaction: {signature}")
            print("-" * 80)
            
            analysis = analyzer.analyze_transaction_failure(signature)
            
            # Save analysis to file
            filename = f"tx_failure_analysis_{signature[:8]}.json"
            with open(filename, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            
            print(f"💾 Analysis saved to: {filename}")
            print("\n" + "=" * 80)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
