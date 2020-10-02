#!/usr/bin/env python3
from datetime import datetime

stream = open('RIVM_timeseries/gemeenten_2weken/latest.csv', 'r')

csvs = []
csv = None
columns = None
while True:
    # search for start
    line = stream.readline()
    if not line:
        csvs.append(csv)
        break
    line = line.strip('\n').strip()
    if 'Gemnr' in line:
        columns = line
        continue
    if 's-Gravenhage' in line: # s-Gravenhage is always the first one mentoined
        # append lines until new csv starts
        if csv is not None:
            csvs.append(csv)
        csv = [line]
    elif csv is not None and line:
        csv.append(line)

stream.close()
#datetime.strptime(fname.split('.')[0], "%d%m%Y").strftime('%Y-%m-%d') + ".csv"
date_c = columns.split(';').index('tot_datum')
for csv in csvs:
    d = csv[0].split(";")[date_c] # this assumes all lines are same date
    with open(f'RIVM_timeseries/gemeenten_2weken/{datetime.strptime(d, "%d-%m-%Y").strftime("%Y-%m-%d")}.csv', 'w') as stream:
        stream.writelines([x + '\n' for x in [columns]+csv])
