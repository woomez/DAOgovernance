import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
import datetime
import glob
import os
import json
from flatten_json import flatten

path = "./res/votes"

def mergeToOne(path):
    df = pd.DataFrame()

    for root, _, files in os.walk(path):
        for file in files:
            try:
                
                #if file doesn't end with .csv:
                if file.endswith('.csv') and file.split('_')[-1] != 'temp.csv':
                    print(file)
                    cdf = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
                    df = pd.concat([cdf, df], ignore_index=True)

            except:
                pass
    # df['weight'] = df['weight'].div(10**18).round(5)
    # df['DAO Token Supply'] = df['DAO Token Supply'].div(10**18).round(5)
    df.drop(df.filter(regex="Unname"),axis=1, inplace=True, errors='ignore')
    df.to_csv("./delegations.csv")
    print("finished")

def combineres(path):
    fdf = pd.read_csv(combined, index_col=False)
    cdf = pd.read_csv(maker, index_col=False, sep=',')
    df = pd.concat([cdf, fdf], ignore_index=True)
    df['Voter Power'].fillna(0, inplace=True)
    df['Voting Power'].fillna(0, inplace=True)
    df['Voter Power'] = df['Voter Power'] + df['Voting Power']
    df.to_csv(path+f'/combined.csv')

path = "/Users/jaeyongpark/codes/governance/query/res/delegations"
# combineres(path)

mergeToOne(path)
