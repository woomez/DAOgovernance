from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pandas as pd
import datetime
import os
os.makedirs('../csv/pooltogether', exist_ok=True)  
apikey = "f39064ae438b52795c630f3366501b6b"

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url = "https://gateway.thegraph.com/api/f39064ae438b52795c630f3366501b6b/subgraphs/id/HZmtsnmRWMKh532QbirX9ouAxUGrzSNtWUPK6nnM2bdL")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
   {
      proposals(first:1000) {
        id
        startBlock
        status
        votes {
          votes
        }
      }
      votes(first: 1000) {
        id
        support
        votes
        voter {
          id
        }
        proposal {
          id
        }
      }
    }
  
"""
)

# Execute the query on the transport
result = client.execute(query)

# Voter/proposal/support matrix 
pd.set_option('display.max_colwidth', None)
df_voters = pd.json_normalize(result,record_path=["votes", "vote"], meta=[['votes', 'id']])

print(df_voters)

cols_to_move = ['proposalID.id', 'voters.id']
df_voters = df_voters[ cols_to_move + [col for col in df_voters.columns if col not in cols_to_move ] ]
df_voters = df_voters.sort_values(by=['proposalID.id'], ascending=True)
df_voters.to_csv('./csv/compoundf.csv')

# Voting Rates
proposal_result = result['proposals']
df_voting_rates = pd.json_normalize(proposal_result, record_path=["votes"], meta=['startBlock', ['id']])

df_voting_rates['id'] = df_voting_rates['id'].astype(int)
df_voting_rates['votes'] = df_voting_rates['votes'].astype(float)
df_voting_rates = df_voting_rates.sort_values(by=['id'], ascending=True)
df_voting_rates = df_voting_rates.groupby(['id', 'startBlock']).sum().reset_index()
df_voting_rates = df_voting_rates.round({'votes': 5})
df_voting_rates['votes'] = df_voting_rates['votes']/10**7

print(df_voting_rates['startBlock'])
df_voting_rates['startBlock'] = df_voting_rates['startBlock'].map(lambda time: datetime.datetime.fromtimestamp(int(time)))

print(df_voting_rates)
df_voting_rates.to_csv('../csv/pooltogether/pooltogether_voting_rates.csv')
print(df_voting_rates)




