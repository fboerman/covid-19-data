#!/usr/bin/env python3

import pandas as pd
from regions import states
from datetime import datetime
try:
    from db import engine
except:
    engine = None


def convert_code(code):
    return [c[0] for c in states if c[1] == code][0]

def rename_and_order(df):
    df = df[['regiao', 'estado', 'data', 'populacaoTCU2019', 'casosAcumulado', 'casosNovos', 'obitosAcumulado',
             'obitosNovos']].copy()
    # df['data'] = df['data'].dt.date
    df.rename(columns={
        'regiao': 'region',
        'estado': 'state',
        'data': 'time',
        'populacaoTCU2019': 'population',
        'casosAcumulado': 'cases_cum',
        'casosNovos': 'cases_new',
        'obitosAcumulado': 'deaths_cum',
        'obitosNovos': 'deaths_new'
    }, inplace=True)
    df.sort_values(['region', 'state', 'time'], ascending=[True, True, True], inplace=True)
    df['population'] = df['population'].astype('float')

    return df


df = pd.read_csv('covid.saude.gov.br.csv', delimiter=';', parse_dates=['data'], date_parser=
                 lambda x: datetime.strptime(x, "%Y-%m-%d"))
df.fillna(0, inplace=True)
df_all = df[df.apply(lambda x: x['regiao'] == 'Brasil', axis=1)]
df = df[df.apply(lambda x: x['estado'] != 0 and x['municipio'] == 0 and x['populacaoTCU2019'] != 0, axis=1)]
df['estado'] = df['estado'].apply(convert_code)

df = rename_and_order(df)
df_all = rename_and_order(df_all)
df_all.drop(['region', 'state', 'population'], axis=1, inplace=True)

df['cases_cum_norm'] = round(df['cases_cum']/(df['population']/1e5), 4)
df['deaths_cum_norm'] = round(df['deaths_cum']/(df['population']/1e5), 4)
df.drop('population', axis=1, inplace=True)

df.to_csv('brazil-states.csv', sep=';', index=False, date_format='%Y-%m-%d')

if engine is not None:
    df.to_sql('brazil_states', engine, if_exists='replace', index=False)
    df_all.to_sql('brazil_whole', engine, if_exists='replace', index=False)
