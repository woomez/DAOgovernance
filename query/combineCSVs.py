import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
import datetime
import gc
import os
from utils import get_block_timestamp

"""
Combine and format results for Onchain data
"""


                      
def combineVotes(path):
    """
    Combine separate vote files into one, store them in votecombined
    """

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
                    
                except:
                    pass
            df['dao'] = dao
            df['Offchains'] = 0
            df['choices'] = df.apply(lambda x: ['FOR', 'AGAINST', 'ABSTAIN'], axis = 1)
            df['proposal.id'] = df['proposal.id'].astype(str)
            df['weight'] = df['weight'].astype(np.float64)
            df.to_csv(path+f'/votecombined/{dao}.csv')

def addProposalToVotes(path):
    """
    After combining votes, add dao proposal params to votes, refactor and store in proposalAdded folder
    """

    os.makedirs(path+f'/proposalAdded', exist_ok=True)
    cpath = path+"/votecombined/"
    dpath = path+"/proposalAdded/"

    for root, _, files in os.walk(path):
        two = os.sep.join(os.path.normpath(root).split(os.sep)[-2:])

        if two == 'proposals/csv':
            dao = root.split(os.path.sep)[-3]
            for file in files:
                if os.path.exists(cpath+dao+'.csv'):
                    cdf = pd.read_csv(cpath+dao+'.csv', low_memory=False)
                    df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
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

                    cdf = rename_cols(cdf)
                    cdf.to_csv(dpath+f'{dao}.csv', index=False)
                    print(dao, 'merged')
                    gc.collect()
                    
                 

def rename_cols(df):
    df.drop(columns=['Unnamed: 0', 'votes', 'id', 'description'], index=1, inplace=True)
    df.rename(columns={
                    "dao": "DAO Name",
                    "voter.id": "Voter Address",
                    "Offchains": "Offchain?",
                    "proposal.id": "Proposal ID",
                    "creationBlock": "Proposal Date Created",
                    "startBlock": "Proposal Date Start",
                    "endBlock": "Proposal Date End",
                    "proposer.id": "Proposal Author",
                    "choices": "Proposal Choices",
                    "choice": "Voter Choice",
                    "reason": "Voter Reason",
                    "txnHash": "Transaction Hash"
                }, inplace=True)

    return df

def combineDelegations(path):
    """
    Combine all delegations into one, store in delegationscombined.csv
    """

    delegations = pd.DataFrame()
    for root, _, files in os.walk(path):
        two = os.sep.join(os.path.normpath(root).split(os.sep)[-2:])
                
        if two == 'delegations/csv':
            dao = root.split(os.path.sep)[-3]
            for file in files:
                df =pd.read_csv(os.path.join(root,file), index_col=None, header=0)
                df['dao'] = dao
                delegations = pd.concat([delegations, df], ignore_index=True)

    delegations.to_csv(path+"/delegationscombined.csv", index=False)

    return delegations

def mergeToOne(path):
    dpath = path+"/proposalAdded"
    df = pd.DataFrame()

    for root, _, files in os.walk(dpath):
        for file in files:
            try:
                cdf = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
                df = pd.concat([cdf, df], ignore_index=True)

            except:
                pass
    # df['weight'] = df['weight'].div(10**18).round(5)
    # df['DAO Token Supply'] = df['DAO Token Supply'].div(10**18).round(5)
    df['Voting Power'] = df['Voting Power'].round(10)
    df.to_csv(path+f'/final_onchain.csv')
    print("finished")
   

def addGovParamters(path):
    dpath = path+"/proposalAdded/"
    for root, _, files in os.walk(path):
        two = os.sep.join(os.path.normpath(root).split(os.sep)[-2:])
        if two == 'governances/csv':
            dao = root.split(os.path.sep)[-3]
            if os.path.exists(dpath+dao+'.csv'):
                cdf = pd.read_csv(dpath+dao+'.csv', index_col=None)
                for file in files:
                    df = pd.read_csv(os.path.join(root, file), index_col=None)
                    total_supply = df['totalTokenSupply'].astype(np.float64)
                    # cdf['DAO Token Supply'] = total_supply[0]
                    cdf['Voting Power'] = cdf['weight'].div(cdf['DAO Token Supply'], axis=0)
                    # daoindex = cdf.index[cdf['DAO Name']==dao]
                    # cdf.loc[daoindex, 'DAO Token Supply'] = str(total_supply[0])

                    cdf.to_csv(dpath+dao+'.csv', index=False)
    
def read_and_merge(path):
    print("combining votes")
    # combineVotes(path)
    print("adding proposals and gov paramaters")
    # addProposalToVotes(path)
    #addGovParamters(path)
    print("merging to one")
    mergeToOne(path)
    print("combining delegations")
    #combineDelegations(path)

