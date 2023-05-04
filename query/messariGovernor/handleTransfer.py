import pandas as pd
import numpy as np
from decimal import Decimal
from web3 import Web3
from utils import log_message

def checkDCCount(dc):
    delegate_change_grouped = dc.groupby('txnHash').size()

    # Get the txnHash values where the row count is greater than 1
    txn_hashes = delegate_change_grouped[delegate_change_grouped > 1].index

    # Filter the rows in the original delegateChange DataFrame based on the selected txnHash values
    rows = dc[dc['txnHash'].isin(txn_hashes)]

    return rows, len(txn_hashes)

def checkDelegateCountInDVPC(dvpc):
    """
    check the number of unique delegates for each txnHash
    Ideally, all delegateVotingPowerChanges should have at most 2 unique delegates
    """
    # Group by 'txnHash' and count the number of unique delegates for each group
    unique_delegate_count = dvpc.groupby('txnHash')['delegate'].nunique()

    # Get the txnHash values where the unique delegate count is greater than 2
    txnHash = unique_delegate_count[unique_delegate_count > 2].index

    # Display the filtered rows
    return txnHash, len(txnHash)



# Define a function to concatenate rows as a list of dictionaries
def concat_rows(df, txn_hash, columns):
    rows = df[df['txnHash'] == txn_hash]
    return [row[columns].to_dict() for _, row in rows.iterrows()]

def addDelegates(delegates, from_address, to_address):
    if from_address not in delegates:
        delegates[from_address] = [to_address]
    elif to_address not in delegates[from_address]:
        delegates[from_address].append(to_address)
    return delegates

def extractDelegateChange(delegate_change, delegates):
    if delegate_change:
        from_address = Web3.to_checksum_address(delegate_change[0]['delegator'])
        to_address = Web3.to_checksum_address(delegate_change[0]['delegate'])
        previous_address = Web3.to_checksum_address(delegate_change[0]['previousDelegate'])
        addDelegates(delegates, from_address, to_address)      
        return from_address, to_address, previous_address, 1, delegates

    return None, None, None, 0, delegates

def extractDVPC(dvpc, delegates):
    net_balance_changes = {}

    if dvpc:
        for change in dvpc:
            delegate = Web3.to_checksum_address(change['delegate'])
            if delegate in delegates:
                net_balance = Decimal(change['newBalance']) - Decimal(change['previousBalance'])
                net_balance_changes[delegate] = net_balance_changes.get(delegate, 0) + net_balance

    return net_balance_changes, delegates

def extractTransfer(transfer, delegates):
    balance_changes = {}
    if transfer:
        for trx in transfer:
            to_address = Web3.to_checksum_address(trx['to'])
            from_address = Web3.to_checksum_address(trx['from'])
            if to_address in delegates:
                print('to_address in delegates')
            if from_address in delegates:
                print('from_address in delegates')
            if to_address in delegates or from_address in delegates:
                amount = Decimal(trx['value'])
                if to_address not in balance_changes:
                    balance_changes[to_address] = []
            
                balance_changes[to_address].append([from_address, amount])
                # print(balance_changes[to_address])
            
    return balance_changes

def handleTransfer(dao):
    log_message(f"Handling transfer for {dao}", "./logs/transfer.log")
    # Load Angle csv from ./res/delegateVotingPowerChanges/Angle.csv
    dvpc = pd.read_csv(f"./res/delegateVotingPowerChanges/{dao}.csv", index_col=None)
    dc = pd.read_csv(f"./res/delegateChanges/{dao}.csv", index_col=None)
    transfer = pd.read_csv(f"./res/transfer/{dao}.csv", index_col=None)

    # Merge the dataframes based on the 'txnHash' column    
    combined_df = pd.concat([dvpc[['txnHash']], dc[['txnHash']]]).drop_duplicates().reset_index(drop=True)

    txnHashes, count = checkDCCount(dc)
    log_message(f"Number of delegate changes {count} \n {txnHashes}", "./logs/transfer.log")

    txnHashes, count = checkDelegateCountInDVPC(dvpc)
    log_message(f"Number of rows where delegates are greater than 2 in dvpc: {count}\n {txnHashes}", "./logs/transfer.log")

    # Add new columns with concatenated information from the original DataFrames, specify columns to be included
    dc_rows = ['delegate', 'delegator', 'previousDelegate']
    dvpc_rows = ['delegate', 'previousBalance', 'newBalance']
    transfer_rows = ['from', 'to', 'value']

    combined_df['delegateChange'] = combined_df['txnHash'].apply(lambda x: concat_rows(dc, x, dc_rows))
    combined_df['delegateVotingPowerChange'] = combined_df['txnHash'].apply(lambda x: concat_rows(dvpc, x, dvpc_rows))
    combined_df['transfer'] = combined_df['txnHash'].apply(lambda x: concat_rows(transfer, x, transfer_rows))

    # Save the combined dataframe to a new CSV file
    combined_df.to_csv(f'./res/combined/{dao}.csv', index=False)

handleTransfer('Angle')
