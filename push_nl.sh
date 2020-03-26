#!/usr/bin/env bash

git add 'nederland/RIVM_timeseries/*.csv'
git add 'nederland/RIVM_reports/*.pdf'
git add 'world/COVID-19'
git commit -m "auto data update" --author="Frank Boerman <frank@fboerman.nl>"
git push
