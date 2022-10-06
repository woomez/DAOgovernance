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

new_urls = [('Compound', 'https://api.studio.thegraph.com/query/28876/compound-governance/v7'),
            ('Hop', 'https://api.studio.thegraph.com/query/28876/hop-governance/v1'),
            ('Silo', "https://api.studio.thegraph.com/query/28876/silo-governance/v1"),
            ('Truefi', "https://api.studio.thegraph.com/query/28876/truefi-governance/v1"),
            ('Unlock', "https://api.studio.thegraph.com/query/28876/unlock-governance/v1"),
            ('CompoundAlpha', 'https://api.studio.thegraph.com/query/28876/compoundalpha-governance/v1'),
            ('Nouns', 'https://api.studio.thegraph.com/query/28876/nouns-governance/v1')]

#specify conversion methods
conversion_methods = ["governances", "proposals", "delegations", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]

test_methods = ["proposals", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]

test_url = ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5')

if __name__ == "__main__":
    path = "/Users/jaeyongpark/codes/governance/query/res"
    for url in new_urls:
        generate_results(url, conversion_methods)
    traverse_tree(path, conversion_methods)


