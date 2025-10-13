# jito_service.py

import traceback
import asyncio
import aiohttp
import json
from typing import Optional
from models import Bundle 
from config import JITO_AUTH_TOKEN
from datetime import datetime, UTC

class JitoClient:
    # London endpoints - closest to major European exchanges
    LONDON_BLOCK_ENGINE = "https://london.mainnet.block-engine.jito.wtf"
    LONDON_RELAYER = "http://london.mainnet.relayer.jito.wtf:8100"
    LONDON_NTP = "ntp.london.jito.wtf"
    LONDON_SHRED_RECEIVER = "142.91.127.175:1002"
    
    # New York endpoints - for US exchanges
    NY_BLOCK_ENGINE = "https://ny.mainnet.block-engine.jito.wtf"
    NY_RELAYER = "http://ny.mainnet.relayer.jito.wtf:8100"
    NY_NTP = "ntp.ny.jito.wtf"
    NY_SHRED_RECEIVER = "144.202.90.136:1002"

    def __init__(self, region="london"):
        """Initialize Jito client with region selection"""
        self.region = region.lower()
        
        # Select endpoints based on region
        if self.region == "ny":
            self.block_engine = self.NY_BLOCK_ENGINE
            self.relayer = self.NY_RELAYER
            self.ntp = self.NY_NTP
            self.shred_receiver = self.NY_SHRED_RECEIVER
            self.location = "New York (🇺🇸)"
        else:
            self.block_engine = self.LONDON_BLOCK_ENGINE
            self.relayer = self.LONDON_RELAYER
            self.ntp = self.LONDON_NTP
            self.shred_receiver = self.LONDON_SHRED_RECEIVER
            self.location = "London (🇬🇧)"
            
        # API endpoints
        self.tx_endpoint = f"{self.block_engine}/api/v1/transactions"
        self.bundle_endpoint = f"{self.block_engine}/api/v1/bundle"
        self.next_slot_endpoint = f"{self.block_engine}/api/v1/next-slot"
        
        # Headers with auth
        self.headers = {
            "Content-Type": "application/json",
            "x-jito-auth": JITO_AUTH_TOKEN
        }
        
        self.session = None
        self.last_slot_check = 0
        
        # Log initialization
        timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] 🔧 Initializing Jito Client:")
        print(f"🌍 Region: {self.location}")
        print(f"🔗 Block Engine: {self.block_engine}")
        print(f"📡 Relayer: {self.relayer}")
        print(f"⏰ NTP Server: {self.ntp}")
        print(f"📦 Shred Receiver: {self.shred_receiver}")
        
    async def initialize(self):
        """Initialize the client session and verify connectivity to endpoints"""
        try:
            self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Test connection to Block Engine
            print(f"\n🔍 Testing connection to Block Engine...")
            async with self.session.get(self.block_engine) as response:
                if response.status == 200:
                    print("✅ Successfully connected to Block Engine")
                else:
                    print(f"⚠️ Warning: Block Engine returned status {response.status}")
                    
            return True
                    
        except Exception as e:
            print(f"❌ Failed to initialize Jito client: {str(e)}")
            traceback.print_exc()
            return False

    async def close(self):
        """Properly close the client session"""
        if self.session:
            await self.session.close()
            print("👋 Closed connection to Block Engine")

    async def get_next_slot(self) -> Optional[int]:
        """Get the next available slot for transaction inclusion"""
        try:
            if not self.session:
                await self.initialize()
                
            async with self.session.get(self.next_slot_endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("slot")
                return None
        except Exception as e:
            print(f"❌ Failed to get next slot: {str(e)}")
            return None

    async def send_bundle(self, bundle: Bundle) -> Optional[str]:
        """Send transaction bundle with low-latency optimizations
        
        Args:
            bundle (Bundle): The bundle to submit
            
        Returns:
            Optional[str]: Transaction signature if successful
        """
        try:
            if not isinstance(bundle, Bundle):
                print(f"❌ Invalid bundle type: {type(bundle)}")
                return None

            if not self.session:
                await self.initialize()
                
            # Get next slot for optimal timing
            next_slot = await self.get_next_slot()
            if next_slot:
                bundle.slot = next_slot
                print(f"📍 Targeting slot: {next_slot}")
                
            bundle_json = bundle.to_json()
            if bundle_json is None:
                return None
                
            # Add tip to incentivize inclusion
            bundle_json["tip"] = {
                "amount": 10000,  # 0.00001 SOL
                "unit": "lamports"
            }

            timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{timestamp}] 📦 Submitting to {self.location}...")
            
            # Submit to both block engine and relayer for redundancy
            async with aiohttp.ClientSession(headers=self.headers) as session:
                tasks = [
                    session.post(self.tx_endpoint, json=bundle_json),
                    session.post(f"{self.relayer}/submit_bundle", json=bundle_json)
                ]
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process responses
                for i, response in enumerate(responses):
                    if isinstance(response, Exception):
                        print(f"❌ Submission {i+1} failed: {str(response)}")
                        continue
                        
                    endpoint = "Block Engine" if i == 0 else "Relayer"
                    status = response.status
                    text = await response.text()
                    
                    print(f"\n🔍 {endpoint} Response (Status {status}):")
                    print(f"📄 {text}")
                    
                    if status == 200:
                        return json.loads(text).get("txid")
                        
            return None
            
        except Exception as e:
            print(f"❌ Bundle submission failed: {str(e)}")
            traceback.print_exc()
            return None

    async def check_connection(self) -> bool:
        """Check connection to Jito services
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            if not self.session:
                await self.initialize()
                
            # Test connection to Block Engine using ping endpoint
            ping_endpoint = f"{self.block_engine}/api/v1/ping"
            async with self.session.get(ping_endpoint) as response:
                if response.status in (200, 204):  # Both are valid success responses
                    print("✅ Successfully connected to Jito Block Engine")
                    return True
                print(f"⚠️ Block Engine ping returned status {response.status}")
                return False
                
        except Exception as e:
            print(f"❌ Jito connection check failed: {str(e)}")
            return False