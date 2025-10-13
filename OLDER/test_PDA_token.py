from solders.pubkey import Pubkey

# Your meme coin mint and router program ID as strings
meme_mint = "5qCtARHJfxANZyczUokjjSA8rthDoMBVBxoTosPfbonk"
router_program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

# Convert to Pubkey objects
mint_pubkey = Pubkey.from_string(meme_mint)
router_prog_pubkey = Pubkey.from_string(router_program_id)

# Prepare the PDA seeds (as bytes)
seeds = [b"token-vault", bytes(mint_pubkey)]

# Derive the PDA and bump
vault_pda, bump = Pubkey.find_program_address(seeds, router_prog_pubkey)

print("Token Vault PDA:", str(vault_pda))
print("Vault Bump:", bump)