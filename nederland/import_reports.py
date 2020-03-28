#!/usr/bin/env python3

import tabula
from db import engine
import pandas as pd
import os

print("[>] parsing latest RIVM report")
reports = [x for x in list(os.walk("RIVM_reports"))[0][2] if x.split('.')[-1] == 'pdf']
reports.sort()

dfs = tabula.read_pdf("RIVM_reports/"+reports[-1], pages='all', multiple_tables=True)
df_age = dfs[0]
df_sex = dfs[1]

for df in dfs:
    try:
        if df.iloc[1,0] == 'Man' and df.iloc[2,0]:
            df_sex = df
            continue
    except:
        pass


    if df.columns[0] == 'Leeftijdsgroep':
        df_age = df
        continue
    try:
        if df.columns[2] == 'Ziekenhuisopname' and len(df.columns) == 3:
            df_hospital = df
            continue
    except:
        pass


df_age.drop([0,21], inplace=True)
df_age.drop(["%", "%.1", "%.2"], axis=1, inplace=True)
df_age.set_index("Leeftijdsgroep", inplace=True)
df_age = df_age.astype('int')

df_age["Totaal_per"] = round(df_age["Totaal"]/df_age["Totaal"].sum() * 100,2)
df_age["Ziekenhuis_per"] = round(df_age["Ziekenhuisopname"]/df_age["Ziekenhuisopname"].sum() * 100,2)
df_age["Overleden_per"] = round(df_age["Overleden"]/df_age["Overleden"].sum() * 100,2)

df_sex.drop(["%", "%.1", "%.2"], inplace=True, axis=1)
df_sex.drop([0], inplace=True)
df_sex.columns = ['Geslacht', 'Totaal', 'Ziekenhuisopname', 'Overleden']
df_sex.set_index('Geslacht', inplace=True)

df_hospital.drop([0], inplace=True)
df_hospital['Totaal_add'] = df_hospital['Totaal'].cumsum()
df_hospital['Ziekenhuisopname_add'] = df_hospital['Ziekenhuisopname'].cumsum()
df_hospital['Ziekenhuisopname_percentage'] = round(df_hospital['Ziekenhuisopname_add']/df_hospital['Totaal_add']*100,2)
c = list(df_hospital.columns)
c[0] = 'time'
df_hospital.columns = c
df_hospital['time'] = pd.to_datetime(df_hospital['time'], format="%Y-%m-%d")



df_age.to_sql('netherlands_rivm_current_age', engine, if_exists='replace')
df_sex.to_sql('netherlands_rivm_current_sex', engine, if_exists='replace')
df_hospital.to_sql('netherlands_rivm_hospitals', engine, if_exists='replace')
