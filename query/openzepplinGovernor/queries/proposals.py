def proposalQuery(client, dao, _query):
    _proposalQuery = gql(  """
              {
                  proposals{
                    id
                    description
                    proposer{
                        id
                    }
                    state
                    quorumVotes
                    tokenHoldersAtStart
                    delegatesAtStart
                    againstDelegateVotes
                    forDelegateVotes
                    abstainDelegateVotes
                    totalDelegateVotes
                    againstWeightedVotes
                    forWeightedVotes
                    abstainWeightedVotes
                    totalWeightedVotes
                    creationBlock
                    votes{
                      choice
                      weight
                      voter{
                        id
                      }
                    }
                    startBlock
                    endBlock
                  }
                }
       """)

    result = client.execute(_proposalQuery)
    save_query_as_json(dao, _query, 0, result)
