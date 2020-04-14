#!/usr/bin/env python3

import os.path
import pandas as pd
import json
from colour import Color
from math import ceil
from regions import states
import copy
from datetime import datetime

code_to_name = lambda df_states_static, code: df_states_static[df_states_static['code'] == code].index.tolist()[0]

with open('map_base/states.geojson', 'r') as stream:
    geojson_base = json.load(stream)

for t in ['confirmed', 'deaths']:
    # print(t)
    df_states_static = pd.DataFrame(states, columns=['name', 'code', 'region', 'people'])
    df_states_static.set_index('name', inplace=True)
    df_states_timeseries = pd.read_csv('saude.gov.br/brazil-timeseries-confirmed+deaths-perstate.csv', delimiter=';')
    df_states_timeseries = df_states_timeseries.loc[df_states_timeseries['type']==t]
    df_states_timeseries.drop('type', axis=1, inplace=True)
    df_states_timeseries.set_index('time', inplace=True)

    df_states_timeseries_norm = df_states_timeseries.copy()

    for column in df_states_timeseries_norm:
        df_states_timeseries_norm[column] /= df_states_static.loc[column, 'people']/100e3

    # print("[*] parsing csv and generate geojson")
    for date, data in df_states_timeseries_norm.iterrows():
        # print("[**] parsing {}".format(date))
        date = datetime.strptime(date, '%Y-%m-%d').strftime("%d%m%Y")
        if os.path.exists('map_data/{}/states_{}.geojson'.format(t, date)) and \
            os.path.exists('map_data/{}/states_colormap_{}.js'.format(t, date)):
            continue
        geojson_aantal_norm = copy.deepcopy(geojson_base)
        data_abs = df_states_timeseries.loc[date, :]

        for i in range(len(geojson_base['features'])):
            obj = geojson_aantal_norm['features'][i]
            try:
                obj['properties']['value'] = round(float(data[code_to_name(df_states_static, obj['properties']['sigla'])]), 4)
                obj['properties']['absvalue'] = round(float(data_abs[code_to_name(df_states_static, obj['properties']['sigla'])]), 4)
            except KeyError:
                obj['properties']['value'] = 0
                obj['properties']['absvalue'] = 0

        with open('map_data/{}/states_{}.geojson'.format(t, date), 'w') as stream:
            json.dump(geojson_aantal_norm, stream, separators=(',', ':'))

        NUMBIN = 25
        BINSIZE = data.max() / float(NUMBIN)
        white = Color("gray")
        colors = list(white.range_to(Color("red"), NUMBIN))
        colors = [c.hex for c in colors]

        colormap = """function getColor(d) {
            return """

        for i, c in enumerate(reversed(colors)):
            if i == NUMBIN - 1:
                colormap += "\t\t\t '{}' ;\n".format(c)
            else:
                colormap += "\t\td > {} ? '{}' :\n".format(round((NUMBIN - i - 1) * BINSIZE, 4), c)
        colormap += "}"

        with open('map_data/{}/states_colormap_{}.js'.format(t, date), 'w') as stream:
            stream.write(colormap)