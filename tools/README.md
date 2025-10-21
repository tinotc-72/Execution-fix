# Execution Pipeline Tools

This directory contains diagnostic and maintenance tools for the execution pipeline.

## diagnose_execution_pipeline.py

**Purpose:** Static analysis tool that scans the repository for execution pipeline failures and produces a structured Markdown report.

**Usage:**
```bash
python tools/diagnose_execution_pipeline.py
```

**Output:**
- Prints summary to stdout
- Generates `docs/PIPELINE_DIAGNOSTIC.md` with detailed findings

**Checks Performed:**
1. **ATA Issues**
   - Placeholder ATA PDA derivation (should use `Pubkey.find_program_address`)
   - `ensure_ata_for` using 'exists' boolean instead of RPC query
   - Improper signer/owner in create_associated_token_account

2. **BuildResult Issues**
   - Functions returning None instead of BuildResult
   - Missing BuildResult imports

3. **Transaction Building Issues**
   - `MessageV0.compile` missing address_lookup_tables parameter
   - Missing `build_alts_from_tables` calls
   - `with_compute_budget` called after MessageV0.compile (should be before)
   - Instruction.data constructed as list instead of bytes
   - Missing `get_recent_blockhash` usage

4. **Submission Issues**
   - Raw submission calls (sendTransaction, sendRawTransaction, requests.post)
   - Should use `send_and_confirm_v0_tx` from executors.submit

5. **Code Quality Issues**
   - Scaffold/nonfunctional executors not gated behind config flags
   - Usage of solana-py imports (should use solders)

**Features:**
- Read-only analysis (does not modify files)
- Idempotent execution
- Prioritized findings (HIGH, MEDIUM, LOW severity)
- Per-file and per-category breakdowns
- Actionable remediation suggestions with code examples

**Example Output:**
```
================================================================================
EXECUTION PIPELINE DIAGNOSTIC SUMMARY
================================================================================

Total Issues Found: 402
  - HIGH severity:   108
  - MEDIUM severity: 26
  - LOW severity:    268

Top Issues by Category:
  - SOLANA_PY_IMPORT: 268
  - RAW_SUBMISSION: 57
  - NONE_RETURN: 37
  ...
```

See `docs/PIPELINE_DIAGNOSTIC.md` for the full detailed report.
