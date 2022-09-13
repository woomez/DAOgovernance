from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

def make_query(api):
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=api)
    
    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql(
    """
    {
        proposals(first: 1000) {
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
        voters(first: 1000, skip: 0) {
            id
            votes{
                proposalID{
                    id
                }
                support
                single_vote
            }
        }
    } 
    """

            )

    # Execute the query on  he transport
    result = client.execute(query)
    return result

