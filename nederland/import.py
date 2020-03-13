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
        df = pd.read_csv('RIVM/'+file, delimiter=';', skiprows=[0,2,3])
        del df['Gemnr']
    else:
        df = pd.read_csv("RIVM/"+file, delimiter=';', skiprows=[0,2,3], index_col=False, usecols=['Gemeente', 'Aantal'])
    df.set_index('Gemeente', inplace=True)
    df = df.T
    df.index = [d]
    dfs.append(df)

df = pd.concat(dfs).fillna(0).sort_index().astype('int')
df = df.loc[:,df.sum(axis=0) != 0]
df.reset_index(level=0, inplace=True)
df.rename(columns={'index': 'time'}, inplace=True)
print("[>] write to database")
df.to_sql('netherlands_cities', engine, if_exists='replace')
