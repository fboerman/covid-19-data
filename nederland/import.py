#!/usr/bin/env python3

import pandas as pd
import os
from datetime import datetime,date
try:
    from db import engine
except:
    engine = None

print("[>] reading and parsing csv for two weeks intervals")
df_2weeks = pd.read_csv('RIVM_timeseries/gemeenten_2weken/latest.csv', skip_blank_lines=True, delimiter=';')
df_2weeks.drop(['Gemnr', 'Bev_2020', 'van_datum'], axis=1, inplace=True)
df_2weeks['tot_datum'] = pd.to_datetime(df_2weeks['tot_datum'], format='%d-%m-%Y')
df_2weeks.rename(columns={'tot_datum': 'time'}, inplace=True)
df_2weeks.sort_values(['time', 'Gemeente'], inplace=True)
df_2weeks['Totaal_inc100000'] = df_2weeks['Totaal_inc100000'].str.replace(',','.').astype(float)
df_2weeks['Zkh_inc100000'] = df_2weeks['Zkh_inc100000'].str.replace(',','.').astype(float)
df_2weeks['Overleden_inc100000'] = df_2weeks['Overleden_inc100000'].str.replace(',','.').astype(float)


print("[>] reading and parsing csv for daily")
df_people = pd.read_csv('RIVM_timeseries/gemeenten_inwoners.csv', delimiter=';')
df_people.set_index('Gemeentecode', inplace=True)

df = pd.read_csv('RIVM_timeseries/gemeenten_latest.csv', delimiter=';')
df = df[['Date_of_publication', 'Municipality_code', 'Municipality_name', 'Total_reported', "Hospital_admission", 'Deceased']].dropna()
df['Municipality_code'] = df['Municipality_code'].apply(lambda x: int(x[2:]))
df.rename({
    'Total_reported': 'Totaal_Absoluut',
    'Hospital_admission': 'Zkh_Absoluut',
    'Deceased': 'Overleden_Absoluut',
    'Date_of_publication': 'time'
}, axis=1, inplace=True)
df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d')
df['Num_Bevolking'] = df.apply(lambda x: df_people.loc[x['Municipality_code']]['Inwoneraantal'], axis=1)


if engine is not None:
    print("[>] write to database")
    df_2weeks.to_sql('netherlands_cities_2weeks', engine, if_exists='replace', index=False)
    df.to_sql('netherlands_cities', engine, if_exists='replace', index=False)
