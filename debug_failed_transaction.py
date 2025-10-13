#!/usr/bin/env python3
"""
Debug Failed Transaction Analysis
Analyze why specific transaction BGAXxeYWJroSxbk8dEXj8cmaeaHGbGc2y88o5R5gL6jTgC1mUAxBxvKjdsjf6R9Bvj8f8csAgnyLcsSqGTamQJ2 failed
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from env_keys import EnvKeys

async def analyze_failed_transaction():
    """Analyze the specific failed transaction to identify the issue"""
    
    signature = "BGAXxeYWJroSxbk8dEXj8cmaeaHGbGc2y88o5R5gL6jTgC1mUAxBxvKjdsjf6R9Bvj8f8csAgnyLcsSqGTamQJ2"
    
    print(f"🔍 ANALYZING FAILED TRANSACTION: {signature[:12]}...")
    print(f"🕐 Analysis Time: {datetime.now()}")
    print("=" * 80)
    
    env_keys = EnvKeys()
    
    # Get transaction details with multiple encodings
    encodings = ["json", "jsonParsed"]
    commitments = ["confirmed", "finalized"]
    
    for encoding in encodings:
        for commitment in commitments:
            print(f"\n📡 TRYING: {encoding} encoding with {commitment} commitment")
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    signature,
                    {
                        "encoding": encoding,
                        "commitment": commitment,
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(env_keys.HELIUS_RPC_URL, json=payload) as response:
                        data = await response.json()
                        
                        if 'error' in data:
                            print(f"❌ ERROR: {data['error']}")
                            continue
                        
                        result = data.get('result')
                        if not result:
                            print(f"❌ NO RESULT")
                            continue
                        
                        print(f"✅ SUCCESS with {encoding}/{commitment}")
                        
                        # Analyze transaction structure
                        await analyze_transaction_structure(result, signature)
                        
                        # Check if this was a failed transaction
                        meta = result.get('meta', {})
                        error = meta.get('err')
                        if error:
                            print(f"🚨 TRANSACTION FAILED WITH ERROR:")
                            print(f"   Error: {error}")
                            await analyze_transaction_failure(result, signature)
                        else:
                            print(f"✅ TRANSACTION SUCCEEDED")
                            await analyze_successful_transaction(result, signature)
                        
                        return  # Found working encoding, exit
                        
            except Exception as e:
                print(f"❌ Exception with {encoding}/{commitment}: {e}")
    
    print(f"🚨 CRITICAL: Could not retrieve transaction data with any method")

async def analyze_transaction_structure(result, signature):
    """Analyze the basic structure of the transaction"""
    print(f"\n🏗️ TRANSACTION STRUCTURE ANALYSIS:")
    
    # Basic info
    meta = result.get('meta', {})
    transaction = result.get('transaction', {})
    
    print(f"   📊 Slot: {result.get('slot', 'Unknown')}")
    print(f"   ⛽ Fee: {meta.get('fee', 0)} lamports")
    print(f"   💻 Compute Units: {meta.get('computeUnitsConsumed', 'Unknown')}")
    
    # Check for errors
    error = meta.get('err')
    if error:
        print(f"   ❌ Error: {error}")
    else:
        print(f"   ✅ Status: Success")
    
    # Analyze logs
    logs = meta.get('logMessages', [])
    print(f"   📝 Log Messages: {len(logs)}")
    
    if logs:
        print(f"   🔍 First 10 logs:")
        for i, log in enumerate(logs[:10]):
            print(f"      [{i}] {log}")
    
    # Analyze account keys
    message = transaction.get('message', {})
    account_keys = message.get('accountKeys', [])
    print(f"   🔑 Account Keys: {len(account_keys)}")
    
    # Look for target wallets
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    ]
    
    for wallet in target_wallets:
        if wallet in account_keys:
            wallet_index = account_keys.index(wallet)
            print(f"   🎯 FOUND TARGET WALLET: {wallet[:8]}... at index {wallet_index}")
        else:
            print(f"   ❌ Target wallet {wallet[:8]}... NOT FOUND")

async def analyze_transaction_failure(result, signature):
    """Analyze why the transaction failed"""
    print(f"\n💥 FAILURE ANALYSIS:")
    
    meta = result.get('meta', {})
    error = meta.get('err')
    
    if isinstance(error, dict):
        if 'InstructionError' in error:
            instruction_error = error['InstructionError']
            instruction_index = instruction_error[0] if len(instruction_error) > 0 else "Unknown"
            error_details = instruction_error[1] if len(instruction_error) > 1 else "Unknown"
            
            print(f"   🎯 Instruction Error at index {instruction_index}")
            print(f"   🔍 Error Details: {error_details}")
            
            # Analyze specific error types
            if isinstance(error_details, dict):
                if 'Custom' in error_details:
                    custom_error = error_details['Custom']
                    print(f"   🚨 Custom Error Code: {custom_error}")
                    await decode_custom_error(custom_error)
                elif 'InvalidOwner' in str(error_details) or 'IllegalOwner' in str(error_details):
                    print(f"   🚨 OWNER ERROR DETECTED - This is the ATA issue!")
                    await analyze_ata_issue(result, instruction_index)
            elif isinstance(error_details, str):
                print(f"   🚨 String Error: {error_details}")
        else:
            print(f"   🚨 Other Error Type: {error}")
    else:
        print(f"   🚨 Simple Error: {error}")

async def decode_custom_error(error_code):
    """Decode custom error codes"""
    error_codes = {
        0: "InsufficientFunds",
        1: "InvalidInstruction", 
        2: "InvalidState",
        3: "InvalidOwner",
        4: "NotRentExempt",
        5: "DataTypeMismatch",
        6: "InvalidArgument",
        6002: "ConstraintRaw (Anchor)",
        6003: "ConstraintMut (Anchor)",
        6004: "ConstraintHasOne (Anchor)",
        6005: "ConstraintSigner (Anchor)",
        6006: "ConstraintOwner (Anchor)"
    }
    
    if error_code in error_codes:
        print(f"      📖 Decoded: {error_codes[error_code]}")
    else:
        print(f"      ❓ Unknown custom error code: {error_code}")

async def analyze_ata_issue(result, instruction_index):
    """Analyze ATA (Associated Token Account) related issues"""
    print(f"\n🔧 ATA ISSUE ANALYSIS:")
    
    transaction = result.get('transaction', {})
    message = transaction.get('message', {})
    instructions = message.get('instructions', [])
    
    if instruction_index < len(instructions):
        failed_instruction = instructions[instruction_index]
        program_id_index = failed_instruction.get('programIdIndex')
        account_keys = message.get('accountKeys', [])
        
        if program_id_index < len(account_keys):
            program_id = account_keys[program_id_index]
            print(f"   🎯 Failed Program: {program_id}")
            
            # Check if it's ATA program
            ata_program = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
            if program_id == ata_program:
                print(f"   🚨 CONFIRMED: ATA Program failure!")
                print(f"   🔍 This is the 'IllegalOwner' error we've been fixing")
                
                # Analyze the accounts involved
                accounts = failed_instruction.get('accounts', [])
                print(f"   📋 Accounts involved:")
                for i, account_index in enumerate(accounts):
                    if account_index < len(account_keys):
                        account = account_keys[account_index]
                        print(f"      [{i}] {account}")

async def analyze_successful_transaction(result, signature):
    """Analyze successful transaction to understand what worked"""
    print(f"\n✅ SUCCESS ANALYSIS:")
    
    meta = result.get('meta', {})
    
    # Analyze balance changes
    pre_balances = meta.get('preBalances', [])
    post_balances = meta.get('postBalances', [])
    pre_token_balances = meta.get('preTokenBalances', [])
    post_token_balances = meta.get('postTokenBalances', [])
    
    print(f"   💰 SOL Balance Changes:")
    for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
        if pre != post:
            change = (post - pre) / 1e9
            print(f"      Account {i}: {change:+.6f} SOL")
    
    print(f"   🪙 Token Balance Changes:")
    
    # Track token changes
    token_changes = {}
    
    # Process pre-token balances
    for balance in pre_token_balances:
        account_index = balance.get('accountIndex')
        mint = balance.get('mint')
        amount = float(balance.get('uiTokenAmount', {}).get('uiAmount', 0))
        if mint not in token_changes:
            token_changes[mint] = {'pre': 0, 'post': 0}
        token_changes[mint]['pre'] = amount
    
    # Process post-token balances
    for balance in post_token_balances:
        account_index = balance.get('accountIndex')
        mint = balance.get('mint')
        amount = float(balance.get('uiTokenAmount', {}).get('uiAmount', 0))
        if mint not in token_changes:
            token_changes[mint] = {'pre': 0, 'post': 0}
        token_changes[mint]['post'] = amount
    
    for mint, changes in token_changes.items():
        change = changes['post'] - changes['pre']
        if abs(change) > 0.000001:  # Ignore dust
            print(f"      {mint[:8]}...: {change:+,.6f}")

if __name__ == "__main__":
    asyncio.run(analyze_failed_transaction())
