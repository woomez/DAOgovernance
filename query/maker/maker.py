from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import datetime
import pandas as pd
import os  
import gc
import json

os.makedirs('./csvs/maker', exist_ok=True)  

# Using protofire stubgraph
api = "https://api.thegraph.com/subgraphs/name/protofire/makerdao-governance"

transport = AIOHTTPTransport(url=api)
client = Client(transport=transport, fetch_schema_from_transport=True)

"""
Generate results for MAKER

TODO:
    understand maker exec votes -
    what are actions

    extract what is needed

    whatis lock, free ?

    how do I get weights for the votes?

    get results for poll votes 
    put it in same format

    add executive votes
"""


# Provide GraphQL query
spellquery = gql(
    """
    query($lastID: ID){
      spells(first: 1000, where:{id_gt: $lastID}) {
        id
        timestamp
        approvals
        casted
        castedWith
        lifted
        liftedWith
        timeLine {
          id
          timestamp
          transactionHash
          sender
          type: __typename
          ... on AddAction {
            locked
          }
          ... on RemoveAction {
            locked
          }
          ... on LockAction {
            wad
          }
          ... on FreeAction {
            wad
          }
        }
      }
    }   
    """
)

govquery = gql(
"""
    {
      governanceInfo(id: "0x0") {
        id
        countProxies
        countAddresses
        countSlates
        countSpells
        countLock
        countFree
        countPolls
        locked
        lastBlock
        lastSynced
        hat
      }
    }
""")


os.makedirs(f'./csvs/maker', exist_ok=True)

_queries = [spellquery, govquery]
# for _query in queries:

"""
get results for gov

gov = client.execute(govquery)
govdf = pd.json_normalize(gov['governanceInfo'])
govdf.to_csv(f"./csvs/maker_gov.csv")


"""

params = {
            "lastID": ""
    }

loadmore = True
count = 1
length = 0

while loadmore:
    
    curr = client.execute(spellquery, variable_values=params)
    length += len(curr['spells'])
    
    if len(curr['spells']) == 0:
        loadmore = False
        break
    
    else:
        # update params
        params["lastID"] = curr['spells'][-1]['id']
        
        # save to csv
        spells = pd.json_normalize(curr['spells'])
        # spells.to_csv(f"./csvs/maker/{count}.csv")
        with open(f'./csvs/maker/'+f'{count}.json', 'w') as outfile:
            json.dump(curr, outfile)
        count += 1
 
    gc.collect()



print(f"done w maker, total {length} delegations")

#os.makedirs(f"./res/{dao}/{query}", exist_ok=True)
#    with open(f'./res/{dao}/{query}/'+f'{counter}.json', 'w') as outfile:
#        json.dump(result, outfile)



