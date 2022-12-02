import pandas as pd
import numpy as np
import os
import pickle


"""
TODO 
make ENS dict
update ENS Column
        - find Unique addresses
        - convert addresses to name
                - if address in dict:
                        - store name
                - else: look up, add to dict
        - from unique address, name pair, make new column ENS, for each address, if in unique address, store name
"""

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

dpath= "./res"
addGovParams(dpath)
