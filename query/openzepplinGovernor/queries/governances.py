def governanceQuery(client, dao, _query):
    _governancesQuery = gql(
            """
                    {
                      governances {
                        id
                        totalTokenSupply
                        currentTokenHolders
                        totalTokenHolders
                        currentDelegates
                        totalDelegates
                        delegatedVotesRaw
                        delegatedVotes
                        proposals
                        proposalsQueued
                        proposalsExecuted
                        proposalsCanceled
                      }
                    }
            """)
    result = client.execute(_governancesQuery)
    result = pd.json_normalize(result[_query])
    save_as_csv(dao, _query, result)
