#!/usr/bin/env python3

import pandas as pd
import json
from datetime import date
try:
    from db import engine
except:
    engine = None

with open('rivm_graphs.json', 'r') as stream:
    data = json.load(stream)

df_age = None
df_hospital = None
df_confirmedcases = None
df_deaths = None

maanden = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']
maand_to_num = lambda x, maanden=maanden: maanden.index(x) + 1


def to_df(data):
    def parse_d(x):
        if '-' in x:
            year = 2000 + int(x.split('-')[2])
            month = maand_to_num(x.split('-')[1])
            day = int(x.split('-')[0])
        else:
            year = int(x.split(' ')[2])
            month = maand_to_num(x.split(' ')[1])
            day = int(x.split(' ')[0])
        return date(year=year, month=month, day=day)

    df = pd.DataFrame(data[1:], columns=['time', 'nieuw', 'gemeld'])
    # replace field that's entirely space (or empty) with 0
    df.replace(r'^\s*$', 0, regex=True, inplace=True)
    # replace nan with 0
    df.fillna(0, inplace=True)
    df = df.astype({'nieuw': 'int', 'gemeld': 'int'})
    df['time'] = df['time'].apply(
        lambda x: parse_d)
    return df


for key, easychart in data['easychart'].items():
    config = json.loads(easychart['config'])
    data_csv = json.loads(easychart['csv'])
    if config['title']['text'] == 'Leeftijd en geslacht overledenen':
        df_age = pd.DataFrame(data_csv[1:], columns=['Leeftijdsgroep', 'Man', "Vrouw"])
        df_age = df_age.astype({'Man': 'int', 'Vrouw': 'int'})
        df_age['Overleden'] = df_age['Man'] + df_age['Vrouw']
    elif config['title']['text'] == 'Overledenen per dag vanaf 27 februari 2020':
        df_deaths = to_df(data_csv)
        df_deaths['deaths'] = df_deaths['nieuw'] + df_deaths['gemeld']
        df_deaths['deaths_cum'] = df_deaths['deaths'].cumsum()
        df_deaths.drop(['nieuw', 'gemeld'], axis=1, inplace=True)
    elif config['title']['text'] == 'In ziekenhuis opgenomen patiënten vanaf 27 februari 2020':
        df_hospital = to_df(data_csv)
        df_hospital['Ziekenhuisopname'] = df_hospital['nieuw'] + df_hospital['gemeld']
        df_hospital['Ziekenhuisopname_add'] = df_hospital['Ziekenhuisopname'].cumsum()
        df_hospital.drop(['nieuw', 'gemeld'], axis=1, inplace=True)
    elif config['title']['text'] == 'GGD Meldingen positief geteste personen per dag  vanaf 27 februari 2020':
        df_confirmedcases = to_df(data_csv)
        df_confirmedcases['Cases'] = df_confirmedcases['nieuw'] + df_confirmedcases['gemeld']
        df_confirmedcases['Cases_add'] = df_confirmedcases['Cases'].cumsum()
        df_confirmedcases.drop(['nieuw', 'gemeld'], axis=1, inplace=True)

df_hospital = pd.merge(df_hospital, df_confirmedcases, left_index=True, right_index=True)
df_hospital.drop('time_y', axis=1, inplace=True)
df_hospital.rename({'time_x': 'time'}, axis=1, inplace=True)


if df_age is not None:
    name = 'netherlands_rivm_current_age'
    if engine is not None:
        df_age.to_sql(name, engine, if_exists='replace')
    df_age.to_csv('RIVM_timeseries/csv_latest/{}.csv'.format(name), sep=';', index=False)
if df_deaths is not None:
    name = 'netherlands_rivm_deaths'
    if engine is not None:
        df_deaths.to_sql(name, engine, if_exists='replace')
    df_deaths.to_csv('RIVM_timeseries/csv_latest/{}.csv'.format(name), sep=';', index=False)
if df_hospital is not None:
    name = 'netherlands_rivm_hospitals'
    if engine is not None:
        df_hospital.to_sql(name, engine, if_exists='replace')
    df_hospital.to_csv('RIVM_timeseries/csv_latest/{}.csv'.format(name), sep=';', index=False)