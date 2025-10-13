# transaction_monitor.py

def is_from_wallet_a(tx_data, wallet_a_address: str) -> bool:
    """
    Check if a transaction is from Wallet A by examining the transaction data
    
    Args:
        tx_data: The transaction data received from the websocket
        wallet_a_address: The public key of Wallet A we're monitoring
    
    Returns:
        bool: True if transaction is from Wallet A, False otherwise
    """
    try:
        # Debug output
        print(f"\n🔍 Analyzing transaction for Wallet A: {wallet_a_address}")

        # Check websocket notification format
        if "params" in tx_data and "result" in tx_data["params"]:
            logs = tx_data["params"]["result"]["value"].get("logs", [])
            
            # Print first few logs for debugging
            print("\n📜 Transaction Logs Preview:")
            for log in logs[:5]:
                print(f"   {log}")

            # Look for Pump.fun program invocations
            pump_program_ids = [
                "BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW",  # Pump.fun router
                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"    # Pump.fun core
            ]
            
            pump_instructions = ["PumpBuy", "PumpSell", "PumpAmmSwap"]
            is_pump_tx = False
            
            # First verify this is a Pump transaction
            for log in logs:
                if any(prog_id in log for prog_id in pump_program_ids) or \
                   any(instr in log for instr in pump_instructions):
                    is_pump_tx = True
                    print("✅ Detected Pump.fun transaction")
                    break
            
            if is_pump_tx:
                # For Pump transactions, check account list in program invocations
                for log in logs:
                    if wallet_a_address in log:
                        print(f"✅ Found Wallet A in transaction logs")
                        return True

        # Fallback: Check transaction format
        if "transaction" in tx_data:
            if isinstance(tx_data["transaction"], dict):
                # JSON transaction format
                message = tx_data["transaction"].get("message", {})
                account_keys = message.get("accountKeys", [])
                for account in account_keys:
                    if account == wallet_a_address:
                        print(f"✅ Found Wallet A in account keys")
                        return True
                        
            elif isinstance(tx_data["transaction"], list) and len(tx_data["transaction"]) > 1:
                # Base64 encoded transaction
                account_keys = tx_data["transaction"][1].get("accountKeys", [])
                for account in account_keys:
                    if account == wallet_a_address:
                        print(f"✅ Found Wallet A in account keys")
                        return True

        print("❌ Wallet A not found in transaction")
        return False

    except Exception as e:
        print(f"❌ Error checking wallet A transaction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def decode_transaction_accounts(tx_data) -> list:
    """
    Decode and return the accounts involved in a transaction
    
    Args:
        tx_data: The transaction data
        
    Returns:
        list: List of account public keys involved in the transaction
    """
    try:
        if 'message' in tx_data and 'accountKeys' in tx_data['message']:
            return tx_data['message']['accountKeys']
        return []
    except Exception as e:
        print(f"❌ Error decoding transaction accounts: {str(e)}")
        return []

def get_transaction_program_ids(tx_data) -> list:
    """
    Extract program IDs from a transaction
    
    Args:
        tx_data: The transaction data
        
    Returns:
        list: List of program IDs involved in the transaction
    """
    try:
        program_ids = []
        if 'transaction' in tx_data and len(tx_data['transaction']) > 0:
            instructions = tx_data['transaction'][0].get('instructions', [])
            for ix in instructions:
                if 'programId' in ix:
                    program_ids.append(ix['programId'])
        return program_ids
    except Exception as e:
        print(f"❌ Error getting program IDs: {str(e)}")
        return []

def log_transaction_details(tx_data):
    """
    Log detailed information about a transaction
    
    Args:
        tx_data: The transaction data to log
    """
    try:
        print("\n📊 Transaction Details:")
        
        # Log signature if available
        if 'signature' in tx_data:
            print(f"🔑 Signature: {tx_data['signature'][:8]}...")
            
        # Log accounts involved
        accounts = decode_transaction_accounts(tx_data)
        if accounts:
            print(f"👥 Accounts involved: {len(accounts)}")
            for i, account in enumerate(accounts):
                print(f"  {i+1}. {account}")
                
        # Log program IDs
        program_ids = get_transaction_program_ids(tx_data)
        if program_ids:
            print(f"🏗️ Programs called: {len(program_ids)}")
            for i, pid in enumerate(program_ids):
                print(f"  {i+1}. {pid}")
                
    except Exception as e:
        print(f"❌ Error logging transaction details: {str(e)}")

def analyze_transaction_type(tx_data) -> str:
    """
    Analyze and return the type of transaction based on program IDs and accounts
    
    Args:
        tx_data: The transaction data
        
    Returns:
        str: Description of transaction type
    """
    try:
        program_ids = get_transaction_program_ids(tx_data)
        
        # Common program IDs
        TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        SYSTEM_PROGRAM = "11111111111111111111111111111111"
        
        if TOKEN_PROGRAM in program_ids:
            return "Token Transaction"
        elif SYSTEM_PROGRAM in program_ids:
            return "System Program Transaction"
        else:
            return "Unknown Transaction Type"
            
    except Exception as e:
        print(f"❌ Error analyzing transaction type: {str(e)}")
        return "Error Analyzing Transaction"

def is_high_priority_transaction(tx_data) -> bool:
    """
    Determine if a transaction should be treated as high priority
    
    Args:
        tx_data: The transaction data
        
    Returns:
        bool: True if high priority, False otherwise
    """
    try:
        # Check for compute budget instructions that might indicate priority
        if 'transaction' in tx_data and len(tx_data['transaction']) > 0:
            instructions = tx_data['transaction'][0].get('instructions', [])
            for ix in instructions:
                if ix.get('programId') == 'ComputeBudget111111111111111111111111111111':
                    return True
                    
        return False
        
    except Exception as e:
        print(f"❌ Error checking transaction priority: {str(e)}")
        return False

def debug_transaction_verification(tx_data, wallet_a_address: str) -> None:
    """
    Print detailed debug information about transaction verification
    """
    print("\n🔍 DEBUG: Transaction Verification")
    print(f"Looking for wallet: {wallet_a_address}")
    
    if "params" in tx_data and "result" in tx_data["params"]:
        result = tx_data["params"]["result"]
        if "value" in result:
            value = result["value"]
            if "signature" in value:
                print(f"Transaction signature: {value['signature']}")
            if "logs" in value:
                print("\nRelevant logs:")
                pump_logs = [log for log in value["logs"] if any(x in log for x in ["PumpBuy", "PumpSell", "PumpAmmSwap"])]
                for log in pump_logs:
                    print(f"  {log}")
                data_logs = [log for log in value["logs"] if log.startswith("Program data:")]
                if data_logs:
                    print("\nProgram data logs found:", len(data_logs))
                
    if "transaction" in tx_data:
        print("\nTransaction format:", type(tx_data["transaction"]))
        if isinstance(tx_data["transaction"], list):
            print("List transaction format, length:", len(tx_data["transaction"]))
            if len(tx_data["transaction"]) > 1:
                print("Account keys in transaction[1]:", tx_data["transaction"][1].get("accountKeys", []))
        elif isinstance(tx_data["transaction"], dict):
            print("Dict transaction format")
            message = tx_data["transaction"].get("message", {})
            print("Account keys in message:", message.get("accountKeys", []))