#!/usr/bin/env bash

echo "[>] pulling RIVM data"
currentdate=$(date '+%Y-%m-%d')
#currentdatecsv="nederland/RIVM_timeseries/${currentdate}.csv"


if [[ ! -e stichtingnice.html ]]; then
  touch stichtingnice.html
fi
if [[ ! -e gemeenten_timestamp.txt ]]; then
  touch gemeenten_timestamp.txt
fi

#wget --quiet $csvlinknl
./nederland/extract_current_csv_rivm.py > ./nederland/RIVM_timeseries/gemeenten_2weken/latest.csv
rivmonline=$?
rivmupdate=0

if [[ $rivmonline == 0 ]]; then
    # download the json from the graphs of rivm
    curl -sL https://www.rivm.nl/coronavirus-covid-19/grafieken | grep -F "application/json" | sed 's/<.*>\(.*\)<\/.*>/\1/' > /tmp/rivm_graphs.json
    rivm_graphs_diff="$(diff /tmp/rivm_graphs.json nederland/rivm_graphs.json)"
    if [[ "0" != "${#rivm_graphs_diff}" ]]; then
      mv /tmp/rivm_graphs.json nederland/rivm_graphs.json
      rivmupdate=1
    fi

    # check the timestamp on the municipality datasheet
    curl -s -I https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv | grep -i 'last-modified' > /tmp/gemeenten_timestamp.txt
    rivm_gemeenten_diff ="$(diff /tmp/gemeenten_timestamp.txt gemeenten_timestamp.txt)"

    if [["0" != "${#rivm_gemeenten_diff}" ]]; then
      curl -s https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv > RIVM_timeseries/gemeenten_latest.csv
      mv /tmp/gemeenten_timestamp.txt gemeenten_timestamp.txt
      rivmupdate=1
    fi
fi

echo "[*>] import json sources (stichting NICE)"
curl -s https://www.stichting-nice.nl/ | grep -A 1 -iF "laatste update" > /tmp/stichtingnice.html
stichting_nice_diff="$(diff /tmp/stichtingnice.html stichtingnice.html)"
if [[ "0" != "${#stichting_nice_diff}" ]]; then
    cd nederland
    ./import_jsonsources.py
    cd ..
    mv /tmp/stichtingnice.html ./
else
    echo "[*>] no changes detected"
fi


echo "[>] pulling johns hopkins data"
cd world/COVID-19
git_output=$(git pull)
cd ../../


echo "[>] writing data to grafana database"
echo "[*>] world"
if [[ "$git_output" != "Already up to date." ]]; then
	cd world
	./import.py
	cd ..
else
	echo "[*>] no changes detected"
fi

echo "[*>] netherlands (RIVM)"
if [[ rivmupdate != 0 ]]; then
  echo "[!>] RIVM no updates"
else
    cd nederland
    echo "[*>] csv data import"
    ./gemeenten_2weken_split_csv.py
    ./import.py
    #./extract_reported_state_rivm.py
    cd ..
    ./push_nl.sh

    cd nederland
    echo "[*>] json data import"
    ./import_rivm_reported_data.py
    cd ..
    ./push_nl.sh
fi