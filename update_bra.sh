#!/usr/bin/env bash

rssnaam="agencia-saude.xml"
csvnaam="brazil-timeseries-confirmed+deaths-perstate.csv"

cd brazil
echo "[>] checking brazil data"
curl -s --compressed https://www.saude.gov.br/noticias/agencia-saude?format=feed\&type=rss > /tmp/$rssnaam

if [[ ! -e ./$rssnaam ]]; then
  touch $rssnaam
fi

brazil_diff_output="$(diff /tmp/$rssnaam ./$rssnaam)"
if [[ "0" != "${#brazil_diff_output}" ]]; then
   mv /tmp/$rssnaam ./$rssnaam
   cp ./saude.gov.br/$csvnaam /tmp/$csvnaam
  ./pull_saude_from_feed.py
  csv_diff_output="$(diff ./saude.gov.br/$csvnaam /tmp/$csvnaam)"
  if [[ "0" != "${#csv_diff_output}" ]]; then
    echo "[*>] writing to database"
    ./import.py
    ./generate_geojson.py
    ./push_bra.sh
  else
    echo "[*>] no changes detected in csv"
  fi
else
  echo "[*>] no changes detected in xml"
fi

cd ..