ToDo:
do a test-run with Nouns using the manual

ens-token: 0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72
ens-governor: 0x323A76393544d5ecca80cd6ef2A560C6a395b7E3


"init": "graph init --studio --protocol=ethereum --from-contract=${npm_config_contract} --contract-name=${npm_config_governor} ${npm_config_subgraph}"

npm run init --subgraph=${DAO name in lower case}-governance
governor format: ${DAO name all caps}Governor
token format: ${DAO name all caps}Token

graph auth with my token from TheGraph Studio

1. prepare token and governor address and start block - add to network in config

2. init:
    * what: generates abi / generated folder inside dao-governance folder
    - Create slug in dao-governance
    - is there a way to create from command line?

3. add abi:
    * move abi and generated

4. prepare protocol folder
    - copy from empty-governance
    - fill in template in config
        - template will be used as yaml for the query
            - :%s/"DAO"/{DAO in all caps}/gcI
            - :%s/"dao"/{lower case}/gcI
        - change name in the template from dao to lower case DAO name

5. update src typescript files
    - rename into lower case DAO name
    - run same script as 4 to replace dao name
    - 

6. clean
    - remove irrelevant folders
    - replace yaml, add yaml from config
    - 
    
7. deploy
    - understand messari

### ToDo:
    - script to run vim commands to auto change name from empty-governance folder
            
    - move relevant folders:
        - abis/${protocol}
        - generated
    
    - add delegation event
