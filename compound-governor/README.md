Project folder for generating subgraphs that are in Compound Governor formats

## TODO

check messari /
separate oz and compound

look into delegations;
Nouns
Aave
Gitcoin

In order to authenticate thegraph studio:
graph auth --studio 1859200c78e860873b66b52310138140

## Manual to deploy a new subgraph

- add slug in Studio as dao-governance

- Prepare token and governor address and start block
  - add network in config
  - check whether the DAO uses OZ/Compound

- Init:
  
  - run: graph init --studio 
  - add token_contract, DAOToken

  * what: generates abi / generated folder inside dao-governance folder

- Add abi:

  - npm run move-abi --protocol=DAO-governance

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

  - npm run prepare:yaml --protocol=DAO-governance

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
