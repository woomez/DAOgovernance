import pandas as pd

voterpath = "./csvs/voters/Gitcoin_voters.csv"
ratepath = "./csvs/voting_rates/Gitcoin_voting_rates.csv"

voters = pd.read_csv(voterpath)
voters['total_cap'] = 100000000
voters['circulating'] = 14198201
voters.to_csv(voterpath)

voterate = pd.read_csv(ratepath)
voterate['total_cap'] = 100000000
voterate['circulating'] = 14198201
voterate.to_csv(ratepath)
