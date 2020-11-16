#!/usr/bin/env bash

# for now use hardcoded aws lambda url and credentials, this should be pulles from the js webpack files
awslink="https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com"
url="/prod/PortalGeral"
parseauth="unAFkcaNDeXajurGB7LChj8SgQYS2ptm"

echo "[>] Brazil"
# extract the last updated at if is changed then pull in new data
curl -s $awslink$url -H "X-Parse-Application-Id: $parseauth" | jq -r ".results | first | .updatedAt" > /tmp/timestamp.txt
diff="$(diff /tmp/timestamp.txt timestamp.txt)"
if [[ "0" != "${#diff}" ]]; then
  echo "[>] new data"
  wget --quiet -O covid.saude.gov.br.csv $(curl -s $awslink$url -H "X-Parse-Application-Id: $parseauth" | jq -r ".results | first | .arquivo.url")
  mv /tmp/timestamp.txt timestamp.txt
  cp covid.saude.gov.br.csv downloads/$(date --iso-8601=seconds).xlsx
  echo "[>] convert and import"
  ./convert_and_import.py
  echo "[>] push extracted data"
  ./push_bra.sh
else
  echo "[>] no changes detected"
fi