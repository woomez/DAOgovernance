from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import os
import gc
import pandas as pd
from queries.delegations import delegateChangesQuery
from queries.delegatePower import delegatePowerChangesQuery

def generate_results(url, _queries):
    dao, api = url
    print(f"\nQuerying {dao}")
    for _query in _queries:
        query(dao, api, _query)
        gc.collect()

def make_client(api):
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=api)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client

def query(dao, api, query):
    client = make_client(api) 
    globals()[query+"Query"](client, dao, query)



