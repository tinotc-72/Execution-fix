# Before/After: merge_parsed_fields Implementation

## Flow Comparison

### BEFORE ❌
```
1. Parse transaction
   ↓
2. Store parsed_tx
   ↓
3. Check signature → default if missing
   ↓
4. Check wallet_address → default to target_wallets[0] (WRONG!)
   ↓  
5. Check dex → default to 'unknown'
   ↓
6. Check action → default to 'unknown'
   ↓
7. Check mint → default to 'PENDING_ANALYSIS'
   ↓
8. Log missing fields

PROBLEM: Parser found fields (e.g., wallet_address='ABC', dex='meteora') 
         but they got overwritten by defaults!
```

### AFTER ✅
```
1. Parse transaction
   ↓
2. Store parsed_tx
   ↓
3. *** MERGE PARSED FIELDS *** (NEW!)
   - Copy dex if trade_info.dex is empty/unknown
   - Copy action if trade_info.action is empty/unknown
   - Copy wallet_address if empty/unknown
   - Copy token_mint/mint if empty/unknown
   - Copy signature if empty/unknown
   ↓
4. Check signature (just log if present)
   ↓
5. Check wallet_address → extract from TX signers if still missing
   ↓
6. Check what's STILL missing after merge
   ↓
7. Log only truly missing fields

RESULT: Parser fields preserved! Only report what's actually missing.
```

## Code Changes

### Helper Function Added
```python
def merge_parsed_fields(trade_info: dict, parsed: dict) -> None:
    """Merge parser fields into trade_info without clobbering."""
    if not parsed:
        return
    
    # Handle parsed_tx wrapper
    if isinstance(parsed.get("parsed_tx"), dict):
        parsed = parsed["parsed_tx"]
    
    # Map and merge fields
    mapping = {
        "dex": "dex",
        "action": "action", 
        "token_mint": "token_mint",
        "mint": "token_mint",
        "wallet_address": "wallet_address",
        "signature": "signature",
    }
    for src, dst in mapping.items():
        val = parsed.get(src)
        if val and trade_info.get(dst) in (None, "", "unknown", "PENDING_ANALYSIS"):
            trade_info[dst] = val
```

### Pipeline Changes

#### OLD wallet_address handling ❌
```python
if not trade_info.get('wallet_address'):
    missing_fields.append("wallet_address")
    logger.warning("[PIPELINE_ENTRY] Missing 'wallet_address', setting to first target wallet.")
    trade_info['wallet_address'] = self.target_wallets[0] if self.target_wallets else 'unknown'
```

#### NEW wallet_address handling ✅
```python
if not trade_info.get("wallet_address"):
    # Try first signer from the tx
    msg = (trade_info.get("transaction") or {}).get("message", {})
    signers = [k["pubkey"] for k in (msg.get("accountKeys") or []) if k.get("signer")]
    if signers:
        trade_info["wallet_address"] = signers[0]
        logger.info("[PIPELINE_ENTRY] Set wallet_address from tx signer: %s", signers[0])
    else:
        logger.warning("[PIPELINE_ENTRY] No signer in tx; leaving wallet_address empty")
```

#### OLD missing fields detection ❌
```python
missing_fields = []

if not sig or sig == "unknown":
    missing_fields.append("signature")
    
if not trade_info.get('wallet_address'):
    missing_fields.append("wallet_address")
    trade_info['wallet_address'] = self.target_wallets[0] if ...
    
if not trade_info.get('dex') and not trade_info.get('dex_type'):
    missing_fields.append("dex/dex_type")
    trade_info['dex'] = 'unknown'
    
# ... more individual checks ...

if missing_fields:
    logger.info(f"[PIPELINE_ENTRY] 📋 Missing/defaulted fields: {', '.join(missing_fields)}")
```

#### NEW missing fields detection ✅
```python
# Check what's STILL missing after merge and extraction
missing = []
for k in ("wallet_address", "dex", "action", "token_mint"):
    if trade_info.get(k) in (None, "", "unknown", "PENDING_ANALYSIS"):
        missing.append(k)
        
if missing:
    logger.info(f"[PIPELINE_ENTRY] 📋 Missing/defaulted fields: {', '.join(missing)}")
else:
    logger.info(f"[PIPELINE_ENTRY] ✅ All expected fields present")
```

## Example Scenarios

### Scenario 1: Parser finds everything
```python
# Parser result
parsed = {
    'dex': 'meteora',
    'action': 'swap',
    'wallet_address': 'ABC123...',
    'mint': 'TokenXYZ...'
}

# BEFORE: Fields would be overwritten with defaults
# trade_info['wallet_address'] = target_wallets[0]  # WRONG!
# trade_info['dex'] = 'unknown'                     # WRONG!

# AFTER: Parser fields preserved
merge_parsed_fields(trade_info, parsed)
# trade_info['wallet_address'] = 'ABC123...'  ✅
# trade_info['dex'] = 'meteora'              ✅
# missing = []                                ✅
```

### Scenario 2: Parser finds some, tx signers fill gap
```python
# Parser result
parsed = {
    'dex': 'meteora',
    'action': 'swap',
    # wallet_address NOT found by parser
}

# Step 1: Merge what parser found
merge_parsed_fields(trade_info, parsed)
# trade_info['dex'] = 'meteora'    ✅
# trade_info['action'] = 'swap'    ✅
# trade_info['wallet_address'] = None (not in parsed)

# Step 2: Extract wallet from tx signers
msg = transaction.get("message", {})
signers = [k["pubkey"] for k in msg.get("accountKeys", []) if k.get("signer")]
if signers:
    trade_info["wallet_address"] = signers[0]  ✅
    
# Result: All fields filled correctly!
# missing = []  ✅
```

### Scenario 3: Truly missing field
```python
# Parser result
parsed = {
    'dex': 'unknown',  # Parser couldn't determine
    'action': 'swap',
    'wallet_address': 'ABC123...',
}

# Transaction has no signers (edge case)
signers = []

# After merge and extraction
# trade_info['dex'] = 'unknown' (parser tried but failed)
# trade_info['wallet_address'] = 'ABC123...' (from parser)

# Missing detection
missing = []
for k in ("wallet_address", "dex", "action", "token_mint"):
    if trade_info.get(k) in (None, "", "unknown", "PENDING_ANALYSIS"):
        missing.append(k)
        
# missing = ['dex']  ✅
# Log: "[PIPELINE_ENTRY] 📋 Missing/defaulted fields: dex"
```

## Benefits Summary

✅ **Parser fields preserved** - No more clobbering  
✅ **Better wallet extraction** - Uses actual tx signers, not arbitrary defaults  
✅ **Cleaner code** - One loop vs multiple if/else blocks  
✅ **Accurate reporting** - Only logs truly missing fields  
✅ **No new dependencies** - Pure Python, existing imports  
✅ **Emoji logging maintained** - Same user-friendly format  
✅ **Fully tested** - Comprehensive test suite passes  

## Problem Statement Compliance

| Requirement | Status |
|-------------|--------|
| Add helper merge_parsed_fields | ✅ Done |
| Copy dex, action, token_mint/mint, wallet_address, signature | ✅ Done |
| Only if destination is empty/unknown/PENDING_ANALYSIS | ✅ Done |
| Call immediately after parsing | ✅ Done |
| Before "Missing/defaulted fields" logic | ✅ Done |
| Replace bad wallet_address defaulting | ✅ Done |
| Keep emoji logging | ✅ Done |
| No new dependencies | ✅ Done |
| Stay within existing rpc client | ✅ Done |
