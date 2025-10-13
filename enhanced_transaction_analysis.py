#!/usr/bin/env python3
"""
Enhanced Transaction Analysis Fix
================================

Based on official Solana documentation, this fixes the program ID extraction
to properly detect DEX programs in transactions.
"""

def extract_program_id_enhanced(instruction, tx_message, instruction_index):
    """
    Extract program ID using official Solana documentation methods
    
    According to docs, instructions can have:
    1. program_id (direct attribute)
    2. program_id_index (index into account_keys array)  
    3. programIdIndex (alternative naming)
    """
    program_id = None
    
    # Method 1: Direct program_id attribute
    if hasattr(instruction, 'program_id'):
        program_id = str(instruction.program_id)
        print(f"🔍 Method 1 - Direct program_id: {program_id}")
        return program_id
    
    # Method 2: program_id_index (standard per docs)
    if hasattr(instruction, 'program_id_index'):
        if hasattr(tx_message, 'account_keys') and instruction.program_id_index < len(tx_message.account_keys):
            program_id = str(tx_message.account_keys[instruction.program_id_index])
            print(f"🔍 Method 2 - program_id_index {instruction.program_id_index}: {program_id}")
            return program_id
        else:
            print(f"⚠️  Invalid program_id_index: {getattr(instruction, 'program_id_index', 'N/A')}")
    
    # Method 3: programIdIndex (alternative naming)
    if hasattr(instruction, 'programIdIndex'):
        if hasattr(tx_message, 'account_keys') and instruction.programIdIndex < len(tx_message.account_keys):
            program_id = str(tx_message.account_keys[instruction.programIdIndex])
            print(f"🔍 Method 3 - programIdIndex {instruction.programIdIndex}: {program_id}")
            return program_id
    
    # Debug: Show what attributes are available
    attrs = [attr for attr in dir(instruction) if not attr.startswith('_')]
    print(f"⚠️  Instruction {instruction_index} - No program ID found")
    print(f"   Available attributes: {attrs[:10]}...")  # First 10 to avoid spam
    
    return None

# Enhanced DEX program database
DEX_PROGRAMS = {
    # Jupiter (most popular aggregator)
    "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
    "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4", 
    
    # Raydium (very popular)
    "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
    "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
    
    # Pump.fun (critical for meme tokens)
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "Pump.fun Program",
    "5pomUfu4cwBF6ygFuaXRgd4veYCgfSCJFf1AGDg4pump": "Pump.fun Trading",
    "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
    "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Global",
    
    # Other popular DEXes
    "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca V1",
    "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
    "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora",
    "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX",
    "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity"
}

SYSTEM_PROGRAMS = {
    "11111111111111111111111111111112": "System Program",
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "SPL Token Program",
    "ComputeBudget111111111111111111111111111111": "Compute Budget Program",
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL": "Associated Token Program"
}

def analyze_instructions_enhanced(instructions, tx_message):
    """
    Analyze transaction instructions for DEX programs using official methods
    """
    print(f"📊 Analyzing {len(instructions)} instructions using official Solana methods")
    
    dex_detected = None
    all_programs = []
    
    for i, instruction in enumerate(instructions):
        program_id = extract_program_id_enhanced(instruction, tx_message, i)
        
        if program_id:
            all_programs.append(program_id)
            
            if program_id in DEX_PROGRAMS:
                dex_detected = DEX_PROGRAMS[program_id]
                print(f"🏢 DEX operation detected: {dex_detected}")
            elif program_id in SYSTEM_PROGRAMS:
                print(f"🔧 System program: {SYSTEM_PROGRAMS[program_id]}")
            else:
                print(f"❓ Unknown program: {program_id}")
    
    print(f"📋 Summary:")
    print(f"   Total instructions: {len(instructions)}")
    print(f"   Programs found: {len(all_programs)}")
    print(f"   DEX detected: {dex_detected or 'None'}")
    print(f"   Unique programs: {len(set(all_programs))}")
    
    return dex_detected, all_programs

if __name__ == "__main__":
    print("🔧 Enhanced Transaction Analysis based on Official Solana Documentation")
    print("This script provides the proper methods for extracting program IDs from transactions.")
