#!/usr/bin/env python3
"""
Analyze successful Pump.fun transaction to reverse engineer the correct format
"""

import asyncio
import json
import struct
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature

async def analyze_successful_tx():
    client = AsyncClient('https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315')
    
    # The successful transaction to analyze
    tx_sig = Signature.from_string('d6yAVd6MmxnenfveMG6Ne5siYRMxaKJGsBFPMS7MbEfXWdaBfmrNi2bQkxP79kKcYmbEzW8GW3GGXB4hbXbYSwF')
    
    try:
        print(f'🔍 Analyzing successful transaction: {tx_sig}')
        result = await client.get_transaction(tx_sig, encoding='jsonParsed', max_supported_transaction_version=0)
        
        if result.value:
            tx = result.value
            print(f'✅ Transaction found!')
            
            # Convert to JSON for easier parsing
            tx_json = json.loads(tx.to_json())
            
            # Extract key components
            transaction = tx_json['transaction']
            message = transaction['message']
            accounts = message['accountKeys']
            instructions = message['instructions']
            
            print(f'📋 Total accounts: {len(accounts)}')
            print(f'📋 Total instructions: {len(instructions)}')
            
            # Debug the structure
            print(f'\n🔍 DEBUG: Transaction structure')
            print(f'   Message keys: {list(message.keys()) if isinstance(message, dict) else "Not a dict"}')
            
            if 'instructions' in message:
                instructions = message['instructions']
                print(f'   Instructions type: {type(instructions)}')
                print(f'   Instructions length: {len(instructions)}')
                
                # Check all instructions first
                print(f'\n📋 ALL INSTRUCTIONS:')
                for i, instr in enumerate(instructions):
                    print(f'   [{i}] Instruction type: {type(instr)}')
                    print(f'   [{i}] Instruction keys: {list(instr.keys()) if isinstance(instr, dict) else "Not a dict"}')
                    
                    # Get program ID - jsonParsed format uses 'programId' directly
                    program_id = instr.get('programId') if isinstance(instr, dict) else None
                    if program_id:
                        print(f'   [{i}] Program: {program_id}')
                    else:
                        print(f'   [{i}] No programId found')
                
                # Find Pump.fun instruction
                pump_program = '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'
                
                for i, instr in enumerate(instructions):
                    program_id = instr.get('programId') if isinstance(instr, dict) else None
                    
                    if program_id == pump_program:
                        print(f'\n🎯 PUMP.FUN INSTRUCTION FOUND at index {i}:')
                        print(f'   Program: {program_id}')
                        
                        # Get account indices and addresses
                        acc_indices = instr.get('accounts', [])
                        print(f'   Account count: {len(acc_indices)}')
                        
                        print(f'\n   📋 ACCOUNT ADDRESSES:')
                        for j, addr in enumerate(acc_indices):
                            print(f'     Position {j:2d}: {addr}')
                        
                        # Analyze instruction data
                        data = instr.get('data', '')
                        print(f'\n   📊 INSTRUCTION DATA ANALYSIS:')
                        print(f'   Raw data: {data}')
                        
                        if data:
                            try:
                                # Try base64 decode first (jsonParsed format)
                                import base64
                                data_bytes = base64.b64decode(data)
                                print(f'   Data decoded from base64')
                            except:
                                try:
                                    # Try hex decode (json format)
                                    data_bytes = bytes.fromhex(data)
                                    print(f'   Data decoded from hex')
                                except:
                                    print(f'   ❌ Could not decode data')
                                    data_bytes = None
                            
                            if data_bytes:
                                print(f'   Data length: {len(data_bytes)} bytes')
                                print(f'   Data hex: {data_bytes.hex()}')
                                
                                if len(data_bytes) >= 8:
                                    discriminator = data_bytes[:8].hex()
                                    print(f'   Discriminator: {discriminator}')
                                    
                                    # Check if this matches the expected buy discriminator
                                    expected_buy = '66063d1201daebea'
                                    if discriminator == expected_buy:
                                        print(f'   ✅ CONFIRMED: This is a BUY instruction!')
                                    else:
                                        print(f'   ⚠️  Discriminator mismatch. Expected: {expected_buy}')
                                    
                                    if len(data_bytes) > 8:
                                        payload = data_bytes[8:]
                                        print(f'   Payload: {payload.hex()}')
                                        
                                        if len(payload) >= 16:
                                            # Decode the amount and min_out values
                                            amount, min_out = struct.unpack('<QQ', payload[:16])
                                            print(f'   SOL Amount: {amount} lamports ({amount/1e9:.9f} SOL)')
                                            print(f'   Min tokens out: {min_out}')
                                            
                                            # Calculate slippage
                                            if amount > 0 and min_out > 0:
                                                ratio = min_out / amount
                                                print(f'   Token/SOL ratio: {ratio:.2f}')
                        
                        # Map the accounts to their roles
                        print(f'\n   🏷️  ACCOUNT ROLE MAPPING:')
                        if len(acc_indices) >= 13:  # Standard pump.fun format
                            roles = [
                                'Global account',
                                'Fee recipient', 
                                'Token mint',
                                'Bonding curve',
                                'Associated bonding curve',
                                'User token account',
                                'User wallet (signer)',
                                'System program',
                                'Token program',
                                'Rent sysvar',
                                'Event authority',
                                'Pump.fun program',
                                'Global volume accumulator (optional)'
                            ]
                            
                            for j, (addr, role) in enumerate(zip(acc_indices, roles)):
                                if j < len(roles):
                                    print(f'     {j:2d}. {role}: {addr}')
                        
                        break
            else:
                print('❌ No instructions found in message')
            
            print(f'\n✅ Analysis complete!')
            
        else:
            print('❌ Transaction not found')
            
    except Exception as e:
        print(f'❌ Error analyzing transaction: {e}')
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(analyze_successful_tx())
