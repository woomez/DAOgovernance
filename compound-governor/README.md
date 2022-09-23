Project folder for generating subgraphs that are in Compound Governor formats
- Currently focused on pulling voting and delegation results

## TODO
how to get circulating tokens at the moment?

time sensitive:
tokenHolders at start of proposal

check whether compound works

In order to authenticate thegraph studio:
graph auth --studio 1859200c78e860873b66b52310138140

## Manual to deploy a new subgraph

- add slug in Studio as dao-governance
 
- Prepare token and governor address and start block 
    - add network in config
    - check whether the DAO uses OZ/Compound

- Init:
    - run: graph init --studio --protocol=ethereum --from-contract=${governor_contract} --contract-name=${DAOGovernor} --${dao-governance}
    - add token_contract, DAOToken
    * what: generates abi / generated folder inside dao-governance folder

- Add abi:
    * move abi and generated from dao-governance to current directory
    * write script to automate this

- prepare protocol folder
    - copy from empty-OZ-governance / empty-COMPOUND-governance
        - cp -a empty-OZ-governance dao-governance 
    - fill in template in config
        - template will be used as yaml for the query
            - :%s/"DAO"/{DAO in all caps}/gcI
            - :%s/"dao"/{lower case}/gcI
        - change name in the template from dao to lower case DAO name

- update src typescript files
    - rename into lower case DAO name
    - run same script as 4 to replace dao name

- prepare yaml
    - npm run prepare:yaml --protocol=silo-governance --template=silo-governance.template.yaml --network=ethereum

- build
    - npm run prepare:build
    
- if no problem, deploy
    - graph deploy --studio dao-governance

## ToDo:
    - script to run vim commands to auto change name from empty-governance folder
            
    - move relevant folders:
        - abis/${protocol}
        - generated
    
    - add delegation event
    
    - add quorum for Compound
    - default browser open
