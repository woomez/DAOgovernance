import pickle
from tqdm import tqdm
import time
import pandas as pd
import numpy as np
import os
import pickle
from ens import ENS
from web3 import Web3
from web3.auto.infura import w3


# look up value of 0xd9ffaf2e880df0cc7b7104e9e789d281a81824cf in ens_map
with open('./ens_map.pickle', 'rb') as handle:
    ens_map = pickle.load(handle)

df = pd.read_csv('./res/delegations/Gitcoin.csv', index_col=0)
# print where column Previous Delegate ENS is null
# print column names of dfc
# get rows that are null

mask = df['Previous Delegate ENS'].isnull()
print(df[mask].iloc[0]['Previous Delegate ENS'])
# df[mask] to a csv 
#df[mask].to_csv('./res/delegations/Gitcoin_null.csv')
delegators = df.loc[mask, 'Previous Delegate'].unique()

a = df.loc[df['Previous Delegate'] == '0x16d2ad8cc04888b537bb7b631715335a901b57ca']
# print rows where column Previous Delegate is equal to 0x00000000

# create df columns where all values are the string 'nan'
dfc = pd.DataFrame(np.nan, index=np.arange(len(df)), columns=['Previous Delegate ENS'])
dfc = dfc.fillna('nan')
dfc = dfc.astype(str)

if '0xf733454bb020b76cfc9c4ad80367bab412edbffb' in ens_map:
    print('found')
else:
    print('not found')


