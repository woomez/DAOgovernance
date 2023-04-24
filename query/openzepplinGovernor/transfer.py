import os
from web3 import Web3
from dotenv import load_dotenv
import json
import pandas as pd
from utils import log_message
from tqdm import tqdm

load_dotenv()

with open("./openzepplinGovernor/abis/transfer.json", "r") as abi_file:
    token_abi = json.load(abi_file)

infura_api_key = os.getenv('INFURA_API_KEY')
infura_url = f'https://mainnet.infura.io/v3/{infura_api_key}'
w3 = Web3(Web3.HTTPProvider(infura_url)) 

# Replace with the transaction hash you're interested in
with open('./openzepplinGovernor/dao.json', 'r') as f:
    dao = json.load(f)

if not os.path.exists('./res/transfer'):
    os.makedirs('./res/transfer')

for name in dao.keys():

    # create df to store results
    results = pd.DataFrame(columns=['txnHash', 'from', 'to', 'value'])
    print(name)
    values = dao[name]
    token_address = Web3.to_checksum_address(values['token'])
    # load delegation csv
    df = pd.read_csv(f'./res/delegateVotingPowerChanges/{name}.csv')
    print(f'{name} size: {len(df)}')
    # if transfer csv exist, load it and fetch the last txnHash
    if os.path.exists(f'./res/transfer/{name}.csv'):
        results = pd.read_csv(f'./res/transfer/{name}.csv')
        last_txnHash = results['txnHash'].iloc[-1]
        # locate the last txnHash in df and update df to start from the next txnHash
        df = df.loc[df['txnHash'] == last_txnHash].iloc[1:]
 

    txn_hash = df['txnHash'].to_list()

    for i, txn in tqdm(enumerate(txn_hash)):
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
                _value = logs['args']['value']

                # Create a new row dictionary
                new_row = pd.DataFrame([{'txnHash': txn_hash, 'from': _from, 'to': _to, 'value': _value}])
                print(new_row)

                # Append the new row to the results DataFrame
                results = pd.concat([results, new_row], ignore_index=True)
    
    # create path if not exist
    results.to_csv(f'./res/transfer/{name}.csv', index=False)
            