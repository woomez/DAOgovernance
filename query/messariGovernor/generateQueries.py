import os
import pandas as pd
from queryHandler import generate_results
from delegateHandler import combineDelegations, addENStoDelegations
import os
import argparse
from web3 import Web3
from dotenv import load_dotenv
import json
import pandas as pd
from utils import log_message
from tqdm import tqdm

votes = ["vote"]
delegations = ["delegateChanges", "delegatePowerChanges"]
_all = ["governances", "proposals", "delegateChanges", "delegatePowerChanges", "votedailysnapshots", "tokendailysnapshots", "votes", "delegates"]

parser = argparse.ArgumentParser(description='Query the Graph')
parser.add_argument('--mode', type=str, default='_all', help='Mode to run the script in (default: _all)')
parser.add_argument('--folder', type=str, default='openzepplinGovernor', help='Folder name to load the data from (default: openzepplinGovernor)')

mode_dict = {
    "votes": votes,
    "delegations": delegations,
    "_all": _all
}

args = parser.parse_args()
args.mode = mode_dict[args.mode]
folder_name = args.folder

infura_api_key = os.getenv('INFURA_API_KEY')
infura_url = f'https://mainnet.infura.io/v3/{infura_api_key}'
w3 = Web3(Web3.HTTPProvider(infura_url))

#Load DAOs 
with open(f'./messariGovernor/{folder_name}/dao.json', 'r') as f:
    dao = json.load(f)

#when testing urls
# dao = {
#         "Angle": {
#             "url": "https://api.thegraph.com/subgraphs/name/messari/angle-governance",
#             "token": "0x31429d1856aD1377A8A0079410B297e1a9e214c2",
#             "normalizer": "10^21",
#             "total_supply": "10^9",
#         },
#     }

if __name__ == "__main__":
    for name in dao.keys():
        print(f"Generating results for {name} \n")
        generate_results(name, dao[name], args.mode)

    #     if os.path.isfile(f'./res/delegations/{dao}.csv'):
    #         merged = pd.read_csv(f'./res/delegations/{dao}.csv')
    #         continue

    #     elif os.path.isfile(f'./res/delegations/{dao}_temp.csv'):
    #         print(f"\n found temp file for {dao}")
    #         merged = pd.read_csv(f'./res/delegations/{dao}_temp.csv')
    #     else: 
    #         try:
    #             merged = combineDelegations(dao);
    #         except Exception as e:
    #             print(f"Error combining delegations for {dao}")
    #             print(e)
    #             continue
                 
    #     merged = addENStoDelegations(merged, dao)
