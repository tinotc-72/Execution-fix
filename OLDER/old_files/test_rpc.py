"""
Quick script to test RPC connection
"""
import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

# Force reload of environment variables and use env_keys
from env_keys import kz
RPC_URL = kz.HELIUS_RPC_URL

async def test_rpc_connection():
    print("\n🔍 Testing RPC Configuration...")
    
    # 1. Check if RPC URL is configured
    rpc_url = RPC_URL
    print(f"📝 RPC URL configured as: {rpc_url if rpc_url else 'Not set'}")
    
    if not rpc_url:
        print("❌ Error: HELIUS_RPC_URL is not set in your .env file")
        return
        
    if not rpc_url.startswith(("http://", "https://")):
        print("❌ Error: RPC URL must start with http:// or https://")
        return
    
    if "api-key" not in rpc_url:
        print("❌ Error: RPC URL must include api-key parameter")
        return
        
    # 2. Test RPC connection
    print("\n🔄 Testing RPC connection...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getHealth",
                }
            )
            
            result = response.json()
            print(f"✅ RPC Response: {json.dumps(result, indent=2)}")
            
            # Test getting latest blockhash
            print("\n🔄 Testing getLatestBlockhash...")
            response = await client.post(
                rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                }
            )
            
            result = response.json()
            if "result" in result and "value" in result["result"]:
                print(f"✅ Latest blockhash: {result['result']['value']['blockhash']}")
            else:
                print(f"❌ Error getting blockhash: {json.dumps(result, indent=2)}")
                
    except httpx.ConnectError as e:
        print(f"❌ Connection Error: {str(e)}")
        print("\n🔍 Common solutions:")
        print("1. Check if your HELIUS_RPC_URL is correct")
        print("2. Verify your API key is valid")
        print("3. Ensure you have internet connectivity")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

async def test_rpc_performance():
    """Test RPC endpoint performance and reliability"""
    print("\n🔬 Testing RPC Performance")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Basic Connection
            print("\n1️⃣ Testing Basic Connection")
            start_time = asyncio.get_event_loop().time()
            
            response = await client.post(
                RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getHealth",
                }
            )
            
            latency = (asyncio.get_event_loop().time() - start_time) * 1000
            print(f"✓ Connection successful")
            print(f"📊 Latency: {latency:.2f}ms")
            
            # Test 2: Get Latest Blockhash
            print("\n2️⃣ Testing getLatestBlockhash")
            start_time = asyncio.get_event_loop().time()
            
            response = await client.post(
                RPC_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getLatestBlockhash",
                }
            )
            
            latency = (asyncio.get_event_loop().time() - start_time) * 1000
            result = response.json()
            print(f"✓ Got latest blockhash")
            print(f"📊 Latency: {latency:.2f}ms")
            
            # Test 3: Multiple Quick Requests
            print("\n3️⃣ Testing Multiple Quick Requests")
            latencies = []
            
            for i in range(5):
                start_time = asyncio.get_event_loop().time()
                response = await client.post(
                    RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getLatestBlockhash",
                    }
                )
                latency = (asyncio.get_event_loop().time() - start_time) * 1000
                latencies.append(latency)
                
            avg_latency = sum(latencies) / len(latencies)
            print(f"✓ Completed 5 quick requests")
            print(f"📊 Average Latency: {avg_latency:.2f}ms")
            print(f"📊 Min Latency: {min(latencies):.2f}ms")
            print(f"📊 Max Latency: {max(latencies):.2f}ms")
            
            if avg_latency > 500:
                print("⚠️ Warning: High average latency detected")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing RPC: {str(e)}")
        return False

async def main():
    """Main test function"""
    await test_rpc_connection()
    await test_rpc_performance()

if __name__ == "__main__":
    asyncio.run(main())
