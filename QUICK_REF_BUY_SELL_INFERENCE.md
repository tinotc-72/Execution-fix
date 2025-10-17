# Buy/Sell Inference - Quick Reference

## 🎯 Problem Solved

Trades now have accurate buy/sell labels with mint routing information, enabling executors to use the correct execution path.

## ✅ Implementation Checklist

- [x] Compare preTokenBalances vs postTokenBalances
- [x] WSOL decreases + token increases → action="buy"
- [x] Token decreases + WSOL increases → action="sell"
- [x] Save mint_in and mint_out
- [x] Log detected action with `logger.info("🎯 Detected action=%s", action)`

## 🔧 How It Works

### File: `trade_processor.py`
### Method: `detect_buy_sell(meta, monitored_wallets)`

1. **Track All Balance Changes** (including WSOL)
   ```python
   WSOL = "So11111111111111111111111111111111111111112"
   owner_changes[owner][mint] = {'delta': delta, ...}
   ```

2. **Analyze WSOL + Token Deltas Together**
   ```python
   wsol_delta = changes.get(WSOL, {}).get('delta', 0)
   for mint, data in token_changes:
       delta = data['delta']
       # Infer action...
   ```

3. **Infer Buy/Sell**
   ```python
   if delta > 0 and wsol_delta < 0:  # BUY
       action_type = 'buy'
       mint_in = WSOL
       mint_out = mint
   elif delta < 0 and wsol_delta > 0:  # SELL
       action_type = 'sell'
       mint_in = mint
       mint_out = WSOL
   ```

4. **Save Routing Fields**
   ```python
   action_data = {
       'action': action_type,
       'mint_in': mint_in,
       'mint_out': mint_out,
       # ...
   }
   ```

5. **Log Detection**
   ```python
   logger.info(f"🎯 Detected action={action_type}")
   logger.info(f"   Mint In: {mint_in}")
   logger.info(f"   Mint Out: {mint_out}")
   ```

## 📊 Example Scenarios

### BUY Trade
```
Pre:  WSOL=1.0,    Token=0.0
Post: WSOL=0.5,    Token=1000.0
→ action="buy", mint_in=WSOL, mint_out=Token
```

### SELL Trade
```
Pre:  WSOL=0.5,    Token=1000.0
Post: WSOL=0.8,    Token=500.0
→ action="sell", mint_in=Token, mint_out=WSOL
```

## 💻 Executor Usage

```python
# Access action data
actions = trade_info.get('detected_balance_actions', [])
for action in actions:
    if action['action'] == 'buy':
        # Execute: mint_in (WSOL) → mint_out (Token)
        swap(action['mint_in'], action['mint_out'], amount=0.001)
    elif action['action'] == 'sell':
        # Execute: mint_in (Token) → mint_out (WSOL)
        swap(action['mint_in'], action['mint_out'], amount=balance)
```

## 🧪 Validation

Run validation: `python validate_buy_sell_inference.py`

Expected: 8/8 tests pass ✅

## 📝 Key Logs

```
🔍 [DELTA_DETECTION] Analyzing balances...
🟢 [DELTA_DETECTION] BUY detected: ... +1000.000000 (WSOL: -0.500000)
🎯 Detected action=buy
   Mint In: So11111111111111111111111111111111111111112
   Mint Out: TokenMint111...
```

## 🚀 Benefits

- ✅ Accurate buy/sell determination
- ✅ Correct executor routing
- ✅ Enhanced debugging
- ✅ Reduced execution errors
