from queries import query
import pandas as pd
import gc

urls = [('Compound', 'https://api.thegraph.com/subgraphs/name/danielkhoo/compound-governance'),
        ('Dydx', 'https://api.thegraph.com/subgraphs/name/messari/dydx-governance'),
        ('Uniswap', 'https://api.thegraph.com/subgraphs/name/danielkhoo/uniswap-governance'),
        ('Aave', 'https://api.thegraph.com/subgraphs/name/messari/aave-governance'),
        ('Hop', 'https://api.thegraph.com/subgraphs/name/messari/hop-governance'),
        ('Truefi', 'https://api.thegraph.com/subgraphs/name/messari/truefi-governance'),
        ('Silo', 'https://api.thegraph.com/subgraphs/name/messari/silo-governance'),
        ('ENS', 'https://api.thegraph.com/subgraphs/name/messari/ens-governance'),
        ('Code4rena', 'https://api.thegraph.com/subgraphs/name/danielkhoo/code4rena-governance'),
        ('Fei', 'https://api.thegraph.com/subgraphs/name/messari/fei-governance'),
        ('Unlock', 'https://api.thegraph.com/subgraphs/name/messari/unlock-governance'),
        ('Euler', 'https://api.thegraph.com/subgraphs/name/messari/euler-governance')
        ]

_queries = ["delegates", "governances", "proposals", "votes", "delegations", "tokendailysnapshots", "votedailysnapshots"]

def generate_results(url, _queries):
    dao, api = url
    print(f"starting process for {dao}")
    for _query in _queries:
        query(dao, api, _query)
    gc.collect()

ens_url = ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5')

generate_results(ens_url, _queries)
