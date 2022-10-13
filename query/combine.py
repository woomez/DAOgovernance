import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
import datetime
import glob
import os
import json
from flatten_json import flatten

onchain = "/Users/jaeyongpark/codes/governance/query/final_onchain.csv"
offchain = "/Users/jaeyongpark/codes/governance/query/offchain.csv"

def combineres(path):
    
    fdf = pd.read_csv(onchain, index_col=False)
    cdf = pd.read_csv(offchain, index_col=False, sep=',')
    df = pd.concat([cdf, fdf], ignore_index=True)
    df.to_csv(path+f'/combined.csv')

path = "/Users/jaeyongpark/codes/governance/query"
combineres(path)
