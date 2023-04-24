from etherscan import Etherscan

def getHistErc20Supply(address, block):
    api_key = 'QFB7NCEGSXA1Y33U19CGBHIMZMRR1CX3KH'

    eth = Etherscan(api_key)

    supply = eth.get_hist_erc20_token_total_supply_by_contract_address_and_block_no(contract_address=address, block_no=block)

    return supply 
