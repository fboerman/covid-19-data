import pandas as pd
import os
from datetime import datetime,date

def parse_all_csv(turn=True):
    files = list(os.walk("RIVM_timeseries"))[0][2]
    files.sort()

    dfs = []
    for file in files:
        d = datetime.strptime(file.split('.')[0], '%d%m%Y').date()
        if d <= date(year=2020, month=3, day=11):
            df = pd.read_csv('RIVM_timeseries/' + file, delimiter=';')
            del df['id']
            del df['Indicator']
            df.fillna(0, inplace=True)
        elif d == date(year=2020, month=3, day=12):
            df = pd.read_csv('RIVM_timeseries/' + file, delimiter=';', skiprows=[2, 3], skip_blank_lines=True)
            del df['Gemnr']
        elif d <= date(year=2020, month=3, day=16):
            df = pd.read_csv("RIVM_timeseries/" + file, delimiter=';', skiprows=[2, 3], skip_blank_lines=True,
                             index_col=False, usecols=['Gemeente', 'Aantal'])
        elif d <= date(year=2020, month=3, day=30):
            df = pd.read_csv("RIVM_timeseries/" + file, delimiter=';', skiprows=[2], skip_blank_lines=True,
                             index_col=False, usecols=['Gemeente', 'BevAant', 'Aantal'])
            if df['Aantal'].sum() > 17e6:
                # column mix up, so swap the two
                df['Aantal'] = df['BevAant']
            df.drop('BevAant', axis=1, inplace=True)
        elif d <= date(year=2020, month=4, day=7):
            df = pd.read_csv("RIVM_timeseries/" + file, delimiter=';', skiprows=[], skip_blank_lines=True,
                             index_col=False, usecols=['Gemeente', 'BevAant', 'Aantal'])
            if df['Aantal'].sum() > 17e6:
                # column mix up, so swap the two
                df['Aantal'] = df['BevAant']
            df.drop('BevAant', axis=1, inplace=True)
        else:
            df = pd.read_csv("RIVM_timeseries/" + file, delimiter=';', skiprows=[], skip_blank_lines=True,
                             index_col=False, usecols=['Gemeente', 'Zkh opname'])
            df.rename(columns={'Zkh opname': 'Aantal'})

        df.set_index('Gemeente', inplace=True)
        if turn:
            df = df.T
            df.index = [d]
        dfs.append(df)

    return [f.split('.')[0] for f in files], dfs