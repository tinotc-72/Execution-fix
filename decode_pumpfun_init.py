
import asyncio
import aiohttp
import base58
import sys

async def decode_pumpfun_init(signature):
    rpc_url = 'https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315'
    async with aiohttp.ClientSession() as session:
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'getTransaction',
            'params': [signature, {'encoding': 'jsonParsed', 'maxSupportedTransactionVersion': 0}]
        }
        async with session.post(rpc_url, json=payload) as response:
            data = await response.json()
            if 'result' in data and data['result']:
                tx = data['result']
                instructions = tx['transaction']['message'].get('instructions', [])
                for i, ix in enumerate(instructions):
                    if 'programId' in ix and ix['programId'] == 'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA':
                        data_field = ix.get('data', '')
                        if data_field:
                            try:
                                decoded_data = base58.b58decode(data_field)
                                discriminator = decoded_data[:8]
                                args = decoded_data[8:]
                                print(f'Instruction #{i}:')
                                print(f'  Discriminator: {discriminator.hex()}')
                                print(f'  Args: {args.hex()}')
                                print(f'  Accounts: {ix.get("accounts", [])}')
                            except Exception as e:
                                print(f'Error decoding: {e}')
                        else:
                            print('No data field')
            else:
                print('No result')
    print('Done.')

async def main():
    if len(sys.argv) > 1:
        signatures = sys.argv[1:]
    else:
        signatures = [
            '53ZPJXgGL6di3NBaJXbCZYyFqet1AKpkRR7kitLjk3AYJkXkDSN9DyNnDLHJJthtVuFujy1m25oEGzkZtHuRbMiR',
            '5MSuayuhZwxdmneRbw4jkAKfUVg3QFmmn4xtsTbBcLZQ5oVDwgUDe7UaawtbGj2cnoP85J6xURhXRopFxkKMvWDs',
            'Sr8vCJMGvFP6pTTNECZVndyWyxCidCp41Qqb1Kep9N6yGjSwSZcvQKeK5noNkd9MjvE1PuvtiLAUbMn9Rf3RkwY'
        ]
    for sig in signatures:
        print(f'\nDecoding {sig[:16]}...')
        await decode_pumpfun_init(sig)

if __name__ == "__main__":
    asyncio.run(main())