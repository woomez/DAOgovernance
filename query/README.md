To run files:
circulating token supply = enterprise model

ask gpt for higher level structure of directory
to get the circulating supply, have to find the addresses of non circulating tokens

## TODO

- [ ] circulating supply at block

  - coingecko enterprise model

- [ ] Delegations
  - [ ] Identify delegation changed
  - for all delegation changed transcation hashes, use txnHash to locate
  - [ ] Once there is a delegation edge, keep track of delegator's token balance
    - [ ] Delegator's token balance can be updated via transfer

Q. What is the case such that there are no corresponding delegate vote changes?
A. The delegator re-delegated to the same delegate, hence no change in votes changed

Q. Why would there be so many of such instances?
A. Esp. towards the end, recheck

format nouns and maker to have same columns - find missing pieces

TODO:

    1. check for new graphs
    1. argparse for generatequeries
    2. automatic pagination --> apollo graphql
    3. for now, use blocks as parameters
    5. check the aave query if they can generate delegations
