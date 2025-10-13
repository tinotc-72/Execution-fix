"""
🎯 WALLET SUBSTITUTION GUIDE
============================

STEP 1: Finding Good Target Wallets
-----------------------------------

1. **Look for Successful Meme Coin Traders:**
   - Check Solscan.io or SolanaFM for wallets with high-profit meme coin trades
   - Look for wallets that:
     * Buy early in meme coin rallies
     * Sell at good profits (2x-10x+)
     * Trade frequently but not excessively
     * Have consistent win rates

2. **Wallet Characteristics to Avoid:**
   - Bots (too many transactions per second)
   - Whales (trades too large to copy profitably)
   - Inactive wallets (no recent trades)
   - Wallets with poor performance history

3. **Tools to Find Good Wallets:**
   - DexScreener: Look at top gainers and check who bought early
   - GmgnAI: Check wallet performance metrics
   - Solscan: Analyze transaction history
   - BirdEye: Track wallet performance

STEP 2: Test New Wallets Safely
-------------------------------

1. **Start with Small Investment:**
   - Set investment_amount_sol=0.001 (very small)
   - Monitor performance for 24-48 hours
   - Only increase if profitable

2. **Monitor Performance:**
   - Check logs regularly
   - Watch for successful trade copies
   - Verify trades are being detected and executed

3. **Performance Metrics to Track:**
   - Detection rate (% of target trades copied)
   - Execution success rate
   - Profit/loss ratio
   - Speed of execution

STEP 3: Safety Precautions
--------------------------

1. **Always Test First:**
   python main.py  # Test with small amounts

2. **Keep Backups:**
   - Save your current config before changes
   - Keep a list of previously successful wallets

3. **Emergency Stop:**
   - Know how to stop the bot (Ctrl+C)
   - Keep emergency liquidation ready

STEP 4: Example Configuration
-----------------------------

# Replace wallet in main.py:
target_wallets=[
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Keep proven wallet
    "YOUR_NEW_WALLET_ADDRESS_HERE",  # Your new target
    # "THIRD_WALLET_IF_DESIRED",  # Optional third wallet
],

STEP 5: Monitoring After Changes
-------------------------------

After changing wallets:
1. Run: python main.py
2. Watch logs for successful subscriptions
3. Monitor for trade detection within first hour
4. Verify trades are being copied correctly

⚠️  IMPORTANT REMINDERS:
- Never copy random wallets without research
- Always test with minimal amounts first
- Monitor bot performance closely after changes
- Keep successful wallet addresses as backups
"""
