from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pickle
import pandas as pd
from flatten_json import flatten

apikey = "f39064ae438b52795c630f3366501b6b"

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url = "https://gateway.thegraph.com/api/f39064ae438b52795c630f3366501b6b/subgraphs/id/EiRmckRKCFMN3hmych8LsefFvGei2ucF86Ka84HX1Jy6")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
    {
      voterRegistries(first: 5) {
        id
        coldAddress
        hotAddress
        voteProxies {
          id
        }
      }
      voteProxies(first: 5) {
        id
        locked
        owner {
          id
        }
        votedSlate {
          id
        }
      }
    }    
"""
)

# Execute the query on the transport
result = client.execute(query)

print(result)
# for voter in voters:
#     n_voter = pd.json_normalize(voter['votes'])
#     print(n_voter)
#     print(n_voter.sort_values("proposalID.id"))
#     break
pd.set_option('display.max_colwidth', None)
df_voters = pd.json_normalize(result,record_path=["voters", "votes"], meta=[['voters', 'id']])
print(df_voters.sort_values('voters.id'))

with open('compound_matrix.pickle', 'wb') as f:
    pickle.dump(df_voters, f)
