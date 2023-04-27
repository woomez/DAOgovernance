from gql import gql
from utils import handle_ens
import numpy as np
import pandas as pd
import os

def handle_votecsv(dao, query, df):
    df = df.sort_values(by=["block"])

    df['DAO Name'] = dao
    df['Offchain?'] = 0
    df['Proposal Choices'] = df.apply(lambda x: ['FOR', 'AGAINST', 'ABSTAIN'], axis = 1)
    
    # convert blocktime to timestamp
    df["proposal.startBlock"] = df["proposal.startBlock"].fillna(0)
    df["proposal.endBlock"] = df["proposal.endBlock"].fillna(0)

    # change data types
    convert_dict = {'proposal.id': str,
                    'weight': np.float64,
                    'voter.delegatedVotes': np.float64,
                    'voter.delegatedVotesRaw': np.float64,
                    'voter.tokenHoldersRepresentedAmount': np.uint,
                    'proposal.startBlock': np.uint,
                    'proposal.endBlock': np.uint
                }
 
    df = df.astype(convert_dict)

    df = handle_ens(df)

    # drop and add columns
    df.drop(columns=['id'], index=1, inplace=True)
    df.rename(columns={
                    "voter.id": "Voter Address",
                    "voter.delegatedVotes": "Current Delegated Votes to Voter",
                    "voter.delegatedVotesRaw": "Current Delegated Votes Raw to Voter",
                    "voter.tokenHoldersRepresentedAmount": "Voter Token Holders Represented",
                    "proposal.state": "Proposal State",
                    "proposal.id": "Proposal ID",
                    "proposal.quorumVotes": "Quorum Votes",
                    "blockTime": "Vote Time",
                    "proposal.tokenHoldersAtStart": "Proposal Token Holders",
                    "proposal.delegatesAtStart": "Proposal Delegate Holders",
                    "proposal.againstWeightedVotes": "Against Weighted Votes",
                    "proposal.againstDelegateVotes": "Against Delegate Votes",
                    "proposal.forDelegateVotes": "For Delegate Votes",
                    "proposal.abstainDelegateVotes": "Abstain Delegate Votes",
                    "proposal.totalDelegateVotes": "Total Delegate Votes",
                    "proposal.forWeightedVotes": "For Weighted Votes",
                    "proposal.abstainWeightedVotes": "Abstain Weighted Votes",
                    "proposal.totalWeightedVotes": "Total Weighted Votes",
                    "proposal.creationTime": "Proposal Date Created",
                    "proposal.startBlock": "Proposal Date Start",
                    "proposal.endBlock": "Proposal Date End",
                    "proposer.id": "Proposal Author",
                    "choice": "Voter Choice",
                    "txnHash": "Transaction Hash",
                    "weight": "Weight"
                }, inplace=True)

    os.makedirs(f"./res/{query}/new", exist_ok=True)
   
    # format CSV
    cols_to_move= ['ENS', 'Voter Address']
    df = df[cols_to_move + [ col for col in df.columns if col not in cols_to_move]] 

    first_column = df.pop('DAO Name')
    df.insert(0, 'DAO Name', first_column)
    df.drop(df.filter(regex="Unname"),axis=1, inplace=True, errors='ignore')

    #save
    try:
        daopath = f"./res/{query}/{dao}.csv"
        daodf = pd.read_csv(daopath)
        print("found previously stored data")
        daodf = pd.concat([daodf, df], ignore_index=True)
        daodf.to_csv(daopath)
        df = daodf

    except:
        print("could not find previously stored data")
        df.to_csv(f"./res/{query}/{dao}.csv", index=False)

    print("successfuly saved")
    return df

def voteQuery(client, dao, _query):
    """
    try except:
        order by blocktime
        handle_votecsv
        try to load last block (if exists, then 

    when saving, sort by block
    """
    params = {
                "lastBlock": "0"
        }

    votes = pd.DataFrame()
    

    try:
        df = pd.read_csv(f"./res/votes/{dao}.csv", index_col=None)
        df = df.sort_values(by=["block"])
        params["lastBlock"] = str(df["block"].iloc[-1])
        lastBlock = params["lastBlock"]

        print(f"Found lastBlock for {dao} at {lastBlock}")

    except:
        print(f"Could not find CSV for {dao}")

    _voteQuery = gql(  """
              query($lastBlock: BigInt) {
                  votes (orderBy:block, orderDirection: asc, first:1000, where: { block_gt: $lastBlock}) {
                        id
                        choice
                        weight
                        voter{
                          id
                          delegatedVotes
                          delegatedVotesRaw
                          tokenHoldersRepresentedAmount
                        }
                        proposal{
                          id
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
                          creationTime
                          startBlock
                          endBlock
                        }
                        block
                        blockTime
                        txnHash
                      }
                    }       """)

    loadmore = True
    counter = 1
    length = 0
    firstcheck = True

    while loadmore:

        curr = client.execute(_voteQuery, variable_values=params)
        currlen = len(curr['votes'])
        length += currlen
        if firstcheck:
            firstcheck = False
            if currlen == 0:
                print("There were no new votes to add")
                return
        else:
            if currlen == 0:
                loadmore = False
            else:
                # update params
                params["lastBlock"] = curr['votes'][-1]['block']
                df = pd.json_normalize(curr['votes'], max_level=1)
                votes = pd.concat([votes, df], ignore_index=True)
                counter += 1
    
    print("Total added votes: ", length)
    votes = handle_votecsv(dao, _query, votes)
