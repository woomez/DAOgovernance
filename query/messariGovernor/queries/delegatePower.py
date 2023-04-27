from gql import gql
from utils import handle_ens
import numpy as np
import pandas as pd
import os

def handle_delegatePowerChange(dao, df):
    #save
    try:
        daopath = f"./res/delegateVotingPowerChanges/{dao}.csv"
        daodf = pd.read_csv(daopath)
        print("found previously stored data")
        daodf = pd.concat([daodf, df], ignore_index=True)
        daodf.to_csv(daopath)
        df = daodf

    except:
        print("could not find previously stored data")
        df.to_csv(f"./res/delegateVotingPowerChanges/{dao}.csv", index=False)

    print("successfuly updated \n")
    return df

def delegatePowerChangesQuery(client, dao, _query):

    print("Starting delegateVotingPowerChange")

    _delegationQuery = gql(  """
              query($lastID: ID) {
                  delegateVotingPowerChanges (first:1000, where: {id_gt: $lastID}) {
                        id
                        txnHash
                        blockTimestamp
                        delegate
                        newBalance
                        previousBalance
                        blockNumber
                    }
                }""")

    params = {
                "lastID": ""
        }
    
    delegations = pd.DataFrame()
    try:
        df = pd.read_csv(f"./res/delegateVotingPowerChanges/{dao}.csv", index_col=None)
        df = df.sort_values(by=["id"])
        params["lastID"] = str(df["id"].iloc[-1])
        lastID = params["lastID"]
        print(f"Found lastBlock for {dao} at {lastID}")

    except:
        print(f"Could not find CSV for {dao}")

    loadmore = True
    counter = 1
    length = 0
    firstcheck = True

    while loadmore:

        curr = client.execute(_delegationQuery, variable_values=params)
        currlen = len(curr['delegateVotingPowerChanges'])
        length += currlen
        if firstcheck:
            firstcheck = False
            if currlen == 0:
                print("There were no new delegation changes to add")
                return
        else:
            if currlen == 0:
                loadmore = False
            else:
                # update params
                params["lastID"] = curr['delegateVotingPowerChanges'][-1]['id']
                df = pd.json_normalize(curr['delegateVotingPowerChanges'], max_level=1)
                delegations = pd.concat([delegations, df], ignore_index=True)
                counter += 1
        
    print(_query, length)
    delegations = handle_delegatePowerChange(dao, delegations)

