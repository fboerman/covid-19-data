#!/usr/bin/env python3

import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from regions import states

def convert_code(code):
    return [c[0] for c in states if c[1]==code][0]

def get_data_from_html(html):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table')
    region = None
    data = []
    rows = table.find_all('tr')
    for i, row in enumerate(rows):
        if i in [0, 1] or i == len(rows) - 1:
            continue
        cells = row.find_all('td')
        if len(cells) == 1:
            region = cells[0].text.strip().split('-')[0].strip()
            continue
        data.append([
            convert_code(cells[1].text.strip()),
            # cells[1].text.strip(),
            int(cells[2].text.strip()),
            int(cells[3].text.strip()),
            #             region
        ])
    return data

def convert_data_to_df(data_per_date, df):
    frames = [df]
    for d, values in data_per_date.items():
        df = pd.DataFrame(values).T
        df.columns = df.iloc[0]
        df.drop([0], inplace=True)
        df['time'] = [d,d]
        df['type'] = ['confirmed', 'deaths']
        frames.append(df)
    df = pd.concat(frames)
    df.sort_values('time', inplace=True)
    return df


if __name__ == '__main__':
    feed = feedparser.parse("https://www.saude.gov.br/noticias/agencia-saude?format=feed&type=rss")

    data_per_date = {}
    try:
        df = pd.read_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', delimiter=';')
        df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d")
        existing = [time.date() for time in df['time']]
    except:
        df = pd.DataFrame()
        existing = []

    df['time'] = existing
    for entry in [entry for entry in feed.entries if 'table' in entry['summary'] and 'corona' in entry['title'].lower()]:
        d = datetime.strptime(entry['published'], "%a, %d %b %Y %H:%M:%S %z").date()
        if d in existing:
            continue
    #     data_per_date[d.strftime("%d-%m-%Y")] = data
        data_per_date[d] = get_data_from_html(entry['summary'])
    df = convert_data_to_df(data_per_date, df)
    df.to_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', sep=';', index=False)