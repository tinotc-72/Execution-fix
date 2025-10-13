from solders.keypair import Keypair
import json

def create_wallet():
    kp = Keypair()
    with open('dev-wallet-funded.json', 'w') as f:
        json.dump(list(kp.to_bytes()), f)
    print(f'Created wallet {kp.pubkey()}')
    
if __name__ == "__main__":
    create_wallet()
