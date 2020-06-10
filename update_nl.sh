#!/usr/bin/env bash

echo "[>] pulling RIVM data"
currentdate=$(date '+%d%m%Y')
currentdatecsv="nederland/RIVM_timeseries/${currentdate}.csv"


if [[ ! -e $currentdatecsv ]]; then
	touch $currentdatecsv
fi
if [[ ! -e stichtingnice.html ]]; then
  touch stichtingnice.html
fi
#wget --quiet $csvlinknl
./extract_current_csv_rivm.py > /tmp/$currentdate.csv
rivmonline=$?


if [[ $rivmonline == 0 ]]; then
    # download the pdf
    curl -sL https://www.rivm.nl/coronavirus-covid-19/grafieken | grep -F ".pdf" > /tmp/rivmreport.html
    rivm_report_diff="$(diff /tmp/rivmreport.html rivmreport.html)"
    if [[ "0" != "${#rivm_report_diff}" ]]; then
	    ./downloadreport.sh
      mv /tmp/rivmreport.html ./rivmreport.html
    fi
    # download the json from the graphs of rivm
    curl -sL https://www.rivm.nl/coronavirus-covid-19/grafieken | grep -F "application/json" | sed 's/<.*>\(.*\)<\/.*>/\1/' > /tmp/rivm_graphs.json
    rivm_graphs_diff="$(diff /tmp/rivm_graphs.json nederland/rivm_graphs.json)"
    if [[ "0" != "${#rivm_graphs_diff}" ]]; then
      mv /tmp/rivm_graphs.json nederland/rivm_graphs.json
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
if [[ $rivmonline != 0 ]]; then
  echo "[!>] RIVM site not online"
else
    diff_output="$(diff /tmp/$currentdate.csv $currentdatecsv)"
    HOUR=$(date +%H)
    if [[ "0" != "${#diff_output}" ]]; then
    mv /tmp/$currentdate.csv $currentdatecsv
    cd nederland
    echo "[*>] csv data import"
    ./import.py
    #./generate_geojson.py
    ./extract_reported_state_rivm.py
    cd ..
    ./push_nl.sh
    if [[ $HOUR != 00 ]]; then
      cd /home/python/covid19bot/
      env/bin/python manage.py send_updates --rivmupdate --top20update
      cd /root/corona
    fi
    else
    echo "[*>] no changes detected in csv"
    fi
    if [[ "0" != "${#rivm_graphs_diff}" ]]; then
        cd nederland
        echo "[*>] json data import"
        ./import_rivm_reported_data.py
        cd ..
        ./push_nl.sh
    else
        echo "[*>] no changes detected in json"
    fi
#    if [[ "0" != "${#rivm_report_diff}" ]]; then
#        cd nederland
#        ./import_reports.py
#        cd ..
#	./push_nl.sh
#    else
#        echo "[*>] no changes detected in report"
#    fi
fi
