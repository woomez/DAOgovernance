from web3.auto.infura import w3
from ens import ENS
import datetime
import gc
import os
import json
from flatten_json import flatten
# from  import get_block_timestamp

from web3 import Web3
from web3.exceptions import BlockNotFound

def get_block_timestamp(block_num):
    infura_url = 'https://mainnet.infura.io/v3/d01265cbfef74bc2a7bf83a6ed7840e5'
    if block_num == 0:
        return

    # if block_num in storage:
    #    return storage[block_num]
    web3 = Web3(Web3.HTTPProvider(infura_url))
    """Get Ethereum block timestamp"""
    try:
        block_info = web3.eth.getBlock(block_num)
    except BlockNotFound:
        # Block was not mined yet,
        # minor chain reorganisation?
        return None
    last_time = block_info["timestamp"]
    # storage[block_num] = last_time
    return last_time

def read_json(filename: str) -> dict:
    try:
        with open(filename, "r") as f:
            data = json.loads(f.read())
    except:
        raise Exception(f"Reading {filename} file encountered an error")
        data = None

    return data     

def handle_spells(path, jsonData):
        
        convert_dict ={'_wad': float,
                       '_locked': float}

        spells = spells.astype(convert_dict)
        

        spells.drop(columns=['_wad', '_locked'], inplace=True)
        spells = spells.loc[spells['_type']=='AddAction']
        spells.rename(columns={
                    "_id": "VoteID",
                    "_timestamp": "blockTime",
                    "_transactionHash": "Transaction Hash",
                    "_sender": "Voter Address",
                    "id": "Proposal ID",
                    "timestamp": "Proposal Date Created"
                }, inplace=True)
        spells.drop(columns=['_type', 'castedWith', 'liftedWith'], inplace=True)


        spells = spells.to_csv(f"{path}/Maker.csv", index=False)
        print('flattened json')
        return spells

def convert_spells_json(jsonpath):
    path ="/Users/jaeyongpark/codes/governance/query/maker/csvs"
    _jsonData = read_json(jsonpath)
    handle_spells(path, _jsonData)


json_path = "/Users/jaeyongpark/codes/governance/query/maker/csvs/1.json"

csv_path = "/Users/jaeyongpark/codes/governance/query/csvs/maker/flattened.csv"

convert_spells_json(json_path)


