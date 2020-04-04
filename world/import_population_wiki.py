#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys
import pandas as pd


r = requests.get("https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population")
if r.status_code != 200:
    print("[!] Could not load page: {}".format(r.status_code))
    sys.exit(-1)

soup = BeautifulSoup(r.text, 'lxml')
rows = soup.find('table', lambda class_: 'wikitable' in class_ and 'sortable' in class_ if class_ is not None else False).find_all('tr')
datatable = []
def extractfromcell(cell):
    if cell.find('span', class_='nowrap') is not None:
        cell =  cell.find('span', class_='nowrap')
    firstlink = cell.find('a')
    if firstlink is not None:
        if firstlink.text != '':
            return firstlink.text
        # there is a link, find the one which has mw-redirect class otherwise first one with no image class
        # return cell.find_all('a', lambda class_: 'image' not in class_)[0].text
        if len(cell.find_all('a', class_='mw-redirect')) != 0:
            return cell.find_all('a', class_='mw-redirect')[0].text
        else:
            return cell.find_all('a', lambda class_: class_ != 'image', recursive=False)[0].text
    else:
        return cell.text

for i, row in enumerate(rows):
    if i == 0:
        continue

    cells = row.find_all('td')
    if len(cells) == 0:
        continue
    datatable.append([
        extractfromcell(cells[1]),
        int(extractfromcell(cells[2]).replace(',',''))
    ])

df = pd.DataFrame(datatable, columns=['country', 'population'])
df.set_index('country', inplace=True)

df.to_csv('world_population_wiki.csv', sep=';')
