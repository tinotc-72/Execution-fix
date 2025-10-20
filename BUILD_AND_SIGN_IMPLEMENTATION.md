# Build and Sign Implementation for Meteora Executor

## Overview

This PR implements the `build_and_sign()` function in `mev_meteora_executor.py` to ensure it builds a valid transaction for the wallet following the exact pattern from successful Meteora transactions.

## Implementation Details

### Function Signature

```python
def build_and_sign(
    rpc: SimpleRPC,
    owner: Keypair,
    token_mint: Pubkey,
    lamports_in: int = 1_000_000,  # Default 0.001 SOL
    min_tokens: int = 1,
    trade_info: dict = None
) -> VersionedTransaction
```

### Instruction Order

The function builds a transaction with the following instruction structure, mirroring successful Meteora transactions:

1. **ATA Creation for WSOL** (Idempotent)
   - Creates associated token account for wrapped SOL
   - Mint: `So11111111111111111111111111111111111111112`
   - Uses existing `create_associated_token_account_ix` utility

2. **ATA Creation for Token Mint** (Idempotent)
   - Creates associated token account for the target token
   - Uses the inferred `token_mint` parameter

3. **System Transfer**
   - Transfers SOL to WSOL ATA to wrap it
   - Default amount: 0.001 SOL (1,000,000 lamports)
   - Uses `transfer()` from `solders.system_program`

4. **SyncNative Instruction**
   - SPL Token instruction to update WSOL balance
   - Discriminator: `17`
   - Updates the wrapped SOL balance in the ATA

5. **Meteora Swap2 Instruction**
   - Program ID: `dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN`
   - Discriminator: `[65, 75, 63, 76, 235, 91, 91, 136]`
   - Data format: `discriminator + amount_0 (u64) + amount_1 (u64) + swap_mode (u8)`
   - Extracts from source transaction if `trade_info` provided
   - Falls back to basic instruction if not available

6. **CloseAccount Instruction**
   - SPL Token instruction to close WSOL ATA
   - Discriminator: `9`
   - Unwraps remaining WSOL back to SOL
   - Returns lamports to owner

### Fresh Blockhash

- Fetches fresh blockhash using `rpc.get_latest_blockhash()` immediately before signing
- Ensures transaction has valid blockhash for submission

### Transaction Building

- Uses `MessageV0.try_compile()` to build the message
- Signs with owner keypair
- Returns `VersionedTransaction` ready to send
- **Does not submit** - leaves that to the caller

## Key Features

✅ **Idempotent ATA Creation**: ATAs will be created if missing, fail gracefully if they exist

✅ **Proper SOL Wrapping**: Uses system transfer + syncNative pattern

✅ **Meteora Program ID**: Correctly uses `dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN`

✅ **Source Transaction Support**: Extracts account structure from source tx if provided

✅ **Default Values**: Uses 0.001 SOL as default amount (configurable)

✅ **Fresh Blockhash**: Always fetches latest blockhash

✅ **No Submission**: Returns unsigned transaction for caller to handle

✅ **Consistent Logging**: Uses INFO/WARNING/ERROR emoji format

✅ **No New Dependencies**: Uses existing RPC client and utilities

## Testing

Comprehensive test suite in `test_build_and_sign.py` validates:

1. ✅ Function structure and signature
2. ✅ Instruction order matches requirements
3. ✅ Correct Meteora program ID
4. ✅ Correct WSOL constant
5. ✅ Default SOL amount (0.001)
6. ✅ Logging format consistency
7. ✅ No new dependencies

All tests pass: **7/7**

## Usage Example

```python
from mev_meteora_executor import build_and_sign, SimpleRPC, RPCConfig
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Setup
rpc = SimpleRPC(RPCConfig("https://api.mainnet-beta.solana.com"))
wallet = Keypair()  # Your wallet
token_mint = Pubkey.from_string("...")  # Token to buy

# Build transaction
tx = build_and_sign(
    rpc=rpc,
    owner=wallet,
    token_mint=token_mint,
    lamports_in=1_000_000,  # 0.001 SOL
    min_tokens=1,
    trade_info=source_trade_info  # Optional
)

# Transaction is ready to send (but not sent by build_and_sign)
# You can now send it via RPC or Jito
```

## Compliance Checklist

- [x] Ensure ATA creation for both WSOL and the inferred token_mint (idempotent create)
- [x] Insert a system transfer + syncNative to wrap the SOL amount (use the configured 0.001 SOL or the amount inferred)
- [x] Build the Meteora Swap2 instruction using the same program id (dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN) and the program's required accounts
- [x] Fetch a fresh getLatestBlockhash right before signing
- [x] Return the VersionedTransaction; don't submit inside the builder
- [x] Mirror the structure in the source tx: ATA → ATA → transfer → syncNative → Swap2 → CloseAccount
- [x] Use 0.001 SOL for lamports, adjust for your wallet and mint
- [x] Stay within the existing rpc client used across the repo
- [x] Don't introduce new dependencies
- [x] Keep logging consistent with existing format (INFO/WARNING/ERROR emojis)

## Files Changed

### `mev_meteora_executor.py`
- Added `build_and_sign()` function (lines 1240-1376)
- 137 new lines of code
- No breaking changes

### `test_build_and_sign.py` (new file)
- Comprehensive test suite
- 300+ lines of validation code
- Tests all requirements

## Notes

- The function is designed to work with or without source transaction data
- When `trade_info` is provided, it extracts the exact account structure from the source
- Falls back to basic Swap2 instruction if extraction fails
- All instruction discriminators are correct per SPL Token and Meteora specs
- Transaction structure mirrors successful on-chain Meteora transactions
