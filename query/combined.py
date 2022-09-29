import os
from query import make_query
from utils import get_voters, add_ens, get_voting_rate

os.makedirs('./csvs/voters', exist_ok=True)  
os.makedirs('./csvs/voting_rates', exist_ok=True)

with open('metadata.txt') as f:
    lines = f.readlines()
    metadata = [] 

    for line in lines:
        line = line.strip() 
        if line:
            metadata.append((item.strip() for item in line.split(',')))

# Generate voter data
for data in metadata:
    name, api, params = data
    
    print(f"Generating vote data for {name}...")
    result = make_query(api)
    voters = get_voters(params, result)
    voters = add_ens(voters)
    voters.to_csv(f"./csvs/voters/{name}_voters.csv")
    
    print(f"Generating voting rate for {name}...")
    proposals = get_voting_rate(params, result)
    proposals.to_csv(f"./csvs/voting_rates/{name}_voting_rates.csv")
