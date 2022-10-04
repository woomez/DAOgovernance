import pandas as pd
import numpy as np
from web3.auto.infura import w3
from ens import ENS
import datetime
import os
import json
from flatten_json import flatten



def read_json(filename: str) -> dict:
  
    try:
        with open(filename, "r") as f:
            data = json.loads(f.read())
    except:
        raise Exception(f"Reading {filename} file encountered an error")
  
    return data

class Conversion():
    def handle_governances(self, path, file, jsonData):
        governance = pd.json_normalize(jsonData["governances"])
        governance.to_csv(f"{path}/csv/governance.csv", index=False)
    
    def handle_proposals(self, path, file, jsonData):
        flattenedj = pd.DataFrame(flatten(proposal, '.') for proposal in jsonData['proposals'])
        flattenedj.to_csv(f"{path}/csv/proposal_{file}.csv", index=False)
        proposals = pd.json_normalize(jsonData["proposals"], max_level=1)
        proposals.to_csv(f"{path}/csv/proposal{file}.csv", index=False)

    def handle_delegations(self, path, file, jsonData):
        delegations = pd.json_normalize(jsonData["delegations"], max_level=1)
        delegations.to_csv(f"{path}/csv/delegations{file}.csv", index=False)

    def handle_votedailysnapshots(self, path, file, jsonData):
        votedailysnapshots = pd.json_normalize(jsonData["voteDailySnapshots"], max_level=1)
        votedailysnapshots.to_csv(f"{path}/csv/votedailysnapshots{file}.csv", index=False)

    def handle_tokendailysnapshots(self, path, file, jsonData):
        tokendailysnapshots = pd.json_normalize(jsonData["tokenDailySnapshots"])
        tokendailysnapshots.to_csv(f"{path}/csv/tokendailysnapshots{file}.csv", index=False)

    def handle_delegates(self, path, file, jsonData):
        delegates = pd.json_normalize(jsonData["delegates"], max_level=1)
        delegates.to_csv(f"{path}/csv/delegates{file}.csv", index=False)

    def handle_votes(self, path, file, jsonData):
        votes = pd.json_normalize(jsonData["votes"], max_level=1)
        votes.to_csv(f"{path}/csv/votes{file}.csv", index=False)
    
"""  
dataframe.rename(columns={
    "results.school": "school",
    "results.high_school": "high_school",
    "results.graduation": "graduation",
    "education.graduation.major": "grad_major",
    "education.graduation.minor": "grad_minor"
}, inplace=True)
"""
  
  
def traverse_tree(path, conversion_methods):
    for root, dirs, files in os.walk(path):
        convert_json(root, files, conversion_methods)

def convert_json(folder, files, conversion_methods):
    conversion = Conversion()
    method = os.path.basename(os.path.normpath(folder))
    # if folder in conversion_methods:
    if method in conversion_methods:
        os.makedirs(f'{folder}/csv', exist_ok=True)
        conversion_method = getattr(conversion, "handle_"+method)
        for file in files:
            if file.endswith(".json"):
                jsonpath = folder+"/"+file
                _jsonData = read_json(jsonpath)
                conversion_method(folder, file, _jsonData)
            

