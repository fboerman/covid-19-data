#!/usr/bin/env bash

git add 'nederland/RIVM/*.csv'
git add 'brazil/saude.gov.br/*.csv'
git add 'world/COVID-19'
git commit -m "auto data update" --author="Frank Boerman <frank@fboerman.nl>"
git push
