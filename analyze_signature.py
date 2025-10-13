#!/usr/bin/env python3
"""
Analyze a specific transaction to extract fee recipient and account order for Pump.fun buy
"""
import httpx
import base64

SIGNATURE = "2zwXd6Ddv4xkDTBUmT3H9xd46ufwwx6Q1gMoqisYhV42UPzdE1JXv4Kp9GhcL6Vn8k6qT6LWVtKoXNSVK1pcqgGG"
RPC_URL = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
PUMP_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

print(f"🔍 Analyzing transaction: {SIGNATURE}")

resp = httpx.post(RPC_URL, json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTransaction",
    "params": [SIGNATURE, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
})

if resp.status_code != 200:
    print(f"❌ Error fetching transaction: {resp.status_code}")
    exit(1)

result = resp.json().get("result", {})
if not result:
    print("❌ No result in transaction fetch")
    exit(1)

transaction = result.get("transaction", {})
message = transaction.get("message", {})
account_keys = message.get("accountKeys", [])
if account_keys and isinstance(account_keys[0], dict):
    account_keys = [k["pubkey"] for k in account_keys]
instructions = message.get("instructions", [])

found = False


print("\nAll instructions in this transaction:")
known_protocols = {
    "Pump.fun program": "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
    "Router program": "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",
    "System program": "11111111111111111111111111111111",
    "ATA program": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",
    "Token program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "SysvarRent": "SysvarRent111111111111111111111111111111111",
}
known_fee_recipients = [
    "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV1T6NVswCLPVXdHy",  # your current
    "pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ",  # seen in this tx
]

for i, ix in enumerate(instructions):
    prog_id = ix.get("programId") or ix.get("programIdIndex")
    if isinstance(prog_id, int):
        prog_id_str = account_keys[prog_id]
    else:
        prog_id_str = prog_id
    data = ix.get("data")
    discriminator = None
    if data:
        try:
            raw = base64.b64decode(data)
            discriminator = raw[:8].hex()
        except Exception:
            discriminator = None
    else:
        discriminator = None
    accounts = ix.get("accounts", [])
    print(f"\nInstruction {i}:")
    print(f"  Program ID: {prog_id_str}")
    for label, addr in known_protocols.items():
        if prog_id_str == addr:
            print(f"    [Protocol: {label}]")
    print(f"  Discriminator (first 8 bytes): {discriminator}")
    print(f"  Accounts:")
    for idx, acc_idx in enumerate(accounts):
        if isinstance(acc_idx, int) and acc_idx < len(account_keys):
            acc = account_keys[acc_idx]
            role = []
            for label, addr in known_protocols.items():
                if acc == addr:
                    role.append(label)
            if acc in known_fee_recipients:
                role.append("Known fee recipient")
            role_str = f" ({', '.join(role)})" if role else ""
            print(f"    [{idx}] {acc}{role_str}")
        else:
            print(f"    [{idx}] {acc_idx}")

print("\nSummary of likely roles for router instruction (Instruction 2):")
if len(instructions) > 2:
    router_ix = instructions[2]
    router_accounts = router_ix.get("accounts", [])
    for idx, acc_idx in enumerate(router_accounts):
        if isinstance(acc_idx, int) and acc_idx < len(account_keys):
            acc = account_keys[acc_idx]
            role = []
            for label, addr in known_protocols.items():
                if acc == addr:
                    role.append(label)
            if acc in known_fee_recipients:
                role.append("Known fee recipient")
            role_str = f" ({', '.join(role)})" if role else ""
            print(f"  [{idx}] {acc}{role_str}")
