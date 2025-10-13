import asyncio
from solana.rpc.async_api import AsyncClient
from solders.signature import Signature
from env_keys import kz

async def analyze_logs(signature: str):
    print(f"Analyzing logs for transaction: {signature}")
    client = AsyncClient(kz.HELIUS_RPC_URL)
    
    # Get transaction with all details including logs
    tx_resp = await client.get_transaction(
        Signature.from_string(signature),
        max_supported_transaction_version=0
    )
    
    if not tx_resp.value:
        print("Transaction not found")
        return
    
    if tx_resp.value.meta and tx_resp.value.meta.log_messages:
        print("\n=== LOG MESSAGES ===")
        for log in tx_resp.value.meta.log_messages:
            print(log)
    
    await client.close()

if __name__ == "__main__":
    # Analyze successful transaction
    signature = "3tvDHHa4oQusyksBi1T3QCo89fNyW7TqY1YB9iPWEbm19UNhHCCWNo2uXrHqmUec8B6jMfqgEiXJ9gmdwh184FYa"
    asyncio.run(analyze_logs(signature))
