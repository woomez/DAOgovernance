import json
from web3 import Web3
from web3.exceptions import BlockNotFound

def get_block_timestamp(block_num):
    infura_url = 'https://mainnet.infura.io/v3/d01265cbfef74bc2a7bf83a6ed7840e5'
    if block_num == 0:
        return

    web3 = Web3(Web3.HTTPProvider(infura_url))
    """Get Ethereum block timestamp"""
    try:
        block_info = web3.eth.getBlock(block_num)
    except BlockNotFound:
        return None
    last_time = block_info["timestamp"]
    return last_time

def read_json(filename: str) -> dict:
    try:
        with open(filename, "r") as f:
            data = json.loads(f.read())
    except:
        raise Exception(f"Reading {filename} file encountered an error")
  
    return data

