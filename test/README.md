ToDo:

1. npm init deploy sequence

ens-token: 0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72
ens-governor: 0x323A76393544d5ecca80cd6ef2A560C6a395b7E3

 "prepare:init": "graph init --studio --protocol=ethereum --from-contract=${npm_config_contract} --contract-name=${npm_config_protocol} ${npm_config_subgraph}",
 
 
pipeline
1. init:
    - priority: create slug
    - automate by reading from config
        - might need script (i.e. from deploy of messari)
        - to automate:
            - read from config
            - token address / governance address
            
    - extract relevant folders:
        - abis/${protocol}
        - generated

2. add to config @ ./protocols/${protocol}/config:
    1. networks - 
    2. templates

3. add ./protocols/${protocol}/src
    1. 

4. 

5. clean
    - remove irrelevant folders
    - replace yaml, add yaml from config
    - 
    
6. deploy
    - understand messari
