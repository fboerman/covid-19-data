#!/usr/bin/env python3

import pandas as pd
import pycountry_convert as pc
from db import engine

confirmed = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
deaths = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv'
recovered = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'


# parse the csv and sum all cases per country
def parse_csv_sumpercountry(fname):
    # df = pd.read_csv(fname, usecols = lambda x: x not in ['Lat','Long'])
    df = pd.read_csv(fname, header=None)
    df = df.fillna('')
    del df[0]
    # del df[1]
    del df[2]
    del df[3]
    # df[0] = pd.to_datetime(df[0], format="%m/%d/%y")
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    df.set_index('Country/Region', inplace=True)
    df=df.astype('int')
    df = df.groupby(df.index).sum().T
    df.index =  pd.to_datetime(df.index, format="%m/%d/%y")
    df.rename(columns={
        'Iran (Islamic Republic of)':'Iran', 
        'Mainland China': 'China',
        'Republic of Korea' : 'Korea, Republic of',
        'Taipei and environs': 'Taiwan',
        'UK': 'United Kingdom',
        'US': 'United States',
        'Congo (Kinshasa)' : 'Congo',
        'Taiwan*': 'Taiwan',
        'Korea, South' : 'South Korea'
    }, inplace=True)
    try:
#         df.drop(['Others'], axis=1, inplace=True)
        df.drop(['Cruise Ship'], axis=1, inplace=True)
    except:
        pass
    
    return df

print("[>] reading and parsing csv")

# read the three categories into dataframe
df_confirmed = parse_csv_sumpercountry(confirmed)
df_confirmed_diff = df_confirmed.diff()
df_confirmed['type']='confirmed'
df_confirmed_diff['type']='confirmed'

df_deaths = parse_csv_sumpercountry(deaths)
df_deaths_diff = df_deaths.diff()
df_deaths['type']='deaths'
df_deaths_diff['type']='deaths'

df_recovered = parse_csv_sumpercountry(recovered)
df_recovered_diff = df_recovered.diff()
df_recovered['type']='recovered'
df_recovered_diff['type']='recovered'

# create one big table
df=pd.concat([df_confirmed,df_deaths,df_recovered])
df_diff=pd.concat([df_confirmed_diff,df_deaths_diff,df_recovered_diff])

# function to retrieve continent with some handling of special cases since WHO does not fully follow ISO
get_continent = lambda cname: 'EU' if  cname in ['Reunion','Channel Islands', 'Holy See', 'Saint Barthelemy'] else 'AS' if cname in ['Hong Kong SAR', 'Macao SAR', 'occupied Palestinian territory'] else 'AF' if cname in ['Cote d\'Ivoire'] else pc.country_alpha2_to_continent_code(pc.country_name_to_country_alpha2(cname))

# create the time column needed for grafana
df.reset_index(level=0, inplace=True)
df.rename(columns={'index': 'time'}, inplace=True)
df_diff.reset_index(level=0, inplace=True)
df_diff.rename(columns={'index': 'time'}, inplace=True)

# write everything to postgresql per continent
print("[>] write to database")
countries = list(df_confirmed.columns)
countries.remove('type')
for continent in ['AF', 'AS', 'EU', 'NA', 'OC', 'SA']:
    countries_select = [c for c in countries if get_continent(c) == continent]
    df[['time'] + list(countries_select) + ['type']].to_sql('world_timeseries_'+continent, engine, if_exists='replace')
    df_diff[['time'] + list(countries_select) + ['type']].to_sql('world_timeseries_'+continent+'_diff', engine, if_exists='replace')

