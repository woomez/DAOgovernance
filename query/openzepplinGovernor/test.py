import os
import pandas as pd
from queryHandler import generate_results
from delegateHandler import combineDelegations, addENStoDelegations, findMissingRows
from urls import urls

new_urls = [('Angle', 'https://api.thegraph.com/subgraphs/name/messari/angle-governance')]

for url in new_urls:
    dao, api = url
    print('Generating results for', dao)

    if os.path.isfile(f'./res/delegations/{dao}.csv'):
        print(f"\n Found file for {dao}")
        merged = pd.read_csv(f'./res/delegations/{dao}.csv')

    elif os.path.isfile(f'./res/delegations/{dao}_temp.csv'):
        print(f"\n Found temp file for {dao}")
        merged = pd.read_csv(f'./res/delegations/{dao}_temp.csv')
    else: 
        try:
            merged = combineDelegations(dao);
        except Exception as e:
            print(f"Error combining delegations for {dao}")
            print(e)
            continue

             
    # merged = addENStoDelegations(merged, dao)
    numMissingRows = findMissingRows(dao)


