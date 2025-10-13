#!/usr/bin/env python3

from solders.pubkey import Pubkey

def test_advanced_creator_vault_derivation():
    """Test creator_vault derivation with potential creator accounts from the working transaction"""
    mint = Pubkey.from_string("8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump")
    pump_program = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
    target = "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ"
    
    print(f"🔍 Testing advanced creator_vault derivation")
    print(f"🎯 Target: {target}")
    print()
    
    # Potential creator accounts from the working transaction
    potential_creators = [
        "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB",  # User/signer
        "87KRgKb3dXCvMaEFk2WWaPNuf7JTVutMFjVBA3SqW9A",   # Account index 1
        "CebN5WGQ4jvEPvsVU4EoHEpgzq1VV1T6NVswCLPVXdHy",  # Fee recipient
        "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",  # Global account
    ]
    
    for creator in potential_creators:
        creator_pubkey = Pubkey.from_string(creator)
        
        patterns = [
            ([b"creator", bytes(mint), bytes(creator_pubkey)], f"creator + mint + {creator[:8]}..."),
            ([b"creator", bytes(creator_pubkey), bytes(mint)], f"creator + {creator[:8]}... + mint"),
            ([bytes(creator_pubkey), bytes(mint)], f"{creator[:8]}... + mint"),
            ([bytes(mint), bytes(creator_pubkey)], f"mint + {creator[:8]}..."),
            ([b"vault", bytes(creator_pubkey), bytes(mint)], f"vault + {creator[:8]}... + mint"),
            ([b"creator_vault", bytes(creator_pubkey)], f"creator_vault + {creator[:8]}..."),
        ]
        
        print(f"Testing with potential creator: {creator}")
        for seeds, description in patterns:
            try:
                pda, bump = Pubkey.find_program_address(seeds, pump_program)
                match = "✅ MATCH!" if str(pda) == target else "❌"
                print(f"  {description}: {pda} {match}")
                if str(pda) == target:
                    print(f"🎉 FOUND! Seeds: {seeds}")
                    return
            except Exception as e:
                print(f"  {description}: Error - {e}")
        print()
    
    print("❌ No matching pattern found with any potential creator")

if __name__ == "__main__":
    test_advanced_creator_vault_derivation()