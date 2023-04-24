import os
import pandas as pd
from queryHandler import generate_results
from delegateHandler import combineDelegations, addENStoDelegations
from urls import urls

"""
token supply : total supply of token (circulating token supply)

ToDo:
write script to move folder contents in new out of it.
if no votes (empty csv) don't save
generate results for other methods too 
add ens to columns (make a dict for that)

add nouns and maker (same format)

for delegations
store new delegations in separate folder
combine delegations and append to the master delegations file

with ousd-governance
search how much of delegatevotingpowerchange there is without txnhash from delegate change, 

find DAOs to add
"""

#when testing urls
new_urls = [('Gitcoin', 'https://api.thegraph.com/subgraphs/name/messari/gitcoin-governance')]

#specify conversion methods
conversion_methods = ["governances", "proposals", "delegateChanges", "delegatePowerChanges", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]
votes = ["governances", "votes"]
delegations = ["delegateChanges", "delegatePowerChanges"]

if __name__ == "__main__":

    for url in urls:
        generate_results(url, delegations)

    for url in urls:
        dao, api = url
        print('\nGenerating results for', dao)

        if os.path.isfile(f'./res/delegations/{dao}.csv'):
            merged = pd.read_csv(f'./res/delegations/{dao}.csv')
            continue

        elif os.path.isfile(f'./res/delegations/{dao}_temp.csv'):
            print(f"\n found temp file for {dao}")
            merged = pd.read_csv(f'./res/delegations/{dao}_temp.csv')
        else: 
            try:
                merged = combineDelegations(dao);
            except Exception as e:
                print(f"Error combining delegations for {dao}")
                print(e)
                continue
                 
        merged = addENStoDelegations(merged, dao)
