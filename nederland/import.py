#!/usr/bin/env python3

import pandas as pd
import os
from datetime import datetime,date
try:
    from db import engine
except:
    engine = None

print("[>] reading and parsing csv")
df = pd.read_csv('RIVM_timeseries/latest.csv', skip_blank_lines=True, delimiter=';')
df.drop(['Gemnr', 'Bev_2020', 'van_datum'], axis=1, inplace=True)
df['tot_datum'] = pd.to_datetime(df['tot_datum'], format='%d-%m-%Y')
df.rename(columns={'tot_datum': 'time'}, inplace=True)
df.sort_values(['time', 'Gemeente'], inplace=True)
df['Totaal_inc100000'] = df['Totaal_inc100000'].str.replace(',','.').astype(float)
df['Zkh_inc100000'] = df['Zkh_inc100000'].str.replace(',','.').astype(float)
df['Overleden_inc100000'] = df['Overleden_inc100000'].str.replace(',','.').astype(float)

if engine is not None:
    print("[>] write to database")
    df.to_sql('netherlands_cities', engine, if_exists='replace', index=False)
    #df_diff.to_sql('netherlands_cities_diff', engine, if_exists='replace', index=False)
