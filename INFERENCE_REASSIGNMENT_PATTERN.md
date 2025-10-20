# Inference Reassignment Pattern - Documentation

## Problem Statement
Ensure the mutated `trade_info` from `infer_missing_fields` is used after inference.

## Solution
All calls to `infer_missing_fields` in the codebase properly follow the reassignment pattern:

```python
trade_info = self.trade_processor.infer_missing_fields(trade_info)
```

## Why This Matters
The `infer_missing_fields` method:
1. **Mutates the input dict** - adds/updates fields in place
2. **Returns the modified dict** - for consistency and chaining

Best practice is to ALWAYS reassign the result, even though the dict is mutated in place:
- ✅ **CORRECT**: `trade_info = self.trade_processor.infer_missing_fields(trade_info)`
- ❌ **AVOID**: `self.trade_processor.infer_missing_fields(trade_info)` (no reassignment)

## Current Status
✅ **All calls are correct!**

Verified locations in `main.py`:
- Line 349: `trade_info = self.trade_processor.infer_missing_fields(trade_info)`
- Line 826: `trade_info = self.trade_processor.infer_missing_fields(trade_info)`
- Line 890: `trade_info = self.trade_processor.infer_missing_fields(trade_info)`

## Validation
Run the validation test:
```bash
python3 test_inference_reassignment.py
```

This test verifies that all calls follow the correct pattern.

## Implementation Details
The `infer_missing_fields` method is defined in `trade_processor.py`:
- Takes `trade_info` dict as input
- Infers missing fields (dex, action, token_mint, etc.)
- Returns the updated dict

The TradeProcessor is initialized with `rpc_client`:
```python
self.trade_processor = TradeProcessor(self.target_wallets, self.rpc_client)
```

So the rpc_client is available via `self.rpc_client` within the method.

## Conclusion
The codebase already follows best practices for inference reassignment. The pattern ensures consistency and makes it clear that the returned dict (which is the same mutated object) is being used for subsequent operations.
