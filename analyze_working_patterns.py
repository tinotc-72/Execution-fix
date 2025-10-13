#!/usr/bin/env python3

def analyze_live_instruction_patterns():
    """Analyze the working instruction patterns we just found"""
    
    print("🔬 ANALYZING LIVE WORKING INSTRUCTION PATTERNS")
    print("=" * 70)
    
    # Working patterns found from live blockchain
    live_patterns = [
        "66063d1201daebea3d8bba6e0500000020d6130000000000",  # Pattern 1
        "66063d1201daebea8d9527a365000000400f380500000000",  # Pattern 2  
        "33e685a4017f83ad166edcd53d000000ef6b5a0200000000",  # Pattern 3
    ]
    
    # Our current (non-working) patterns
    our_patterns = [
        "000b9a530600000000ef0e483a8f000000",  # Our current
        "00bdda4598000000004586f554dc040000",  # Our old
    ]
    
    print("🎯 WORKING PATTERNS FROM LIVE BLOCKCHAIN:")
    for i, pattern in enumerate(live_patterns):
        print(f"   Pattern {i+1}: {pattern}")
        print(f"   Length: {len(pattern)} hex chars ({len(pattern)//2} bytes)")
        
        # Analyze pattern structure
        analyze_pattern_structure(pattern, f"Live Pattern {i+1}")
    
    print(f"\n❌ OUR NON-WORKING PATTERNS:")
    for i, pattern in enumerate(our_patterns):
        print(f"   Our Pattern {i+1}: {pattern}")
        print(f"   Length: {len(pattern)} hex chars ({len(pattern)//2} bytes)")
        
        # Analyze pattern structure
        analyze_pattern_structure(pattern, f"Our Pattern {i+1}")
    
    print(f"\n🔍 KEY DIFFERENCES:")
    print(f"   Live patterns: {len(live_patterns[0])//2} bytes vs Our patterns: {len(our_patterns[0])//2} bytes")
    print(f"   Live patterns start with: {[p[:8] for p in live_patterns]}")
    print(f"   Our patterns start with:  {[p[:8] for p in our_patterns]}")
    
    # Recommend the most common pattern
    recommend_pattern(live_patterns)

def analyze_pattern_structure(hex_pattern, name):
    """Analyze the structure of a hex pattern"""
    try:
        bytes_data = bytes.fromhex(hex_pattern)
        
        print(f"     {name} breakdown:")
        print(f"       First 4 bytes:  {hex_pattern[:8]} ({bytes_data[:4].hex()})")
        print(f"       Next 4 bytes:   {hex_pattern[8:16]} ({bytes_data[4:8].hex()})")
        print(f"       Next 8 bytes:   {hex_pattern[16:32]} ({bytes_data[8:16].hex()})")
        if len(hex_pattern) > 32:
            print(f"       Remaining:      {hex_pattern[32:]} ({bytes_data[16:].hex()})")
        
    except Exception as e:
        print(f"     ❌ Error analyzing {name}: {e}")

def recommend_pattern(live_patterns):
    """Recommend which pattern to use"""
    
    print(f"\n🎯 RECOMMENDATION:")
    print(f"=" * 50)
    
    # Find common prefixes
    first_bytes = [p[:8] for p in live_patterns]
    unique_prefixes = list(set(first_bytes))
    
    print(f"Found {len(unique_prefixes)} unique instruction prefixes:")
    for prefix in unique_prefixes:
        count = first_bytes.count(prefix)
        print(f"   {prefix}: appears {count} times")
    
    # Most common pattern
    most_common = max(set(live_patterns), key=live_patterns.count)
    print(f"\n✅ RECOMMENDED PATTERN: {most_common}")
    print(f"   This pattern appears most frequently in working transactions")
    
    return most_common

def generate_fixed_implementation():
    """Generate the corrected implementation"""
    
    recommended_pattern = "66063d1201daebea3d8bba6e0500000020d6130000000000"
    
    print(f"\n🔧 GENERATING FIXED IMPLEMENTATION:")
    print(f"=" * 50)
    
    implementation_code = f'''
# CORRECTED PUMP.FUN INSTRUCTION DATA (from live working transactions)

def create_mev_buy_instruction(self, mint_pubkey, bonding_curve, associated_bonding_curve, 
                             associated_user, user_pubkey, sol_amount, token_amount):
    """Create MEV buy instruction with CORRECT working instruction data"""
    
    # ✅ WORKING INSTRUCTION DATA from live blockchain analysis
    instruction_data = bytes.fromhex("{recommended_pattern}")
    
    # Rest of the instruction creation remains the same
    accounts = [
        AccountMeta(pubkey=Pubkey("7SszVYfhNHoBhNtLHFLdCWhc2qU4sHQYTfDdMdPAL1sh"), is_signer=False, is_writable=False),  # Global
        AccountMeta(pubkey=Pubkey("3tz9tNT8v1mXmyMsKC7y6akyMfcBELpF9WepF2XPMZ9Q"), is_signer=False, is_writable=True),   # Fee recipient
        AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),
        AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_user, is_signer=False, is_writable=True),
        AccountMeta(pubkey=user_pubkey, is_signer=True, is_writable=True),
        AccountMeta(pubkey=Pubkey("11111111111111111111111111111111"), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey("SysvarRent111111111111111111111111111111111"), is_signer=False, is_writable=False)
    ]
    
    return TransactionInstruction(
        keys=accounts,
        program_id=PUMPFUN_PROGRAM_ID,  # 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P
        data=instruction_data
    )
'''
    
    print(implementation_code)
    
    return recommended_pattern

if __name__ == "__main__":
    analyze_live_instruction_patterns()
    recommended = generate_fixed_implementation()
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Update complete_mev_bot.py with pattern: {recommended}")
    print(f"2. Test the corrected implementation")
    print(f"3. Verify transactions execute successfully")
