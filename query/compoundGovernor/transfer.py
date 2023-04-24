import os
from web3 import Web3
from dotenv import load_dotenv
import json
import pandas as pd
from utils import log_message

load_dotenv()

with open("./compoundGovernor/abis/transfer.json", "r") as abi_file:
    token_abi = json.load(abi_file)

infura_api_key = os.getenv('INFURA_API_KEY')
infura_url = f'https://mainnet.infura.io/v3/{infura_api_key}'
w3 = Web3(Web3.HTTPProvider(infura_url)) 

print(w3.is_connected())

# Replace with the transaction hash you're interested in
with open('./compoundGovernor/dao.json', 'r') as f:
    dao = json.load(f)


for name in dao.keys():
    # create df to store results
    results = pd.DataFrame(columns=['txnHash', 'from', 'to', 'value'])
    print(name)
    values = dao[name]
    token_address = values['token']
    # load delegation csv
    df = pd.read_csv(f'./res/delegateVotingPowerChanges/{name}.csv')
    print(f'{name} size: {len(df)}')

    txn_hash = df['txnHash'].tolist()

    for i, txn in enumerate(txn_hash):
        # Get the transaction receipt for the transaction
        tx_receipt= w3.eth.get_transaction_receipt(txn)

        # Check if the transaction receipt is valid
        if tx_receipt is None:
            print("Invalid transaction hash")
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
    if not os.path.exists('./res/transfer'):
        os.makedirs('./res/transfer')
    results.to_csv(f'./res/transfer/{name}.csv', index=False)
            