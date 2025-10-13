# models.py

from dataclasses import dataclass, field
from typing import List, Union
import traceback
from solders.transaction import Transaction, VersionedTransaction
from base58 import b58encode
from base64 import b64encode
from datetime import datetime, UTC

@dataclass
class WalletPosition:
    """Track position for a specific token"""
    token_mint: str
    initial_amount: float = 0.0
    current_amount: float = 0.0
    our_amount: float = 0.0
    entry_price: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

# models.py
@dataclass
class Bundle:
    """Bundle format following Jito docs: https://docs.jito.wtf/lowlatencytxnsend/#sendtransaction"""
    transactions: List[Union[Transaction, VersionedTransaction]]
    
    def to_json(self):
        """Convert to Jito API format for bundle submission following official documentation"""
        try:
            if not self.transactions or len(self.transactions) == 0:
                print("❌ No transactions to send")
                return None
                
            timestamp = "2025-06-09 19:44:27"
            print(f"[{timestamp}] 📝 Encoding bundle with {len(self.transactions)} transaction(s)...")
            
            # Encode all transactions in the bundle
            encoded_transactions = []
            
            for idx, tx in enumerate(self.transactions):
                # Ensure transaction is versioned
                if not isinstance(tx, VersionedTransaction):
                    print(f"❌ Transaction {idx} must be versioned")
                    return None
                    
                # Get transaction bytes and encode
                print(f"🔍 Converting transaction {idx} to wire format...")
                tx_bytes = bytes(tx)
                print(f"Transaction {idx} bytes length: {len(tx_bytes)}")
                
                # Verify account keys before encoding
                message = tx.message
                print(f"🔍 Verifying account keys for transaction {idx}:")
                for key_idx, key in enumerate(message.account_keys):
                    print(f"  {key_idx}: {key} (signer: {key_idx < message.header.num_required_signatures})")
                
                encoded_tx = b64encode(tx_bytes).decode('utf-8')
                encoded_transactions.append(encoded_tx)
                print(f"Base64 encoded length for tx {idx}: {len(encoded_tx)}")
            
            # Format following Jito's sendBundle API documentation
            bundle_json = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendBundle",
                "params": [
                    encoded_transactions,
                    {
                        "encoding": "base64"
                    }
                ]
            }
            
            print(f"✅ Bundle JSON created")
            print(f"🔍 Bundle Details:")
            print(f"  - Method: {bundle_json['method']}")
            print(f"  - Transaction Count: {len(encoded_transactions)}")
            print(f"  - Encoding: base64")
            print(f"  - Total Encoded Size: {sum(len(tx) for tx in encoded_transactions)} chars")
            
            return bundle_json
            
        except Exception as e:
            print(f"❌ Bundle conversion failed: {str(e)}")
            traceback.print_exc()
            return None