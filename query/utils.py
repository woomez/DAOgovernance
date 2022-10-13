import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
import datetime
import glob
import os
import json
from flatten_json import flatten
from blocktimecal import get_block_timestamp

def read_json(filename: str) -> dict:
    try:
        with open(filename, "r") as f:
            data = json.loads(f.read())
    except:
        raise Exception(f"Reading {filename} file encountered an error")
  
    return data

class Conversion():
    def handle_governances(self, path, file, jsonData):
        governance = pd.json_normalize(jsonData["governances"])
        governance.to_csv(f"{path}/csv/governance.csv", index=False)
    
    def handle_proposals(self, path, file, jsonData):
        flattenedj = pd.DataFrame(flatten(proposal, '.') for proposal in jsonData['proposals'])
        flattenedj.to_csv(f"{path}/csv/proposal_{file}.csv", index=False)
        proposals = pd.json_normalize(jsonData["proposals"], max_level=1)
        proposals.to_csv(f"{path}/csv/proposal{file}.csv", index=False)

    def handle_delegations(self, path, file, jsonData):
        delegations = pd.json_normalize(jsonData["delegations"], max_level=1)
        delegations.to_csv(f"{path}/csv/delegations{file}.csv", index=False)

    def handle_votedailysnapshots(self, path, file, jsonData):
        votedailysnapshots = pd.json_normalize(jsonData["voteDailySnapshots"], max_level=1)
        votedailysnapshots.to_csv(f"{path}/csv/votedailysnapshots{file}.csv", index=False)

    def handle_tokendailysnapshots(self, path, file, jsonData):
        tokendailysnapshots = pd.json_normalize(jsonData["tokenDailySnapshots"])
        tokendailysnapshots.to_csv(f"{path}/csv/tokendailysnapshots{file}.csv", index=False)

    def handle_delegates(self, path, file, jsonData):
        delegates = pd.json_normalize(jsonData["delegates"], max_level=1)
        delegates.to_csv(f"{path}/csv/delegates{file}.csv", index=False)

    def handle_votes(self, path, file, jsonData):
        votes = pd.json_normalize(jsonData["votes"], max_level=1)
        votes.to_csv(f"{path}/csv/votes{file}.csv", index=False)
    
"""  
TODO
from proposal
convert block time to proposal created, proposal start, proposal end
proposal author
"""

  
def traverse_tree(path, conversion_methods):
    for root, dirs, files in os.walk(path):
        convert_json(root, files, conversion_methods)

def convert_json(folder, files, conversion_methods):
    conversion = Conversion()
    method = os.path.basename(os.path.normpath(folder))
    # if folder in conversion_methods:
    if method in conversion_methods:
        os.makedirs(f'{folder}/csv', exist_ok=True)
        conversion_method = getattr(conversion, "handle_"+method)
        for file in files:
            if file.endswith(".json"):
                jsonpath = folder+"/"+file
                _jsonData = read_json(jsonpath)
                conversion_method(folder, file, _jsonData)

def combine_csvs(path, vote_csv, delegation_csv):
    for root, dirs, files in os.walk(path):
        two = os.sep.join(os.path.normpath(root).split(os.sep)[-2:])

        if two == 'votes/csv':
            dao = root.split(os.path.sep)[-3]
            print(dao)
            for file in files:
                df =pd.read_csv(os.path.join(root,file), index_col=None, header=0)
                df['dao'] = dao
                df['Offchains'] = 0
                df['choices'] = df.apply(lambda x: ['FOR', 'AGAINST', 'ABSTAIN'], axis = 1)                
                vote_csv = pd.concat([vote_csv, df], ignore_index=True)
                
        elif two == 'delegations/csv':
            dao = root.split(os.path.sep)[-3]
            print(dao)
            for file in files:
                df =pd.read_csv(os.path.join(root,file), index_col=None, header=0)
                df['dao'] = dao
                delegation_csv = pd.concat([delegation_csv, df], ignore_index=True)

    vote_csv.to_csv(path+"/votescombined.csv", index=False)
    delegation_csv.to_csv(path+"/delegationscombined.csv", index=False)

    return vote_csv, delegation_csv

def add_paramters_csvs(path, votedf):
    os.makedirs(path+f'/proposalcombined', exist_ok=True)
    cpath = "/Users/jaeyongpark/codes/governance/query/res/votecombined/"
    dpath = "/Users/jaeyongpark/codes/governance/query/res/proposalcombined/"

    for root, dirs, files in os.walk(path):
        two = os.sep.join(os.path.normpath(root).split(os.sep)[-2:])
        if two == 'governances/csv':
            dao = root.split(os.path.sep)[-3]
            for file in files:
                df = pd.read_csv(os.path.join(root, file), index_col=None, header=0)
                total_delegations = df['totalDelegations']
                
                #filter dao and add totalDelegations
                # daoindex = votedf.index[votedf['dao']==dao]
                # votedf.loc[daoindex, 'totalDelegations'] = str(total_delegations[0])

        if two == 'proposals/csv':
            dao = root.split(os.path.sep)[-3]
            for file in files:
                print("current: ", dao)
                if len(file) == 18:
                    try:
                        cdf = pd.read_csv(cpath+dao+'.csv')
                        df = pd.read_csv(os.path.join(root, file), index_col=None)
                        cdf['proposal.id'] = cdf['proposal.id'].astype(str)
                        df['dao'] = dao
                        df['id'] = df['id'].astype(str)
                        df["startBlock"] = df["startBlock"].astype('Int64')
                        df["startBlock"] = df["startBlock"].fillna(0)
                        df["startBlock"] = df["startBlock"].map(lambda x: get_block_timestamp(x))
                        df["endBlock"] = df["endBlock"].astype('Int64')
                        df["endBlock"] = df["endBlock"].fillna(0)
                        df["endBlock"] = df["endBlock"].map(lambda x: get_block_timestamp(x))
                        df["creationBlock"] = df["creationBlock"].astype('Int64')
                        df["creationBlock"] = df["creationBlock"].fillna(0)
                        df["creationBlock"] = df["creationBlock"].map(lambda x: get_block_timestamp(x))
                        df.rename(columns={
                                "id": "proposal.id"
                            }, inplace=True)
                        
                        cdf = cdf.merge(df, how='outer', on=['proposal.id', 'dao'])
                        cdf.to_csv(dpath+f'/{dao}.csv', index=False)
                        print(dao, 'merged')

                        
                    except:
                        pass
                                        

path = "/Users/jaeyongpark/codes/governance/query/res"
file = "votescombined.csv"
#combine all files in the list
#export to csv
vote_csv = pd.DataFrame()
delegation_csv =pd.DataFrame()

# vote_csv, delegation_csv = combine_csvs(path, vote_csv, delegation_csv)


def combineVotes(path):
    os.makedirs(path+f'/votecombined', exist_ok=True)
    
    for root, dirs, files in os.walk(path):
        two = os.sep.join(os.path.normpath(root).split(os.sep)[-2:])
        if two == 'votes/csv':
            df = pd.DataFrame()
            dao = root.split(os.path.sep)[-3]
            for file in files:
                try:
                    cdf = pd.read_csv(os.path.join(root, file), index_col=None)
                    df = pd.concat([cdf, df], ignore_index=True)
                    df['dao'] = dao
                    df['Offchains'] = 0
                    df['choices'] = df.apply(lambda x: ['FOR', 'AGAINST', 'ABSTAIN'], axis = 1)
                    df['proposal.id'] = df['proposal.id'].astype(str)
                    df.to_csv(path+f'/votecombined/{dao}.csv')
                except:
                    pass

#combineVotes(path)
df = pd.DataFrame()
# add_paramters_csvs(path, df)

dpath = "/Users/jaeyongpark/codes/governance/query/res/proposalcombined/"

def combineres(path):
    df = pd.DataFrame()

    for root, dirs, files in os.walk(path):
        dao = root.split(os.path.sep)[-3]
        for file in files:
            try:
                cdf = pd.read_csv(os.path.join(root, file), index_col=None)
                df = pd.concat([cdf, df], ignore_index=True)

            except:
                pass
    # trim
    df.drop(columns=['Unnamed: 0', 'votes', 'id'], index=1, inplace=True)

    df.rename(columns={
                    "dao": "DAO Name",
                    "voter.id": "Voter",
                    "Offchains": "Offchain?",
                    "proposal.id": "Proposal ID",
                    "creationBlock": "Proposal Date Created",
                    "startBlock": "Proposal Date Start",
                    "endBlock": "Proposal Date End",
                    "proposer.id": "Proposal Author",
                    "choices": "Proposal Choices",
                    "choice": "Voter Choice",
                    "reason": "Voter Reason",
                    "txnHash": "Transaction Hash",
                    "Voter": "Voter Address"
                }, inplace=True)
    df.to_csv(dpath+f'/final_onchain.csv')
    
# combineres(dpath)


df = pd.read_csv("/Users/jaeyongpark/codes/governance/query/res/proposalcombined/final_onchain.csv")

def add_gov_paramters_csvs(cdf):
    finalpath = "/Users/jaeyongpark/codes/governance/query/res"

    for root, dirs, files in os.walk(finalpath):
        two = os.sep.join(os.path.normpath(root).split(os.sep)[-2:])
        if two == 'governances/csv':
            dao = root.split(os.path.sep)[-3]
            for file in files:
                df = pd.read_csv(os.path.join(root, file), index_col=None, header=0)
                total_supply = df['totalTokenSupply']
                print(total_supply)
                #filter dao and add totalDelegations
                daoindex = cdf.index[cdf['DAO Name']==dao]
                cdf.loc[daoindex, 'DAO Token Supply'] = str(total_supply[0])

    cdf.to_csv(finalpath+'final_onchain.csv', index=False)
    


add_gov_paramters_csvs(df)

