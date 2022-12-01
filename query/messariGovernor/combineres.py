
import pandas as pd
import numpy as np
import os


"""
One time:
dao to front

get dailysnapshottokens
"""

def generate_ens(path, ens_map={}):
    """
    one time to handle queries
    """
    for root, _, files in os.walk(path):
        for file in files:
            if file[-4:] == ".csv":
                print(file)
                df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
                cols_to_move= ['ENS', 'Voter Address']
                df = df[cols_to_move + [ col for col in df.columns if col not in cols_to_move]] 
                first_column = df.pop('DAO Name')
                df.insert(0, 'DAO Name', first_column)

                df.drop(df.filter(regex="Unname"),axis=1, inplace=True, errors='ignore')
                df.to_csv(f"./res/votes/new/{file}", index=False)



def mergeToOne(path):
    """
    TODO
    If final_onchain exists, load and add only the new.
    
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
    if token supply is 0, add to list and save
    """

    vote_path = path+"/votes/"
    gov_path = path+"/governances"
    for root, _, files in os.walk(gov_path):
        for file in files:
            print(file)
            gov_df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
            try:
                df = pd.read_csv(vote_path+file, index_col=None, low_memory=False)
                total_supply = gov_df['totalTokenSupply'].astype(np.float64)
                if total_supply[0] == 0:
                    print(file, " has 0 total_supply. Find total_supply from elsewhere.")
                else: 
                    df['DAO Token Supply'] = total_supply[0]
                    df['Voter Power'] = df['Weight'].div(df['DAO Token Supply'], axis=0)
                    df['Voter Power'] = df['Voter Power'].round(10)
                    df.to_csv(vote_path+file, index=False)
            except:
                pass


def read_and_merge(path):
    
    addGovParamters(path)
    print("merging to one")
    mergeToOne(path)


