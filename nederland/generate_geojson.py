import os
import pandas as pd
import json
from colour import Color
from math import ceil
from util import parse_all_csv
import copy

files = list(os.walk("RIVM_timeseries"))[0][2]
files.sort()
fnames, dfs = parse_all_csv(turn=False)
csvs = list(zip(fnames, dfs))
with open('map_base/gemeente_2019.geojson', 'r') as stream:
    geojson_base = json.load(stream)

df_BevAant = pd.read_csv('map_base/gemeente_2019_mensen.csv', delimiter=';')
df_BevAant = df_BevAant.set_index('Gemeente')

for name, df in csvs:
    df.index = df.index.str.strip()
    df_BevAant.index = df_BevAant.index.str.strip()
    df = pd.merge(df, df_BevAant, left_index=True, right_index=True)
    df.index = ["'s-Gravenhage" if c == 's-Gravenhage' else c for c in df.index]
    df['aantal_norm'] = round(df['Aantal'] / (df['BevAant'] / 100000), 1)

    geojson_aantal = copy.deepcopy(geojson_base)
    geojson_aantal_norm = copy.deepcopy(geojson_base)

    for i in range(len(geojson_base['features'])):
        obj = geojson_aantal['features'][i]
        try:
            obj['properties']['value'] = float(df.loc[obj['properties']['statnaam'],'Aantal'])
        except KeyError:
            obj['properties']['value'] = 0

        obj2 = geojson_aantal_norm['features'][i]
        try:
            obj2['properties']['value'] = float(df.loc[obj2['properties']['statnaam'], 'aantal_norm'])
        except KeyError:
            obj2['properties']['value'] = 0

    with open('map_data/aantal/gemeenten_{}.geojson'.format(name), 'w') as stream:
        json.dump(geojson_aantal, stream, separators=(',', ':'))

    with open('map_data/aantal_norm/gemeenten_{}.geojson'.format(name), 'w') as stream:
        json.dump(geojson_aantal_norm, stream, separators=(',', ':'))

    NUMBIN = 25
    for t in ['Aantal', 'aantal_norm']:
        BINSIZE = ceil(df[t].max()/NUMBIN)
        white = Color("white")
        colors = list(white.range_to(Color("darkred"), NUMBIN))
        colors = [c.hex for c in colors]

        colormap = """function getColor(d) {
            return """

        for i, c in enumerate(reversed(colors)):
            if i == NUMBIN - 1:
                colormap += "\t\t\t '{}' ;\n".format(c)
            else:
                colormap += "\t\td > {} ? '{}' :\n".format((NUMBIN - i - 1) * BINSIZE, c)
        colormap += "}"

        with open('map_data/{}/gemeenten_colormap_{}.js'.format(t.lower(), name), 'w') as stream:
            stream.write(colormap)