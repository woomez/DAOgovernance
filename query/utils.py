import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
import datetime

"""
To Do:
    add way to export infura key
"""

def get_voters(params, result):
    print("generating voters table")
    voters = pd.json_normalize(result,record_path=["voters", "votes"], meta=[['voters', 'id']])
    cols_to_move = ['proposalID.id', 'voters.id']
    voters = voters[cols_to_move + [col for col in voters.columns if col not in cols_to_move]]
    voters = voters.rename(columns={"proposalID.id": "proposal", "voters.id": "voter"})
    voters['proposal'] = voters['proposal'].astype(int)
    voters['single_vote'] = np.array(voters['single_vote'], dtype=np.float64)
    voters['single_vote'] = voters['single_vote'] / 10**int(params)

    voters = voters.sort_values(by=['proposal'], ascending=True)
    return voters

def get_voting_rate(params, result):
    # return voting_rate
    proposals = result['proposals']
    proposals = pd.json_normalize(proposals)

    forvotes, againstvotes, vote_rate = [], [], []
    print(proposals)
    for index, proposal in proposals.iterrows():
        forvote = np.float64(proposal["forvotes"]) / 10**int(params)
        againstvote = np.float64(proposal['againstvotes']) / 10**int(params)
        forvotes.append(forvote)
        againstvotes.append(againstvote)
        vote_rate.append(forvote + againstvote)

    proposals['id'] = proposals['id'].astype(int)
    proposals = proposals.sort_values(by=['id'], ascending=True)
    proposals['blocktime'] = proposals['blocktime'].map(lambda time: datetime.datetime.fromtimestamp(int(time)))
    proposals['vote_rate'] = vote_rate
    proposals['forvotes'] = forvotes
    proposals['againstvotes'] = againstvotes
    return proposals

def add_ens(voters):
    ns = ENS.fromWeb3(w3)
    addresses = voters['voter'].unique()

    print("Number of unique addresses: ", len(addresses))
    voters['name'] = voters['voter']
    
    print('starting conversion...')
    for address in addresses:
        voters.loc[voters['voter'] == address, 'name'] = ns.name(address)
    
    return voters



