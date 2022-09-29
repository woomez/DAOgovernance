import pandas as pd
from web3.auto.infura import w3
from ens import ENS

paths = ["ENS_1.csv", "ENS_2.csv"]
ns = ENS.fromWeb3(w3)

def pathtocsv(path):
    df = pd.read_csv(path)
    df = df.sort_values('tokenHoldersRepresentedAmount')
    df = df.reset_index()
    topDelegates = getTopDelegates(df)
    df.to_csv('test_'+path)
    return

def getTopDelegates(df):
    topDelegatesID = df[-4:]['id']
    topDelegatesENS = topDelegatesID.apply(ns.name)
    print(topDelegatesENS)
    return topDelegatesENS

for path in paths:
    pathtocsv(path)




