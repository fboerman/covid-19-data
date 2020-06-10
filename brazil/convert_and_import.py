#!/usr/bin/env python3

import pandas as pd
from regions import states
from db import engine

def convert_code(code):
    return [c[0] for c in states if c[1]==code][0]

df = pd.read_excel('covid.saude.gov.br.xlsx')
df.fillna(0, inplace=True)
df = df[df.apply(lambda x: x['estado'] != 0 and x['municipio'] == 0 and x['populacaoTCU2019'] != 0, axis=1)]
df = df[['regiao', 'estado', 'data', 'populacaoTCU2019', 'casosAcumulado', 'casosNovos', 'obitosAcumulado', 'obitosNovos']]
df['estado'] = df['estado'].apply(convert_code)
df['data'] = df['data'].dt.date
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
df['cases_cum_norm'] = round(df['cases_cum']/df['population'], 4)
df['deaths_cum_norm'] = round(df['deaths_cum']/df['population'], 4)
df.drop('population', axis=1, inplace=True)


