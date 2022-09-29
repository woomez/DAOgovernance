from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import datetime
import pandas as pd
import os  
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

url = 'https://api.thegraph.com/subgraphs/name/messari/ens-governance'
os.makedirs('./test_ens', exist_ok=True)  

# Provide a GraphQL query
_queryDelegates = gql(
    """
      query($lastID: String) {
        delegates (first:1000, where: {delegatedVotesRaw_gt: 0, id_gt: $lastID, tokenHoldersRepresentedAmount_gt: 1}) {  
            id
            delegatedVotesRaw
            tokenHoldersRepresentedAmount
            tokenHoldersRepresented {
              id
            }
            numberVotes
            proposals {
              id
            }
        }  
      }
   """
)

_queryVotes = gql(
        """
      query($lastID: String) {
        delegates (first:1000, where: {delegatedVotesRaw_gt: 0, id_gt: $lastID, tokenHoldersRepresentedAmount_gt: 1}) {  
            id
            delegatedVotesRaw
            tokenHoldersRepresentedAmount
            tokenHoldersRepresented {
              id
            }
            numberVotes
            proposals {
              id
            }
        }  
      }
   """
)


for link in urls:
    name, subgraph = link
    transport = AIOHTTPTransport(url=subgraph)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    os.makedirs(f'./csvs/delegations/{name}', exist_ok=True)
    
    print("Starting :", name)
    gov = client.execute(govquery)
    govdf = pd.json_normalize(gov['governances'])
    govdf.to_csv(f"./csvs/{name}.csv")
    params = {
                "lastID": ""
        }

    loadmore = True
    count = 1
    length = 0

    while loadmore:
        
        curr = client.execute(query, variable_values=params)
        length += len(curr['delegates'])
        
        if len(curr['delegates']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['delegates'][-1]['id']
            
            # save to csv
            delegations = pd.json_normalize(curr['delegates'])
            delegations.to_csv(f"./csvs/delegations/{name}/{name}_{count}.csv")

            count += 1
     
    print(f"done w {name}, total {length} delegations")
    gc.collect()





