# Meteora Detection Implementation Flow

## 🔍 Detection Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│         parse_transaction(tx_data) - Entry Point            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract transaction structure (handle both formats)         │
│  tx = tx_data.get("transaction", {}) or tx_data             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: DEX Detection - Loop through instructions          │
│                                                              │
│  for ix in tx.get("message", {}).get("instructions"):       │
│      pid = ix.get("programId") or ix.get("program")         │
│                                                              │
│      if pid in METEORA_PROGRAM_IDS:                         │
│          ┌────────────────────────────────────────┐         │
│          │  parsed["dex"] = "meteora"             │         │
│          │                                         │         │
│          │  if parsed.get("action") in (None, "unknown"): │
│          │      parsed["action"] = "swap"         │         │
│          │                                         │         │
│          │  Log: "✅ [PARSER] Meteora detected"  │         │
│          │  break                                  │         │
│          └────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Wallet Address Extraction                          │
│                                                              │
│  signers = [k["pubkey"] for k in                            │
│             tx.get("message", {}).get("accountKeys")        │
│             if k.get("signer")]                             │
│                                                              │
│  if signers:                                                │
│      parsed["wallet_address"] = signers[0]                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Continue with standard DEX decoder flow...                 │
│  (identify_dex, dex_decoder.decode, etc.)                   │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Constant Definition

```python
# Lines 40-43
METEORA_PROGRAM_IDS = {
    "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",  # Meteora AMM
    "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN",  # Meteora alt
}
```

## 🎯 Key Features

### 1. Early Detection
- Meteora is detected **before** standard DEX identification
- Prevents fallback to "unknown" DEX
- Sets sensible defaults immediately

### 2. Dual Program ID Support
Both Meteora program IDs are detected:
- `Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB` (Meteora AMM)
- `dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN` (Meteora aggregator)

### 3. Action Override
- Sets `action="swap"` as default when Meteora detected
- Only applies if action is `None` or `"unknown"`
- Follows industry standard for AMM DEXs

### 4. Wallet Address Extraction
- Extracts from first signer in `transaction.message.accountKeys`
- Handles multiple signers (uses first)
- Gracefully handles no signers (leaves unset)

## ✅ Test Coverage

| Test File | Status | Coverage |
|-----------|--------|----------|
| `test_meteora_wallet_address.py` | ✅ PASS | Basic detection, return format |
| `test_meteora_both_program_ids.py` | ✅ PASS | Both program IDs, multiple signers |
| `verify_meteora_implementation.py` | ✅ PASS | Code verification, logging format |

## 🔧 Example Usage

```python
tx_data = {
    "signature": "5KqV...",
    "message": {
        "instructions": [
            {"programId": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"}
        ],
        "accountKeys": [
            {"pubkey": "9xQe...", "signer": True}
        ]
    }
}

result = parser.parse_transaction(tx_data)
# result["dex"] = "meteora"
# result["action"] = "swap"
# result["wallet_address"] = "9xQe..."
```

## 📊 Impact

### Before
```
⚠️ [PARSER] DEX=unknown after enhancement
Pipeline had to guess DEX type
No wallet_address extraction
```

### After
```
✅ [PARSER] Meteora detected: programId=Eo7WjKq6...
DEX correctly identified upfront
wallet_address properly extracted
```

## 🚀 Production Ready

- ✅ No breaking changes
- ✅ Backward compatible
- ✅ No new dependencies
- ✅ Comprehensive test coverage
- ✅ Follows existing patterns
- ✅ Clear logging for debugging
