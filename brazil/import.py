#!/usr/bin/env python3

from db import engine
import pandas as pd

df = pd.read_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', delimiter=';')

print("[>] write to database")
df.to_sql('brazil_states', engine, if_exists='replace')