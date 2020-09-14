#!/usr/bin/env bash

git add 'nederland/*.csv'
git add 'world/COVID-19'
git add 'world/world_timeseries_per_pop.csv'
git commit -m "auto data update NL and world data" --author="Frank Boerman <frank@fboerman.nl>"
git push
