#!/usr/bin/env python3

def compare_account_structures():
    """Compare our account structure with successful transaction"""
    
    print("🔍 Comparing account structures:")
    print()
    
    print("Successful transaction (14 accounts):")
    successful_accounts = [
        "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",  # 0 - global
        "G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP",  # 1 - fee_recipient_writable  
        "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump",  # 2 - mint
        "2hFs2bu8vhEPWtynp49hFU199gUWkJW1dZaJRWXbtPHa",  # 3 - bonding_curve
        "BxE1Fvd8qftJdzC4ZxaDfDyo2BrEWAPkSfZQztZMAnz1",  # 4 - associated_bonding_curve
        "76HJzzJjzgmjU8ACg82c6rh6h1BQmZhj4QURQT7x3WBm",  # 5 - user_token_account
        "G1UNVXCvitMWeKjqZ9bNpqnYYk8uLhA8bSh2kBT7La45",  # 6 - user (signer)
        "11111111111111111111111111111111",              # 7 - system_program
        "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ",  # 8 - creator_vault
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",   # 9 - token_program
        "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1",  # 10 - event_authority
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",   # 11 - pump_program
        "8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt",  # 12 - fee_recipient
        "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ"    # 13 - fee_program
    ]
    
    for i, acc in enumerate(successful_accounts):
        marker = ""
        if acc == "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf":
            marker = " <-- GLOBAL"
        elif acc == "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump":
            marker = " <-- MINT"
        elif acc == "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ":
            marker = " <-- CREATOR_VAULT"
        elif acc == "8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt":
            marker = " <-- FEE_RECIPIENT"
        elif acc == "G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP":
            marker = " <-- FEE_RECIPIENT_WRITABLE"
        print(f"  {i:2d}: {acc}{marker}")
    
    print()
    print("Our current structure (16 accounts with ATA bundling):")
    our_accounts = [
        "global_account",                    # 0
        "fee_recipient_writable",           # 1  <-- We use extracted fee_recipient here
        "mint",                             # 2
        "bonding_curve",                    # 3
        "associated_bonding_curve",         # 4
        "user_token_account",              # 5
        "user (signer)",                   # 6
        "system_program",                  # 7
        "token_program",                   # 8
        "creator_vault",                   # 9  <-- Different position than successful (was 8)
        "event_authority",                 # 10
        "pump_program",                    # 11
        "global_volume_accumulator",       # 12
        "user_volume_accumulator",         # 13
        "fee_config",                      # 14
        "fee_program"                      # 15
    ]
    
    for i, acc in enumerate(our_accounts):
        print(f"  {i:2d}: {acc}")
        
    print()
    print("🔍 Key differences:")
    print("1. Successful tx has creator_vault at index 8, ours at index 9")
    print("2. Successful tx has fee_recipient at index 12, but different value than our index 1")
    print("3. We have additional accounts: global_volume_accumulator, user_volume_accumulator, fee_config")
    print("4. The fee_recipient_writable in successful tx (index 1) is G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP")
    print("   But our extracted fee_recipient is 8Wf5TiAheLUqBrKXeYg2JtAFFMWtKdG2BSFgqUcPVwTt")

if __name__ == "__main__":
    compare_account_structures()