import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

infura_api_key = os.getenv('INFURA_API_KEY')
infura_url = f'https://mainnet.infura.io/v3/{infura_api_key}'
w3 = Web3(Web3.HTTPProvider(infura_url))

erc20_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

erc20_address = Web3.to_checksum_address("0x57d90b64a1a57749b0f932f1a3395792e12e7055")
block_number = 8000000
token_contract = w3.eth.contract(address=erc20_address, abi=erc20_abi)
    
try:
    total_supply = token_contract.functions.totalSupply().call(block_identifier=block_number)
    print(f'Total supply at block {block_number}: {total_supply}')
except Exception as error:
    print(f'Error: {error}')





