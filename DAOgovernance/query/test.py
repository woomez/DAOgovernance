import pandas as pd
import numpy as np
df = pd.read_csv (r'./csvs/voters/Compound_voters.csv')

df['single_vote'] = np.array(df['single_vote'], dtype=np.float64)
df['single_vote'] = df['single_vote'] / 10**18
print (np.mean(df['single_vote'])/10**7)


"""
    {
        proposals{
            id
            blocktime
            forvotes
            againstvotes
        }
        singleVotes {
            id
            voter {
              id
            }
            single_vote
            proposalID {
              id
            }
            support
        }
        voters(first: 1000) {
            id
            votes{
                proposalID{
                    id
                }
                support
                single_vote
            }
        }
        implementations{
            id
            blocktime
            newImplementation
        }
    } 
    """
