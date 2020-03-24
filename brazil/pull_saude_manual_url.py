#!/usr/bin/env python3

from pull_saude_from_feed import get_data_from_html, convert_data_to_df
import pandas as pd
from datetime import datetime
import requests

if __name__ == '__main__':
    data_per_date = {}
    df = pd.read_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', delimiter=';')
    df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d")

    data_per_date = {}
    while True:
        url = input("Manual url to feed from (q for exit):")
        if url == 'q':
            break
        d = input("Date (format %Y-%m-%d):")
        d = datetime.strptime(d, "%Y-%m-%d").date()
        if d in df['time']:
            print("this date is already added")
            continue
        r = requests.get(url)
        data_per_date[d] = get_data_from_html(r.text)

    df = convert_data_to_df(data_per_date, df)
    df.to_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', sep=';', index=False)