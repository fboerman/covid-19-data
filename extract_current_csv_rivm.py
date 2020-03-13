#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys


r = requests.get("https://www.rivm.nl/coronavirus-kaart-van-nederland")
if r.status_code != 200:
    print("[!] Could not retrieve rivm site")
    sys.exit(-1)

soup = BeautifulSoup(r.text, 'lxml')
csvdata = soup.find('div', id='csvData')
print(csvdata.text)
