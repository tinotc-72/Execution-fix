# Aggressive Trade Execution Implementation

## Overview

This implementation revises the trade execution logic for the Solana copy trading bot to allow aggressive trade copying. The bot now executes trades when **EITHER** of two conditions is met:

1. **Trade instructions are detected** - A recognizable DEX program (swap/buy/sell instruction) is found in the transaction
2. **Transaction signer is in MONITORED_WALLETS** - The transaction is signed by a monitored wallet

## Key Features

### 1. Explicit Execution Conditions

The bot now explicitly checks two conditions before executing:

```python
# Condition 1: Check for trade instructions (DEX programs)
instruction_info = self.trade_processor._check_trade_instructions(trade_info)
has_trade_instructions = instruction_info.get('has_trade_instructions', False)

# Condition 2: Check if signer is in MONITORED_WALLETS
signer_info = self.trade_processor._check_monitored_wallet_is_signer(trade_info)
has_monitored_signer = signer_info.get('has_monitored_involvement', False)

# EXECUTE IF EITHER CONDITION IS MET
if has_trade_instructions or has_monitored_signer:
    # Execute trade
```

### 2. Trade Instruction Detection

The bot detects trade instructions by checking for known DEX programs:
- Jupiter V6
- Pump.fun
- Raydium (AMM, CPMM, CLMM)
- Orca (Swap, Whirlpool)
- Meteora (DAMM, DLMM)
- Alpha DEX

### 3. Monitored Wallet Detection

The bot checks if any signer or fee payer in the transaction is from the MONITORED_WALLETS list:
- Analyzes transaction header for number of signatures
- Extracts all signers from the transaction
- Checks if any signer is in the monitored wallets list

### 4. Buy Execution (0.001 SOL)

When a buy is detected and execution conditions are met:
```python
await self.execution_coordinator._execute_copy_buy(
    token_mint=token_mint, 
    source_wallet=source_wallet, 
    trade_info=trade_info,
    amount_sol=0.001  # Explicit 0.001 SOL investment
)
```

### 5. Sell Execution (Same Percentage)

When a sell is detected, the bot:
1. Calculates the percentage sold by the monitored wallet
2. Sells the same percentage of our holdings

```python
# Calculate sell percentage from monitored wallet's balance change
sell_percentage = self._calculate_sell_percentage(trade_info, source_wallet, token_mint)

await self.execution_coordinator._execute_copy_sell(
    token_mint=token_mint, 
    source_wallet=source_wallet, 
    trade_info=trade_info,
    sell_percentage=sell_percentage
)
```

### 6. Percentage Calculation Logic

The sell percentage is calculated by:
1. Extracting pre and post token balances from transaction metadata
2. Finding the monitored wallet's balance change for the specific token
3. Calculating: `(amount_sold / pre_amount) * 100`
4. Defaulting to 100% if balance data is unavailable

## Execution Flow

```
Trade Detected
    ↓
Check Condition 1: Trade Instructions (DEX programs)?
    ↓
Check Condition 2: Signer in MONITORED_WALLETS?
    ↓
If EITHER condition is true:
    ↓
    Determine Action (buy/sell/swap)
    ↓
    If BUY:
        → Execute with 0.001 SOL
    ↓
    If SELL:
        → Calculate % from monitored wallet
        → Execute sell with same %
    ↓
    If UNKNOWN:
        → Default to BUY with 0.001 SOL
```

## Changes Made

### main.py

**`_process_detected_trade()` method:**
- Added explicit condition checking using `_check_trade_instructions()` and `_check_monitored_wallet_is_signer()`
- Added detailed logging for both conditions
- Skip execution if neither condition is met
- Execute if EITHER condition is met
- Explicit 0.001 SOL for buy executions
- Calculate and pass sell percentage for sell executions

**New `_calculate_sell_percentage()` method:**
- Analyzes transaction metadata for balance changes
- Calculates percentage sold by monitored wallet
- Handles missing data gracefully (defaults to 100%)
- Returns percentage between 0-100

### test_aggressive_execution.py

Updated tests to validate:
1. Execution condition checks (trade instructions and monitored signer)
2. Sell percentage calculation implementation
3. Aggressive execution patterns
4. Execution method calls
5. Logging and debugging

## Behavior Changes

### Previous Behavior
- Executed on ANY detected trade without explicit condition checking
- Relied on implicit validation in fallback logic
- Less transparent about why execution was triggered

### New Behavior
- Explicitly checks two clear conditions before execution
- Logs which condition triggered execution
- More transparent and debuggable
- Same aggressive behavior but with clearer logic

## Safety Features

1. **Condition-based execution**: Only executes when legitimate trade signals are detected
2. **Percentage-based selling**: Mirrors monitored wallet's sell strategy
3. **Fallback defaults**: Defaults to 100% sell if percentage cannot be calculated
4. **Logging**: Comprehensive logging for debugging and monitoring
5. **Error handling**: Graceful handling of missing or incomplete data

## Testing

All tests pass successfully:

```
✅ TEST 1: Execution Condition Checks (4/4)
✅ TEST 2: Sell Percentage Calculation (4/4)
✅ TEST 3: Aggressive Execution Patterns (4/4)
✅ TEST 4: Execution Method Calls (4/4)
✅ TEST 5: Logging and Debugging (4/4)
```

## Monitored Wallets

Configured in `config.py`:
```python
MONITORED_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Target wallet 1
    "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",  # Target wallet 2
    "Ez2jp3rwXUbaTx7XwiHGaWVgTPFdzJoSg8TopqbxfaJN",  # Target wallet 3
    "9ePNTG4j5eDGTFtUr6axt7h747HHzJPfmFh6JHAwFZsd",  # Target wallet 4
    "gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB",  # Target wallet 5
]
```

## Known DEX Programs

The bot recognizes these DEX programs for trade instruction detection:
- Jupiter V6: `JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4`
- Pump.fun: `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P`
- Raydium AMM: `675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8`
- Raydium CPMM: `CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C`
- Raydium CLMM: Multiple addresses
- Orca Swap: `SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8`
- Orca Whirlpool: `whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc`
- Meteora: `dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN`
- Meteora DLMM: `Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB`
- Alpha DEX: `ALPHAQmeA7bjrVuccPsYPiCvsi428SNwte66Srvs4pHA`

## Summary

This implementation makes the bot behave like top Solana copiers by:
1. ✅ Executing trades when DEX programs are detected OR monitored wallet is signer
2. ✅ Investing exactly 0.001 SOL on buys
3. ✅ Selling the same percentage as the monitored wallet
4. ✅ Removing strict validation requirements while maintaining safety through explicit conditions
5. ✅ Providing clear, transparent execution logic with comprehensive logging

The bot is now more aggressive in copying trades while maintaining safety through explicit condition checking and transparent execution logic.
