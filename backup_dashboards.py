#!/usr/bin/env python3

import requests
import sys
import json

r = requests.get("https://data.boerman.dev/api/search?query=%")
if r.status_code != 200:
    sys.exit(-1)

dashboards = []

for uid in [x['uid'] for x in r.json()]:
    r2 = requests.get("https://data.boerman.dev/api/dashboards/uid/" + uid)
    if r2.status_code != 200:
        sys.exit(-1)
    dashboards.append(r2.json()['dashboard'])

with open('dashboards_backup.json', 'w') as stream:
    json.dump(dashboards, stream)
