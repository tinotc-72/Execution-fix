import requests
import base64
import pprint
import base58

def find_pump_instruction(transaction, log_messages):
    inner_ix = []
    parent_ix_stack = []
    ix_map = {}  # Map program invocations to instruction indices
    
    # First pass - identify instruction hierarchy
    for i, log in enumerate(log_messages):
        if "Program" in log and "invoke" in log:
            program = log.split()[1]
            depth = int(log.split('[')[1].split(']')[0])
            while len(parent_ix_stack) >= depth:
                parent_ix_stack.pop()
            parent_ix_stack.append((program, i))
            ix_map[i] = len(inner_ix)
            inner_ix.append(parent_ix_stack[-1])
    
    # Find the PUMP router instruction
    pump_index = -1
    pump_parent = None
    for i, log in enumerate(log_messages):
        if "Program BSfD6SHZ" in log and i+1 < len(log_messages) and "Instruction: PumpBuy" in log_messages[i+1]:
            pump_index = ix_map[i]
            break
    
    if pump_index >= 0:
        print(f"\nFound PUMP instruction at index {pump_index}")
        message = transaction.get("message", {})
        instructions = message.get("instructions", [])
        if pump_index < len(instructions):
            return pump_index
    return -1

# Transaction with successful PUMP buy
TX_SIG = "48Yp8uU4Gj2CtsWXQ1ZvgYxocANqtGuXWUkFJvUfAussrjxHk5AiULgVW19Hx1RPv2yLnGRdxzNHFxjeyWDCFwfs"

def get_tx_data():
    url = "https://api.mainnet-beta.solana.com"
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            TX_SIG,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

print("Fetching transaction data...")
result = get_tx_data()

if "result" not in result or not result["result"]:
    print("Failed to fetch transaction")
    exit(1)

tx_data = result["result"]

def find_pump_instruction(log_messages, instructions):
    pump_ix_index = -1
    for i, log in enumerate(log_messages):
        if "Program BSfD6SHZ" in log and "Instruction: PumpBuy" in log_messages[i+1]:
            # Count the number of "Program" invocations up to this point
            program_invokes = sum(1 for l in log_messages[:i] if "Program" in l and "invoke" in l)
            pump_ix_index = program_invokes - 1
            break
    return pump_ix_index

def extract_transaction_data(tx_data):
    try:
        transaction = tx_data.get("transaction", {})
        meta = tx_data.get("meta", {})
        log_messages = meta.get("logMessages", [])
        message = transaction.get("message", {})
        instructions = message.get("instructions", [])
        
        # Print all log messages first for debugging
        print("\nSearching through logs to find PUMP buy instruction:")
        for i, log in enumerate(log_messages):
            print(f"{i:2d}: {log}")
            
        # Find the PUMP instruction index by correlating log messages with instructions
        instruction_index = find_pump_instruction(log_messages, instructions)
        if instruction_index == -1:
            print("\nCouldn't find PUMP instruction in logs")
            return
        
        if instruction_index is None:
            print("No PUMP router instruction found!")
            return
        
        message = transaction.get("message", {})
        instructions = message.get("instructions", [])
        account_keys = message.get("accountKeys", [])
        
        if instruction_index >= len(instructions):
            print(f"Instruction index {instruction_index} out of range!")
            return
        
        # Get all instructions leading up to and including the target instruction
        print("\n🚀 PUMP Router Sequence Analysis:")
        print("=" * 50)

        print("Instructions found:")
        for i, ix in enumerate(instructions):
            if i > instruction_index:
                break
            print(f"\nInstruction {i}:")
            program_id = ix.get("programId")
            print(f"Program ID: {program_id}")
            
            # Decode data if present
            data = ix.get("data")
            if data:
                try:
                    data_bytes = base58.b58decode(data)
                    print("Data:")
                    print(f"  Base58: {data[:64]}...")
                    print(f"  Hex: {data_bytes.hex()[:64]}...")
                    if len(data_bytes) >= 8:
                        discriminator = data_bytes[:8].hex()
                        print(f"  Discriminator: {discriminator}")
                except:
                    print(f"  Raw: {data[:64]}...")
            
            # Print account info
            print("\nAccounts:")
            accounts = ix.get("accounts", [])
            for j, acc_index in enumerate(accounts):
                try:
                    signer = acc_index < (message.get("header", {}).get("numRequiredSignatures", 0))
                    writable = account_keys[acc_index] in message.get("header", {}).get("writableSignedAccounts", []) + message.get("header", {}).get("writableUnsignedAccounts", [])
                    print(f"  {j}: {account_keys[acc_index]} (signer: {signer}, writable: {writable})")
                except:
                    print(f"  {j}: Account index {acc_index}")
                    
            if i == instruction_index:
                print("\n✨ This is the target PUMP instruction!\n")
        
        # Print the full instruction, data, and all account metas for the PUMP buy instruction
        print(f"\n=== PUMP Buy Instruction at index {instruction_index} ===")
        ix = instructions[instruction_index]
        print(f"Program ID: {ix.get('programId')}")
        print(f"Data (base58): {ix.get('data')}")
        data_bytes = base58.b58decode(ix.get('data')) if ix.get('data') else b''
        print(f"Data (hex): {data_bytes.hex()}")
        print("Accounts:")
        for j, acc_index in enumerate(ix.get('accounts', [])):
            print(f"  {j}: {account_keys[acc_index]}")
        
        # Print log messages around this instruction
        print("\nRelevant Log Messages:")
        start_index = max(0, instruction_index - 2)
        end_index = min(len(log_messages), instruction_index + 3)
        for i in range(start_index, end_index):
            prefix = ">>> " if i == instruction_index else "    "
            print(f"{prefix}{log_messages[i]}")
            
    except Exception as e:
        print(f"Error analyzing transaction: {e}")

# Analyze the transaction
print("\nPUMP Router & Trade Instructions:")
print("=" * 50)
extract_transaction_data(tx_data)

# Print the full logs for context
print("\nFull Transaction Logs:")
print("=" * 50)
for log in tx_data.get("meta", {}).get("logMessages", []):
    print(log)
