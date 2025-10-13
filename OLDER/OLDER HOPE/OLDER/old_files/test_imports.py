"""Test script to verify Solana and Solders package imports."""

print("Testing Solana package imports...")
try:
    import solana
    print("✓ Base solana package")
    
    from solana.rpc.api import Client
    print("✓ solana.rpc.api")
    
    from solana.transaction import Transaction
    print("✓ solana.transaction")
    
except ImportError as e:
    print(f"❌ Error importing Solana package: {e}")

print("\nTesting Solders package imports...")
try:
    import solders
    print("✓ Base solders package")
    
    from solders import keypair
    print("✓ solders.keypair")
    
    from solders import pubkey
    print("✓ solders.pubkey")
    
    from solders import instruction
    print("✓ solders.instruction")
    
    from solders import transaction
    print("✓ solders.transaction")
    
    from solders import message
    print("✓ solders.message")
    
    from solders import compute_budget
    print("✓ solders.compute_budget")
    
except ImportError as e:
    print(f"❌ Error importing Solders package: {e}")
