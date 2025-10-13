
import requests
import base64

TX_SIG = "59eReUUMc2gmrgYqkMdJqaayXPPkqzD2vcZty2nwZogbiDjUkagTmeCFMxAcgm9MynuSPjcFAP3w1DSwCEJWZ37y"
RPC_URL = "https://api.mainnet-beta.solana.com"

def fetch_and_print_parsed_transaction(tx_sig: str):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_sig,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    response = requests.post(RPC_URL, json=payload)
    res_json = response.json()
    result = res_json.get("result")
    if not result:
        print("No transaction found.")
        return
    
    transaction = result.get("transaction")
    if not transaction:
        print("No transaction field.")
        return
    
    message = transaction.get("message")
    if not message:
        print("No message field.")
        return
    
    account_keys = message.get("accountKeys", [])
    print("\nAccount Keys:")
    for i, acc in enumerate(account_keys):
        pubkey = acc if isinstance(acc, str) else acc.get("pubkey")
        print(f"{i:3d}: {pubkey}")
    
    instructions = message.get("instructions", [])
    print("\nInstructions:")
    for i, ix in enumerate(instructions):
        program_id = ix.get("programId")
        accounts = ix.get("accounts", [])
        data = ix.get("data", "")
        print(f"\nInstruction {i}:")
        print(f"  Program ID: {program_id}")
        print(f"  Accounts ({len(accounts)}):")
        for acc in accounts:
            print(f"    {acc}")
        print(f"  Data (base64 or raw): {data}")
        print(f"  Data length: {len(data)}")

if __name__ == "__main__":
    fetch_and_print_parsed_transaction(TX_SIG)
