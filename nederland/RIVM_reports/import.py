#!/usr/bin/env python3

import tabula
from db import engine

print("[>] parsing pdf 23-03-2020")
df = tabula.read_pdf("23-03-2020.pdf", pages='all', multiple_tables=True)
print("[>] writing to db")
df_age = df[0]
df_sex = df[1]
#df_conditions = df[2]

df_age.drop([0], inplace=True)
df_age.drop(["%", "%.1", "%.2"], axis=1, inplace=True)
df_age.set_index("Leeftijdsgroep", inplace=True)

df_age["Totaal_per"] = round(df_age["Totaal"]/df_age["Totaal"].sum() * 100,2)
df_age["Ziekenhuis_per"] = round(df_age["Ziekenhuisopname"]/df_age["Ziekenhuisopname"].sum() * 100,2)
df_age["Overleden_per"] = round(df_age["Overleden"]/df_age["Overleden"].sum() * 100,2)

df_sex.drop(["%", "%.1", "%.2"], inplace=True, axis=1)
df_sex.drop([0], inplace=True)
df_sex.set_index('Geslacht', inplace=True)

#df_conditions.drop([4,5,6,7], inplace=True)
#df_conditions.drop(["%", "%.1", "%.2", "Unnamed: 0"], inplace=True, axis=1)


df_age.to_sql('netherlands_rivm_23032020_age', engine, if_exists='replace')
df_sex.to_sql('netherlands_rivm_23032020_sex', engine, if_exists='replace')
