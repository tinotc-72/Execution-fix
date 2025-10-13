# generate_test.py
import base58
from solders.keypair import Keypair
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_private_key(key: str) -> None:
    """Test private key format and keypair creation"""
    try:
        # Remove any whitespace and check for common issues
        cleaned_key = key.strip()
        
        # Check for common formatting issues
        if '_' in cleaned_key:
            logger.error("❌ Invalid character '_' found in key")
            return
            
        if '=' in cleaned_key:
            logger.error("❌ Base64 padding character '=' found - key might be base64 encoded")
            return
            
        if len(cleaned_key) < 64:
            logger.error(f"❌ Key seems too short: {len(cleaned_key)} chars")
            return
            
        # Try decoding
        try:
            decoded = base58.b58decode(cleaned_key)
            logger.info(f"✅ Successfully decoded key (length: {len(decoded)} bytes)")
        except ValueError as ve:
            logger.error(f"❌ Base58 decode failed: {ve}")
            return
            
        # Try creating keypair
        try:
            if len(decoded) == 64:
                # Try full bytes
                kp = Keypair.from_bytes(decoded)
                logger.info(f"✅ Created keypair from full bytes")
            else:
                # Try seed bytes
                kp = Keypair.from_seed(decoded[:32])
                logger.info(f"✅ Created keypair from seed bytes")
                
            pubkey = kp.pubkey()
            logger.info(f"✅ Generated public key: {pubkey}")
            
            # Test signing
            msg = bytes([1,2,3,4])
            sig = kp.sign_message(msg)
            logger.info(f"✅ Successfully tested signing")
            
        except Exception as e:
            logger.error(f"❌ Keypair creation failed: {e}")
            return
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    # Example of how a proper base58 private key might look
    logger.info("Private Key Format Examples:")
    logger.info("1. Base58 keys are typically 88 characters long")
    logger.info("2. They contain only these characters: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    logger.info("3. They never contain: 0, O, I, l, _")
    
    # Test your key (replace with your actual key)
    print("\nTesting your private key...")
    key = "your_private_key_here"  # Replace with your actual key
    test_private_key(key)