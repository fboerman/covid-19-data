#!/usr/bin/env python3

import pandas as pd
import pycountry_convert as pc
import os
from datetime import datetime,date
from db import engine

files = list(os.walk("RIVM"))[0][2]

print("[>] reading and parsing csv")
dfs = []
for file in files:
    d = datetime.strptime(file.split('.')[0], '%d%m%Y').date()
    if d <= date(year=2020,month=3,day=11):
        df = pd.read_csv('RIVM/'+file, delimiter=';')
        del df['id']
        del df['Indicator']
        df.fillna(0, inplace=True)
    elif d == date(year=2020,month=3,day=12):
        df = pd.read_csv('RIVM/'+file, delimiter=';', skiprows=[2,3], skip_blank_lines=True)
        del df['Gemnr']
    elif d <= date(year=2020,month=3, day=16):
        df = pd.read_csv("RIVM/"+file, delimiter=';', skiprows=[2,3], skip_blank_lines=True, index_col=False, usecols=['Gemeente', 'Aantal'])
    else:
        df = pd.read_csv("RIVM/"+file, delimiter=';', skiprows=[2], skip_blank_lines=True, index_col=False, usecols=['Gemeente', 'Aantal'])
    df.set_index('Gemeente', inplace=True)
    df = df.T
    df.index = [d]
    dfs.append(df)

df = pd.concat(dfs).fillna(0).sort_index().astype('int')
df = df.loc[:,df.sum(axis=0) != 0]
df_diff = df.diff()

df.reset_index(level=0, inplace=True)
df.rename(columns={'index': 'time'}, inplace=True)
df_diff.reset_index(level=0, inplace=True)
df_diff.rename(columns={'index': 'time'}, inplace=True)

df_extra = pd.read_csv('RIVM_extra.csv', delimiter=';')
df_extra['time'] = pd.to_datetime(df_extra['time'], format="%d-%m-%y")

print("[>] write to database")
df.to_sql('netherlands_cities', engine, if_exists='replace')
df_diff.to_sql('netherlands_cities_diff', engine, if_exists='replace')
df_extra.to_sql('netherlands_extra', engine, if_exists='replace')
