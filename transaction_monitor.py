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
        # Get transaction message
        if not tx_data or 'transaction' not in tx_data:
            return False
            
        # Check if the transaction contains account keys
        transaction = tx_data['transaction']
        if not transaction or len(transaction) < 1:
            return False

        # Check if the first signer (fee payer) is Wallet A
        if 'message' in tx_data and 'accountKeys' in tx_data['message']:
            account_keys = tx_data['message']['accountKeys']
            if account_keys and len(account_keys) > 0:
                fee_payer = account_keys[0]
                return fee_payer == wallet_a_address

        return False

    except Exception as e:
        print(f"❌ Error checking wallet A transaction: {str(e)}")
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