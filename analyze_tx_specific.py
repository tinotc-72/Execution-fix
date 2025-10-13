#!/usr/bin/env python3
"""
Analyze specific transaction signature
"""

from trading_pattern_analyzer import TradingPatternAnalyzer
import asyncio
import json

async def analyze_transaction():
    analyzer = TradingPatternAnalyzer()
    signature = '3hnCLxeaKRLKP2aYTYLtH6ZHSVFnj7hQaCSQL6Nzpzae6TPmdHzgDuZES5NnXCFXpo1TT5pHataaD5UMMvnJjfCm'
    print(f'🔍 Analyzing transaction: {signature[:30]}...')
    print('=' * 80)
    
    try:
        import httpx
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'getTransaction',
            'params': [
                signature,
                {
                    'encoding': 'json',
                    'maxSupportedTransactionVersion': 0
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(analyzer.rpc_url, json=payload)
            data = response.json()
            
            if 'result' in data and data['result']:
                tx = data['result']
                
                print('✅ Transaction found!')
                print(f'📅 Block Time: {tx.get("blockTime", "Unknown")}')
                print(f'💰 Fee: {tx.get("meta", {}).get("fee", "Unknown")} lamports')
                print(f'✅ Success: {tx.get("meta", {}).get("err") is None}')
                
                # Get account keys
                message = tx.get('transaction', {}).get('message', {})
                account_keys = message.get('accountKeys', [])
                
                print(f'\n🔑 ACCOUNT KEYS ({len(account_keys)}):')
                print('-' * 50)
                
                # Map account keys to known programs
                known_programs = {}
                unknown_programs = []
                for i, account in enumerate(account_keys):
                    program_name = analyzer.programs.get(account, 'Unknown Program')
                    if program_name != 'Unknown Program':
                        known_programs[account] = program_name
                        print(f'{i:2d}. {account} → {program_name}')
                    else:
                        unknown_programs.append((i, account))
                        print(f'{i:2d}. {account}')
                
                if known_programs:
                    print(f'\n🚀 IDENTIFIED PROGRAMS ({len(known_programs)}):')
                    print('-' * 40)
                    for program_id, name in known_programs.items():
                        print(f'🎯 {name}')
                        print(f'   📍 {program_id}')
                
                # Get instructions
                instructions = message.get('instructions', [])
                print(f'\n📝 INSTRUCTIONS ({len(instructions)}):')
                print('-' * 40)
                
                for i, instruction in enumerate(instructions):
                    program_idx = instruction.get('programIdIndex', 0)
                    if program_idx < len(account_keys):
                        program_id = account_keys[program_idx]
                        program_name = analyzer.programs.get(program_id, 'Unknown')
                        accounts_used = instruction.get('accounts', [])
                        print(f'{i+1}. Program: {program_name}')
                        print(f'   ID: {program_id}')
                        print(f'   Accounts: {len(accounts_used)}')
                        print()
                
                # Pattern analysis
                print('🎯 PATTERN COMPARISON WITH YOUR EXECUTORS:')
                print('-' * 50)
                
                # Check for MEV protection
                mev_detected = any('BSfD6SH' in pid or 'Photon' in name or 'MEV' in name for pid, name in known_programs.items())
                if mev_detected:
                    print('✅ MEV Protection: MATCHES your MEV executor approach')
                    mev_programs = [name for pid, name in known_programs.items() if 'BSfD6SH' in pid or 'Photon' in name or 'MEV' in name]
                    for mev in mev_programs:
                        print(f'   🔒 {mev}')
                else:
                    print('❌ MEV Protection: No Photon MEV protection detected')
                
                # Check for pump.fun
                pumpfun_detected = any('6EF8rre' in pid or 'Pump.fun' in name for pid, name in known_programs.items())
                if pumpfun_detected:
                    print('✅ Pump.fun: MATCHES your pump.fun MEV executor')
                else:
                    print('ℹ️  Pump.fun: Not a pump.fun transaction')
                
                # Check for Jupiter
                jupiter_detected = any('JUP' in pid or 'Jupiter' in name for pid, name in known_programs.items())
                if jupiter_detected:
                    print('⚠️  Jupiter: Using aggregator (your direct executors are more reliable)')
                else:
                    print('✅ Direct Execution: No Jupiter aggregator detected')
                
                # Check for Raydium
                raydium_detected = any('Raydium' in name for name in known_programs.values())
                if raydium_detected:
                    print('✅ Raydium: MATCHES your Raydium executor capabilities')
                else:
                    print('ℹ️  Raydium: Not using Raydium DEX')
                
                # Check for LaunchLab
                launchlab_detected = any('LanMV9s' in pid or 'LaunchLab' in name for pid, name in known_programs.items())
                if launchlab_detected:
                    print('✅ LaunchLab: MATCHES your newly integrated LaunchLab support')
                else:
                    print('ℹ️  LaunchLab: Not using LaunchLab variant')
                
                # Summary
                print(f'\n📈 EXECUTION SUMMARY:')
                print('-' * 30)
                print(f'Total Programs: {len(known_programs)} known, {len(unknown_programs)} unknown')
                print(f'Instructions: {len(instructions)}')
                fee_sol = tx.get("meta", {}).get("fee", 0) / 1000000
                print(f'Fee: {fee_sol:.3f} SOL')
                print(f'Success: {"✅" if tx.get("meta", {}).get("err") is None else "❌"}')
                    
            else:
                print('❌ Transaction not found or failed')
                print(f'Response: {data}')
                
    except Exception as e:
        print(f'❌ Error analyzing transaction: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_transaction())
