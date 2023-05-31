# combines delegation with vote files
import pandas as pd
import os 
import json
from web3 import Web3
from copy import deepcopy

"""
Deprecated, just use extract_block_number
"""

def extract_block_number(delegation_df):
    # If 'delegateVotingPowerChange' is already a list, no need to parse it
    if isinstance(delegation_df['delegateVotingPowerChange'].iloc[0], list):
        delegation_df['blockNumber'] = delegation_df['delegateVotingPowerChange'].apply(lambda x: min([item['blockNumber'] for item in x]) if x else None)
    else:    
        # Convert delegateVotingPowerChange to list of dictionaries
        delegation_df['delegateVotingPowerChange'] = delegation_df['delegateVotingPowerChange'].apply(lambda x: json.loads(x.replace("\'", "\"")) if pd.notnull(x) else [])
        # Extract smallest block number and add as a new column
        delegation_df['blockNumber'] = delegation_df['delegateVotingPowerChange'].apply(lambda x: min([item['blockNumber'] for item in x]) if x else None)

    # If 'delegateChange' is already a list, no need to parse it
    if isinstance(delegation_df['delegateChange'].iloc[0], list):
        delegation_df['blockNumber'] = delegation_df['blockNumber'].fillna(delegation_df['delegateChange'].apply(lambda x: min([item['blockNumber'] for item in x]) if x else None))
    else:
        # Convert delegateChange to list of dictionaries
        delegation_df['delegateChange'] = delegation_df['delegateChange'].apply(lambda x: json.loads(x.replace("\'", "\"")) if pd.notnull(x) else [])
        # Extract smallest block number and add as a new column if blockNumber is still None
        delegation_df['blockNumber'] = delegation_df['blockNumber'].fillna(delegation_df['delegateChange'].apply(lambda x: min([item['blockNumber'] for item in x]) if x else None))
    
    #sort delegation_df by blockNumber
    delegation_df = delegation_df.sort_values("blockNumber")
    delegation_df.to_csv(f'./res/combined/DAO_test.csv', index=False)

    return delegation_df

def loadVoteDelegation(DAO):
    DELEGATION_PATH = f'./res/combined/{DAO}.csv'
    VOTE_PATH = f'./res/vote/{DAO}.csv'

    if os.path.exists(DELEGATION_PATH):
        delegation_df = pd.read_csv(DELEGATION_PATH)
    else:
        print("Delegation file not found")
        return None, None

    if os.path.exists(VOTE_PATH):
        vote_df = pd.read_csv(VOTE_PATH)
    else:
        print("Vote file not found")
        return None, None  

    print(f"Successfully loaded {DAO} with {len(delegation_df)} delegation rows and {len(vote_df)} votes")

    vote_df = vote_df.sort_values("block")
    delegation_df = extract_block_number(delegation_df)

    return vote_df, delegation_df

vote_df, delegation_df = loadVoteDelegation("Angle")

if vote_df is None or delegation_df is None:
    print("Error loading files")
    exit()

proposal_blocks = vote_df['Proposal Date End'].unique().tolist()

vote_df["Delegated Votes History"] = [{} for i in range(len(vote_df))]

# initialize balance dictionary
balances = {}

# Precompute the delegates
block_balance = {}

last_proposal_block = 0
for idx, row in delegation_df.iterrows():

    block = row['blockNumber']

    # Ensure delegateChange and transfer columns are parsed as lists/dictionaries
    delegate_changes = row['delegateChange']
    if isinstance(delegate_changes, str):
        delegate_changes = json.loads(delegate_changes.replace("\'", "\""))
    
    transfers = row['transfer']
    if isinstance(transfers, str):
        transfers = json.loads(transfers.replace("\'", "\""))
        
    voting_power_changes = row['delegateVotingPowerChange']
    if isinstance(voting_power_changes, str):
        voting_power_changes = json.loads(voting_power_changes.replace("\'", "\""))

    curr_delegates = {}

    # handle delegate changes
    if len(delegate_changes) > 1:
        print(f"Row with more than one delegate change {row['delegateChange']}")

    for change in delegate_changes:
        delegate = Web3.to_checksum_address(change['delegate'])
        delegator = Web3.to_checksum_address(change['delegator'])
        curr_delegates[delegate] = delegator

        if delegate not in balances:
            balances.setdefault(delegate, {'non-delegator': 0})
        if delegator not in balances[delegate]:
            balances[delegate][delegator] = 0
    
    if len(curr_delegates) > 1:
        print("More than 1 delegate change event: ", curr_delegates)
    
    # handle voting power changes
    for change in voting_power_changes:
        delegator = None
        delegate = Web3.to_checksum_address(change['delegate'])
        new_balance = int(change['newBalance'])
        prev_balance = int(change['previousBalance'])
        balance_change = new_balance - prev_balance

        if delegate in curr_delegates:
            delegator = curr_delegates[delegate]
        
        if delegate not in balances:
            print("NOT IN BALANCES", delegate)
            exit()
            continue

        if delegator and len(transfers) == 0:
            balances[delegate][delegator] += balance_change

        if not delegator or len(transfers) > 0:
            # handle transfers
            for change in transfers:
                from_address = Web3.to_checksum_address(change['from'])
                to_address = Web3.to_checksum_address(change['to'])
                value = int(change['value'])
                # check if either address is a delegate, and update the balance of the specific delegator
                if from_address in balances[delegate]:
                    if to_address != delegate:
                        print("from_address in balances[delegate]")
                        print(change)
                    # balances[from_address][to_address] -= value
                    #     else:
                #         balances[from_address]["non-delegator"] -= value
                if to_address == delegate:
                    if from_address in balances[to_address]:
                        balances[to_address][from_address] += value
                    else:
                        balances[to_address]["non-delegator"] += value
                    
        
    if len(voting_power_changes) == 0 and len(transfers) > 1:
        print("No voting power changes but transfers: ", transfers)
    
    if proposal_blocks and block > proposal_blocks[last_proposal_block]:
        block_balance[proposal_blocks[last_proposal_block]] = deepcopy(balances)
        # Increment last_proposal_block to point to the next element of proposal_blocks
        last_proposal_block += 1
        if last_proposal_block >= len(proposal_blocks):
            break

#save block_balance as json
with open(f'./res/block_balance.json', 'w') as f:
    json.dump(block_balance, f)


# vote_df.to_csv(f'./res/final/{DAO}.csv', index=False)