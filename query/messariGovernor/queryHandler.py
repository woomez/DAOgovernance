from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import os
import gc
import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
from web3 import Web3
from web3.exceptions import BlockNotFound
import pickle

"""
Contains functions for querying endpoints of the graph:
    - Uses the Messari Governance query modules
    - Currently works for governance, votes, daily snapshots

TODO:
    handle int input from gql transport to update changes in blocks
        - whereblock from API

for gov, if total supply is 0, add to list
write function to add new params.
"""

ns = ENS.fromWeb3(w3)

def get_block_timestamp(block_num):
    infura_url = 'https://mainnet.infura.io/v3/d01265cbfef74bc2a7bf83a6ed7840e5'
    if block_num == 0:
        return

    web3 = Web3(Web3.HTTPProvider(infura_url))
    """Get Ethereum block timestamp"""
    try:
        block_info = web3.eth.getBlock(block_num)
    except BlockNotFound:
        return None
    last_time = block_info["timestamp"]
    return last_time

def generate_results(url, _queries):
    dao, api = url
    print(f"starting process for {dao}")
    for _query in _queries:
        query(dao, api, _query)
        gc.collect()

def make_client(api):
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=api)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client

def save_query_as_json(dao, query, counter, result):
    os.makedirs(f"./res/new/{dao}/{query}", exist_ok=True)
    with open(f'./res/new/{dao}/{query}/'+f'{counter}.json', 'w') as outfile:
        json.dump(result, outfile)

def save_as_csv(dao, query, df):
    os.makedirs(f"./res/{query}", exist_ok=True)
    df.to_csv(f"./res/{query}/{dao}.csv")

def apply_unique(df, orig_col, new_col, func):
    return df.merge(df[[orig_col]]
                    .drop_duplicates()
                    .assign(**{new_col: lambda x: x[orig_col].apply(func)}
                           ), how='inner', on=orig_col)

def handle_ens(df):
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

    return df


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

def query(dao, api, _query):
    client = make_client(api) 
    
    if _query == "delegates":
        delegateQuery(client, dao, _query)

    if _query == "governances":
        governanceQuery(client, dao, _query)

    if _query == "proposals":
        proposalQuery(client, dao, _query)
    
    if _query == "votes":
        voteQuery(client, dao, _query)

    if _query == "delegations":
        delegationQuery(client, dao, _query)

    if _query == "tokendailysnapshots":
        tokendailysnapshotQuery(client, dao, _query)

    if _query == "votedailysnapshots":
        votedailysnapshotQuery(client, dao, _query)

def delegateQuery(client, dao, _query):

    _delegateQuery = gql(  """
              query($lastID: String) {
                delegates (first:1000, where: {id_gt: $lastID}) {  
                    id
                    delegatedVotesRaw
                    delegatedVotes
                    tokenHoldersRepresentedAmount
                    tokenHoldersRepresented {
                      id
                    }
                    votes{
                        id
                        choice
                        weight
                        proposal{
                            id
                        }
                    }
                    numberVotes
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
            
            # save to csv
            # delegations = pd.json_normalize(curr['delegates'])
            # delegations.to_csv(f"./csvs/delegations/{name}/{name}_{count}.csv")

            save_query_as_json(dao, _query, counter, curr)
            counter += 1
        
        gc.collect()
    print(_query, length)

def governanceQuery(client, dao, _query):
    _governancesQuery = gql(
            """
                    {
                      governances {
                        id
                        totalTokenSupply
                        currentTokenHolders
                        totalTokenHolders
                        currentDelegates
                        totalDelegates
                        delegatedVotesRaw
                        delegatedVotes
                        proposals
                        proposalsQueued
                        proposalsExecuted
                        proposalsCanceled
                      }
                    }
            """)
    result = client.execute(_governancesQuery)
    result = pd.json_normalize(result[_query])
    save_as_csv(dao, _query, result)

def proposalQuery(client, dao, _query):
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

    result = client.execute(_proposalQuery)
    save_query_as_json(dao, _query, 0, result)


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
        return

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

def delegationQuery(client, dao, _query):

    _delegationQuery = gql(  """
              query($lastID: ID) {
                  delegations (first:1000, where: {id_gt: $lastID}) {
                        id
                        delegate{
                            id
                        }
                        delegator{
                            id
                        }
                        delegateTokens
                        delegatorTokens
                        block
                        blockTime
                        txnHash
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
            # save to csv
            # delegations = pd.json_normalize(curr['delegates'])
            # delegations.to_csv(f"./csvs/delegations/{name}/{name}_{count}.csv")

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        
        gc.collect()
    print(_query, length)

def delegationQuery2(client, dao, _query):

    _delegationQuery = gql(  """
              query($lastID: ID) {
                  delegateChanges (first:1000, where: {id_gt: $lastID}) {
                        id
                        delegate
                        delegator
                        previousDelegate
                        delegateTokens
                        delegatorTokens
                        block
                        logIndex
                        txnHash
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
            # save to csv
            # delegations = pd.json_normalize(curr['delegates'])
            # delegations.to_csv(f"./csvs/delegations/{name}/{name}_{count}.csv")

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        
        gc.collect()
    print(_query, length)


def votedailysnapshotQuery(client, dao, _query):

    _votedailysnapshotQuery = gql(  """
              query($lastID: ID) {
                  voteDailySnapshots (first:1000, where: {id_gt: $lastID}) {
                        id
                        proposal{
                            id
                        }
                        forWeightedVotes
                        againstWeightedVotes
                        totalWeightedVotes
                        timestamp
                        blockNumber
                      }
                    }       """)


    params = {
                "lastID": ""
        }
    

    loadmore = True
    counter = 1
    length = 0

    while loadmore:
        
        curr = client.execute(_votedailysnapshotQuery, variable_values=params)
        length += len(curr['voteDailySnapshots'])
        
        if len(curr['voteDailySnapshots']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['voteDailySnapshots'][-1]['id']
            

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        gc.collect()
    print(_query, length)

def tokendailysnapshotQuery(client, dao, _query):

    _tokendailysnapshotQuery = gql(  """
              query($lastID: ID) {
                  tokenDailySnapshots (first:1000, where: {id_gt: $lastID}) {
                        id
                        totalSupply
                        tokenHolders
                        delegates
                        delegations
                        timestamp
                        blockNumber
                      }
                    }       """)


    params = {
                "lastID": ""
        }
    

    loadmore = True
    counter = 1
    length = 0

    while loadmore:
        
        curr = client.execute(_tokendailysnapshotQuery, variable_values=params)
        length += len(curr['tokenDailySnapshots'])
        
        if len(curr['tokenDailySnapshots']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['tokenDailySnapshots'][-1]['id']
            

            save_query_as_json(dao, _query, counter, curr)
            counter += 1
        
        gc.collect()
    print(_query, length)
