import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
import datetime
import glob
import os
import json
from flatten_json import flatten

combined = "/Users/jaeyongpark/codes/governance/query/combined.csv"
new = "/Users/jaeyongpark/codes/governance/query/res/new/final_onchain.csv"
maker = "/Users/jaeyongpark/codes/governance/query/maker/csvs/Maker.csv"

def combineres(path):
    
    fdf = pd.read_csv(combined, index_col=False)
    cdf = pd.read_csv(maker, index_col=False, sep=',')
    df = pd.concat([cdf, fdf], ignore_index=True)
    df['Voter Power'].fillna(0, inplace=True)
    df['Voting Power'].fillna(0, inplace=True)
    df['Voter Power'] = df['Voter Power'] + df['Voting Power']
    df.to_csv(path+f'/combined.csv')

path = "/Users/jaeyongpark/codes/governance/query"
# combineres(path)

df = pd.read_csv(combined, index_col=False)
df['Voter Power'].fillna(0, inplace=True)
df['Voting Power'].fillna(0, inplace=True)
df['Voter Power'] = df['Voter Power'] + df['Voting Power']
df.drop(columns=['Voting Power', 'Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.1.1'], index=1, inplace=True)
df.to_csv(path+"/updated.csv")
