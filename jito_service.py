# jito_service.py

import traceback
import aiohttp
import json
from typing import Optional
from models import Bundle 
from config import JITO_AUTH_TOKEN
from datetime import datetime, UTC

class JitoClient:
    LONDON_BLOCK_ENGINE = "https://london.mainnet.block-engine.jito.wtf"
    LONDON_RELAYER = "http://london.mainnet.relayer.jito.wtf:8100"
    LONDON_NTP = "ntp.london.jito.wtf"
    LONDON_SHRED_RECEIVER = "142.91.127.175:1002"

    def __init__(self):
        """Initialize Jito client specifically for London endpoints"""
        # Use London-specific endpoints
        self.base_url = self.LONDON_BLOCK_ENGINE
        # Update to use correct endpoint format
        self.tx_endpoint = f"{self.base_url}/api/v1/transactions"
        
        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "x-jito-auth": JITO_AUTH_TOKEN
        }
        
        self.session = None
        
        # Log initialization
        timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{timestamp}] 🔧 Initializing Jito London Client:")
        print(f"🌍 Region: London (🇬🇧)")
        print(f"🔗 Block Engine: {self.base_url}")
        print(f"📡 Relayer: {self.LONDON_RELAYER}")
        print(f"⏰ NTP Server: {self.LONDON_NTP}")
        print(f"📦 Shred Receiver: {self.LONDON_SHRED_RECEIVER}")

    async def initialize(self):
        """Initialize the client session and verify connectivity to London endpoints"""
        try:
            self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Test connection to London Block Engine
            print(f"\n🔍 Testing connection to London Block Engine...")
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    print("✅ Successfully connected to London Block Engine")
                else:
                    print(f"⚠️ Warning: London Block Engine returned status {response.status}")
                    
            return True
                    
        except Exception as e:
            print(f"❌ Failed to initialize London Jito client: {str(e)}")
            traceback.print_exc()
            return False

    async def close(self):
        """Properly close the client session"""
        if self.session:
            await self.session.close()
            print("👋 Closed connection to London Block Engine")

    async def send_bundle(self, bundle: Bundle) -> Optional[str]:
        """Send transaction to London Block Engine
        
        Args:
            bundle (Bundle): The bundle to submit
            
        Returns:
            Optional[str]: Transaction signature if successful, None otherwise
        """
        try:
            if not isinstance(bundle, Bundle):
                print(f"❌ Invalid bundle type: {type(bundle)}")
                return None

            if not self.session:
                await self.initialize()

            bundle_json = bundle.to_json()
            if bundle_json is None:
                return None

            timestamp = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{timestamp}] 📦 Submitting to London Block Engine...")
            print(f"🔗 URL: {self.tx_endpoint}")
            print(f"🔑 Auth: {self.headers['x-jito-auth'][:8]}...")

            # Submit transaction
            async with self.session.post(
                self.tx_endpoint,
                json=bundle_json
            ) as response:
                response_text = await response.text()
                
                print(f"\n🔍 London Block Engine Response:")
                print(f"Status: {response.status}")
                print(f"Body: {response_text[:200]}...")

                if response.status == 200:
                    result = json.loads(response_text)
                    if "error" in result:
                        print(f"❌ Transaction error: {result['error']}")
                        return None
                    print("✅ Transaction successfully submitted to London Block Engine")
                    return result.get('result')
                else:
                    print(f"⚠️ London Block Engine returned status {response.status}")
                    if response_text:
                        print(f"Full response: {response_text}")
                    return None

        except Exception as e:
            print(f"❌ London transaction submission failed: {str(e)}")
            traceback.print_exc()
            return None