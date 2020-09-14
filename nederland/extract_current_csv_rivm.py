#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys

try:
    r = requests.get("https://www.rivm.nl/coronavirus-kaart-van-nederland", timeout=10)
except:
    print("[!] Could not retrieve rivm site: unreachable")
    sys.exit(-1)
if r.status_code != 200:
    print("[!] Could not retrieve rivm site: {}".format(r.status_code))
    sys.exit(-1)

soup = BeautifulSoup(r.text, 'lxml')
csvdata = soup.find('div', id='csvData')
print(csvdata.text)