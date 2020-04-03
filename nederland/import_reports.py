#!/usr/bin/env python3

import tabula
# from db import engine
import pandas as pd
import os
import PyPDF2
from datetime import date
import re

print("[>] parsing latest RIVM report")
reports = [x for x in list(os.walk("RIVM_reports"))[0][2] if x.split('.')[-1] == 'pdf']
reports.sort()
fileobj = open('RIVM_reports/'+reports[-1], 'rb')
pdfreader = PyPDF2.PdfFileReader(fileobj)
tables = [pagenum+1  for pagenum in range(pdfreader.numPages) if 'Tabel' in pdfreader.getPage(pagenum).extractText()]

dfs = tabula.read_pdf("RIVM_reports/"+reports[-1], pages=tables, multiple_tables=True)
df_sex = None
df_age = None
df_hospital = None
df_deaths = None

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
        if 'Ziekenhuis' in df.columns[2] and len(df.columns) == 3:
            df_hospital = df
            df_hospital.columns = ['Ziekenhuisopname' if 'Ziekenhuis' in x else x for x in df_hospital.columns]
            continue
    except:
        pass

if df_age is not None:
    df_age.drop([0], inplace=True)
    try:
        df_age.drop([x for x in df_age.columns if '%' in x], axis=1, inplace=True)
        df_age.columns = ['Leeftijdsgroep', 'Totaal', 'Ziekenhuisopname', 'Overleden']
    except:
        df_age.columns = list(range(len(df_age.columns)))
        df_age.drop([2,4], axis=1, inplace=True)
        df_age['Overleden'] = df_age['Overleden'].apply(lambda x: x.split(' ')[0])
        
    df_age.set_index("Leeftijdsgroep", inplace=True)
    df_age = df_age.astype('int')

    df_age["Totaal_per"] = round(df_age["Totaal"]/df_age["Totaal"].sum() * 100,2)
    df_age["Ziekenhuis_per"] = round(df_age["Ziekenhuisopname"]/df_age["Ziekenhuisopname"].sum() * 100,2)
    df_age["Overleden_per"] = round(df_age["Overleden"]/df_age["Overleden"].sum() * 100,2)
else:
    print("[!] could not find df_age")

if df_sex is not None:
    df_sex.drop(["%", "%.1", "%.2"], inplace=True, axis=1)
    df_sex.drop([0], inplace=True)
    df_sex.columns = ['Geslacht', 'Totaal', 'Ziekenhuisopname', 'Overleden']
    df_sex.set_index('Geslacht', inplace=True)
else:
    print("[!] could not find df_sex")

if df_hospital is not None:
    df_hospital.drop([0], inplace=True)
    df_hospital['Aantal_add'] = df_hospital['Aantal'].cumsum()
    df_hospital['Ziekenhuisopname_add'] = df_hospital['Ziekenhuisopname'].cumsum()
    df_hospital['Ziekenhuisopname_percentage'] = round(df_hospital['Ziekenhuisopname_add']/df_hospital['Aantal_add']*100,2)
    c = list(df_hospital.columns)
    c[0] = 'time'
    df_hospital.columns = c
    df_hospital['time'] = pd.to_datetime(df_hospital['time'], format="%Y-%m-%d")
else:
    print("[!] could not find df_hospital")

# this table somehow is not picked up by tabula so lets scrape it manually from the text, extracted by PyPDF2
# asume below statement only produces one result
pagenum = [pagenum  for pagenum in range(pdfreader.numPages) if 'Datumvanoverlijden' in pdfreader.getPage(pagenum).extractText() \
           and 'Tabel' in pdfreader.getPage(pagenum).extractText()][0]
pagestr = pdfreader.getPage(pagenum).extractText()
# the line we are seeking has multiple "2020" and "-" in it
dataline = None
for line in pagestr.split('\n'):
    if line.count("2020") > 1 and line.count("-") > 1:
        dataline = line
        break
if dataline is not None:
    datatable = []
    dataline = dataline.replace("202020", "20|2020").replace("2020", "|2020").replace("||", "|")
    rows = dataline.split("|")
    for i, row in enumerate(rows):
        if i == 0:
            continue
        num = row.split('-')[-1]
        if i == len(rows) -1:
            num = re.sub(r'[^0-9]', '' ,num)
        try:
            value = int(num[2:])
        except ValueError:
            value = 0
        datatable.append([
            date(year=int(row.split('-')[0]), month=int(row.split('-')[1]), day=int(num[:2])),
            value
        ])

    df_deaths = pd.DataFrame(datatable, columns=['time', 'deaths'])
    df_deaths['deaths_cum'] = df_deaths['deaths'].cumsum()

else:
    print("[!] could not find df_deaths")


fileobj.close()

if df_age is not None:
    df_age.to_sql('netherlands_rivm_current_age', engine, if_exists='replace')
if df_sex is not None:
    df_sex.to_sql('netherlands_rivm_current_sex', engine, if_exists='replace')
if df_hospital is not None:
    df_hospital.to_sql('netherlands_rivm_hospitals', engine, if_exists='replace')
if df_deaths is not None:
    df_deaths.to_sql('netherlands_rivm_deaths', engine, if_exists='replace')
