Project folder for DAO governance
- Deploy subgraph in Compound-Governor, make queries in Query

## TODO

* [ ] add delegation
    - delegate vote changed and delegate changed are two separate events
    - they only share the delegate address
    - cannot create an id for the entity to share the event
    - tried with block number, but seems like there are cases where the events are stored in different blocks
    - need to do unit testing to make sure
* [ ] update query methods - test with current json files to put it in desired format
* [ ] first send off results for OZ-governor, create json file for votes
* [ ] update on how to pull most recent data
* [ ] Crosscheck against Tally, Sybil
