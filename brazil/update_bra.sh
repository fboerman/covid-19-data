#!/usr/bin/env bash

if [[ ! -e saude.gov.br/source.csv ]]; then
  touch saude.gov.br/source.csv
fi

# for now use hardcoded aws lambda url and credentials, this should be pulles from the js webpack files
awslink="https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com"
url="/prod/PortalGeral"
parseauth="unAFkcaNDeXajurGB7LChj8SgQYS2ptm"

# bash oneliner to extract the csvurl and save it
echo "[>] pulling brazil source data"
wget --quiet -O /tmp/saudebr.csv $(curl -s $awslink$url -H "X-Parse-Application-Id: $parseauth" | jq -r '.results | first | .arquivo.url')

# check for changes, if so run convert and import script
diff="$(diff /tmp/saudebr.csv saude.gov.br/source.csv)"
if [[ "0" != "${#diff}" ]]; then
  echo "[>] new data"
  mv /tmp/saudebr.csv saude.gov.br/source.csv
  echo "[>] convert csv"
  ./convert.py
  echo "[>] import csv"
  ./import.py
  ./push_bra.sh
  echo "[>] generate geojson"
  ./generate_geojson.py
else
  echo "[>] no changes detected"
fi
