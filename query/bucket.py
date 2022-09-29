import pandas as pd
import numpy as np
import os

"""
Used to generate time buckets
"""

daos = ['Nouns', 'Compound', 'Gitcoin', 'Uniswap', 'PoolTogether']

os.makedirs('./csvs/buckets', exist_ok=True)

def get_buckets(df):
    res = [] 
    df['blocktime'] = pd.to_datetime(df['blocktime'])
    last = df.iloc[-1].blocktime
    start_date = pd.to_datetime("2022-01-01 00:00:00")
    end_date = pd.to_datetime("2022-01-31 00:00:00")

    while start_date < last:
        mask = (df['blocktime'] > start_date) & (df['blocktime'] <= end_date)
        a = df.loc[mask]
        voting_rate = a['vote_rate'].mean()
        total_cap = a['total_cap'].mean()
        circulating_cap = a['circulating'].mean()
        total_voting_rate = voting_rate / total_cap
        circulating_voting_rate = voting_rate / circulating_cap
        """
         - make list with (start_date.date, end.date), voting_rate, for, against, 
        """
        res.append([start_date.date().strftime("%Y%m%d") +"-" + end_date.date().strftime("%Y%m%d"), total_voting_rate, circulating_voting_rate, voting_rate]) 
        start_date += pd.DateOffset(30)
        end_date += pd.DateOffset(30)

    res = pd.DataFrame(np.array(res, dtype=object))
    res.columns = ["Date", "Rate/total", "Rate/circulating", "Total tokens"]

    return res 

for dao in daos:
    ratepath = f"./csvs/voting_rates/{dao}_voting_rates.csv"
    print(f"Starting {dao}")
    df = pd.read_csv(ratepath)
    res = get_buckets(df)
    res.to_csv(f'./csvs/buckets/{dao}_buckets.csv')




