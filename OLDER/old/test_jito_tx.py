#!/usr/bin/env python3

import asyncio
import logging
import base58
from solders.keypair import Keypair
from models import Bundle
from jito_service import JitoClient
from fast_executor import FastExecutor
from config import kz
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_jito.log'),
        logging.StreamHandler()
    ]
)

async def test_jito_latency():
    """Test Jito low-latency transaction submission"""
    try:
        print("\n🔍 Testing Jito Low-Latency Transaction Submission")
        print("===============================================")
        
        # Initialize clients for both regions
        london_client = JitoClient(region="london")
        ny_client = JitoClient(region="ny")
        
        await london_client.initialize()
        await ny_client.initialize()
        
        # Load test wallet
        key = kz.BULLX_NEO_PRIVATE_KEY_QM.strip()
        keypair = Keypair.from_bytes(base58.b58decode(key))
        print(f"\n🔑 Using test wallet: {keypair.pubkey()}")
        
        # Create executor
        executor = FastExecutor(keypair)
        
        # Test transaction structure
        test_bundle = Bundle(
            transactions=[],  # We'll create this in the full test
            keypair=keypair
        )
        
        # Test next slot retrieval
        print("\n⏰ Testing next slot retrieval:")
        london_slot = await london_client.get_next_slot()
        ny_slot = await ny_client.get_next_slot()
        
        print(f"London next slot: {london_slot}")
        print(f"NY next slot: {ny_slot}")
        
        # Test latency to each endpoint
        print("\n⚡ Testing submission latency:")
        
        async def measure_latency(client, region):
            start = time.perf_counter()
            slot = await client.get_next_slot()
            elapsed = (time.perf_counter() - start) * 1000
            return region, elapsed, slot
            
        # Run latency tests in parallel
        results = await asyncio.gather(
            measure_latency(london_client, "London"),
            measure_latency(ny_client, "New York")
        )
        
        # Print results
        print("\n📊 Latency Results:")
        print("------------------")
        for region, latency, slot in results:
            print(f"{region}: {latency:.2f}ms (slot {slot})")
            
        # Determine optimal region
        fastest_region = min(results, key=lambda x: x[1])[0]
        print(f"\n✨ Optimal region: {fastest_region}")
        
        # Clean up
        await london_client.close()
        await ny_client.close()
        
        print("\n✅ Jito latency test completed")
        
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_jito_latency())
