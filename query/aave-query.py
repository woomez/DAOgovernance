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
    os.makedirs(f"./res/new/{dao}/{query}", exist_ok=True)
    with open(f'./res/new/{dao}/{query}/'+f'{counter}.json', 'w') as outfile:
        json.dump(result, outfile)


def query(dao, api, _query):
    client = make_client(api) 
    
    if _query == "governances":
        governanceQuery(client, dao, _query)

    if _query == "proposals":
        proposalQuery(client, dao, _query)
    
    if _query == "votes":
        voteQuery(client, dao, _query)



def proposalQuery(client, dao, _query):

    _proposalQuery = gql(  """
              {
                  proposals{
                    id: ID!
                    state: ProposalState!
                    ipfsHash: String!
                    creator: Bytes!
                    executor: Executor
                    targets: [Bytes!]
                    values: [BigInt!]
                    signatures: [String!]
                    calldatas: [Bytes!]
                    withDelegatecalls: [Boolean!]
                    startBlock: BigInt!
                    endBlock: BigInt!
                    governanceStrategy: Bytes!
                    currentYesVote: BigInt!
                    currentNoVote: BigInt!
                    winner: Winner!
                    votes: [Vote!]!
                    createdTimestamp: Int!
                    executionTime: BigInt
                    initiatorQueueing: Bytes
                    initiatorExecution: Bytes
                    lastUpdateTimestamp: Int!
                    lastUpdateBlock: BigInt!
                    title: String!
                    shortDescription: String!
                    govContract: Bytes!
                    totalPropositionSupply: BigInt!
                    totalVotingSupply: BigInt!
                    createdBlockNumber: BigInt!
                    totalCurrentVoters: Int!
                    aipNumber: BigInt!
                    author: String!
                    discussions: String! 
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
    length = 0

    while loadmore:
        
        curr = client.execute(_voteQuery, variable_values=params)
        length += len(curr['votes'])
        
        if len(curr['votes']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['votes'][-1]['id']
            # save to csv
            # delegations = pd.json_normalize(curr['delegates'])
            # delegations.to_csv(f"./csvs/delegations/{name}/{name}_{count}.csv")

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        
        gc.collect()
    print(_query, length)

