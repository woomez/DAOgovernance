from queryHandler import generate_results
from resultHandler import traverse_tree
from combineCSVs import read_and_merge

urls = [('Angle', 'https://api.studio.thegraph.com/query/28876/angle-governance/v2'),
        ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5'),
        ('Fei', 'https://api.studio.thegraph.com/query/28876/fei-governance/v1'),
        ('Euler', 'https://api.studio.thegraph.com/query/28876/euler-governance/v2'),
        ('Compound', 'https://api.studio.thegraph.com/query/28876/compound-governance/v7'),
        ('Hop', 'https://api.studio.thegraph.com/query/28876/hop-governance/v1'),
        ('Silo', "https://api.studio.thegraph.com/query/28876/silo-governance/v1"),
        ('Truefi', "https://api.studio.thegraph.com/query/28876/truefi-governance/v1"),
        ('Unlock', "https://api.studio.thegraph.com/query/28876/unlock-governance/v1"),
        ('CompoundAlpha', 'https://api.studio.thegraph.com/query/28876/compoundalpha-governance/v1'),
        ('Nouns', 'https://api.studio.thegraph.com/query/28876/nouns-governance/v1'),
        ('UniswapBravo', 'https://api.studio.thegraph.com/query/28876/uniswap-governance/v0.1'),
        ('YamFinance', 'https://api.studio.thegraph.com/query/28876/yamfinance-governance/v0.1'),
        ('UniswapAlphaV2', 'https://api.studio.thegraph.com/query/28876/uniswapa2-governance/v0.2'),
        ('PoolTogether', 'https://api.studio.thegraph.com/query/28876/pooltogether-governance/v0.1'),
        ('Radicle', 'https://api.studio.thegraph.com/query/28876/radicle-governance/v0.1')]

new_urls = []

#specify conversion methods
conversion_methods = ["governances", "proposals", "delegations", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]

test_url = ('ENS', 'https://api.studio.thegraph.com/query/28876/ens-governance/v5')

if __name__ == "__main__":
    path = "/Users/jaeyongpark/codes/governance/query/res"
    print("starting query")
    # for url in urls:
        # generate_results(url, conversion_methods)
    print("converting json to csv")
    # traverse_tree(path, conversion_methods)
    read_and_merge(path)


