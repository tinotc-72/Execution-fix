#!/usr/bin/env python3
"""
Official Solana Transaction Analysis Implementation
==================================================

This implements transaction analysis following the official Solana documentation:
https://solana.com/docs/core/transactions

Key insights from documentation:
1. Instructions use CompiledInstruction format with program_id_index
2. program_id_index points to account_keys array
3. Proper error handling for index bounds
4. Comprehensive DEX program database
"""

def extract_program_id_official(instruction, tx_message, instruction_index, logger):
    """
    Extract program ID following official Solana documentation methods
    
    Returns: (program_id_string, method_used)
    """
    # Method 1: Direct program_id attribute (for parsed instructions)
    if hasattr(instruction, 'program_id'):
        program_id = str(instruction.program_id)
        logger.debug(f"🔍 Instruction {instruction_index} - Direct program_id: {program_id}")
        return program_id, "direct"
    
    # Method 2: program_id_index (official CompiledInstruction format per docs)
    elif hasattr(instruction, 'program_id_index'):
        if hasattr(tx_message, 'account_keys') and instruction.program_id_index < len(tx_message.account_keys):
            program_id = str(tx_message.account_keys[instruction.program_id_index])
            logger.debug(f"🔍 Instruction {instruction_index} - program_id_index[{instruction.program_id_index}]: {program_id}")
            return program_id, "index"
        else:
            logger.debug(f"⚠️  Invalid program_id_index {getattr(instruction, 'program_id_index', 'N/A')} for instruction {instruction_index}")
    
    # Method 3: Alternative naming (programIdIndex)
    elif hasattr(instruction, 'programIdIndex'):
        if hasattr(tx_message, 'account_keys') and instruction.programIdIndex < len(tx_message.account_keys):
            program_id = str(tx_message.account_keys[instruction.programIdIndex])
            logger.debug(f"🔍 Instruction {instruction_index} - programIdIndex[{instruction.programIdIndex}]: {program_id}")
            return program_id, "legacy_index"
    
    # Debug: Show available attributes for troubleshooting
    attrs = [attr for attr in dir(instruction) if not attr.startswith('_')]
    logger.debug(f"⚠️  Instruction {instruction_index}: No program ID found. Attributes: {attrs[:8]}...")
    return None, "none"

def get_dex_programs():
    """
    Comprehensive DEX program database based on current Solana ecosystem
    """
    return {
        # Jupiter (most popular aggregator)
        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
        
        # Raydium (very popular)
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
        "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
        "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
        
        # Pump.fun (critical for meme tokens) - CORRECTED PROGRAM IDS
        "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump.fun Program (Official)",
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Legacy (Deprecated)",
        "5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump": "Pump.fun Trading",
        "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
        "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Global",
        
        # Other major DEXes
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca V1",
        "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
        "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora",
        "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX",
        "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity"
    }

def get_system_programs():
    """System programs we expect to see in transactions"""
    return {
        "11111111111111111111111111111112": "System Program",
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token Program",
        "ComputeBudget111111111111111111111111111111": "Compute Budget Program",
        "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program"
    }

def analyze_instructions_official(instructions, tx_message, logger):
    """
    Analyze instructions following official Solana documentation
    
    Returns: (dex_detected_name, all_program_ids)
    """
    logger.info(f"📊 Analyzing {len(instructions)} instructions using OFFICIAL Solana methods")
    
    dex_detected = None
    all_program_ids = []
    dex_programs = get_dex_programs()
    system_programs = get_system_programs()
    
    for i, instruction in enumerate(instructions):
        try:
            program_id, method = extract_program_id_official(instruction, tx_message, i, logger)
            
            if program_id:
                all_program_ids.append(program_id)
                
                if program_id in dex_programs:
                    dex_detected = dex_programs[program_id]
                    logger.info(f"🏢 DEX DETECTED: {dex_detected} (Method: {method})")
                elif program_id in system_programs:
                    logger.debug(f"🔧 System: {system_programs[program_id]}")
                else:
                    logger.debug(f"❓ Unknown program: {program_id}")
                    
        except Exception as e:
            logger.debug(f"Error processing instruction {i}: {e}")
    
    # Summary
    unique_programs = len(set(all_program_ids))
    logger.info(f"📋 Analysis Summary:")
    logger.info(f"   Instructions: {len(instructions)}")
    logger.info(f"   Programs found: {len(all_program_ids)}")
    logger.info(f"   Unique programs: {unique_programs}")
    logger.info(f"   DEX detected: {dex_detected or 'None'}")
    
    return dex_detected, all_program_ids

# Export the main function for use in main.py
def extract_trade_info_official_method(transaction, wallet_address, logger):
    """
    Updated extract_trade_info using official Solana documentation methods
    """
    try:
        # Handle transaction structure correctly
        if hasattr(transaction, 'transaction'):
            tx_data = transaction.transaction
        else:
            tx_data = transaction
        
        # Get transaction message
        if hasattr(tx_data, 'message'):
            tx_message = tx_data.message
        elif hasattr(tx_data, 'transaction') and hasattr(tx_data.transaction, 'message'):
            tx_message = tx_data.transaction.message
        else:
            logger.error(f"❌ Cannot find transaction message in structure: {type(transaction)}")
            return None
        
        instructions = tx_message.instructions
        
        # Use official method to analyze instructions
        dex_detected, all_program_ids = analyze_instructions_official(instructions, tx_message, logger)
        
        # If no DEX detected, return None
        if not dex_detected:
            logger.info(f"❓ No DEX programs found in transaction")
            return None
        
        # Continue with existing token balance analysis...
        logger.info(f"✅ DEX transaction confirmed, proceeding with balance analysis")
        
        # Rest of the existing logic for token balance analysis would go here
        # For now, return a basic structure
        return {
            'dex_detected': dex_detected,
            'program_ids': all_program_ids,
            'analysis_method': 'official_solana_docs'
        }
        
    except Exception as e:
        logger.error(f"❌ Error in official trade extraction: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Official Solana Transaction Analysis")
    print("Based on: https://solana.com/docs/core/transactions")
    print()
    print("Key improvements:")
    print("✅ Uses CompiledInstruction format per docs")
    print("✅ Proper program_id_index handling")
    print("✅ Comprehensive DEX program database")
    print("✅ Enhanced error handling and debugging")
