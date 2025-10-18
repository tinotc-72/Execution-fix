from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from solders.transaction import VersionedTransaction

@dataclass
class BuildResult:
    ok: bool
    tx: Optional[VersionedTransaction]
    reason: Optional[str] = None
    dex: Optional[str] = None
    action: Optional[str] = None
