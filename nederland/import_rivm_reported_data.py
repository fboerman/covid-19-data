#!/usr/bin/env python3

import pandas as pd
import json
from datetime import date
from db import engine

with open('rivm_graphs.json', 'r') as stream:
    data = json.load(stream)

df_age = None
df_hospital = None
df_confirmedcases = None
df_deaths = None

maanden = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']
maand_to_num = lambda x, maanden=maanden: maanden.index(x) + 1

def to_df(data):
    df = pd.DataFrame(data[1:], columns=['time', 'nieuw', 'gemeld'])
    df = df.astype({'nieuw': 'int', 'gemeld': 'int'})
    df['time'] = df['time'].apply(
        lambda x: date(year=2020, month=maand_to_num(x.replace('-', ' ').split(' ')[1]),
                       day=int(x.replace('-', ' ').split(' ')[0])))
    return df

for key, easychart in data['easychart'].items():
    config = json.loads(easychart['config'])
    data = json.loads(easychart['csv'])
    if config['title']['text'] == 'Leeftijd en geslacht overledenen':
        df_age = pd.DataFrame(data[1:], columns=['Leeftijdsgroep', 'Man', "Vrouw"])
        df_age = df_age.astype({'Man': 'int', 'Vrouw': 'int'})
        df_age['Overleden'] = df_age['Man'] + df_age['Vrouw']
    elif config['title']['text'] == 'Overledenen per dag':
        df_deaths = to_df(data)
        df_deaths['deaths'] = df_deaths['nieuw'] + df_deaths['gemeld']
        df_deaths['deaths_cum'] = df_deaths['deaths'].cumsum()
        df_deaths.drop(['nieuw', 'gemeld'], axis=1, inplace=True)
    elif config['title']['text'] == 'In ziekenhuis opgenomen patiënten':
        df_hospital = to_df(data)
        df_hospital['Ziekenhuisopname'] = df_hospital['nieuw'] + df_hospital['gemeld']
        df_hospital['Ziekenhuisopname_add'] = df_hospital['Ziekenhuisopname'].cumsum()
        df_hospital.drop(['nieuw', 'gemeld'], axis=1, inplace=True)
    elif config['title']['text'] == 'Bij de GGD gemelde patiënten':
        df_confirmedcases = to_df(data)
        df_confirmedcases['Cases'] = df_confirmedcases['nieuw'] + df_confirmedcases['gemeld']
        df_confirmedcases['Cases_add'] = df_confirmedcases['Cases'].cumsum()
        df_confirmedcases.drop(['nieuw', 'gemeld'], axis=1, inplace=True)

df_hospital = pd.merge(df_hospital, df_confirmedcases, left_index=True, right_index=True)
df_hospital.drop('time_y', axis=1, inplace=True)
df_hospital.rename({'time_x': 'time'}, axis=1, inplace=True)


if df_age is not None:
    name = 'netherlands_rivm_current_age'
    df_age.to_sql(name, engine, if_exists='replace')
    df_age.to_csv('RIVM_reports/csv_latest/{}.csv'.format(name), sep=';', index=False)
if df_deaths is not None:
    name = 'netherlands_rivm_deaths'
    df_deaths.to_sql(name, engine, if_exists='replace')
    df_deaths.to_csv('RIVM_reports/csv_latest/{}.csv'.format(name), sep=';', index=False)
if df_hospital is not None:
    name = 'netherlands_rivm_hospitals'
    df_hospital.to_sql(name, engine, if_exists='replace')
    df_hospital.to_csv('RIVM_reports/csv_latest/{}.csv'.format(name), sep=';', index=False)