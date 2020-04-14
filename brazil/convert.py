#!/usr/bin/env python3

import pandas as pd
from regions import states

def convert_code(code):
    return [c[0] for c in states if c[1]==code][0]


sourcedf = pd.read_csv("saude.gov.br/source.csv", delimiter=';')
sourcedf.drop(['regiao', 'casosNovos', 'obitosNovos'], axis=1, inplace=True)
sourcedf['data'] = pd.to_datetime(sourcedf['data'], format="%d/%m/%Y")
sourcedf['data'] = sourcedf['data'].dt.date

dfs = []

for d, df in list(sourcedf.groupby('data')):
    df.drop('data', axis=1, inplace=True)
    df['estado'] = df['estado'].apply(convert_code)
    df = df.T
    df.columns = df.loc['estado']
    df.drop('estado', inplace=True)
    df['time'] = [d, d]
    df = df.loc[:, ['time'] + sorted(list(df.columns)[:-1])]
    df['type'] = ['confirmed', 'deaths']
    df.reset_index(inplace=True)
    df.drop('index', axis=1, inplace=True)
    dfs.append(df)

df = pd.concat(dfs)
df.reset_index(inplace=True)
df.drop('index', axis=1, inplace=True)

df.to_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', sep=';', index=False)