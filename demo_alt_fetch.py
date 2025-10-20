#!/usr/bin/env python3
"""
Demonstration of synchronous ALT fetch helpers usage.

This script shows how to use the synchronous ALT helpers in utils/alt_fetch.py
for fetching and building Address Lookup Table accounts.
"""
import logging
from unittest.mock import patch, MagicMock
from utils.alt_fetch import fetch_lookup_table, build_alts_from_tables
from solders.message import MessageV0
from solders.instruction import Instruction
from solders.hash import Hash
from solders.keypair import Keypair
from solders.pubkey import Pubkey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_basic_usage():
    """Demonstrate basic usage of ALT fetch helpers"""
    print("\n" + "="*70)
    print("DEMO 1: Basic ALT Fetching")
    print("="*70 + "\n")
    
    # Mock RPC for demonstration
    with patch('utils.alt_fetch.requests.post') as mock_post:
        # Simulate a successful getAddressLookupTable response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "value": {
                    "addresses": [
                        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                        "11111111111111111111111111111111",
                        "So11111111111111111111111111111111111111112"
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        rpc_url = "http://example-rpc.com"
        alt_address = "AddressLookupTab1e1111111111111111111111111"
        
        print(f"Fetching ALT: {alt_address}")
        addresses = fetch_lookup_table(rpc_url, alt_address)
        
        print(f"\n✅ Successfully fetched {len(addresses)} addresses:")
        for i, addr in enumerate(addresses, 1):
            print(f"   {i}. {addr}")
    
    print()


def demo_build_alts():
    """Demonstrate building AddressLookupTableAccount objects"""
    print("\n" + "="*70)
    print("DEMO 2: Building AddressLookupTableAccount Objects")
    print("="*70 + "\n")
    
    with patch('utils.alt_fetch.fetch_lookup_table') as mock_fetch:
        # Mock multiple ALTs
        mock_fetch.side_effect = [
            ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"],
            ["11111111111111111111111111111111", "So11111111111111111111111111111111111111112"],
        ]
        
        rpc_url = "http://example-rpc.com"
        table_pubkeys = [
            "AddressLookupTab1e1111111111111111111111111",
            "AddressLookupTab1e2222222222222222222222222"
        ]
        
        print(f"Building ALT accounts for {len(table_pubkeys)} tables...")
        alts = build_alts_from_tables(rpc_url, table_pubkeys)
        
        print(f"\n✅ Successfully built {len(alts)} AddressLookupTableAccount objects:")
        for i, alt in enumerate(alts, 1):
            print(f"   ALT {i}:")
            print(f"      Key: {alt.key}")
            print(f"      Addresses: {len(alt.addresses)}")
    
    print()


def demo_v0_transaction_cloning():
    """Demonstrate using ALTs for v0 transaction cloning"""
    print("\n" + "="*70)
    print("DEMO 3: V0 Transaction Cloning with ALTs")
    print("="*70 + "\n")
    
    # Simulate a v0 transaction structure
    mock_tx_data = {
        "transaction": {
            "message": {
                "accountKeys": [
                    {"pubkey": "11111111111111111111111111111111", "signer": True, "writable": True}
                ],
                "addressTableLookups": [
                    {
                        "accountKey": "AddressLookupTab1e1111111111111111111111111",
                        "writableIndexes": [0],
                        "readonlyIndexes": [1, 2]
                    }
                ]
            }
        }
    }
    
    print("Step 1: Detect v0 transaction")
    message = mock_tx_data["transaction"]["message"]
    address_table_lookups = message.get("addressTableLookups", [])
    
    if address_table_lookups:
        print(f"   ✅ Detected v0 transaction with {len(address_table_lookups)} ALT(s)")
    else:
        print("   ℹ️  No ALTs detected (legacy transaction)")
    
    print("\nStep 2: Extract ALT addresses")
    table_pubkeys = [lookup["accountKey"] for lookup in address_table_lookups]
    for i, pubkey in enumerate(table_pubkeys, 1):
        print(f"   {i}. {pubkey}")
    
    print("\nStep 3: Fetch and build ALT accounts")
    with patch('utils.alt_fetch.fetch_lookup_table') as mock_fetch:
        mock_fetch.return_value = [
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "11111111111111111111111111111111"
        ]
        
        rpc_url = "http://example-rpc.com"
        alts = build_alts_from_tables(rpc_url, table_pubkeys)
        print(f"   ✅ Built {len(alts)} AddressLookupTableAccount object(s)")
    
    print("\nStep 4: Create MessageV0 with ALTs")
    payer = Keypair()
    instruction = Instruction(
        program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
        accounts=[],
        data=bytes([])
    )
    blockhash = Hash.default()
    
    message_v0 = MessageV0.try_compile(
        payer.pubkey(),
        [instruction],
        alts,
        blockhash
    )
    print("   ✅ MessageV0 created successfully with ALTs")
    
    print("\nStep 5: Create VersionedTransaction")
    from solders.transaction import VersionedTransaction
    tx = VersionedTransaction(message=message_v0, keypairs=[payer])
    print("   ✅ VersionedTransaction created and signed")
    
    print()


def demo_integration_pattern():
    """Demonstrate the recommended integration pattern"""
    print("\n" + "="*70)
    print("DEMO 4: Recommended Integration Pattern")
    print("="*70 + "\n")
    
    print("Code pattern for clone/submit paths:\n")
    print("```python")
    print("# 1. Check for Address Lookup Tables")
    print("address_table_lookups = message.get('addressTableLookups', [])")
    print("address_lookup_tables = []")
    print()
    print("if address_table_lookups:")
    print("    # 2. Extract ALT addresses")
    print("    table_pubkeys = [lookup['accountKey'] for lookup in address_table_lookups]")
    print()
    print("    # 3. Fetch and build ALTs (synchronous)")
    print("    from utils.alt_fetch import build_alts_from_tables")
    print("    address_lookup_tables = build_alts_from_tables(rpc_url, table_pubkeys)")
    print()
    print("    # OR for async code:")
    print("    # from utils.alts import alts_from_lookups")
    print("    # address_lookup_tables = await alts_from_lookups(rpc_url, address_table_lookups)")
    print()
    print("# 4. Build message based on ALT presence")
    print("if address_lookup_tables:")
    print("    # Use MessageV0 for transactions with ALTs")
    print("    from solders.message import MessageV0")
    print("    new_message = MessageV0.try_compile(")
    print("        payer_pubkey,")
    print("        instructions,")
    print("        address_lookup_tables,")
    print("        recent_blockhash")
    print("    )")
    print("else:")
    print("    # Use legacy Message for transactions without ALTs")
    print("    new_message = Message.new_with_blockhash(")
    print("        instructions,")
    print("        payer_pubkey,")
    print("        recent_blockhash")
    print("    )")
    print("```")
    print()


def main():
    """Run all demonstrations"""
    print("\n" + "🚀"*35)
    print("SYNCHRONOUS ALT FETCH HELPERS DEMONSTRATIONS")
    print("🚀"*35)
    
    demo_basic_usage()
    demo_build_alts()
    demo_v0_transaction_cloning()
    demo_integration_pattern()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    print("✅ Demonstrated basic ALT fetching")
    print("✅ Demonstrated building AddressLookupTableAccount objects")
    print("✅ Demonstrated v0 transaction cloning workflow")
    print("✅ Provided recommended integration pattern")
    print()
    print("KEY POINTS:")
    print("   • Use message.addressTableLookups (not meta.loadedAddresses)")
    print("   • Use synchronous helpers for sync code, async helpers for async code")
    print("   • Pass ALTs to MessageV0.try_compile()")
    print("   • Fall back to legacy Message for non-v0 transactions")
    print()
    print("🎉 Ready to use synchronous ALT fetch helpers in production!")


if __name__ == "__main__":
    main()
