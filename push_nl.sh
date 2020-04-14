#!/usr/bin/env bash

git add 'nederland/*.csv'
git add 'nederland/RIVM_reports/*.pdf'
git add 'world/COVID-19'
git commit -m "auto data update NL and world data" --author="Frank Boerman <frank@fboerman.nl>"
git push
