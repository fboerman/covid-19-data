#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys
import re
import pandas as pd
import unicodedata
from db import engine

try:
    r = requests.get("https://www.rivm.nl/coronavirus-kaart-van-nederland", timeout=10)
except:
    print("[!] Could not retrieve rivm site: unreachable")
    sys.exit(-1)
if r.status_code != 200:
    print("[!] Could not retrieve rivm site: {}".format(r.status_code))
    sys.exit(-1)

soup = BeautifulSoup(r.text, 'lxml')
# cards = soup.find('div', {'class':['card-wrapper', 'top']})
# numbers = [int(re.sub(r'[^0-9]', '', x.text)) for x in cards.find_all('span', class_='h3')]
# numbers_diff = [int(x) for x in [re.sub(r'[^0-9]', '', x.text) for x in cards.find_all('p') if '+' in str(x)] if x != '']

rows = soup.find('table').find_all('tr')
numbers = []
numbers_diff = []
for row in rows:
    parts = unicodedata.normalize("NFKD", row.find('h4').text).split(' ')
    numbers.append(int(re.sub(r'[^0-9]', '', parts[0])))
    numbers_diff.append(int(re.sub(r'[^0-9]', '', parts[1])))

# numbers = [int(re.sub(r'[^0-9]', '', x.text)) for x in rows[1].find_all('td')[1].split(' ')]
# numbers_diff = [int(re.sub(r'[^0-9]', '', x.text)) for x in rows[2].find_all('td')]

df = pd.DataFrame([
    numbers,
    numbers_diff
], columns=['confirmed', 'admissions', 'deaths'])

df.to_sql('netherlands_rivm_current', engine, if_exists='replace')
