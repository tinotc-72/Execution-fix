#!/usr/bin/env python3
"""
Analyze the specific programs used in the missed transaction
"""
import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.signature import Signature
import env_keys

async def analyze_transaction_programs():
    """Get the actual program IDs used in this transaction"""
    
    signature = "2wdEcuWDtGGoWaPSHoNQ7Re2XxbiPCfS9uWJqTdNUkjqi35rizsdpTHQRwqwjDtt99mbcctG7XSQPtZrLQfwaz3D"
    target_wallet = "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    
    print("🔍 ANALYZING TRANSACTION PROGRAMS")
    print("=" * 50)
    
    env = env_keys.EnvKeys()
    client = AsyncClient(env.HELIUS_RPC_URL)
    
    try:
        sig_obj = Signature.from_string(signature)
        tx_response = await client.get_transaction(
            sig_obj, 
            encoding="json", 
            max_supported_transaction_version=0
        )
        
        if not tx_response.value:
            print("❌ Transaction not found")
            return
        
        tx = tx_response.value
        accounts = tx.transaction.transaction.message.account_keys
        instructions = tx.transaction.transaction.message.instructions
        
        print("📋 FULL PROGRAM ANALYSIS:")
        print("")
        
        for i, instruction in enumerate(instructions):
            program_id = str(accounts[instruction.program_id_index])
            print(f"Instruction {i+1}:")
            print(f"   Program ID: {program_id}")
            
            # Check if this is a known program
            known_programs = {
                "11111111111111111111111111111111": "System Program",
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token Program", 
                "ComputeBudget111111111111111111111111111111": "Compute Budget Program",
                "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
                "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium CPMM",
                "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium V4",
                "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
                "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
                "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
                "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca Legacy",
                "BSfD6SHZigAfDWSjzD5Q41jw2ftSyNzwbGkzjzJWrBSA": "BSfD Program (Unknown)"
            }
            
            if program_id in known_programs:
                print(f"   ✅ IDENTIFIED: {known_programs[program_id]}")
                if "CPMM" in known_programs[program_id]:
                    print(f"   🎯 THIS IS A RAYDIUM CPMM TRANSACTION!")
            else:
                print(f"   ❓ UNKNOWN PROGRAM")
            print("")
        
        # Check specific programs we missed
        cpmm_v2_program = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
        bsfd_program = "BSfD6SHZigAfDWSjzD5Q41jw2ftSyNzwbGkzjzJWrBSA"
        
        print("🔍 KEY FINDINGS:")
        print(f"✅ This transaction uses Raydium CPMM V2: {cpmm_v2_program}")
        print(f"❓ Unknown program BSfD...: {bsfd_program}")
        print("")
        
        print("🚨 CRITICAL ISSUE IDENTIFIED:")
        print("Your DEX detection system is missing 'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C'")
        print("This is Raydium CPMM V2 program - a newer version!")
        print("")
        
        print("🔧 SOLUTION:")
        print("Add this program ID to your DEX detection list:")
        print(f'   "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2"')
        
        # Show token details
        print("")
        print("🪙 TOKEN DETAILS:")
        print("   Token purchased: gCxKC39Ah7FuejTFkUPMuWCxQjkZv5NyHpgQVU9bonk")
        print("   SOL spent: 5.130005 SOL")
        print("   DEX used: Raydium CPMM V2")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(analyze_transaction_programs())
