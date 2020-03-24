#!/usr/bin/env bash

echo "[>] pulling RIVM data"
#csvlinknl=$(curl -s https://www.volksgezondheidenzorg.info/onderwerp/infectieziekten/regionaal-internationaal/coronavirus-covid-19 | tr '"' '\n' | grep '\.csv$')
#csvlinknl="https://www.volksgezondheidenzorg.info${csvlinknl}"
#cd nederland/RIVM
#currentdate=$(echo $csvlinknl | grep -oE '[0-9]{8}')
currentdate=$(date '+%d%m%Y')
currentdatecsv="nederland/RIVM/${currentdate}.csv"
braziltimestamp="brazil-last-modified.txt"

if [[ ! -e $currentdatecsv ]]; then
	touch $currentdatecsv
fi
if [[ ! -e $braziltimestamp ]]; then
  touch
fi
#wget --quiet $csvlinknl
./extract_current_csv_rivm.py > /tmp/$currentdate.csv

#echo "[*>] fix names of csv"
#cd nederland/RIVM
#for file in ./*.csv; do
#    [ -e "$file" ] || continue
#    name=${file##*/}
#    newname=$(echo $name | grep -oE '[0-9]{8}')
#    newname="${newname}.csv"
#    mv $name $newname 2> /dev/null
#done
#cd ../..

echo "[>] pulling johns hopkins data"
cd world/COVID-19
git_output=$(git pull)
cd ../../

echo "[>] pulling brazil data"
curl -sIL https://www.saude.gov.br/noticias/agencia-saude\?format\=feed\&type\=rss | grep "last-modified" >> /tmp/$braziltimestamp
brazil_diff_output="$(diff /tmp/$braziltimestamp.csv $braziltimestamp)"
if [[ "0" != "${#brazil_diff_output}" ]]; then
  cd brazil
  ./pull_saude_from_feed.py
  mv /tmp/$braziltimestamp ./$braziltimestamp
  cd ..
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
diff_output="$(diff /tmp/$currentdate.csv $currentdatecsv)"
HOUR=$(date +%H)
if [[ "0" != "${#diff_output}" ]]; then
	mv /tmp/$currentdate.csv $currentdatecsv
	cd nederland
	./import.py
	cd ..
	./push_nl.sh
	if [[ $HOUR != 00 ]]; then
		#./extract_current_ziekenhuis_number.py
		cd /home/python/covid19bot/
		env/bin/python manage.py send_updates --rivmupdate --top20update
		cd /root/corona
	fi
else
	echo "[*>] no changes detected"
fi

echo "[*>] brazil"
if [[ "0" != "${#brazil_diff_output}" ]]; then
  cd brazil
  ./import.py
  cd ..
  ./push_bra.sh
else
  echo "[*>] no changes detected"
fi
