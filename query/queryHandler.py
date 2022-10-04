from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import os
import gc

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
    os.makedirs(f"./res/{dao}/{query}", exist_ok=True)
    with open(f'./res/{dao}/{query}/'+f'{counter}.json', 'w') as outfile:
        json.dump(result, outfile)


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
    total_delegates = 0

    while loadmore:
        
        curr = client.execute(_delegateQuery, variable_values=params)
        total_delegates += len(curr['delegates'])
        
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
                        totalDelegations
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
    save_query_as_json(dao, _query, 0, result)

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

    _voteQuery = gql(  """
              query($lastID: ID) {
                  votes (first:1000, where: {id_gt: $lastID}) {
                        id
                        choice
                        weight
                        reason
                        voter{
                          id
                        }
                        proposal{
                          id
                        }
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
    total_delegates = 0

    while loadmore:
        
        curr = client.execute(_voteQuery, variable_values=params)
        total_delegates += len(curr['votes'])
        
        if len(curr['votes']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['votes'][-1]['id']
            print(total_delegates)
            # save to csv
            # delegations = pd.json_normalize(curr['delegates'])
            # delegations.to_csv(f"./csvs/delegations/{name}/{name}_{count}.csv")

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        gc.collect()

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
    total_delegates = 0

    while loadmore:
        
        curr = client.execute(_delegationQuery, variable_values=params)
        total_delegates += len(curr['delegations'])
        
        if len(curr['delegations']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['delegations'][-1]['id']
            print(total_delegates)
            # save to csv
            # delegations = pd.json_normalize(curr['delegates'])
            # delegations.to_csv(f"./csvs/delegations/{name}/{name}_{count}.csv")

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        gc.collect()


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
    total_delegates = 0

    while loadmore:
        
        curr = client.execute(_votedailysnapshotQuery, variable_values=params)
        total_delegates += len(curr['voteDailySnapshots'])
        
        if len(curr['voteDailySnapshots']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['voteDailySnapshots'][-1]['id']
            print(total_delegates)

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        gc.collect()

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
    total_delegates = 0

    while loadmore:
        
        curr = client.execute(_tokendailysnapshotQuery, variable_values=params)
        total_delegates += len(curr['tokenDailySnapshots'])
        
        if len(curr['tokenDailySnapshots']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['tokenDailySnapshots'][-1]['id']
            print(total_delegates)

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        gc.collect()
