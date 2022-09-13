from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import datetime
import pandas as pd
import os  
import gc

urls = [('Maker', '')]

os.makedirs('./csvs/maker', exist_ok=True)  

# Provide a GraphQL query
query = gql(
    """
      {
      votePollActions{
        id
        sender
        poll {
          id
        }
        block
        transactionHash
      }
      spells{
        id
        timestamp
        data
        casted
        castedWith
        approvals
        totalVotes
      }
      votingActions{
        id
        sender
        spell {
          id
        }
        block
        transactionHash
      }
    }
   """
)

govquery = gql(
"""
        {
          governances {
            id
            currentTokenHolders
            totalTokenHolders
            currentDelegates
          }
        }
""")

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




