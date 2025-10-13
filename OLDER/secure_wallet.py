# secure_wallet.py
from dotenv import load_dotenv
import os
from pathlib import Path
import base58
import json

class SecureWallet:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Create secure directories if they don't exist
        self.secure_dir = Path(".secure")
        self.secure_dir.mkdir(exist_ok=True)
        
        # Create .gitignore if it doesn't exist and add .secure/
        gitignore_path = Path(".gitignore")
        if not gitignore_path.exists() or ".secure/" not in gitignore_path.read_text():
            with open(gitignore_path, "a") as f:
                f.write("\n# Secure wallet directory\n.secure/\n")

    def setup_wallet(self, private_key=None):
        """Setup wallet with optional private key input"""
        if private_key is None:
            print("\n🔐 Secure Wallet Setup")
            print("Enter your private key (it will not be displayed):")
            import getpass
            private_key = getpass.getpass()

        # Validate private key format
        try:
            # Check if it's a valid base58 key
            decoded = base58.b58decode(private_key)
            if len(decoded) != 64:  # Standard Solana private key length
                raise ValueError("Invalid key length")
        except Exception as e:
            print("❌ Invalid private key format")
            return False

        # Store encrypted key in .secure directory
        try:
            from cryptography.fernet import Fernet
            key = Fernet.generate_key()
            
            # Store encryption key securely
            key_path = self.secure_dir / ".key"
            with open(key_path, "wb") as f:
                f.write(key)
            
            # Encrypt and store private key
            f = Fernet(key)
            encrypted_key = f.encrypt(private_key.encode())
            
            wallet_path = self.secure_dir / "wallet.enc"
            with open(wallet_path, "wb") as f:
                f.write(encrypted_key)
                
            print("✅ Wallet configured securely")
            return True
            
        except Exception as e:
            print(f"❌ Error securing wallet: {str(e)}")
            return False

    def get_wallet_key(self):
        """Safely retrieve the wallet key"""
        try:
            from cryptography.fernet import Fernet
            
            # Read encryption key
            key_path = self.secure_dir / ".key"
            if not key_path.exists():
                print("❌ Wallet not configured")
                return None
                
            with open(key_path, "rb") as f:
                key = f.read()
                
            # Read encrypted wallet
            wallet_path = self.secure_dir / "wallet.enc"
            with open(wallet_path, "rb") as f:
                encrypted_key = f.read()
                
            # Decrypt
            f = Fernet(key)
            private_key = f.decrypt(encrypted_key).decode()
            
            return private_key
            
        except Exception as e:
            print(f"❌ Error accessing wallet: {str(e)}")
            return None

    def clear_wallet(self):
        """Securely clear wallet data"""
        try:
            for file in self.secure_dir.glob("*"):
                file.unlink()
            self.secure_dir.rmdir()
            print("✅ Wallet data cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing wallet: {str(e)}")
            return False