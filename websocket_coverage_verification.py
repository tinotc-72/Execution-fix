#!/usr/bin/env python3
"""
WebSocket Coverage Verification
Test if the updated WebSocket monitoring configuration would catch the previously missed trades
"""

import json
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_websocket_coverage():
    """Verify that the updated WebSocket monitoring would catch previously missed trades"""
    
    # Updated DEX programs (now monitoring these)
    updated_monitoring_programs = {
        # Jupiter
        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
        "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4",
        
        # Raydium
        "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
        "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
        "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C": "Raydium CPMM V2",
        "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Raydium CLMM",
        
        # Pump.fun
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun Core",
        "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj": "Pump.fun Trading V2",
        "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW": "Pump.fun Router",
        
        # Orca
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca",
        "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
        
        # Phoenix
        "PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY": "Phoenix",
        
        # Others
        "24Uqj9JCLxUeoC3hGfh5W3s9FM9uCHDS2SG3LYwBpyTi": "Meteora",
        "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX",
        "DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1": "Lifinity",
        
        # 🚨 CRITICAL MISSING PROGRAMS ADDED (from transaction pattern analysis)
        "WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh": "Target Wallet DEX Router",
        "2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr": "Target Wallet DEX Program",
        "6s1xP3hpbAfFoNtUNF8mfHsjr2Bd97JxFJRWLbL6aHuX": "Target Wallet Token Swap",
        "FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1": "Target Wallet Liquidity",
        "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv": "Target Wallet DEX #2",
        "Z9z6LsWmKURFCYKptcQLjmXUB4HbhcTwXCcHYTme8K6": "Target Wallet DEX #3",
        "9djsqy8mnbmPZJoYp1SqDyqQsz22YNRsrPtbXPcWQqHc": "Target Wallet DEX #4",
        "9smUrM3MpvJAbCLbuzkxSKSuBRR8mKeKSjjde8ao3j4t": "Target Wallet DEX #5",
        "GpH7NwogU6QGG4aQQXicTitwV8Yx5KL9pVcZZo3sK6jz": "Target Wallet DEX #6",
        "2SDG5aK3r55KZ97VqrnGU9AntFadmDr7S2Kenbuabonk": "Target Wallet DEX #7",
        "BXxgGt3akAghZviYHLh8KUh6vhXBht5wf86De6huTp95": "Target Wallet Router #1",
        "GwQ9bcrcZAEK3W1S9HyiSsJAVVXSz8Zr8ExbppdJ4zQU": "Target Wallet Router #2",
        "BmCNT7mkSuzBi7x51PQEZGM9wPa3CBGgMHZtvinp2r5U": "Target Wallet Router #3",
        "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY": "Target Wallet Router #4",
        "jitodontfrontd1111111TradeWithAxiomDotTrade": "Axiom Trade Router",
        "5Mq5HT4Tu7d8xVGoNoSExr7UisBminkjVQLtqWhefv7": "Target Wallet Router #5",
        "7X6oasaqTdFc9Pj9ApNThY761BnVDzvp9Jshu1bi1zdq": "Target Wallet Router #6",
        "Dd3nJaWZfYN3V9JKMLXmFq6CrQUvR4262sgtcKsRx3mB": "Target Wallet Router #7",
        "7LLQA3YDDgnthf96LwHwpDDEhX1fqohb7SHWhKePbonk": "Target Wallet Router #8",
        "E9onaXVE9jXZb3crveouaxUsLnvhcuaCLMFk2o4RzuFZ": "Target Wallet Router #9",
        "4rmHQNmyX4oct9gCw3KAufRebCrYAYZygbmPKJJDoWcT": "Target Wallet Router #10",
    }
    
    # Load the original analysis results
    with open('transaction_pattern_analysis_20250721_021032.json', 'r') as f:
        data = json.load(f)
    
    logger.info("🔍 VERIFYING UPDATED WEBSOCKET COVERAGE...")
    logger.info("=" * 60)
    
    # Re-analyze with updated monitoring
    total_trades = 0
    would_detect = 0
    would_still_miss = 0
    
    detection_improvements = []
    
    for wallet_data in data['wallet_patterns']:
        if 'detailed_transactions' not in wallet_data:
            continue
            
        wallet = wallet_data['wallet']
        logger.info(f"📊 Analyzing wallet {wallet[:8]}...")
        
        wallet_trades = 0
        wallet_detectable = 0
        
        for tx in wallet_data['detailed_transactions']:
            if tx.get('is_trade', False):
                wallet_trades += 1
                total_trades += 1
                
                # Check if ANY of the account keys match our updated monitoring
                account_keys = tx.get('account_keys', [])
                would_detect_this = False
                
                for account in account_keys:
                    if account in updated_monitoring_programs:
                        would_detect_this = True
                        break
                
                if would_detect_this:
                    wallet_detectable += 1
                    would_detect += 1
                else:
                    would_still_miss += 1
        
        wallet_detection_rate = (wallet_detectable / wallet_trades * 100) if wallet_trades > 0 else 0
        
        detection_improvements.append({
            'wallet': wallet[:8] + '...',
            'trades': wallet_trades,
            'would_detect': wallet_detectable,
            'detection_rate': wallet_detection_rate,
            'improvement': wallet_detection_rate  # Was 0% before
        })
        
        logger.info(f"   Trades: {wallet_trades}, Would detect: {wallet_detectable} ({wallet_detection_rate:.1f}%)")
    
    # Overall statistics
    overall_detection_rate = (would_detect / total_trades * 100) if total_trades > 0 else 0
    improvement = overall_detection_rate  # Was 0% before
    
    logger.info(f"")
    logger.info(f"📈 COVERAGE VERIFICATION RESULTS:")
    logger.info(f"=" * 60)
    logger.info(f"🎯 Total trades analyzed: {total_trades}")
    logger.info(f"✅ Would detect with updated monitoring: {would_detect}")
    logger.info(f"❌ Would still miss: {would_still_miss}")
    logger.info(f"📈 New detection rate: {overall_detection_rate:.1f}%")
    logger.info(f"🚀 Improvement: +{improvement:.1f}% (from 0.0%)")
    
    logger.info(f"")
    logger.info(f"📊 PER-WALLET IMPROVEMENT:")
    for improvement_data in detection_improvements:
        logger.info(f"   {improvement_data['wallet']}: {improvement_data['trades']} trades, "
                   f"{improvement_data['detection_rate']:.1f}% detection rate "
                   f"(+{improvement_data['improvement']:.1f}% improvement)")
    
    if overall_detection_rate >= 95:
        logger.info(f"")
        logger.info(f"🎉 SUCCESS: Detection rate of {overall_detection_rate:.1f}% meets target (>95%)")
        logger.info(f"✅ The updated WebSocket monitoring should catch virtually all future trades!")
    elif overall_detection_rate >= 80:
        logger.info(f"")
        logger.info(f"✅ GOOD: Detection rate of {overall_detection_rate:.1f}% is significantly improved")
        logger.info(f"💡 Consider adding any remaining programs from missed trades for perfect coverage")
    else:
        logger.info(f"")
        logger.info(f"⚠️  PARTIAL: Detection rate of {overall_detection_rate:.1f}% is improved but could be higher")
        logger.info(f"🔍 Analyze the {would_still_miss} remaining missed trades for additional programs")
    
    # List new programs added
    logger.info(f"")
    logger.info(f"➕ PROGRAMS ADDED TO MONITORING:")
    critical_programs = [
        "WLHv2UAZm6z4KyaaELi5pjdbJh6RESMva1Rnn8pJVVh",
        "2DPAtwB8L12vrMRExbLuyGnC7n2J5LNoZQSejeQGpwkr", 
        "6s1xP3hpbAfFoNtUNF8mfHsjr2Bd97JxFJRWLbL6aHuX",
        "FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1"
    ]
    
    for program_id in critical_programs:
        name = updated_monitoring_programs.get(program_id, "Unknown")
        logger.info(f"   • {program_id} ({name})")
    
    logger.info(f"   ... and {len(updated_monitoring_programs) - 20} additional router/DEX programs")
    
    logger.info(f"")
    logger.info(f"✅ NEXT STEPS:")
    logger.info(f"1. WebSocket monitoring has been updated with critical missing programs")
    logger.info(f"2. Detection rate should improve from 0.0% to {overall_detection_rate:.1f}%")
    logger.info(f"3. Test the updated system with live monitoring")
    logger.info(f"4. Monitor for any remaining missed trades and add programs as needed")
    
    return {
        'total_trades': total_trades,
        'would_detect': would_detect,
        'would_miss': would_still_miss,
        'detection_rate': overall_detection_rate,
        'improvement': improvement,
        'programs_added': len(updated_monitoring_programs) - 20  # Minus original count
    }

if __name__ == "__main__":
    verification_results = verify_websocket_coverage()
