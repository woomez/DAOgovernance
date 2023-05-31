import pandas as pd
import numpy as np
import os
import pickle
from ens import ENS 
from web3 import Web3
from tqdm import tqdm
from dotenv import load_dotenv

import warnings
warnings.filterwarnings("ignore")

load_dotenv()
infura_api_key = os.getenv('INFURA_API_KEY')
infura_url = f'https://mainnet.infura.io/v3/{infura_api_key}'
w3 = Web3(Web3.HTTPProvider(infura_url))

ns = ENS.from_web3(w3)

def getUniqueDelegators(df, address, ENScol):
    
    mask = df[ENScol].isnull()
    delegators = df.loc[mask, address].unique() 
    return delegators

def handle_ens(df, address='voter.id'):
    if address == 'voter.id':
        ENScol = 'ENS'
    else: ENScol = address + ' ENS' 

    if ENScol not in df.columns:
        df.loc[:, ENScol] = pd.Series()

    # get unique delegators with null ens
    unique_addresses = getUniqueDelegators(df, address, ENScol) 

    with open('./ens_map.pickle', 'rb') as handle:
        ens_map = pickle.load(handle)
    print(len(unique_addresses), "to sort")
   
    look_up = [uniqueA for uniqueA in unique_addresses if uniqueA not in ens_map]
    print(len(look_up), "to look up")
    
    search_ens = True
    if len(look_up) != 0 and search_ens:
        for i, uniqueA in enumerate(tqdm(look_up)):
            if i != 0 and i % 500 == 0:
                print('saved at check point', i)
                with open('./ens_map.pickle', 'wb') as handle:
                    pickle.dump(ens_map, handle)
            if uniqueA not in ens_map:
                try:
                    ENS_name = ns.name(uniqueA)
                    ens_map[uniqueA] = ENS_name
                    pass
                except Exception as Error:
                    print(f"\n Error raised in {uniqueA}:\n", Error)
                    continue

    with open('./ens_map.pickle', 'wb') as handle:
        pickle.dump(ens_map, handle) 
   
    print('ens_map saved \n')
    # add column in df called address + ENS and store ens_map[uniqueA]
    df.loc[:, ENScol] = df[address].map(ens_map)   
    df[ENScol] = df[ENScol].astype(str)

    # place the new column next to the address column
    cols = list(df.columns.values)
    cols.pop(cols.index(address))
    cols.pop(cols.index(ENScol))
    df = df[[address, ENScol] + cols]
    return df

def get_block_timestamp(block_num):
    infura_url = 'https://mainnet.infura.io/v3/d01265cbfef74bc2a7bf83a6ed7840e5'
    if block_num == 0:
        return

    web3 = Web3(Web3.HTTPProvider(infura_url))
    """Get Ethereum block timestamp"""
    try:
        block_info = web3.eth.getBlock(block_num)
    except BlockNotFound:
        return None
    last_time = block_info["timestamp"]
    return last_time

def generate_ens(path, ens_map={}):
    """
    Retrieves all ENS ids from current CSV and stores in a dict, which is saved to a pickle
    """
    for root, _, files in os.walk(path):
        for file in files:
            print(file)
            df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
            unique_addresses = df['Voter Address'].unique()
            df['ENS'].fillna('nan', inplace=True)
            for address in unique_addresses:
                if address in ens_map:
                    continue
                ENS = df[df['Voter Address']==address]['ENS'].values[0]
                if ENS != 'nan':
                    ens_map[address] = ENS

    # Save
    with open('ens_map.pickle', 'wb') as handle:
        pickle.dump(ens_map, handle, protocol=pickle.HIGHEST_PROTOCOL)


def addGovParams(path):

    """TODO
    later, get token supply from daily snapshot, update accordingly
    """
    missing = []
    vote_path = path+"/votes/"
    gov_path = path+"/governances/"
    for root, _, files in os.walk(gov_path):
        for file in files:
            dao = file[:-4]
            gov_df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
            
            try:
                df = pd.read_csv(vote_path+file, index_col=None, low_memory=False)
                total_supply = gov_df['totalTokenSupply'].astype(np.float64)
                if total_supply[0] == 0:
                    print(dao, "has 0 total_supply.")
                    supply = fetchGovParams(dao)
                    if supply != 0:
                        gov_df['totalTokenSupply'] = supply
                        gov_df.to_csv(gov_path+file, index=False)
                    else:
                       missing.append(dao) 

                else: 
                    supply = total_supply[0]

                df['DAO Token Supply'] = supply
                df['Voter Power'] = df['Weight'].div(df['DAO Token Supply'], axis=0)
                df['Voter Power'] = df['Voter Power'].round(10)
                df.to_csv(vote_path+file, index=False)

            except:
                print(f"Gov file does not exist for {file}")
                pass
    
    print(missing)
    
def fetchGovParams(daoname):
    with open('./messariGovernor/supply.txt') as f:
        for line in f:
            line = line.strip().split(" ")
            if line[0] == daoname:
                return np.float64(line[1])*(10**18)

        return 0

def log_message(message, log_file="output.log"):
    print("logging \n")
    with open(log_file, "a") as file:
        file.write(message + "\n")
