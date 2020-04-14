#!/usr/bin/env python3

import pandas as pd
import requests
import json
from db import engine
from functools import reduce

with open('json-sources-config.json', 'r') as stream:
    config = json.load(stream)

for table in config:
    df = None
    print("[*>] loading from json {}".format(table['tablename']))
    if table['type'] == 'dataframe':
        for resource in table['data']:
            dfi = pd.read_json(requests.get(resource['url']).text)
            dfi = dfi.set_index(resource['index'])
            if 'columns' in resource:
                dfi = dfi[resource['columns']]
            if df is None:
                df = dfi
            else:
                df = pd.merge(df, dfi, left_index=True, right_index=True)
    elif table['type'] == 'timeseries':
        dfs = []
        for resource in table['data']:
            data = requests.get(resource['url']).json()
            if type(data[0]) == list:
                df_total = None
                for d in data:
                    df = pd.DataFrame(d)
                    df[resource['index']] = pd.to_datetime(df[resource['index']], format=table['dformat'])
                    df[resource['index']] = df[resource['index']].dt.date
                    df.set_index(resource['index'], inplace=True)
                    if df_total is None:
                        df_total = df
                    else:
                        df_total = df_total.add(df, fill_value=0)
            else:
                df_total = pd.DataFrame(data)
                df_total[resource['index']] = pd.to_datetime(df_total[resource['index']], format=table['dformat'])
                df_total[resource['index']] = df_total[resource['index']].dt.date
                df_total.set_index(resource['index'], inplace=True)
            df_total.columns = resource['columns']
            dfs.append(df_total)
        df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), dfs)
    elif table['type'] == 'custom':
        df = pd.DataFrame(requests.get(table['data']['url']).json())
        df.set_index(table['data']['index'], inplace=True)

    if "csv" in table:
        df.to_csv(table["csv"], sep=';')
    df.reset_index(level=0, inplace=True)
    df.rename(columns={'index': 'time'}, inplace=True)
    df.to_sql(table['tablename'], engine, if_exists='replace')