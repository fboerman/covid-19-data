#!/usr/bin/env python3

import pandas as pd
import os
from datetime import datetime,date
from db import engine
from util import parse_all_csv

print("[>] reading and parsing csv")
fnames, dfs = parse_all_csv()

df = pd.concat(dfs).fillna(0).sort_index().astype('int')
df = df.loc[:,df.sum(axis=0) != 0]
df_diff = df.diff()

df.reset_index(level=0, inplace=True)
df.rename(columns={'index': 'time'}, inplace=True)
# set the 31/3 row to all zero since RIVM switched to only hospital cases that day
df_diff.loc[date(year=2020, month=3, day=31)] = len(df_diff.columns)*[0]
df_diff.reset_index(level=0, inplace=True)
df_diff.rename(columns={'index': 'time'}, inplace=True)

print("[>] write to database")
df.to_sql('netherlands_cities', engine, if_exists='replace')
df_diff.to_sql('netherlands_cities_diff', engine, if_exists='replace')
