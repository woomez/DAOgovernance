import pandas as pd
import numpy as np
import os

def generate_ens(path, ens_map={}):
    """
    one time to handle queries
    """
    for root, _, files in os.walk(path):
        for file in files:
            if file[-4:] == ".csv":
                print(file)
                df = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
                cols_to_move= ['ENS', 'Voter Address']
                df = df[cols_to_move + [ col for col in df.columns if col not in cols_to_move]] 
                first_column = df.pop('DAO Name')
                df.insert(0, 'DAO Name', first_column)

                df.drop(df.filter(regex="Unname"),axis=1, inplace=True, errors='ignore')
                df.to_csv(f"./res/votes/new/{file}", index=False)



def mergeToOne(path):
    """
    TODO
    If final_onchain exists, load and add only the new.
    
    """
    dpath = path +"/votes"
    df = pd.DataFrame()

    for root, _, files in os.walk(dpath):
        for file in files:
            try:
                cdf = pd.read_csv(os.path.join(root, file), index_col=None, low_memory=False)
                df = pd.concat([cdf, df], ignore_index=True)

            except:
                pass
    # df['weight'] = df['weight'].div(10**18).round(5)
    # df['DAO Token Supply'] = df['DAO Token Supply'].div(10**18).round(5)
    df.to_csv("./onchain.csv")
    print("finished")

def sanity_check(df):
    max_val = df['Voter Power'].max()
    print(max_val)
    fixed_values = df['Voter Power'].apply(check_int).dropna()
    print(fixed_values)

def check_int(value):
    try:
        if value < 1:
            return np.NaN
    except ValueError:
        return value

df = pd.read_csv('./onchain.csv')
sanity_check(df)

