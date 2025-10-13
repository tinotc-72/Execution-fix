#!/usr/bin/env python3
"""
🔄 PROPORTIONAL SELLING IMPLEMENTATION
Apply proportional selling to all remaining executors
"""

import os
import re

def apply_proportional_selling_pattern():
    """Apply proportional selling to remaining executors"""
    print("🔄 APPLYING PROPORTIONAL SELLING TO ALL EXECUTORS")
    print("=" * 70)
    
    # Pattern for proportional selling logic
    proportional_logic = '''
            # Proportional sell calculation
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            if sell_percentage <= 0 or sell_percentage > 100.0:
                logger.warning(f"⚠️ Invalid sell_percentage {{sell_percentage}}, defaulting to 100%.")
                sell_percentage = 100.0
            
            # Calculate proportional amount to sell
            amount_to_sell = int(token_balance * (sell_percentage / 100.0))
            logger.info(f"🎯 PROPORTIONAL SELL:\\n   Total balance: {{token_balance}} tokens\\n   Amount to sell: {{amount_to_sell}} tokens\\n   Sell percentage: {{sell_percentage:.2f}}%")
'''
    
    # Files to update
    executor_files = [
        "raydium_copy_executor.py",
        "raydium_clmm_copy_executor.py", 
        "clmm_copy_executor.py",
        "raydium_trade_executor.py",
        "raydium_clmm_trade_executor.py"
    ]
    
    for executor_file in executor_files:
        print(f"\n📝 Processing {executor_file}...")
        
        if not os.path.exists(executor_file):
            print(f"   ❌ File not found: {executor_file}")
            continue
        
        try:
            with open(executor_file, 'r') as f:
                content = f.read()
            
            # Find execute_sell_copy methods and add **kwargs
            updated_content = content
            
            # Update method signatures to include **kwargs
            patterns_to_replace = [
                (r"async def execute_sell_copy\(self, ([^)]+)\):", 
                 r"async def execute_sell_copy(self, \1, **kwargs):"),
                (r"async def execute_copy_trade\(self, ([^)]+)\):",
                 r"async def execute_copy_trade(self, \1, **kwargs):"),
            ]
            
            for pattern, replacement in patterns_to_replace:
                if re.search(pattern, updated_content):
                    updated_content = re.sub(pattern, replacement, updated_content)
                    print(f"   ✅ Updated method signature")
            
            # Find token balance calculation and add proportional logic
            balance_patterns = [
                r"(token_balance = await self\.get_token_balance\([^)]+\))",
                r"(token_balance\s*=\s*[^;]+)",
                r"(amount_to_sell\s*=\s*token_balance)"
            ]
            
            for pattern in balance_patterns:
                if re.search(pattern, updated_content):
                    # Replace amount_to_sell = token_balance with proportional logic
                    updated_content = re.sub(
                        r"amount_to_sell\s*=\s*token_balance",
                        f"""# Proportional sell calculation
            sell_percentage = kwargs.get('sell_percentage', 100.0)
            if sell_percentage <= 0 or sell_percentage > 100.0:
                logger.warning(f"⚠️ Invalid sell_percentage {{sell_percentage}}, defaulting to 100%.")
                sell_percentage = 100.0
            
            # Calculate proportional amount to sell
            amount_to_sell = int(token_balance * (sell_percentage / 100.0))
            logger.info(f"🎯 PROPORTIONAL SELL:\\n   Total balance: {{token_balance}} tokens\\n   Amount to sell: {{amount_to_sell}} tokens\\n   Sell percentage: {{sell_percentage:.2f}}%")""",
                        updated_content
                    )
                    print(f"   ✅ Added proportional selling logic")
                    break
            
            # Update execute_sell_copy calls to pass **kwargs
            updated_content = re.sub(
                r"await self\.execute_sell_copy\(([^)]+)\)",
                r"await self.execute_sell_copy(\1, **kwargs)",
                updated_content
            )
            
            # Update calls in execute_copy_trade to pass kwargs to execute_sell_copy
            updated_content = re.sub(
                r"return await self\.execute_sell_copy\(([^)]+)\)",
                r"return await self.execute_sell_copy(\1, **kwargs)",
                updated_content
            )
            
            # Write updated content
            with open(executor_file, 'w') as f:
                f.write(updated_content)
            
            print(f"   ✅ Updated {executor_file}")
            
        except Exception as e:
            print(f"   ❌ Error updating {executor_file}: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 PROPORTIONAL SELLING IMPLEMENTATION COMPLETE!")
    print("✅ All executors should now support proportional selling")
    print("=" * 70)

if __name__ == "__main__":
    apply_proportional_selling_pattern()
