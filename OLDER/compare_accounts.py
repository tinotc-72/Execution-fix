"""
Compare our account structure with the successful pump.fun transaction.
"""

# Successful transaction accounts (from JSON)
successful_accounts = [
    "8VfFy8wPDujYo5qdhFa1oEoW8USWqi4Qwc2pm4Ek25w2",  # User wallet
    "4UxvYvUf4wuBz1XvsWn7oE628y6xzgTxA7QXUamQ4Pox",  # Authority/Config
    "ADyA8hdefvWN2dbGGWFotbzWxrAvLW83WG6QCVXvJKqw",  # Route state  
    "9Gnf5oG7QiK4uZWgMmc55Ui2uZnJcf8YVZTH52ctpump",  # Token mint
    "So11111111111111111111111111111111111111112",  # WSOL/Native mint
    "7SNNJf1xVSpK3JBoP4YJZXbetq7XFkergsn3ArwGE8ym",  # Token vault
    "CGUmmvw6PDYtgy2Js9DmzBsRcfjVvWQ2AX3ST9zYxcWP",  # WSOL account (user)
    "9dTszr1Pd2qzHSfMYPqvcZpGKQgFfMp13T1zeNraQ6CK",  # Token account (user)
    "3GiWzgJa6DN719Ci3huFTnoq8gjtDH64QwCQoCuXJAST",  # WSOL vault
    "JCRGumoE9Qi5BBgULTgdgTLjSgkCMSbF62ZZfGs84JeU",  # Fee authority
    "DWpvfqzGWuVy9jVSKSShdM2733nrEsnnhsUStYbkj6Nn",  # Fee account
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program (duplicate?)
    "11111111111111111111111111111111",  # System program
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",  # ATA program
    "GS4CU59F31iL7aR2Q8zVS8DRrcRnXX1yjQ66TqNVQnaR",  # Unknown
    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA",  # Unknown
    "7Gz1sQF4UiC14X91sBhDPFhNeV7L56JaLqJiawiWjNXF",  # Unknown
    "2QE6WrapfaWGp8RbDmpuNoLnBg3CBbGonp28AhXFok9s"   # Unknown
]

# Our current accounts (from last log)
our_accounts = [
    "76TbS54V6PNn8JFMvSLqfXft834hQ1EDEHsU9GoeNEoN",  # Config
    "4t6oEFXhxzgt19pacAdbsdTCzeUt55ZkVAJr8vpKsdTQ",  # Route state
    "7PWe75FSbwQGg7m1MwPgUQQLBUYMAC7gyZaGMh83U3Ca",  # Route params
    "9Gnf5oG7QiK4uZWgMmc55Ui2uZnJcf8YVZTH52ctpump",  # Token mint (SAME!)
    "HQ7zcHCsBwquAk7aBuF9CeFqQJX9rrCZaKigufDtRjM6",  # WSOL vault
    "7PPkAvzH7wT7KbifacLmcRaMBWhVLhSMDg2jwcrJQ5qt",  # Token vault
    "4uuCMQ54vCFHxg7Xoq1s9X2hnfCCNhLjTnVhHD8GFzJT",  # Token account (user)
    "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB",  # User wallet
    "AVUCZyuT35YSuj4RH7fwiyPu82Djn2Hfg7y2ND2XcnZH",  # Fee account
    "6Ghc5hr7MWa3pujTew43ggQnfTdVfTZvZMgQ2XAe8dT1",  # Fee authority
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",  # Trade program
    "11111111111111111111111111111111",  # System program (SAME!)
    "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",  # ATA program (SAME!)
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program (SAME!)
    "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"   # Metadata program
]

print("ACCOUNT COMPARISON:")
print(f"Successful: {len(successful_accounts)} accounts")
print(f"Our current: {len(our_accounts)} accounts")
print()

print("KEY DIFFERENCES:")
print("1. Account count differs (17 vs 15)")
print("2. Account ordering is completely different")
print("3. We might be missing the WSOL native mint account")
print("4. We might have wrong route state/config accounts")
print()

print("MISSING FROM OUR LIST:")
print("- So11111111111111111111111111111111111111112 (WSOL native mint)")
print("- User's WSOL account (wrapped SOL account)")
print("- Different config/authority accounts")
print()

print("ACTION PLAN:")
print("1. Add WSOL native mint to our account list")
print("2. Try to match the successful transaction's account order")
print("3. Create user's WSOL account if needed")
print("4. Test with the corrected account structure")
