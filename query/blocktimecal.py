import datetime
from web3 import Web3
import time
from web3.contract import Contract
from web3.datastructures import AttributeDict
from web3.exceptions import BlockNotFound
from eth_abi.codec import ABICodec

# Currently this method is not exposed over official web3 API,
# but we need it to construct eth_getLogs parameters
from web3._utils.filters import construct_event_filter_params
from web3._utils.events import get_event_data




def get_block_timestamp(block_num):
        infura_url = 'https://mainnet.infura.io/v3/d01265cbfef74bc2a7bf83a6ed7840e5'
        print('curr block: ', block_num)
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
