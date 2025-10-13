from typing import Dict, Optional, List, Any
import re
import base64
import base58
from solders.pubkey import Pubkey

# Known token program IDs
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
ASSOCIATED_TOKEN_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"

class TokenExtractor:
    @staticmethod
    def extract_token_info_from_logs(logs: List[str]) -> Dict[str, Any]:
        """Extract token information from transaction logs"""
        token_info = {
            "token_in": None,
            "amount_in": None,
            "token_out": None,
            "amount_out": None
        }
        
        # Pattern for base58 encoded public keys
        pubkey_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
        
        for i, log in enumerate(logs):
            # Look for token transfers
            if "Instruction: Transfer" in log or "Instruction: TransferChecked" in log:
                # Look in surrounding logs for token accounts
                surrounding_logs = logs[max(0, i-3):min(len(logs), i+4)]
                for surrounding_log in surrounding_logs:
                    # Find potential token addresses
                    matches = re.findall(pubkey_pattern, surrounding_log)
                    for match in matches:
                        try:
                            # Validate it's a proper base58 address
                            decoded = base58.b58decode(match)
                            if len(decoded) == 32:  # Valid pubkey length
                                # If we don't have token_in yet, set it
                                if not token_info["token_in"]:
                                    token_info["token_in"] = match
                                # If we have token_in but not token_out and this is different
                                elif not token_info["token_out"] and match != token_info["token_in"]:
                                    token_info["token_out"] = match
                        except:
                            continue

            # Look for instruction data that might contain amounts
            if "Program data:" in log:
                try:
                    # Extract and decode program data
                    data = log.split("Program data: ")[1].strip()
                    decoded = base64.b64decode(data)
                    # Amounts are typically 8-byte integers
                    if len(decoded) >= 8:
                        amount = int.from_bytes(decoded[-8:], 'little')
                        if amount > 0:
                            if not token_info["amount_in"]:
                                token_info["amount_in"] = amount
                            elif not token_info["amount_out"]:
                                token_info["amount_out"] = amount
                except:
                    continue

        return token_info

    @staticmethod
    def extract_from_instruction(log: str) -> Optional[str]:
        """Extract token mint from instruction data"""
        try:
            # Look for base58 encoded addresses
            pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
            matches = re.findall(pattern, log)
            
            for match in matches:
                try:
                    # Validate it's a proper pubkey
                    Pubkey.from_string(match)
                    return match
                except:
                    continue
                    
            return None
        except:
            return None

    @staticmethod
    def infer_token_from_accounts(accounts: List[str]) -> Optional[str]:
        """Infer token mint from account list"""
        try:
            # Filter out system accounts
            filtered_accounts = [
                acc for acc in accounts 
                if acc not in [
                    "11111111111111111111111111111111",
                    TOKEN_PROGRAM_ID,
                    ASSOCIATED_TOKEN_PROGRAM_ID
                ]
            ]
            
            # Look for potential token mints
            for account in filtered_accounts:
                try:
                    # Validate it's a proper pubkey
                    Pubkey.from_string(account)
                    return account
                except:
                    continue
                    
            return None
        except:
            return None

class PumpFunExtractor:
    """Specialized extractor for Pump.fun transactions"""
    
    # Pump.fun program IDs
    PUMP_ROUTER = "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW"
    PUMP_CORE = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    
    @staticmethod
    def extract_from_pump_logs(logs: List[str]) -> Dict[str, Any]:
        """Extract token information specifically from Pump.fun transactions"""
        token_info = {
            "token_in": None,
            "amount_in": None,
            "token_out": None,
            "amount_out": None
        }
        
        try:
            # Find the Pump.fun instruction
            pump_indices = []
            for i, log in enumerate(logs):
                if "Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke" in log:
                    pump_indices.append(i)
                    
            if not pump_indices:
                return token_info
                
            # For each Pump.fun instruction block
            for idx in pump_indices:
                # Look at the next few logs after the Pump instruction
                relevant_logs = logs[idx:idx+10]
                instruction_type = None
                
                # Determine if it's a buy or sell
                for log in relevant_logs:
                    if "Instruction: PumpBuy" in log or "Instruction: Buy" in log:
                        instruction_type = "buy"
                        break
                    elif "Instruction: PumpSell" in log or "Instruction: Sell" in log:
                        instruction_type = "sell"
                        break
                
                if not instruction_type:
                    continue
                
                # Look for program data which contains token information
                for log in relevant_logs:
                    if "Program data:" in log:
                        data = log.split("Program data: ")[1].strip()
                        try:
                            decoded = base64.b64decode(data)
                            # Pump.fun instructions typically have token mint at a specific offset
                            if len(decoded) >= 40:  # Minimum length for a valid instruction
                                if instruction_type == "buy":
                                    # For buy, token out is typically at offset 8
                                    potential_token = decoded[8:40]
                                    if len(potential_token) == 32:
                                        token_info["token_out"] = base58.b58encode(potential_token).decode()
                                else:  # sell
                                    # For sell, token in is typically at offset 8
                                    potential_token = decoded[8:40]
                                    if len(potential_token) == 32:
                                        token_info["token_in"] = base58.b58encode(potential_token).decode()
                                
                                # Amount is typically the last 8 bytes
                                amount = int.from_bytes(decoded[-8:], 'little')
                                if amount > 0:
                                    if instruction_type == "buy":
                                        token_info["amount_out"] = amount
                                    else:
                                        token_info["amount_in"] = amount
                        except:
                            continue
                            
        except Exception as e:
            print(f"❌ Error in Pump.fun extraction: {str(e)}")
            
        return token_info

# Update the main parse_program_logs function to use PumpFunExtractor
def parse_program_logs(logs: List[str]) -> Dict[str, Any]:
    """Parse program logs for token information"""
    # First try Pump.fun specific extraction
    pump_extractor = PumpFunExtractor()
    token_info = pump_extractor.extract_from_pump_logs(logs)
    
    # If we couldn't get token info from Pump.fun extraction, try generic extraction
    if not any(token_info.values()):
        generic_extractor = TokenExtractor()
        token_info = generic_extractor.extract_token_info_from_logs(logs)
        
        # If still no token, try to infer from accounts
        if not any(token_info.values()):
            accounts = []
            for log in logs:
                if "Program " in log and " invoke" in log:
                    parts = log.split("Program ")
                    if len(parts) > 1:
                        potential_account = parts[1].split(" ")[0]
                        accounts.append(potential_account)
            
            inferred_token = TokenExtractor.infer_token_from_accounts(accounts)
            if inferred_token:
                token_info["token_in"] = inferred_token
    
    return token_info
