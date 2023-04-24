from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import os
import gc
import pandas as pd
import numpy as np
import pickle
from web3.auto.infura import w3 
from ens import ENS

ns = ENS.fromWeb3(w3)

"""
run from main dir 

Description: execute to retrieve results from Nouns, update the results in res folder
Todo: set up query, get query endpoint, parse results
update the results in 

load final_onchain and merge

update the formatting
check missing cols, add new cols

rename cols and add new in the query handler
update add gov parameter function
"""

api = "https://api.thegraph.com/subgraphs/name/nounsdao/nouns-subgraph"
dao = 'Nouns'
queries = ['votes']

def handle_Nounvote(dao, query, df):
    df = df.sort_values(by=["blockNumber"])

    df['DAO Name'] = dao
    df['Offchain?'] = 0
    df['Proposal Choices'] = df.apply(lambda x: ['FOR', 'AGAINST', 'ABSTAIN'], axis = 1)

    # convert blocktime to timestamp
    df["proposal.startBlock"] = df["proposal.startBlock"].fillna(0)
    df["proposal.endBlock"] = df["proposal.endBlock"].fillna(0)

    # change data types
    convert_dict = {'proposal.id': str,
                    'votes': np.float64,
                    'voter.delegatedVotes': np.float64,
                    'voter.delegatedVotesRaw': np.float64,
                    'voter.tokenHoldersRepresentedAmount': np.uint,
                    'proposal.startBlock': np.uint,
                    'proposal.endBlock': np.uint,
                    'proposal.totalSupply': np.uint
                }
 
    df = df.astype(convert_dict)

    unique_addresses = df['voter.id'].unique()

    with open('./ens_map.pickle', 'rb') as handle:
        ens_map = pickle.load(handle)

    for address in unique_addresses:
        if address in ens_map:
            df.loc[df['voter.id']==address, 'ENS'] = ens_map[address]
        else:
            ENS = ns.name(address)
            ens_map[address] = ENS
            df.loc[df['voter.id']==address, 'ENS'] = ens_map[address]

    with open('./ens_map.pickle', 'wb') as handle:
        pickle.dump(ens_map, handle, protocol=pickle.HIGHEST_PROTOCOL) 
    

    """
        "proposal.delegatesAtStart": "Proposal Delegate Holders",
        "proposal.againstWeightedVotes": "Against Weighted Votes",
        "proposal.totalDelegateVotes": "Total Delegate Votes",
        "proposal.forWeightedVotes": "For Weighted Votes",
        "proposal.abstainWeightedVotes": "Abstain Weighted Votes",
        "proposal.totalWeightedVotes": "Total Weighted Votes",
    """
    # drop and add columns
    df.rename(columns={
                    "voter.id": "Voter Address",
                    "voter.delegatedVotes": "Current Delegated Votes to Voter",
                    "voter.delegatedVotesRaw": "Current Delegated Votes Raw to Voter",
                    "voter.tokenHoldersRepresentedAmount": "Voter Token Holders Represented",
                    "proposal.status": "Proposal State",
                    "proposal.id": "Proposal ID",
                    "proposal.quorumVotes": "Quorum Votes",
                    "blockNumber": "Vote Time",
                    "proposal.againstVotes": "Against Delegate Votes",
                    "proposal.forVotes": "For Delegate Votes",
                    "proposal.abstainVotes": "Abstain Delegate Votes",
                    "proposal.createdTimestamp": "Proposal Date Created",
                    "proposal.startBlock": "Proposal Date Start",
                    "proposal.endBlock": "Proposal Date End",
                    "proposal.createdBlock": "Proposal Created",
                    "proposal.proposer.id": "Proposal Author",
                    "proposal.totalSupply": "Total Supply at Time",
                    "supportDetailed": "Voter Choice",
                    "votes": "Weight"
                }, inplace=True)

    os.makedirs(f"./res/{query}", exist_ok=True)
    
    cols_to_move= ['ENS', 'Voter Address']
    df = df[cols_to_move + [ col for col in df.columns if col not in cols_to_move]]
    first_column = df.pop('DAO Name')
    df.insert(0, 'DAO Name', first_column)
    df.drop(columns=['id', 'support', 'Proposal Author', 'Proposal Date Created', 'Proposal Created'], index=1, inplace=True)
    df.drop(df.filter(regex="Unname"),axis=1, inplace=True, errors='ignore')



    # Custom Logic
    df["DAO Token Supply"] = df["Total Supply at Time"].iat[-1]
    df["Voter Power"] = df[["Weight"]].div(df['Total Supply at Time'].values, axis=0)
    df["block"] = df["Vote Time"]

    # Save
    try:
        daopath = "./res/votes/Nouns.csv"
        daodf = pd.read_csv(daopath, index=False)
        print("found previously stored data")
        daodf = pd.concat([daodf, df], ignore_index=True)
        daodf.to_csv(daopath, index=False)
        df = daodf

    except:
        print("could not find previously stored data")
        df.to_csv(f"./res/{query}/{dao}.csv", index=False)

    print("successfuly saved")
    return df

def make_client(api):
    transport = AIOHTTPTransport(url=api)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client

def save_as_csv(dao, query, counter, result):
    os.makedirs(f"./res/{dao}/{query}", exist_ok=True)
    df = pd.json_normalize(result[query], max_level=1)
    df = df.to_csv(f"./res/{dao}/{query}/{counter}.csv")

        
def query(dao, api, _query):
    client = make_client(api) 
    
    if _query == "delegates":
        delegateQuery(client, dao, _query)

    if _query == "delegations":
        delegationQuery(client, dao, _query)

    if _query == "governances":
        governanceQuery(client, dao, _query)

    if _query == "proposals":
        proposalQuery(client, dao, _query)
    
    if _query == "votes":
        voteQuery(client, dao, _query)


def delegateQuery(client, dao, _query):

    _delegateQuery = gql(  """
              query($lastID: ID) {
                delegates (first:1000, where: {id_gt: $lastID}) {  
                    id
                    delegatedVotesRaw
                    delegatedVotes
                    tokenHoldersRepresentedAmount
                    tokenHoldersRepresented {
                      id
                    }
                    nounsRepresented{
                          id
                    }
                    votes{
                        id
                        support
                        proposal{
                            id
                        }
                    }
                    proposals {
                      id
                    }
                }  
              }
       """)


    params = {
                "lastID": ""
        }
    

    loadmore = True
    counter = 1
    length = 0

    while loadmore:
        
        curr = client.execute(_delegateQuery, variable_values=params)
        length += len(curr['delegates'])
        
        if len(curr['delegates']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['delegates'][-1]['id']
            save_as_csv(dao, _query, counter, curr)
            counter += 1
        gc.collect()
    print(_query, length)

def governanceQuery(client, dao, _query):
    _governancesQuery = gql(
            """
                    {
                      governances {
                        id
                        currentTokenHolders
                        totalTokenHolders
                        currentDelegates
                        totalDelegates
                        delegatedVotesRaw
                        delegatedVotes
                        proposals
                        proposalsQueued
                      }
                    }
            """)
    result = client.execute(_governancesQuery)
    save_as_csv(dao, _query, 0, result)

def proposalQuery(client, dao, _query):

    _proposalQuery = gql(  """
              {
                  proposals{
                    id
                    description
                    proposer{
                        id
                    }
                    quorumVotes
                    proposalThreshold
                    forVotes
                    againstVotes
                    abstainVotes
                    status
                    createdTimestamp
                    createdBlock
                    votes{
                      support
                      supportDetailed
                      voter{
                        id
                      }
                    }
                    totalSupply
                    startBlock
                    endBlock
                  }
                }
       """)

    result = client.execute(_proposalQuery)
    save_as_csv(dao, _query, 0, result)

def voteQuery(client, dao, _query):
    
    params = {
                "lastBlock": "0"
        }

    votes = pd.DataFrame()
    

    try:
        df = pd.read_csv(f"./res/votes/{dao}.csv", index_col=None)
        df = df.sort_values(by=["block"])
        params["lastBlock"] = str(df["block"].iloc[-1])
        lastBlock = params["lastBlock"]
        loaded=True

        print(f"Found lastBlock for {dao} at {lastBlock}")

    except:
        print(f"Could not find CSV for {dao}")
        loaded=False

    _voteQuery = gql(  """
              query($lastBlock: BigInt) {
                  votes (orderBy: blockNumber, orderDirection: asc, first:1000, where: {blockNumber_gt: $lastBlock}) {
                        id
                        supportDetailed
                        support
                        votes
                        voter{
                          id
                          delegatedVotes
                          delegatedVotesRaw
                          tokenHoldersRepresentedAmount
                        }
                        proposal{
                          id
                          proposer{
                            id
                          }
                          status
                          startBlock
                          endBlock
                          quorumVotes
                          forVotes
                          againstVotes
                          abstainVotes
                          totalSupply
                          createdTimestamp
                          createdBlock
                        }
                        blockNumber
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
            if currlen == 0 and loaded:
                print("There were no new votes to add")
                return
        
        else:
            
            if currlen == 0:
                loadmore = False
            else:
                # update params
                params["lastBlock"] = curr['votes'][-1]['blockNumber']
                df = pd.json_normalize(curr['votes'], max_level=2)
                votes = pd.concat([votes, df], ignore_index=True)
                counter += 1

    print("Total added votes: ", length)
    votes = handle_Nounvote(dao, _query, votes)

def delegationQuery(client, dao, _query):

    _delegationQuery = gql(  """
              query($lastID: ID) {
                  delegationEvents (first:1000, where: {id_gt: $lastID}) {
                        id
                        noun{
                            id
                            owner{
                                id
                            }
                        }
                        previousDelegate{
                            id
                            delegatedVotes
                        }
                        newDelegate{
                            id
                            delegatedVotes
                        }
                        blockNumber
                        blockTimestamp
                      }
                    }       """)


    params = {
                "lastID": ""
        }
    

    loadmore = True
    counter = 1
    length = 0

    while loadmore:
        
        curr = client.execute(_delegationQuery, variable_values=params)
        length += len(curr['delegations'])
        
        if len(curr['delegations']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['delegations'][-1]['id']
            save_as_csv(dao, _query, counter, curr)
            counter += 1
        gc.collect()
    print(_query, length)

for _query in queries:
    query(dao, api, _query)
    gc.collect()
