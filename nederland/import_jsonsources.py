#!/usr/bin/env python3

import pandas as pd
import requests
import json
from db import engine

with open('json-sources-config.json', 'r') as stream:
    config = json.load(stream)

for table in config:
    df = None
    print("[*>] loading from json {}".format(table['tablename']))
    for resource in table['data']:
        dfi = pd.read_json(requests.get(resource['url']).text)
        dfi = dfi.set_index(resource['index'])
        dfi = dfi[resource['columns']]
        if df is None:
            df = dfi
        else:
            df = pd.merge(df, dfi, left_index=True, right_index=True)
    if "csv" in table:
        df.to_csv(table["csv"], sep=';')
    df.reset_index(level=0, inplace=True)
    df.rename(columns={'index': 'time'}, inplace=True)
    df.to_sql(table['tablename'], engine, if_exists='replace')