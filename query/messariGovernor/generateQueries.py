from queryHandler import generate_results
from combineres import read_and_merge

urls = [('Angle', 'https://api.thegraph.com/subgraphs/name/messari/angle-governance'), 
        ('ENS', 'https://api.thegraph.com/subgraphs/name/messari/ens-governance'),
        ('Fei', 'https://api.thegraph.com/subgraphs/name/messari/fei-governance'),
        ('CompoundBravo', 'https://api.thegraph.com/subgraphs/name/messari/compound-governance'),
        ('CompoundV1', 'https://api.thegraph.com/subgraphs/name/messari/compound-governance-v1'),
        ('Hop', 'https://api.thegraph.com/subgraphs/name/messari/hop-governance'),
        ('Silo', "https://api.thegraph.com/subgraphs/name/messari/silo-governance"),
        ('Truefi', "https://api.thegraph.com/subgraphs/name/messari/truefi-governance"),
        ('Unlock', "https://api.thegraph.com/subgraphs/name/messari/unlock-governance"),
        ('UniswapV2', 'https://api.thegraph.com/subgraphs/name/messari/uniswap-governance-v2'),
        ('UniswapV1', 'https://api.thegraph.com/subgraphs/name/messari/uniswap-governance-v1'),
        ('PoolTogether', 'https://api.thegraph.com/subgraphs/name/messari/pooltogether-governance'),
        ('Radicle', 'https://api.thegraph.com/subgraphs/name/messari/radicle-governance'),
        ('Ampleforth', 'https://api.thegraph.com/subgraphs/name/messari/ampleforth-governance'),
        ('Gitcoin', 'https://api.thegraph.com/subgraphs/name/messari/gitcoin-governance'),
        ('AaveV2', 'https://api.thegraph.com/subgraphs/name/messari/aave-governance'),
        ('DYDX', 'https://api.thegraph.com/subgraphs/name/danielkhoo/dydx-governance'),
        ('Cryptex', 'https://api.thegraph.com/subgraphs/name/messari/cryptex-governance'),
        ('Idle', 'https://api.thegraph.com/subgraphs/name/messari/idle-governance'),
        ('Indexed', 'https://api.thegraph.com/subgraphs/name/messari/indexed-governance'),
        ('Ousd', 'https://api.thegraph.com/subgraphs/name/messari/ousd-governance'),
        ('Reflexer','https://api.thegraph.com/subgraphs/name/messari/reflexer-governance'),
        ('Rarible', 'https://api.thegraph.com/subgraphs/name/messari/rarible-governance'),
        ('Threshold', 'https://api.thegraph.com/subgraphs/name/messari/threshold-governance')]

"""
ToDo:
write script to move folder contents in new out of it.
if no votes (empty csv) don't save
generate results for other methods too 
add ens to columns (make a dict for that)

add nouns and maker (same format)

find DAOs to add
"""
new_urls = []

#specify conversion methods
conversion_methods = ["governances", "proposals", "delegations", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]
votes = ["governances", "votes"]

if __name__ == "__main__":

    print("starting query")
    for url in urls:
        generate_results(url, votes)
        
    dpath= "/Users/jaeyongpark/codes/governance/query/messariGovernor/res"
    print("Merging res")
    read_and_merge(dpath)


