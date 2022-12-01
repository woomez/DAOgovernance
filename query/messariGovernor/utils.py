import pandas as pd
import numpy as np
import os
import pickle


"""
TODO 
make ENS dict
update ENS Column
        - find Unique addresses
        - convert addresses to name
                - if address in dict:
                        - store name
                - else: look up, add to dict
        - from unique address, name pair, make new column ENS, for each address, if in unique address, store name
"""

def generate_ens(path, ens_map={}):
    """
    Retrieves all ENS ids from current CSV and stores in a dict, which is saved to a pickle
    """
    for root, _, files in os.walk(path):
        for file in files:
            print(file)
            df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
            unique_addresses = df['Voter Address'].unique()
            df['ENS'].fillna('nan', inplace=True)
            for address in unique_addresses:
                if address in ens_map:
                    continue
                ENS = df[df['Voter Address']==address]['ENS'].values[0]
                if ENS != 'nan':
                    ens_map[address] = ENS
    # Save
    with open('ens_map.pickle', 'wb') as handle:
        pickle.dump(ens_map, handle, protocol=pickle.HIGHEST_PROTOCOL)


def ens_map_lookup(df, address):
    pass

def mergeToOne(path):
    """TODO
    
    """
    dpath = path +"/votes"
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
    df.to_csv(path+f'/final_onchain.csv')
    print("finished")

def addGovParamters(path):

    """TODO
    traverse through given folder, 
    add parameters from governances

    later, get token supply from daily snapshot, update accordingly
    """

    vote_path = path+"/votes/"
    gov_path = path+"/governances"
    for root, _, files in os.walk(gov_path):
        for file in files:
            print(file)
            gov_df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
            df = pd.read_csv(vote_path+file, index_col=None, low_memory=False)
            total_supply = gov_df['totalTokenSupply'].astype(np.float64)
            df['DAO Token Supply'] = total_supply[0]
            df['Voter Power'] = df['Weight'].div(df['DAO Token Supply'], axis=0)
            df['Voter Power'] = df['Voter Power'].round(10)
            df.to_csv(vote_path+file, index=False)


def read_and_merge(path):
    
    addGovParamters(path)
    print("merging to one")
    mergeToOne(path)

dpath= "/Users/jaeyongpark/codes/governance/query/messariGovernor/res"
read_and_merge(dpath)
