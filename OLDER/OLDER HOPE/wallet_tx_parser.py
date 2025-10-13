# wallet_tx_parser.py

import json
import logging
import base58
import base64
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, List
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from tx_builder import build_buy_tx, build_sell_tx
from config import WALLET_A_ADDRESS, RPC_URL

# Constants
FIXED_BUY_AMOUNT = 0.05  # Fixed amount in SOL for buys

# Known Programs to watch for
KNOWN_PROGRAMS = {
    "Pump.fun": [
        "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # new router
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # core trading program
    ],
    "Photon": "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi",
    "Meteora": "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi",
    "Raydium": "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C",
    "Jupiter": "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB",
}

class WalletATxParser:
    """Parser for Wallet A's transactions"""
    
    def __init__(self):
        self.wallet_a = Pubkey.from_string(WALLET_A_ADDRESS)
        
    def is_known_program(self, program_id: str) -> Optional[str]:
        """Check if program ID belongs to a known DEX"""
        for platform, ids in KNOWN_PROGRAMS.items():
            if isinstance(ids, list):
                if program_id in ids:
                    return platform
            elif program_id == ids:
                return platform
        return None
    
    def extract_token_from_pump_data(self, data_str: str) -> Optional[str]:
        """Extract token from Pump.fun transaction data using multiple approaches"""
        try:
            # Base64 decode the data
            try:
                decoded = base64.b64decode(data_str)
                logging.debug(f"Data length: {len(decoded)} bytes")
            except:
                logging.debug("Failed to base64 decode data")
                return None

            # Known token address locations in Pump.fun transactions
            token_offsets = [
                72,  # Standard offset (0x48)
                104, # Alternative offset seen in some transactions
                40,  # Offset for newer transaction format
                8   # Minimal offset for direct token references
            ]

            # Try each known offset first
            for offset in token_offsets:
                if offset + 32 <= len(decoded):
                    try:
                        token_bytes = decoded[offset:offset+32]
                        token = str(Pubkey.from_bytes(token_bytes))
                        if token and len(token) == 44:  # Valid base58 Solana address length
                            if token != str(self.wallet_a):  # Skip if it's the wallet address
                                logging.info(f"Found token at offset {offset}: {token}")
                                return token
                    except:
                        continue

            # Advanced scan: look for patterns that might indicate a token address
            # Pump.fun usually has a specific format: instruction (1 byte) + parameters + token
            def is_likely_token_address(pos: int, data: bytes) -> bool:
                """Check if a position in data likely points to a token address"""
                # Check surrounding bytes for common patterns
                if pos >= 4 and data[pos-4:pos] in [b'\x00\x00\x00\x00', b'\x01\x00\x00\x00']:
                    return True
                # Check if preceded by length indicator
                if pos >= 1 and data[pos-1] in [32, 64]:
                    return True
                return False

            # Thorough scan with validation
            for i in range(0, len(decoded) - 31, 8):
                try:
                    if is_likely_token_address(i, decoded):
                        token = str(Pubkey.from_bytes(decoded[i:i+32]))
                        if (token and 
                            len(token) == 44 and  # Valid base58 Solana address length
                            token != str(self.wallet_a)): # Not the wallet address
                            logging.info(f"Found likely token at offset {i}: {token}")
                            return token
                except:
                    continue

            logging.warning("Could not find token in any known location")
            return None

        except Exception as e:
            logging.debug(f"Error in extract_token_from_pump_data: {str(e)}\n{traceback.format_exc()}")
            return None

    def extract_token_from_logs(self, logs: List[str]) -> Optional[str]:
        """Extract token address from transaction logs using multiple strategies"""
        try:
            logging.debug("Starting token extraction from logs...")
            
            # Strategy 1: Direct token mention
            for log in logs:
                # Look for explicit token mentions
                token_indicators = [
                    "Program log: Token:", 
                    "Program log: Mint:", 
                    "Token mint:", 
                    "Target mint:"
                ]
                for indicator in token_indicators:
                    if indicator in log:
                        try:
                            token = log.split(indicator)[1].strip()
                            if token and len(token) == 44:
                                _ = Pubkey.from_string(token)  # Validate address
                                logging.info(f"Found token via direct mention: {token}")
                                return token
                        except:
                            continue

            # Strategy 2: Pump.fun transaction data
            pump_programs = [
                "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # New router
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"   # Core trading
            ]
            
            for prog in pump_programs:
                for i, log in enumerate(logs):
                    if f"Program {prog} invoke" in log:
                        # Search next few logs for data
                        window = min(i + 20, len(logs))
                        for j in range(i, window):
                            if "Program data:" in logs[j] or "Instruction data:" in logs[j]:
                                data = logs[j].split("data:")[1].strip()
                                token = self.extract_token_from_pump_data(data)
                                if token:
                                    return token

            # Strategy 3: ATA initialization
            # This is a reliable method since ATA creation clearly shows the token mint
            token_program = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
            ata_window = 10  # Lines to check around ATA initialization
            
            for i, log in enumerate(logs):
                if f"Program {token_program} invoke" in log:
                    start = max(0, i - ata_window)
                    end = min(len(logs), i + ata_window)
                    
                    # First look for initialization logs
                    for j in range(start, end):
                        if "Initialize the associated token account" in logs[j]:
                            # Then look for the token mint nearby
                            for k in range(start, end):
                                if "Account:" in logs[k] or "Mint:" in logs[k]:
                                    try:
                                        token = logs[k].split(":")[1].strip()
                                        # Validate it's a proper token address
                                        if token and len(token) == 44:
                                            _ = Pubkey.from_string(token)
                                            logging.info(f"Found token in ATA init: {token}")
                                            return token
                                    except:
                                        continue

            # Strategy 4: Account key analysis
            # Look for token accounts in a broader context
            token_indicators = ["Account:", "Mint:", "Token program:", "Transfer:"]
            for i, log in enumerate(logs):
                for indicator in token_indicators:
                    if indicator in log:
                        try:
                            parts = log.split(indicator)
                            if len(parts) > 1:
                                potential_token = parts[1].strip().split()[0]
                                if len(potential_token) == 44:
                                    _ = Pubkey.from_string(potential_token)
                                    if potential_token != str(self.wallet_a):
                                        logging.info(f"Found token via account analysis: {potential_token}")
                                        return potential_token
                        except:
                            continue

            logging.warning("Could not find token in any known location")
            logging.debug("Full logs for analysis:")
            for i, log in enumerate(logs):
                logging.debug(f"[{i}] {log}")
            return None

        except Exception as e:
            logging.error(f"Error extracting token: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    async def parse_transaction(self, tx_data: Dict) -> Optional[Dict]:
        """Parse transaction data from Wallet A with enhanced detection"""
        try:
            # Extract basic info
            tx_value = tx_data.get("value", {})
            logs = tx_value.get("logs", [])
            accounts = tx_value.get("accountKeys", [])
            
            if not logs:
                logging.debug("No logs found in transaction")
                return None
                
            signature = tx_value.get("signature")
            logging.debug(f"Transaction signature: {signature}")
            logging.debug(f"Full transaction data: {json.dumps(tx_value, indent=2)}")
            
            # Verify Wallet A involvement
            found_wallet_a = False
            for log in logs:
                if str(self.wallet_a) in log:
                    found_wallet_a = True
                    logging.debug("✅ Confirmed Wallet A involvement")
                    break
                    
            if not found_wallet_a:
                logging.debug("Transaction does not involve Wallet A")
                return None
            
            # Look for Pump.fun trades with enhanced detection
            pump_fun = False
            pump_type = None
            program_found = False
            
            for log in logs:
                # Check all known Pump.fun programs
                for prog in KNOWN_PROGRAMS["Pump.fun"]:
                    if f"Program {prog} invoke" in log:
                        pump_fun = True
                        program_found = True
                        logging.debug(f"Found Pump.fun program: {prog}")
                        break
                        
                if "Program log: Instruction: PumpBuy" in log:
                    pump_type = "buy"
                    logging.debug("Detected BUY instruction")
                elif "Program log: Instruction: PumpSell" in log:
                    pump_type = "sell"
                    logging.debug("Detected SELL instruction")
                    
                # Also check for alternative instruction formats
                elif "Buy" in log and "Program log: Instruction:" in log:
                    pump_type = "buy"
                    logging.debug("Detected alternative BUY format")
                elif "Sell" in log and "Program log: Instruction:" in log:
                    pump_type = "sell"
                    logging.debug("Detected alternative SELL format")
                    
                if program_found and pump_type:
                    break
                    
            if not pump_fun:
                logging.debug("Not a Pump.fun transaction")
                return None
                
            logging.info("Found Pump.fun transaction")
            
            if not pump_type:
                logging.debug("Could not determine trade type")
                return None
                
            logging.info(f"✅ Detected {pump_type.upper()} trade")
                
            # Extract token with enhanced logging
            logging.debug("Attempting token extraction...")
            token = self.extract_token_from_logs(logs)
            
            if not token:
                logging.debug("First token extraction attempt failed, trying data analysis...")
                # Try extracting from program data if available
                for log in logs:
                    if "Program data:" in log:
                        data = log.split("Program data:")[1].strip()
                        token = self.extract_token_from_pump_data(data)
                        if token:
                            logging.debug("Successfully extracted token from program data")
                            break
                            
            if not token:
                logging.error("Could not extract token address after all attempts")
                logging.debug("Full logs for analysis:")
                for i, log in enumerate(logs):
                    logging.debug(f"[{i}] {log}")
                return None
                
            logging.info("🎯 Trade parsed successfully:")
            logging.info(f"  Type: {pump_type.upper()}")
            logging.info(f"  Token: {token}")
            logging.info(f"  Amount: {'0.05 SOL' if pump_type == 'buy' else 'SELL ALL'}")
                
            return {
                "type": pump_type,
                "token": token,
                "amount": 0.05 if pump_type == "buy" else None,
                "signature": signature
            }
            
        except Exception as e:
            logging.error(f"Error parsing transaction: {str(e)}")
            logging.error(traceback.format_exc())
            return None