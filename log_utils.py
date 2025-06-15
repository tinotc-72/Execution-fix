# log_utils.py

import re
import base64
import base58

def extract_mint_from_logs(logs: list[str]) -> str | None:
    """
    Extracts a likely mint address from base64-encoded `Program data:` logs.
    """
    for line in logs:
        if "Program data:" in line:
            try:
                encoded = line.split("Program data:")[1].strip()
                # Remove trailing padding or junk
                encoded = encoded.split(" ")[0]
                decoded = base64.b64decode(encoded + "==", validate=True)
                chunks = re.findall(rb".{32}", decoded)
                for chunk in chunks:
                    b58 = base58.b58encode(chunk).decode()
                    if b58 and len(b58) in range(32, 45):  # Typical Pubkey length
                        return b58
            except Exception as e:
                continue
    return None



def extract_curve_from_logs(logs: list[str]) -> str | None:
    """
    Extracts the bonding curve address from the log lines.
    Looks for base64 data blobs and applies the same logic as extract_mint_from_logs.
    Assumes both mint and curve are present, and curve comes after mint.
    """
    candidates = []

    for line in logs:
        if "data:" in line:
            try:
                encoded = line.split("data:")[1].strip()
                decoded = base64.b64decode(encoded)
                chunks = re.findall(rb".{32}", decoded)
                for chunk in chunks:
                    b58 = base58.b58encode(chunk).decode()
                    if b58 and len(b58) >= 32:
                        candidates.append(b58)
            except Exception:
                continue

    # Heuristically: 1st is mint, 2nd is likely curve (depends on structure)
    if len(candidates) >= 2:
        return candidates[1]
    elif candidates:
        return candidates[0]

    return None


def extract_amount_from_logs(logs: list[str]) -> int | None:
    """
    Placeholder for extracting amount from logs.
    Implement if logs contain raw numeric values (e.g. in base64 or plain).
    """
    return None  # You can replace this with a real parser when needed



