import pandas as pd
import numpy as np
import os
from utils import handle_ens, log_message
from tqdm import tqdm
"""
TODO:
combine results from transfer
instead of tracking delegate changes, track voting power changes' txnHash

for each transaction hash, store all events. Think about calculating amount last

flags:
0: amount = 0
1: delegate to self w amount > 0
2: delegate to other w amount > 0 
"""

def findMissingRows(dao):
    dcpath = os.path.join("./res/delegateChanges", dao+".csv")
    dc = pd.read_csv(dcpath, index_col=None)
    dvpcpath = os.path.join("./res/delegateVotingPowerChanges", dao+".csv")
    dvpc = pd.read_csv(dvpcpath, index_col=None)
    dvpc_txn_hashes = dvpc["txnHash"].unique()
    dc_txn_hashes = dc["txnHash"].unique()
    dvpc_not_in_dc = dvpc[~dvpc["txnHash"].isin(dc_txn_hashes)]
    dvpc_not_in_dc_count = len([txn_hash for txn_hash in dvpc_txn_hashes if txn_hash not in dc_txn_hashes])
    print(f"total dvpc rows: {len(dvpc)}")
    print(f"total dc rows: {len(dc)}")
    print(f"Rows in dvpc not in dc: {dvpc_not_in_dc_count}")
    txn_hashes_str = ', '.join(dvpc_not_in_dc.head(5)["txnHash"].tolist())
    log_message(f"txnHash of rows in dvpc not in dc (first 5 rows):\n {txn_hashes_str}", "test.log")
    return dvpc_not_in_dc_count
    

def combineDelegations(dao):
    """
    read from dcpath, find matching dvpcpath to combine delegation csv
    dc = delegates changed
    dvpc = delegates voting power changed
    returns a merged dataframe, saved into res/delegations/dao.csv
    """

    zeroAddress = "0x0000000000000000000000000000000000000000"

    ddict = {}

    dcpath = os.path.join("./res/delegateChanges", dao+".csv")
    dc = pd.read_csv(dcpath, index_col=None)
    dvpcpath = os.path.join("./res/delegateVotingPowerChanges", dao+".csv")
    dvpc = pd.read_csv(dvpcpath, index_col=None)
    transferpath = os.path.join("./res/transfer", dao+".csv")
    transfer = pd.read_csv(transferpath, index_col=None)

    cols = ["newBalance", "previousBalance"]
    dvpc = convertNP(dvpc, cols)
    transfer = convertNP(transfer, ["value"])
    
    merged = pd.DataFrame()

    #use tqdm to show progress in bar 
    #store all rows with same txnHash in merged. For now, store all events in same txnHash in same row
    print(f"combineDelegations: Number of delegate changes: {len(dc)}")
    for i, row in tqdm(dvpc.iterrows(), total=dc.shape[0]):
        delegator = row["delegator"]
        prev_del = row["previousDelegate"]
        new_del = row["delegate"]
        blocktime = row["blockTimestamp"]

        # get rows with same transactionHash
        sameTxnDvpcRows = dvpc.loc[dvpc["txnHash"] == dc["txnHash"].values[i]]
        numRows = len(sameTxnDvpcRows)
        
        # if delegator not in ddict, add it and add new_del to list if new_del is not inlist
        if delegator not in ddict:
            ddict[delegator] = []
        if new_del not in ddict[delegator]:
            ddict[delegator].append(new_del)
        amount = flag = -1

        if numRows == 0:
            amount = flag = 0
            merged = appendRow(delegator, prev_del, new_del, amount, flag, ddict[delegator], blocktime, merged)

        if numRows >= 1:
            grouped = sameTxnDvpcRows.groupby("delegate")
            uniqueDelegates = sameTxnDvpcRows["delegate"].nunique()

            if uniqueDelegates > 2:
                log_message(f"combineDelegations: uniqueDelegates more than 2: {dao}: {i}, {sameTxnDvpcRows} \n")
            
            amounts = []
            for name, group in grouped:
                prev = group.iloc[0]["previousBalance"]
                new = group.iloc[-1]["newBalance"]
                amount = new - prev
        
                if amount > 0:
                    amounts.append(amount)
                    flag = 1 if delegator == name else 2
                    merged = appendRow(delegator, prev_del, name, amount, flag, ddict[delegator], blocktime, merged)
                    if name != new_del:
                        log_message(f"combineDelegations: delegate and new delegate do not match for {dao} at row {i} \n")
                
                if len(amounts) > 1:
                    log_message(f"combineDelegations: {uniqueDelegates} have positive amount for delegation at row {i} for {dao} \n") 

    # moving flag column to the end
    flags = merged.pop('Flag')
    merged = pd.concat([merged, flags], 1) 

    merged['DAO Name'] = dao 

    #save and make directory if it doesn't exist
    if not os.path.exists(f"./res/delegations"):
        os.makedirs(f"./res/delegations")
    
    #temp save before add ENS
    merged.to_csv(f"./res/delegations/{dao}_temp.csv", index=False)
    
    #print rows where flag is -1
    if len(merged.loc[merged['Flag'] == -1]) > 0:
        log_message(f"combineDelegations: Flag is -1 at {merged.loc[merged['Flag'] == -1]} for {dao} \n")
        
    return merged

def addENStoDelegations(merged, dao):

    daotemppath = f"./res/delegations/{dao}_temp.csv"

    # add ENS
    merged = handle_ens(merged, "Previous Delegate")
    merged.to_csv(f"./res/delegations/{dao}_temp.csv", index=False)

    merged = handle_ens(merged, "New Delegate")
    merged.to_csv(f"./res/delegations/{dao}_temp.csv", index=False)

    merged = handle_ens(merged, "Delegator")
    merged.to_csv(f"./res/delegations/{dao}_temp.csv", index=False)
    
    #move dao name to the front
    daoName = merged.pop('DAO Name')
    merged = pd.concat([daoName, merged], 1)

    #sort by Blocktime
    merged = merged.sort_values(by=['Blocktime'])
    merged.to_csv(f"./res/delegations/{dao}.csv", index=False)

    return merged

# function that finds rows with non empty values, gets the unique delegators

def appendRow(delegator, prev_del, new_del, amount, flag, delegates, blocktime, merged):
    row = {
                'Delegator': delegator,
                'New Delegate': new_del,
                'Previous Delegate': prev_del,
                'Amount': amount,
                'Flag': flag,
                'Delegates': delegates,
                'Blocktime': blocktime 
              }
    merged = merged.append(row, ignore_index=True)
    return merged

# helper function
def convertNP(df, cols, num=(10**18)):
    df[cols] = df[cols].astype(np.float64) / (10**18)
    return df 
