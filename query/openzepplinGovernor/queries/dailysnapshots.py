def votedailysnapshotQuery(client, dao, _query):

    _votedailysnapshotQuery = gql(  """
              query($lastID: ID) {
                  voteDailySnapshots (first:1000, where: {id_gt: $lastID}) {
                        id
                        proposal{
                            id
                        }
                        forWeightedVotes
                        againstWeightedVotes
                        totalWeightedVotes
                        timestamp
                        blockNumber
                      }
                    }       """)


    params = {
                "lastID": ""
        }
    

    loadmore = True
    counter = 1
    length = 0

    while loadmore:
        
        curr = client.execute(_votedailysnapshotQuery, variable_values=params)
        length += len(curr['voteDailySnapshots'])
        
        if len(curr['voteDailySnapshots']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['voteDailySnapshots'][-1]['id']
            

            save_query_as_json(dao, _query, counter, curr)
            counter += 1

        gc.collect()
    print(_query, length)

def tokendailysnapshotQuery(client, dao, _query):

    _tokendailysnapshotQuery = gql(  """
              query($lastID: ID) {
                  tokenDailySnapshots (first:1000, where: {id_gt: $lastID}) {
                        id
                        totalSupply
                        tokenHolders
                        delegates
                        delegations
                        timestamp
                        blockNumber
                      }
                    }       """)


    params = {
                "lastID": ""
        }
    

    loadmore = True
    counter = 1
    length = 0

    while loadmore:
        
        curr = client.execute(_tokendailysnapshotQuery, variable_values=params)
        length += len(curr['tokenDailySnapshots'])
        
        if len(curr['tokenDailySnapshots']) == 0:
            loadmore = False
        
        else:
            # update params
            params["lastID"] = curr['tokenDailySnapshots'][-1]['id']
            

            save_query_as_json(dao, _query, counter, curr)
            counter += 1
        
        gc.collect()
    print(_query, length)
