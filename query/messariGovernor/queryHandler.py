from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import os
import gc
import pandas as pd
from queries.delegations import delegateChangesQuery
from queries.delegatePower import delegatePowerChangesQuery
from queries.votes import voteQuery

def generate_results(name, dao, _queries):
    print(f"Querying {name} \n")
    url = dao['url']

    for _query in _queries:
        query(name, dao, url, _query)
        gc.collect()

def make_client(api):
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=api)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client

def query(name, dao, api, query):
    client = make_client(api) 
    globals()[query+"Query"](client, name, dao, query)



