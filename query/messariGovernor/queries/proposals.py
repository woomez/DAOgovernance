from gql import gql
import pandas as pd
import numpy as np
import os

def handle_proposal(dao, df):
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

def proposalQuery(client, dao, _query):
    print("Querying proposals \n")
    _proposalQuery = gql(  """
              {
                  proposals{
                    id
                    description
                    proposer{
                        id
                    }
                    state
                    quorumVotes
                    tokenHoldersAtStart
                    delegatesAtStart
                    againstDelegateVotes
                    forDelegateVotes
                    abstainDelegateVotes
                    totalDelegateVotes
                    againstWeightedVotes
                    forWeightedVotes
                    abstainWeightedVotes
                    totalWeightedVotes
                    creationBlock
                    votes{
                      choice
                      weight
                      voter{
                        id
                      }
                    }
                    startBlock
                    endBlock
                  }
                }
       """)
    params = {
                "lastID": ""
        }

    try:
        df = pd.read_csv(f"./res/proposals/{dao}.csv", index_col=None)
        df = df.sort_values(by=["id"])
        params["lastID"] = str(df["id"].iloc[-1])
        lastID = params["lastID"]
        print(f"Found lastBlock for {dao} at {lastID}")
    except:
        print(f"Could not find CSV for {dao}")

    result = client.execute(_proposalQuery)
