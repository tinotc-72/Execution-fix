# Minimal per-DEX Tests

Quick, repeatable tests to catch regressions before live copy-trading.

## Overview

This directory contains minimal test scripts for each DEX integration:

- `test_pumpfun.py` - Pump.fun buy transaction test
- `test_jupiter.py` - Jupiter swap buy transaction test  
- `test_raydium_cpmm.py` - Raydium CPMM buy transaction test
- `test_meteora.py` - Meteora Dynamic Bonding Curve buy transaction test

## Usage

Each script supports two modes and an optional amount parameter:

### Simulate Mode (Dry-run)
Builds the transaction but does not submit it:
```bash
python tests/test_jupiter.py --simulate
python tests/test_pumpfun.py --simulate
python tests/test_raydium_cpmm.py --simulate
python tests/test_meteora.py --simulate
```

### Submit Mode (Live)
Signs and submits the transaction to the blockchain:
```bash
python tests/test_jupiter.py --submit
python tests/test_pumpfun.py --submit
python tests/test_raydium_cpmm.py --submit
python tests/test_meteora.py --submit
```

### Custom Amount
Specify a custom amount in SOL (default is 0.001 SOL):
```bash
python tests/test_jupiter.py --simulate --amount 0.005
python tests/test_jupiter.py --submit --amount 0.002
```

## Test Details

### Jupiter (Fully Functional)
- ✅ Builds 0.001 SOL → USDC swap transaction (amount customizable via --amount)
- ✅ Uses Jupiter API to get best route
- ✅ Signs transaction with wallet
- ✅ Uses `send_and_confirm_v0_tx()` for submission
- ✅ Logs signature and final status via `log_submit_result()`

### Pump.fun (Transaction Cloning Architecture)
- ⚠️ Requires source transaction to clone
- Uses direct copy executor pattern
- Monitors target wallet and clones transactions
- Not suitable for standalone buy transactions
- ✅ Supports --amount flag and uses `log_submit_result()` for status output

### Raydium CPMM (Not Yet Implemented)
- ❌ Minimal scaffold only
- Needs pool resolution from trade_info
- Needs swap instruction building
- Needs Raydium CPMM program integration
- ✅ Supports --amount flag and uses `log_submit_result()` for status output

### Meteora (Partial Implementation)
- ⚠️ Pool resolution incomplete
- Needs accurate bonding curve calculation
- Needs Meteora Anchor IDL for swap instructions
- Partial execute_buy implementation exists
- ✅ Supports --amount flag and uses `log_submit_result()` for status output

## Requirements

- Python 3.11+
- Dependencies from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```
- `.env` file with required environment variables:
  1. Copy `.env.example` to `.env`
  2. Fill in your actual values:
     - `PHANTOM_PRIVATE_KEY` - Your wallet private key (base58 encoded)
     - `HELIUS_RPC_URL` - Your RPC endpoint URL
     - `HELIUS_API_KEY` - Your Helius API key
     - `RPC_URL` - Fallback RPC endpoint

⚠️ **Security**: Never commit your `.env` file with real credentials!

## Token Used

All tests use USDC as the target token:
- **USDC Mint**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`

This is a known liquid token with high availability across all DEXs.

## Test Amount

All tests use **0.001 SOL** (1,000,000 lamports) as the swap amount.

## Safety

- ⚠️ **IMPORTANT**: The `--submit` flag will execute real transactions on mainnet
- Always test with `--simulate` first
- Use a test wallet with minimal funds
- Review transaction details before submission

## Logging

All tests use comprehensive logging:
- Transaction building steps
- API responses (Jupiter)
- Signature and confirmation status
- Error messages with full stack traces

### Unified Submit Result Logging
All tests use `log_submit_result()` from `utils.logs` to print standardized transaction results:
```
DEX={dex_name} action={action} mint={mint} sig={signature} status={status} ok={success}
```

This ensures consistent output format across all DEX test scripts, making it easy to:
- Track transaction success/failure
- Parse logs programmatically
- Debug issues across different DEXs

Log level can be adjusted in each script.

## Future Improvements

1. Complete Raydium CPMM implementation
2. Complete Meteora pool resolution and swap logic
3. Add Pump.fun standalone buy support (if possible)
4. Add transaction simulation via RPC before submission
5. Add balance checks before/after swaps
6. Add success rate tracking
