import etherscan
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import numpy as np
import pandas as pd
import os  
import pickle
import json
from ens import ENS
from web3.auto.infura import w3
from etherscan import Etherscan


def getMakerHistErc20Supply(block):
    api_key = 'QFB7NCEGSXA1Y33U19CGBHIMZMRR1CX3KH'

    address = '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'

    eth = Etherscan(api_key)

    supply = eth.get_hist_erc20_token_total_supply_by_contract_address_and_block_no(contract_address=address, block_no=block)

    return supply

ns = ENS.fromWeb3(w3)

# Using protofire stubgraph
api = "https://api.thegraph.com/subgraphs/name/protofire/makerdao-governance"

# Provide GraphQL query
def handle_spell(dao, df):
    # df = df.sort_values(by=["blockNumber"])

    df['DAO Name'] = dao
    df['Offchain?'] = 0
    df['Proposal Choices'] = df.apply(lambda x: ['Add', 'Remove', 'Free', 'Lock'], axis = 1)

    # change data types
    convert_dict2 = {'proposal.id': str,
                    'votes': np.float64,
                    'voter.delegatedVotes': np.float64,
                    'voter.delegatedVotesRaw': np.float64,
                    'voter.tokenHoldersRepresentedAmount': np.uint,
                    'proposal.startBlock': np.uint,
                    'proposal.endBlock': np.uint,
                    'proposal.totalSupply': np.uint
                }
    
    convert_dict ={'_wad': np.float64,
                   '_locked': np.float64}

    df = df.astype(convert_dict)
    df['_wad'].fillna(0, inplace=True)
    df['_locked'].fillna(0, inplace=True)
    df['Weight'] = df['_wad'] + df['_locked']

    unique_addresses = df['_sender'].unique()

    with open('./ens_map.pickle', 'rb') as handle:
        ens_map = pickle.load(handle)

    for address in unique_addresses:
        if address in ens_map:
            df.loc[df['_sender']==address, 'ENS'] = ens_map[address]
        else:
            ENS = ns.name(address)
            ens_map[address] = ENS
            df.loc[df['_sender']==address, 'ENS'] = ens_map[address]

    with open('./ens_map.pickle', 'wb') as handle:
        pickle.dump(ens_map, handle, protocol=pickle.HIGHEST_PROTOCOL) 
   

    """
        "proposal.delegatesAtStart": "Proposal Delegate Holders",
        "proposal.againstWeightedVotes": "Against Weighted Votes",
        "proposal.totalDelegateVotes": "Total Delegate Votes",
        "proposal.forWeightedVotes": "For Weighted Votes",
        "proposal.abstainWeightedVotes": "Abstain Weighted Votes",
        "proposal.totalWeightedVotes": "Total Weighted Votes",
        "voter.delegatedVotes": "Current Delegated Votes to Voter",
        "voter.delegatedVotesRaw": "Current Delegated Votes Raw to Voter",
    """
    # drop and add columns
    df.rename(columns={
                    "_timestamp": "Vote Time",
                    "_transactionHash": "Transaction Hash",
                    "_sender": "Voter Address",
                    "_type": "Voter Choice",
                    "_block": "block",
                    "id": "Proposal ID",
                    "timestamp": "Proposal Date Created",
                    "approvals": "Total Weighted Votes",
                    "totalVotes": "Total Delegate Votes",
                    "liftedWith": "Quorum Votes",
                    "lifted": "Proposal Date Start"
                }, inplace=True)
    

    os.makedirs(f"./res/votes", exist_ok=True)

    cols_to_move= ['ENS', 'Voter Address']
    df = df[cols_to_move + [ col for col in df.columns if col not in cols_to_move]]
    first_column = df.pop('DAO Name')
    df.insert(0, 'DAO Name', first_column)
    df.drop(columns=['_id', '_locked', '_wad', 'casted', 'castedWith'], index=1, inplace=True)
    df.drop(df.filter(regex="Unname"),axis=1, inplace=True, errors='ignore')

    df.to_csv("./test.csv")

    # Custom Logic
    """
    TODO

    understand approval
    use etherscan api to compute Voter Power
    """
    df["DAO Token Supply"] = df["block"].map(getMakerHistErc20Supply)
    df["Voter Power"] = df[["Weight"]].div(df['DAO Token Supply'].values, axis=0)

    # Save
    try:
        daopath = "./res/votes/Maker.csv"
        daodf = pd.read_csv(daopath, index=False)
        print("found previously stored data")
        daodf = pd.concat([daodf, df], ignore_index=True)
        daodf.to_csv(daopath, index=False)
        df = daodf

    except:
        print("could not find previously stored data")
        df.to_csv(f"./res/votes/{dao}.csv", index=False)

    print("successfuly saved")
    return df



def voteQuery(client, dao, _query):
    
    params = {
                "lastID": ""
        }

    votes = pd.DataFrame()
    
    loaded=False
    try:
        df = pd.read_csv(f"./res/votes/{dao}.csv", index_col=None)
        df = df.sort_values(by=["block"])
        params["lastBlock"] = str(df["block"].iloc[-1])
        lastBlock = params["lastBlock"]
        loaded=True
        print(f"Found lastBlock for {dao} at {lastBlock}")

    except:
        print(f"Could not find CSV for {dao}")


    _spellQuery = gql(  """
            query($lastID: ID){
                spells(orderBy: id, orderDirection:asc, first: 1000, where:{id_gt: $lastID}) {
                id
                timestamp
                approvals
                totalVotes
                casted
                castedWith
                lifted
                liftedWith
                timeLine {
                  id
                  timestamp
                  block
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
            """)
    
    loadmore = True
    counter = 1
    length = 0
    firstcheck = True

    while loadmore:
        
        curr = client.execute(_spellQuery, variable_values=params)
        currlen = len(curr['spells'])
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
                params["lastID"] = curr['spells'][-1]['id']
                spells = pd.json_normalize(curr["spells"], record_path='timeLine', meta=['id', 'timestamp', 'approvals', 'casted', 'castedWith', 'lifted', 'liftedWith'], record_prefix='_')
                votes = pd.concat([votes, spells], ignore_index=True)
                counter += 1

    print("Total added votes: ", length)
    votes = handle_spell(dao, votes)


# for _query in queries:

"""
get results for gov

gov = client.execute(govquery)
govdf = pd.json_normalize(gov['governanceInfo'])
govdf.to_csv(f"./csvs/maker_gov.csv")


"""
def make_client(api):
    transport = AIOHTTPTransport(url=api)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client

def generate_Maker_votes(dao, api):
    client = make_client(api)
    voteQuery(client, dao, 'votes')

generate_Maker_votes('Maker', api)
#os.makedirs(f"./res/{dao}/{query}", exist_ok=True)
#    with open(f'./res/{dao}/{query}/'+f'{counter}.json', 'w') as outfile:
#        json.dump(result, outfile)



