#!/usr/bin/env bash

wget --quiet -O nederland/RIVM_reports/$(date +%Y-%m-%d).pdf $(curl -s https://www.rivm.nl/actuele-informatie-over-coronavirus/data | grep "COVID-19.*\.pdf" | grep -oP 'https://www.rivm.nl.*?.pdf')
