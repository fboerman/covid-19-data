#!/usr/bin/env bash

echo "[>] pulling RIVM data"
currentdate=$(date '+%d%m%Y')
currentdatecsv="nederland/RIVM_timeseries/${currentdate}.csv"
braziltimestamp="brazil-page.html"

if [[ ! -e $currentdatecsv ]]; then
	touch $currentdatecsv
fi
if [[ ! -e $braziltimestamp ]]; then
  touch $braziltimestamp
fi
if [[ ! -e stichtingnice.html ]]; then
  touch stichtingnice.html
fi
#wget --quiet $csvlinknl
./extract_current_csv_rivm.py > /tmp/$currentdate.csv
rivmonline=$?

if [[ $rivmonline == 0 ]]; then
    curl -s https://www.rivm.nl/actuele-informatie-over-coronavirus/data | grep -F ".pdf" > /tmp/rivmreport.html
    rivm_report_diff="$(diff /tmp/rivmreport.html rivmreport.html)"
    if [[ "0" != "${#rivm_report_diff}" ]]; then
        wget --quiet -O nederland/RIVM_reports/$(date +%Y-%m-%d).pdf  $(curl -s https://www.rivm.nl/actuele-informatie-over-coronavirus/data | grep -F ".pdf" | grep -oP 'https://www.rivm.nl.*?.pdf')
        mv /tmp/rivmreport.html ./rivmreport.html
    fi
fi

echo "[*>] import json sources"
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

echo "[>] pulling brazil data"
curl -s --compressed https://www.saude.gov.br/noticias/agencia-saude?format=feed\&type=rss > /tmp/$braziltimestamp

brazil_diff_output="$(diff /tmp/$braziltimestamp $braziltimestamp)"
if [[ "0" != "${#brazil_diff_output}" ]]; then
  cd brazil
  ./pull_saude_from_feed.py
  cd ..
  mv /tmp/$braziltimestamp ./$braziltimestamp
fi

echo "[>] writing data to grafana database"
echo "[*>] world"
if [[ "$git_output" != "Already up to date." ]]; then
	cd world
	./import.py
	cd ..
else
	echo "[*>] no changes detected"
fi

echo "[*>] netherlands"
if [[ $rivmonline != 0 ]]; then
  echo "[!>] RIVM site not online"
else
    diff_output="$(diff /tmp/$currentdate.csv $currentdatecsv)"
    HOUR=$(date +%H)
    if [[ "0" != "${#diff_output}" ]]; then
    mv /tmp/$currentdate.csv $currentdatecsv
    cd nederland
    ./import.py
    ./generate_geojson.py
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
    if [[ "0" != "${#rivm_report_diff}" ]]; then
        cd nederland
        ./import_reports.py
        cd ..
	./push_nl.sh
    else
        echo "[*>] no changes detected in report"
    fi
fi

echo "[*>] brazil"
if [[ "0" != "${#brazil_diff_output}" ]]; then
  cd brazil
  ./import.py
  ./generate_geojson.py
  cd ..
  ./push_bra.sh
else
  echo "[*>] no changes detected"
fi
