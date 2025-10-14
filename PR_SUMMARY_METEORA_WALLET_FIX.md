# PR Summary: Meteora DEX Detection and wallet_address Fix

## Problem Statement
The wallet transaction parser was showing `DEX=unknown` warnings in logs for Meteora transactions, requiring the pipeline to guess the DEX type. Additionally, the parser needed to extract the correct wallet address from transaction signers.

## Solution
Implemented explicit Meteora detection using the exact snippet from the problem statement:

### Changes Made

#### 1. Meteora DEX Detection (Lines 674-684)
```python
METEORA_PID = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"

# 1) DEX detection
for ix in (tx.get("message", {}).get("instructions") or []):
    pid = ix.get("programId") or ix.get("program")
    if pid == METEORA_PID:
        parsed["dex"] = "meteora"
        parsed.setdefault("action", "swap")
        self.logger.info(f"✅ [PARSER] Meteora detected: programId={METEORA_PID[:8]}...")
        break
```

**Benefits:**
- Explicit DEX detection happens upfront before complex parsing
- No more `DEX=unknown` warnings for Meteora transactions
- Action defaults to "swap" when not otherwise specified

#### 2. Wallet Address Extraction (Lines 686-689)
```python
# 2) Real source wallet (wallet being copied)
signers = [k["pubkey"] for k in (tx.get("message", {}).get("accountKeys") or []) if k.get("signer")]
if signers:
    parsed["wallet_address"] = signers[0]
```

**Benefits:**
- Correctly identifies the wallet being copied (first signer)
- Handles transactions with multiple signers
- Gracefully handles transactions with no signers

#### 3. Return Format Update (Line 815)
Changed return dictionary key from `source_wallet` to `wallet_address`:

```python
return {
    "dex": dex,
    "action": action,
    "mint": mint,
    "amount": amount,
    "signature": signature,
    "wallet_address": wallet_address,  # Changed from source_wallet
    "original_result": decoder_result
}
```

**Backward Compatibility:**
- ✅ `main.py` already expects `wallet_address`: `trade_info.get("wallet_address")`
- ✅ No breaking changes to existing code
- ✅ All tests pass

#### 4. Logging Consistency
- ✅ Uses INFO level with ✅ emoji for successful detection
- ⚠️ Uses WARNING level with ⚠️ emoji for unknown DEX
- Consistent with existing logging format

### Test Coverage

#### Updated test_meteora_early_detection.py
- Tests METEORA_PID constant
- Tests DEX detection loop pattern
- Tests wallet_address extraction from signers
- Tests logging format consistency

#### New test_meteora_wallet_address.py
- Tests Meteora detection with message.instructions format
- Tests multiple signers (uses first)
- Tests no signers (returns None)
- Tests return dictionary includes wallet_address
- Verifies source_wallet is NOT in return dict

### Test Results
```
✅ test_meteora_early_detection.py: ALL TESTS PASSED
✅ test_meteora_wallet_address.py: ALL TESTS PASSED
```

## Impact
- **Improved Accuracy**: Meteora transactions are now correctly identified upfront
- **Better Logging**: Clear visibility when Meteora is detected, no more DEX=unknown warnings
- **Correct Wallet Tracking**: Wallet address properly extracted from transaction signers
- **Backward Compatible**: Existing code already expects wallet_address field

## Implementation Notes
- Follows exact snippet from problem statement
- Maintains existing RPC client usage
- No new dependencies added
- Logging format consistent with repository standards (INFO/WARNING/ERROR emojis)
