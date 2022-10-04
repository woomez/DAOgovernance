from queryHandler import generate_results
import pandas as pd
import gc
import os
from utils import traverse_tree

urls = [('Angle', 'https://api.studio.thegraph.com/query/28876/angle-governance/v2'),
        ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5'),
        ('Fei', 'https://api.studio.thegraph.com/query/28876/fei-governance/v1'),
        ('Euler', 'https://api.studio.thegraph.com/query/28876/euler-governance/v2')
        ]

#specify conversion methods
conversion_methods = ["governances", "proposals", "delegations", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]

test_methods = ["proposals", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]

_queries = ["delegates", "governances", "proposals", "votes", "delegations", "tokendailysnapshots", "votedailysnapshots"]

test_url = ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5')

if __name__ == "__main__":
    path = "/Users/jaeyongpark/codes/governance/query/res"

    traverse_tree(path, conversion_methods)
    # for url in urls:
    #     generate_results(url, _queries)


