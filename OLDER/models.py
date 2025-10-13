# models.py

from dataclasses import dataclass
from typing import List, Union, Optional
import traceback
from solders.transaction import Transaction, VersionedTransaction
from base58 import b58encode
from datetime import datetime, UTC

@dataclass
class TradeInfo:
    """Information about a trade detected from Wallet A"""
    type: str  # 'buy' or 'sell'
    token: str  # Token address
    amount: Optional[float]  # Amount in SOL (None for sells)
    signature: str  # Transaction signature
    program: str  # DEX program name
    timestamp: datetime = datetime.now(UTC)
    
    @property
    def is_buy(self) -> bool:
        return self.type.lower() == 'buy'

# models.py
@dataclass
class Bundle:
    """Bundle format following Jito docs: https://docs.jito.wtf/lowlatencytxnsend/#sendtransaction"""
    transactions: List[Union[Transaction, VersionedTransaction]]
    
    def to_json(self):
        """Convert to Jito API format for transaction submission"""
        try:
            if not self.transactions or len(self.transactions) == 0:
                print("❌ No transactions to send")
                return None
                
            timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] 📝 Encoding transaction...")
            
            tx = self.transactions[0]  # Get first transaction
            
            # Ensure transaction is versioned
            if not isinstance(tx, VersionedTransaction):
                print("❌ Transaction must be versioned")
                return None
                
            # Get transaction bytes and encode
            print("🔍 Converting transaction to wire format...")
            tx_bytes = bytes(tx)
            print(f"Transaction bytes length: {len(tx_bytes)}")
            
            # Verify account keys before encoding
            message = tx.message
            print("🔍 Verifying account keys:")
            for idx, key in enumerate(message.account_keys):
                print(f"  {idx}: {key} (signer: {idx < message.header.num_required_signatures})")
            
            encoded_tx = b58encode(tx_bytes).decode('utf-8')
            print(f"Base58 encoded length: {len(encoded_tx)}")
            
            # Format following Jito's API documentation
            bundle_json = {
                "transactions": [encoded_tx],
                "params": {
                    "maxRetries": 3,
                    "skipPreflight": True
                }
            }
            print(f"Base58 encoded length: {len(encoded_tx)}")
            
            # Format following Jito's API documentation
            tx_json = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [encoded_tx]
            }
            
            print(f"✅ Transaction JSON created")
            print(f"🔍 Transaction Details:")
            print(f"  - Method: {tx_json['method']}")
            print(f"  - Transaction Type: VersionedTransaction")
            print(f"  - Message Type: {tx.message.__class__.__name__}")
            print(f"  - Account Keys: {len(message.account_keys)}")
            print(f"  - Required Signatures: {message.header.num_required_signatures}")
            print(f"  - Encoded Length: {len(encoded_tx)}")
            
            return tx_json
            
        except Exception as e:
            print(f"❌ Transaction conversion failed: {str(e)}")
            traceback.print_exc()
            return None