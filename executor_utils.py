"""
Utility functions for executor standardization to avoid circular imports.
"""

def exec_ok(executor_name: str, signature: str, details: dict | None = None):
    """Standard success result for executors"""
    return {"ok": True, "executor": executor_name, "signature": signature, "details": details or {}}

def exec_err(executor_name: str, error: str, details: dict | None = None):
    """Standard error result for executors"""
    return {"ok": False, "executor": executor_name, "error": error, "details": details or {}}

def is_success(result: dict | None) -> bool:
    """Check if executor result indicates success"""
    return bool(result and isinstance(result, dict) and result.get("ok") is True and isinstance(result.get("signature"), str))