import os
import argparse
from web3 import Web3
from dotenv import load_dotenv
import json
import pandas as pd
from utils import log_message
from tqdm import tqdm

load_dotenv()

parser = argparse.ArgumentParser(description='')
parser.add_argument('--folder', type=str, default='openzepplinGovernor', help='Folder name to load the data from (default: openzepplinGovernor)')

args = parser.parse_args()
folder_name = args.folder

infura_api_key = os.getenv('INFURA_API_KEY')
infura_url = f'https://mainnet.infura.io/v3/{infura_api_key}'
w3 = Web3(Web3.HTTPProvider(infura_url)) 

# Replace with the transaction hash you're interested in
with open(f'./messariGovernor/{folder_name}/dao.json', 'r') as f:
    dao = json.load(f)

if not os.path.exists('./res/transfer'):
    os.makedirs('./res/transfer')

for name in dao.keys():
    if name=="Reflexer":
        continue
    #load abi
    with open(f"./messariGovernor/{folder_name}/abis/{name}/{name}.json", "r") as abi_file:
        token_abi = json.load(abi_file)

    # create df to store results
    results = pd.DataFrame(columns=['txnHash', 'from', 'to', 'value'])
    values = dao[name]
    token_address = Web3.to_checksum_address(values['token'])
    # load delegation csv if there is one
    delegation_path = f'./res/delegateVotingPowerChanges/{name}.csv'

    if os.path.exists(delegation_path):
        df = pd.read_csv(delegation_path)
        print(f"\nLoaded {len(df)} rows from {delegation_path}")
    else: #stop loop
        continue

    # if transfer csv exist, load it and fetch the last txnHash
    if os.path.exists(f'./res/transfer/{name}.csv'):
        results = pd.read_csv(f'./res/transfer/{name}.csv')
        last_txnHash = results['txnHash'].iloc[-1]
        # look up last_txnHash in df and slice df to start from there
        last_txnHash_index = df[df['txnHash'] == last_txnHash].index[0]
        df = df.iloc[last_txnHash_index+1:]
    
    print(f'Processing {name} with {len(df)} txns to process \n')
    print(f'Last txnHash: {last_txnHash} \n')
    print(f'Length of current transfers: {len(results)} \n')
    txn_hash = df['txnHash'].to_list()

    for i, txn in tqdm(enumerate(txn_hash), total=len(df), bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
        if i!= 0 and i % 100 == 0:
            results.to_csv(f'./res/transfer/{name}.csv', index=False)
        # Get the transaction receipt for the transaction
        tx_receipt= w3.eth.get_transaction_receipt(txn)

        # Check if the transaction receipt is valid
        if tx_receipt is None:
            log_message(f"Invalid transaction hash for {name} at index {i}, txn: {txn}\n", "./logs/transfer.log")
        else:
            # Create a contract object for the ERC20 token
            contract = w3.eth.contract(address=token_address, abi=token_abi)
            logs = contract.events.Transfer().process_receipt(tx_receipt)
            if len(logs) != 0:
                logs=logs[0]

                # Extract values from the AttributeDict
                txn_hash = logs['transactionHash'].hex()
                _from = logs['args']['from']
                _to = logs['args']['to']
                try:
                    _value = logs['args']['amount']
                except: 
                    _value = logs['args']['value']

                # Create a new row dictionary
                new_row = pd.DataFrame([{'txnHash': txn_hash, 'from': _from, 'to': _to, 'value': _value}])

                # Append the new row to the results DataFrame
                results = pd.concat([results, new_row], ignore_index=True)
    
    # create path if not exist
    results.to_csv(f'./res/transfer/{name}.csv', index=False)
            