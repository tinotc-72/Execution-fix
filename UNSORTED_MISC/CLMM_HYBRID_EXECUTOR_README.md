# CLMM Hybrid Copy Executor

## Overview
The `clmm_hybrid_copy_executor.py` provides a hybrid trading strategy that attempts CLMM trades first and falls back to Jupiter API v6 for reliable execution. This executor is fully compatible with your existing copy bot architecture.

## ✅ Key Features

### 🚀 Hybrid Strategy
- **Primary Method**: CLMM direct trading for optimal speed and fees
- **Fallback Method**: Jupiter API v6 for reliable execution when CLMM fails
- **Smart Routing**: Automatically switches between methods based on availability

### 🔧 Copy Bot Compatible
- **Function Signatures**: Matches existing executor pattern
- **Return Format**: Standardized `{"success": bool, "signature": str}` dictionary
- **Error Handling**: Consistent error reporting across all methods

### 🛡️ Robust Execution
- **Official Confirmation**: Uses Solana's `getSignatureStatuses` for transaction verification
- **Retry Logic**: Automatic failover between CLMM and Jupiter
- **Balance Checking**: Real-time token balance verification for sells

## 📋 Available Functions

### Primary Functions (Copy Bot Compatible)
```python
async def try_clmm_hybrid_buy(token_mint: str, wallet: Keypair, amount_sol: float) -> dict
async def try_clmm_hybrid_sell_all(token_mint: str, wallet: Keypair) -> dict
```

### Additional Functions
```python
async def try_clmm_hybrid_sell(token_mint: str, wallet: Keypair, percentage: float = 100.0) -> dict
async def cleanup() -> None
```

## 🔧 Integration Example

```python
from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all
from config import WALLET

# Buy tokens
buy_result = await try_clmm_hybrid_buy("FV6Xcw9K5GZRb2jDN7e6xXgzs4ZDgJM1BE6nWRqRbonk", WALLET, 0.001)
if buy_result.get('success'):
    print(f"✅ Buy successful: {buy_result.get('signature')}")

# Sell all tokens
sell_result = await try_clmm_hybrid_sell_all("FV6Xcw9K5GZRb2jDN7e6xXgzs4ZDgJM1BE6nWRqRbonk", WALLET)
if sell_result.get('success'):
    print(f"✅ Sell successful: {sell_result.get('signature')}")
```

## 🎯 Test Results

### Successful Test Execution
```
✅ Buy successful: 5VxQkHsyEJbfVCRuf9ioDyRuwqS4kPwpppevsJxNurMPCMiAEg6UaEYxbEqPeHn2GDtyHN3tLDyEmaUcDvs5f4Dz
✅ Sell successful: 3U2A4fHV8eqhNFLK6rdNfpAJjBnirRZqWgw148QpBEMEfKtCMKx364Z4GWsryCkvPfBfgy57CXuoh5nvP1sYe1Tr
🎯 All tests passed! CLMM Hybrid Copy Executor is working correctly.
```

### Execution Flow
1. **CLMM Attempt**: Tries direct CLMM trading for optimal performance
2. **Jupiter Fallback**: Automatically falls back to Jupiter API v6 when CLMM fails
3. **Official Confirmation**: Uses Solana RPC `getSignatureStatuses` for transaction verification
4. **Return Format**: Consistent dictionary format with success status and signature

## 📁 Files Created

1. **`clmm_hybrid_copy_executor.py`** - Main executor with hybrid strategy
2. **`test_clmm_hybrid_executor.py`** - Standalone test script

## 🔗 Integration with Copy Bot

The executor is designed to seamlessly integrate with your existing copy bot architecture:

- **Compatible Signatures**: Matches `(token_mint, wallet, amount)` pattern for buys and `(token_mint, wallet)` for sells
- **Consistent Returns**: Uses standard `{"success": bool, "signature": str}` format
- **Global State**: Maintains executor instance for efficient resource usage
- **Proper Cleanup**: Includes cleanup function for resource management

## 🚀 Next Steps

You can now use this executor in your copy bot by importing the functions and calling them just like your existing executors:

```python
from clmm_hybrid_copy_executor import try_clmm_hybrid_buy, try_clmm_hybrid_sell_all

# Use in your copy bot logic
routes = [
    ("CLMM Hybrid", try_clmm_hybrid_buy, try_clmm_hybrid_sell_all),
    # ... other routes
]
```

The executor provides the best of both worlds - CLMM speed when available, Jupiter reliability when needed!
