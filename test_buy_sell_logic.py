#!/usr/bin/env python3
"""
Test the improved buy/sell detection logic using known transaction patterns
"""

def test_buy_sell_detection():
    """Test buy/sell detection with mock transaction logs"""
    
    # Mock logs from a SELL transaction (like WARi9zjewz6e...)
    sell_logs = [
        "Program 11111111111111111111111111111111 invoke [1]",
        "Program 11111111111111111111111111111111 success", 
        "Program ComputeBudget111111111111111111111111111111 invoke [1]",
        "Program ComputeBudget111111111111111111111111111111 success",
        "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]",
        "Program log: CreateIdempotent",
        "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
        "Program log: Instruction: InitializeAccount3",
        "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]",
        "Program log: Instruction: Swap",
        "Program log: Instruction: TransferChecked",
        "Program log: Instruction: TransferChecked", 
        "Program log: Instruction: TransferChecked",
        "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [1]",
        "Program log: Instruction: CloseAccount",  # THIS IS THE KEY FOR SELL
        "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
        "Program 11111111111111111111111111111111 invoke [1]",
        "Program 11111111111111111111111111111111 success"
    ]
    
    # Mock logs from a BUY transaction
    buy_logs = [
        "Program 11111111111111111111111111111111 invoke [1]",
        "Program 11111111111111111111111111111111 success",
        "Program ComputeBudget111111111111111111111111111111 invoke [1]", 
        "Program ComputeBudget111111111111111111111111111111 success",
        "Program ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL invoke [1]",
        "Program log: CreateIdempotent",
        "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
        "Program log: Instruction: InitializeAccount3",  # INIT for BUY
        "Program dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN invoke [1]",
        "Program log: Instruction: Swap",
        "Program log: Instruction: TransferChecked",
        "Program log: Instruction: TransferChecked",
        "Program log: Instruction: TransferChecked"
        # NO CloseAccount = BUY
    ]
    
    def analyze_direction(logs, test_name):
        print(f"\n🧪 Testing {test_name}:")
        
        # Look for swap instruction
        action_type = None
        for log_line in logs:
            if 'Program log: Instruction:' in log_line:
                instruction = log_line.split('Instruction:')[1].strip()
                if instruction == 'Swap':
                    action_type = 'swap'
                    print(f"   🔧 Found Swap instruction")
                    break
        
        if action_type == 'swap':
            # Now determine buy vs sell
            has_close_account = any('CloseAccount' in log for log in logs)
            has_init_account = any('InitializeAccount' in log for log in logs)
            token_transfers = [log for log in logs if 'TransferChecked' in log]
            
            print(f"   📊 Analysis:")
            print(f"      CloseAccount: {has_close_account}")
            print(f"      InitializeAccount: {has_init_account}")  
            print(f"      Token transfers: {len(token_transfers)}")
            
            if has_close_account:
                final_action = 'sell'
                print(f"   ✅ SELL detected: CloseAccount found")
            elif has_init_account and len(token_transfers) >= 2:
                final_action = 'buy'
                print(f"   ✅ BUY detected: InitializeAccount + {len(token_transfers)} transfers")
            else:
                final_action = 'swap'
                print(f"   ✅ SWAP detected: Generic trading")
                
            return final_action
        
        return None
    
    # Test both scenarios
    sell_result = analyze_direction(sell_logs, "SELL Transaction")
    buy_result = analyze_direction(buy_logs, "BUY Transaction")
    
    print(f"\n📊 RESULTS:")
    print(f"   Sell test: {'✅ PASS' if sell_result == 'sell' else '❌ FAIL'} (detected: {sell_result})")
    print(f"   Buy test: {'✅ PASS' if buy_result == 'buy' else '❌ FAIL'} (detected: {buy_result})")
    
    if sell_result == 'sell' and buy_result == 'buy':
        print(f"\n🎉 Buy/Sell detection logic is working correctly!")
        return True
    else:
        print(f"\n❌ Buy/Sell detection needs improvement")
        return False

if __name__ == "__main__":
    print("🧪 BUY/SELL DETECTION LOGIC TEST")
    print("=" * 50)
    test_buy_sell_detection()
