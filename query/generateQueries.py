from queryHandler import query
import pandas as pd
import gc
import os
from utils import traverse_tree

urls = [('Angle', 'https://api.studio.thegraph.com/query/28876/angle-governance/v2'),
        ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5'),
        ('Fei', 'https://api.studio.thegraph.com/query/28876/fei-governance/v1'),
        ('Euler', 'https://api.studio.thegraph.com/query/28876/euler-governance/v2')
        ]

_queries = ["delegates", "governances", "proposals", "votes", "delegations", "tokendailysnapshots", "votedailysnapshots"]

def generate_results(url, _queries):
    dao, api = url
    print(f"starting process for {dao}")
    for _query in _queries:
        query(dao, api, _query)
        gc.collect()

ens_url = ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5')

if __name__ == "__main__":
    path = "/Users/jaeyongpark/codes/governance/query/res"
    traverse_tree(path)
    # for url in urls:
    #     generate_results(url, _queries)


