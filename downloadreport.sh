#!/usr/bin/env bash

rivm_url="https://www.rivm.nl/coronavirus-covid-19/grafieken"
wget --quiet -O nederland/RIVM_reports/$(date +%Y-%m-%d).pdf $(curl -s $rivm_url | grep "COVID-19.*\.pdf" | grep -oP 'https://www.rivm.nl.*?.pdf')