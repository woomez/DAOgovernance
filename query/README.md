export WEB3_INFURA_PROJECT_ID=d01265cbfef74bc2a7bf83a6ed7840e5

TODO:
    1. Find compound related DAOs
    2. Add Maker to CSV result
    3. Clean code (first)
        - add module for newly added DAOs
    4. Clean CSV
    5. Clean  Maker results
    6. argparse for generatequeries
    7. figure out total supply


    
    In the next hour and a half or so:
    - Clean utils
    - Understand what needs to be changed in the CSV
    - Finish Maker
    - Send email to Andy about results
    - get Raw data and convert into numpy results
        - i forget where this was tho...

    
Workflow:
    - generateQueries: 
        - takes in URLs and conversion methods
        - generates json files from the queries
    - traverse_tree:
        - traverse_tree and converts json into csv
    - combine:
        - combine individual votes
        - add gov, proposal params
        - merge into one
    
