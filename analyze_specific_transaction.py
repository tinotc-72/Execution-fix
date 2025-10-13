#!/usr/bin/env python3
"""
Analyze specific transaction failure
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def analyze_specific_transaction():
    """Analyze the provided transaction signature"""
    
    signature = "5Dz5vtE5wmtQi738itycjf7cRmFFWXWMUKQUXXFyuBpbQkTfmtbosSCmX84LtPc5DhTfCoEkb8NUUr9vN68HmTc"
    
    print(f"🔍 ANALYZING TRANSACTION: {signature}")
    print("=" * 80)
    
    try:
        from transaction_failure_analyzer import TransactionFailureAnalyzer
        
        print("📋 Fetching transaction details...")
        analyzer = TransactionFailureAnalyzer()
        result = analyzer.analyze_transaction_failure(signature)
        
        if result:
            print("✅ Analysis complete!")
        else:
            print("❌ Analysis failed or transaction not found")
            
    except Exception as e:
        print(f"❌ Error analyzing transaction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_specific_transaction())
