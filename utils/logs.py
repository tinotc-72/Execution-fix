from __future__ import annotations

def log_submit_result(dex: str, action: str, mint: str, res) -> None:
    try:
        print(f"DEX={dex} action={action} mint={mint} sig={res.signature} status={res.status} ok={res.ok}")
    except Exception:
        print(f"DEX={dex} action={action} mint={mint} [malformed SubmitResult]")
