#!/usr/bin/env python3

### WARNING
#   PDF scraping is very flacky, I kept adjusting this script but it became to much of a hassle and sometimes
#   plain didnt work. This script works until the report from 06-04-2020. See import_rivm_reported_data.py
#   for a scraping method that pulls in the json from rivm graps page, not all data is supported so some pdf scraping is imported
#   this will be phased out as soon as rivm publishes graphs of the other things as well

###

import tabula
from db import engine
import pandas as pd
import os
import PyPDF2
from datetime import date

print("[>] parsing latest RIVM report")
reports = [x for x in list(os.walk("RIVM_reports"))[0][2] if x.split('.')[-1] == 'pdf']
reports.sort()
fileobj = open('RIVM_reports/'+reports[-1], 'rb')
pdfreader = PyPDF2.PdfFileReader(fileobj)
tables = [pagenum+1  for pagenum in range(pdfreader.numPages) if 'Tabel' in pdfreader.getPage(pagenum).extractText()]

if len(tables) == 0:
    tables='all'

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
    df_hospital.drop([0,1], inplace=True)
    df_hospital['Aantal_add'] = df_hospital['Totaal'].cumsum()
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
           and 'Tabel' in pdfreader.getPage(pagenum).extractText()]
if len(pagenum) == 0:
    print("[!] could not find df_deaths")
else:
    pagestr = pdfreader.getPage(pagenum[0]).extractText()
    datatable = []
    for line in pagestr.split('\n'):
        if '2020-' not in line or 'T/m' in line:
            continue
        parts = line.split('-')
        datatable.append([
            date(year=int(parts[0]), month=int(parts[1]), day=int(parts[2][:2])),
            int(parts[2][2:])
        ])
    df_deaths = pd.DataFrame(datatable, columns=['time', 'deaths'])
    df_deaths['deaths_cum'] = df_deaths['deaths'].cumsum()

## deprecated method for before 04-04-2020
# # the line we are seeking has multiple "2020" and "-" in it
# dataline = None
# for line in pagestr.split('\n'):
#     if line.count("2020") > 1 and line.count("-") > 1:
#         dataline = line
#         break
# if dataline is not None:
#     datatable = []
#     dataline = dataline.replace("202020", "20|2020").replace("2020", "|2020").replace("||", "|")
#     rows = dataline.split("|")
#     for i, row in enumerate(rows):
#         if i == 0:
#             continue
#         num = row.split('-')[-1]
#         if i == len(rows) -1:
#             num = re.sub(r'[^0-9]', '' ,num)
#         try:
#             value = int(num[2:])
#         except ValueError:
#             value = 0
#         datatable.append([
#             date(year=int(row.split('-')[0]), month=int(row.split('-')[1]), day=int(num[:2])),
#             value
#         ])
#
#     df_deaths = pd.DataFrame(datatable, columns=['time', 'deaths'])
#     df_deaths['deaths_cum'] = df_deaths['deaths'].cumsum()
#
# else:
#     print("[!] could not find df_deaths")


fileobj.close()

if df_age is not None:
    name = 'netherlands_rivm_current_age'
    df_age.to_sql(name, engine, if_exists='replace')
    df_age.to_csv('RIVM_reports/csv_latest/{}.csv'.format(name), sep=';', index=False)
if df_sex is not None:
    name = 'netherlands_rivm_current_sex'
    df_sex.to_sql(name, engine, if_exists='replace')
    df_sex.to_csv('RIVM_reports/csv_latest/{}.csv'.format(name), sep=';', index=False)
if df_hospital is not None:
    name = 'netherlands_rivm_hospitals'
    df_hospital.to_sql(name, engine, if_exists='replace')
    df_hospital.to_csv('RIVM_reports/csv_latest/{}.csv'.format(name), sep=';', index=False)
if df_deaths is not None:
    name = 'netherlands_rivm_deaths'
    df_deaths.to_sql(name, engine, if_exists='replace')
    df_deaths.to_csv('RIVM_reports/csv_latest/{}.csv'.format(name), sep=';', index=False)

