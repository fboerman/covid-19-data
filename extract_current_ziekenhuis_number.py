#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


url = "https://www.rivm.nl/nieuws/actuele-informatie-over-coronavirus"
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')
zinnen = soup.find('div', class_="par content-block-wrapper").find_all('span', class_='content-date-created')[2].text.split('.')
zin = [z for z in zinnen if 'opgenomen' in z][0]
number = int(re.findall(r"\d+", zin)[0])

with open('nederland/RIVM_extra.csv', 'a') as stream:
    stream.write(datetime.now().strftime("%d-%m-%Y") + ";" + str(number))

