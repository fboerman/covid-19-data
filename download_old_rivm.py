#!/usr/bin/env python3

import requests
from datetime import date, timedelta
baseurl = "https://www.volksgezondheidenzorg.info/sites/default/files/map/detail_data/klik_corona{}"

status = lambda r: 404 if r is None else r.status_code

def fetch(url):
    try:
        r = requests.get(url, timeout=1)
        return r
    except requests.exceptions.Timeout:
        return None
 

d = date.today() - timedelta(1)
while True:

    link = baseurl.format(d.strftime("%d%m%Y"))
    print("trying {}: ".format(d.strftime("%d%m%Y")), end='')
    r = fetch(link + "_0.csv")
    fname = "klik_corona" + d.strftime("%d%m%Y") + "_0.csv"
    if status(r) != 200:
        r = fetch(link + ".csv")
        fname = "klik_corona" + d.strftime("%d%m%Y") + ".csv"

    print(status(r))
    if status(r) == 200:
        with open('nederland/RIVM/' + fname, 'wb') as stream:
            stream.write(r.content)

    d -= timedelta(1)
    if d.year < 2020:
        break
