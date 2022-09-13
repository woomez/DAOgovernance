from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import os
import gc

def make_client(api):
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=api)
    
    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    return client

def save_query_as_json(dao, query, counter, result):
    os.makedirs(f"./res/{dao}", exist_ok=True)
    with open(f'./res/{dao}/{query}'+"_"+f'{counter}.json', 'w') as outfile:
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

def delegateQuery(client, dao, _query):

    _delegateQuery = gql(  """
              query($lastID: String) {
                delegates (first:1000, where: {id_gt: $lastID}) {  
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
                    againstDelegateVotes
                    forDelegateVotes
                    abstainDelegateVotes
                    totalDelegateVotes
                    againstDelegateVotes
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
              query($lastID: String) {
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
       
