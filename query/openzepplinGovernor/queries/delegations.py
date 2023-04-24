from gql import gql
import pandas as pd
import numpy as np
import os

def handle_delegateChange(dao, df):
    #save
    try:
        daopath = f"./res/delegateChanges/{dao}.csv"
        daodf = pd.read_csv(daopath)
        print("found previously stored data")
        daodf = pd.concat([daodf, df], ignore_index=True)
        daodf.to_csv(daopath)
        df = daodf

    except:
        print("could not find previously stored data")
        # save to CSV
        df.to_csv(f"./res/delegateChanges/{dao}.csv", index=False)

    print("successfuly updated \n")
    return df


def delegateChangesQuery(client, dao, _query):

    print("Starting delegateChange \n")
    delegations = pd.DataFrame()
    _delegationQuery = gql(  """
              query($lastID: ID) {
                  delegateChanges(first:1000, where: {id_gt: $lastID}) {
                        id
                        txnHash
                        blockNumber
                        blockTimestamp
                        delegate
                        delegator
                        previousDelegate
                      }
                    }       """)


    params = {
                "lastID": ""
        }

    try:
        df = pd.read_csv(f"./res/delegateChanges/{dao}.csv", index_col=None)
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
        currlen = len(curr['delegateChanges'])
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
                params["lastID"] = curr['delegateChanges'][-1]['id']
                df = pd.json_normalize(curr['delegateChanges'], max_level=1)
                delegations = pd.concat([delegations, df], ignore_index=True)
                counter += 1
        
    print(_query, length)
    delegations = handle_delegateChange(dao, delegations)


