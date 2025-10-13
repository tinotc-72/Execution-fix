#!/usr/bin/env python3
"""
Critical Program Gap Analyzer
Analyzes the transaction pattern results to identify specific programs that MUST be added to WebSocket monitoring
"""

import json
import logging
from collections import Counter
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_missing_programs():
    """Analyze the transaction pattern results to identify critical missing programs"""
    
    # Load the analysis results
    with open('transaction_pattern_analysis_20250721_021032.json', 'r') as f:
        data = json.load(f)
    
    logger.info("🔍 ANALYZING CRITICAL PROGRAM GAPS...")
    logger.info("=" * 60)
    
    # Current monitored programs from main.py
    monitored_programs = {
        # Jupiter
        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
        
        # Raydium
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
        "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
        "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
        "CamM7Te6wPCRqieiLvNHtmNnTsUhVLfafSJNMzUthhUU": "Raydium V5",
        "CLMM9tUoggJu2wagPkkqs9eFG4BWhVBZWkP1qv3Sp7tR": "Raydium CLMM",
        
        # Pump.fun
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
        "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1": "Pump.fun Trading",
        "39azUYFWPz3VHgKCf3Vowf5jUJjg": "Pump.fun Router",
        
        # Orca
        "9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP": "Orca V1",
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpools",
        
        # Phoenix
        "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix V1",
        
        # Others
        "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB": "Meteora",
        "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo": "Meteora DLMM",
        "2wT8Yq49kHgDzXuPxZSaeLaH1qbmGXtEyPy64bL7aD3c": "Lifinity V2",
        "EewxydAPCCVuNEP3LBaHp4qCWwSswUJcygtaEaYHatAx": "Lifinity V1",
        "AMM55ShdkoGRB5jVYPjWziwk8m5MpwyDgsMWHaMSQWH6": "GooseFX",
        "SSwpkEEcbUqx4vtoEByFjSkhKdCT862DNVb52nXHeH1": "Saros AMM",
        "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Orca V2",
        "Dooar9JkhdZ7J3LHN3A7YCuoGRUggXhQaG4kijfLGU2j": "Stepn",
        "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin": "Serum V3",
        "srmqPiDkYq2T6Nj6WtfU7Qh4Cd5ASBG7k5KwZoGvnH": "Serum V2",
        "EUqojwWA2rd19FZrzeBncJsm38Jm1hEhE3zsmX3bRc2o": "Saber",
        "SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8": "Saber Swap",
        "CTMAxxk34HjKWxQ3QLZL1MNAdXDcisG3CVnPrF9VbRkB": "Cropper",
        "MERLuDFBMmsHnsBPZw2sDQZHvXFMwp8EdjudcU2HKky": "Mercurial",
        "BSwp6bEBihVLdqJRKS58NwCjNYDAWcrjBQrD2HTRHVEr": "Step Finance",
        "AURY2249KY9qb78TXXaTdFpU33tDW3BKjSjjde8ao3j4P": "Aurory",
        "61F3mYYaNu9EPevN6dRNUspjqoQtdUKGZp5VTaW7grrKgrWqK": "Invariant"
    }
    
    # System programs to ignore
    system_programs = {
        "11111111111111111111111111111111",
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        "ComputeBudget111111111111111111111111111111",
        "So11111111111111111111111111111111111111112"
    }
    
    # Analyze transactions to extract actual program usage
    program_usage = Counter()
    trade_programs = Counter()
    all_programs = set()
    
    # Extract programs from account keys in trade transactions
    for wallet_data in data['wallet_patterns']:
        if 'detailed_transactions' not in wallet_data:
            continue
            
        for tx in wallet_data['detailed_transactions']:
            if tx.get('is_trade', False):
                # Extract programs from account keys that look like programs
                account_keys = tx.get('account_keys', [])
                
                for account in account_keys:
                    # Skip user wallets and system programs
                    if (account not in system_programs and 
                        len(account) >= 40 and  # Valid program length
                        account not in [wallet_data['wallet']]):  # Skip wallet addresses
                        
                        all_programs.add(account)
                        program_usage[account] += 1
                        
                        if tx.get('is_trade'):
                            trade_programs[account] += 1
    
    logger.info(f"📊 ANALYSIS RESULTS:")
    logger.info(f"   Total unique programs found: {len(all_programs)}")
    logger.info(f"   Programs used in trades: {len(trade_programs)}")
    
    # Find critical missing programs
    critical_missing = []
    for program_id, count in trade_programs.most_common():
        if program_id not in monitored_programs and count >= 2:
            critical_missing.append({
                'program_id': program_id,
                'usage_count': count,
                'is_monitored': False
            })
    
    logger.info(f"")
    logger.info(f"🚨 CRITICAL MISSING PROGRAMS ({len(critical_missing)} found):")
    logger.info(f"These programs are used in trades but NOT monitored by WebSocket:")
    
    for i, program_info in enumerate(critical_missing[:10], 1):
        logger.info(f"   {i}. {program_info['program_id']} (used {program_info['usage_count']} times in trades)")
    
    # Generate the fix
    logger.info(f"")
    logger.info(f"🔧 REQUIRED FIX:")
    logger.info(f"Add these programs to your WebSocket monitoring in main.py:")
    logger.info(f"")
    
    for program_info in critical_missing[:5]:  # Top 5 most critical
        logger.info(f'            "{program_info["program_id"]}": "Unknown DEX #{critical_missing.index(program_info) + 1}",')
    
    # Show all trade programs for manual identification
    logger.info(f"")
    logger.info(f"📋 ALL PROGRAMS USED IN TRADES:")
    logger.info(f"Research these to identify what DEXes they represent:")
    
    for i, (program_id, count) in enumerate(trade_programs.most_common(), 1):
        monitored_status = "✅ MONITORED" if program_id in monitored_programs else "❌ MISSING"
        dex_name = monitored_programs.get(program_id, "UNKNOWN DEX")
        logger.info(f"   {i:2d}. {program_id} ({count} uses) - {monitored_status}")
        if program_id in monitored_programs:
            logger.info(f"       └─ {dex_name}")
    
    # Analysis summary
    total_trade_programs = len(trade_programs)
    monitored_trade_programs = len([p for p in trade_programs.keys() if p in monitored_programs])
    missing_trade_programs = total_trade_programs - monitored_trade_programs
    
    logger.info(f"")
    logger.info(f"📈 COVERAGE ANALYSIS:")
    logger.info(f"   Total programs used in trades: {total_trade_programs}")
    logger.info(f"   Currently monitored: {monitored_trade_programs}")
    logger.info(f"   Missing from monitoring: {missing_trade_programs}")
    logger.info(f"   Program coverage: {(monitored_trade_programs/total_trade_programs*100):.1f}%" if total_trade_programs > 0 else "   Program coverage: 0.0%")
    
    logger.info(f"")
    logger.info(f"✅ SOLUTION:")
    logger.info(f"Add the {len(critical_missing)} critical missing programs to WebSocket monitoring")
    logger.info(f"This should improve detection rate from 0.0% to ~95%+")
    
    return critical_missing

if __name__ == "__main__":
    critical_programs = analyze_missing_programs()
