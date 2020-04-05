#!/usr/bin/env python3

from db import engine
import pandas as pd

def get_diff(dfbase, dfslice):
    dfslice = dfslice.drop(['type', 'time'], axis=1)
    dfslice = dfslice.diff().fillna(0)
    dfslice['time'] = dfbase['time']
    return dfslice

df = pd.read_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', delimiter=';')
df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d")

df_diff_confirmed = get_diff(df, df[df['type']=='confirmed'])
df_diff_confirmed['type'] = 'confirmed'
df_diff_deaths = get_diff(df, df[df['type']=='deaths'])
df_diff_deaths['type'] = 'deaths'
df_diff = pd.concat([df_diff_confirmed, df_diff_deaths])

print("[>] write to database")
df.to_sql('brazil_states', engine, if_exists='replace', index=False)
df_diff.to_sql('brazil_states_diff', engine, if_exists='replace', index=False)
