# generate_tx_solscan.py

import base64
from solders.transaction import VersionedTransaction

def fix_base64_padding(s: str) -> str:
    return s + "=" * ((4 - len(s) % 4) % 4)

raw_tx_base64 = "<your_base64_string_here>"
raw_tx_base64 = raw_tx_base64.strip().replace("\n", "").replace(" ", "")
raw_tx_base64 = fix_base64_padding(raw_tx_base64)

tx_bytes = base64.b64decode(raw_tx_base64)
tx = VersionedTransaction.from_bytes(tx_bytes)

resolved_message = tx.message.resolve()

print(f"Signatures: {[sig.to_bytes().hex() for sig in tx.signatures]}")

print("Instructions:")
for idx, instr in enumerate(resolved_message.instructions):
    print(f"Instruction {idx}:")
    print(f"  Program ID: {instr.program_id}")
    print(f"  Accounts:")
    for account in instr.accounts:
        print(f"    {account.pubkey} (signer={account.is_signer}, writable={account.is_writable})")
    print(f"  Data (hex): {instr.data.hex()}")



