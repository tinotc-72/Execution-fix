#!/usr/bin/env python3
"""
🔍 NEW TRANSACTION ANALYSIS
==========================

Analyzing transaction: 2pT917H73HoUe2yJzxVoysNM5W1CWmDbHJN5ukQ7atk8qU744JrHx4xRJZQVtvsBmGfmXznVC46YAUmikpSoxjSa

This script will:
1. Fetch and analyze the transaction details
2. Identify the program/DEX used
3. Extract trading patterns
4. Determine if we need a new MEV executor
5. Enhance our pattern recognition system
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def analyze_new_transaction():
    """Analyze the new transaction using our enhanced pattern analyzer"""
    
    signature = "2pT917H73HoUe2yJzxVoysNM5W1CWmDbHJN5ukQ7atk8qU744JrHx4xRJZQVtvsBmGfmXznVC46YAUmikpSoxjSa"
    
    logger.info("🔍 NEW TRANSACTION ANALYSIS")
    logger.info("=" * 60)
    logger.info(f"📋 Transaction: {signature}")
    logger.info(f"🕐 Analysis Time: {datetime.now()}")
    logger.info("")
    
    try:
        # Import our enhanced trading pattern analyzer
        from trading_pattern_analyzer import TradingPatternAnalyzer
        
        # Initialize analyzer
        analyzer = TradingPatternAnalyzer()
        logger.info("✅ Trading pattern analyzer initialized")
        
        # Analyze the transaction
        logger.info("🔍 Analyzing transaction patterns...")
        result = await analyzer.analyze_signature(signature)
        
        if result:
            logger.info("✅ Transaction analysis completed!")
            logger.info("")
            logger.info("📊 ANALYSIS RESULTS:")
            logger.info("=" * 40)
            
            # Print key findings
            pattern = result.get('pattern', 'Unknown')
            confidence = result.get('confidence', 0)
            dex = result.get('dex', 'Unknown')
            programs = result.get('programs_used', [])
            
            logger.info(f"🎯 Pattern: {pattern}")
            logger.info(f"📊 Confidence: {confidence}/10")
            logger.info(f"🏪 DEX: {dex}")
            logger.info(f"🔧 Programs: {len(programs) if programs else 0} detected")
            
            # Detailed program analysis
            if programs:
                logger.info("")
                logger.info("🔧 PROGRAM ANALYSIS:")
                logger.info("-" * 30)
                for i, program in enumerate(programs[:5]):  # Show first 5
                    logger.info(f"   {i+1}. {program}")
                if len(programs) > 5:
                    logger.info(f"   ... and {len(programs) - 5} more")
            
            # Check if this is a new pattern
            logger.info("")
            logger.info("🆕 NEW PATTERN DETECTION:")
            logger.info("-" * 35)
            
            known_patterns = [
                'Direct Pump.fun',
                'Direct Meteora DBC'
            ]
            
            if pattern not in known_patterns:
                logger.info(f"🎉 NEW PATTERN DISCOVERED: {pattern}")
                logger.info("🚀 This could be a candidate for a new MEV executor!")
                
                # Analyze program IDs for new DEX detection
                if programs:
                    logger.info("")
                    logger.info("🔍 PROGRAM ID ANALYSIS:")
                    logger.info("-" * 25)
                    
                    # Known program IDs for comparison
                    known_programs = {
                        '6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P': 'Pump.fun Direct',
                        'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN': 'Meteora DBC',
                        'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4': 'Jupiter V6',
                        'JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB': 'Jupiter V4',
                        '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8': 'Raydium AMM',
                        'CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK': 'Raydium CLMM',
                        'CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C': 'Raydium CPMM',
                        'whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc': 'Orca Whirlpool',
                        '9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM': 'Orca V1',
                        'DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1': 'Orca V2',
                        'PhoeNiX7VUpF3HXAkG3pZ3rWwUPtzPwNDtKJsDQdj9yV': 'Phoenix',
                        'opnb2LAfJYbRMAHHvqjCwQxanZn7ReEHp1k81EohpZb': 'OpenBook',
                        'srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX': 'Serum',
                    }
                    
                    new_programs = []
                    for program in programs:
                        if program in known_programs:
                            logger.info(f"   ✅ Known: {program} ({known_programs[program]})")
                        else:
                            logger.info(f"   🆕 NEW: {program}")
                            new_programs.append(program)
                    
                    if new_programs:
                        logger.info("")
                        logger.info(f"🎯 FOUND {len(new_programs)} NEW PROGRAM(S)!")
                        logger.info("🚀 These could be candidates for new MEV executors")
                        
                        # Save new program info for further analysis
                        new_program_data = {
                            'transaction': signature,
                            'pattern': pattern,
                            'confidence': confidence,
                            'new_programs': new_programs,
                            'analysis_date': datetime.now().isoformat()
                        }
                        
                        with open('new_program_analysis.json', 'w') as f:
                            json.dump(new_program_data, f, indent=2)
                        
                        logger.info("💾 New program data saved to: new_program_analysis.json")
            else:
                logger.info(f"✅ Known pattern: {pattern}")
                logger.info("ℹ️ This transaction uses an existing MEV executor")
            
            # Print full result for debugging
            logger.info("")
            logger.info("📋 FULL ANALYSIS RESULT:")
            logger.info("-" * 30)
            logger.info(json.dumps(result, indent=2, default=str))
            
            return result
            
        else:
            logger.error("❌ Transaction analysis failed - no result returned")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error analyzing transaction: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

async def main():
    """Main analysis function"""
    result = await analyze_new_transaction()
    
    if result:
        logger.info("")
        logger.info("🎯 ANALYSIS COMPLETE!")
        logger.info("=" * 30)
        
        pattern = result.get('pattern', 'Unknown')
        confidence = result.get('confidence', 0)
        
        if confidence >= 8:
            logger.info("🚀 HIGH CONFIDENCE PATTERN - Excellent for MEV execution")
        elif confidence >= 6:
            logger.info("✅ GOOD CONFIDENCE PATTERN - Suitable for MEV execution")
        elif confidence >= 4:
            logger.info("⚠️ MEDIUM CONFIDENCE PATTERN - May need more analysis")
        else:
            logger.info("❌ LOW CONFIDENCE PATTERN - Needs investigation")
        
        logger.info("")
        logger.info("📋 NEXT STEPS:")
        if pattern not in ['Direct Pump.fun', 'Direct Meteora DBC']:
            logger.info("1. 🔍 Review new_program_analysis.json for detailed findings")
            logger.info("2. 🚀 Consider building new MEV executor if pattern is profitable")
            logger.info("3. 🎯 Update execution coordinator with new DEX detection")
            logger.info("4. 📊 Analyze more transactions from this program for patterns")
        else:
            logger.info("1. ✅ Transaction uses existing MEV executor")
            logger.info("2. 🎯 No new executor needed")
            logger.info("3. 🚀 Ready for copy trading execution")

if __name__ == "__main__":
    asyncio.run(main())
