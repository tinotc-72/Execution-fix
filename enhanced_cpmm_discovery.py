#!/usr/bin/env python3
"""
Enhanced CPMM Pool Discovery
Find what tokens are actually paired with SOL in CPMM pools
"""

import asyncio
import struct
import logging
from typing import Optional, Dict, List, Tuple
from collections import defaultdict

from env_keys import load_wallet_from_private_key, validate_env_vars
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
CPMM_PROGRAM_ID = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")

# Common token mints to check
COMMON_MINTS = {
    "SOL": Pubkey.from_string("So11111111111111111111111111111111111111112"),
    "USDC": Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
    "USDT": Pubkey.from_string("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"),
    "BONK": Pubkey.from_string("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
    "WIF": Pubkey.from_string("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"),
    "RAY": Pubkey.from_string("4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"),
    "MEME": Pubkey.from_string("B5nFu5iWq8kwVkWYKbJoZeYGWcWVwbWKdXPGXzfgKRkW"),
    "POPCAT": Pubkey.from_string("7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"),
}

async def discover_cpmm_pool_pairs(client: AsyncClient) -> Dict[str, List[str]]:
    """Discover what token pairs exist in CPMM pools"""
    logger.info("🔍 Discovering CPMM pool token pairs...")
    
    try:
        # Get program accounts
        response = await client.get_program_accounts(
            CPMM_PROGRAM_ID,
            encoding="base64",
            commitment=Confirmed
        )
        
        if not response or not response.value:
            logger.warning("⚠️ No CPMM program accounts found")
            return {}
        
        logger.info(f"📊 Analyzing {len(response.value)} CPMM accounts...")
        
        # Track found token pairs
        pairs_found = defaultdict(list)
        token_counts = defaultdict(int)
        
        # Check first 100 accounts for performance
        for i, account in enumerate(response.value[:100]):
            try:
                account_info = account.account
                if len(account_info.data) < 200:
                    continue
                
                data = account_info.data
                
                # Look for token mint addresses at common offsets
                found_mints = []
                
                # Check specific offsets where mints are commonly stored
                common_offsets = [8, 40, 72, 104, 136, 168, 200, 232, 264]
                
                for offset in common_offsets:
                    if offset + 32 <= len(data):
                        try:
                            candidate = data[offset:offset+32]
                            pubkey = Pubkey(candidate)
                            
                            # Check if it's a known mint
                            for mint_name, mint_pubkey in COMMON_MINTS.items():
                                if pubkey == mint_pubkey:
                                    found_mints.append(mint_name)
                                    token_counts[mint_name] += 1
                                    break
                        except:
                            continue
                
                # If we found exactly 2 mints, it's likely a trading pair
                if len(found_mints) == 2:
                    pair = f"{found_mints[0]}-{found_mints[1]}"
                    pairs_found[pair].append(str(account.pubkey))
                    logger.info(f"✅ Found {pair} pool: {account.pubkey}")
                
                # Also check for SOL specifically
                elif len(found_mints) == 1 and "SOL" in found_mints:
                    # Look for the second mint more carefully
                    for offset in range(0, min(len(data) - 32, 400), 8):
                        try:
                            candidate = data[offset:offset+32]
                            pubkey = Pubkey(candidate)
                            
                            # Skip if it's SOL or system accounts
                            if pubkey == SOL_MINT or str(pubkey).startswith("1111111"):
                                continue
                            
                            # Check if it looks like a valid mint
                            mint_info = await client.get_account_info(pubkey)
                            if mint_info.value and len(mint_info.value.data) == 82:  # Mint account size
                                pairs_found[f"SOL-{pubkey}"].append(str(account.pubkey))
                                logger.info(f"✅ Found SOL-{pubkey} pool: {account.pubkey}")
                                break
                        except:
                            continue
                
                if i % 10 == 0:
                    logger.info(f"📊 Processed {i+1}/100 accounts...")
                    
            except Exception as e:
                logger.debug(f"Error processing account {i}: {e}")
                continue
        
        # Summary
        logger.info(f"\n📊 CPMM Pool Discovery Summary:")
        logger.info(f"   Total pairs found: {len(pairs_found)}")
        
        logger.info(f"\n🏆 Most common tokens in CPMM pools:")
        for token, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {token}: {count} pools")
        
        logger.info(f"\n📋 Trading pairs found:")
        for pair, pools in pairs_found.items():
            logger.info(f"   {pair}: {len(pools)} pools")
            for pool in pools[:3]:  # Show first 3 pools
                logger.info(f"      - {pool}")
        
        return dict(pairs_found)
        
    except Exception as e:
        logger.error(f"Error discovering pools: {e}")
        return {}

async def find_best_sol_pair(client: AsyncClient) -> Optional[Tuple[str, str]]:
    """Find the best SOL trading pair available in CPMM"""
    logger.info("🎯 Finding best SOL trading pair...")
    
    pairs = await discover_cpmm_pool_pairs(client)
    
    # Look for SOL pairs in order of preference
    preferred_pairs = ["SOL-USDC", "SOL-USDT", "SOL-RAY", "SOL-BONK", "SOL-WIF"]
    
    for pair in preferred_pairs:
        if pair in pairs:
            logger.info(f"✅ Found preferred pair: {pair}")
            return pair, pairs[pair][0]  # Return pair name and first pool address
    
    # Look for any SOL pair
    for pair in pairs:
        if pair.startswith("SOL-"):
            logger.info(f"✅ Found SOL pair: {pair}")
            return pair, pairs[pair][0]
    
    logger.warning("⚠️ No SOL pairs found in CPMM pools")
    return None

async def analyze_specific_pool(client: AsyncClient, pool_address: str):
    """Analyze a specific CPMM pool in detail"""
    logger.info(f"🔬 Analyzing pool: {pool_address}")
    
    try:
        pool_pubkey = Pubkey.from_string(pool_address)
        
        # Get pool account
        pool_info = await client.get_account_info(pool_pubkey, commitment=Confirmed)
        if not pool_info or not pool_info.value:
            logger.error("❌ Pool not found")
            return
        
        data = pool_info.value.data
        logger.info(f"📊 Pool details:")
        logger.info(f"   Address: {pool_address}")
        logger.info(f"   Owner: {pool_info.value.owner}")
        logger.info(f"   Data length: {len(data)} bytes")
        
        # Extract key addresses
        logger.info(f"\n🔍 Extracting key addresses:")
        
        # Common offsets for CPMM pools
        key_offsets = {
            8: "Authority",
            40: "Mint A",
            72: "Mint B", 
            104: "Vault A",
            136: "Vault B",
            168: "LP Mint",
            200: "Config",
        }
        
        for offset, name in key_offsets.items():
            if offset + 32 <= len(data):
                try:
                    candidate = data[offset:offset+32]
                    pubkey = Pubkey(candidate)
                    
                    # Check if it's a known mint
                    mint_name = "Unknown"
                    for token, mint_pubkey in COMMON_MINTS.items():
                        if pubkey == mint_pubkey:
                            mint_name = token
                            break
                    
                    logger.info(f"   {name} (offset {offset}): {pubkey} ({mint_name})")
                    
                    # Verify the account exists
                    try:
                        account_info = await client.get_account_info(pubkey)
                        if account_info.value:
                            logger.info(f"      ✅ Account exists, owner: {account_info.value.owner}")
                        else:
                            logger.info(f"      ❌ Account not found")
                    except:
                        logger.info(f"      ❓ Could not verify account")
                        
                except Exception as e:
                    logger.info(f"   {name} (offset {offset}): Error - {e}")
        
        # Look for fee configuration
        logger.info(f"\n💰 Fee configuration:")
        try:
            # Fee might be stored as u64 or u32
            for offset in [264, 296, 328]:
                if offset + 8 <= len(data):
                    fee_u64 = struct.unpack("<Q", data[offset:offset+8])[0]
                    fee_u32 = struct.unpack("<I", data[offset:offset+4])[0]
                    
                    logger.info(f"   Offset {offset}: {fee_u64} (u64) / {fee_u32} (u32)")
                    
                    # Convert to basis points if reasonable
                    if fee_u32 < 10000:
                        logger.info(f"      Possible fee: {fee_u32/100:.2f}%")
        except:
            logger.info("   Could not parse fee configuration")
        
    except Exception as e:
        logger.error(f"Error analyzing pool: {e}")

async def main():
    """Main analysis function"""
    try:
        # Load environment
        env_vars = validate_env_vars()
        
        logger.info("🔍 Enhanced CPMM Pool Discovery")
        logger.info("=" * 50)
        
        async with AsyncClient(env_vars["RPC_URL"]) as client:
            # Discover all pool pairs
            pairs = await discover_cpmm_pool_pairs(client)
            
            if not pairs:
                logger.warning("⚠️ No CPMM pools found")
                return
            
            # Find best SOL pair
            best_pair = await find_best_sol_pair(client)
            
            if best_pair:
                pair_name, pool_address = best_pair
                logger.info(f"\n🎯 Best SOL pair found: {pair_name}")
                logger.info(f"   Pool address: {pool_address}")
                
                # Analyze the pool in detail
                await analyze_specific_pool(client, pool_address)
                
                logger.info(f"\n✅ Ready for CPMM trading implementation!")
                logger.info(f"📋 Use this pool for your SOL trading bot:")
                logger.info(f"   Pair: {pair_name}")
                logger.info(f"   Pool: {pool_address}")
                
            else:
                logger.warning("⚠️ No suitable SOL pairs found")
                
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
