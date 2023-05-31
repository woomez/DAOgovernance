from gql import gql
from utils import handle_ens
import numpy as np
import pandas as pd
import os

"""
Read proposal blocks from csv and query for delegates for those blocks
"""

def delegatesQuery(client, dao, values, _query):

    # read csv if file exists else exit with error
    if not os.path.exists(f"./res/vote/{dao}.csv"):
        print(f"Could not find vote csv for {dao}")
        return

    vote_df = pd.read_csv(f"./res/vote/{dao}.csv", index_col=None)

    proposal_blocks = vote_df['Proposal Date End'].unique().tolist()
    proposal_blocks.sort()

    _delegateQuery = gql("""
            query getDelegates($blockNumber: Int!) {
                delegates(block: {number: $blockNumber}) {
                delegatedVotes
                id
                tokenHoldersRepresented {
                    id
                    tokenBalance
                    totalTokensHeld
                }
                }
            }
            """)

    rows = []

    try:
        df = pd.read_csv(f"./res/delegates/{dao}.csv", index_col=None)
        # get last block from df
        last_block = df["Block"].iloc[-1]
        # blocks to query are blocks after last block 
        blocks_to_query = proposal_blocks[proposal_blocks.index(last_block)+1:]

    except:
        print(f"Could not find CSV for {dao}")
        df = pd.DataFrame()
        blocks_to_query = proposal_blocks

    for block in blocks_to_query:
        params = {"blockNumber": int(block)}
        curr = client.execute(_delegateQuery, variable_values=params)

        delegates = curr["delegates"]

        for delegate in delegates:
            delegate_id = delegate['id']
            delegated_votes = delegate['delegatedVotes']
            
            for token_holder in delegate['tokenHoldersRepresented']:
                row = {
                    'Block': block,
                    'Delegate': delegate_id,
                    'Delegated Votes': delegated_votes,
                    'Delegator': token_holder['id'],
                    'Delegation Amount': token_holder['tokenBalance'],
                    'Delegator Total': token_holder['totalTokensHeld']
                }
                rows.append(row)

    # append rows to df
    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    
    # sort by block
    df = df.sort_values(by=["Block"])
    df.to_csv(f'./res/delegates/{dao}_temp.csv', index=False)

    df = handle_ens(df, "Delegate")
    df.to_csv(f"./res/delegates/{dao}_temp.csv", index=False)

    df = handle_ens(df, "Delegator")
    df.to_csv(f"./res/delegates/{dao}_temp.csv", index=False)

    print(f"Finished querying delegates for {dao}\n")

    # delete temp file
    os.remove(f"./res/delegates/{dao}_temp.csv")

    df['DAO Name'] = str(dao)
    # Create a list of columns in the desired order
    cols = ['DAO Name', 'Block'] + [col for col in df.columns if col not in ['DAO Name', 'Block']]

    # Reindex your dataframe using this new order
    df = df.reindex(columns=cols)

    df.to_csv(f"./res/delegates/{dao}.csv", index=False)

    return df

        
