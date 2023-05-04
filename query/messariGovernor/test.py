import os
import pandas as pd
from queryHandler import generate_results
from delegateHandler import combineDelegations, addENStoDelegations, findMissingRows

new_urls = [('Angle', 'https://api.thegraph.com/subgraphs/name/messari/angle-governance')]

for url in new_urls:
    dao, api = url
    print('Generating results for', dao)

    if os.path.isfile(f'./res/delegations/{dao}.csv'):
        print(f"\n Found file for {dao}")
        merged = pd.read_csv(f'./res/delegations/{dao}.csv')

    elif os.path.isfile(f'./res/delegations/{dao}_temp.csv'):
        print(f"\n Found temp file for {dao}")
        merged = pd.read_csv(f'./res/delegations/{dao}_temp.csv')
    else: 
        try:
            merged = combineDelegations(dao);
        except Exception as e:
            print(f"Error combining delegations for {dao}")
            print(e)
            continue

             
    # merged = addENStoDelegations(merged, dao)
    numMissingRows = findMissingRows(dao)


# Create a dictionary to store delegates and their corresponding delegators
delegates = {}

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


def extract_info(row, delegates):
    from_address, to_address, previous_address, flag, delegates = extractDelegateChange(row['delegateChange'], delegates)

    amount_list, delegates = extractDVPC(row['delegateVotingPowerChange'], delegates)

    if len(amount_list) > 1 and flag == 1:
        print("Error: more than one delegateVotingPowerChange for txnHash: ", row['txnHash'])

    transfer_list = extractTransfer(row['transfer'], delegates)
    
    # if amount is positive and from/to address are already defined from extractTransfer, simply add the amount to the list

    # if from/to is not defined when going through amount_list, then need to get from/to addresses from transfer

    # need to merge amount_list and transfer_list
    # if flag == 0:
    #     # need to get from_address from transfer
    #     from_address = row['transfer'][0]['from']
    
    # for amount in amount_list:
    #     amount = extractTransfer(row['transfer'], to_address)

    return transfer_list, from_address, to_address, previous_address, amount_list, flag

# Create a dictionary to store delegates and their corresponding delegators
delegates = {}

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


def extract_info(row, delegates):
    from_address, to_address, previous_address, flag, delegates = extractDelegateChange(row['delegateChange'], delegates)

    amount_list, delegates = extractDVPC(row['delegateVotingPowerChange'], delegates)

    if len(amount_list) > 1 and flag == 1:
        print("Error: more than one delegateVotingPowerChange for txnHash: ", row['txnHash'])

    transfer_list = extractTransfer(row['transfer'], delegates)
    
    return transfer_list, from_address, to_address, previous_address, amount_list, flag




# Apply the extract_info function to the combined DataFrame
combined_df[['transfer', 'from', 'to', 'previous', 'amount', 'flag']] = combined_df.apply(lambda row: extract_info(row, delegates), axis=1, result_type='expand')

# Save the updated combined dataframe to a new CSV file
combined_df.to_csv('extracted.csv', index=False)